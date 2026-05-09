# Stripe課金システム設計

## 概要
占いリーディングアプリにStripe Checkout Sessionを使った課金機能を追加。個人鑑定¥2,000、相性鑑定¥3,000。サンプル結果を無料閲覧可能にし、有料リーディングへの導線を作る。

## ユーザーフロー

### 有料リーディング
1. ホームページで価格を確認、サンプルを閲覧
2. 「魂のリーディング」or「相性リーディング」を選択 → フォームページ
3. フォーム入力 → 送信
4. サーバーがフォームデータをDB保存（status=pending）+ Stripe Checkout Session作成
5. ブラウザがStripe決済ページへリダイレクト
6. 決済完了 → `/payment/success?session_id=xxx` へリダイレクト
7. サーバーがStripeで決済確認 → ストリーミング生成ページ表示 → 自動リーディング開始
8. 生成完了 → 結果ページへ遷移

### キャンセル
- Stripe決済をキャンセル → `/payment/cancel` → フォームページへ戻るリンク表示

### サンプル閲覧
- ホームページの「サンプルを見る」→ `/sample` で固定サンプル結果を表示

## 技術設計

### DBスキーマ変更（readingsテーブル）
- `payment_status TEXT DEFAULT 'free'` — `pending` / `paid` / `free`
- `stripe_session_id TEXT` — Stripe Checkout Session ID
- `form_data_json TEXT` — 決済前のフォームデータをJSON保存

### 新規ファイル
- `app/routers/payment.py` — Checkout作成、success、cancelエンドポイント
- `app/templates/payment_success.html` — 決済完了→生成開始画面
- `app/templates/sample.html` — サンプル結果ページ

### 変更ファイル
- `app/main.py` — paymentルーター追加、マイグレーション追加
- `app/config.py` — `stripe_secret_key` 追加
- `app/models.py` — Readingモデルにカラム追加
- `app/static/js/reading.js` — フォーム送信先を`/api/payment/create-checkout`に変更
- `app/templates/index.html` — 価格表示、サンプルリンク追加
- `requirements.txt` — `stripe` 追加

### エンドポイント

#### POST /api/payment/create-checkout
- リクエスト：フォームデータ + reading_type（personal/compatibility）
- 処理：フォームデータをJSON化してDB保存、Stripe Checkout Session作成
- レスポンス：`{checkout_url: "https://checkout.stripe.com/..."}`

#### GET /payment/success
- クエリ：`session_id`
- 処理：Stripe APIで決済確認、reading.payment_status='paid'に更新、ストリーミング生成ページをレンダリング
- ページ内JSが自動的に`/api/readings/generate/{reading_id}`を呼んでストリーミング開始

#### GET /payment/cancel
- フォームページへの戻りリンクを表示

#### POST /api/readings/generate/{reading_id}
- 既存のstream処理を切り出し、reading_idを受け取って生成するエンドポイント
- payment_status='paid'のreadingのみ生成許可

### Stripe設定
- Checkout Session mode: `payment`
- `price_data`で動的に金額指定（Dashboardでの事前Product作成不要）
- `client_reference_id`: reading ID
- `success_url`: `/payment/success?session_id={CHECKOUT_SESSION_ID}`
- `cancel_url`: `/payment/cancel`

### 環境変数
- `STRIPE_SECRET_KEY` — .envとRender環境変数に設定
