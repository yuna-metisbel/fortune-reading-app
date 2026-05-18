# セッション引き継ぎ — LUNA ORACLE 占いリーディングWebアプリ（2026-05-18）

## プロジェクト概要
生年月日・血液型・出身地・出生時間・人相・手相から8つの占術体系を統合した実用型リーディングを生成するWebアプリ。Madame Lune（マダム・リュンヌ）というキャラクターが「思考パターン・行動特性・認知プロファイル」を読み解く形式。3つのデザインテーマ（月光の間/紙の月/VOID）を切替可能。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (public)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン（persistent disk `/data/fortune.db`）
- ローカル開発: `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001`（8000はdispatch-appが使用中のことがある）

## 技術スタック
FastAPI + Jinja2 + SQLAlchemy(async) + SQLite(aiosqlite) + Claude API(Sonnet 4.6, Vision) + html2canvas + Stripe/PayPal
Python 3.11 on Render

## ディレクトリ構成
```
fortune-app/
├── app/
│   ├── main.py          # FastAPI app + テーマ切替エンドポイント(/theme/{name})
│   ├── config.py, database.py, models.py
│   ├── deps.py          # BrowserIdMiddleware（theme cookieもここで読む）
│   ├── routers/
│   │   ├── pages.py     # _t()ヘルパーでテーマ別テンプレート分岐
│   │   ├── readings.py  # 結果表示でテーマ分岐
│   │   ├── daily.py     # デイリーでテーマ分岐 + 7フォーマット切替
│   │   ├── daily_compat.py, chat.py, payment.py
│   │   ├── face_reading.py, palm_reading.py
│   ├── services/
│   │   ├── prompts.py   # ★改修済み: Madame Lune人格 + 認知プロファイル + 思考パターン
│   │   ├── claude_client.py, numerology.py, rokusei.py, shichusuimei.py
│   ├── templates/
│   │   ├── *.html           # 現行デザイン（theme=default時に使用）
│   │   ├── a/               # テーマA: 月光の間（ダーク×ゴールド）
│   │   │   ├── base.html, index.html, reading_result.html, daily.html
│   │   ├── b/               # テーマB: 紙の月（ライト×マガジン）
│   │   │   ├── base.html, index.html, reading_result.html, daily.html
│   │   ├── c/               # テーマC: VOID（ダーク×ターミナル）
│   │   │   ├── base.html, index.html, reading_result.html, daily.html
│   └── static/
│       ├── css/style.css         # 現行CSS
│       ├── css/theme-a.css       # テーマA CSS（現在は未使用、テンプレート内にCSS埋め込み方式に変更済み）
│       ├── css/theme-b.css       # テーマB CSS（同上）
│       ├── css/theme-c.css       # テーマC CSS（同上）
│       └── js/reading.js, js/chat.js
├── docs/reflections/
├── HANDOFF.md
```

## 今回やったこと（セッション12）

### テーマシステム構築
- 3つのデザインテーマ（A: 月光の間/B: 紙の月/C: VOID）の完全テンプレートセット作成
- `/theme/a|b|c|default` でcookie切替、全ページに適用
- 各テーマはCSS埋め込み方式の独立テンプレート（a/base.html等）
- ルーター分岐: pages.py `_t()`, readings.py, daily.py で `request.state.theme` を参照

### プロンプト全面改修（最重要変更）
- **SYSTEM_PROMPT_PERSONAL**: Madame Lune人格導入、認知プロファイル（分析力/直感力/共感力/決断速度/柔軟性の0-100スコア）、思考パターン分析、対人関係の構造、「やめるべきこと」セクション追加。テキスト緩急ルール（キャッチ15文字以内→本文3-6文で濃く）
- **DAILY_SYSTEM_PROMPT**: 7フォーマット日替わり（standard/story/question/letter/warning/number/reverse）、predictionフィールド追加（翌日検証可能な予言）、message文字数150-250文字に拡大
- **SYSTEM_PROMPT_COMPATIBILITY**: 二人の認知プロファイル比較、衝突の因果構造解説、具体的場面描写

### 手相占い改修
- 左手/右手の選択UI（カード型、選択理由の説明付き）
- カメラ撮影 + カメラロール選択の2ボタン
- APIにhandパラメータ送信（バックエンド側の処理は未実装）

