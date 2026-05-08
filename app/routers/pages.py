from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Profile, Reading

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reading).order_by(Reading.created_at.desc()))
    readings = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "readings": readings})


@router.get("/reading/new", response_class=HTMLResponse)
async def reading_new(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    profiles = result.scalars().all()
    return templates.TemplateResponse("reading_form.html", {"request": request, "profiles": profiles})


@router.get("/compatibility/new", response_class=HTMLResponse)
async def compatibility_new(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    profiles = result.scalars().all()
    return templates.TemplateResponse("compatibility_form.html", {"request": request, "profiles": profiles})
