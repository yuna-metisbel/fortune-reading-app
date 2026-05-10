# Y2K Design Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 占いアプリのデザインをY2K Glow-Up + DALL-E背景 + HTMLオーバーレイのポスター構造にリニューアルし、SNSシェア導線を追加する。

**Architecture:** DALL-E 3でテキストなしの装飾背景画像を鑑定ごとに生成し、HTML/CSSでテキストをオーバーレイする2層構造。鑑定ストリーミング中にDALL-E生成を並行実行。html2canvasでポスター画像保存、OGPメタタグでURLシェア。

**Tech Stack:** FastAPI, Jinja2, DALL-E 3 API, html2canvas, CSS (Y2K design system)

**Reference:** `mockup-overlay.html`（承認済みデザイン）, `docs/superpowers/specs/2026-05-10-y2k-design-overhaul.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `app/static/css/style.css` | Rewrite | Y2Kデザインシステム全体 |
| `app/templates/base.html` | Modify | フォント変更、sparkles変更、OGPブロック追加 |
| `app/templates/index.html` | Modify | Y2Kトップページ |
| `app/templates/reading_result.html` | Rewrite | DALL-E背景+オーバーレイポスター+シェア+アコーディオン |
| `app/templates/reading_form.html` | Modify | デフォルト値クリア、Y2Kデザイン適用 |
| `app/templates/reading_generate.html` | Modify | Y2Kデザイン適用 |
| `app/services/image_generator.py` | Modify | テキストなしプロンプト（済）、画像ローカル保存追加 |
| `app/routers/readings.py` | Modify | 並行DALL-E生成、OGPメタ情報 |
| `app/static/js/reading.js` | Modify | ポスター画像保存、リンクコピー機能 |

---

### Task 1: Y2Kデザインシステム — CSS変数とベースリセット

**Files:**
- Rewrite: `app/static/css/style.css` (lines 1-32)
- Modify: `app/templates/base.html` (lines 7-8, フォント変更)

- [ ] **Step 1: base.htmlのフォントリンクを変更**

```html
<!-- 変更前 (line 8) -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500&family=Noto+Serif+JP:wght@400;500;700&display=swap" rel="stylesheet">

<!-- 変更後 -->
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: style.cssのCSS変数とベースリセットを書き換え**

CSS変数セクション (lines 1-32) を以下に置換:

```css
/* ============================================================
   星図リーディング — Y2K Glow-Up Design System
   ============================================================ */

:root {
  --main:         #B388FF;
  --main-vivid:   #9C5CFF;
  --accent:       #FF80AB;
  --glow:         #D946EF;
  --text:         #3D2463;
  --text-light:   #7C5DAF;
  --white:        #FFFFFF;
  --glass-bg:     rgba(255, 255, 255, 0.55);
  --glass-bg-strong: rgba(255, 255, 255, 0.72);
  --glass-border: rgba(179, 136, 255, 0.3);

  --shadow-soft:  0 4px 24px rgba(179, 136, 255, 0.12);
  --shadow-card:  0 8px 32px rgba(179, 136, 255, 0.15);
  --shadow-glow:  0 0 20px rgba(179, 136, 255, 0.25);

  --radius-sm:    8px;
  --radius-md:    16px;
  --radius-lg:    24px;
  --radius-xl:    32px;

  --font-heading: 'Zen Maru Gothic', 'Noto Sans JP', sans-serif;
  --font-body:    'Noto Sans JP', sans-serif;
  --font-accent:  'Quicksand', sans-serif;

  --transition:   0.25s ease;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-body);
  font-weight: 300;
  font-size: 15px;
  line-height: 1.8;
  color: var(--text);
  background: linear-gradient(135deg, #DDD6FE 0%, #E9D5FF 25%, #F0ABFC33 50%, #E9D5FF 75%, #DDD6FE 100%);
  background-size: 400% 400%;
  animation: bg-shift 12s ease-in-out infinite;
  background-attachment: fixed;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

@keyframes bg-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

a {
  color: var(--main-vivid);
  text-decoration: none;
  transition: color var(--transition);
}
a:hover { color: var(--accent); }

img, svg { max-width: 100%; height: auto; }
```

