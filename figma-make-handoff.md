# Fortune Reading App — Figma Make Design Handoff

## App Overview
A mobile-first fortune reading web app (iOS Safari viewport: 390×844). Japanese spiritual reading app combining 6 divination systems. The aesthetic is "ethereal aura" — deep purple gradients, glassmorphism cards, glowing orbs, and sparkle particles.

---

## Design Tokens

### Colors
```
Background gradient (top→bottom): #352466 → #4a3590 → #3a2a75
Glow violet: #9333ea
Glow soft: #a78bfa
Glow pink: #c084fc
Card BG: rgba(255,255,255,0.08)
Card border: rgba(216,180,254,0.22)
Card glow: rgba(167,139,250,0.18)
Text primary: #F5F0FF
Text secondary: #D8B4FE
Accent mauve: #E9D5FF
Accent pink: #F0ABFC
Highlight (white text): #FAF5FF
BANNED colors: no orange, warm tones, or gold (#FFD700)
```

### Typography
```
Headings/Catch copy: Zen Kaku Gothic New — 700, 24-28px, letter-spacing 2px
Tab names/Buttons: Shippori Mincho — 700, 14-16px
Detail body ("更に詳しく"): Kaisei Decol — 700, 14px, line-height 2.4
Body text: Noto Sans JP — 500, 14px, line-height 2.2
Labels (English): JetBrains Mono — 600-700, 9-11px, letter-spacing 3-4px, UPPERCASE
```

### Spacing & Layout
```
Container max-width: 440px, centered
Container padding: 0 20px 60px
Card border-radius: 12-14px
Card padding: 28px 24px
Input border-radius: 8px
Button border-radius: 8-10px
Section gap: 10px
Grid columns: 2 (personal reading), 1 (compatibility reading)
```

### Effects
```
Glassmorphism: backdrop-filter blur(16px), rgba(255,255,255,0.08) bg
Button gradient: linear-gradient(135deg, #9333ea, #c084fc)
Button shadow: 0 4px 28px rgba(147,51,234,0.35)
Glow pulse: text-shadow 0 0 28px rgba(216,180,254,0.7)
Card hover glow: box-shadow 0 0 20px rgba(167,139,250,0.18)
Background orbs: 200-280px blurred circles, rgba purple/mauve at 15-25% opacity
```

---

## PAGE 1: Top / Index (/)

Mobile viewport 390×844. Deep purple gradient background with floating glow orbs and sparkle particles.

### Structure (top to bottom):

1. **Hero Section** (centered)
   - Mandala SVG: 200×200, concentric circles + star polygon, slow rotation animation
   - Moon emoji (🌙) centered in mandala with glow effect
   - Title: "あなたの魂が描く\n人生の星図" — Zen Kaku Gothic New, 28px, 700, #FAF5FF, glow pulse animation
   - Subtitle: "6つの占術体系を統合した\n実用型スピリチュアルリーディング" — 13px, #D8B4FE
   - Tags row (6 tags, flex-wrap): "西洋占星術" "数秘術" "九星気学" "六星占術" "四柱推命" "タロット"
     - Each tag: JetBrains Mono, 9px, 600, letter-spacing 2px, padding 6px 12px, border-radius 6px, rgba(255,255,255,0.05) bg, rgba(216,180,254,0.15) border

2. **Divider**: "✧ ✦ ✧" with gradient lines extending left/right

3. **Menu Cards** (vertical stack, 16px gap)
   - Card 1: 🌙 icon (purple bg) | "魂のリーディング" + "あなただけの星図を読み解く" | "FREE" badge | → arrow
   - Card 2: ✨ icon (pink bg) | "相性リーディング" + "二人の星図を重ね合わせる" | "FREE" badge | → arrow
   - Card 3: ✦ icon (purple bg) | "サンプル鑑定を見る" + "鑑定の雰囲気を体験" | → arrow
   - Each card: glass card style, flex row, 28px padding, 12px border-radius
   - Icon container: 52×52px, 12px border-radius
   - Title: Zen Kaku Gothic New, 15px, 700, white-space nowrap
   - Desc: Noto Sans JP, 12px, 400, #D8B4FE
   - Badge: JetBrains Mono, 9px, 700, #F0ABFC text, rgba(240,171,252,0.1) bg

4. **Recent Readings** section
   - Header: "✧ RECENT READINGS" — JetBrains Mono, 10px, 700, letter-spacing 4px
   - Empty state: glass card, 🌙 icon, "まだ鑑定履歴がありません\n最初のリーディングを体験してみましょう"
   - Or reading cards: icon + theme name + date

5. **Footer**: "✧ FORTUNE READING ✧ 2026" — JetBrains Mono, 9px, rgba(216,180,254,0.3)

