# Aura/Ethereal フルリデザイン 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 占いリーディングWebアプリの全ページをAura/Etherealトーンで統一リデザインし、GPT Imageポスター生成機能を追加する。

**Architecture:** 既存のFastAPI+Jinja2+vanilla JSアーキテクチャを維持。CSSを全面書き直し、全テンプレートをモックアップに合わせて更新。バックエンドにGPT Image API連携を追加。

**Tech Stack:** FastAPI, Jinja2, CSS3 (backdrop-filter, CSS animations), vanilla JS, OpenAI API (gpt-image-1), html2canvas

---

## ファイル構成

| ファイル | 変更種別 | 担当タスク |
|---------|---------|-----------|
| `app/static/css/style.css` | 全面書き直し | Task 1 |
| `app/templates/base.html` | 修正 | Task 2 |
| `app/templates/index.html` | 書き直し | Task 3 |
| `app/templates/reading_form.html` | 書き直し | Task 4 |
| `app/templates/compatibility_form.html` | 書き直し | Task 4 |
| `app/templates/reading_generate.html` | 書き直し | Task 5 |
| `app/templates/reading_result.html` | 全面書き直し | Task 6 |
| `app/static/js/reading.js` | 修正 | Task 6, 8 |
| `app/templates/chat.html` | 書き直し | Task 7 |
| `app/static/js/chat.js` | 軽微修正 | Task 7 |
| `app/templates/sample.html` | 書き直し | Task 7 |
| `app/services/prompts.py` | 修正 | Task 8 |
| `app/services/image_generator.py` | 関数追加 | Task 8 |
| `app/routers/readings.py` | エンドポイント追加 | Task 8 |

---

### Task 1: CSSデザインシステム全面書き直し

**Files:**
- Rewrite: `app/static/css/style.css`

**参照モックアップ:** `.superpowers/brainstorm/result-page-v6.html`, `form-page-mockup.html`, `top-page-mockup.html`, `loading-chat-mockup.html`

- [ ] **Step 1: 旧CSSをバックアップして新CSSの骨格を作成**

`app/static/css/style.css` を全面書き直し。以下のセクション構成で記述する:

```css
/* ============================================
   AURA/ETHEREAL DESIGN SYSTEM
   Fortune Reading App — 2026
   ============================================ */

/* --- Reset & Variables --- */
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  /* Colors */
  --bg-top: #352466;
  --bg-mid: #4a3590;
  --bg-bottom: #3a2a75;
  --glow-violet: #9333ea;
  --glow-soft: #a78bfa;
  --glow-pink: #c084fc;
  --card-bg: rgba(255,255,255,0.08);
  --card-border: rgba(216,180,254,0.22);
  --card-glow: rgba(167,139,250,0.18);
  --text-primary: #f5f0ff;
  --text-secondary: #d8b4fe;
  --accent-mauve: #e9d5ff;
  --accent-pink: #f0abfc;
  --highlight: #faf5ff;

  /* Fonts */
  --font-heading: 'Rajdhani', 'Noto Sans JP', sans-serif;
  --font-emphasis: 'Inter', 'Noto Sans JP', sans-serif;
  --font-label: 'JetBrains Mono', monospace;
  --font-body: 'Noto Sans JP', sans-serif;
}

body {
  font-family: var(--font-body);
  background: var(--bg-top);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}
```

- [ ] **Step 2: 背景・グローオーブ・スパークル・アニメーションを記述**

