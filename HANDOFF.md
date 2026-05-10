# セッション引き継ぎ — 占いリーディングWebアプリ（セッション5後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。Aura/Etherealデザインにリニューアル中。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (private)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン

## 技術スタック
FastAPI + Jinja2 + SQLite(aiosqlite) + Claude API(Sonnet) + DALL-E 3 + GPT Image API + Stripe/PayPal
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
├── docs/superpowers/specs/ (stripe-billing-design.md, y2k-design-overhaul.md, aura-redesign.md)
├── docs/superpowers/plans/ (y2k-design-overhaul.md, aura-redesign.md)
└── requirements.txt, Procfile, render.yaml, .env
```

## デザイン方針（Aura/Ethereal — セッション5で確定）

### コンセプト
- ターゲット: 20代女性、SNS映え、Instagramストーリーでシェアしたくなる
- トーン: Aura/Ethereal — すりガラス、光のグロー、パステルラベンダー、クリスタル
- 2層構造: ビジュアル重視のファーストビュー（ポスター風） → 「更に詳しく」で詳細アコーディオン
- 絵文字: UIでは🌙のみ許可、Claude生成テキストから絵文字排除

### ページ別デザイン
- **トップ**: マンダラ+🌙ヒーロー、Glass Cardメニュー
- **フォーム**: タロットカード（女教皇）SVG挿絵、明るい背景、キラキラ33個
- **ローディング**: マンダラ回転+8フェーズ進行表示
- **結果**: ファーストビュー（ポスター風）+ タブ切替 + アコーディオン詳細 + 月別グリッド
- **チャット**: Auraトーンのバブルデザイン

### DALL-E画像の扱い
- 背景として `opacity: 0.18` で配置（読みやすさ優先）
- シェア用ポスター: GPT Image APIで新規生成（html2canvasスクショではない）

## フォント体系（セッション5で確定）

| 用途 | フォント | Weight |
|------|----------|--------|
| 見出し | Rajdhani | 700 |
| 強調 | Inter | 800 |
| ラベル | JetBrains Mono | 600 |
| 本文 | Noto Sans JP | 500 |

## カラーパレット（セッション5で確定）

- 背景: #352466 〜 #4a3590（これ以上暗くしない）
- すりガラス: `rgba(255,255,255,0.08)` + `backdrop-filter: blur(16px)`
- テキスト: #F3EAFF（メイン）、#C4B5FD（サブ）
- アクセント: #E0B0FF（モーヴピンク）、#A78BFA（ラベンダー）、#A855F7（バイオレット）
- グロー: `box-shadow: 0 0 40px rgba(168,85,247,0.3)`
- キラキラ: ✦✧· 白い星のアニメーション（丸ドット禁止）
- 禁止色: オレンジ・暖色系・ゴールド(#FFD700)

## ユーザーのデザインフィードバック傾向

- **「暗い」に敏感** → 背景は#352466/#4a3590くらいが限界、グロー強めにする
- **「シンプルすぎ」に敏感** → キラキラ・挿絵・装飾は多めが好み
- **「読みにくい」** → line-height 2.4、改行多め、短文化
- **文章を読むのは好き** → 「更に詳しく」で長文を展開できる2層構造が◎
- **タロットカードのイラストが好き** → SVGで各所に配置
- **パステルラベンダー x クリスタルの参照画像**（ChatGPT生成ポスター）が品質基準
- **「画像にする」= GPT Image APIで新規ポスター生成**（html2canvasスクショではない）
- **ファイル作ったら自動で開け！** — 何度か怒られた。必ずopenすること
- **デザイン比較では差が大きくないとわからない**
- 「ちゃちい」「安っぽい」に敏感 → 丸ゴシック、絵文字多用、カーブの多い枠はNG
- オレンジ・暖色系を嫌う → ゴールド(#FFD700)もNG、ピンクはモーヴ系ならOK
- 実機（スマホ）確認を重視 → 必ずスマホでの見え方を確認すること

## 占術計算モジュール（Pythonで正確に計算）
- `rokusei.py`: 六星占術（運命星+陰陽+霊合星人+12年周期+大殺界判定）
- `shichusuimei.py`: 四柱推命（年柱の天干地支+五行+陰陽）
- `numerology.py`: 数秘術（ライフパスナンバー、マスターナンバー11/22/33保持）

## 検証済みの計算結果
- ゆうな(1995/6/26): 火星人マイナス(-), LP11/2(マスターナンバー), 2026年=健弱
- 彼(1999/5/7): LP4

## APIキー
- Anthropic: .env + Render環境変数に設定済み
- OpenAI: .env + Render環境変数に設定済み（DALL-E 3 + GPT Image API）
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

## モックアップファイル一覧（セッション5で作成）

| ファイル | 内容 |
|----------|------|
| `.superpowers/brainstorm/result-page-mockup.html` | 結果ページ（v1〜v7の最終版） |
| `.superpowers/brainstorm/top-page-mockup.html` | トップページ |
| `.superpowers/brainstorm/form-page-mockup.html` | フォームページ |
| `.superpowers/brainstorm/loading-chat-mockup.html` | ローディング+チャット |

## 設計書・実装計画への参照

- **設計書**: `docs/superpowers/specs/2026-05-10-aura-redesign.md`
- **実装計画**: `docs/superpowers/plans/2026-05-10-aura-redesign.md`（全9タスク）
- 旧Y2K設計書: `docs/superpowers/specs/2026-05-10-y2k-design-overhaul.md`（参考用）

## 未完了・次にやるべきこと

### 実装計画（9タスク — `docs/superpowers/plans/2026-05-10-aura-redesign.md` 参照）

推奨: subagent-driven-development で並列実行

1. **Task 1: CSS全面書き直し**（最優先、全ページの基盤）
   - `app/static/css/style.css` をAura/Etherealパレット・フォント・すりガラスで再構築
2. **Task 2: トップページテンプレート**
   - `app/templates/index.html` — マンダラ+🌙ヒーロー、Glass Cardメニュー
3. **Task 3: フォームページテンプレート**
   - `app/templates/reading_form.html` — タロットカードSVG、キラキラ33個
4. **Task 4: ローディングページテンプレート**
   - `app/templates/reading_generate.html` — マンダラ回転+8フェーズ
5. **Task 5: 結果ページテンプレート**
   - `app/templates/reading_result.html` — ポスター+タブ+アコーディオン+月別グリッド
6. **Task 6: チャットページテンプレート**
   - `app/templates/chat.html` — Auraトーンバブル
7. **Task 7: 相性フォームテンプレート**
   - `app/templates/compatibility_form.html` — Auraトーン適用
8. **Task 8: バックエンド修正**
   - `app/services/prompts.py` — Claude生成テキストから絵文字排除
   - GPT Image APIでシェア用ポスター生成エンドポイント追加
9. **Task 9: 統合テスト**
   - 全ページの表示確認、ストリーミング動作、ポスター生成

### インフラ
10. **Render Diskの手動追加** — /dataに1GBディスク追加が必要。やらないとデプロイのたびにDBが消える

### 決済関連
11. **決済の再導入** — 現在は一時的に外してFREE状態。Stripe/PayPal審査完了後に再導入
12. **有料化の切替手順**: reading.jsの送信先を `/api/payment/create-checkout` に戻す、価格表示を戻す

## 参照画像
`/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg` — ChatGPTで生成されたパステルラベンダー x クリスタルのスピリチュアル鑑定ポスター（品質基準）

## 関連ファイル
- 作業ログ1: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ開発.md`
- 作業ログ2: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ改善.md`
- 作業ログ3: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリ課金化.md`
- 作業ログ4: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリY2Kデザイン.md`
- 作業ログ5: `/Users/kousuke/Documents/readings/作業ログ_20260510_占いアプリAuraリデザイン.md`
- アクションプラン: `/Users/kousuke/Documents/action-plan-may15.html`
- 設計書(Aura): `/Users/kousuke/fortune-app/docs/superpowers/specs/2026-05-10-aura-redesign.md`
- 実装計画(Aura): `/Users/kousuke/fortune-app/docs/superpowers/plans/2026-05-10-aura-redesign.md`
- 旧設計書(Y2K): `/Users/kousuke/fortune-app/docs/superpowers/specs/2026-05-10-y2k-design-overhaul.md`
