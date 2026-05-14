"""DALL-E 3 / GPT Image API を使用して鑑定結果ポスター画像を生成するモジュール。"""

import base64
import uuid
from pathlib import Path
from typing import Optional

import httpx
import openai

from app.config import settings

_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "static" / "images" / "posters"
IMAGES_DIR = Path(settings.images_dir) if settings.images_dir else _DEFAULT_DIR
_URL_PREFIX = "/poster-images/" if settings.images_dir else "/static/images/posters/"


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

        return f"{_URL_PREFIX}{filename}"
    except Exception:
        return None


async def generate_poster_image(
    nickname: str,
    birth_date: str,
    catch_copy: str,
    personality: str = "",
    strength: str = "",
    love: str = "",
    career: str = "",
    yearly_theme: str = "",
    message: str = "",
) -> Optional[str]:
    """GPT Image APIで鑑定ポスター画像を生成する。"""
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    cc = catch_copy.strip('「」')
    pr = personality.strip('「」')
    st = strength.strip('「」')
    lv = love.strip('「」')
    cr = career.strip('「」')
    yt = yearly_theme.strip('「」')
    ms = message.strip('「」')

    prompt = f"""パステルラベンダー × クリスタルのスピリチュアル鑑定ポスター。
淡いラベンダー、パステルパープル、シルバー、白を基調にした、
幻想的で透明感のあるスピリチュアル鑑定ポスター。

全体は柔らかい雲、月、星、クリスタル、光の粒、繊細な装飾フレームで構成し、
女性向けの優しく神秘的な雰囲気にする。

一番上にごく小さく: あなたの魂が描く、人生の星図
名前: {nickname}
生年月日: {birth_date}

タイトル（大きく）: {cc}

セクション配置:
- 魂のテーマ: {cc}
- 性格: {pr}
- 強み: {st}
- 恋愛傾向: {lv}
- 仕事の方向: {cr}
- 今年のテーマ: {yt}
- あなたへのメッセージ: {ms}

装飾にはムーンストーン、アメジスト、ローズクォーツ、蝶、月のモチーフ、
吊り下げオーナメント、花、光のエフェクトを使用する。

日本語テキストは白文字で太めに、はっきり読めるように描くこと。
括弧「」は使わない。
優雅で可愛く、柔らかい読みやすいレイアウトの1枚完結の鑑定シートにしてください。"""

    try:
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536",
            quality="high",
            n=1,
        )

        image_data = response.data[0]
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"poster_{uuid.uuid4().hex[:12]}.png"
        filepath = IMAGES_DIR / filename

        if image_data.b64_json:
            filepath.write_bytes(base64.b64decode(image_data.b64_json))
        elif image_data.url:
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_data.url, timeout=120.0)
                img_response.raise_for_status()
                filepath.write_bytes(img_response.content)
        else:
            return None

        return f"{_URL_PREFIX}{filename}"
    except Exception as e:
        print(f"Poster generation failed: {e}")
        return None
