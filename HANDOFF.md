# セッション引き継ぎ — 占いリーディングWebアプリ（セッション10後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。セッション10でKPカード表示改善・テーマ色コントラスト向上・iOS Safari word-break対応等を実施。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (**public**)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン（persistent disk `/data/fortune.db`）

## 技術スタック
FastAPI + Jinja2 + SQLite(aiosqlite) + Claude API(Sonnet) + DALL-E 3 + GPT Image API + html2canvas + Stripe/PayPal
Python 3.11 on Render

## ディレクトリ構成
```
fortune-app/
├── app/
│   ├── main.py, config.py, database.py, models.py
│   ├── routers/ (pages, profiles, readings, chat, payment)
│   ├── services/ (claude_client, prompts, rokusei, shichusuimei, numerology, image_generator)
│   ├── templates/ (base, index, reading_form, compatibility_form, reading_result, chat, reading_generate, sample, payment_success, payment_cancel)
│   └── static/ (css/style.css, js/reading.js, js/chat.js, images/posters/)
├── tests/
├── docs/superpowers/specs/
├── docs/superpowers/plans/
├── docs/reflections/ (2026-05-11.md, 2026-05-12.md, 2026-05-13.md, 2026-05-13_2.md, 2026-05-13_3.md)
├── figma-make-handoff.md
└── requirements.txt, Procfile, render.yaml, .env
```

## フォント体系

| 用途 | フォント | 適用先 |
|------|----------|--------|
| 見出し・キャッチコピー | Zen Kaku Gothic New (A) | タイトル、セクションキャッチ、強調テキスト |
| タブ名・ボタン | Shippori Mincho (C) | セクションタブ名、ボタン |
| 「更に詳しく」中身 | Kaisei Decol (E) | read-more-content |
| 本文 | Noto Sans JP (G) | 一般テキスト、ラベル |
| ラベル（英字） | JetBrains Mono | PERSONALITY, SOUL READING 等 |

## カラーパレット（セッション10で改定）

