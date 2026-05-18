import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_browser_user
from app.models import DailyFortune, LineSubscription, User, WeeklyArc
from app.services.claude_client import generate_message
from app.services.numerology import calculate_life_path

JST = timezone(timedelta(hours=9))

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

DAILY_FORMAT_TYPES = [
    "standard",
    "story",
    "question",
    "letter",
    "warning",
    "number",
    "reverse",
]

DAILY_FORMAT_INSTRUCTIONS = {
    "standard": "通常形式で出力。",
    "story": 'messageを一人称の物語風に書く。「あなたは今朝、鏡の前で少し迷った──」のように場面から入る。',
    "question": 'messageを「Q: 今日◯◯していい？ A: ◯◯なら。ただし△△で」のような一問一答形式にする。3組出す。',
    "letter": 'messageを「── 親愛なる◯◯へ。今日あなたに伝えなければならないことがある」で始まる手紙形式にする。',
    "warning": "messageの冒頭に「本日の注意報」と書き、今日守るべきルールを3つ先に出してから理由を述べる。",
    "number": 'messageを「14:00 / 3人目 / 左から2番目」のように今日の鍵となる3つの数字で表現し、その意味を解説する。',
    "reverse": 'messageを「1ヶ月後のあなたから今日のあなたへ」という未来視点で書く。',
}

DAILY_SYSTEM_PROMPT = """あなたはMadame Lune（マダム・リュンヌ）。
生年月日と今日の日付から、今日一日の運勢を読み解く。

語り口：上品だが親しみがある。「〜よ」「〜ね」「〜わ」。核心を突く。

必ず以下のJSON形式のみで回答。JSON以外のテキストは一切含めない。

{
  "overall_luck": (1-100の整数。50が平均、80以上は大吉、30以下は要注意),
  "one_liner": "(最初の一撃。具体的で刺さる一文。「今日は良い日」禁止。「3ヶ月間モヤモヤしていたあの件、今日答えが降りてくる」のように具体的。25文字以内)",
  "message": "(本日の運勢メッセージ。DAILY_FORMAT指示に従う。具体的な時間帯・場所・行動に言及。150〜250文字で濃く書く。比喩や場面描写を入れて読み応えを出す)",
  "prediction": "(明日検証できる具体的な予言1つ。「午後3時台に知り合いから連絡が来る」「帰り道で黄色いものが目に入る」等。検証可能なものだけ。30文字以内)",
  "action_tip": "(今日やるべき具体的な行動。「午前中に白い花を目にする場所を歩く」レベルで具体的に)",
  "caution": "(今日気をつけること。具体的に)",
  "lucky_stone": "(パワーストーン日本語名。実在する石のみ)",
  "stone_message": "(なぜ今日この石が必要か。1-2文)",
  "lucky_color": "(ラッキーカラー名)",
  "lucky_number": (1-9の整数),
  "nail_color": "(ネイルカラー名。「ダスティローズ」「シアーラベンダー」等)",
  "nail_color_code": "(#RRGGBB形式。くすみ系・シアー系の美しい色)",
  "nail_message": "(このネイルカラーが運気にどう作用するか1文)",
  "fashion_base": "(ファッションのベースカラー)",
  "fashion_accent": "(差し色)",
  "fashion_message": "(この配色の効果1文)"
}

ルール:
- 生年月日の数秘術的意味と今日の日付のエネルギーを組み合わせる
- one_linerは曖昧禁止。日時・場所・感情を具体的に
- predictionは「当たった/ハズレ」が翌日に判定できるものだけ
- messageは150〜250文字。短すぎNG。読み応え重視
- パワーストーンは実在するもの
- ネイルカラーコードは実際にネイルとして美しい色
- JSONのみ出力"""


