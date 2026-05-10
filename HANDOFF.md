# セッション引き継ぎ — 占いリーディングWebアプリ（セッション3後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。Stripe課金システム実装済み（審査待ち）。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (private)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン

## 技術スタック
FastAPI + Jinja2 + SQLite(aiosqlite) + Claude API(Sonnet) + DALL-E 3 + Stripe
Python 3.11 on Render

## ディレクトリ構成
```
fortune-app/
├── app/
│   ├── main.py, config.py, database.py, models.py
│   ├── routers/ (pages, profiles, readings, chat, payment)
│   ├── services/ (claude_client, prompts, rokusei, shichusuimei, numerology, image_generator)
│   ├── templates/ (base, index, reading_form, compatibility_form, reading_result, chat, reading_generate, sample, payment_success, payment_cancel)
│   └── static/ (css/style.css, js/reading.js, js/chat.js)
├── tests/
├── docs/superpowers/specs/ (stripe-billing-design.md)
└── requirements.txt, Procfile, render.yaml, .env
```

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
- Stripe: テストキー(sk_test_...)をRenderに設定済み。ライブキー(sk_live_...)は審査待ち

## Stripe課金システム（実装済み・審査待ち）
- 個人鑑定 ¥2,000 / 相性鑑定 ¥3,000
- Stripe Checkout Session方式
- **現在は無料モード**: reading.jsのフォーム送信先が直接ストリーミングAPIを呼んでいる
- **有料化の切替手順**:
  1. `app/static/js/reading.js` の2箇所の `TODO` コメントを探す
  2. `/api/readings/personal/stream` → `/api/payment/create-checkout` に変更（JSON bodyも `{reading_type:'personal', form_data: formData}` に）
  3. `/api/readings/compatibility/stream` → `/api/payment/create-checkout` に変更（同様）
  4. `app/templates/index.html` の「無料体験中」を「¥2,000」「¥3,000」に戻す
  5. Render環境変数 `STRIPE_SECRET_KEY` をライブキーに変更

## SSEストリーミング
- スペースチャンク消失バグ修正済み（.trim() → .slice()）
- 改行エスケープ修正済み（サーバー側で⏎にエスケープ、クライアントで復元）
- chat.js, reading.js, payment_success.html の3ファイルが対象

## 鑑定中アニメーション
- テキストストリーミング表示を廃止
- 回転リング＋水晶＋星の瞬き＋フェーズテキスト切替＋プログレスバー
- 完了後に結果ページへ自動遷移

## チャットプロンプトの制約
- ユーザーの行動についてアドバイス・正論・説教をしない
- 星の配置から状況を照らすことに徹する
- ユーザーの味方であり続ける

## 未完了・次にやるべきこと

### 最優先
1. **DALL-E画像の動作確認** — URL不一致バグは修正済み（9821ad6）だが、実際にスマホで画像が表示されるか未確認
2. **Render Diskの手動追加** — Renderダッシュボードで/dataに1GBディスク追加が必要。やらないとデプロイのたびにDBが消える
3. **DALL-E画像の品質確認** — プロンプトを改善したが、生成結果が参照画像レベルか未検証

### Stripe関連
4. **Stripe本人確認の審査完了待ち** — 完了したら上記の有料化切替手順を実行
5. **Stripeセキュリティチェックリストの委託先設定** — 「委託先企業」が誤選択された可能性、「従業員」に修正が必要かも

### デザイン改善
6. **ポスターカードのデザイン品質** — HTML/CSSポスターは参照画像とまだ差がある。DALL-E画像がメインビジュアルとして機能すれば解決
7. **フォームのデフォルト値** — 現在Yunaの情報がプリセットされている。本番公開前に空に戻す必要あり

### 機能改善
8. **相性リーディングのテスト**
9. **画像保存ボタン（html2canvas）のテスト**
10. **チャット機能のテスト** — 正論禁止のプロンプト変更後の動作確認

## ユーザー（ゆうな）の要望の温度感
- デザインへのこだわりが強い（参照画像レベルを求める）
- 占術の正確性を重視（自分の結果を知っていて間違いを指摘してくる）
- 文章アレルギーの人への配慮（箇条書き・太字ポイント・キャッチコピー重視）
- 画像保存＆共有を重要視
- **鑑定師チャットで正論・アドバイスを言われたくない**（味方でいてほしい）
- アクションプラン（/Users/kousuke/Documents/action-plan-may15.html）に基づく課金化を推進中

## 参照画像
`/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg` — ChatGPTで生成されたパステルラベンダー×クリスタルのスピリチュアル鑑定ポスター

## 関連ファイル
- 作業ログ1: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ開発.md`
- 作業ログ2: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ改善.md`
- 作業ログ3: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリ課金化.md`
- アクションプラン: `/Users/kousuke/Documents/action-plan-may15.html`
- 設計書: `/Users/kousuke/fortune-app/docs/superpowers/specs/2026-05-09-stripe-billing-design.md`
