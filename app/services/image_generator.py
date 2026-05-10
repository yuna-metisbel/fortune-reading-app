"""DALL-E 3 を使用して鑑定結果ポスター画像を生成するモジュール。"""

import openai

from app.config import settings


async def generate_reading_image(nickname: str, sections_summary: str) -> str | None:
    """DALL-E 3 でスピリチュアル鑑定ポスター画像を生成する。"""
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = (
        "Create a Japanese spiritual astrology reading poster (占い鑑定ポスター). "
        "Style: pastel lavender, soft purple, silver, white watercolor illustration. "
        "NOT photorealistic — soft dreamy watercolor/digital illustration style. "
        "\n\n"
        "LAYOUT (vertical poster, top to bottom):\n"
        "- TOP: Night sky with crescent moon and stars. Title: 'あなたの魂が描く、人生の星図' in elegant Japanese serif font.\n"
        f"- Subtitle: '{nickname} さんの星図'\n"
        "- CENTER: Large circular mandala/star chart with a glowing crystal ball in the middle. "
        "Around the mandala, 6 labels: 直感, 知性, 行動, 再生, 感性, 共感.\n"
        "- LEFT/RIGHT of mandala: Two frosted glass cards — '魂のテーマ' and '自然な性格' with small bullet points.\n"
        "- MIDDLE ROWS: 2-column frosted glass cards for '強み', '弱点・課題' with crystal gem decorations between them.\n"
        "- 3-column row: '恋愛傾向', '人間関係の特徴', '仕事の向いている方向' with small gem icons.\n"
        "- 3-column row: '運気を高める習慣', 'おすすめアイテム' (with crystal illustrations: amethyst, moonstone, rose quartz), '避けたいもの・注意点'.\n"
        "- TIMELINE: '人生のサイクルとテーマ' horizontal timeline with dots.\n"
        "- BOTTOM: 'あなたへのメッセージ' section with decorative frame, 'With Love & Light ✦'.\n"
        "\n"
        "DECORATIONS throughout: glowing crystals, butterflies, hanging moon ornaments, "
        "small flowers, light particles, stars. Each section has frosted glass background "
        "with subtle gradient borders. "
        "Amethyst, moonstone, selenite, rose quartz crystal illustrations scattered between sections. "
        "Color palette: #c8a2e0, #e8d5f5, #f8f3ff, #e8b4c8, white, silver. "
        "Japanese text must be clearly readable. Elegant, feminine, mystical mood."
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