```css
/* --- Background --- */
.bg-layer {
  position: fixed; inset: 0; z-index: 0;
  background:
    radial-gradient(ellipse 140% 80% at 50% 0%, rgba(167,139,250,.55) 0%, transparent 50%),
    radial-gradient(ellipse 100% 60% at 85% 20%, rgba(216,180,254,.4) 0%, transparent 45%),
    radial-gradient(ellipse 90% 60% at 10% 55%, rgba(192,132,252,.35) 0%, transparent 45%),
    radial-gradient(ellipse 120% 60% at 50% 100%, rgba(233,213,255,.35) 0%, transparent 45%),
    radial-gradient(ellipse 60% 40% at 50% 50%, rgba(240,171,252,.15) 0%, transparent 50%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 40%, var(--bg-bottom) 100%);
}

/* --- Glow Orbs --- */
.glow-orb {
  position: fixed; border-radius: 50%;
  filter: blur(50px); z-index: 0;
  pointer-events: none;
  animation: orbFloat 8s ease-in-out infinite;
}
.glow-orb.a { width: 280px; height: 280px; background: rgba(167,139,250,.25); top: 8%; left: -5%; }
.glow-orb.b { width: 240px; height: 240px; background: rgba(216,180,254,.22); top: 40%; right: -8%; animation-delay: -3s; }
.glow-orb.c { width: 220px; height: 220px; background: rgba(233,213,255,.2); bottom: 12%; left: 8%; animation-delay: -5s; }
.glow-orb.d { width: 200px; height: 200px; background: rgba(240,171,252,.15); top: 65%; left: 45%; animation-delay: -7s; }

/* --- Sparkles --- */
.sparkle {
  position: fixed; z-index: 1; pointer-events: none;
  animation: twinkle var(--dur, 3s) ease-in-out infinite;
  animation-delay: var(--del, 0s);
}
.sparkle.star { color: rgba(255,255,255,.8); }
.sparkle.lavender { color: rgba(216,180,254,.7); }
.sparkle.pink { color: rgba(240,171,252,.6); }

/* --- Animations --- */
@keyframes orbFloat {
  0%, 100% { transform: translate(0,0) scale(1); opacity: .7; }
  33% { transform: translate(15px,-20px) scale(1.1); opacity: 1; }
  66% { transform: translate(-10px,10px) scale(.95); opacity: .8; }
}
@keyframes twinkle {
  0%, 100% { opacity: .1; transform: scale(.6); }
  50% { opacity: 1; transform: scale(1.4); }
}
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
@keyframes glowPulse {
  0%, 100% { text-shadow: 0 0 8px rgba(216,180,254,.2); }
  50% { text-shadow: 0 0 28px rgba(216,180,254,.7), 0 0 56px rgba(147,51,234,.3); }
}
@keyframes floatGlow {
  0%, 100% { filter: drop-shadow(0 0 6px rgba(240,171,252,.3)); transform: translateY(0); }
  50% { filter: drop-shadow(0 0 18px rgba(240,171,252,.6)); transform: translateY(-3px); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}
@keyframes slowSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { opacity: .5; }
  50% { opacity: 1; }
}
@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
```

- [ ] **Step 3: コンテナ・Glass Card・ボタン・ディバイダー等のコンポーネントを記述**

```css
/* --- Container --- */
.container {
  position: relative; z-index: 2;
  max-width: 440px; margin: 0 auto;
  padding: 0 20px 100px;
}

/* --- Glass Card --- */
.glass-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 28px 24px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
  transition: all .3s;
}
.glass-card:hover {
  border-color: rgba(216,180,254,.35);
  box-shadow: 0 0 20px var(--card-glow);
}
.glass-card::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.06) 45%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.06) 55%, transparent 60%);
  background-size: 200% 100%;
  animation: shimmer 6s ease-in-out infinite;
  pointer-events: none;
}

/* --- Frosted Title Card --- */
.title-glass {
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(216,180,254,.2);
  border-radius: 12px;
  padding: 32px 24px;
  position: relative;
  overflow: hidden;
}
.title-glass::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.06) 50%, transparent 60%);
  background-size: 200% 100%;
  animation: shimmer 6s ease-in-out infinite;
  pointer-events: none;
}

/* --- Buttons --- */
.btn-primary {
  display: inline-flex;
  align-items: center; gap: 8px;
  font-family: var(--font-heading);
  font-size: 16px; font-weight: 700;
  padding: 16px 36px;
  border-radius: 8px; border: none;
  background: linear-gradient(135deg, var(--glow-violet), var(--glow-pink));
  color: white; cursor: pointer;
  box-shadow: 0 4px 28px rgba(147,51,234,.35);
  transition: all .3s;
  text-decoration: none; letter-spacing: 2px;
}
.btn-primary:hover {
  box-shadow: 0 6px 36px rgba(147,51,234,.5);
  transform: translateY(-2px);
}
.btn-secondary {
  font-family: var(--font-label);
  font-size: 12px; font-weight: 600;
  letter-spacing: 2px;
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid var(--card-border);
  background: rgba(255,255,255,.06);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all .3s;
  backdrop-filter: blur(8px);
}
.btn-secondary:hover {
  background: rgba(255,255,255,.12);
  color: var(--highlight);
  box-shadow: 0 0 16px rgba(167,139,250,.2);
}

/* --- Divider --- */
.divider {
  display: flex; align-items: center; gap: 12px;
  margin: 48px auto; max-width: 240px;
}
.divider::before, .divider::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(216,180,254,.4), transparent);
}
.divider-stars {
  font-size: 10px; color: var(--text-secondary);
  letter-spacing: 6px;
  animation: twinkle 3s ease-in-out infinite;
}

/* --- Crystal Decoration --- */
.crystal {
  position: absolute;
  width: 0; height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 20px solid rgba(216,180,254,.1);
  filter: drop-shadow(0 0 8px rgba(216,180,254,.25));
  z-index: 0; pointer-events: none;
}
.crystal::after {
  content: '';
  position: absolute; top: 20px; left: -8px;
  width: 0; height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 12px solid rgba(216,180,254,.07);
}
```

