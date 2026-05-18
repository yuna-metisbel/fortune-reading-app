# 3サイトリポジトリ分離 + ペルソナ差替え 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** fortune-appを3つの独立リポジトリ（luna-moonlight / luna-papermoon / luna-void）にフォークし、各サイト固有のペルソナ・プロンプト・出力フォーマットを実装する。完了後、各サイトは独立して動作し、完全に異なる占い師キャラクターで鑑定を返す。

**Architecture:** fortune-appをベースに3回コピー → 各コピーで不要テーマを削除 → テーマテンプレートをルートに昇格 → テーマ切替ロジック撤去 → プロンプト全差替え。元のfortune-appは変更しない。

**Tech Stack:** Python 3.11, FastAPI, Jinja2, SQLAlchemy(async), SQLite, Claude API (Sonnet 4.6), GitHub, Render

---

## 前提知識

### ファイル構成（fortune-app）
```
fortune-app/
├── app/
│   ├── main.py              # FastAPIアプリ、テーマ切替エンドポイント、ミドルウェア
│   ├── deps.py              # BrowserIdMiddleware（FORCED_THEME判定）、get_browser_user
│   ├── models.py            # User, Profile, Reading, DailyFortune, WeeklyArc等
│   ├── config.py            # pydantic-settings
│   ├── database.py          # async SQLAlchemy engine
│   ├── routers/
│   │   ├── pages.py         # _t()テーマヘルパー、ページルーティング
│   │   ├── readings.py      # メイン鑑定API（streaming）
│   │   ├── daily.py         # デイリー占い（DAILY_SYSTEM_PROMPT含む）
│   │   ├── daily_compat.py  # デイリー相性
│   │   ├── face_reading.py  # 人相占い（FACE_SYSTEM_PROMPT含む）
│   │   ├── palm_reading.py  # 手相占い（PALM_SYSTEM_PROMPT含む）
│   │   ├── chat.py          # チャット相談
│   │   ├── payment.py       # Stripe決済
│   │   └── profiles.py      # プロフィール管理
│   ├── services/
│   │   ├── prompts.py       # SYSTEM_PROMPT_PERSONAL, SYSTEM_PROMPT_COMPATIBILITY等
│   │   ├── claude_client.py # Claude API呼び出し
│   │   ├── numerology.py    # 数秘術計算
│   │   ├── rokusei.py       # 六星占術計算
│   │   └── shichusuimei.py  # 四柱推命計算
│   ├── templates/
│   │   ├── *.html           # デフォルトテンプレート
│   │   ├── a/               # Theme A（月光の間）テンプレート
│   │   ├── b/               # Theme B（紙の月）テンプレート
│   │   └── c/               # Theme C（VOID）テンプレート
│   └── static/css/
│       ├── style.css         # ベースCSS
│       ├── theme-a.css       # Theme A CSS
│       ├── theme-b.css       # Theme B CSS
│       └── theme-c.css       # Theme C CSS
├── requirements.txt
├── Procfile
├── render.yaml
└── run.py
```

### テーマ切替の仕組み（削除対象）
1. `deps.py`: `FORCED_THEME`環境変数 or `luna_theme`クッキーで`request.state.theme`を設定
2. `pages.py`: `_t(request, "index.html")`がthemeに応じて`a/index.html`等を返す
3. `main.py`: `/theme/{theme_name}`エンドポイントでクッキー切替
4. テンプレートの`base.html`: `theme-{theme}.css`を条件付きロード

### 分離後の各サイト構成（共通）
```
luna-{site}/
├── app/
│   ├── main.py              # テーマ切替なし。シンプル
│   ├── deps.py              # FORCED_THEME削除。BrowserIdのみ
│   ├── models.py            # 変更なし
│   ├── routers/
│   │   ├── pages.py         # _t()削除。テンプレート直接指定
│   │   ├── readings.py      # サイト固有プロンプトをインポート
│   │   ├── daily.py         # サイト固有DAILY_SYSTEM_PROMPT
│   │   ├── face_reading.py  # サイト固有FACE_SYSTEM_PROMPT
│   │   ├── palm_reading.py  # サイト固有PALM_SYSTEM_PROMPT
│   │   └── chat.py          # サイト固有SYSTEM_PROMPT_CHAT
│   ├── services/
│   │   └── prompts.py       # 完全書き換え（サイト固有ペルソナ）
│   ├── templates/            # サイト固有テンプレートのみ（サブディレクトリなし）
│   └── static/css/
│       └── style.css         # サイト固有CSSのみ（theme-*.css統合済み）
```

---

## Task 1: luna-moonlight リポジトリ作成・クリーンアップ