---

## PAGE 2: Personal Reading Form (/reading/new)

### Structure:

1. **Page Header** (centered)
   - "← TOP" back link
   - "魂のリーディング" — 24px, Zen Kaku Gothic New, 700
   - "生年月日から、あなただけの星図を読み解きます" — 12px, #D8B4FE

2. **Form Card** (glass card, 14px border-radius, 32px 24px padding)
   - Section title: "PROFILE" — JetBrains Mono, 9px, 700, letter-spacing 3px, #F0ABFC
   - Saved profile dropdown (if available)
   - Fields:
     - ニックネーム: text input, placeholder "呼ばれたい名前"
     - 生年月日: 3-column grid (year/month/day), placeholder "1995" "6" "26"
     - 出生時刻 OPTIONAL: 2-column grid (hour/minute), placeholder "14" "30"
     - 出生地 OPTIONAL: text input, placeholder "東京都"
     - 性別 OPTIONAL: select (女性/男性/その他/回答しない)
     - 血液型 OPTIONAL: select (A/B/O/AB)
   - Input style: rgba(255,255,255,0.07) bg, rgba(216,180,254,0.15) border, 8px radius, 12px 16px padding
   - Label: Zen Kaku Gothic New, 12px, 600, #D8B4FE
   - "OPTIONAL" tag: JetBrains Mono, 9px, rgba(216,180,254,0.4)

3. **Theme Card** (separate glass card)
   - 相談テーマ: textarea, placeholder "今の自分に必要なメッセージ\n何でも自由に書いてください"