def _build_daily_prompt(birth_date: date, today: date, blood_type: str | None = None, birth_place: str | None = None, weekly_theme: str | None = None, today_seed: str | None = None) -> str:
    life_path = calculate_life_path(birth_date.year, birth_date.month, birth_date.day)
    day_number = (today.year + today.month + today.day) % 9 + 1

    format_idx = (today.toordinal() + birth_date.toordinal()) % len(DAILY_FORMAT_TYPES)
    format_type = DAILY_FORMAT_TYPES[format_idx]
    format_instruction = DAILY_FORMAT_INSTRUCTIONS[format_type]

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
    if weekly_theme:
        lines.append(f"今週のテーマ: {weekly_theme}")
    if today_seed:
        lines.append(f"今日のストーリー: {today_seed}")
    lines.append("")
    lines.append(f"【DAILY_FORMAT: {format_type}】")
    lines.append(format_instruction)
    lines.append("")
    lines.append("この情報を元に今日の運勢をJSON形式で出力してください。")
    if weekly_theme:
        lines.append("今週のテーマと今日のストーリーを自然にmessageに織り込んでください。")
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

    yesterday = today - timedelta(days=1)
    yest_result = await db.execute(
        select(DailyFortune)
        .where(DailyFortune.user_id == user.id, DailyFortune.fortune_date == yesterday)
        .limit(1)
    )
    yesterday_fortune = yest_result.scalar_one_or_none()

    monday = _monday_of(today)
    arc_result = await db.execute(
        select(WeeklyArc)
        .where(WeeklyArc.user_id == user.id, WeeklyArc.week_start == monday)
        .limit(1)
    )
    weekly_arc = arc_result.scalar_one_or_none()

    cutoff = today - timedelta(days=30)
    rate_result = await db.execute(
        select(DailyFortune)
        .where(
            DailyFortune.user_id == user.id,
            DailyFortune.prediction_result.isnot(None),
            DailyFortune.fortune_date >= cutoff,
        )
    )
    rate_fortunes = rate_result.scalars().all()
    scored = [f for f in rate_fortunes if f.prediction_result in ("hit", "miss")]
    hit_count = sum(1 for f in scored if f.prediction_result == "hit")
    hit_total = len(scored)
    hit_rate = round(hit_count / hit_total * 100) if hit_total > 0 else None

    day_index = (today - monday).days
    arc_seeds = []
    if weekly_arc:
        arc_seeds = [s.strip() for s in weekly_arc.story_seed.split(",")]

    theme = getattr(request.state, "theme", "default")
    tpl_name = "daily.html"
    if theme in ("a", "b", "c"):
        from pathlib import Path as _P
        if (_P(__file__).resolve().parent.parent / "templates" / theme / "daily.html").exists():
            tpl_name = f"{theme}/daily.html"

    return templates.TemplateResponse(tpl_name, {
        "request": request,
        "fortune": fortune,
        "today": today,
        "active_tab": "daily",
        "yesterday_fortune": yesterday_fortune,
        "weekly_arc": weekly_arc,
        "arc_seeds": arc_seeds,
        "day_index": day_index,
        "hit_rate": hit_rate,
        "hit_count": hit_count,
        "hit_total": hit_total,
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

    monday = _monday_of(today)
    arc_result = await db.execute(
        select(WeeklyArc)
        .where(WeeklyArc.user_id == user.id, WeeklyArc.week_start == monday)
        .limit(1)
    )
    arc = arc_result.scalar_one_or_none()
    weekly_theme = None
    today_seed = None
    if arc:
        weekly_theme = arc.theme
        seeds = [s.strip() for s in arc.story_seed.split(",")]
        day_idx = (today - monday).days
        today_seed = seeds[day_idx] if day_idx < len(seeds) else None

    user_prompt = _build_daily_prompt(birth_date, today, blood_type, birth_place, weekly_theme, today_seed)

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
        prediction=data.get("prediction", ""),
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
        "prediction": f.prediction or "",
    }


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


@router.post("/api/daily/prediction-check")
async def prediction_check(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    fortune_id = body.get("fortune_id")
    result = body.get("result")
    if result not in ("hit", "miss", "na"):
        return JSONResponse({"error": "Invalid result"}, status_code=400)

    fortune = await db.get(DailyFortune, fortune_id)
    if not fortune or fortune.user_id != user.id:
        return JSONResponse({"error": "Not found"}, status_code=404)
    if fortune.prediction_result:
        return JSONResponse({"error": "Already checked"}, status_code=400)

    fortune.prediction_result = result
    fortune.prediction_checked_at = datetime.now(JST).replace(tzinfo=None)
    await db.commit()
    return JSONResponse({"status": "ok"})


@router.get("/api/daily/hit-rate")
async def hit_rate(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    cutoff = date.today() - timedelta(days=30)
    result = await db.execute(
        select(DailyFortune)
        .where(
            DailyFortune.user_id == user.id,
            DailyFortune.prediction_result.isnot(None),
            DailyFortune.fortune_date >= cutoff,
        )
    )
    fortunes = result.scalars().all()
    scored = [f for f in fortunes if f.prediction_result in ("hit", "miss")]
    hits = sum(1 for f in scored if f.prediction_result == "hit")
    total = len(scored)
    rate = round(hits / total * 100) if total > 0 else None
    return JSONResponse({"rate": rate, "hits": hits, "total": total})


@router.get("/api/daily/yesterday-prediction")
async def yesterday_prediction(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    yesterday = date.today() - timedelta(days=1)
    result = await db.execute(
        select(DailyFortune)
        .where(
            DailyFortune.user_id == user.id,
            DailyFortune.fortune_date == yesterday,
        )
        .limit(1)
    )
    fortune = result.scalar_one_or_none()
    if not fortune or not fortune.prediction:
        return JSONResponse({"has_prediction": False})
    return JSONResponse({
        "has_prediction": True,
        "fortune_id": fortune.id,
        "prediction": fortune.prediction,
        "already_checked": fortune.prediction_result is not None,
        "result": fortune.prediction_result,
    })


WEEKLY_ARC_PROMPT = """あなたはMadame Lune。
今週（月曜〜日曜）の統一テーマと7日間のストーリーの種を生成する。

以下のJSON形式のみで回答：
{
  "theme": "(今週のテーマ。6〜12文字。例：「沈黙が語る週」「手放しと再構築」)",
  "story_seed": "(月曜から日曜まで1文ずつ。7文をカンマ区切りで。各文は15〜25文字。日ごとに物語が展開する構成にする)"
}

JSON以外のテキストは一切含めない。"""


@router.get("/api/daily/weekly-arc")
async def get_weekly_arc(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    today = date.today()
    monday = _monday_of(today)
    result = await db.execute(
        select(WeeklyArc)
        .where(WeeklyArc.user_id == user.id, WeeklyArc.week_start == monday)
        .limit(1)
    )
    arc = result.scalar_one_or_none()
    if not arc:
        return JSONResponse({"has_arc": False})

    day_idx = (today - monday).days
    seeds = [s.strip() for s in arc.story_seed.split(",")]
    return JSONResponse({
        "has_arc": True,
        "theme": arc.theme,
        "day_index": day_idx,
        "today_seed": seeds[day_idx] if day_idx < len(seeds) else "",
        "seeds": seeds,
    })


@router.post("/api/daily/weekly-arc")
async def create_weekly_arc(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    body = await request.json()
    birth_date_str = body.get("birth_date", "")
    try:
        birth_date = date.fromisoformat(birth_date_str)
    except (ValueError, TypeError):
        return JSONResponse({"error": "Invalid birth_date"}, status_code=400)

    today = date.today()
    monday = _monday_of(today)

    result = await db.execute(
        select(WeeklyArc)
        .where(WeeklyArc.user_id == user.id, WeeklyArc.week_start == monday)
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        seeds = [s.strip() for s in existing.story_seed.split(",")]
        day_idx = (today - monday).days
        return JSONResponse({
            "has_arc": True,
            "theme": existing.theme,
            "day_index": day_idx,
            "today_seed": seeds[day_idx] if day_idx < len(seeds) else "",
            "seeds": seeds,
        })

    life_path = calculate_life_path(birth_date.year, birth_date.month, birth_date.day)
    user_prompt = f"生年月日: {birth_date.isoformat()}\nライフパス: {life_path.get('life_path', '不明')}\n今週の月曜日: {monday.isoformat()}"

    for attempt in range(2):
        raw = await generate_message(WEEKLY_ARC_PROMPT, user_prompt)
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else json.loads(raw)
            break
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt == 1:
                return JSONResponse({"error": "生成に失敗しました"}, status_code=500)

    arc = WeeklyArc(
        user_id=user.id,
        birth_date=birth_date,
        week_start=monday,
        theme=data.get("theme", ""),
        story_seed=data.get("story_seed", ""),
    )
    db.add(arc)
    await db.commit()

    seeds = [s.strip() for s in arc.story_seed.split(",")]
    day_idx = (today - monday).days
    return JSONResponse({
        "has_arc": True,
        "theme": arc.theme,
        "day_index": day_idx,
        "today_seed": seeds[day_idx] if day_idx < len(seeds) else "",
        "seeds": seeds,
    })
