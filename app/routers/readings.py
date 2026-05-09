import re
from datetime import date, time
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session, get_db
from app.models import Profile, Reading, User
from app.services.claude_client import stream_message
from app.services.image_generator import generate_reading_image
from app.services.prompts import (
    SYSTEM_PROMPT_COMPATIBILITY,
    SYSTEM_PROMPT_PERSONAL,
    build_compatibility_user_prompt,
    build_personal_user_prompt,
)
from app.services.numerology import calculate_life_path
from app.services.rokusei import calculate_cycle_position, calculate_rokusei
from app.services.shichusuimei import calculate_year_pillar

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class PersonalReadingRequest(BaseModel):
    nickname: str
    birth_date: str
    birth_time: str | None = None
    birth_place: str | None = None
    gender: str | None = None
    blood_type: str | None = None
    theme: str


class CompatibilityReadingRequest(BaseModel):
    person1_nickname: str
    person1_birth_date: str
    person1_birth_time: str | None = None
    person1_birth_place: str | None = None
    person1_gender: str | None = None
    person1_blood_type: str | None = None
    person2_nickname: str
    person2_birth_date: str
    person2_birth_time: str | None = None
    person2_birth_place: str | None = None
    person2_gender: str | None = None
    person2_blood_type: str | None = None
    relationship_type: str
    met_date: str | None = None
    theme: str


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

async def _get_or_create_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(name="default")
        db.add(user)
        await db.flush()
    return user


def _compute_fortune_data(birth_date_str: str) -> tuple[dict | None, dict | None, dict | None]:
    """生年月日文字列から六星占術・四柱推命・数秘術の計算結果を返す。"""
    try:
        bd = date.fromisoformat(birth_date_str)
        rokusei_result = calculate_rokusei(bd.year, bd.month, bd.day)
        current_year = date.today().year
        cycle = calculate_cycle_position(bd.year, bd.month, bd.day, current_year)
        rokusei_result["cycle_position"] = cycle["cycle_position"]
        rokusei_result["is_daisakkai"] = cycle["is_daisakkai"]
        rokusei_result["cycle_year"] = cycle["cycle_year"]
        rokusei_result["star_full"] += f"／{current_year}年の運勢位置：{cycle['cycle_position']}"
        if cycle["is_daisakkai"]:
            rokusei_result["star_full"] += "【大殺界】"
        shichusuimei_result = calculate_year_pillar(bd.year)
        numerology_result = calculate_life_path(bd.year, bd.month, bd.day)
        return rokusei_result, shichusuimei_result, numerology_result
    except (ValueError, TypeError):
        return None, None, None


async def _get_or_create_profile(
    db: AsyncSession,
    user_id: int,
    nickname: str,
    birth_date_str: str,
    birth_time_str: str | None,
    birth_place: str | None,
    gender: str | None,
    blood_type: str | None,
) -> Profile:
    birth_date = date.fromisoformat(birth_date_str)

    birth_time: time | None = None
    if birth_time_str:
        birth_time = time.fromisoformat(birth_time_str)

    profile = Profile(
        user_id=user_id,
        nickname=nickname,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        gender=gender,
        blood_type=blood_type,
    )
    db.add(profile)
    await db.flush()
    return profile


# ---------------------------------------------------------------------------
# POST /api/readings/personal/stream
# ---------------------------------------------------------------------------

