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
from app.models import DailyFortune, LineSubscription, User
from app.services.claude_client import generate_message
from app.services.numerology import calculate_life_path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

DAILY_SYSTEM_PROMPT = """あなたは鋭い直感と深い占術知識を持つ占い師です。
ユーザーの生年月日と今日の日付から、今日一日の運勢を占います。

必ず以下のJSON形式のみで回答してください。JSON以外のテキストは一切含めないでください。

{
  "overall_luck": (1-100の整数。50が平均、80以上は大吉、30以下は要注意),
  "one_liner": "(最初の一撃。具体的で刺さる一文。「今日は良い日」のような曖昧なものは禁止。「3ヶ月間モヤモヤしていたあの件、今日答えが降りてくる」のように具体的に)",
  "message": "(2-3文の本日の運勢メッセージ。具体的な時間帯や場面に言及する)",
  "action_tip": "(今日やるべき具体的な行動。「午前中に白い花を目にする場所を歩く」のように具体的に)",
  "caution": "(今日気をつけること。具体的に)",
  "lucky_stone": "(パワーストーンの日本語名。実在する石のみ: アメジスト、ローズクォーツ、ラピスラズリ、タイガーアイ、ムーンストーン、ラブラドライト、フローライト、アクアマリン、シトリン、ガーネット、ターコイズ、カーネリアン、オニキス、水晶、スモーキークォーツ、サンストーン、アパタイト、ルチルクォーツ、プレナイト、セレスタイト、アンバー、マラカイト、ロードナイト等)",
  "stone_message": "(なぜ今日この石が必要なのか。石のエネルギーと今日の運勢の関連を1-2文で)",
  "lucky_color": "(ラッキーカラー名)",
  "lucky_number": (1-9の整数),
  "nail_color": "(今月おすすめのネイルカラー名。「ダスティローズ」「シアーラベンダー」「ミルキーベージュ」等の具体的な色名)",
  "nail_color_code": "(ネイルカラーの16進数カラーコード。#RRGGBB形式)",
  "nail_message": "(このネイルカラーが今の運気にどう作用するか1文)",
  "fashion_base": "(今日のファッションのベースカラー)",
  "fashion_accent": "(差し色として入れるべき色)",
  "fashion_message": "(この配色が今日のあなたにどう作用するか1文)"
}

ルール:
- 生年月日の数秘術的意味と今日の日付のエネルギーを組み合わせて占う
- one_linerは絶対に曖昧にしない。「あなたに転機が」は禁止。日時・場所・感情を具体的に
- パワーストーンは必ず実在するものを選ぶ
- ネイルカラーコードは実際にネイルとして美しい色を選ぶ（くすみ系、シアー系が好まれる）
- JSONのみ出力。説明文は不要
- 全フィールド合計で400文字以内に収める
- one_linerは30文字以内
- messageは80文字以内（2文まで）
- action_tip, caution, stone_message, nail_message, fashion_messageはそれぞれ40文字以内"""


def _build_daily_prompt(birth_date: date, today: date, blood_type: str | None = None, birth_place: str | None = None) -> str:
    life_path = calculate_life_path(birth_date.year, birth_date.month, birth_date.day)
    day_number = (today.year + today.month + today.day) % 9 + 1

    lines = [
        f"生年月日: {birth_date.isoformat()}",
        f"今日の日付: {today.isoformat()}",
        f"曜日: {today.strftime('%A')}",
        f"ライフパスナンバー: {life_path.get('life_path', '不明')}",
        f"今日の数秘デイナンバー: {day_number}",
    ]
    if blood_type:
        lines.append(f"血液型: {blood_type}型")
    if birth_place:
        lines.append(f"出身地: {birth_place}")
    lines.append("")
    lines.append("この情報を元に今日の運勢をJSON形式で出力してください。")
    if blood_type:
        lines.append(f"血液型{blood_type}型の性格特性も加味して占ってください。")
    if birth_place:
        lines.append(f"出身地の土地のエネルギーも考慮してください。")
    return "\n".join(lines)