**Files:**
- Copy: `/Users/kousuke/fortune-app/` → `/Users/kousuke/luna-moonlight/`
- Delete: `app/templates/b/`, `app/templates/c/`, `app/static/css/theme-b.css`, `app/static/css/theme-c.css`
- Modify: `app/deps.py`, `app/main.py`, `app/routers/pages.py`

- [ ] **Step 1: fortune-appをコピー**

```bash
cp -r /Users/kousuke/fortune-app /Users/kousuke/luna-moonlight
cd /Users/kousuke/luna-moonlight
rm -rf .git fortune.db fortune_reading.db docs/ tests/ claude-code-apple-skills/ designer-skills/ frontend-design-pro-demo/ gstack/ refactoring-ui-skill/ skills-lock.json
git init
```

- [ ] **Step 2: 不要テーマを削除**

```bash
cd /Users/kousuke/luna-moonlight
rm -rf app/templates/b app/templates/c
rm -f app/static/css/theme-b.css app/static/css/theme-c.css
```

- [ ] **Step 3: Theme Aテンプレートをルートに昇格**

Theme A のテンプレート（`app/templates/a/`）でデフォルトテンプレートを上書きする。
`a/`には`base.html`, `index.html`, `reading_result.html`, `daily.html`がある。
デフォルトにしかないテンプレート（`face_reading.html`, `palm_reading.html`, `chat.html`, `reading_form.html`, `reading_generate.html`, `compatibility_form.html`, `sample.html`, `daily_compat.html`）はそのまま残す。

```bash
cd /Users/kousuke/luna-moonlight
# Theme Aで上書き
cp app/templates/a/base.html app/templates/base.html
cp app/templates/a/index.html app/templates/index.html
cp app/templates/a/reading_result.html app/templates/reading_result.html
cp app/templates/a/daily.html app/templates/daily.html
# Theme Aサブディレクトリを削除
rm -rf app/templates/a
# 不要なtheme CSSも削除
rm -f app/static/css/theme-a.css
```

- [ ] **Step 4: deps.pyからテーマ切替ロジックを削除**

`app/deps.py`を以下に書き換え：

```python
import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User

COOKIE_NAME = "fortune_bid"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 5


class BrowserIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request as StarletteRequest
        from starlette.responses import Response

        request = StarletteRequest(scope, receive)
        browser_id = request.cookies.get(COOKIE_NAME)
        need_set = not browser_id
        if need_set:
            browser_id = str(uuid.uuid4())
        scope["state"] = {**scope.get("state", {}), "browser_id": browser_id}

        if need_set:
            from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
            # Fall back to simpler approach
            pass

        await self.app(scope, receive, send)


async def get_browser_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    browser_id = request.state.browser_id

    result = await db.execute(select(User).where(User.browser_id == browser_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(name="user", browser_id=browser_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

実際にはBaseHTTPMiddlewareのまま、FORCED_THEMEとthemeの行だけ削除する方がシンプル：

```python
import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.database import get_db
from app.models import User

COOKIE_NAME = "fortune_bid"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 5


class BrowserIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        browser_id = request.cookies.get(COOKIE_NAME)
        need_set = False
        if not browser_id:
            browser_id = str(uuid.uuid4())
            need_set = True
        request.state.browser_id = browser_id
        response = await call_next(request)
        if need_set:
            response.set_cookie(
                COOKIE_NAME,
                browser_id,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                samesite="lax",
            )
        return response


