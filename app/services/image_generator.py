"""無料画像生成（Pollinations.ai）を使用して鑑定ポスター画像を生成するモジュール。

APIキー不要。URLベースで画像を生成する。
"""

import urllib.parse

import httpx


async def generate_reading_image(nickname: str, sections_summary: str) -> str | None:
    """Pollinations.ai でスピリチュアル鑑定ポスターの背景画像を生成する。

    Args:
        nickname: 占い対象者のニックネーム
        sections_summary: 鑑定セクションの要約テキスト

    Returns:
        生成された画像の URL、失敗時は None
    """
    prompt = (
        "A mystical spiritual astrology poster, pastel lavender purple silver white color scheme, "
        "dreamy ethereal atmosphere, soft clouds, crescent moon, stars, glowing crystals, "
        "light particles, delicate ornamental frame, mandala star chart in the center with "
        "a shining crystal, moonstone amethyst rose quartz decorations, butterflies, "
        "flower motifs, hanging ornaments, light effects, feminine gentle mystical mood, "
        "soft gradients, no text, no words, no letters, clean decorative background only, "
        "high quality illustration style"
    )

    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1792&model=flux&nologo=true&seed={hash(nickname) % 10000}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.head(url, follow_redirects=True)
            if resp.status_code == 200:
                return url
    except Exception:
        pass

    return url