- [ ] **Step 3: ブラウザで確認**

Run: `cd /Users/kousuke/fortune-app && python3 -m uvicorn app.main:app --reload --port 8000`

トップページにアクセスして背景グラデーションとフォントが変わっていることを確認。

- [ ] **Step 4: コミット**

```bash
git add app/static/css/style.css app/templates/base.html
git commit -m "feat: replace design system with Y2K palette and fonts"
```

---

### Task 2: Sparkles — 星の瞬きアニメーション

**Files:**
- Modify: `app/static/css/style.css` (sparklesセクション, lines 88-130)
- Modify: `app/templates/base.html` (line 14, sparkles div)

- [ ] **Step 1: style.cssのsparklesセクションを置換**

既存の `.sparkles` 〜 `@keyframes sparkle-drift` (lines 88-130) を以下に置換:

```css
/* ── Star Twinkle Background ── */
.sparkles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.sparkle-star {
  position: absolute;
  color: rgba(179, 136, 255, 0.6);
  font-size: 12px;
  animation: twinkle ease-in-out infinite;
  pointer-events: none;
}

@keyframes twinkle {
  0%, 100% { opacity: 0; transform: scale(0.5) rotate(0deg); }
  50% { opacity: 1; transform: scale(1) rotate(20deg); }
}
```

- [ ] **Step 2: base.htmlのsparkles divをJS生成に変更**

既存の `<div class="sparkles" aria-hidden="true"></div>` (line 14) の後にscriptを追加:

```html
<div class="sparkles" id="sparkles" aria-hidden="true"></div>
<script>
(function() {
  var c = document.getElementById('sparkles');
  var chars = ['✦', '✧', '·'];
  var colors = [
    'rgba(179,136,255,0.55)', 'rgba(244,114,182,0.45)',
    'rgba(217,70,239,0.4)', 'rgba(196,181,253,0.5)'
  ];
  for (var i = 0; i < 18; i++) {
    var s = document.createElement('span');
    s.className = 'sparkle-star';
    s.textContent = chars[Math.floor(Math.random() * chars.length)];
    s.style.left = Math.random() * 100 + '%';
    s.style.top = Math.random() * 100 + '%';
    s.style.color = colors[Math.floor(Math.random() * colors.length)];
    s.style.fontSize = (Math.random() * 10 + 8) + 'px';
    s.style.animationDuration = (Math.random() * 4 + 3) + 's';
    s.style.animationDelay = (Math.random() * 6) + 's';
    c.appendChild(s);
  }
})();
</script>
```

- [ ] **Step 3: ブラウザで確認**

リロードして星が静かに瞬いていることを確認。丸ドットが残っていないことを確認。

- [ ] **Step 4: コミット**

```bash
git add app/static/css/style.css app/templates/base.html
git commit -m "feat: replace sparkle dots with twinkling star characters"
```

---

### Task 3: グラデーションボーダーカード + ボタン + フォーム

**Files:**
- Modify: `app/static/css/style.css` (glass-card, buttons, form セクション)

- [ ] **Step 1: glass-cardをglow-cardに置換**

既存の `.glass-card` セクション (lines 133-148) を以下に置換:

```css
/* ── Glow Border Card ── */
.glow-card {
  position: relative;
  border-radius: var(--radius-lg);
  padding: 1.5px;
  background: linear-gradient(135deg, var(--main), var(--accent), #82B1FF, var(--main));
  background-size: 300% 300%;
  animation: border-glow 4s ease-in-out infinite;
}

.glow-card-inner {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: calc(var(--radius-lg) - 1.5px);
  padding: 24px;
}

.glow-card:hover .glow-card-inner {
  background: rgba(255, 255, 255, 0.8);
}

@keyframes border-glow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

- [ ] **Step 2: ボタンスタイルを更新**

既存の `.btn` 〜 `.btn-full` セクションを以下に置換:

```css
/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-heading);
  font-weight: 500;
  font-size: 15px;
  padding: 14px 28px;
  border-radius: var(--radius-xl);
  border: none;
  cursor: pointer;
  transition: all var(--transition);
  letter-spacing: 0.04em;
  white-space: nowrap;
  text-decoration: none;
}

