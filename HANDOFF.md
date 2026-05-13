# セッション引き継ぎ — 占いリーディングWebアプリ（セッション7後）

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。セッション7で改行・装飾ルールの最終実装、ポスター生成修正、相性リーディング専用レイアウト、各種UIバグ修正を完了。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (private)
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
│   └── static/ (css/style.css, js/reading.js, js/chat.js, images/posters/, images/tab-illustrations.css)
├── tests/
├── docs/superpowers/specs/
├── docs/superpowers/plans/
├── docs/reflections/ (2026-05-11.md, 2026-05-12.md)
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

## 改行ルール（セッション7で実装完了）

### 3つの関数（reading_result.html内のJS）

| 関数 | 使う場所 | `、` | `。` | `：` `／` ` — ` `）` |
|------|----------|------|------|------|
| `breakShort` | キャッチコピー、ハイライトカード、ラベルなしKP、ポスター要素 | **改行** | **改行(末尾削除)** | **改行** |
| `breakLabeled` | ラベル付きKP(ライフパス：等)の値部分 | そのまま | そのまま | **改行** |
| `breakBody` | 「更に詳しく」本文 | そのまま | **改行** | **改行** |

### 全関数共通
- `「」『』`は全関数の先頭で除去
- 文末の`、`や`。`は削除（breakShortのみ）

### 太字差別化ルール
- **単語**（助詞/副詞なし＆8文字以下）→ サイズ大 + 背景ハイライト（`kw-word`）
- **フレーズ**（助詞/副詞あり or 9文字以上）→ 下線 + テーマカラー（`kw-phrase`）
- 判定: `を|が|に|で|は|の|と|も|から|まで|して|ている|ない|やすい|すぎ|よう|く$|ながら|つつ|ずつ|たび|ほど|だけ|ばかり`

### Jinja側の処理
- Jinjaでは`「」`除去のみ（`| replace('「','') | replace('」','')`）
- `| replace('、','<br>')`等はしない（JSと競合するため）
- `| safe`も不要

## 画像生成

### 背景画像（DALL-E 3）
- リーディング生成時にバックグラウンドで自動生成
- テキストなし、背景のみ
- サイズ: 1024x1792、品質: hd
- HTMLのテキストがその上にオーバーレイ

### 保存ボタン（html2canvas）
- 「✦ 占いの結果を保存する」ボタン
- html2canvasでポスター部分をスクリーンショット→PNGダウンロード
- キャプチャ時にボタン・スクロールプロンプトを一時非表示

### GPT Image API（gpt-image-1）の注意
- URLではなくbase64（`b64_json`）で返す。`.url`はNone
- サポートサイズ: 1024x1024, 1024x1536, 1536x1024, auto のみ

## タロットカードSVG（5種）
- default（汎用）、priestess（女教皇）、star（星）、wands8（ワンドの8）、pentacles8（ペンタクルの8）、empress（女帝）
- `getTarotKey(name)`で名前からマッチング

## 相性リーディング専用レイアウト
- `is_compat`フラグで分岐（`reading.type == "compatibility"`）
- ポスター: ハイライトカード非表示、ベン図マンダラ、「COMPATIBILITY READING」ラベル
- 名前表示: `profile.nickname × profile_2.nickname`
- セクショングリッド: 1列（個人は2列）
- テーマカラー: 専用8色

## ユーザーのデザインフィードバック傾向

- 改行ルールに厳格。コンテキストごとに異なるルールを期待。一律適用は絶対NG
- 「ちゃちい」「安っぽい」に敏感 → 丸ゴシック、絵文字多用、カーブの多い枠はNG
- 太字だけでなく、サイズ差・下線・色変えなどメリハリを求める
- AskUserQuestionの選択肢UIは好まない → モックHTMLを見せて選んでもらう方が速い
- 「ファイル作ったら開け」を忘れると怒られる
- 実機（スマホ）確認を重視
- 「見せて」と言われたら `open` コマンドでブラウザに出す
- デザインの変更はまとめて実装してから見せること（途中で出すと混乱する）
- **現在は2026年5月**。年の間違いに厳しい
- ポスター画像生成は「背景のみ生成→HTMLで文字をオーバーレイ」。テキスト入りの画像生成はNG（文字化けする）
- プロンプト変更は元のものを基準に最小限の差分で。大幅書き換えは嫌がる

## 今回やったこと

