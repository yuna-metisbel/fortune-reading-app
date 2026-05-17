"""Claude API ストリーミングクライアント"""
from collections.abc import AsyncIterator

import anthropic

from app.config import settings


def get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def generate_message(
    system_prompt: str,
    user_prompt: str,
) -> str:
    client = get_client()
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


async def stream_message(
    system_prompt: str,
    user_prompt: str,
    messages: list[dict] | None = None,
) -> AsyncIterator[str]:
    client = get_client()
    if messages is None:
        messages = [{"role": "user", "content": user_prompt}]

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