.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-primary {
  background: linear-gradient(135deg, var(--main-vivid) 0%, var(--glow) 50%, var(--accent) 100%);
  color: var(--white);
  box-shadow: 0 4px 20px rgba(179, 136, 255, 0.35);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(179, 136, 255, 0.5);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--glass-border);
  color: var(--text);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.8);
  border-color: var(--main);
  transform: translateY(-1px);
}

.btn-full { width: 100%; }
```

- [ ] **Step 3: フォームスタイルを更新**

既存の `.form-group` セクションの色参照を更新。`--silver` → `var(--glass-border)` に。`--font-sans` → `var(--font-body)` に。フォーカス時のbox-shadowの色を `rgba(179, 136, 255, ...)` に変更。

- [ ] **Step 4: ブラウザで確認してコミット**

```bash
git add app/static/css/style.css
git commit -m "feat: add glow-card, update buttons and forms for Y2K theme"
```

---

### Task 4: トップページ Y2K化

**Files:**
- Modify: `app/static/css/style.css` (top page セクション)
- Modify: `app/templates/index.html`

- [ ] **Step 1: index.htmlをY2K構造に変更**

```html
{% extends "base.html" %}
{% block title %}星図リーディング{% endblock %}

{% block content %}
<div class="top-header fade-in">
  <div class="hero-crystal">🔮</div>
  <span class="top-ornament">☽ · ✦ · ☽</span>
  <h1 class="top-title">あなたの魂が描く<br>人生の星図</h1>
  <p class="top-subtitle">本来のあなたを思い出し、調和の流れに乗るスピリチュアルリーディング</p>
  <div class="fortune-systems">
    <span class="system-tag">西洋占星術</span>
    <span class="system-tag">数秘術</span>
    <span class="system-tag">九星気学</span>
    <span class="system-tag">六星占術</span>
    <span class="system-tag">四柱推命</span>
    <span class="system-tag">タロット</span>
  </div>
</div>

<div class="menu-cards fade-in">
  <a href="/reading/new" class="menu-card">
    <div class="glow-card">
      <div class="glow-card-inner menu-card-row">
        <span class="menu-card-icon">🌙</span>
        <div class="menu-card-body">
          <div class="menu-card-title">魂のリーディング</div>
          <div class="menu-card-desc">生年月日と星の配置から、あなたの本質と<br>今の流れを読み解きます</div>
          <div class="menu-card-price">FREE</div>
        </div>
        <span class="menu-card-arrow">›</span>
      </div>
    </div>
  </a>

  <a href="/compatibility/new" class="menu-card">
    <div class="glow-card">
      <div class="glow-card-inner menu-card-row">
        <span class="menu-card-icon">✨</span>
        <div class="menu-card-body">
          <div class="menu-card-title">相性リーディング</div>
          <div class="menu-card-desc">二人の魂のつながりと、関係の流れを<br>星から読み解きます</div>
          <div class="menu-card-price">FREE</div>
        </div>
        <span class="menu-card-arrow">›</span>
      </div>
    </div>
  </a>

  <a href="/sample" class="menu-card">
    <div class="glow-card">
      <div class="glow-card-inner menu-card-row">
        <span class="menu-card-icon">📖</span>
        <div class="menu-card-body">
          <div class="menu-card-title">サンプル鑑定を見る</div>
          <div class="menu-card-desc">実際のリーディング結果をご覧ください</div>
        </div>
        <span class="menu-card-arrow">›</span>
      </div>
    </div>
  </a>
</div>

{% if readings %}
<div class="section-header fade-in">
  <div class="section-title">過去のリーディング</div>
</div>
<div class="reading-list fade-in">
  {% for reading in readings %}
  <a href="/reading/{{ reading.id }}" class="reading-item">
    <div class="reading-item-body">
      <div class="reading-item-theme">{{ reading.theme }}</div>
      <div class="reading-item-date">{{ reading.created_at.strftime('%Y年%m月%d日') }}</div>
    </div>
    <span class="reading-item-type">{% if reading.type == 'compatibility' %}相性{% else %}個人{% endif %}</span>
  </a>
  {% endfor %}