### 改行・装飾ルール
- breakShort/breakLabeled/breakBodyの仕様照合→不足パターン追加（：、／）
- Jinja/JS競合解消（Jinjaはreplace削除、JSが統一処理）
- ポスター要素にformatPosterElements()追加
- 太字判定に副詞パターン追加
- 全break関数+renderMarkdownBodyで「」『』除去
- 「具体的にNつ」除去

### レイアウト・UI
- 「最後のメッセージ」タブ全幅→「今すぐやること」横並びに
- タブSVGイラスト大胆リデザイン（130px、占いモチーフ、高彩度）
- オーファン文字対策（text-wrap: balance）
- スタートページメニュータイトル15px+nowrap

### ポスター・画像
- gpt-image-1のbase64レスポンス対応
- 保存方式変更: DALL-E 3背景+html2canvasでスクショ保存
- 「占いの結果を保存する」ボタンに変更

### セクション名
- 「最後のメッセージ」→「魂のメッセージ」（プロンプト+表示）
- 「発信」除去

### 相性リーディング
- 専用レイアウト（1列、ハイライト非表示、ベン図、専用テーマカラー）
- profile_2のロード追加
- ポスター名を「名前 × 名前」表示に

### タロット
- ペンタクルの8、女帝のSVG追加

## 現在の状態

- **サーバー**: `localhost:8000`で動作中
- **本番**: Renderにデプロイ済み（最新コミット: fe5aa78以降）
- **結果ページ**: 改行・太字ルール実装完了、全関数で「」除去済み
- **相性リーディング**: 専用レイアウト実装済み
- **未コミット**: docs/reflections/2026-05-12.md、HANDOFF.md

## 未完了・次にやること

### 最優先: スマホ実機確認
1. **iPhone 15での全ページ目視確認** — 改行・オーファン・レイアウトずれ
2. **相性リーディング全セクション展開** — 1列グリッドの表示確認
3. **html2canvas保存テスト** — 実機でのスクショ品質・レイアウトずれ

### リーディング品質
4. **新規リーディング生成テスト** — 新プロンプト（2026年、九星気学先頭、絵文字排除、魂のメッセージ）の出力確認
5. **仕事・お金のタイトル確認** — 新規生成で「発信」が出ないか

### デザイン
6. **タブのアニメーション追加** — ユーザーが「もっと工夫」を求めていた

### インフラ
7. **Render Diskの手動追加** — /dataに1GBディスク（デプロイのたびにDBが消える）
8. **コミット** — docs/reflections + HANDOFF.md

### 決済
9. **決済の再導入** — Stripe/PayPal審査完了後に再導入

## 注意点・ハマりポイント

- **reading.jsのキャッシュ**: JSを変更したら`?v=N`をテンプレートのscriptタグで更新するか、Cmd+Shift+Rでハードリフレッシュ
- **改行ルールは文脈依存**: キャッチコピーと本文で`、`の扱いが真逆。一律適用は破綻する
- **Jinja replaceとJS textContentの競合**: Jinjaで`<br>`に変換すると、JSのtextContentで句読点が消える。Jinjaでは「」除去のみ
- **gpt-image-1はbase64で返す**: `.url`はNone。`b64_json`をデコードして保存。サイズは1024x1536まで
- **text-wrap: balanceが日本語オーファン対策に有効**: word-break: keep-allは日本語に効かない
- **相性リーディングのprofile_2**: selectinloadで明示的にロードしないとNone
- **section_themes配列のインデックス**: セクションをpopすると後続のテーマカラーがズレる。相性は専用テーマ配列を使用
- **bg-layerにpointer-events: none必須**: ないとスクロールやクリックが奪われる
- **ユーザーの年指定**: 現在は2026年5月。2025年のデータが出ると怒られる

## 参照ファイル
- 設計書(Aura): `docs/superpowers/specs/2026-05-10-aura-redesign.md`
- 実装計画(Aura): `docs/superpowers/plans/2026-05-10-aura-redesign.md`
- 反省ログ: `docs/reflections/2026-05-11.md`, `docs/reflections/2026-05-12.md`
- フォント比較モック: `.superpowers/brainstorm/font-comparison-aura.html`
- タブイラストCSS: `app/static/images/tab-illustrations.css`
- 参照画像: `/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg`

## 次回の開き方

```
handoff.mdを見て占いアプリの続きをして。
スマホ実機で全ページ確認。新規リーディング生成テスト。
```