- [ ] **Step 4: フォーム・タイポグラフィ・ラベル・ユーティリティを記述**

```css
/* --- Typography --- */
.heading-lg {
  font-family: var(--font-heading);
  font-weight: 700; font-size: 28px;
  line-height: 1.8; letter-spacing: 2px;
  color: var(--highlight);
}
.heading-md {
  font-family: var(--font-heading);
  font-weight: 700; font-size: 18px;
  letter-spacing: 1px; color: var(--highlight);
}
.label {
  font-family: var(--font-label);
  font-size: 11px; font-weight: 600;
  letter-spacing: 4px; text-transform: uppercase;
  color: var(--text-secondary);
}
.label-sm {
  font-family: var(--font-label);
  font-size: 9px; font-weight: 700;
  letter-spacing: 3px; text-transform: uppercase;
  color: var(--accent-pink);
}
.body-text {
  font-family: var(--font-body);
  font-size: 14px; font-weight: 500;
  line-height: 2.4; letter-spacing: .5px;
}

/* --- Form --- */
.form-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 32px 24px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  position: relative; overflow: hidden;
  margin-bottom: 20px;
}
.form-card::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.05) 50%, transparent 60%);
  background-size: 200% 100%;
  animation: shimmer 8s ease-in-out infinite;
  pointer-events: none;
}
.form-section-title {
  font-family: var(--font-label);
  font-size: 9px; font-weight: 700;
  letter-spacing: 3px; text-transform: uppercase;
  color: var(--accent-pink);
  margin-bottom: 24px;
}
.input-group { margin-bottom: 20px; }
.input-label {
  display: block;
  font-family: var(--font-emphasis);
  font-size: 12px; font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.input-label .optional {
  font-family: var(--font-label);
  font-size: 9px; font-weight: 500;
  color: rgba(216,180,254,.4);
  margin-left: 6px; letter-spacing: 1px;
}
.text-input, .select-input {
  width: 100%; padding: 12px 16px;
  font-family: var(--font-body);
  font-size: 14px; font-weight: 500;
  color: var(--text-primary);
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(216,180,254,.15);
  border-radius: 8px; outline: none;
  transition: all .3s;
}
.text-input:focus, .select-input:focus {
  border-color: rgba(240,171,252,.4);
  box-shadow: 0 0 12px rgba(240,171,252,.1);
}
.text-input::placeholder { color: rgba(216,180,254,.3); font-weight: 400; }
.select-input { appearance: none; cursor: pointer; }
.select-input option { background: #2e1f6a; color: var(--text-primary); }
.textarea-input {
  width: 100%; min-height: 100px;
  padding: 14px 16px;
  font-family: var(--font-body);
  font-size: 14px; font-weight: 500;
  color: var(--text-primary);
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(216,180,254,.15);
  border-radius: 8px; outline: none;
  resize: vertical; transition: all .3s;
  line-height: 2;
}
.textarea-input:focus {
  border-color: rgba(240,171,252,.4);
  box-shadow: 0 0 12px rgba(240,171,252,.1);
}
.textarea-input::placeholder { color: rgba(216,180,254,.3); }
.date-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }

/* --- Footer --- */
.footer {
  margin-top: 80px; text-align: center; padding-bottom: 48px;
}
.footer-text {
  font-family: var(--font-label);
  font-size: 9px; font-weight: 500;
  letter-spacing: 4px;
  color: rgba(216,180,254,.3);
}
```