</div>
{% else %}
<div class="empty-state fade-in">
  <p>まだリーディングの記録がありません。<br>上のメニューから始めてみましょう。</p>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: style.cssにトップページ用CSSを追加/更新**

既存のトップページセクションを以下に置換。ヒーロークリスタル、グラデーションテキスト、menu-card-rowレイアウトを追加:

```css
/* ── Top Page ── */
.hero-crystal {
  text-align: center;
  font-size: 64px;
  margin: 0 auto 8px;
  filter: drop-shadow(0 0 20px rgba(179, 136, 255, 0.5));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

.top-header {
  text-align: center;
  padding: 56px 24px 36px;
  position: relative;
  z-index: 1;
}

.top-ornament {
  font-size: 20px;
  color: var(--main-vivid);
  letter-spacing: 0.6em;
  margin-bottom: 16px;
  display: block;
  filter: drop-shadow(0 0 8px rgba(179, 136, 255, 0.5));
}

.top-title {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 700;
  line-height: 1.6;
  margin-bottom: 14px;
  background: linear-gradient(135deg, #7C3AED 0%, var(--main-vivid) 30%, var(--accent) 60%, var(--glow) 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: text-shimmer 3s linear infinite;
}

@keyframes text-shimmer {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.top-subtitle {
  font-family: var(--font-heading);
  font-size: 13px;
  color: var(--text-light);
  line-height: 1.8;
  max-width: 300px;
  margin: 0 auto 20px;
}

.fortune-systems {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}

.system-tag {
  font-size: 11px;
  font-family: var(--font-heading);
  color: var(--main-vivid);
  background: rgba(179, 136, 255, 0.1);
  border: 1px solid rgba(179, 136, 255, 0.25);
  border-radius: 20px;
  padding: 4px 14px;
  backdrop-filter: blur(8px);
}

.menu-cards {
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  z-index: 1;
}

.menu-card {
  text-decoration: none;
  color: var(--text);
  transition: transform var(--transition);
}

.menu-card:hover {
  transform: translateY(-3px);
  color: var(--text);
}

.menu-card-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-card-icon {
  font-size: 34px;
  flex-shrink: 0;
  filter: drop-shadow(0 0 10px rgba(179, 136, 255, 0.5));
}

.menu-card-body { flex: 1; }

.menu-card-title {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.menu-card-desc {
  font-size: 12px;
  color: var(--text-light);
  line-height: 1.6;
}

.menu-card-price {
  display: inline-block;
  font-family: var(--font-accent);
  font-size: 14px;
  font-weight: 700;
  margin-top: 6px;
  background: linear-gradient(90deg, var(--glow), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.menu-card-arrow {
  font-size: 20px;
  color: var(--main);
  flex-shrink: 0;
}
```

- [ ] **Step 3: ブラウザで確認してコミット**

```bash
git add app/static/css/style.css app/templates/index.html
git commit -m "feat: redesign top page with Y2K hero, glow cards, gradient text"
```

---

### Task 5: DALL-E並行生成 — ストリーミング中に画像を裏で生成

**Files:**
- Modify: `app/routers/readings.py` (personal_stream内, lines 178-192)
- Modify: `app/services/image_generator.py` (画像ローカル保存追加)

- [ ] **Step 1: image_generator.pyに画像ダウンロード保存を追加**

DALL-E APIは一時URLを返すので、ローカルにダウンロードして静的ファイルとして保存する:

