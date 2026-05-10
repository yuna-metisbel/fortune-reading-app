# Aura/Ethereal フルリデザイン設計書

## 概要
占いリーディングWebアプリの全ページをAura/Etherealトーンで統一リデザインする。20代女性向け、SNS映え、Instagram共有を重視。

## デザインシステム

### カラーパレット
| 用途 | コード | 備考 |
|------|--------|------|
| 背景（深部） | `#352466` | 明るめパープル |
| 背景（中間） | `#4a3590` | ラベンダー寄り |
| 背景グロー | `#7c3aed` / `#a78bfa` | radial-gradient複数層 |
| カード背景 | `rgba(255,255,255,0.08-0.1)` | backdrop-filter: blur(16px) |
| カードボーダー | `rgba(216,180,254,0.22-0.28)` | |
| テキスト主 | `#f5f0ff` | |
| テキスト副 | `#d8b4fe` | |
| アクセント | `#f0abfc` | ピンク系ラベル |
| アクセント2 | `#e9d5ff` | モーヴ |
| ハイライト | `#faf5ff` | タイトル等 |

### 背景構成
- radial-gradient 5-6層（強度0.25-0.55）で全体を明るく発光させる
- 浮遊グローオーブ 3-4個（blur(50px)、orbFloatアニメーション8s）
- 背景は全ページ共通CSS

### タイポグラフィ
| 役割 | フォント | ウェイト |
|------|---------|---------|
| 見出し | Rajdhani + Noto Sans JP | 700 |
| 強調・サブ見出し | Inter + Noto Sans JP | 700-800 |
| ラベル・数字 | JetBrains Mono | 600-700 |
| 本文 | Noto Sans JP | 500 |

### 装飾
- **キラキラ**: ✦✧·の3色（白・ラベンダー・ピンク）、25-33個、twinkleアニメーション
- **クリスタル**: CSS三角形+after擬似要素、四隅に配置
- **マンダラ**: SVG、同心円+8方位星+宝石ドット、slowSpin 60s
- **タロットカード挿絵**: SVG、各ページ・セクションに合わせたモチーフ
- **シマー**: カード表面を光が横切るアニメーション（shimmer 6s）
- **グローパルス**: タイトルテキストのtext-shadow点滅
- **🌙**: floatGlowアニメーション、唯一許可された絵文字

