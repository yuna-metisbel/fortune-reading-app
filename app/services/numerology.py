"""数秘術（Numerology）のライフパスナンバーを算出するモジュール。

マスターナンバー（11, 22, 33）は縮約せず保持する。
"""

MASTER_NUMBERS = {11, 22, 33}


def _reduce(n: int) -> int:
    """数字を1桁またはマスターナンバーになるまで縮約する。"""
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


def calculate_life_path(birth_year: int, birth_month: int, birth_day: int) -> dict:
    """ライフパスナンバーを算出する。

    全桁を合算し、マスターナンバー（11, 22, 33）はそのまま保持。

    Args:
        birth_year: 生まれ年（西暦）
        birth_month: 生まれ月（1-12）
        birth_day: 生まれ日（1-31）

    Returns:
        dict with keys:
            life_path: int          ライフパスナンバー
            is_master: bool         マスターナンバーかどうか
            description: str        表示用テキスト
    """
    total = sum(int(d) for d in f"{birth_year}{birth_month:02d}{birth_day:02d}")
    life_path = _reduce(total)
    is_master = life_path in MASTER_NUMBERS

    description = str(life_path)
    if is_master:
        reduced = _reduce(sum(int(d) for d in str(life_path)))
        description = f"{life_path}/{reduced}（マスターナンバー）"

    return {
        "life_path": life_path,
        "is_master": is_master,
        "description": description,
    }