@router.post("/api/readings/personal/stream")
async def personal_stream(
    body: PersonalReadingRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    user = await _get_or_create_user(db)
    profile = await _get_or_create_profile(
        db,
        user_id=user.id,
        nickname=body.nickname,
        birth_date_str=body.birth_date,
        birth_time_str=body.birth_time,
        birth_place=body.birth_place,
        gender=body.gender,
        blood_type=body.blood_type,
    )

    rokusei_result, shichusuimei_result, numerology_result = _compute_fortune_data(body.birth_date)

    user_prompt = build_personal_user_prompt(
        nickname=body.nickname,
        birth_date=body.birth_date,
        birth_time=body.birth_time,
        birth_place=body.birth_place,
        gender=body.gender,
        blood_type=body.blood_type,
        theme=body.theme,
        rokusei_result=rokusei_result,
        shichusuimei_result=shichusuimei_result,
        numerology_result=numerology_result,
    )

    reading = Reading(
        user_id=user.id,
        type="personal",
        profile_id=profile.id,
        theme=body.theme,
        content="",
        prompt_used=user_prompt,
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    reading_id = reading.id

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(SYSTEM_PROMPT_PERSONAL, user_prompt):
            chunks.append(chunk)
            yield f"data: {chunk}\n\n"

        content = "".join(chunks)

        async with async_session() as save_db:
            r = await save_db.get(Reading, reading_id)
            r.content = content
            await save_db.commit()

        yield f"event: done\ndata: {reading_id}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# POST /api/readings/compatibility/stream
# ---------------------------------------------------------------------------

@router.post("/api/readings/compatibility/stream")
async def compatibility_stream(
    body: CompatibilityReadingRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    user = await _get_or_create_user(db)

    profile1 = await _get_or_create_profile(
        db,
        user_id=user.id,
        nickname=body.person1_nickname,
        birth_date_str=body.person1_birth_date,
        birth_time_str=body.person1_birth_time,
        birth_place=body.person1_birth_place,
        gender=body.person1_gender,
        blood_type=body.person1_blood_type,
    )
    profile2 = await _get_or_create_profile(
        db,
        user_id=user.id,
        nickname=body.person2_nickname,
        birth_date_str=body.person2_birth_date,
        birth_time_str=body.person2_birth_time,
        birth_place=body.person2_birth_place,
        gender=body.person2_gender,
        blood_type=body.person2_blood_type,
    )

    met_date: date | None = None
    if body.met_date:
        try:
            met_date = date.fromisoformat(body.met_date)
        except ValueError:
            met_date = None

    p1_rokusei, p1_shichusuimei, p1_numerology = _compute_fortune_data(body.person1_birth_date)
    p2_rokusei, p2_shichusuimei, p2_numerology = _compute_fortune_data(body.person2_birth_date)

    user_prompt = build_compatibility_user_prompt(
        person1_nickname=body.person1_nickname,
        person1_birth_date=body.person1_birth_date,
        person1_birth_time=body.person1_birth_time,
        person1_birth_place=body.person1_birth_place,
        person1_gender=body.person1_gender,
        person1_blood_type=body.person1_blood_type,
        person2_nickname=body.person2_nickname,
        person2_birth_date=body.person2_birth_date,
        person2_birth_time=body.person2_birth_time,
        person2_birth_place=body.person2_birth_place,
        person2_gender=body.person2_gender,
        person2_blood_type=body.person2_blood_type,
        relationship_type=body.relationship_type,
        met_date=body.met_date,
        theme=body.theme,
        person1_rokusei=p1_rokusei,
        person1_shichusuimei=p1_shichusuimei,
        person1_numerology=p1_numerology,
        person2_rokusei=p2_rokusei,
        person2_shichusuimei=p2_shichusuimei,
        person2_numerology=p2_numerology,
    )

    reading = Reading(
        user_id=user.id,
        type="compatibility",
        profile_id=profile1.id,
        profile_id_2=profile2.id,
        relationship_type=body.relationship_type,
        met_date=met_date,
        theme=body.theme,
        content="",
        prompt_used=user_prompt,
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    reading_id = reading.id

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(SYSTEM_PROMPT_COMPATIBILITY, user_prompt):
            chunks.append(chunk)
            yield f"data: {chunk}\n\n"

        content = "".join(chunks)

        async with async_session() as save_db:
            r = await save_db.get(Reading, reading_id)
            r.content = content
            await save_db.commit()

        yield f"event: done\ndata: {reading_id}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# GET /reading/{reading_id}
# ---------------------------------------------------------------------------

@router.get("/reading/{reading_id}")
async def reading_result(
    request: Request,
    reading_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reading).where(Reading.id == reading_id).options(selectinload(Reading.profile))
    )
    reading = result.scalar_one_or_none()
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Parse markdown into sections
    sections = []
    if reading.content:
        # Split by ## headers
        parts = re.split(r'^## ', reading.content, flags=re.MULTILINE)
        for part in parts[1:]:  # skip the first empty/intro part
            lines = part.strip().split('\n', 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            # Extract key points (lines starting with - or *)
            key_points = []
            for line in body.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    key_points.append(line[2:])
                elif line.startswith('**') and line.endswith('**'):
                    key_points.append(line.strip('*'))
            sections.append({
                "title": title,
                "body": body,
                "key_points": key_points[:5],  # top 5 points for summary
            })

    # Map section titles to icons and short labels for summary card
    section_icons = {
        "全体要約": "🔮", "性格": "🌙", "才能": "✨", "強み": "✨",
        "注意": "⚡", "課題": "⚡", "仕事": "💼", "お金": "💰",
        "恋愛": "💕", "人間関係": "🤝", "今年": "📅", "月別": "🗓️",
        "今すぐ": "⭐", "メッセージ": "💌",
    }

    for section in sections:
        icon = "✦"
        for keyword, emoji in section_icons.items():
            if keyword in section["title"]:
                icon = emoji
                break
        section["icon"] = icon

    try:
        return templates.TemplateResponse(
            "reading_result.html", {"request": request, "reading": reading, "sections": sections}
        )
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)


# ---------------------------------------------------------------------------
# POST /api/readings/{reading_id}/generate-image
# ---------------------------------------------------------------------------

@router.post("/api/readings/{reading_id}/generate-image")
async def generate_image(
    reading_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reading).where(Reading.id == reading_id).options(selectinload(Reading.profile))
    )
    reading = result.scalar_one_or_none()
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    if reading.image_url:
        return JSONResponse({"image_url": reading.image_url})

    nickname = reading.profile.nickname if reading.profile else "あなた"
    image_url = await generate_reading_image(
        nickname=nickname,
        sections_summary="",
    )

    if image_url:
        reading.image_url = image_url
        await db.commit()

    return JSONResponse({"image_url": image_url})
