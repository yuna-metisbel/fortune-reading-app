from datetime import date, time

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Profile, User

router = APIRouter(prefix="/api/profiles")


class ProfileCreate(BaseModel):
    nickname: str
    birth_date: date
    birth_time: time | None = None
    birth_place: str | None = None
    gender: str | None = None
    blood_type: str | None = None


@router.post("")
async def create_profile(body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    # Auto-create a default User if none exists
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(name="default")
        db.add(user)
        await db.flush()

    profile = Profile(
        user_id=user.id,
        nickname=body.nickname,
        birth_date=body.birth_date,
        birth_time=body.birth_time,
        birth_place=body.birth_place,
        gender=body.gender,
        blood_type=body.blood_type,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return {"id": profile.id, "nickname": profile.nickname}


@router.get("")
async def list_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    profiles = result.scalars().all()

    return [
        {
            "id": p.id,
            "nickname": p.nickname,
            "birth_date": p.birth_date,
            "birth_time": p.birth_time,
            "birth_place": p.birth_place,
            "gender": p.gender,
            "blood_type": p.blood_type,
        }
        for p in profiles
    ]
