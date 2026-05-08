from datetime import date

import pytest

from app.models import ChatMessage, ChatSession, Profile, Reading, User


@pytest.mark.asyncio
async def test_create_user_and_profile(db_session):
    user = User(name="テストユーザー")
    db_session.add(user)
    await db_session.flush()

    profile = Profile(
        user_id=user.id,
        nickname="ゆうな",
        birth_date=date(1995, 6, 26),
    )
    db_session.add(profile)
    await db_session.flush()

    assert user.id is not None
    assert profile.id is not None
    assert profile.user_id == user.id


@pytest.mark.asyncio
async def test_create_reading_with_chat(db_session):
    user = User(name="テスト")
    db_session.add(user)
    await db_session.flush()

    profile = Profile(user_id=user.id, nickname="テスト", birth_date=date(2000, 1, 1))
    db_session.add(profile)
    await db_session.flush()

    reading = Reading(
        user_id=user.id,
        type="personal",
        profile_id=profile.id,
        theme="仕事運",
        content="# リーディング結果",
        prompt_used="テストプロンプト",
    )
    db_session.add(reading)
    await db_session.flush()

    session = ChatSession(reading_id=reading.id)
    db_session.add(session)
    await db_session.flush()

    msg = ChatMessage(session_id=session.id, role="user", content="こんにちは")
    db_session.add(msg)
    await db_session.flush()

    assert reading.id is not None
    assert session.reading_id == reading.id
    assert msg.session_id == session.id