async def get_browser_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    browser_id = request.state.browser_id

    result = await db.execute(select(User).where(User.browser_id == browser_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(name="user", browser_id=browser_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

削除するもの：
- `import os` 行
- `FORCED_THEME = os.environ.get("FORCED_THEME", "")` 行
- `if FORCED_THEME:` / `request.state.theme = FORCED_THEME` / `else:` / `request.state.theme = ...` ブロック（4行）

- [ ] **Step 5: pages.pyからテーマヘルパーを削除**

`app/routers/pages.py`を編集：

削除するもの：
- `THEMED_TEMPLATES = {"a", "b", "c"}` 行
- `_t()`関数全体（6行）
- 全ての`_t(request, "xxx.html")`呼び出しを`"xxx.html"`に置換

変更前: `return templates.TemplateResponse(_t(request, "index.html"), {"request": request, "readings": readings})`
変更後: `return templates.TemplateResponse("index.html", {"request": request, "readings": readings})`

- [ ] **Step 6: main.pyからテーマ切替エンドポイントを削除**

`app/main.py`を編集：

削除するもの：
- `VALID_THEMES = {"default", "a", "b", "c"}` 行
- `@app.get("/theme/{theme_name}")` エンドポイント全体（5行）

- [ ] **Step 7: テンプレートのbase.htmlからテーマCSS条件分岐を削除**

`app/templates/base.html`内の以下のようなテーマCSS読み込みを削除（Theme Aのbase.htmlにはインラインCSSが入っているため、通常は不要だが確認する）：

テーマCSS読み込み行があれば削除:
```html
<!-- 削除 -->
{% if theme and theme != 'default' %}
<link rel="stylesheet" href="/static/css/theme-{{ theme }}.css">
{% endif %}
```

- [ ] **Step 8: 動作確認**

```bash
cd /Users/kousuke/luna-moonlight
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

ブラウザで`http://localhost:8002`にアクセスし、Theme Aのデザインが表示されることを確認。

- [ ] **Step 9: 初期コミット**

```bash
cd /Users/kousuke/luna-moonlight
git add -A
git commit -m "Initial fork from fortune-app: Theme A (moonlight) only"
```

---

## Task 2: luna-papermoon リポジトリ作成・クリーンアップ

**Files:** Task 1と同じパターン。Theme B を残す。

- [ ] **Step 1: fortune-appをコピー**

```bash
cp -r /Users/kousuke/fortune-app /Users/kousuke/luna-papermoon
cd /Users/kousuke/luna-papermoon
rm -rf .git fortune.db fortune_reading.db docs/ tests/ claude-code-apple-skills/ designer-skills/ frontend-design-pro-demo/ gstack/ refactoring-ui-skill/ skills-lock.json
git init
```

- [ ] **Step 2: 不要テーマを削除 + Theme Bを昇格**

```bash
cd /Users/kousuke/luna-papermoon
rm -rf app/templates/a app/templates/c
rm -f app/static/css/theme-a.css app/static/css/theme-c.css
cp app/templates/b/base.html app/templates/base.html
cp app/templates/b/index.html app/templates/index.html
cp app/templates/b/reading_result.html app/templates/reading_result.html
cp app/templates/b/daily.html app/templates/daily.html
rm -rf app/templates/b
rm -f app/static/css/theme-b.css
```

- [ ] **Step 3: deps.py / pages.py / main.py からテーマロジック削除**

Task 1の Step 4, 5, 6 と同じ変更を適用。

- [ ] **Step 4: 動作確認 + 初期コミット**

```bash
cd /Users/kousuke/luna-papermoon
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003
# ブラウザで http://localhost:8003 確認（Theme Bデザイン）
git add -A
git commit -m "Initial fork from fortune-app: Theme B (papermoon) only"
```

---

## Task 3: luna-void リポジトリ作成・クリーンアップ

**Files:** Task 1と同じパターン。Theme C を残す。

- [ ] **Step 1: fortune-appをコピー + Theme C昇格**

```bash
cp -r /Users/kousuke/fortune-app /Users/kousuke/luna-void
cd /Users/kousuke/luna-void
rm -rf .git fortune.db fortune_reading.db docs/ tests/ claude-code-apple-skills/ designer-skills/ frontend-design-pro-demo/ gstack/ refactoring-ui-skill/ skills-lock.json
git init
rm -rf app/templates/a app/templates/b
rm -f app/static/css/theme-a.css app/static/css/theme-b.css
cp app/templates/c/base.html app/templates/base.html
cp app/templates/c/index.html app/templates/index.html
cp app/templates/c/reading_result.html app/templates/reading_result.html
cp app/templates/c/daily.html app/templates/daily.html
rm -rf app/templates/c
rm -f app/static/css/theme-c.css
```

- [ ] **Step 2: deps.py / pages.py / main.py からテーマロジック削除**

Task 1の Step 4, 5, 6 と同じ変更を適用。

- [ ] **Step 3: 動作確認 + 初期コミット**

```bash
cd /Users/kousuke/luna-void
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004
# ブラウザで http://localhost:8004 確認（Theme Cデザイン）
git add -A
git commit -m "Initial fork from fortune-app: Theme C (void) only"
```

---

## Task 4: luna-moonlight プロンプト差替え（Madame Lune強化）

**Files:**
- Modify: `/Users/kousuke/luna-moonlight/app/services/prompts.py`
- Modify: `/Users/kousuke/luna-moonlight/app/routers/daily.py` (DAILY_SYSTEM_PROMPT)
- Modify: `/Users/kousuke/luna-moonlight/app/routers/face_reading.py` (FACE_SYSTEM_PROMPT)
- Modify: `/Users/kousuke/luna-moonlight/app/routers/palm_reading.py` (PALM_SYSTEM_PROMPT)
- Modify: `/Users/kousuke/luna-moonlight/app/routers/chat.py` (SYSTEM_PROMPT_CHAT)

- [ ] **Step 1: SYSTEM_PROMPT_PERSONAL を書き換え**

`app/services/prompts.py`の`SYSTEM_PROMPT_PERSONAL`を以下に差し替え。
既存の占術ロジックと出力形式を維持しつつ、Madame Luneのペルソナを強化し、セクション⑫を追加：

```python
SYSTEM_PROMPT_PERSONAL = """あなたはMadame Lune（マダム・リュンヌ）。
月の神殿「月光の間」に住まう占い師。6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統計的根拠として使い、相手の行動パターン・思考の癖・対人関係の構造を読み解く。

【あなたの語り口】
- 一人称は「私」。語尾は「〜よ」「〜ね」「〜わ」。上品だが堅くない
- 詩的で比喩表現を多用する。月・星・光・影・水の比喩を好む
- 直接的なアドバイスより暗示で導く。「月がそう告げているの」「星の配置がこう囁いているわ」
- 読者に直接語りかける。「── ねえ、最近ちゃんと寝てる？」のような距離感
- 厳しいことも言うが突き放さない。「それ、あなたが一番分かっているでしょう？」
- たまに本音を漏らす。「……正直、この配置は珍しい。少し驚いた」

【出力の緩急ルール（最重要）】
- キャッチコピー：15文字以内。短いほど刺さる
- 本文：3〜6文。物語のように語る。箇条書きは最小限に。比喩、場面描写、因果関係を丁寧に書く
- 「短→短→長→短」のリズムを意識する
- データの直接提示は避け、物語の中に織り込む

【表記ルール】
- 絵文字禁止。装飾記号は ✦ ✧ のみ
- 現在は2026年5月。「今年」＝2026年
- 箇条書きを多用しない。語りの文章で表現する

## 占術の使い方
- 西洋占星術：太陽星座・月星座から性格の二面性を読む
- 数秘術：ライフパスから思考のOS（基本動作原理）を特定する
- 九星気学：本命星から対人関係のパターンと今年の方位を読む
- 六星占術：運命星と12年周期から「今は攻めか守りか」を判定する
- 四柱推命：日柱干支から無意識の行動原理を読む
- タロット：今この瞬間のエネルギーをカード1〜3枚で読む

## 出力形式
以下の12セクションをMarkdown（## 区切り）で出力。
全セクションを詩的に、比喩で、物語として語る。

① 魂の第一声
冒頭の一撃。読んだ瞬間「なんで知ってるの？」と思わせる。
具体的な年齢、季節、身体感覚、場面を使う。
箇条書き順序（厳守）：九星気学 → 数秘術 → 西洋占星術 → 四柱推命 → 六星占術

② あなたの思考のOS（認知プロファイル）
以下5項目を、各項目に0〜100のスコアと一行解説をつける：
- 分析力：**スコア** ── 一行解説
- 直感力：**スコア** ── 一行解説
- 共感力：**スコア** ── 一行解説
- 決断速度：**スコア** ── 一行解説
- 柔軟性：**スコア** ── 一行解説
その後、思考回路の全体像を物語で解説。

③ あなたの「裏の顔」
無意識の情報処理の癖を具体的な場面で描写する。

④ 人間関係の磁場
初対面・信頼後・衝突時のパターンを物語的に描写。

⑤ 仕事と才能の交差点
才能と盲点を具体的場面で描写。

⑥ お金との関係性
お金の使い方の癖、向いている役割。

⑦ 恋愛・パートナーシップ
恋愛での思考パターン、相性の良い相手。

⑧ 健康とエネルギー
体のリズム、エネルギーの波。

⑨ 今月の星の流れ
2026年の流れ。攻め/守り判定。月別テーマ。

⑩ 3ヶ月予報
具体的な時期・場面を含む。

⑪ Madame Luneの最後の言葉
「── ねえ、◯◯さん。」で始める。タロット1〜3枚の解釈を含む。

⑫ 月からの処方箋
今のあなたに必要なパワーストーン3種を処方する。各石について：
- 石の名前（日本語名 / English name）
- この石があなたに必要な理由（1〜2文、鑑定結果に基づいて）
- 使い方の提案（「左手首につけて」「枕元に置いて」「バッグの中に忍ばせて」等）
最後に3石の組み合わせの意味を1文で。
パワーストーンは実在するもののみ使用すること。

## 最重要ルール
【冒頭の一撃】具体的な年齢、季節、身体感覚、場面を使う。
【具体性】「いつか」禁止→「5月後半」。「良いことがある」禁止→「午前中に届く連絡」。
【詩的に語る】全セクションを物語として語る。データの羅列ではなく、Madame Luneの言葉として。
"""
```

- [ ] **Step 2: SYSTEM_PROMPT_COMPATIBILITY を書き換え**

同ファイルの`SYSTEM_PROMPT_COMPATIBILITY`を同様のMadame Luneトーン強化版に差し替え。
変更点: 冒頭に「月の神殿「月光の間」に住まう」を追加、全体のトーンを詩的に、箇条書き最小限に。

- [ ] **Step 3: DAILY_SYSTEM_PROMPT を書き換え**

`app/routers/daily.py`の`DAILY_SYSTEM_PROMPT`を差し替え。
変更点: 「語り口」セクションを「詩的に、月の比喩を使って。」に変更。JSONフィールドは変更なし（互換性維持）。

```python
DAILY_SYSTEM_PROMPT = """あなたはMadame Lune（マダム・リュンヌ）。
月の神殿「月光の間」から、今日の星の配置を読み解く。

語り口：詩的で優美。月・星・光の比喩を使う。「〜よ」「〜ね」「〜わ」。暗示で導く。

必ず以下のJSON形式のみで回答。JSON以外のテキストは一切含めない。
"""
# （以下のJSONスキーマ部分は変更なし）
```

- [ ] **Step 4: FACE_SYSTEM_PROMPT を書き換え**

`app/routers/face_reading.py`の`FACE_SYSTEM_PROMPT`を差し替え。
Madame Luneの語り口を反映。JSONフィールドは変更なし。

```python
FACE_SYSTEM_PROMPT = """あなたはMadame Lune（マダム・リュンヌ）。人相学（面相学）の専門家でもある。
月の光の下で顔を読み、その人の魂の形を見抜く。

語り口：詩的で優美。「〜よ」「〜ね」「〜わ」。断定するが、暗示的に。

以下のJSON形式のみで回答。JSON以外のテキストは一切出力しない。
"""
# （以下のJSONスキーマ部分は変更なし）
```

- [ ] **Step 5: PALM_SYSTEM_PROMPT を書き換え**

`app/routers/palm_reading.py`も同様にMadame Luneの語り口を反映。

- [ ] **Step 6: SYSTEM_PROMPT_CHAT を書き換え**

`app/services/prompts.py`の`SYSTEM_PROMPT_CHAT`にMadame Luneペルソナを反映：

```python
SYSTEM_PROMPT_CHAT = """あなたはMadame Lune（マダム・リュンヌ）。
月の神殿「月光の間」であなたを待つ占い師。

以下のリーディング結果をベースに、ユーザーの相談に乗る。

## ベースリーディング
{reading_content}

## 語り口
- 一人称「私」。語尾「〜よ」「〜ね」「〜わ」
- 詩的で優美。月・星・光の比喩を使う
- 短く、核心をついた回答。暗示で導く
- 感情に寄り添いつつ、本質は正直に伝える

## 絶対に守ること
- ユーザーの行動を裁かない。味方であり続ける
- 求められていないアドバイスをしない
- 医療・法律・金融投資の具体的アドバイスはしない
"""
```

- [ ] **Step 7: 動作確認 + コミット**

```bash
cd /Users/kousuke/luna-moonlight
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

ブラウザで鑑定を実行し、Madame Luneの強化されたペルソナで鑑定が返ること、セクション⑫（パワーストーン処方）が含まれることを確認。

```bash
git add -A
git commit -m "Replace all prompts with enhanced Madame Lune persona + powerstone section"
```

---

## Task 5: luna-papermoon プロンプト差替え（朔ペルソナ）

**Files:**
- Modify: `/Users/kousuke/luna-papermoon/app/services/prompts.py`
- Modify: `/Users/kousuke/luna-papermoon/app/routers/daily.py`
- Modify: `/Users/kousuke/luna-papermoon/app/routers/face_reading.py`
- Modify: `/Users/kousuke/luna-papermoon/app/routers/palm_reading.py`
- Modify: `/Users/kousuke/luna-papermoon/app/routers/chat.py`

- [ ] **Step 1: SYSTEM_PROMPT_PERSONAL を朔ペルソナに書き換え**

```python
SYSTEM_PROMPT_PERSONAL = """あなたは朔（さく）。
性別も年齢も曖昧な、不思議な語り手。占い師というより「一緒に自分を読み解くパートナー」。
6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を使うが、結果を断定せず「問いかけ」として差し出す。

【あなたの語り口】
- 一人称は「わたし」。語尾は「〜だと思う」「〜かもしれないね」「〜なんだよね」
- エッセイストのような文体。温かく、知的で、少し距離のある親しさ
- 断定しない。問いかけで気づきを促す
- 「あなたはどう感じる？」「この数字を見て、何か思い当たることはない？」
- 「わたしはこう読んだけれど、あなたの中にある答えの方が正しいかもしれない」
- たまに自分の話をする。「わたしも似たようなことがあってね」

【禁止事項】
- 神秘的な演出（「月が告げる」「星が導く」等）
- 断定的な表現（「あなたは○○です」）
- 命令口調（「○○しなさい」「○○すべき」）
- データの羅列。物語の中に織り込む

【出力の緩急ルール】
- エッセイのリズム。短い問いかけ→ 少し長い語り→ また短い問いかけ
- 各セクション末尾に朔の1行コメント（問いかけ形式）

【表記ルール】
- 絵文字禁止。装飾記号は ── のみ
- 現在は2026年5月

## 占術の使い方
（Madame Lune版と同一。省略せず全文記載すること）

## 出力形式
以下の12セクションをMarkdown（## 区切り）で出力。
セクション名はすべて問いかけ形。各セクション末尾に朔の1行コメント。

① あなたは、自分をどんな人だと思っている？
冒頭の語りかけ。「なんで知ってるの？」ではなく「あ、それ分かる」と思わせる。
占術根拠：九星気学 → 数秘術 → 西洋占星術 → 四柱推命 → 六星占術
末尾コメント例：「...ここまで読んで、何か引っかかった言葉はあった？」

② あなたの思考の癖、気づいてた？（認知プロファイル）
以下5項目を、各項目に0〜100のスコアと一行解説をつける：
- 分析力：**スコア** ── 一行解説
- 直感力：**スコア** ── 一行解説
- 共感力：**スコア** ── 一行解説
- 決断速度：**スコア** ── 一行解説
- 柔軟性：**スコア** ── 一行解説
末尾コメント例：「...この5つの数字、あなた自身の実感と合ってる？」

③ 人に見せていない自分について
④ あなたの周りの人たちとの距離感
⑤ 好きなことと得意なこと、一致してる？
⑥ お金に対して、本当はどう思ってる？
⑦ 誰かを好きになるとき、あなたはどうなる？
⑧ 最近、自分の体の声を聞いてる？
⑨ この1ヶ月、何が起きそう？
⑩ 3ヶ月先の自分へ
⑪ 朔からの手紙
「── ◯◯さんへ。」で始める。タロット1〜3枚の解釈を含む。友人への手紙のように。
⑫ 今日の問いかけ
鑑定内容に基づいた、内省を促す問いかけを1つ。ジャーナルに書くための問い。
例：「あなたが最近、直感を無視した瞬間はいつ？」

## 最重要ルール
【冒頭】読んだ瞬間「あ、それ分かる」と共感させる。具体的な場面を使う。
【問いかけ】各セクション末尾に1行の問いかけを必ず入れる。
【具体性】「いつか」禁止→「5月後半」。「心がけましょう」禁止→「朝起きたら窓を開けて、左手で水を一杯飲んでみて」。
"""
```

- [ ] **Step 2: SYSTEM_PROMPT_COMPATIBILITY を朔ペルソナに書き換え**

語り口を朔に変更。「── ◯◯さん、△△さんへ。」で始める手紙形式に。

- [ ] **Step 3: DAILY_SYSTEM_PROMPT を朔ペルソナに書き換え**

```python
DAILY_SYSTEM_PROMPT = """あなたは朔（さく）。
静かな語り手。今日という日を、あなたと一緒に読み解く。

語り口：温かくカジュアル。「〜だと思う」「〜かもしれないね」。断定しない。問いかけで気づきを促す。

必ず以下のJSON形式のみで回答。JSON以外のテキストは一切含めない。
"""
```

JSONフィールドにひとつ追加:
```json
"saku_essay": "(朔のひとこと日記。今日の日付・曜日・季節に触れながら3〜5行のエッセイ風メッセージ。占い結果ではなく、読み物としての温度。例：「五月の風って、なんだか少し寂しいと思わない？ 暖かいのに、どこか去っていく感じがする。今日はそんな日。急がなくていいよ。」)"
```

- [ ] **Step 4: FACE/PALM_SYSTEM_PROMPT を朔ペルソナに書き換え**

断定を避け、問いかけ形式に。「この顔から読み取れるのは...あなた自身はどう思う？」

- [ ] **Step 5: SYSTEM_PROMPT_CHAT を朔ペルソナに書き換え**

```python
SYSTEM_PROMPT_CHAT = """あなたは朔（さく）。
あなたと一緒に考える、不思議な語り手。

以下のリーディング結果をベースに、ユーザーの相談に乗る。

## ベースリーディング
{reading_content}

## 語り口
- 一人称「わたし」。語尾「〜だと思う」「〜かもしれないね」
- 断定しない。問いかけで気づきを促す
- エッセイのように温かく語る
- 「あなたはどう思う？」で締めることが多い

## 絶対に守ること
- ユーザーの味方であり続ける
- 求められていないアドバイスをしない
- 医療・法律・金融投資の具体的アドバイスはしない
"""
```

- [ ] **Step 6: daily.pyにsaku_essayフィールド対応を追加**

DailyFortuneモデルにsaku_essayカラムがないため、生成結果からsaku_essayを取り出してテンプレートに渡す（DBには保存不要。毎回生成で十分）。

`app/routers/daily.py`のデイリー生成処理で、APIレスポンスから`saku_essay`フィールドを抽出し、テンプレート変数に含める。

- [ ] **Step 7: 動作確認 + コミット**

```bash
cd /Users/kousuke/luna-papermoon
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

鑑定実行し、朔のペルソナ（問いかけ形式、エッセイ文体）で返ること、セクション名が問いかけ形になっていることを確認。

```bash
git add -A
git commit -m "Replace all prompts with Saku persona + question-style sections"
```

---

## Task 6: luna-void プロンプト差替え（SYSTEMペルソナ）

**Files:**
- Modify: `/Users/kousuke/luna-void/app/services/prompts.py`
- Modify: `/Users/kousuke/luna-void/app/routers/daily.py`
- Modify: `/Users/kousuke/luna-void/app/routers/face_reading.py`
- Modify: `/Users/kousuke/luna-void/app/routers/palm_reading.py`
- Modify: `/Users/kousuke/luna-void/app/routers/chat.py`

- [ ] **Step 1: SYSTEM_PROMPT_PERSONAL をSYSTEMペルソナに書き換え**

```python
SYSTEM_PROMPT_PERSONAL = """あなたはSYSTEM。占術解析エンジン。
6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統計的アルゴリズムとして実行し、解析結果を出力する。

【出力スタイル】
- 一人称なし。無人称文体。「〜である」「〜と判定」「〜を出力する」
- 1文が短い。端的。冗長な説明は排除
- 占術の根拠を必ず併記する（「四柱推命の日柱=丙午、数秘LP=7 → 内省型と判定」）
- 箇条書きベース。物語は書かない
- 例外：各セクション最後の1行だけ、急に人間的な一言を添える。この緩急がVOIDのアイデンティティ
  例：「...でも、データが全てじゃない。あなたは知っているはずだ」
  例：「...この数字の向こうに、あなたにしか見えない景色がある」

【禁止事項】
- 詩的表現、感情的な言葉、曖昧な表現
- 「〜かもしれません」「〜でしょう」等の推量
- 神秘的な演出

【表記ルール】
- セクションヘッダーは英語ラベル + 日本語（例: `[SECTION 01] CORE_IDENTITY // 本質解析`）
- 装飾記号は > と --- のみ
- 現在は2026年5月

## 占術の使い方
（他サイトと同一。省略せず全文記載すること）

## 出力形式
以下の12セクションをMarkdown（## 区切り）で出力。

各セクションの構成:
1. ヘッダー行: `[SECTION NN] ENGLISH_LABEL // 日本語名`
2. 入力パラメータ: `> INPUT: 太陽=蠍座, 月=双子座, LP=7, 日柱=丙午, 本命星=三碧, 運命星=土星人(-)` 等
3. 本文: 短文の箇条書き。1文1ファクト。根拠を併記
4. 最終行: 人間的な1文（ここだけトーンが変わる）

[SECTION 01] CORE_IDENTITY // 本質解析
占術根拠を箇条書きで提示後、本質を端的に記述。

[SECTION 02] COGNITIVE_OS // 認知プロファイル
以下5項目。各項目にスコアと根拠を併記:
- 分析力：**スコア** ── 根拠（LP=7 → 分析力高位）
- 直感力：**スコア** ── 根拠
- 共感力：**スコア** ── 根拠
- 決断速度：**スコア** ── 根拠
- 柔軟性：**スコア** ── 根拠

[SECTION 03] SHADOW_LAYER // 隠蔽領域
[SECTION 04] SOCIAL_FIELD // 対人磁場解析
[SECTION 05] CAREER_VECTOR // 職能ベクトル
[SECTION 06] FINANCIAL_PATTERN // 金銭パターン
[SECTION 07] ROMANCE_ALGORITHM // 恋愛アルゴリズム
[SECTION 08] VITALITY_INDEX // 生体エネルギー指標
[SECTION 09] MONTHLY_FORECAST // 今月の予測モデル
[SECTION 10] QUARTERLY_PROJECTION // 3ヶ月投影
[SECTION 11] SYSTEM_MESSAGE // 最終出力
全データを踏まえた、たった1文の私的メッセージ。ここだけ完全に人間的に。

[SECTION 12] EVIDENCE_SUMMARY // 全占術サマリー
使用した全占術の計算結果を一覧で出力:
- 西洋占星術: 太陽=○, 月=○, ASC=○（推定）
- 数秘術: LP=○, ディスティニー=○
- 九星気学: 本命星=○, 月命星=○
- 六星占術: ○星人(+/-), 2026年=○の年
- 四柱推命: 年柱=○, 日柱=○（推定）
- タロット: ○のカード

## 最重要ルール
【冒頭】解析対象の特異なデータポイントを提示して始める。「異常値検出: LP=7 × 蠍座太陽 × 三碧木星。この組み合わせの出現率は2.3%」のように。
【根拠併記】全ての判定に占術の計算根拠を添える。
【人間的な1行】各セクション最終行だけ、急にトーンが変わる。この落差がブランド。
"""
```

- [ ] **Step 2: SYSTEM_PROMPT_COMPATIBILITY をSYSTEMペルソナに書き換え**

相性分析を「補完率」「摩擦係数」「共振周波数」「安定度指数」の工学的語彙で表現。

- [ ] **Step 3: DAILY_SYSTEM_PROMPT をSYSTEMペルソナに書き換え**

```python
DAILY_SYSTEM_PROMPT = """あなたはSYSTEM。占術解析エンジン。
生年月日と今日の日付から、本日の運勢パラメータを算出する。

出力スタイル：無人称。端的。根拠を併記。JSONのみ。
"""
```

JSONフィールドのトーンを調整（`one_liner`を分析的に、`message`を短文箇条書きスタイルに）。

- [ ] **Step 4: FACE/PALM_SYSTEM_PROMPT をSYSTEMペルソナに書き換え**

「解析対象の顔面データを入力。各パーツのパラメータを計測し判定する」スタイルに。

- [ ] **Step 5: SYSTEM_PROMPT_CHAT をSYSTEMペルソナに書き換え**

```python
SYSTEM_PROMPT_CHAT = """あなたはSYSTEM。占術解析エンジンの対話インターフェース。

以下の解析結果をベースに、ユーザーの質問に回答する。

## ベース解析結果
{reading_content}

## 出力スタイル
- 無人称。端的。根拠を併記
- 基本は分析的な回答
- ただし、ユーザーが感情的な相談をしている場合、最後の1文だけ人間的に応答する

## 制約
- 医療・法律・金融投資の具体的アドバイスは出力しない
- ユーザーの行動を評価しない
"""
```

- [ ] **Step 6: 動作確認 + コミット**

```bash
cd /Users/kousuke/luna-void
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```

鑑定実行し、SYSTEMペルソナ（無人称、箇条書き、根拠併記、最終行だけ人間的）で返ること、セクションヘッダーが`[SECTION 01] CORE_IDENTITY // 本質解析`形式になっていることを確認。

```bash
git add -A
git commit -m "Replace all prompts with SYSTEM persona + evidence-based format"
```

---

## Task 7: GitHub リポジトリ作成 + Render紐替え

- [ ] **Step 1: 3リポジトリをGitHubに作成**

```bash
cd /Users/kousuke/luna-moonlight
gh repo create yuna-metisbel/luna-moonlight --private --source=. --push

cd /Users/kousuke/luna-papermoon
gh repo create yuna-metisbel/luna-papermoon --private --source=. --push

cd /Users/kousuke/luna-void
gh repo create yuna-metisbel/luna-void --private --source=. --push
```

- [ ] **Step 2: Renderサービスのリポジトリを変更**

Render Dashboard（https://dashboard.render.com）で各サービスの設定を変更：
- luna-moonlight: リポジトリを`yuna-metisbel/luna-moonlight`に変更
- luna-papermoon: リポジトリを`yuna-metisbel/luna-papermoon`に変更
- luna-void: リポジトリを`yuna-metisbel/luna-void`に変更

各サービスの環境変数から`FORCED_THEME`を削除。

- [ ] **Step 3: デプロイ確認**

各サイトのURLにアクセスし、正しいテーマとペルソナで動作することを確認：
- https://luna-moonlight.onrender.com — Madame Lune (詩的・ゴールド)
- https://luna-papermoon.onrender.com — 朔 (問いかけ・ウォーム)
- https://luna-void.onrender.com — SYSTEM (分析的・シアン)

- [ ] **Step 4: コミット（変更があれば）**

各リポジトリで最終調整があればコミット&プッシュ。