@router.get("/daily")
async def daily_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    today = date.today()
    result = await db.execute(
        select(DailyFortune)
        .where(DailyFortune.user_id == user.id, DailyFortune.fortune_date == today)
        .limit(1)
    )
    fortune = result.scalar_one_or_none()
    return templates.TemplateResponse("daily.html", {
        "request": request,
        "fortune": fortune,
        "today": today,
    })


@router.post("/api/daily/generate")
async def generate_daily(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    birth_date_str = body.get("birth_date", "")
    blood_type = body.get("blood_type") or None
    birth_place = body.get("birth_place") or None
    try:
        birth_date = date.fromisoformat(birth_date_str)
    except (ValueError, TypeError):
        return JSONResponse({"error": "生年月日が正しくありません"}, status_code=400)

    today = date.today()

    result = await db.execute(
        select(DailyFortune)
        .where(DailyFortune.user_id == user.id, DailyFortune.fortune_date == today)
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return JSONResponse(_fortune_to_dict(existing))

    user_prompt = _build_daily_prompt(birth_date, today, blood_type, birth_place)

    for attempt in range(2):
        raw = await generate_message(DAILY_SYSTEM_PROMPT, user_prompt)
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(raw)
            break
        except (json.JSONDecodeError, ValueError):
            if attempt == 1:
                return JSONResponse({"error": "占い結果の生成に失敗しました"}, status_code=500)

    fortune = DailyFortune(
        user_id=user.id,
        birth_date=birth_date,
        fortune_date=today,
        overall_luck=int(data.get("overall_luck", 50)),
        lucky_stone=data.get("lucky_stone", "水晶"),
        stone_message=data.get("stone_message", ""),
        lucky_color=data.get("lucky_color", "紫"),
        lucky_number=int(data.get("lucky_number", 7)),
        nail_color=data.get("nail_color", "シアーピンク"),
        nail_color_code=data.get("nail_color_code", "#E8B4B8"),
        nail_message=data.get("nail_message", ""),
        fashion_base=data.get("fashion_base", "アイボリー"),
        fashion_accent=data.get("fashion_accent", "ラベンダー"),
        fashion_message=data.get("fashion_message", ""),
        one_liner=data.get("one_liner", ""),
        message=data.get("message", ""),
        action_tip=data.get("action_tip", ""),
        caution=data.get("caution", ""),
    )
    db.add(fortune)
    await db.commit()
    await db.refresh(fortune)

    return JSONResponse(_fortune_to_dict(fortune))


@router.post("/api/daily/line-subscribe")
async def line_subscribe(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    result = await db.execute(
        select(LineSubscription).where(LineSubscription.user_id == user.id).limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.subscribed = 1
        await db.commit()
    else:
        sub = LineSubscription(user_id=user.id, subscribed=1)
        db.add(sub)
        await db.commit()
    return JSONResponse({"status": "subscribed"})


@router.get("/api/daily/line-status")
async def line_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    result = await db.execute(
        select(LineSubscription).where(LineSubscription.user_id == user.id).limit(1)
    )
    sub = result.scalar_one_or_none()
    return JSONResponse({"subscribed": bool(sub and sub.subscribed)})


def _fortune_to_dict(f: DailyFortune) -> dict:
    return {
        "id": f.id,
        "overall_luck": f.overall_luck,
        "one_liner": f.one_liner,
        "message": f.message,
        "action_tip": f.action_tip,
        "caution": f.caution,
        "lucky_stone": f.lucky_stone,
        "stone_message": f.stone_message,
        "lucky_color": f.lucky_color,
        "lucky_number": f.lucky_number,
        "nail_color": f.nail_color,
        "nail_color_code": f.nail_color_code,
        "nail_message": f.nail_message,
        "fashion_base": f.fashion_base,
        "fashion_accent": f.fashion_accent,
        "fashion_message": f.fashion_message,
    }
