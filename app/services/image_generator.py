"""DALL-E 3 を使用して鑑定結果ポスター画像を生成するモジュール。"""

import openai

from app.config import settings


async def generate_reading_image(nickname: str, sections_summary: str) -> str | None:
    """DALL-E 3 でスピリチュアル鑑定ポスター画像を生成する。

    Returns:
        生成された画像の URL、失敗時は None
    """
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = (
        "A mystical spiritual astrology reading poster in pastel lavender, purple, silver and white tones. "
        "Dreamy ethereal atmosphere with soft clouds, crescent moon, stars, glowing crystals, "
        "and light particles. A large circular mandala star chart in the center with a shining crystal. "
        "Decorated with moonstone, amethyst, rose quartz gems, butterflies, moon motifs, "
        "hanging ornaments, flowers, and light effects. "
        "Soft feminine mystical mood with delicate ornamental frames. "
        "The poster has sections arranged around the mandala for: "
        "Soul Theme, Natural Personality, Strengths, Challenges, Love Tendency, "
        "Relationships, Career Direction, Lucky Habits, Recommended Items, Cautions, "
        "Life Cycles, and Personal Message. "
        "Japanese aesthetic, elegant, cute, soft readable layout. "
        "High quality illustration, no photorealistic elements. "
        f"Title area says '{nickname}' in decorative text."
    )

    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="hd",
            n=1,
        )
        return response.data[0].url
    except Exception:
        return None
