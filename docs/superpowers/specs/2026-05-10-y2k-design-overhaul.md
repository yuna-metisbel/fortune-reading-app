# Y2K Glow-Up Design Overhaul

## Goal
占いリーディングWebアプリのデザインを、20代女性がInstagramストーリーでシェアしたくなるY2K風デザインにリニューアルする。文字が苦手な子でもハマれるビジュアル重視の2層構造にする。

## Design Decisions

### Visual Direction
- Y2K Glow-Up: キラキラ×パープル×ピンクのグラデーション、品のあるグロー効果
- ライト寄りの中間トーン背景（ラベンダー〜パープル系の動くグラデーション）
- 絵文字は原則排除。メッセージセクションの🌙のみ許可。それ以外は英字ラベルで世界観を統一
- 改行はデザインとして意味の区切りで折る（例: 「感性とやさしさを」「活かす」で2行）

### Fonts
- 見出し: `Zen Maru Gothic`（丸ゴシック、Y2K感+可愛い）
- 本文: `Noto Sans JP`（可読性キープ）
- 英字アクセント: `Quicksand`（Y2K定番の丸い英字フォント）

### Poster (Result Page)
- DALL-E 3で鑑定ごとにユニークな背景画像を生成（テキストなし、純粋なビジュアルのみ）
- 画像の上にHTML/CSSでテキストをオーバーレイ
- すりガラス風カードで読みやすさ確保
- 構成:
  - ヘッダー: タイトル「あなたの魂が描く人生の星図」+ ユーザー名
  - Soul Theme: キャッチコピー1行（最大2行改行）
  - グリッド: 4カード（自然な性格/強み/恋愛傾向/仕事の方向）各カードは英字ラベル+タイトル+キャッチコピー+キーワードタグ
  - メッセージ: 🌙付きの締めメッセージ
  - フッター: サイトURL

### 2-Layer Structure
1. **ファーストビュー（ポスター）**: ビジュアル重視、文字少なめ。シェアしたくなるレベル
2. **「もっと詳しく読む」の先**: 既存のアコーディオン詳細リーディング（文字好きな人向け）

### Image Generation
- DALL-E 3 API（既存設定済み）
- テキストなし: クリスタル、月、星、水彩背景、宝石などビジュアル装飾のみ
- サイズ: 1024x1792 (9:16, ストーリーサイズ)
- 品質: HD
- タイミング: 鑑定ストリーミング中に裏で並行生成（asyncio.create_task）
- コスト: 約$0.08/枚（¥2,000の鑑定料に対して許容範囲）

### Share Features
1. **ストーリー用画像保存**: html2canvas でポスター（DALL-E背景+HTMLテキスト）をPNG化してダウンロード
2. **URLシェア + OGPカード**: `<meta og:image>` にDALL-E画像URLを設定。LINE/Twitterでリッチプレビュー表示

### Top Page Changes
- 背景: ラベンダー〜パープル系の動くグラデーション
- キラキラ: ✦✧· の小さな星が静かに瞬くCSSアニメーション（丸ドット禁止）
- メニューカード: グラデーションボーダー付きすりガラスカード
- ヒーローエリア: 浮かぶクリスタルアニメーション

### Form Page Changes
- 同じY2Kデザインシステムを適用
- デフォルト値をクリア（yuna情報を空に）

### Files to Modify
- `app/static/css/style.css` — 全面改修（Y2Kデザインシステム）
- `app/templates/base.html` — フォント変更、sparkles変更
- `app/templates/index.html` — メニューカード構造変更
- `app/templates/reading_result.html` — ポスターオーバーレイ構造に変更、シェアボタン追加、OGP追加
- `app/templates/reading_form.html` — デフォルト値クリア、デザイン適用
- `app/templates/reading_generate.html` — デザイン適用
- `app/services/image_generator.py` — テキストなしプロンプトに変更（済）
- `app/routers/readings.py` — 画像並行生成ロジック追加、OGP用メタ情報追加
- `app/static/js/reading.js` — html2canvas保存機能改善

### Reference Files
- Mockup: `/Users/kousuke/fortune-app/mockup-overlay.html`（承認済みデザイン）
- Reference image: `/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg`
- Test DALL-E bg: `/Users/kousuke/fortune-app/app/static/images/poster-bg.png`
