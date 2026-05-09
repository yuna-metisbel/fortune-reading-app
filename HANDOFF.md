# セッション引き継ぎ — 占いリーディングWebアプリ

## プロジェクト概要
生年月日等から6つの占術体系（西洋占星術・数秘術・九星気学・六星占術・四柱推命・タロット）を統合した実用型リーディングを生成するWebアプリ。LINE風チャットで相談も可能。

## 所在地
- ローカル: `/Users/kousuke/fortune-app/`
- GitHub: `https://github.com/yuna-metisbel/fortune-reading-app` (private)
- 本番: `https://fortune-reading-app.onrender.com`
- Render: 有料プラン

## 技術スタック
FastAPI + Jinja2 + SQLite(aiosqlite) + Claude API(Sonnet) + DALL-E 3
Python 3.11 on Render

## ディレクトリ構成
```
fortune-app/
├── app/
│   ├── main.py, config.py, database.py, models.py
│   ├── routers/ (pages, profiles, readings, chat)
│   ├── services/ (claude_client, prompts, rokusei, shichusuimei, numerology, image_generator)
│   ├── templates/ (base, index, reading_form, compatibility_form, reading_result, chat, reading_generate)
│   └── static/ (css/style.css, js/reading.js, js/chat.js)
├── tests/ (conftest, test_models, test_profiles, test_readings, test_chat)
├── docs/superpowers/specs/ + plans/
└── requirements.txt, Procfile, render.yaml, .env
```

## 占術計算モジュール（全てPythonで正確に計算、Claudeに渡す）
- `rokusei.py`: 六星占術（運命星+陰陽+霊合星人+12年周期+大殺界判定）
- `shichusuimei.py`: 四柱推命（年柱の天干地支+五行+陰陽）
- `numerology.py`: 数秘術（ライフパスナンバー、マスターナンバー11/22/33保持）

## 検証済みの計算結果
- ゆうな(1995/6/26): 火星人マイナス(-), LP11/2(マスターナンバー), 2026年=健弱
- 彼(1999/5/7): LP4

## APIキー
- Anthropic: .env + Render環境変数に設定済み
- OpenAI: 新規アカウント、.env + Render環境変数に設定済み

## 直前のバグ修正
- Jinja2テンプレートエラー修正済み（loop.index in conditional for → slice）
- 結果ページが500エラーだったのを修正 → 要動作確認

## 未完了・次にやるべきこと
1. **結果ページの動作確認** — Jinja2エラー修正後の確認がまだ
2. **ポスターカードのデザイン品質** — 参照画像（HHpHDDyasAAy_E6.jpeg）に近づける。現在HTML/CSSで作っているが、参照画像レベルの美しさにはまだ遠い
3. **画像保存ボタンのテスト** — html2canvasでPNG保存が動くか確認
4. **SQLite永続化** — Render有料プランならDisk追加で永続化可能
5. **CSSの全体見直し** — 文字サイズ・余白・太字ハイライトの最終調整
6. **相性リーディングのテスト** — 自動入力が正しく動くか確認
7. **チャット機能のテスト** — リーディング後のチャット相談が動くか確認

## ユーザー（ゆうな）の要望の温度感
- デザインへのこだわりが強い（参照画像レベルを求める）
- 占術の正確性を重視（自分の結果を知っていて間違いを指摘してくる）
- 文章アレルギーの人への配慮（箇条書き・太字ポイント・キャッチコピー重視）
- 画像保存＆共有を重要視

## 参照画像
`/Users/kousuke/fortune-app/HHpHDDyasAAy_E6.jpeg` — パステルラベンダー×クリスタルのスピリチュアル鑑定ポスター。この画像レベルのポスターを結果ページの上部に表示したい。

## 関連ファイル
- 個人リーディング保存: `/Users/kousuke/Documents/readings/ゆうな_個人リーディング_20260507.md`
- 二人のリーディング保存: `/Users/kousuke/Documents/readings/ゆうな×彼_二人のリーディング_20260507.md`
- 作業ログ1: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ開発.md`
- 作業ログ2: `/Users/kousuke/Documents/readings/作業ログ_20260509_占いアプリ改善.md`
- 設計書: `/Users/kousuke/docs/superpowers/specs/2026-05-09-fortune-reading-app-design.md`
- 実装計画: `/Users/kousuke/docs/superpowers/plans/2026-05-09-fortune-reading-app.md`
