# セッション引き継ぎ — 占いリーディングWebアプリ（セッション9後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。セッション9でKP色分け・タロットSVG・テーマ色ズレ・空セクション等8件のバグを一括修正しRenderにデプロイ済み。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (**public**)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン

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
├── docs/reflections/ (2026-05-11.md, 2026-05-12.md, 2026-05-13.md, 2026-05-13_2.md)
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

## カラーパレット

- 背景: #352466 〜 #4a3590
- テキスト: #F5F0FF（メイン）、#D8B4FE（サブ）
- アクセント: #E9D5FF（モーヴ）、#F0ABFC（ピンク）、#A78BFA（ラベンダー）
- 禁止色: オレンジ・暖色系・ゴールド(#FFD700)

## セクションテーマカラー（個人リーディング・10色）

| セクション | slug | 色 |
|-----------|------|-----|
| 全体要約 | summary | #a78bfa |
| 性格・本質 | personality | #c084fc |
| 才能・強み | strength | #818cf8 |
| 注意点・課題 | caution | #f472b6 |
| 仕事・お金 | career | #34d399 |
| 恋愛・人間関係 | love | #f0abfc |
| 今年のテーマ | yearly | #60a5fa |
| 月別の流れ | monthly | #a78bfa |
| 今すぐやること | action | #fbbf24 |
| 魂のメッセージ | message | #e9d5ff |

## セクションテーマカラー（相性リーディング・8色）

| セクション | slug | 色 |
|-----------|------|-----|
| 二人の全体像 | overview | #c084fc |
| それぞれの本質 | essence | #a78bfa |
| 相性分析 | chemistry | #f0abfc |
| 関係の課題 | challenge | #f472b6 |
| 恋愛アドバイス | love | #e9d5ff |
| 今年のタイムライン | timeline | #60a5fa |
| 今すぐやること | action | #fbbf24 |
| 魂のメッセージ | message | #34d399 |

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

### KPカード色分けルール（セッション9で実装）
- **技術テキスト** = テーマ色 + alpha `aa`（控えめ） → `.kp-body`
- **結論（`**...**`部分）** = `#FAF5FF`白（目立つ） → `.kp-point`
- ラベルとテキストの間に **〰** セパレーター → `.kp-sep`
- CSS `opacity`は子要素に乗算されるので使わない。色のmutingには8桁hex alpha（`#c084fcaa`）を使用

### Jinja側の処理
- Jinjaでは`「」`除去のみ
- `| replace('、','<br>')`等はしない（JSと競合するため）
- `| safe`も不要
- KPの`**`マーカーはJinja側で除去しない（JSの`kpBold`が`.kp-point`に変換するため）

## KPパース（readings.py）のルール（セッション9で改修）

### key_pointsの構築
- **最初の`**...**`standalone行のみ** → `key_points[0]`（キャッチコピー）
- 以降の`**...**`standalone行 → **スキップ**（サブヘッダーであり、KPカードにしない）
- `- `で始まるbullet行 → `key_points[1:]`
- `key_points[:5]`で最大5件（catchcopy + KP最大4枚）

### detail_bodyの構築
- bullet行（`- `, `* `）→ スキップ（KPカードに表示済み）
- standalone bold行（`**...**`）→ `枚目`か`からのメッセージ`を含まない限りスキップ
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

## 今回やったこと（セッション9）

### バグ修正8件（一括）
1. **KP色分け方向の反転**: `kpBold`が結論をテーマ色にしていた → 結論=白`.kp-point`、本文=テーマ色+alpha`.kp-body`に修正
2. **タロット行のdetail_body除外**: `**女帝からのメッセージ：**`が`枚目`チェックのみで除外されていた → `からのメッセージ`も保持条件に追加
3. **compat_themesのズレ**: timeline pop後に⑧がaction slugになっていた → compat_themesからもtimeline除去
4. **サブヘッダーのKPカード混入**: `**二人でできる行動：3つ**`等がKPカードに → 最初のbold行のみcatchcopy
5. **空の「更に詳しく」**: detail_bodyが空なのにボタン表示 → Jinja条件で非表示
6. **改善策のdetail_body漏出**: indented continuation行がorphanedに → `bl.startswith('  ')`でスキップ
7. **タロット本文の`。`改行**: `breakBody`適用で不自然 → `「」`除去のみに変更
8. **タロットカードbodyの✦チェック**: 第3カード本文が`✦`で始まる場合にスキップされていた → ✦チェック除去

### CSSデザイン
- `.kp-point` (結論: 白、太字)、`.kp-body` (本文: テーマ色+alpha)、`.kp-sep` (〰セパレーター) 追加

### デプロイ
- コミット `6c065b6` → GitHub push → Render自動デプロイ

## 現在の状態

- **サーバー**: `localhost:8000`で動作中
- **Render**: pushしてデプロイ中（ビルド完了は未確認）
- **最新の相性リーディング**: reading ID 14（新プロンプトで生成済み）
- **未コミット変更**: prompts.py（前セッションの変更）、HANDOFF.md

### 確認済み
- ✅ ①KP色分け（技術テキスト=控えめ、結論=白）
- ✅ ②人物グルーピング（Yuna/びー分離）
- ✅ ⑧タロットカードSVG（女帝/星/ペンタクルス表示、本文一行流し）
- ✅ テーマ色のズレ修正（⑧=message slug）
- ✅ 空セクションの「更に詳しく」非表示
- ✅ 〰セパレーター追加

### 未確認
- ❓ Renderデプロイ完了
- ❓ 個人リーディング（魂のリーディング）への影響
- ❓ iPhone実機表示

## 未完了・次にやること

### 最優先: 確認作業
1. **Renderデプロイ完了確認** — `fortune-reading-app.onrender.com/reading/14` を確認
2. **個人リーディングへの影響確認** — KPパース変更（catchcopy_found等）が個人リーディングを壊していないか
3. **prompts.pyのコミット** — 未コミットの変更がある（前セッション分の可能性）

### デザイン改善
4. **タロットカードアニメーション** — 紙飛行機のようにくるくる飛んでくるアニメーション（ユーザー要望）

### リーディング品質
5. **新規相性リーディング生成テスト** — 括弧不使用、入力情報繰り返し禁止が効いているか
6. **iPhone実機確認** — 改行・レイアウト・タップ操作

## 注意点・ハマりポイント

- **U+2500のダッシュ**: Claude APIが生成する`──`はU+2500（BOX DRAWINGS LIGHT HORIZONTAL）。U+2014（EM DASH）ではない。正規表現に必ず含めること
- **readings.pyのKPパース**: `**`は除去しない。JSの`kpBold`が`**`→`.kp-point`変換に使用。ただし**最初のstandalone bold行のみcatchcopy**、以降はスキップ
- **JS実行順序**: `groupPersonCards`（DOM再構築）→ `formatKeyPoints`（テキスト整形）の順。逆にするとラベル検出が壊れる
- **`_clean`に`：`を入れない**: breakBodyで`：`が改行になると本文が断片化する。`：`→改行はbreakShortとbreakLabeledだけ
- **改行ルールは文脈依存**: キャッチコピーと本文で`、`の扱いが真逆。一律適用は破綻する
- **CSS opacity は子要素に乗算**: `opacity: .7`の親の中で子に`opacity: 1`しても0.7のまま。色のmutingには`color: #c084fcaa`（8桁hex alpha）を使う
- **compat_themesとtimeline pop**: timeline sectionをpopしたら、compat_themesからもtimeline entryを除去しないと⑦⑧のslugがずれる
- **タロット行の保持条件**: `**...**`でも`枚目`or`からのメッセージ`を含む行はdetail_bodyに保持。空行もセパレーターとして保持
- **indented continuation line**: Pythonで`bl.startswith('  ')`（strip前）でチェック。`bl.strip()`するとインデント情報が失われる
- **サイズ統一ルール**: 複数行に分かれたとき、行ごとにサイズを変えない。最長行のサイズに全行を統一（小さい方に合わせる）
- **ポイントとキーワードの区別**: KPカード=色で区別（kpBold→.kp-point白）。「更に詳しく」内の太字=サイズで区別（styleBold→.kw-hl）。逆にしない
- **ブラウザキャッシュ**: JSを変更したら`?v=N`をURLに付けるかCmd+Shift+Rでハードリフレッシュ
- **fortune-appのサーバー**: ポート8000で別アプリ（dispatch-app）が動いていることがある。`lsof -i :8000`で確認してから起動
- **ユーザーの年指定**: 現在は2026年5月。2025年のデータが出ると怒られる
- **ユーザーのデザインフィードバック傾向**: 改行ルールに極めて厳格。「直った」と報告する前に必ず実際のレンダリングを検証すること。場当たり修正を嫌う。問題を複数報告されたら即座に全件把握→一括修正

## 参照ファイル
- Figma Make handoff: `figma-make-handoff.md`
- Figma Make URL: `https://www.figma.com/make/m6t0jZEGUsCa9r2NjOyJnW/Improve-Compatibility-Reading-Design`
- 反省ログ: `docs/reflections/2026-05-13.md`, `docs/reflections/2026-05-13_2.md`
- 設計書(Aura): `docs/superpowers/specs/2026-05-10-aura-redesign.md`
- 実装計画(Aura): `docs/superpowers/plans/2026-05-10-aura-redesign.md`

## 次回の開き方

```
HANDOFF.mdを読んで占いアプリの続きをして。
まずRenderデプロイが完了しているか確認して、本番の reading/14 を開いて表示確認。
次に個人リーディング（IDは1〜13のどれか）もブラウザで開いてKPパース変更の影響がないか確認。
問題なければタロットカードの飛んでくるアニメーションに着手。
```
