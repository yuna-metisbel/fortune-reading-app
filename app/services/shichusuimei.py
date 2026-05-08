"""四柱推命の年柱（天干地支）を算出するモジュール。

生まれ年から年柱の天干（十干）と地支（十二支）を求める。
60年周期の干支暦に基づく。
"""

# 十干（天干 / Heavenly Stems）
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二支（地支 / Earthly Branches）
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行（天干の五行対応）
_STEM_ELEMENTS = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 五行（地支の五行対応）
_BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 陰陽（天干の陰陽）
_STEM_YINYANG = {
    "甲": "陽", "乙": "陰",
    "丙": "陽", "丁": "陰",
    "戊": "陽", "己": "陰",
    "庚": "陽", "辛": "陰",
    "壬": "陽", "癸": "陰",
}


def calculate_year_pillar(birth_year: int) -> dict:
    """生まれ年から四柱推命の年柱を算出する。

    Args:
        birth_year: 生まれ年（西暦）

    Returns:
        dict with keys:
            pillar: str        年柱（例: "乙亥"）
            stem: str          天干（例: "乙"）
            branch: str        地支（例: "亥"）
            stem_element: str  天干の五行（例: "木"）
            branch_element: str 地支の五行（例: "水"）
            yinyang: str       陰陽（例: "陰"）
    """
    stem_idx = (birth_year - 4) % 10
    branch_idx = (birth_year - 4) % 12

    stem = HEAVENLY_STEMS[stem_idx]
    branch = EARTHLY_BRANCHES[branch_idx]

    return {
        "pillar": f"{stem}{branch}",
        "stem": stem,
        "branch": branch,
        "stem_element": _STEM_ELEMENTS[stem],
        "branch_element": _BRANCH_ELEMENTS[branch],
        "yinyang": _STEM_YINYANG[stem],
    }
