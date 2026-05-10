"""DALL-E 3 を使用して鑑定結果ポスター画像を生成するモジュール。"""

import uuid
from pathlib import Path

import httpx
import openai

from app.config import settings

IMAGES_DIR = Path(__file__).resolve().parent.parent / "static" / "images" / "posters"


async def generate_reading_image(
    nickname: str,
    soul_theme: str = "",
    keywords: list[str] | None = None,
) -> str | None:
    """DALL-E 3 でスピリチュアル鑑定ポスター画像を生成する。

    画像にはビジュアル装飾のみ（テキストなし）。
    テキストはHTML側でオーバーレイ表示する。
    生成画像をローカルに保存し、静的ファイルパスを返す。
    """
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = (
        "Create a vertical spiritual poster background illustration. "
        "Style: dreamy pastel watercolor, soft purple/lavender/pink palette. "
        "NOT photorealistic — ethereal watercolor/digital art.\n\n"
        "LAYOUT (vertical, 9:16 ratio):\n"
        "- TOP AREA: Dreamy night-to-dawn sky with crescent moon, scattered stars, "
        "and aurora-like light.\n"
        "- CENTER: A large glowing crystal ball surrounded by a mandala circle. "
        "Soft light particles emanating from the crystal ball.\n"
        "- DECORATIONS: Beautiful crystal gem illustrations (amethyst, moonstone, "
        "rose quartz, selenite) arranged at bottom corners. Hanging crescent moon "
        "ornaments. Small butterflies. Light particles and star sparkles throughout.\n"
        "- Semi-transparent frosted card areas for text overlay (leave blank, "
        "no text inside).\n\n"
        "ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO CHARACTERS OF ANY LANGUAGE "
        "IN THE IMAGE. The image must be purely visual with zero text elements.\n\n"
        "IMPORTANT STYLE NOTES:\n"
        "- Color palette: lavender #c8a2e0, soft pink #e8b4c8, white, silver, "
        "pale purple #e8d5f5\n"
        "- Frosted glass effect on card areas\n"
        "- Overall mood: elegant, feminine, mystical, dreamy — like a premium "
        "astrology service\n"
        "- High detail illustration quality, suitable for Instagram story sharing"
    )

    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="hd",
            n=1,
        )
        dalle_url = response.data[0].url

        # Download the image and save locally
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4()}.png"
        filepath = IMAGES_DIR / filename

        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(dalle_url, timeout=60.0)
            img_response.raise_for_status()
            filepath.write_bytes(img_response.content)

        return f"/static/images/posters/{filename}"
    except Exception:
        return None