- [ ] **Step 5: トップページ固有スタイルを記述**

モックアップ `top-page-mockup.html` のヒーロー・メニューカード・最近の鑑定セクションのCSS。

- [ ] **Step 6: 結果ページ固有スタイルを記述**

モックアップ `result-page-v6.html` のポスター・ハイライトカード・アコーディオン・更に詳しく・月別グリッドのCSS。

- [ ] **Step 7: チャット・ローディング・サンプル固有スタイルを記述**

モックアップ `loading-chat-mockup.html` のローディング・チャット固有CSS。

- [ ] **Step 8: ブラウザでモックアップと見比べて確認**

Run: `cd /Users/kousuke/fortune-app && python -m uvicorn app.main:app --reload --port 8000`

全ページを開いてモックアップと比較。差異があれば修正。

- [ ] **Step 9: コミット**

```bash
git add app/static/css/style.css
git commit -m "feat: rewrite CSS with Aura/Ethereal design system

Complete replacement of Y2K design with new palette, typography
(Rajdhani/Inter/JetBrains Mono), glass cards, sparkle animations,
glow orbs, and shimmer effects."
```

---

### Task 2: base.html — フォント・背景・スパークル

**Files:**
- Modify: `app/templates/base.html`

- [ ] **Step 1: Google Fontsリンクを差し替え**

旧フォント（Zen Maru Gothic, Shippori Mincho, Quicksand, Noto Sans JP）を新フォントに:

```html
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
```

- [ ] **Step 2: body構造を書き換え**

旧: `.app-container` > `.sparkles` + content
新: `.bg-layer` + `.glow-orb`×4 + `.sparkle`(JS生成) + `.container` > content

```html
<body>
    <div class="bg-layer"></div>
    <div class="glow-orb a"></div>
    <div class="glow-orb b"></div>
    <div class="glow-orb c"></div>
    <div class="glow-orb d"></div>
    <script>
    (function(){
      var sp=[{chars:['✦','✧'],cls:'star',n:14},{chars:['✦','·'],cls:'lavender',n:8},{chars:['✧','·'],cls:'pink',n:6}];
      sp.forEach(function(g){
        for(var i=0;i<g.n;i++){
          var s=document.createElement('div');
          s.className='sparkle '+g.cls;
          s.textContent=g.chars[i%g.chars.length];
          s.style.left=Math.random()*100+'%';
          s.style.top=Math.random()*100+'%';
          s.style.setProperty('--dur',(2+Math.random()*5)+'s');
          s.style.setProperty('--del',(Math.random()*6)+'s');
          s.style.fontSize=(7+Math.random()*9)+'px';
          document.body.appendChild(s);
        }
      });
    })();
    </script>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
```

- [ ] **Step 3: OGPメタタグを維持しつつtitleを確認**

既存のog:site_name、og:type、twitter:cardは維持。

- [ ] **Step 4: コミット**

```bash
git add app/templates/base.html
git commit -m "feat: update base template with new fonts and sparkle system

Replace Y2K fonts with Rajdhani/Inter/JetBrains Mono/Noto Sans JP.
New background layer, glow orbs, and 28-sparkle system (white/lavender/pink)."
```

---

### Task 3: トップページ (index.html)

**Files:**
- Rewrite: `app/templates/index.html`

**参照:** `.superpowers/brainstorm/top-page-mockup.html`

- [ ] **Step 1: ヒーロー・メニュー・最近の鑑定を書き直し**

旧デザイン（クリスタルオーブ+4層リング）を削除。新デザイン（マンダラSVG+🌙+メニューカード）に置換。

テンプレート変数（`readings`リスト）は既存ロジックを維持。メニューカードのリンク先（`/reading/personal`, `/reading/compatibility`, `/sample`）も維持。

マンダラSVGは `top-page-mockup.html` の `.hero-mandala` SVGをそのまま使用。

- [ ] **Step 2: ブラウザで確認**

Run: ブラウザで `http://localhost:8000` を開き、モックアップと比較。

- [ ] **Step 3: コミット**

