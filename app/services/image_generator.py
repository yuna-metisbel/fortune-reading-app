"""DALL-E 3 を使用して鑑定結果ポスター画像を生成するモジュール。"""

import openai

from app.config import settings


async def generate_reading_image(nickname: str, sections_summary: str) -> str | None:
    """DALL-E 3 でスピリチュアル鑑定ポスター画像を生成する。

    Args:
        nickname: 占い対象者のニックネーム
        sections_summary: 鑑定セクションの要約テキスト

    Returns:
        生成された画像の URL、失敗時は None
    """
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = f"""パステルラベンダー × クリスタルのスピリチュアル鑑定ポスターを作成してください。

淡いラベンダー、パステルパープル、シルバー、白を基調にした、幻想的で透明感のあるスピリチュアル鑑定シート。

全体は柔らかい雲、月、星、クリスタル、光の粒、繊細な装飾フレームで構成し、女性向けの優しく神秘的な雰囲気にする。

タイトルは大きく「{nickname}さんの星図」。
サブタイトルは「あなたの魂が描く、人生の星図」。

中央には大きな円形の星図・曼荼羅チャートを配置し、中央には輝くクリスタルを描く。

その周囲に以下のセクションを配置する：
{sections_summary}

装飾にはムーンストーン、アメジスト、ローズクォーツ、蝶、月のモチーフ、吊り下げオーナメント、花、光のエフェクトを使用する。

日本語テキストで、優雅で可愛く、柔らかい読みやすいレイアウトの1枚完結の鑑定シートにしてください。"""

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
