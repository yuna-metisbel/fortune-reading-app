import asyncio
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
        bd = date.fromisoformat(_zen_to_han(birth_date_str))
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


def _zen_to_han(s: str) -> str:
    return s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))


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
    birth_date = date.fromisoformat(_zen_to_han(birth_date_str))

    birth_time: time | None = None
    if birth_time_str:
        birth_time = time.fromisoformat(_zen_to_han(birth_time_str))

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

    async def _generate_bg_image(rid: int, nick: str):
        try:
            url = await generate_reading_image(nickname=nick)
            if url:
                async with async_session() as save_db:
                    r = await save_db.get(Reading, rid)
                    if r:
                        r.image_url = url
                        await save_db.commit()
        except Exception:
            pass

    bg_task = asyncio.create_task(_generate_bg_image(reading_id, body.nickname))

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(SYSTEM_PROMPT_PERSONAL, user_prompt):
            chunks.append(chunk)
            yield f"data: {chunk.replace(chr(10), '⏎')}\n\n"

        content = "".join(chunks)

        async with async_session() as save_db:
            r = await save_db.get(Reading, reading_id)
            r.content = content
            await save_db.commit()

        try:
            await asyncio.wait_for(asyncio.shield(bg_task), timeout=5.0)
        except (asyncio.TimeoutError, Exception):
            pass

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

    async def _generate_bg_image(rid: int, nick: str):
        try:
            url = await generate_reading_image(nickname=nick)
            if url:
                async with async_session() as save_db:
                    r = await save_db.get(Reading, rid)
                    if r:
                        r.image_url = url
                        await save_db.commit()
        except Exception:
            pass

    bg_task = asyncio.create_task(_generate_bg_image(reading_id, body.person1_nickname))

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(SYSTEM_PROMPT_COMPATIBILITY, user_prompt):
            chunks.append(chunk)
            yield f"data: {chunk.replace(chr(10), '⏎')}\n\n"

        content = "".join(chunks)

        async with async_session() as save_db:
            r = await save_db.get(Reading, reading_id)
            r.content = content
            await save_db.commit()

        try:
            await asyncio.wait_for(asyncio.shield(bg_task), timeout=5.0)
        except (asyncio.TimeoutError, Exception):
            pass

        yield f"event: done\ndata: {reading_id}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# POST /api/readings/generate/{reading_id} — 決済完了後のリーディング生成
# ---------------------------------------------------------------------------

