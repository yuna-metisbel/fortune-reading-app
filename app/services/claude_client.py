"""Claude API ストリーミングクライアント"""
from collections.abc import AsyncIterator

import anthropic

from app.config import settings

# モデル定数
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU = "claude-haiku-3-5-20241022"


def get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


def _system_with_cache(system_prompt: str) -> list[dict]:
    """システムプロンプトにプロンプトキャッシュを適用する。"""
    return [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]


async def generate_message(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str = MODEL_HAIKU,
    max_tokens: int = 1024,
) -> str:
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=_system_with_cache(system_prompt),
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


async def generate_vision_message(
    system_prompt: str,
    user_prompt: str,
    image_base64: str,
    media_type: str = "image/jpeg",
    *,
    model: str = MODEL_HAIKU,
    max_tokens: int = 1024,
) -> str:
    if media_type not in SUPPORTED_IMAGE_TYPES:
        media_type = "image/jpeg"
    client = get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=_system_with_cache(system_prompt),
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
    *,
    model: str = MODEL_SONNET,
    max_tokens: int = 8192,
) -> AsyncIterator[str]:
    client = get_client()
    if messages is None:
        messages = [{"role": "user", "content": user_prompt}]

    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=_system_with_cache(system_prompt),
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
