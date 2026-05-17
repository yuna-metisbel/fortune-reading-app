import json
import re
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_browser_user
from app.models import DailyCompatibility, User
from app.services.claude_client import generate_message
from app.services.numerology import calculate_life_path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

RELATIONSHIP_LABELS = {
    "lover": "恋人",
    "partner": "ビジネスパートナー",
    "friend": "友人",
    "family": "家族",
    "colleague": "同僚",
}

COMPAT_SYSTEM_PROMPT = """あなたは人間関係の専門家であり、鋭い直感を持つ占い師です。
二人の生年月日・関係性・今日の日付から、「今日の二人」の相性とアドバイスを占います。

必ず以下のJSON形式のみで回答してください。JSON以外のテキストは一切含めないでください。

{
  "compatibility_score": (1-100の整数。50が平均的、80以上は最高の日、30以下は要注意の日),
  "one_liner": "(今日の二人を一言で。具体的で刺さる一文。「今日、あの人が黙り込んだら——それは怒りではなく、言葉を選んでいる証拠」のように場面を描写)",
  "today_energy": "(今日の二人の間に流れるエネルギーを2-3文で。具体的な場面や時間帯に言及)",
  "communication_tip": "(今日のコミュニケーションで意識すべきこと。「結論から言わず、まず相手の話を30秒聞く」のように具体的な行動で)",
  "do_this": "(今日この相手に対してやるべきこと。「午前中にLINEで軽いスタンプを送る」レベルで具体的に)",
  "avoid_this": "(今日この相手に対して避けるべきこと。具体的に)",
  "power_word": "(今日この相手に伝えると関係が良くなる一言。実際に口に出せるフレーズ)",
  "evening_action": "(今日の夜にやること。一日の締めくくりとして関係を深める行動)"
}

ルール:
- 関係性（恋人/ビジネスパートナー/友人/家族）に合わせたトーンとアドバイスにする
- 恋人向け: 感情・スキンシップ・デートの提案を含む
- ビジネスパートナー向け: 会議・提案・交渉のタイミング等を含む
- 友人向け: 連絡の取り方・遊びの提案を含む
- 家族向け: 日常の中の小さな気遣い・会話を含む
- 「心がけましょう」は禁止。全て具体的な行動で書く
- power_wordは「」で囲まず、そのまま口に出せる自然な日本語で
- JSONのみ出力。説明文は不要
- 全フィールド合計で350文字以内に収める
- one_linerは30文字以内
- today_energyは60文字以内（2文まで）
- communication_tip, do_this, avoid_this, evening_actionはそれぞれ40文字以内
- power_wordは20文字以内"""


def _build_compat_prompt(my_bd: date, partner_bd: date, rel_type: str, nickname: str, today: date) -> str:
    my_lp = calculate_life_path(my_bd.year, my_bd.month, my_bd.day)
    p_lp = calculate_life_path(partner_bd.year, partner_bd.month, partner_bd.day)
    day_num = (today.year + today.month + today.day) % 9 + 1
    rel_label = RELATIONSHIP_LABELS.get(rel_type, rel_type)

    return f"""あなたの生年月日: {my_bd.isoformat()}
あなたのライフパスナンバー: {my_lp.get('life_path', '不明')}
相手（{nickname}）の生年月日: {partner_bd.isoformat()}
相手のライフパスナンバー: {p_lp.get('life_path', '不明')}
二人の関係性: {rel_label}
今日の日付: {today.isoformat()}
曜日: {today.strftime('%A')}
今日の数秘デイナンバー: {day_num}

この情報を元に今日の二人の相性とアドバイスをJSON形式で出力してください。"""


@router.get("/daily/compatibility")
async def daily_compat_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    today = date.today()
    result = await db.execute(
        select(DailyCompatibility)
        .where(DailyCompatibility.user_id == user.id, DailyCompatibility.fortune_date == today)
        .order_by(DailyCompatibility.created_at.desc())
    )
    recent = result.scalars().all()
    return templates.TemplateResponse("daily_compat.html", {
        "request": request,
        "recent": recent,
        "today": today,
    })


@router.post("/api/daily/compatibility/generate")
async def generate_daily_compat(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    try:
        my_bd = date.fromisoformat(body.get("my_birth_date", ""))
        partner_bd = date.fromisoformat(body.get("partner_birth_date", ""))
    except (ValueError, TypeError):
        return JSONResponse({"error": "生年月日が正しくありません"}, status_code=400)

    nickname = body.get("partner_nickname", "相手")
    rel_type = body.get("relationship_type", "friend")
    today = date.today()

    result = await db.execute(
        select(DailyCompatibility).where(
            DailyCompatibility.user_id == user.id,
            DailyCompatibility.partner_birth_date == partner_bd,
            DailyCompatibility.relationship_type == rel_type,
            DailyCompatibility.fortune_date == today,
        ).limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return JSONResponse(_compat_to_dict(existing))

    prompt = _build_compat_prompt(my_bd, partner_bd, rel_type, nickname, today)

    for attempt in range(2):
        raw = await generate_message(COMPAT_SYSTEM_PROMPT, prompt)
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else json.loads(raw)
            break
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt == 1:
                return JSONResponse({"error": "占い結果の生成に失敗しました"}, status_code=500)

    compat = DailyCompatibility(
        user_id=user.id,
        my_birth_date=my_bd,
        partner_birth_date=partner_bd,
        partner_nickname=nickname,
        relationship_type=rel_type,
        fortune_date=today,
        compatibility_score=int(data.get("compatibility_score", 50)),
        one_liner=data.get("one_liner", ""),
        today_energy=data.get("today_energy", ""),
        communication_tip=data.get("communication_tip", ""),
        do_this=data.get("do_this", ""),
        avoid_this=data.get("avoid_this", ""),
        power_word=data.get("power_word", ""),
        evening_action=data.get("evening_action", ""),
    )
    db.add(compat)
    await db.commit()
    await db.refresh(compat)
    return JSONResponse(_compat_to_dict(compat))


def _compat_to_dict(c: DailyCompatibility) -> dict:
    return {
        "id": c.id,
        "partner_nickname": c.partner_nickname,
        "relationship_type": c.relationship_type,
        "compatibility_score": c.compatibility_score,
        "one_liner": c.one_liner,
        "today_energy": c.today_energy,
        "communication_tip": c.communication_tip,
        "do_this": c.do_this,
        "avoid_this": c.avoid_this,
        "power_word": c.power_word,
        "evening_action": c.evening_action,
    }