```bash
git add app/templates/index.html
git commit -m "feat: redesign top page with mandala hero and glass menu cards"
```

---

### Task 4: フォームページ (reading_form.html, compatibility_form.html)

**Files:**
- Rewrite: `app/templates/reading_form.html`
- Rewrite: `app/templates/compatibility_form.html`

**参照:** `.superpowers/brainstorm/form-page-mockup.html`

- [ ] **Step 1: reading_form.htmlを書き直し**

旧フォームレイアウトを新デザインに:
- ←戻る + タイトル + サブテキスト
- タロットカード挿絵SVG（女教皇）— `form-page-mockup.html` のSVGを使用
- Glass Cardでフォームセクション分け（SAVED PROFILE / BASIC INFO / READING THEME）
- フォームの`name`属性と既存のJSバインディング（`initPersonalForm`, `initSavedProfileHandlers`）を維持
- 生年月日の3分割入力、出生時刻テキスト入力を維持

- [ ] **Step 2: compatibility_form.htmlを書き直し**

同じデザインシステムで2人分のフォームを配置。
- Person 1 / Person 2 をそれぞれGlass Cardセクションに
- 関係性セクション（relationship_type, met_date, theme）もGlass Card
- 既存のJSバインディング（`initCompatibilityForm`, `autoFillLatestProfile`）を維持

- [ ] **Step 3: ブラウザで両フォームを確認、送信テスト**

個人リーディングフォームと相性フォームの両方を開いて:
- 保存済みプロフィール選択が動くか
- フォーム送信が正常に動くか（ストリーミング開始するか）

- [ ] **Step 4: コミット**

```bash
git add app/templates/reading_form.html app/templates/compatibility_form.html
git commit -m "feat: redesign form pages with tarot illustration and glass cards"
```

---

### Task 5: ローディングページ (reading_generate.html)

**Files:**
- Rewrite: `app/templates/reading_generate.html`

**参照:** `.superpowers/brainstorm/loading-chat-mockup.html` (LOADING tab)

- [ ] **Step 1: ローディングUIを書き直し**

旧デザイン（🔮パルス）を新デザインに:
- マンダラSVG回転（slowSpin 8s）+ 🌙中央
- 「星の配置を読み解いています」タイトル
- 8フェーズ進行表示（.phase要素のリスト）
- ストリーミングエリア（非表示、aria-live）
- 完了後のアクションボタン

既存JSの`readingId`変数と`handleStream()`呼び出しは維持。

`reading.js` の `_showStreamingView()` がフェーズ表示を更新するので、フェーズのDOM IDを合わせる。

- [ ] **Step 2: reading.jsのフェーズアニメーションを新UIに合わせて調整**

`_showStreamingView()` 内のフェーズ更新ロジックを新しい `.phase` クラス構造に合わせる:
- `.phase.active` でピンクドットpulse
- `.phase.done` で薄い色

- [ ] **Step 3: ブラウザでリーディング生成を実行して確認**

実際にフォームからリーディングを送信し、ローディング画面のフェーズ進行とストリーミングを確認。

- [ ] **Step 4: コミット**

```bash
git add app/templates/reading_generate.html app/static/js/reading.js
git commit -m "feat: redesign loading page with mandala spinner and phase indicators"
```

---

### Task 6: 結果ページ (reading_result.html) ★最重要

**Files:**
- Rewrite: `app/templates/reading_result.html`
- Modify: `app/static/js/reading.js` — ポスター関連JS追加

**参照:** `.superpowers/brainstorm/result-page-v6.html`

- [ ] **Step 1: ファーストビュー（ポスター部分）を書き直し**

旧: DALL-E背景フルスクリーン + HTMLテキストオーバーレイ（破綻している）
新: 以下の構造

