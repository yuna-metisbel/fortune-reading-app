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


SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


async def generate_vision_message(
    system_prompt: str,
    user_prompt: str,
    image_base64: str,
    media_type: str = "image/jpeg",
) -> str:
    if media_type not in SUPPORTED_IMAGE_TYPES:
        media_type = "image/jpeg"
    client = get_client()
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": user_prompt},
            ],
        }],
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
