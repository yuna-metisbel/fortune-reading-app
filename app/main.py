from contextlib import asynccontextmanager
from pathlib import Path

import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers import chat, pages, profiles, readings

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add image_url column if it doesn't exist (simple migration)
        try:
            await conn.execute(sa.text("ALTER TABLE readings ADD COLUMN image_url TEXT"))
        except Exception:
            pass  # Column already exists
    yield


app = FastAPI(title="星図リーディング", lifespan=lifespan, debug=True)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(pages.router)
app.include_router(profiles.router)
app.include_router(readings.router)
app.include_router(chat.router)
