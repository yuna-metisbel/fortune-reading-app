"""六星占術（Rokusei Senjutsu）の運命星・陰陽・霊合星人を算出するモジュール。

細木数子が提唱した六星占術の計算を、公式の運命数表に基づいて正確に実装。
運命数表の値は「年の基準値 + 月初日までの累積日数 (mod 60)」で再現できる。
"""

import calendar

# ── 定数 ──────────────────────────────────────────────

# 1990年1月の運命数（公式運命数表より）
_REFERENCE_YEAR = 1990
_REFERENCE_JAN_BASE = 3

# 星人の範囲（星数 1-60）
STARS = [
    (1, 10, "土星人"),
    (11, 20, "金星人"),
    (21, 30, "火星人"),
    (31, 40, "天王星人"),
    (41, 50, "木星人"),
    (51, 60, "水星人"),
]

# 地支（Earthly Branches）
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# プラス（陽支）: 子(0), 寅(2), 辰(4), 午(6), 申(8), 戌(10)
_PLUS_BRANCH_INDICES = {0, 2, 4, 6, 8, 10}

# 霊合星人の判定テーブル: (星人名, 極性) → 該当する地支インデックス
_REIGOU_TABLE: dict[tuple[str, str], int] = {
    ("土星人", "プラス(+)"): 10,    # 戌
    ("土星人", "マイナス(-)"): 11,   # 亥
    ("金星人", "プラス(+)"): 8,     # 申
    ("金星人", "マイナス(-)"): 9,    # 酉
    ("火星人", "プラス(+)"): 6,     # 午
    ("火星人", "マイナス(-)"): 7,    # 未
    ("天王星人", "プラス(+)"): 4,   # 辰
    ("天王星人", "マイナス(-)"): 5,  # 巳
    ("木星人", "プラス(+)"): 2,     # 寅
    ("木星人", "マイナス(-)"): 3,    # 卯
    ("水星人", "プラス(+)"): 0,     # 子
    ("水星人", "マイナス(-)"): 1,    # 丑
}

# 霊合星人の対になる星人ペア
_REIGOU_PAIR: dict[str, str] = {
    "土星人": "天王星人",
    "天王星人": "土星人",
    "金星人": "木星人",
    "木星人": "金星人",
    "火星人": "水星人",
    "水星人": "火星人",
}


# ── 内部関数 ──────────────────────────────────────────

def _jan_base(year: int) -> int:
    """指定年の1月の運命数基準値を算出する。

    公式運命数表は「前年の日数(365 or 366)を足す(mod 60)」で再現可能。
    """
    base = _REFERENCE_JAN_BASE
    if year >= _REFERENCE_YEAR:
        for y in range(_REFERENCE_YEAR, year):
            days_in_year = 366 if calendar.isleap(y) else 365
            base = (base + days_in_year) % 60
            if base == 0:
                base = 60
    else:
        for y in range(year, _REFERENCE_YEAR):
            days_in_year = 366 if calendar.isleap(y) else 365
            base = (base - days_in_year) % 60
            if base <= 0:
                base += 60
    return base


def _days_before_month(year: int, month: int) -> int:
    """1月1日からmonth月1日までの累積日数（1月は0）。"""
    total = 0
    for m in range(1, month):
        total += calendar.monthrange(year, m)[1]
    return total


# ── 公開関数 ──────────────────────────────────────────

def calculate_rokusei(birth_year: int, birth_month: int, birth_day: int) -> dict:
    """六星占術の運命星・陰陽・霊合星人を算出する。

    Args:
        birth_year: 生まれ年（西暦）
        birth_month: 生まれ月（1-12）
        birth_day: 生まれ日（1-31）

    Returns:
        dict with keys:
            star: str          星人名（例: "火星人"）
            polarity: str      極性（"プラス(+)" or "マイナス(-)"）
            star_full: str     フル表記（例: "火星人マイナス(-)"）
            star_number: int   星数（1-60）
            reigou: bool       霊合星人かどうか
            reigou_pair: str|None  霊合の場合の対になる星人名
    """
    # Step 1: 運命数を求める
    jb = _jan_base(birth_year)
    cumdays = _days_before_month(birth_year, birth_month)
    unmei = (jb + cumdays) % 60
    if unmei == 0:
        unmei = 60

    # Step 2: 星数を求める
    star_number = unmei - 1 + birth_day
    if star_number > 60:
        star_number -= 60

    # Step 3: 星人を判定
    star = ""
    for low, high, name in STARS:
        if low <= star_number <= high:
            star = name
            break

    # Step 4: プラス/マイナスを判定（地支の陰陽）
    branch_idx = (birth_year - 4) % 12
    polarity = "プラス(+)" if branch_idx in _PLUS_BRANCH_INDICES else "マイナス(-)"

    # Step 5: 霊合星人の判定
    reigou = False
    reigou_pair: str | None = None
    reigou_branch = _REIGOU_TABLE.get((star, polarity))
    if reigou_branch is not None and branch_idx == reigou_branch:
        reigou = True
        reigou_pair = _REIGOU_PAIR.get(star)

    star_full = f"{star}{polarity}"
    if reigou and reigou_pair:
        star_full += f"（霊合星人・{reigou_pair}の性質を併せ持つ）"

    return {
        "star": star,
        "polarity": polarity,
        "star_full": star_full,
        "star_number": star_number,
        "reigou": reigou,
        "reigou_pair": reigou_pair,
    }


# ── 12年周期（運命周期）計算 ──

# 12年周期の運勢名（順番は固定）
CYCLE_NAMES = [
    "種子", "緑生", "立花", "健弱", "達成", "乱気",
    "再会", "財成", "安定", "陰影", "停止", "減退",
]

# 大殺界に該当する位置（陰影・停止・減退）
DAISAKKAI_POSITIONS = {"陰影", "停止", "減退"}


def calculate_cycle_position(birth_year: int, birth_month: int, birth_day: int, target_year: int) -> dict:
    """指定年における六星占術の12年周期の位置を算出する。

    Args:
        birth_year: 生まれ年
        birth_month: 生まれ月
        birth_day: 生まれ日
        target_year: 調べたい年（例: 2026）

    Returns:
        dict with keys:
            cycle_position: str  運勢名（例: "達成"）
            is_daisakkai: bool   大殺界かどうか
            cycle_year: int      12年周期の何年目か（1-12）
    """
    rokusei = calculate_rokusei(birth_year, birth_month, birth_day)
    star = rokusei["star"]

    # 各星人の「種子」が始まる基準年（公式データに基づく近似）
    # 星人ごとに12年周期のスタート年が異なる
    seed_year_bases = {
        "土星人": 2009,
        "金星人": 2010,
        "火星人": 2011,
        "天王星人": 2006,
        "木星人": 2007,
        "水星人": 2008,
    }

    base = seed_year_bases.get(star, 2009)
    offset = (target_year - base) % 12
    cycle_position = CYCLE_NAMES[offset]
    is_daisakkai = cycle_position in DAISAKKAI_POSITIONS

    return {
        "cycle_position": cycle_position,
        "is_daisakkai": is_daisakkai,
        "cycle_year": offset + 1,
    }
