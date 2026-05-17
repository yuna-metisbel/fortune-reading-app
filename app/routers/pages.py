from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_browser_user
from app.models import Profile, Reading, User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    result = await db.execute(
        select(Reading)
        .where(Reading.user_id == user.id)
        .order_by(Reading.created_at.desc())
    )
    readings = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "readings": readings})


@router.get("/sample", response_class=HTMLResponse)
async def sample_page(request: Request):
    return templates.TemplateResponse("sample.html", {"request": request})


@router.get("/reading/new", response_class=HTMLResponse)
async def reading_new(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
):
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == user.id)
        .order_by(Profile.created_at.desc())
    )
    profiles = result.scalars().all()
    return templates.TemplateResponse("reading_form.html", {"request": request, "profiles": profiles})


@router.get("/compatibility/new", response_class=HTMLResponse)
async def compatibility_new(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_browser_user),
    from_nick: str = "",
    from_bd: str = "",
):
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == user.id)
        .order_by(Profile.created_at.desc())
    )
    profiles = result.scalars().all()
    return templates.TemplateResponse("compatibility_form.html", {
        "request": request,
        "profiles": profiles,
        "from_nick": from_nick,
        "from_bd": from_bd,
    })


@router.get("/reading/generate/{reading_id}")
async def reading_generate(request: Request, reading_id: int):
    return templates.TemplateResponse("reading_generate.html", {"request": request, "reading_id": reading_id})