```html
<div class="poster" id="poster-capture">
    <div class="poster-dalle" style="background-image:url('{{ reading.image_url or '' }}')"></div>
    <!-- Crystal decorations -->
    <div class="poster-content">
        <div class="label" style="animation:glowPulse 4s ease-in-out infinite">SOUL READING</div>
        <div class="poster-meta">
            <div class="poster-name">{{ profile.nickname | upper }}</div>
            <div class="poster-date">{{ profile.birth_date }}</div>
        </div>
        <!-- Mandala SVG -->
        <!-- Frosted glass title card with catch_copy -->
        <!-- Tarot crystal divider SVG -->
        <!-- 4 highlight cards (PERSONALITY/STRENGTH/LOVE/CAREER) -->
        <!-- Message box -->
        <button class="save-image-btn" onclick="generatePoster('{{ reading.id }}')">✦ 占いの結果を画像にする</button>
        <button class="share-link" onclick="copyLink()">LINK をコピー</button>
        <div class="scroll-prompt">...</div>
    </div>
</div>
```

テンプレート変数: 既存の `reading`, `profile`, `sections` を使用。`sections` はreading内容をパースした辞書。

- [ ] **Step 2: 詳細セクション（アコーディオン + 更に詳しく）を実装**

6セクションのアコーディオン。各セクションに:
- パステルSVGアイコン（セクション別）
- タロット風SVG挿絵
- 要約テキスト（`section.key_points` から）
- 「✧ 更に詳しく」で全文展開（`section.body` から）

```html
{% for section in sections %}
<div class="reading-section">
    <button class="section-trigger" onclick="toggleSection(this)">
        <div class="section-icon-wrap" style="background:...">
            <!-- Section-specific SVG icon -->
        </div>
        <span class="section-title">{{ section.title }}</span>
        <span class="section-arrow">▾</span>
    </button>
    <div class="section-body">
        <div class="section-illust"><!-- Section SVG --></div>
        <div class="section-content">
            {{ section.key_points | safe }}
            <button class="read-more-toggle" onclick="toggleMore(this)">✧ 更に詳しく</button>
            <div class="read-more-body">
                <div class="read-more-content">{{ section.body | safe }}</div>
            </div>
        </div>
    </div>
</div>
{% endfor %}
```

- [ ] **Step 3: 月別の流れグリッドを実装**

12ヶ月の3列グリッド。各月クリックで展開。
月別データは `sections` の「月別」セクションからパース、またはClaude出力から抽出。

```html
<div class="month-grid">
    {% for month in monthly_data %}
    <div class="month-card {% if month.is_current %}current{% endif %}" onclick="toggleMonth(this)">
        <div class="month-num">{{ month.label }}</div>
        <div class="month-keyword">{{ month.keyword }}</div>
        <div class="month-star">{{ month.stars }}</div>
        <div class="month-detail">
            <div class="month-detail-content">{{ month.detail }}</div>
        </div>
    </div>
    {% endfor %}
</div>
```

- [ ] **Step 4: JavaScript関数を追加**

`reading_result.html` のインラインJSに以下を追加:

```javascript
function toggleSection(el) {
  el.closest('.reading-section').classList.toggle('open');
}
function toggleMore(btn) {
  var body = btn.nextElementSibling;
  body.classList.toggle('open');
  btn.textContent = body.classList.contains('open') ? '✧ 閉じる' : '✧ 更に詳しく';
}
function toggleMonth(el) {
  var wasExpanded = el.classList.contains('expanded');
  document.querySelectorAll('.month-card.expanded').forEach(function(c) { c.classList.remove('expanded'); });
  if (!wasExpanded) el.classList.add('expanded');
}
function copyLink() {
  navigator.clipboard.writeText(location.href);
  showToast('✧ リンクをコピーしました');
}
function showToast(msg) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() { t.classList.remove('show'); }, 2500);
}
```

- [ ] **Step 5: ポスター生成のフロントエンド呼び出しを追加**

```javascript
function generatePoster(readingId) {
  var btn = document.querySelector('.save-image-btn');
  btn.classList.add('saving');
  btn.textContent = '✦ ポスター生成中...';

  fetch('/api/readings/' + readingId + '/generate-poster', { method: 'POST' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.image_url) {
        var a = document.createElement('a');
        a.href = data.image_url;
        a.download = 'fortune-reading-poster.png';
        a.click();
        showToast('✧ ポスター画像を保存しました');
      }
      btn.classList.remove('saving');
      btn.textContent = '✦ 占いの結果を画像にする';
    })
    .catch(function() {
      btn.classList.remove('saving');
      btn.textContent = '✦ 占いの結果を画像にする';
      showToast('生成に失敗しました');
    });
}
```

- [ ] **Step 6: readings.pyのセクションパース処理を更新**

