from contextlib import asynccontextmanager
from pathlib import Path

import sqlalchemy as sa
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import engine
from app.deps import BrowserIdMiddleware
from app.models import Base
from app.routers import chat, daily, daily_compat, face_reading, pages, palm_reading, payment, profiles, readings

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for col_sql in [
            "ALTER TABLE readings ADD COLUMN image_url TEXT",
            "ALTER TABLE readings ADD COLUMN payment_status TEXT DEFAULT 'free'",
            "ALTER TABLE readings ADD COLUMN stripe_session_id TEXT",
            "ALTER TABLE readings ADD COLUMN form_data_json TEXT",
            "ALTER TABLE users ADD COLUMN browser_id TEXT",
            "ALTER TABLE readings ADD COLUMN type_badge TEXT",
            "ALTER TABLE daily_fortunes ADD COLUMN prediction TEXT",
            "ALTER TABLE daily_fortunes ADD COLUMN prediction_result TEXT",
            "ALTER TABLE daily_fortunes ADD COLUMN prediction_checked_at DATETIME",
        ]:
            try:
                await conn.execute(sa.text(col_sql))
            except Exception:
                pass
    yield


app = FastAPI(title="星図リーディング", lifespan=lifespan)
app.add_middleware(BrowserIdMiddleware)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

if settings.images_dir:
    _img_dir = Path(settings.images_dir)
    _img_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/poster-images", StaticFiles(directory=str(_img_dir)), name="poster-images")

VALID_THEMES = {"default", "a", "b", "c"}


@app.get("/theme/{theme_name}")
async def switch_theme(theme_name: str):
    from fastapi.responses import RedirectResponse
    t = theme_name if theme_name in VALID_THEMES else "default"
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("luna_theme", t, max_age=60 * 60 * 24 * 365)
    return resp


app.include_router(pages.router)
app.include_router(daily.router)
app.include_router(daily_compat.router)
app.include_router(profiles.router)
app.include_router(readings.router)
app.include_router(chat.router)
app.include_router(payment.router)
app.include_router(face_reading.router)
app.include_router(palm_reading.router)