@router.post("/api/readings/generate/{reading_id}")
async def generate_paid_reading(
    reading_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    reading = await db.get(Reading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.payment_status != "paid":
        raise HTTPException(status_code=403, detail="Payment required")

    user = await _get_or_create_user(db)

    if reading.type == "personal":
        profile = await _get_or_create_profile(
            db, user_id=user.id,
            nickname=body.get("nickname", ""),
            birth_date_str=body.get("birth_date", "2000-01-01"),
            birth_time_str=body.get("birth_time"),
            birth_place=body.get("birth_place"),
            gender=body.get("gender"),
            blood_type=body.get("blood_type"),
        )
        reading.profile_id = profile.id
        await db.commit()

        rokusei, shichusuimei, numerology = _compute_fortune_data(body.get("birth_date", "2000-01-01"))
        user_prompt = build_personal_user_prompt(
            nickname=body.get("nickname", ""),
            birth_date=body.get("birth_date", ""),
            birth_time=body.get("birth_time"),
            birth_place=body.get("birth_place"),
            gender=body.get("gender"),
            blood_type=body.get("blood_type"),
            theme=body.get("theme", ""),
            rokusei_result=rokusei,
            shichusuimei_result=shichusuimei,
            numerology_result=numerology,
        )
        system_prompt = SYSTEM_PROMPT_PERSONAL
    else:
        profile1 = await _get_or_create_profile(
            db, user_id=user.id,
            nickname=body.get("person1_nickname", ""),
            birth_date_str=body.get("person1_birth_date", "2000-01-01"),
            birth_time_str=body.get("person1_birth_time"),
            birth_place=body.get("person1_birth_place"),
            gender=body.get("person1_gender"),
            blood_type=body.get("person1_blood_type"),
        )
        profile2 = await _get_or_create_profile(
            db, user_id=user.id,
            nickname=body.get("person2_nickname", ""),
            birth_date_str=body.get("person2_birth_date", "2000-01-01"),
            birth_time_str=body.get("person2_birth_time"),
            birth_place=body.get("person2_birth_place"),
            gender=body.get("person2_gender"),
            blood_type=body.get("person2_blood_type"),
        )
        reading.profile_id = profile1.id
        reading.profile_id_2 = profile2.id
        if body.get("met_date"):
            try:
                reading.met_date = date.fromisoformat(body["met_date"])
            except ValueError:
                pass
        await db.commit()

        p1_rok, p1_shi, p1_num = _compute_fortune_data(body.get("person1_birth_date", "2000-01-01"))
        p2_rok, p2_shi, p2_num = _compute_fortune_data(body.get("person2_birth_date", "2000-01-01"))
        user_prompt = build_compatibility_user_prompt(
            person1_nickname=body.get("person1_nickname", ""),
            person1_birth_date=body.get("person1_birth_date", ""),
            person1_birth_time=body.get("person1_birth_time"),
            person1_birth_place=body.get("person1_birth_place"),
            person1_gender=body.get("person1_gender"),
            person1_blood_type=body.get("person1_blood_type"),
            person2_nickname=body.get("person2_nickname", ""),
            person2_birth_date=body.get("person2_birth_date", ""),
            person2_birth_time=body.get("person2_birth_time"),
            person2_birth_place=body.get("person2_birth_place"),
            person2_gender=body.get("person2_gender"),
            person2_blood_type=body.get("person2_blood_type"),
            relationship_type=body.get("relationship_type", ""),
            met_date=body.get("met_date"),
            theme=body.get("theme", ""),
            person1_rokusei=p1_rok, person1_shichusuimei=p1_shi, person1_numerology=p1_num,
            person2_rokusei=p2_rok, person2_shichusuimei=p2_shi, person2_numerology=p2_num,
        )
        system_prompt = SYSTEM_PROMPT_COMPATIBILITY

    reading.prompt_used = user_prompt
    await db.commit()

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(system_prompt, user_prompt):
            chunks.append(chunk)
            yield f"data: {chunk.replace(chr(10), '⏎')}\n\n"
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
        select(Reading).where(Reading.id == reading_id).options(
            selectinload(Reading.profile),
            selectinload(Reading.profile_2),
        )
    )
    reading = result.scalar_one_or_none()
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Parse markdown into sections
    sections = []
    if reading.content:
        parts = re.split(r'^## ', reading.content, flags=re.MULTILINE)
        for part in parts[1:]:
            lines = part.strip().split('\n', 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            key_points = []
            catchcopy_found = False
            for line in body.split('\n'):
                stripped = line.strip()
                if stripped.startswith('- ') or stripped.startswith('* '):
                    point = stripped[2:].strip('「」')
                    key_points.append(point)
                elif stripped.startswith('**') and stripped.endswith('**'):
                    if not catchcopy_found:
                        key_points.append(stripped.strip('*').strip('「」'))
                        catchcopy_found = True
            clean_title = re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]\s*', '', title)
            clean_title = clean_title.replace('・発信', '').replace('・発信力', '')
            if '最後のメッセージ' in clean_title:
                clean_title = '魂のメッセージ'

            body_lines = body.split('\n')
            summary_paragraphs = []
            for bl in body_lines:
                bl_s = bl.strip()
                if not bl_s:
                    if summary_paragraphs and summary_paragraphs[-1] != '':
                        summary_paragraphs.append('')
                    continue
                if bl_s.startswith('- ') or bl_s.startswith('* '):
                    continue
                if bl.startswith('  ') or bl.startswith('\t'):
                    continue
                if bl_s.startswith('**') and bl_s.endswith('**'):
                    if '枚目' not in bl_s and 'からのメッセージ' not in bl_s:
                        continue
                if re.match(r'^.{1,20}へ$', bl_s):
                    continue
                if bl_s.startswith('---'):
                    continue
                if bl_s.startswith('|'):
                    continue
                summary_paragraphs.append(bl_s)
            while summary_paragraphs and summary_paragraphs[-1] == '':
                summary_paragraphs.pop()

            sections.append({
                "title": clean_title,
                "body": body,
                "detail_body": '\n'.join(summary_paragraphs),
                "key_points": key_points[:5],
            })

    # Section theme config: slug, color, icon SVG
    section_themes = [
        {"slug": "summary",  "color": "#c4b5fd", "bg": "rgba(196,181,253,.12)"},
        {"slug": "personality", "color": "#d4a0ff", "bg": "rgba(212,160,255,.12)"},
        {"slug": "strength", "color": "#a5b4fc", "bg": "rgba(165,180,252,.12)"},
        {"slug": "caution",  "color": "#f9a8d4", "bg": "rgba(249,168,212,.12)"},
        {"slug": "career",   "color": "#34d399", "bg": "rgba(52,211,153,.12)"},
        {"slug": "love",     "color": "#f5c6ff", "bg": "rgba(245,198,255,.12)"},
        {"slug": "yearly",   "color": "#60a5fa", "bg": "rgba(96,165,250,.12)"},
        {"slug": "monthly",  "color": "#c4b5fd", "bg": "rgba(196,181,253,.12)"},
        {"slug": "action",   "color": "#fbbf24", "bg": "rgba(251,191,36,.12)"},
        {"slug": "message",  "color": "#e9d5ff", "bg": "rgba(233,213,255,.15)"},
    ]

    for i, section in enumerate(sections):
        theme = section_themes[i] if i < len(section_themes) else section_themes[0]
        section["theme"] = theme
        # Clean key_points: remove 「」, strip numbers like "5つ" "3つ"
        cleaned = []
        for kp in section.get("key_points", []):
            kp = kp.strip('「」')
            kp = re.sub(r'\s*\d+つ$', '', kp)
            cleaned.append(kp)
        section["key_points"] = cleaned

    # Parse monthly data from 月別 section
    monthly_data = []
    monthly_section_idx = None
    for i, section in enumerate(sections):
        if "月別" in section["title"] or "タイムライン" in section["title"]:
            monthly_section_idx = i
            for line in section["body"].split('\n'):
                m = re.match(r'\|\s*(\d{1,2})月\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', line)
                if m:
                    monthly_data.append({
                        "num": m.group(1),
                        "keyword": m.group(2).strip().replace('**', ''),
                        "action": m.group(3).strip().replace('**', ''),
                        "note": m.group(4).strip().replace('**', ''),
                    })
            break

    # Remove monthly section from accordion if we have grid data
    if monthly_data and monthly_section_idx is not None:
        sections.pop(monthly_section_idx)

    # Remove yearly theme section if it references wrong year (e.g. 2025)
    sections = [s for s in sections if not ("今年" in s["title"] and "2025" in s["title"])]

    is_compat = reading.type == "compatibility"

    if is_compat:
        compat_themes = [
            {"slug": "overview",  "color": "#d4a0ff", "bg": "rgba(212,160,255,.12)"},
            {"slug": "essence",   "color": "#c4b5fd", "bg": "rgba(196,181,253,.12)"},
            {"slug": "chemistry", "color": "#f5c6ff", "bg": "rgba(245,198,255,.12)"},
            {"slug": "challenge", "color": "#f9a8d4", "bg": "rgba(249,168,212,.12)"},
            {"slug": "love",      "color": "#e9d5ff", "bg": "rgba(233,213,255,.15)"},
            {"slug": "timeline",  "color": "#60a5fa", "bg": "rgba(96,165,250,.12)"},
            {"slug": "action",    "color": "#fbbf24", "bg": "rgba(251,191,36,.12)"},
            {"slug": "message",   "color": "#34d399", "bg": "rgba(52,211,153,.12)"},
        ]
        if monthly_data:
            compat_themes = [t for t in compat_themes if t["slug"] != "timeline"]
        for i, section in enumerate(sections):
            theme = compat_themes[i] if i < len(compat_themes) else compat_themes[0]
            section["theme"] = theme

    return templates.TemplateResponse(
        "reading_result.html", {
            "request": request,
            "reading": reading,
            "sections": sections,
            "monthly_data": monthly_data,
            "is_compat": is_compat,
        }
    )


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

    soul_theme = ""
    keywords = []
    if reading.content:
        parts = re.split(r'^## ', reading.content, flags=re.MULTILINE)
        for part in parts[1:]:
            lines = part.strip().split('\n', 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            if not soul_theme:
                for line in body.split('\n'):
                    line = line.strip()
                    if line.startswith('**') and line.endswith('**'):
                        soul_theme = line.strip('*')
                        break
            for line in body.split('\n'):
                line = line.strip()
                if (line.startswith('- ') or line.startswith('* ')) and len(keywords) < 6:
                    kw = line[2:].replace('**', '').strip()
                    if len(kw) <= 12:
                        keywords.append(kw)

    image_url = await generate_reading_image(
        nickname=nickname,
        soul_theme=soul_theme,
        keywords=keywords,
    )

    if image_url:
        reading.image_url = image_url
        await db.commit()

    return JSONResponse({"image_url": image_url})


# ---------------------------------------------------------------------------
# POST /api/readings/{reading_id}/generate-poster
# ---------------------------------------------------------------------------

@router.post("/api/readings/{reading_id}/generate-poster")
async def generate_poster(
    reading_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reading).where(Reading.id == reading_id).options(selectinload(Reading.profile))
    )
    reading = result.scalar_one_or_none()
    if reading is None:
        return JSONResponse({"error": "Reading not found"}, status_code=404)

    nickname = reading.profile.nickname if reading.profile else "あなた"

    image_url = await generate_reading_image(nickname=nickname)

    if image_url:
        reading.image_url = image_url
        await db.commit()
        return JSONResponse({"image_url": image_url})
    return JSONResponse({"error": "Generation failed"}, status_code=500)


@router.get("/api/diagnostics/image-config")
async def image_config_check():
    from app.services.image_generator import IMAGES_DIR, _URL_PREFIX
    from app.config import settings as _s
    import os
    return JSONResponse({
        "openai_key_set": bool(_s.openai_api_key),
        "openai_key_prefix": _s.openai_api_key[:8] + "..." if _s.openai_api_key else None,
        "images_dir": str(IMAGES_DIR),
        "images_dir_exists": IMAGES_DIR.exists(),
        "url_prefix": _URL_PREFIX,
        "data_mount_exists": os.path.isdir("/data"),
    })


@router.get("/api/diagnostics/test-dalle")
async def test_dalle():
    import openai
    from app.config import settings as _s
    if not _s.openai_api_key:
        return JSONResponse({"error": "OPENAI_API_KEY not set"})
    try:
        client = openai.AsyncOpenAI(api_key=_s.openai_api_key)
        response = await client.models.list()
        models = [m.id for m in response.data if "dall" in m.id.lower() or "gpt-image" in m.id.lower()]
        return JSONResponse({"status": "ok", "image_models": models})
    except Exception as e:
        return JSONResponse({"error": str(e)})