### テーマA改修（企画チーム分析後）
- 「今日◯◯人が占った」ソーシャルプルーフカウンター追加
- タイプ名の劇的出現アニメーション（0.8秒遅延 → スケールアップ）
- 「友達にも占ってもらう」招待リンクコピーボタン

### テストデータ
- 旧プロンプト: ゆーな(ID:15), ゆーご(ID:16), 相性(ID:18)
- 新プロンプト: ゆーな(ID:20), ゆーご(ID:21), 相性(ID:22)

## 現在の状態
- ローカルで動作中（port 8001）
- 3テーマ全て切替可能、新プロンプトで生成済みデータあり
- **本番未デプロイ**（全変更はローカルのみ）
- git commitもまだ

## 未完了・次にやること

### 最優先（バックエンド機能）
1. **認知プロファイルのパース→表示**: AIが生成した「分析力：72」等の数値をreading.contentからパースし、テンプレートのバーチャートに反映するコード
2. **的中フィードバック機能**: DailyFortuneにpredictionカラム追加、翌日の当たり/ハズレ記録UI、的中率計算・表示
3. **週間アークシステム**: 月曜にweekly_theme生成→火〜日で連続展開するロジック

### 中優先
4. **手相ルーターでhandパラメータをプロンプトに反映**（左手=先天/右手=後天の指示をAIに渡す）
5. **チャットプロンプトのMadame Lune化**（SYSTEM_PROMPT_CHATが旧式のまま）
6. **テーマB/Cの画面表示検証**（テンプレートは作成済みだが実際のレンダリング未確認）
7. **テーマ選択UIをアプリ内に設置**（現在はURL直打ちのみ）

### デプロイ
8. **git commit → push → Renderデプロイ**
9. **本番動作確認**

## 注意点・ハマりポイント

### テーマシステム
- テーマCSS（theme-a/b/c.css）は作成したが**現在は使っていない**。テンプレート内に`<style>`で直接CSSを埋め込む方式に変更した。理由: style.cssに紫色がハードコード137箇所あり、CSS変数上書きだけでは切り替わらなかった
- テーマ分岐は `request.state.theme` で行う。`deps.py` の `BrowserIdMiddleware` でcookie `luna_theme` から読み取り
- `pages.py` の `_t(request, "index.html")` ヘルパーがテーマ別テンプレートパスを返す。`THEMED_TEMPLATES = {"a", "b", "c"}`

### プロンプト
- 個人リーディングは10セクション→11セクションに増えた（②認知プロファイルが新設）
- `reading_result.html`のパースは`## `区切りに依存。新セクションは既存パーサーで自動的に拾われる
- デイリーの`prediction`フィールドは新規追加。既存のDailyFortuneモデルにカラムがない→DBマイグレーション必要
- デイリーの7フォーマット切替は`(today.toordinal() + birth_date.toordinal()) % 7`で決定

### DB
- ローカルDBにはテストデータ（ID:15-22）が入っている
- 本番DBとは別。本番はRenderのpersistent disk上の`/data/fortune.db`
- DailyFortuneテーブルにpredictionカラムが未追加（ALTER TABLE必要）

### ポート
- 8000はdispatch-appが使っていることがある。fortune-appは8001で起動する
- `lsof -i :8000`で確認してから起動

### ユーザーの好み
- **文章が長いのは好き、尺（ステップ数）が長いのは嫌い**: 入力は最小限（生年月日のみ必須）、結果は濃く読み応えあるテキスト
- **論理的な使い方**: 占いをスピリチュアルとしてではなく「思考パターンと行動特性の分析ツール」として使っている
- **デザインよりも中身**: ガワだけ変えても意味がない。プロンプト→バックエンド→テンプレートの順で進めるべき

## 次回の開き方

```
HANDOFF.mdを読んで占いアプリの続きをして。

最優先:
1. 認知プロファイルの数値をパースしてバーチャートで表示する
2. 的中フィードバック機能（prediction保存→翌日判定→的中率表示）
3. 週間アーク（月曜テーマ設定→日ごとに連続展開）

テーマB/Cの画面表示も確認して、おかしいところがあれば直して。
全部できたらgit commitしてRenderにデプロイ。
```
