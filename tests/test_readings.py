"""個人・相性リーディング用プロンプトビルダーの単体テスト"""
import pytest

from app.services.prompts import (
    build_compatibility_user_prompt,
    build_personal_user_prompt,
)


class TestBuildPersonalPrompt:
    def test_build_personal_prompt(self):
        """全フィールドが出力に含まれ、blood_type=None は '不明' と表示されることを確認する。"""
        result = build_personal_user_prompt(
            nickname="さくら",
            birth_date="1995-07-20",
            birth_time="08:30",
            birth_place="大阪府大阪市",
            gender="女性",
            blood_type=None,  # 不明ケース
            theme="仕事と恋愛の両立について知りたい",
        )

        # ニックネームが含まれる
        assert "さくら" in result

        # 生年月日が含まれる
        assert "1995-07-20" in result

        # 生まれた時刻が含まれる
        assert "08:30" in result

        # 出生地が含まれる
        assert "大阪府大阪市" in result

        # 性別が含まれる
        assert "女性" in result

        # blood_type=None は "不明" と表示される
        assert "不明" in result
        assert "None" not in result

        # テーマが含まれる
        assert "仕事と恋愛の両立について知りたい" in result

    def test_build_personal_prompt_all_optional_none(self):
        """オプションフィールドがすべて None のとき、エラーなく生成できることを確認する。"""
        result = build_personal_user_prompt(
            nickname="テスト太郎",
            birth_date="2000-01-01",
            birth_time=None,
            birth_place=None,
            gender=None,
            blood_type=None,
            theme=None,
        )

        assert "テスト太郎" in result
        assert "2000-01-01" in result
        # None フィールドはすべて "不明" に変換されている
        assert "None" not in result


class TestBuildCompatibilityPrompt:
    def test_build_compatibility_prompt(self):
        """両人物のフィールド・relationship_type・met_date がすべて出力に含まれることを確認する。"""
        result = build_compatibility_user_prompt(
            person1_nickname="ハルカ",
            person1_birth_date="1993-03-15",
            person1_birth_time="12:00",
            person1_birth_place="東京都",
            person1_gender="女性",
            person1_blood_type="A",
            person2_nickname="ケンジ",
            person2_birth_date="1991-11-28",
            person2_birth_time=None,
            person2_birth_place="神奈川県",
            person2_gender="男性",
            person2_blood_type="O",
            relationship_type="交際中",
            met_date="2022年夏",
            theme="結婚を考えているが相性が気になる",
        )

        # 1人目の情報
        assert "ハルカ" in result
        assert "1993-03-15" in result
        assert "12:00" in result
        assert "東京都" in result
        assert "女性" in result
        assert "A" in result

        # 2人目の情報
        assert "ケンジ" in result
        assert "1991-11-28" in result
        assert "神奈川県" in result
        assert "男性" in result
        assert "O" in result

        # 2人目の birth_time=None は "不明" と表示される
        assert "不明" in result
        assert "None" not in result

        # 関係性情報
        assert "交際中" in result
        assert "2022年夏" in result

        # テーマ
        assert "結婚を考えているが相性が気になる" in result

    def test_build_compatibility_prompt_optional_fields_none(self):
        """relationship_type・met_date・theme が None のときエラーなく生成できることを確認する。"""
        result = build_compatibility_user_prompt(
            person1_nickname="Aさん",
            person1_birth_date="1988-06-01",
            person1_birth_time=None,
            person1_birth_place=None,
            person1_gender=None,
            person1_blood_type=None,
            person2_nickname="Bさん",
            person2_birth_date="1990-09-09",
            person2_birth_time=None,
            person2_birth_place=None,
            person2_gender=None,
            person2_blood_type=None,
            relationship_type=None,
            met_date=None,
            theme=None,
        )

        assert "Aさん" in result
        assert "Bさん" in result
        assert "None" not in result
