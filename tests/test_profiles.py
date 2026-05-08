from datetime import date

import pytest

from app.models import Profile, User


@pytest.mark.asyncio
async def test_create_and_list_profiles(db_session):
    user = User(name="test")
    db_session.add(user)
    await db_session.flush()

    p1 = Profile(user_id=user.id, nickname="ゆうな", birth_date=date(1995, 6, 26))
    p2 = Profile(user_id=user.id, nickname="彼", birth_date=date(1999, 5, 7), blood_type="A")
    db_session.add_all([p1, p2])
    await db_session.flush()

    from sqlalchemy import select
    result = await db_session.execute(select(Profile).order_by(Profile.id))
    profiles = result.scalars().all()

    assert len(profiles) == 2
    assert profiles[0].nickname == "ゆうな"
    assert profiles[1].blood_type == "A"