既存の `GET /reading/{reading_id}` ルートが `sections` を構築する部分で、月別データを別途パースしてテンプレートに渡す。`monthly_data` として12ヶ月分のデータをテンプレートコンテキストに追加。

- [ ] **Step 7: ブラウザで結果ページを確認**

既存のリーディング結果を開いて:
- ファーストビューのポスター表示
- アコーディオン開閉
- 「更に詳しく」展開
- 月別カードのクリック展開
- リンクコピー

- [ ] **Step 8: コミット**

```bash
git add app/templates/reading_result.html app/static/js/reading.js app/routers/readings.py
git commit -m "feat: complete result page redesign with poster, accordions, monthly grid

Frosted glass title, tarot illustrations, two-layer detail expansion,
clickable monthly cards, and GPT Image poster generation button."
```

---

### Task 7: チャット・サンプルページ

**Files:**
- Rewrite: `app/templates/chat.html`
- Rewrite: `app/templates/sample.html`
- Minor: `app/static/js/chat.js` — CSSクラス名の更新のみ

**参照:** `.superpowers/brainstorm/loading-chat-mockup.html` (CHAT tab)

- [ ] **Step 1: chat.htmlを書き直し**

旧デザインを新Auraトーンに。構造:
- 固定ヘッダー（←戻る + 🌙 + タイトル + SOUL READINGラベル）
- スクロールメッセージエリア
- ウェルカムメッセージ（✦アイコン + 案内テキスト）
- バブル: ユーザー（gradient purple, 右寄せ）、アシスタント（Glass Card, 左寄せ, 「✦ 鑑定師」ラベル）
- タイピングインジケーター
- 固定入力エリア（textarea + 送信ボタン）

`chat.js` の `createBubble()` が参照するCSSクラスを合わせる。

- [ ] **Step 2: chat.jsのCSSクラス名を更新**

`createBubble()` 内のクラス名を新デザインのクラスに合わせる。ロジックは変更なし。

- [ ] **Step 3: sample.htmlを書き直し**

結果ページと同じレイアウトだが、静的コンテンツ。
- 「これはサンプル鑑定です」ラベル
- 同じポスター構造（マンダラ、すりガラスタイトル、4カード、メッセージ）
- CTAは「自分の鑑定をする」→リーディングフォームへ

- [ ] **Step 4: ブラウザでチャットとサンプルを確認**

- チャットページ: メッセージ送信、ストリーミング受信、バブル表示
- サンプルページ: 静的コンテンツの表示

- [ ] **Step 5: コミット**

```bash
git add app/templates/chat.html app/templates/sample.html app/static/js/chat.js
git commit -m "feat: redesign chat and sample pages with Aura theme"
```

---

### Task 8: バックエンド — プロンプト修正 + GPT Imageポスター生成API

**Files:**
- Modify: `app/services/prompts.py`
- Modify: `app/services/image_generator.py`
- Modify: `app/routers/readings.py`

- [ ] **Step 1: prompts.pyに絵文字排除指示を追加**

`SYSTEM_PROMPT_PERSONAL` と `SYSTEM_PROMPT_COMPATIBILITY` の冒頭に追加:

```python
# prompts.py の各システムプロンプトに以下を追加
"""
【重要な表記ルール】
- 絵文字を一切使用しないでください
- 装飾記号は ✦ と ✧ のみ使用可能です
- セクション見出しに絵文字を含めないでください
"""
```

- [ ] **Step 2: image_generator.pyにGPT Imageポスター生成関数を追加**

