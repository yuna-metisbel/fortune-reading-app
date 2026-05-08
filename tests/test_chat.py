from datetime import date

import pytest

from app.models import ChatMessage, ChatSession, Profile, Reading, User


@pytest.mark.asyncio
async def test_chat_session_with_messages(db_session):
    user = User(name="test")
    db_session.add(user)
    await db_session.flush()

    profile = Profile(user_id=user.id, nickname="テスト", birth_date=date(2000, 1, 1))
    db_session.add(profile)
    await db_session.flush()

    reading = Reading(
        user_id=user.id, type="personal", profile_id=profile.id,
        theme="仕事", content="テストリーディング", prompt_used="テスト",
    )
    db_session.add(reading)
    await db_session.flush()

    session = ChatSession(reading_id=reading.id)
    db_session.add(session)
    await db_session.flush()

    msg1 = ChatMessage(session_id=session.id, role="user", content="こんにちは")
    msg2 = ChatMessage(session_id=session.id, role="assistant", content="はい、お話しましょう")
    db_session.add_all([msg1, msg2])
    await db_session.flush()

    from sqlalchemy import select
    result = await db_session.execute(
        select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