```python
"""DALL-E 3 を使用して鑑定結果ポスター画像を生成するモジュール。"""

import uuid
from pathlib import Path

import httpx
import openai

from app.config import settings

IMAGES_DIR = Path(__file__).resolve().parent.parent / "static" / "images" / "posters"


async def generate_reading_image(
    nickname: str,
    soul_theme: str = "",
    keywords: list[str] | None = None,
) -> str | None:
    """DALL-E 3 でテキストなしの装飾背景画像を生成し、ローカルに保存する。"""
    if not settings.openai_api_key:
        return None

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = (
        "Create a vertical decorative background illustration for a spiritual astrology poster. "
        "Style: dreamy pastel watercolor, soft purple/lavender/pink palette. "
        "NOT photorealistic — ethereal watercolor/digital art. "
        "ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO CHARACTERS in the image.\n\n"
        "LAYOUT (vertical, 9:16 ratio):\n"
        "- TOP: Dreamy night-to-dawn gradient sky with crescent moon, scattered stars, aurora-like soft light.\n"
        "- UPPER CENTER: Empty space with soft light rays (text will be overlaid).\n"
        "- CENTER: A large glowing crystal ball surrounded by a circular mandala of delicate line art. "
        "Soft glow emanating from the crystal.\n"
        "- MIDDLE: Semi-transparent frosted glass card-shaped areas (rounded rectangles in 2x2 grid) "
        "with very subtle borders — placeholder areas for text overlay.\n"
        "- BOTTOM: Crystal gem cluster illustrations (amethyst, moonstone, rose quartz, selenite). "
        "Hanging crescent moon ornaments. Small butterflies. Old mystical book.\n"
        "- Throughout: Light particles, star sparkles, small floating gems.\n\n"
        "IMPORTANT:\n"
        "- ZERO text anywhere. No letters, no characters, no writing.\n"
        "- Color palette: lavender #c8a2e0, soft pink #e8b4c8, white, silver, pale purple #e8d5f5\n"
        "- Frosted card areas subtle enough for text to be readable on top\n"
        "- Mood: elegant, feminine, mystical, premium quality\n"
        "- High detail illustration, suitable for Instagram story sharing"
    )

    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="hd",
            n=1,
        )
        remote_url = response.data[0].url

        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.png"
        filepath = IMAGES_DIR / filename

        async with httpx.AsyncClient() as http:
            img_resp = await http.get(remote_url)
            filepath.write_bytes(img_resp.content)

        return f"/static/images/posters/{filename}"
    except Exception:
        return None
```

- [ ] **Step 2: readings.pyのpersonal_streamにDALL-E並行生成を追加**

`event_stream()` 内で、ストリーミング開始前にバックグラウンドタスクを起動する。`import asyncio` を先頭に追加し、personal_stream関数内を以下のように変更:

```python
import asyncio

# ... (existing imports) ...

@router.post("/api/readings/personal/stream")
async def personal_stream(
    body: PersonalReadingRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    # ... (existing user/profile/reading creation code, lines 138-176) ...

    # Start DALL-E image generation in background
    async def _generate_bg_image(rid: int, nick: str):
        try:
            url = await generate_reading_image(nickname=nick)
            if url:
                async with async_session() as save_db:
                    r = await save_db.get(Reading, rid)
                    if r:
                        r.image_url = url
                        await save_db.commit()
        except Exception:
            pass

    bg_task = asyncio.create_task(_generate_bg_image(reading_id, body.nickname))

    async def event_stream() -> AsyncIterator[str]:
        # ... (existing streaming code) ...
        # After content save, wait for bg_task if still running
        try:
            await asyncio.wait_for(asyncio.shield(bg_task), timeout=5.0)
        except (asyncio.TimeoutError, Exception):
            pass

        yield f"event: done\ndata: {reading_id}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

- [ ] **Step 3: compatibility_streamにも同様のDALL-E並行生成を追加**

同じパターンで`compatibility_stream`にも`_generate_bg_image`タスクを追加。

- [ ] **Step 4: 動作確認してコミット**

```bash
git add app/services/image_generator.py app/routers/readings.py
git commit -m "feat: generate DALL-E poster bg in parallel during streaming"
```

---

### Task 6: 結果ページ — DALL-E背景+HTMLオーバーレイポスター

**Files:**
- Rewrite: `app/templates/reading_result.html`
- Modify: `app/static/css/style.css` (ポスターオーバーレイCSS追加)

- [ ] **Step 1: reading_result.htmlをオーバーレイ構造に書き換え**

`mockup-overlay.html`を参考に、ポスター部分をDALL-E背景+HTMLオーバーレイに変更。アコーディオン詳細は「もっと詳しく読む」ボタンの後に配置:

```html
{% extends "base.html" %}
{% block title %}{{ reading.theme }} — 星図リーディング{% endblock %}

