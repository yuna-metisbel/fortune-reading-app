from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.models import ChatMessage, ChatSession, Reading
from app.services.claude_client import stream_message
from app.services.prompts import SYSTEM_PROMPT_CHAT

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class ChatSendRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# GET /chat/{reading_id}
# ---------------------------------------------------------------------------

@router.get("/chat/{reading_id}")
async def chat_page(
    request: Request,
    reading_id: int,
    db: AsyncSession = Depends(get_db),
):
    reading = await db.get(Reading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    result = await db.execute(
        select(ChatSession).where(ChatSession.reading_id == reading_id).limit(1)
    )
    session = result.scalar_one_or_none()

    if session is None:
        session = ChatSession(reading_id=reading_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "reading": reading,
            "messages": messages,
            "session_id": session.id,
        },
    )


# ---------------------------------------------------------------------------
# POST /api/chat/{reading_id}/send
# ---------------------------------------------------------------------------

@router.post("/api/chat/{reading_id}/send")
async def chat_send(
    reading_id: int,
    body: ChatSendRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    reading = await db.get(Reading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    result = await db.execute(
        select(ChatSession).where(ChatSession.reading_id == reading_id).limit(1)
    )
    session = result.scalar_one_or_none()

    if session is None:
        session = ChatSession(reading_id=reading_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    session_id = session.id

    user_msg = ChatMessage(session_id=session_id, role="user", content=body.message)
    db.add(user_msg)
    await db.commit()

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    all_messages = result.scalars().all()

    api_messages = [{"role": msg.role, "content": msg.content} for msg in all_messages]

    system_prompt = SYSTEM_PROMPT_CHAT.format(reading_content=reading.content)

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in stream_message(system_prompt, body.message, messages=api_messages):
            chunks.append(chunk)
            yield f"data: {chunk}\n\n"

        content = "".join(chunks)

        async with async_session() as save_db:
            assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=content)
            save_db.add(assistant_msg)
            await save_db.commit()

        yield "event: done\ndata: ok\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