```python
async def generate_poster_image(
    nickname: str,
    birth_date: str,
    catch_copy: str,
    personality: str,
    strength: str,
    love: str,
    career: str,
    yearly_theme: str,
    message: str,
) -> str | None:
    """GPT Image APIで鑑定ポスター画像を生成する"""
    prompt = f"""パステルラベンダー × クリスタルのスピリチュアル鑑定
淡いラベンダー、パステルパープル、シルバー、白を基調にした、
幻想的で透明感のあるスピリチュアル鑑定ポスター。

全体は柔らかい雲、月、星、クリスタル、光の粒、繊細な装飾フレームで構成し、
女性向けの優しく神秘的な雰囲気にする。

タイトル: 「{catch_copy}」
名前: {nickname}
生年月日: {birth_date}

セクション配置:
- 魂のテーマ: {catch_copy}
- 性格: {personality}
- 強み: {strength}
- 恋愛傾向: {love}
- 仕事の方向: {career}
- 今年のテーマ: {yearly_theme}
- あなたへのメッセージ: {message}

装飾にはムーンストーン、アメジスト、ローズクォーツ、蝶、月のモチーフ、
吊り下げオーナメント、花、光のエフェクトを使用する。

日本語テキストで、優雅で可愛く、柔らかい読みやすいレイアウトの
1枚完結の鑑定シートにしてください。"""

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1792",
            quality="high",
            n=1,
        )

        image_url = response.data[0].url
        # Download and save locally
        import httpx, uuid
        async with httpx.AsyncClient() as http:
            img_resp = await http.get(image_url)
            if img_resp.status_code == 200:
                filename = f"poster_{uuid.uuid4().hex[:12]}.png"
                save_dir = Path(__file__).parent.parent / "static" / "images" / "posters"
                save_dir.mkdir(parents=True, exist_ok=True)
                save_path = save_dir / filename
                save_path.write_bytes(img_resp.content)
                return f"/static/images/posters/{filename}"
    except Exception as e:
        print(f"Poster generation failed: {e}")
    return None
```

- [ ] **Step 3: readings.pyにポスター生成APIエンドポイントを追加**

```python
@router.post("/api/readings/{reading_id}/generate-poster")
async def generate_poster(reading_id: int, db: AsyncSession = Depends(get_db)):
    reading = await db.get(Reading, reading_id)
    if not reading:
        return JSONResponse({"error": "Reading not found"}, status_code=404)

    # Parse sections from reading.content
    sections = _parse_sections(reading.content)

    profile = await db.get(Profile, reading.profile_id)
    nickname = profile.nickname if profile else "あなた"
    birth_date = str(profile.birth_date) if profile else ""

    image_url = await generate_poster_image(
        nickname=nickname,
        birth_date=birth_date,
        catch_copy=sections.get("全体要約", {}).get("catchcopy", ""),
        personality=sections.get("性格", {}).get("catchcopy", ""),
        strength=sections.get("才能", {}).get("catchcopy", ""),
        love=sections.get("恋愛", {}).get("catchcopy", ""),
        career=sections.get("仕事", {}).get("catchcopy", ""),
        yearly_theme=sections.get("今年のテーマ", {}).get("catchcopy", ""),
        message=sections.get("最後のメッセージ", {}).get("body", ""),
    )

    if image_url:
        return {"image_url": image_url}
    return JSONResponse({"error": "Generation failed"}, status_code=500)
```

- [ ] **Step 4: ポスター生成をテスト**

既存のリーディング結果ページで「占いの結果を画像にする」ボタンを押して:
- API呼び出しが成功するか
- 画像がダウンロードされるか
- 画像の内容がプロンプト通りか

- [ ] **Step 5: コミット**

```bash
git add app/services/prompts.py app/services/image_generator.py app/routers/readings.py
git commit -m "feat: add emoji removal to prompts and GPT Image poster generation API

Remove emojis from Claude output, add POST /api/readings/{id}/generate-poster
endpoint using gpt-image-1 for Instagram-ready poster generation."
```

---

### Task 9: 統合テスト・最終調整

**Files:**
- All modified files

- [ ] **Step 1: 全フローをE2Eで通しテスト**

1. トップページ → 魂のリーディング → フォーム入力 → 送信
2. ローディング画面（フェーズ進行確認）
3. 結果ページ（ポスター表示、アコーディオン、月別、更に詳しく）
4. 「占いの結果を画像にする」→ ポスター画像ダウンロード
5. 「鑑定師に相談する」→ チャットページ
6. チャットでメッセージ送受信
7. サンプルページ表示
8. 相性リーディングフォーム → 送信 → 結果

- [ ] **Step 2: スマホサイズで表示確認**

Chrome DevToolsでiPhone SE/14サイズにして全ページ確認。

- [ ] **Step 3: 微調整・修正があればコミット**

```bash
git add -A
git commit -m "fix: final adjustments from integration testing"
```

- [ ] **Step 4: 全変更をpush**

```bash
git push origin main
```