{% block head %}
<meta property="og:title" content="{{ reading.profile.nickname if reading.profile else 'あなた' }}の星図リーディング">
<meta property="og:description" content="6つの占術を統合したスピリチュアルリーディング">
{% if reading.image_url %}
<meta property="og:image" content="{{ reading.image_url }}">
{% endif %}
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
{% endblock %}

{% block content %}
<div class="result-page">
  <a href="/" class="back-link">トップに戻る</a>

  {# ── Poster Card ── #}
  <div class="poster-card-wrap" id="poster-card">
    {% if reading.image_url %}
    <img class="poster-bg" src="{{ reading.image_url }}" alt="">
    {% else %}
    <div class="poster-bg poster-bg--fallback"></div>
    {% endif %}

    <div class="poster-overlay">
      <div class="p-header">
        <span class="p-ornament">☽ · ✦ · ☽</span>
        <h1 class="p-title">あなたの魂が描く<br>人生の星図</h1>
        <p class="p-name">{{ reading.profile.nickname if reading.profile else 'あなた' }}'s reading</p>
      </div>

      {% if sections %}
      {% set s0 = sections[0] if sections|length > 0 else none %}
      <div class="p-soul">
        <div class="p-soul-label">— soul theme —</div>
        <div class="p-soul-text">
          {% if s0 and s0.key_points %}{{ s0.key_points[0] }}{% endif %}
        </div>
      </div>

      <div class="p-grid">
        {% set cards = [
          {'idx': 1, 'label': 'personality', 'title': '自然な性格'},
          {'idx': 2, 'label': 'strength', 'title': '強み'},
          {'idx': 5, 'label': 'love', 'title': '恋愛傾向'},
          {'idx': 4, 'label': 'career', 'title': '仕事の方向'}
        ] %}
        {% for card in cards %}
          {% set sec = sections[card.idx] if sections|length > card.idx else none %}
          <div class="p-card">
            <div class="p-card-label">{{ card.label }}</div>
            <div class="p-card-title">{{ card.title }}</div>
            {% if sec and sec.key_points %}
            <div class="p-card-catch">{{ sec.key_points[0] }}</div>
            <div class="p-keywords">
              {% for kp in sec.key_points[1:4] %}
              <span class="p-kw">{{ kp }}</span>
              {% endfor %}
            </div>
            {% endif %}
          </div>
        {% endfor %}
      </div>

      {% set last = sections[-1] if sections else none %}
      <div class="p-message">
        <div class="p-msg-title">🌙 あなたへのメッセージ 🌙</div>
        <p class="p-msg-body">{% if last and last.key_points %}{{ last.key_points[0] }}{% endif %}</p>
        <p class="p-msg-sign">With Love & Light</p>
      </div>
      {% endif %}

      <div class="p-footer">fortune-reading-app.onrender.com</div>
    </div>
  </div>

  {# ── Share Buttons ── #}
  <div class="share-bar">
    <button class="share-btn share-btn--save" id="save-poster-btn" onclick="savePoster()">ストーリーに保存</button>
    <button class="share-btn share-btn--link" onclick="copyLink()">リンクをコピー</button>
  </div>

  {# ── More Detail Toggle ── #}
  <button class="more-detail-btn" id="more-detail-btn" onclick="toggleDetail()">
    もっと詳しく読む（6つの占術の詳細）
  </button>

  {# ── Accordion Detail (hidden by default) ── #}
  <div class="accordion-container" id="detail-area" style="display:none;">
    {% if sections %}
    {% for section in sections %}
    <div class="accordion-item">
      <button class="accordion-trigger" onclick="toggleAccordion(this)">
        <span class="accordion-title">{{ section.title }}</span>
        <span class="accordion-arrow">▸</span>
      </button>
      <div class="accordion-content">
        <div class="reading-body" data-raw="{{ section.body | e }}"></div>
      </div>
    </div>
    {% endfor %}
    {% endif %}
  </div>

  <div class="result-actions">
    <a href="/chat/{{ reading.id }}" class="btn btn-primary">鑑定師に相談する</a>
    <a href="/" class="btn btn-secondary">トップに戻る</a>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function toggleAccordion(btn) {
  var item = btn.parentElement;
  var content = item.querySelector('.accordion-content');
  var arrow = btn.querySelector('.accordion-arrow');
  var isOpen = content.style.maxHeight && content.style.maxHeight !== '0px';
  if (isOpen) {
    content.style.maxHeight = null;
    arrow.textContent = '▸';
    item.classList.remove('open');
  } else {
    content.style.maxHeight = content.scrollHeight + 'px';
    arrow.textContent = '▾';
    item.classList.add('open');
  }
}

function toggleDetail() {
  var area = document.getElementById('detail-area');
  var btn = document.getElementById('more-detail-btn');
  if (area.style.display === 'none') {
    area.style.display = 'block';
    btn.textContent = '詳細を閉じる';
  } else {
    area.style.display = 'none';
    btn.textContent = 'もっと詳しく読む（6つの占術の詳細）';
  }
}

function renderMarkdownBody(el) {
  var raw = el.dataset.raw || '';
  if (!raw) return;
  function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  var lines = raw.split('\n');
  var html = '', inList = false;
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    if (/^### (.+)/.test(line)) {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<h4>' + esc(line.replace(/^### /,'')) + '</h4>';
    } else if (/^[-*] (.+)/.test(line)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += '<li>' + esc(line.replace(/^[-*] /,'')) + '</li>';
    } else if (line.trim() === '') {
      if (inList) { html += '</ul>'; inList = false; }
    } else {
      if (inList) { html += '</ul>'; inList = false; }
      html += '<p>' + esc(line) + '</p>';
    }
  }
  if (inList) html += '</ul>';
  html = html.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
  el.innerHTML = html;
}

async function savePoster() {
  var btn = document.getElementById('save-poster-btn');
  btn.disabled = true;
  btn.textContent = '生成中...';
  try {
    var card = document.getElementById('poster-card');
    var canvas = await html2canvas(card, { scale: 2, backgroundColor: null, useCORS: true });
    var link = document.createElement('a');
    link.download = '星図リーディング.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  } catch (e) {
    console.error(e);
  }
  btn.textContent = 'ストーリーに保存';
  btn.disabled = false;
}

function copyLink() {
  navigator.clipboard.writeText(window.location.href).then(function() {
    var btn = event.target;
    btn.textContent = 'コピーしました';
    setTimeout(function() { btn.textContent = 'リンクをコピー'; }, 2000);
  });
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.reading-body').forEach(renderMarkdownBody);
});
</script>
{% endblock %}
```

- [ ] **Step 2: style.cssにポスターオーバーレイCSSを追加**

`mockup-overlay.html`のスタイルをstyle.cssに移植。`.poster-card-wrap`, `.poster-bg`, `.poster-overlay`, `.p-header`, `.p-soul`, `.p-grid`, `.p-card`, `.p-message`, `.share-bar`, `.share-btn`, `.more-detail-btn` の全スタイルを追加。フォールバック背景（DALL-E画像がない場合）用の `.poster-bg--fallback` も追加。

- [ ] **Step 3: ブラウザで確認してコミット**

```bash
git add app/templates/reading_result.html app/static/css/style.css
git commit -m "feat: poster overlay with DALL-E bg, share buttons, detail toggle"
```

---

### Task 7: フォームページ — デフォルト値クリア + Y2Kデザイン

**Files:**
- Modify: `app/templates/reading_form.html` (lines 39, 45, 49, 55, 63, 75)

- [ ] **Step 1: デフォルト値を削除**

```html
<!-- line 39: value="yuna" → 削除 -->
<input type="text" id="nickname" name="nickname" placeholder="例：さくら" required autocomplete="off">

<!-- line 45: value="1995-06-26" → 削除 -->
<input type="date" id="birth_date" name="birth_date" required min="1940-01-01" max="2015-12-31">

<!-- line 49: value="06:25" → 削除 -->
<input type="time" id="birth_time" name="birth_time">

<!-- line 55: value="函館" → 削除 -->
<input type="text" id="birth_place" name="birth_place" placeholder="例：東京都渋谷区" autocomplete="off">

<!-- line 63: selected を削除 -->
<option value="女性">女性</option>

<!-- line 75: selected を削除 -->
<option value="O">O型</option>
```

- [ ] **Step 2: フォームのセクションクラスを更新**

`.form-section` → `.glow-card` + `.glow-card-inner` 構造に変更して統一感を出す。

- [ ] **Step 3: コミット**

```bash
git add app/templates/reading_form.html
git commit -m "fix: clear hardcoded form defaults, apply Y2K form design"
```

---

### Task 8: 残りのCSS移植 — チャット、アコーディオン、ユーティリティ

**Files:**
- Modify: `app/static/css/style.css` (chat, accordion, utility セクション)

- [ ] **Step 1: チャットページのCSSカラーを更新**

`.chat-header` のグラデーション色を `var(--main-vivid)` ベースに。`.chat-bubble.user` の背景を Y2K パレットに。その他テキスト色を `var(--text)`, `var(--text-light)` に統一。

- [ ] **Step 2: アコーディオンCSSを更新**

`.accordion-trigger` の `font-family` を `var(--font-heading)` に変更。色参照を新変数に。`.reading-body strong` のハイライト色をY2Kパレットに。

- [ ] **Step 3: ritual animationの色を更新**

`.ritual-ring` のborder-colorとアニメーションの色をY2Kパレットに合わせる。

- [ ] **Step 4: 全ページ確認してコミット**

トップ、フォーム、鑑定中、結果、チャットの各ページを確認。

```bash
git add app/static/css/style.css
git commit -m "feat: update chat, accordion, ritual styles to Y2K palette"
```

---

### Task 9: OGPメタタグ — URLシェア時のリッチプレビュー

**Files:**
- Modify: `app/templates/base.html` (headブロック内)
- Modify: `app/routers/readings.py` (reading_resultにOGP用データ追加)

- [ ] **Step 1: base.htmlにデフォルトOGPを追加**

`{% block head %}{% endblock %}` の前に:

```html
<meta property="og:site_name" content="星図リーディング">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

- [ ] **Step 2: reading_result.htmlには既にTask 6でOGPブロックを追加済み**

`{% block head %}` 内で `og:title`, `og:description`, `og:image` を設定している。`reading.image_url` がローカルパスの場合はフルURLに変換が必要。`readings.py` の `reading_result` ビューで `request.url_for('static', ...)` を使ってフルURLを渡す。

- [ ] **Step 3: コミット**

```bash
git add app/templates/base.html app/routers/readings.py
git commit -m "feat: add OGP meta tags for rich URL sharing"
```

---

### Task 10: 最終確認 — 全ページ通しテスト

- [ ] **Step 1: 開発サーバー起動**

```bash
cd /Users/kousuke/fortune-app && python3 -m uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 2: 全ページ確認チェックリスト**

1. トップページ: ヒーロークリスタル浮遊、グラデーションテキスト、星の瞬き、グローカード
2. フォームページ: デフォルト値が空、Y2Kスタイル適用
3. 鑑定中: リチュアルアニメーション表示
4. 結果ページ: DALL-E背景+テキストオーバーレイ、シェアボタン、「もっと詳しく」トグル
5. アコーディオン: 開閉動作、マークダウンレンダリング
6. 画像保存: html2canvasでPNG保存
7. リンクコピー: クリップボードにURL

- [ ] **Step 3: スマホ確認**

ローカルIP経由でスマホからアクセスし、全ページの表示を確認。

- [ ] **Step 4: モックアップファイル削除 + 最終コミット**

```bash
rm mockup-y2k.html mockup-overlay.html
git add -A
git commit -m "feat: complete Y2K design overhaul"
```
