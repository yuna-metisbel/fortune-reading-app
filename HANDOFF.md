# セッション引き継ぎ — 占いリーディングWebアプリ（セッション6後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。セッション6でAura/Etherealデザインの実装が完了し、結果ページの改行・フォント・装飾の最終調整中。

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
│   └── static/ (css/style.css, js/reading.js, js/chat.js, images/posters/, images/tab-illustrations.css)
├── tests/
├── docs/superpowers/specs/
├── docs/superpowers/plans/
├── docs/reflections/2026-05-11.md
└── requirements.txt, Procfile, render.yaml, .env
```

## フォント体系（セッション6で確定）

| 用途 | フォント | 適用先 |
|------|----------|--------|
| 見出し・キャッチコピー | Zen Kaku Gothic New (A) | タイトル、セクションキャッチ、強調テキスト |
| タブ名・ボタン | Shippori Mincho (C) | セクションタブ名、「占いの結果を画像にする」「LINKをコピー」 |
| 「更に詳しく」中身 | Kaisei Decol (E) | read-more-content |
| 本文 | Noto Sans JP (G) | 一般テキスト、ラベル |
| ラベル（英字） | JetBrains Mono | PERSONALITY, SOUL READING 等 |

## カラーパレット

- 背景: #352466 〜 #4a3590
- テキスト: #F5F0FF（メイン）、#D8B4FE（サブ）
- アクセント: #E9D5FF（モーヴ）、#F0ABFC（ピンク）、#A78BFA（ラベンダー）
- 禁止色: オレンジ・暖色系・ゴールド(#FFD700)

## セクションテーマカラー（10色）

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
| 最後のメッセージ | message | #e9d5ff |

## 改行ルール（セッション6で設計、実装途中）

### 3つの関数に分離

| 関数 | 使う場所 | `、` | `。` | `：` `／` ` — ` `）` |
|------|----------|------|------|------|
| `breakShort` | キャッチコピー、ハイライトカード、ラベルなしKP | **改行** | **改行(末尾削除)** | **改行** |
| `breakLabeled` | ラベル付きKP(ライフパス：等)の値部分 | そのまま | そのまま | **改行** |
| `breakBody` | 「更に詳しく」本文 | そのまま | **改行** | **改行** |

### 文末ルール
- 文末の`、`や`。`は**削除**する（改行に変換しない）

### 太字差別化ルール
- **単語**（助詞なし＆8文字以下）→ サイズ大 + 背景ハイライト（`kw-word`）
- **フレーズ**（助詞あり or 9文字以上）→ 下線 + テーマカラー、サイズ変えない（`kw-phrase`）
- 助詞判定: `を|が|に|で|は|の|と|も|から|まで|して|ている|ない|やすい|すぎ|よう`

## ユーザーのデザインフィードバック傾向

- 改行ルールに厳格。コンテキストごとに異なるルールを期待。一律適用は絶対NG
- 「ちゃちい」「安っぽい」に敏感 → 丸ゴシック、絵文字多用、カーブの多い枠はNG
- 太字だけでなく、サイズ差・下線・色変えなどメリハリを求める
- 均等なグリッドは「ダサい」 → リズムのあるレイアウトが好み
- AskUserQuestionの選択肢UIは好まない → モックHTMLを見せて選んでもらう方が速い
- 「ファイル作ったら開け」を忘れると怒られる
- 実機（スマホ）確認を重視
- 「見せて」と言われたら `open` コマンドでブラウザに出す
- デザインの変更はまとめて実装してから見せること（途中で出すと混乱する）
- **現在は2026年5月**。年の間違いに厳しい

## 今回やったこと

### デザイン実装（Task 1-7完了）
- CSS全面書き直し（Aura/Etherealパレット、フォント、すりガラス、グローオーブ、スパークル）
- base.html（新フォント、bg-layer、glow-orb、28スパークル）
- 全テンプレート書き直し（top/form/compat/loading/result/chat/sample/payment_cancel）
- chat.js クラス名更新（bubble/bubble-label/typing）

### バックエンド（Task 8完了）
- prompts.py: 絵文字排除指示、2026年5月指定、九星気学を出力順1番目に、「仕事・お金」（発信削除）
- image_generator.py: GPT Image APIポスター生成関数追加
- readings.py: ポスター生成APIエンドポイント、セクションテーマカラー、月別データパース、「今年(2025)」セクション除外、「月別」タブ除外（グリッドに統合）、detail_body（重複除去済み本文）

### 結果ページ改善
- ポスタータイトル・カード・メッセージの「」削除
- ハイライト4カード
- メッセージのキラキラグロー演出
- 2列アコーディオングリッド
- 10色テーマカラー
- キャッチコピーの行サイズ調整
- キーポイントカードの`：`分離表示
- 「更に詳しく」重複除去（detail_bodyに変更）
- 月別3列グリッド（5月ハイライト、タップ展開）
- タロットカードSVGイラスト（女教皇・星・ワンドの8）+ ふわふわアニメ
- タブにパステルSVGイラスト背景
- 白シマー（shimmer）全削除
- 背景 `bg-layer` に `pointer-events: none` 追加

### フォント変更
- 見出し → Zen Kaku Gothic New
- タブ名・ボタン → Shippori Mincho
- 「更に詳しく」中身 → Kaisei Decol 太字
- 本文 → Noto Sans JP (font-weight: 500)

## 現在の状態

- **サーバー**: `localhost:8000` で動作中
- **結果ページ**: 改行・太字のJS処理は3関数に分離済み（breakShort/breakLabeled/breakBody）だが、**実際の表示がユーザーの期待通りか最終確認が必要**
- **既存データ**: reading/9 は旧プロンプト（2025年）で生成されたデータ。新プロンプトで再生成していない
- **未コミット**: 全変更がgit未コミット

## 未完了・次にやること

### 最優先: 結果ページの改行・装飾の最終調整
1. **改行ルールの表示確認** — breakShort/breakLabeled/breakBodyが正しく動いているか、reading/9を開いて全セクション目視確認
2. **新規リーディングで再テスト** — 新プロンプト（2026年、九星気学先頭、絵文字排除）でリーディングを生成し、出力を確認
3. **仕事・お金のタイトル** — 既存データは「仕事・お金・発信」のまま。新規生成で「仕事・お金」になるか確認

### デザイン調整
4. **タブのアニメーション追加** — fadeSlideUp + delay は入れたが、ユーザーが「もっと工夫」を求めていた
5. **スマホ実機確認** — 全ページをスマホで確認

### インフラ
6. **コミット＆プッシュ** — 全変更をまとめてコミット
7. **Render Diskの手動追加** — /dataに1GBディスク追加が必要（デプロイのたびにDBが消える）

### 決済
8. **決済の再導入** — 現在はFREE状態。Stripe/PayPal審査完了後に再導入

## 注意点・ハマりポイント

- **reading.jsのキャッシュ**: JSを変更したら `?v=N` をテンプレートのscriptタグで更新するか、Cmd+Shift+Rでハードリフレッシュ。ユーザーが変わってないと言ったらまずキャッシュを疑う
- **`_showStreamingView()`**: フォーム送信時のローディングUI。`.container` をquerySelectorで探す。テンプレートのクラス名を変えたらここも追従必須
- **改行ルールは文脈依存**: キャッチコピーと本文で`、`の扱いが真逆。一律適用は破綻する
- **太字の判定**: 助詞を含む→フレーズ→下線、含まない＆短い→単語→サイズ大。「相手の感情を先読みして」の「して」は助詞→フレーズ扱い
- **section_themes配列のインデックス**: セクションをpopすると後続のテーマカラーがズレる可能性あり。テーマ割り当ては `for i, section` のインデックスベース
- **bg-layerにpointer-events: none必須**: ないとスクロールやクリックが奪われる
- **ユーザーの年指定**: 現在は2026年5月。2025年のデータが出ると怒られる
- **AskUserQuestion**: このユーザーにはモック見せる方式の方が合う

## 参照ファイル
- 設計書(Aura): `docs/superpowers/specs/2026-05-10-aura-redesign.md`
- 実装計画(Aura): `docs/superpowers/plans/2026-05-10-aura-redesign.md`
- 反省ログ: `docs/reflections/2026-05-11.md`
- フォント比較モック: `.superpowers/brainstorm/font-comparison-aura.html`
- タブイラストCSS: `app/static/images/tab-illustrations.css`
- 参照画像: `/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg`

## 次回の開き方

```
handoff.mdを見て占いアプリの続きをして。
結果ページの改行と装飾の最終調整から。reading/9を開いてまず現状確認して。
```