4. **Submit Button**: "✦ 星図を読み解く" — full width, gradient bg (#9333ea→#c084fc), Zen Kaku Gothic New, 16px, 700, white text, 10px radius, glow shadow

---

## PAGE 3: Compatibility Form (/compatibility/new)

### Structure:

1. **Page Header** (centered)
   - "← TOP" back link
   - "相性リーディング" — 24px
   - "二人の星図を重ね合わせます" — 12px, #D8B4FE

2. **Person 1 Card** — "PERSON 1 — あなた"
   - Same fields as personal form with "person1_" prefix

3. **Person 2 Card** — "PERSON 2 — 相手"
   - Same fields with "person2_" prefix

4. **Relationship Card** — "RELATIONSHIP"
   - 関係性: select (交際中/片思い/友人/家族/職場・仕事/元カレ・元カノ/その他)
   - 出会った時期 OPTIONAL: text input
   - 相談テーマ: textarea

5. **Submit Button**: "✦ 二人の星図を読み解く"

---

## PAGE 4: Loading / Generating

Full-screen centered loading state.

1. **Ritual Orb**: 3 concentric spinning rings (different speeds, different purple tones), 🔮 emoji center with glow
2. **Title**: "星の配置を読み解いています" — 22px
3. **Phase text**: rotating messages ("西洋占星術の星座を確認中" → "数秘術のライフパスを算出中" → etc.)
4. **Progress bar**: thin 3px, 200px wide, gradient fill expanding left to right

---

## PAGE 5: Reading Result (/reading/{id})

### A. Poster Section (full-bleed, DALL-E background at 18% opacity)

**Personal Reading:**
1. "SOUL READING" label — JetBrains Mono, 11px, glow pulse
2. Name (uppercase) + birth date — JetBrains Mono, 14px/11px, #E9D5FF
3. Mandala SVG (120×120) with 🌙 center
4. Title glass card: catch copy text — 28px, Zen Kaku Gothic New, text-shadow glow
5. Divider "✧ ✦ ✧"
6. **Highlight Cards** (2×2 grid, 10px gap):
   - PERSONALITY / STRENGTH / LOVE / CAREER
   - Each: glass card, label (JetBrains Mono 9px #F0ABFC) + value (13px, 700)
7. Soul message card: gradient glass, 15px, Zen Kaku Gothic New, #E9D5FF, glow pulse
8. "✦ 占いの結果を保存する" button (save)
9. "✧ LINK をコピー" button (secondary)
10. "SCROLL FOR DETAIL ▼" floating prompt

**Compatibility Reading:**
- "COMPATIBILITY READING" label instead
- Names: "Name1 × Name2"
- Venn diagram mandala (two overlapping circles)
- No highlight cards (hidden)
- Single-column detail grid below

### B. Detail Section (accordion grid)

- "✧ DETAILED READING ✧" header
- Grid of section cards (2-col personal, 1-col compatibility)

**Personal sections (10):**
| Section | Color | Slug |
|---------|-------|------|
| 全体要約 | #a78bfa | summary |
| 性格・本質 | #c084fc | personality |
| 才能・強み | #818cf8 | strength |
| 注意点・課題 | #f472b6 | caution |
| 仕事・お金 | #34d399 | career |
| 恋愛・人間関係 | #f0abfc | love |
| 今年のテーマ | #60a5fa | yearly |
| 月別の流れ | #a78bfa | monthly |
| 今すぐやること | #fbbf24 | action |
| 魂のメッセージ | #e9d5ff | message |

**Compatibility sections (8):**
| Section | Color | Slug |
|---------|-------|------|
| 二人の全体像 | #c084fc | overview |
| それぞれの本質 | #a78bfa | essence |
| 相性分析 | #f0abfc | chemistry |
| 関係の課題 | #f472b6 | challenge |
| 恋愛アドバイス | #e9d5ff | love |
| 今年のタイムライン | #60a5fa | timeline |
| 今すぐやること | #fbbf24 | action |
| 魂のメッセージ | #34d399 | message |

**Each section card (collapsed):**
- Glass card, 12px radius
- Trigger row: colored icon (36×36, 8px radius) + title (Shippori Mincho, 14px, 700, section color) + ▾ arrow
- On open: spans full width (grid-column: 1 / -1)

**Each section card (expanded):**
- Catch copy: Zen Kaku Gothic New, 18px, 700, left border (3px, section color), glass bg
- Key point cards: flex row, ✦ marker + text, glass bg, subtle border
  - Labeled KP: "ラベル：値" split with label as JetBrains Mono 9px
  - Unlabeled KP: dynamic font size based on length (6chars→20px, 10→17px, 16→15px)
- "✧ 更に詳しく" toggle button
- Expanded body: Kaisei Decol, 14px, 700, line-height 2.4
  - h4 subheadings with colored bottom border
  - Bulleted lists with glass-bg items
  - Bold keywords: short words → size up + bg highlight, phrases → underline + color
  - Tarot card SVG illustrations for 魂のメッセージ section

### C. Monthly Grid (if applicable)
- 3-column grid of month cards
- Each: month number + keyword
- Current month highlighted with pink border
- Expandable on tap: action text + warning note

### D. CTA Section
- "✦ 鑑定師に相談する" primary button (gradient)
- "← TOP" secondary link

---

## PAGE 6: Chat (/chat/{id})

1. **Sticky Header**: glass bg, back arrow + 🔮 icon + "鑑定師に質問" title + "AI READING" sublabel
2. **Messages area**: scrollable, flex column
   - Welcome message: centered, 🔮 icon + intro text
   - User bubbles: right-aligned, purple gradient bg
   - Assistant bubbles: left-aligned, glass card bg, "READER" label in pink
   - Typing indicator: 3 bouncing dots
3. **Sticky Input**: glass bg, textarea + purple send button (44×44)

---

## PAGE 7: Sample (/sample)

Simplified version of result page:
- "SAMPLE" badge
- Static poster with hardcoded content
- No accordion, just the poster
- CTA to start real reading

---

## Background Effects (all pages)

1. **Gradient layer**: fixed, full viewport, multiple radial gradients in purple/mauve/pink
2. **Glow orbs**: 4 fixed blurred circles (200-280px), subtle floating animation, different positions
3. **Sparkle particles**: 28 total (14 white ✦✧, 8 lavender ✦·, 6 pink ✧·), randomly positioned, twinkling animation at varying speeds

---

## Component Library Summary

| Component | BG | Border | Radius | Padding |
|-----------|-----|--------|--------|---------|
| Glass Card | rgba(255,255,255,0.08) | rgba(216,180,254,0.22) | 12px | 28px 24px |
| Form Card | rgba(255,255,255,0.08) | rgba(216,180,254,0.22) | 14px | 32px 24px |
| Input | rgba(255,255,255,0.07) | rgba(216,180,254,0.15) | 8px | 12px 16px |
| Primary Button | gradient #9333ea→#c084fc | none | 8-10px | 16px 36px |
| Secondary Button | rgba(255,255,255,0.06) | rgba(216,180,254,0.22) | 8px | 12px 24px |
| Tag | rgba(255,255,255,0.05) | rgba(216,180,254,0.15) | 6px | 6px 12px |
| Toast | rgba(147,51,234,0.9) | none | 8px | 12px 24px |
| Section Card | rgba(255,255,255,0.08) | rgba(216,180,254,0.22) | 12px | 14px trigger |
| KP Card | rgba(255,255,255,0.04) | rgba(216,180,254,0.1) | 8px | 12px 14px |
| Month Card | rgba(255,255,255,0.08) | rgba(216,180,254,0.22) | 10px | 14px 10px |