### コンポーネント
- **Glass Card**: backdrop-filter:blur(16px)、薄いボーダー、border-radius:10-12px
- **ボタン**: gradient(#9333ea, #c084fc)、box-shadow、hover時translateY(-2px)
- **アコーディオン**: Glass Card + 開閉トランジション(max-height)
- **すりガラスタイトル**: blur(20px) + パープルグラデーション透過

### 排除するもの
- オレンジ・ゴールド・暖色系
- 絵文字（🌙以外）
- 丸ゴシック
- border-radius 16px以上
- 4層リング回転（旧ヒーロー）

---

## ページ別設計

### 1. トップページ (index.html)
**モックアップ**: `.superpowers/brainstorm/top-page-mockup.html`

- ヒーロー: マンダラSVG(slowSpin) + 🌙中央 + タイトル「あなたの魂が描く人生の星図」
- 6占術タグ: JetBrains Mono、pill型
- メニューカード3枚: Glass Card、アイコン+タイトル+説明+FREE badge+矢印
  - 魂のリーディング（🌙）
  - 相性リーディング（✨）
  - サンプル鑑定を見る（✦）
- 最近の鑑定: 条件分岐表示、空の場合は🌙+案内テキスト
- フェードインアニメーション(fadeSlideUp)

### 2. フォームページ (reading_form.html / compatibility_form.html)
**モックアップ**: `.superpowers/brainstorm/form-page-mockup.html`

- ヘッダー: ←戻る + タイトル + サブテキスト
- タロットカード挿絵: 女教皇SVG、半透明+色付き、パープルドロップシャドウ
- フォーム: Glass Cardでセクション分け
  - SAVED PROFILE（select）
  - BASIC INFO（ニックネーム、生年月日3列、出生時刻、出生地、性別、血液型）
  - READING THEME（textarea）
- 送信ボタン: gradient、glowシャドウ
- 入力フォーカス時: ピンクボーダー + グローシャドウ
- 背景は他ページより明るめ（#352466 / #4a3590）
- キラキラ33個

### 3. ローディングページ (reading_generate.html)
**モックアップ**: `.superpowers/brainstorm/loading-chat-mockup.html` (LOADING tab)

- マンダラSVG回転（slowSpin 8s — 生成中は速め）
- 🌙中央 floatGlow
- タイトル「星の配置を読み解いています」
- 8フェーズ進行表示:
  1. 生年月日から星図を作成
  2. 六星占術の運命星を算出
  3. 数秘術のライフパスを計算
  4. 四柱推命の天干地支を解析
  5. タロットカードを引く
  6. 6つの占術を統合
  7. リーディングを生成中
  8. 背景画像を生成中
- 各フェーズ: ドットインジケーター（active=ピンクpulse、done=薄い）
- DALL-E並行生成は維持（フェーズ8で表示）

### 4. 結果ページ (reading_result.html) ★最重要
**モックアップ**: `.superpowers/brainstorm/result-page-v6.html` をベース

#### ファーストビュー（ポスター）
- DALL-E画像: opacity 0.18のぼかし背景（現行維持）
- SOUL READING ラベル
- 名前 + 生年月日（JetBrains Mono 700）
- マンダラSVG（slowSpin 60s）+ 🌙
- **すりガラスカード内にタイトル**（キャッチコピー）+ サブテキスト
- タロット風ディバイダー（クリスタル3つのSVG）
- 4枚ハイライトカード（PERSONALITY / STRENGTH / LOVE / CAREER）
- メッセージボックス（✧装飾付き）
- 「✦ 占いの結果を画像にする」ボタン → **GPT Image APIでポスター生成**
- 「LINK をコピー」ボタン
- DETAIL ↓ スクロールプロンプト

#### 詳細セクション（アコーディオン）
- 6セクション、各セクションに:
  - パステルSVGアイコン（44×44、内容に合わせたモチーフ）
  - タロット風SVG挿絵（セクション内上部）
  - 要約テキスト（短文、改行多め、line-height: 2.4）
  - 「✧ 更に詳しく」ボタン → 長文展開（read-more-body）
- セクション一覧:
  1. 総合リーディング（星図アイコン）
  2. 性格・本質（ハートアイコン）
  3. 強み・才能（星アイコン）
  4. 恋愛傾向（月と光アイコン）
  5. 仕事の方向（ブリーフケースアイコン）
  6. 2026年のテーマ（サイクルアイコン）

#### 月別の流れ
- ヘッダー: カレンダーSVGアイコン + 「2026年 月別の流れ」
- 3列×4行グリッド（12ヶ月）
- 各月カード: 月名(JAN等) + キーワード2行 + ✧で運勢表示
- 今月ハイライト（ピンクボーダー+グロー）
- **クリック展開**: タップで全幅に広がり詳細テキスト表示

#### CTA
- 「✦ 鑑定師に相談する」ボタン → チャットページ
- ← TOP リンク

### 5. チャットページ (chat.html)
**モックアップ**: `.superpowers/brainstorm/loading-chat-mockup.html` (CHAT tab)

- 固定ヘッダー: ←戻る + 🌙 + タイトル + SOUL READING ラベル
- スクロールメッセージエリア
- ウェルカムメッセージ: ✦アイコン + 案内テキスト
- バブル:
  - ユーザー: gradient(purple), 右寄せ
  - アシスタント: Glass Card, 左寄せ, 「✦ 鑑定師」ラベル
- タイピングインジケーター: 3ドットバウンス
- 固定入力エリア: textarea(auto-resize) + 丸送信ボタン(↑)

### 6. サンプルページ (sample.html)
- 結果ページと同じレイアウト
- 「これはサンプルです」ラベル
- CTAはリーディングフォームへのリンク

---

## GPT Image ポスター生成

### フロー
1. ユーザーが結果ページで「占いの結果を画像にする」をタップ
2. フロントからPOST `/api/readings/{id}/generate-poster`
3. バックエンドがリーディング結果からプロンプトを組み立て
4. OpenAI GPT Image API (gpt-image-1) で1080×1920画像を生成
5. 画像をローカル保存、URLを返す
6. フロントでダウンロード/表示

### プロンプトテンプレート
```
パステルラベンダー × クリスタルのスピリチュアル鑑定
淡いラベンダー、パステルパープル、シルバー、白を基調にした、
幻想的で透明感のあるスピリチュアル鑑定ポスター。

全体は柔らかい雲、月、星、クリスタル、光の粒、繊細な装飾フレームで構成し、
女性向けの優しく神秘的な雰囲気にする。

タイトル: 「{catch_copy}」
名前: {nickname}
生年月日: {birthdate}

セクション配置:
- 魂のテーマ: {soul_theme}
- 性格: {personality}
- 強み: {strength}
- 恋愛傾向: {love}
- 仕事の方向: {career}
- 今年のテーマ: {yearly_theme}
- メッセージ: {message}

装飾にはムーンストーン、アメジスト、ローズクォーツ、蝶、月のモチーフ、
吊り下げオーナメント、花、光のエフェクトを使用する。

日本語テキストで、優雅で可愛く、柔らかい読みやすいレイアウトの
1枚完結の鑑定シートにしてください。
```

### DALL-E背景画像
- 既存のストリーミング中並行生成は維持
- 結果ページの背景としてopacity 0.18で使用
- テキストなし画像（現行と同じ）

---

## プロンプト修正

### Claude AIテキストから絵文字排除
`app/services/prompts.py` のシステムプロンプトに以下を追加:
- 「絵文字を一切使用しない」
- 「記号は✦✧のみ許可」

---

## 対象ファイル
| ファイル | 変更内容 |
|---------|---------|
| `app/static/css/style.css` | 全面書き直し（2009行→新デザインシステム） |
| `app/templates/base.html` | フォント変更、背景/スパークルJS |
| `app/templates/index.html` | マンダラヒーロー、メニューカード |
| `app/templates/reading_form.html` | タロット挿絵、Glass Cardフォーム |
| `app/templates/compatibility_form.html` | 同上（2人分） |
| `app/templates/reading_generate.html` | マンダラ回転、フェーズ表示 |
| `app/templates/reading_result.html` | ★全面書き直し。ポスター+アコーディオン+月別+GPT Image |
| `app/templates/chat.html` | バブルデザイン、固定ヘッダー |
| `app/templates/sample.html` | 結果ページ準拠 |
| `app/static/js/reading.js` | GPT Imageポスター生成呼び出し追加 |
| `app/services/prompts.py` | 絵文字排除指示追加 |
| `app/services/image_generator.py` | GPT Imageポスター生成関数追加 |
| `app/routers/readings.py` | ポスター生成APIエンドポイント追加 |

---

## モックアップファイル
| ファイル | ページ |
|---------|--------|
| `.superpowers/brainstorm/result-page-v6.html` | 結果ページ（タブ・月別・更に詳しく） |
| `.superpowers/brainstorm/result-page-v7.html` | ポスター生成デモ |
| `.superpowers/brainstorm/top-page-mockup.html` | トップページ |
| `.superpowers/brainstorm/form-page-mockup.html` | フォームページ（タロット挿絵付き） |
| `.superpowers/brainstorm/loading-chat-mockup.html` | ローディング+チャット |