- 背景: #352466 〜 #4a3590
- テキスト: #F5F0FF（メイン）、#D8B4FE（サブ）
- アクセント: #E9D5FF（モーヴ）、#F5C6FF（ピンク ← 旧#F0ABFC）、#C4B5FD（ラベンダー ← 旧#A78BFA）
- 禁止色: オレンジ・暖色系・ゴールド(#FFD700)・純白(#FFFFFF)

## セクションテーマカラー（セッション10で明度UP）

### 個人リーディング（10色）
| セクション | slug | 色 | 旧色 |
|-----------|------|-----|------|
| 全体要約 | summary | #c4b5fd | ~~#a78bfa~~ |
| 性格・本質 | personality | #d4a0ff | ~~#c084fc~~ |
| 才能・強み | strength | #a5b4fc | ~~#818cf8~~ |
| 注意点・課題 | caution | #f9a8d4 | ~~#f472b6~~ |
| 仕事・お金 | career | #34d399 | (変更なし) |
| 恋愛・人間関係 | love | #f5c6ff | ~~#f0abfc~~ |
| 今年のテーマ | yearly | #60a5fa | (変更なし) |
| 月別の流れ | monthly | #c4b5fd | ~~#a78bfa~~ |
| 今すぐやること | action | #fbbf24 | (変更なし) |
| 魂のメッセージ | message | #e9d5ff | (変更なし) |

### 相性リーディング（8色）
| セクション | slug | 色 | 旧色 |
|-----------|------|-----|------|
| 二人の全体像 | overview | #d4a0ff | ~~#c084fc~~ |
| それぞれの本質 | essence | #c4b5fd | ~~#a78bfa~~ |
| 相性分析 | chemistry | #f5c6ff | ~~#f0abfc~~ |
| 関係の課題 | challenge | #f9a8d4 | ~~#f472b6~~ |
| 恋愛アドバイス | love | #e9d5ff | (変更なし) |
| 今年のタイムライン | timeline | #60a5fa | (変更なし) |
| 今すぐやること | action | #fbbf24 | (変更なし) |
| 魂のメッセージ | message | #34d399 | (変更なし) |

※ timelineセクションがpopされた場合、compat_themesからもtimelineを除去してインデックスを揃える処理が入っている（セッション9で修正）

## 改行ルール（セッション8で大幅改修）

### 共通除去・変換（`_clean`関数）
- `「」『』` → 除去
- ダッシュ連続（`──` U+2500、`——` U+2014、`ーー` U+30FC、`━━` 等すべて）→ 改行
- ` — `（半角スペース付きemダッシュ）→ 改行
- `）`の後に文字が続く場合 → 改行（ただし次が助詞・×なら改行しない）
- `／` → 改行

### 3つの関数（reading_result.html内のJS）

| 関数 | 使う場所 | `：` | `、` | `。` |
|------|----------|------|------|------|
| `breakShort` | キャッチコピー、KPカード、ポスター要素 | **改行** | **改行** | **改行(末尾削除)** |
| `breakLabeled` | 「更に詳しく」内のラベル付きリスト値 | **改行** | そのまま | そのまま |
| `breakBody` | 「更に詳しく」本文 | そのまま | そのまま | **改行(。残す)** |

### 禁則処理（`_fixHead`関数）
- 改行後に助詞（を、が、に、で、は、の、と、も等）や`×`が来る場合 → 前の行に結合
- 4文字以下の短い断片 → 前の行に結合（breakShortのみ）

### サイズルール
- 複数行に分かれた場合 → **最長行のサイズに統一（小さい方に合わせる）**
- ポイント（KPカード） → **色で区別**（文字サイズ差❌）
- キーワード（太字） → **文字サイズで区別**（色変え❌）
- キャッチコピーのサイズ閾値: `maxLen<=8→24px、<=14→20px、それ以上→16px`

### KPカード色分けルール（セッション10で改定）
- **本文テキスト** = テーマ色フル不透明度 → `.kp-body`
- **結論（`**...**`部分）** = テーマ色フル不透明度 + `font-weight:700` → `.kp-point`
- **ラベル** = テーマ色 + opacity .8 → `.kp-label`（`**`マーカーはJSで除去）
- ラベルとテキストの間に **〰** セパレーター → `.kp-sep`
- `.kp-body`に `text-shadow: 0 0 16px rgba(233,213,255,.18)` でキラキラ感
- CSS `opacity`は子要素に乗算されるので使わない。色のmutingには8桁hex alphaを使用

### Jinja側の処理
- Jinjaでは`「」`除去のみ
- `| replace('、','<br>')`等はしない（JSと競合するため）
- `| safe`も不要
- KPの`**`マーカーはJinja側で除去しない（JSの`kpBold`が`.kp-point`に変換するため）

## KPパース（readings.py）のルール（セッション10で追加フィルタ）

### key_pointsの構築
- **最初の`**...**`standalone行のみ** → `key_points[0]`（キャッチコピー）
- 以降の`**...**`standalone行 → **スキップ**（サブヘッダーであり、KPカードにしない）
- `- `で始まるbullet行 → `key_points[1:]`
- `key_points[:5]`で最大5件（catchcopy + KP最大4枚）

### detail_bodyの構築
- bullet行（`- `, `* `）→ スキップ（KPカードに表示済み）
- standalone bold行（`**...**`）→ `枚目`か`からのメッセージ`を含まない限りスキップ
- **人物宛ヘッダー**（`^.{1,20}へ$`にマッチする行）→ スキップ（セッション10で追加）
- **indented行**（`  `や`\t`で始まる）→ スキップ（改善策等の continuation line）
- `---`行 → スキップ
- `|`行（テーブル）→ スキップ
- 空行 → 直前が空行でなければセパレーターとして保持（タロットカード区切り用）

### compat_themesのインデックス
- timelineセクションをpopした場合、`compat_themes`からもtimelineを除去
- これにより⑦=action、⑧=messageが正しく割り当てられる

## 相性リーディングのポスター

- `COMPATIBILITY READING`ラベル
- 名前表示: `profile.nickname × profile_2.nickname`
- 生年月日表示: `1995.06.26 × 1999.05.07`
- VennMandala: 3重同心円×2（160px、slowSpin）、中央に8角星
- 背景画像: 個人リーディングと同じ`poster-dalle`（18%透過、ポスター全体）
- タイトル: ダッシュで主題/副題に分割、主題=大文字(18-22px)白、副題=小文字(14px)モーヴ
- セクショングリッド: 1列（個人は2列）

## 相性リーディングのプロンプト構造（セッション8で追加）

- 各セクション冒頭に**太字キャッチコピー**1行 → **箇条書き3〜5個（40文字以内）** → 短い本文
- ①全体像: 占術5項目の順序指定、各項目「結果 → **二人にとっての意味（太字）**」
- ②本質: 1人目と2人目を交互に同数で。小見出し(###)で分けない
- ⑥タイムライン: 表形式（月|テーマ|アクション|注意点）→ 月別グリッドで表示
- ⑦今すぐ: 二人でできる行動3つ / 各自の開運行動2つ / やめること3つ
- スタイルルール追加:
  - 入力済み情報（生年月日、星座名等）を繰り返さない
  - 括弧（）は極力使わない

## タロットカードSVG（セッション9で修復）

### JS側のレンダリングフロー
1. `renderMarkdownBody`が`slug==='message'`かつ`_isTarotLine(t)`でタロット行を検出
2. `TAROT_RE`: `/^\*\*(\d+枚目|.+からのメッセージ|女教皇|女帝|...)/` でマッチ
3. `getTarotKey(name)`: カード名 → SVGテンプレートキー（priestess, empress, star, wands8, pentacles8, default）
4. カード本文: 次のタロット行 or 空行まで収集。**`。`では改行しない**（`breakBody`を使わず、`「」`除去のみ）

### Python側の保持条件
- `**女帝からのメッセージ：**` 等は`からのメッセージ`を含むため detail_body に保持
- `**1枚目：女教皇**` 等は`枚目`を含むため detail_body に保持
- 空行もセパレーターとして保持（カード間の区切りに必要）

## 今回やったこと（セッション10）

### バグ修正・UI改善（10件）
1. **KPラベル`**`マーカー除去**: `formatKeyPoints()`内でラベル部分から`**`をstrip
2. **KPインライン太字の色変更**: 白(#FAF5FF)→テーマ色フル不透明度に変更。コントラスト過剰を解消
3. **「○○へ」孤立ラベルフィルタ**: `^.{1,20}へ$`パターンの行をdetail_bodyから除外
4. **word-break対応**: `auto-phrase`のみ残し（keep-allは日本語でオーバーフローを起こすため削除）
5. **キャッチコピーフォント**: 長い行の閾値 17→16px
6. **テーマ色5色をライトパステルに**: コントラスト比3.2-3.5:1 → 4.7-7.0:1に改善
7. **KP body alpha除去**: テーマ色をフル不透明度で表示（視認性大幅向上）
8. **KP label opacity**: .6→.8に変更
9. **KP bodyテキストグロウ**: `text-shadow: 0 0 16px rgba(233,213,255,.18)` でキラキラ感追加
10. **CSS変数・グラデーション色更新**: --glow-soft, --glow-pink, --accent-pink, ボタングラデーション

### デプロイ
- コミット `366c15c` + `7230d6a` → GitHub push → Render自動デプロイ

## 現在の状態

- **サーバー**: `localhost:8000`で動作中
- **Render**: pushしてデプロイ中（デプロイ直後に全reading 404になっている。要確認）
- **最新コミット**: `7230d6a` (word-break: keep-all削除)

### 確認済み（ローカル）
- ✅ KPラベルの`**`マーカー除去
- ✅ KPインライン太字がテーマ色で表示
- ✅ テーマ色5色の明度UP（ローカルで視認性確認済み）
- ✅ KP bodyフル不透明度 + テキストグロウ
- ✅ 全リーディング（ID 1-14）正常ロード
- ✅ 個人リーディングへのKPパース変更の影響なし

### 未確認
- ❓ **Renderデプロイ完了** — デプロイ後に全reading 404。DBパスか再起動の問題の可能性
- ❓ **本番でのポスター背景画像(poster-dalle)** — ユーザーから「消えた？」と報告あり
- ❓ **iPhone実機でのword-break** — keep-all削除後の表示
- ❓ **魂のリーディング（個人）のサイズ** — ユーザーから「サイズミス」報告あり

## 未完了・次にやること

### 最優先: Renderデプロイ確認
1. **Renderダッシュボードでデプロイ状態確認** — ビルドログ・エラー確認
2. **全reading 404の原因調査** — DBパス、persistent disk、再起動後のDB作成
3. **ポスター背景画像の確認** — poster-dalleが表示されるか

### デザイン改善
4. **タロットカードアニメーション** — 紙飛行機のようにくるくる飛んでくるアニメーション（ユーザー要望）
5. **魂のリーディングのサイズ調整** — ユーザーから報告あり、具体的な箇所は未特定

### リーディング品質
6. **新規相性リーディング生成テスト** — 括弧不使用、入力情報繰り返し禁止が効いているか
7. **iPhone実機確認** — 改行・レイアウト・タップ操作

## 注意点・ハマりポイント

- **U+2500のダッシュ**: Claude APIが生成する`──`はU+2500（BOX DRAWINGS LIGHT HORIZONTAL）。U+2014（EM DASH）ではない。正規表現に必ず含めること
- **readings.pyのKPパース**: `**`は除去しない。JSの`kpBold`が`**`→`.kp-point`変換に使用。ただし**最初のstandalone bold行のみcatchcopy**、以降はスキップ
- **KPラベルの`**`除去**: `formatKeyPoints()`内でラベル（`：`の前）から`lbl.replace(/\*\*/g,'')`で除去。kpBoldは適用されないため必須
- **JS実行順序**: `groupPersonCards`（DOM再構築）→ `formatKeyPoints`（テキスト整形）の順。逆にするとラベル検出が壊れる
- **`_clean`に`：`を入れない**: breakBodyで`：`が改行になると本文が断片化する。`：`→改行はbreakShortとbreakLabeledだけ
- **改行ルールは文脈依存**: キャッチコピーと本文で`、`の扱いが真逆。一律適用は破綻する
- **CSS opacity は子要素に乗算**: `opacity: .7`の親の中で子に`opacity: 1`しても0.7のまま。色のmutingには`color: #c084fcaa`（8桁hex alpha）を使う
- **compat_themesとtimeline pop**: timeline sectionをpopしたら、compat_themesからもtimeline entryを除去しないと⑦⑧のslugがずれる
- **タロット行の保持条件**: `**...**`でも`枚目`or`からのメッセージ`を含む行はdetail_bodyに保持。空行もセパレーターとして保持
- **indented continuation line**: Pythonで`bl.startswith('  ')`（strip前）でチェック。`bl.strip()`するとインデント情報が失われる
- **サイズ統一ルール**: 複数行に分かれたとき、行ごとにサイズを変えない。最長行のサイズに全行を統一（小さい方に合わせる）
- **ポイントとキーワードの区別**: KPカード=色で区別（kpBold→.kp-point）。「更に詳しく」内の太字=サイズで区別（styleBold→.kw-hl）。逆にしない
- **ブラウザキャッシュ**: JSを変更したら`?v=N`をURLに付けるかCmd+Shift+Rでハードリフレッシュ
- **fortune-appのサーバー**: ポート8000で別アプリ（dispatch-app）が動いていることがある。`lsof -i :8000`で確認してから起動
- **ユーザーの年指定**: 現在は2026年5月。2025年のデータが出ると怒られる
- **ユーザーのデザインフィードバック傾向**: 改行ルールに極めて厳格。「直った」と報告する前に必ず実際のレンダリングを検証すること。場当たり修正を嫌う。問題を複数報告されたら即座に全件把握→一括修正
- **word-break: keep-allは日本語NG**: 日本語にはスペースがなく、文全体が1単語扱いになりテキストがオーバーフローする。`auto-phrase`のみ使い、Safariはデフォルトnormalにフォールバック
- **テーマ色のコントラスト**: 暗い紫背景(#352466)上では、紫・ピンク系の色はコントラスト比4.5:1以上を確保すること。旧色(#c084fc等)は3.2:1で不足していた
- **「○○へ」フィルタ**: detail_body構築時に`^.{1,20}へ$`パターンの行をスキップ。人物宛サブヘッダーが孤立テキストとして表示されるのを防止

## 参照ファイル
- Figma Make handoff: `figma-make-handoff.md`
- Figma Make URL: `https://www.figma.com/make/m6t0jZEGUsCa9r2NjOyJnW/Improve-Compatibility-Reading-Design`
- 反省ログ: `docs/reflections/2026-05-13.md`, `docs/reflections/2026-05-13_2.md`, `docs/reflections/2026-05-13_3.md`
- 設計書(Aura): `docs/superpowers/specs/2026-05-10-aura-redesign.md`
- 実装計画(Aura): `docs/superpowers/plans/2026-05-10-aura-redesign.md`

## 次回の開き方

```
HANDOFF.mdを読んで占いアプリの続きをして。
まずRenderデプロイの状態を確認（全reading 404問題の調査）。
次にポスター背景画像が消えた問題、魂のリーディングのサイズミスを調査・修正。
問題解決後、タロットカードの飛んでくるアニメーションに着手。
```
