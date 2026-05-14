from contextlib import asynccontextmanager
from pathlib import Path

import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import chat, pages, payment, profiles, readings

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
        ]:
            try:
                await conn.execute(sa.text(col_sql))
            except Exception:
                pass
    yield


app = FastAPI(title="星図リーディング", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

if settings.images_dir:
    _img_dir = Path(settings.images_dir)
    _img_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/poster-images", StaticFiles(directory=str(_img_dir)), name="poster-images")

app.include_router(pages.router)
app.include_router(profiles.router)
app.include_router(readings.router)
app.include_router(chat.router)
app.include_router(payment.router)
