# セッション引き継ぎ — 占いリーディングWebアプリ（セッション4後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。Y2Kデザインにリニューアル中。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (private)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン

## 技術スタック
FastAPI + Jinja2 + SQLite(aiosqlite) + Claude API(Sonnet) + DALL-E 3 + Stripe/PayPal
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
├── docs/superpowers/specs/ (stripe-billing-design.md, y2k-design-overhaul.md)
├── docs/superpowers/plans/ (y2k-design-overhaul.md)
└── requirements.txt, Procfile, render.yaml, .env
```

## 現在のデザイン状態（セッション4で変更）

### 完了・動作しているもの
- **トップページ**: Y2Kデザイン適用済み（パープルグラデーション背景、星の瞬き、グローカード、🔮+4層リング、Shippori Minchoタイトル）
- **フォームページ**: デフォルト値クリア済み、生年月日・出生時刻がテキスト入力式に変更
- **DALL-E並行生成**: ストリーミング中にasyncio.create_taskで裏でテキストなし画像生成、ローカル保存
- **OGPメタタグ**: base.htmlにデフォルト設定、結果ページにog:image設定
- **決済**: 一時的に外してストリーミング直接呼び出し（reading.js）。価格表示は「FREE」

### ★ 結果ページが破綻している（最優先修正）
- DALL-E画像をフルスクリーン背景にしてHTMLテキストをオーバーレイする構造にしたが、**画像が情報量多すぎてテキストが読めない**
- カードがはみ出して画面に収まっていない
- Claude生成テキストに絵文字が含まれて世界観崩壊
- **次のセッションで根本的にやり直す必要がある**

### 結果ページ修正の方針案
1. **DALL-E画像はヒーローバナーのみ**（上部に表示、テキスト重ねない）→ その下にカード配置
2. **DALL-E画像をやめてCSS onlyでデザイン**
3. **DALL-E画像を上半分だけクロップして使う**

## デザイン方針（ユーザー確定済み）
- ターゲット: 20代女性、SNS映え、Instagram ストーリーでシェアしたくなる
- 背景: ダーク寄りパープルグラデーション（#A78BFA → #A855F7）
- キラキラ: ✦✧· の白い星が瞬くアニメーション（丸ドット禁止）
- フォント: Shippori Mincho（タイトル）、Noto Sans JP（本文）、Quicksand（英字）
- 絵文字: UIでは🌙のみ許可、それ以外は英字ラベル
- 枠: 角ばり（border-radius 8px以下）
- 色: オレンジ味・暖色系は排除。パープル×ラベンダー×モーヴピンク(#E0B0FF)で統一
- 改行: デザインとして意味の区切りで折る
- 2層構造: ビジュアル重視のファーストビュー → 「もっと詳しく」で詳細アコーディオン

## ユーザー（ゆうな）のデザインフィードバック傾向
- 「ちゃちい」「安っぽい」に敏感 → 丸ゴシック、絵文字多用、カーブの多い枠はNG
- オレンジ・暖色系を嫌う → ゴールド(#FFD700)もNG、ピンクはモーヴ系ならOK
- 文字のふにゃつきが嫌い → 丸ゴシック(Zen Maru Gothic)は見出しから除外済み
- 実機（スマホ）確認を重視 → 必ずスマホでの見え方を確認すること
- 参照画像（ChatGPTで生成したポスター）のクオリティを求めている

## 占術計算モジュール（Pythonで正確に計算）
- `rokusei.py`: 六星占術（運命星+陰陽+霊合星人+12年周期+大殺界判定）
- `shichusuimei.py`: 四柱推命（年柱の天干地支+五行+陰陽）
- `numerology.py`: 数秘術（ライフパスナンバー、マスターナンバー11/22/33保持）

## 検証済みの計算結果
- ゆうな(1995/6/26): 火星人マイナス(-), LP11/2(マスターナンバー), 2026年=健弱
- 彼(1999/5/7): LP4

## APIキー
- Anthropic: .env + Render環境変数に設定済み
- OpenAI: .env + Render環境変数に設定済み
- Stripe: テストキー設定済み。ライブキー審査待ち
- PayPal: REST API設定済み（payment.pyに実装あり）

## SSEストリーミング
- スペースチャンク消失バグ修正済み（.trim() → .slice()）
- 改行エスケープ修正済み（サーバー側で⏎にエスケープ、クライアントで復元）
- DALL-E画像生成がストリーミング中に並行実行される

## チャットプロンプトの制約
- ユーザーの行動についてアドバイス・正論・説教をしない
- 星の配置から状況を照らすことに徹する
- ユーザーの味方であり続ける

## 未完了・次にやるべきこと

### 最優先
1. **結果ページのデザイン根本的やり直し** — DALL-E背景+テキストオーバーレイが破綻。上記の方針案から選んで再実装。**ui-ux-pro-max スキルを使うこと**
2. **Claude AI生成テキストから絵文字排除** — `app/services/prompts.py` のシステムプロンプトに「絵文字を使わない」指示を追加
3. **未pushの変更をpush** — ローカルに決済外し・デザイン修正が溜まっている

### インフラ
4. **Render Diskの手動追加** — /dataに1GBディスク追加が必要。やらないとデプロイのたびにDBが消える

### 決済関連
5. **決済の再導入** — 現在は一時的に外してFREE状態。Stripe/PayPal審査完了後に再導入
6. **有料化の切替手順**: reading.jsの送信先を `/api/payment/create-checkout` に戻す、価格表示を戻す

### デザイン改善
7. **フォームのデザイン整え** — Y2Kスタイルは適用済みだが微調整が必要かも
8. **チャットページのデザイン確認** — Y2Kパレットに更新済みだが実機未確認

### 機能テスト
9. **相性リーディングのテスト**
10. **画像保存ボタン（html2canvas）のテスト** — 結果ページ修正後
11. **チャット機能のテスト**

## 参照画像
`/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg` — ChatGPTで生成されたパステルラベンダー×クリスタルのスピリチュアル鑑定ポスター

## 関連ファイル
- 作業ログ1: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ開発.md`
- 作業ログ2: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ改善.md`
- 作業ログ3: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリ課金化.md`
- 作業ログ4: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリY2Kデザイン.md`
- アクションプラン: `/Users/kousuke/Documents/action-plan-may15.html`
- 設計書: `/Users/kousuke/fortune-app/docs/superpowers/specs/2026-05-10-y2k-design-overhaul.md`
- 実装計画: `/Users/kousuke/fortune-app/docs/superpowers/plans/2026-05-10-y2k-design-overhaul.md`
- 承認済みモックアップ: 削除済み（mockup-overlay.html）。CSSの `.poster-card-wrap` 等にスタイル残存
