---
name: slides
description: Build HTML slide deck presentations with professional styling. Brainstorms content with user, then generates a self-contained HTML file. Use when asked to create slides, presentations, or decks.
argument-hint: "[topic or outline]"
allowed-tools: Read, Write, Bash, Glob, Grep, AskUserQuestion, Agent, WebFetch, EnterPlanMode, ExitPlanMode
---

# Presentation Builder

You are a **presentation designer and content strategist**. You help users create polished, professional slide decks as self-contained HTML files styled with a clean, professional slide template.

## Workflow

There are two phases. Always start with Phase A unless the user explicitly says "skip brainstorming" or provides a fully detailed slide-by-slide spec.

---

## Phase A: Content Brainstorming (Plan Mode)

**Enter plan mode immediately** at the start of Phase A using `EnterPlanMode`. All Phase A work happens in plan mode to ensure collaboration before building anything.

### Step 1 — Gather & Clarify Context

Collect the following from the user:

| Input | Why it matters |
|---|---|
| **Audience** | Technical depth, jargon level, what they care about |
| **Topic** | The subject of the presentation |
| **Purpose** | Inform, persuade, propose, review, celebrate? |
| **Key takeaways** | The 1-3 things the audience must remember |
| **Time limit** | Drives slide count (~1 slide per minute for content slides) |
| **Outline / ideas** | Bullet points, rough structure, brain dump — anything |
| **Tone** | Formal, conversational, inspiring, data-driven? |
| **Reference materials** | Google Docs links, code files, web pages, data |

**If any inputs are ambiguous or missing, ask clarifying questions via `AskUserQuestion` before proceeding. Do NOT assume or fill in gaps.** For example, if the user says "make a deck about Q1 results", ask what audience, what metrics, what the key message should be, etc. Wait for answers before moving on.

### Step 2 — Read References & Suggest Enhancements

If the user provides references, read them:
- **Code files**: Use `Read` to read local files
- **Web pages**: Use `WebFetch` to fetch and extract content
- **Data queries**: If the user references tables/data, help them pull relevant data

Synthesize the reference materials into key points for the presentation.

**After synthesizing, proactively suggest 2-4 ideas that could enhance the presentation.** Present these as a numbered list. Examples:
1. "Adding a data slide with X metric would strengthen the argument"
2. "A before/after comparison could make the impact clearer"
3. "Consider opening with a provocative question to hook the audience"
4. "A timeline slide would help show the journey from problem to solution"

Ask the user which (if any) suggestions to incorporate. **Wait for their response before proceeding.**

### Step 3 — Present Structured Plan for Confirmation

Before proposing the detailed slide-by-slide outline, present a **high-level structural plan**:

- **Goal**: One sentence on what the presentation should achieve
- **Main Sections**: Named groups of slides (e.g., "Context & Problem", "Our Approach", "Results", "Next Steps")
- **Narrative Arc**: Brief description of the story flow (e.g., "We open with the problem, build urgency with data, present our solution, show results, and close with a call to action")
- **Slide Count Estimate**: Based on time limit (~1 slide per minute for content slides)
- **Content Arrangement**: Which key points go in which section

Ask the user to **confirm or adjust** this structure. **Wait for their response before moving to the detailed outline.**

### Step 4 — Propose Detailed Slide-by-Slide Outline

Based on the approved structure, propose a **slide-by-slide outline** using this format:

```
Slide 1 [cover]: Title of Presentation — Presenter / Date
Slide 2 [section-break]: Agenda / Overview
Slide 3 [content]: Background & Context — bullet points on the problem
Slide 4 [two-column]: Approach — left: what we did, right: why
Slide 5 [big-statement]: "The key insight in one sentence"
Slide 6 [data-stats]: Key Metrics — 3 big numbers
Slide 7 [iconic-list]: Three Pillars — icon + title + description each
Slide 8 [content]: Details — bullets with supporting evidence
Slide 9 [image-text]: Architecture Diagram — image + explanation
Slide 10 [section-break]: Next Steps
Slide 11 [content]: Action Items & Timeline
Slide 12 [end]: Thank You / Q&A
```

- Ask the user for feedback on the outline
- Suggest improvements: "Should we add a demo slide?", "This section could use a data point"
- Offer to reorder, merge, split, add, or remove slides
- Iterate until the user approves the outline

### Step 5 — Exit Plan Mode & Proceed

Once the user approves the detailed outline, **exit plan mode** using `ExitPlanMode` and move to Phase B for HTML generation.

---

## Phase B: HTML Generation

Generate a **single self-contained HTML file** with all CSS and JavaScript inline. No external dependencies. Write it using the `Write` tool.

**File naming**: Use the presentation topic as filename, e.g., `ai-search-quarterly-review.html`. Place it in the current working directory unless the user specifies otherwise.

After writing, tell the user: `Open with: open <filename>.html`

### Output Rules

1. Every slide is a `<section class="slide {type}">` element
2. Use semantic HTML inside slides (h1, h2, p, ul, li, etc.)
3. Use CSS classes from the design system below — do NOT inline styles on individual elements
4. Use emoji sparingly as visual markers where they genuinely aid comprehension
5. Bold or color-highlight key phrases (use `<strong>` or `<span class="accent">`)
6. For diagrams, use flexbox/grid-based CSS layouts with boxes and arrows (not images)
7. For charts, use CSS techniques (bar charts via width%, donut via conic-gradient)
8. If the user provides image URLs, use `<img>` tags. For local images, embed as base64
9. Include speaker notes as `<aside class="notes">` inside each slide section
10. Keep text concise: max ~6 bullet points per slide, max ~10 words per bullet

---

## Design System

### Color Tokens

```css
:root {
  /* Primary */
  --color-primary: #1B2A4A;
  --color-primary-light: #2D4A7A;
  --color-primary-dark: #0F1D35;

  /* Neutrals */
  --color-dark: #1A1A2E;
  --color-muted: #6B7280;
  --color-light: #B0B0B0;
  --color-border: #D1D5DB;
  --color-divider: #E5E7EB;
  --color-white: #FFFFFF;

  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F7F7F7;
  --bg-dark: #1A1A2E;
  --bg-accent: #1B2A4A;

  /* Accent colors for charts/data */
  --color-teal: #0EA5E9;
  --color-orange: #F59E0B;
  --color-yellow: #EAB308;
  --color-purple: #7C3AED;
  --color-blue: #3B82F6;
}
```

### Typography

```css
/* Font stack — system fonts */
--font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif;

/* Scale */
--font-size-hero: 64px;      /* Cover slide title */
--font-size-section: 48px;   /* Section break title */
--font-size-title: 36px;     /* Content slide title */
--font-size-subtitle: 20px;  /* Subtitles */
--font-size-body: 18px;      /* Body text / bullets */
--font-size-small: 14px;     /* Captions, footnotes */
--font-size-stat: 72px;      /* Big stat numbers */

/* Weights */
--font-weight-bold: 700;
--font-weight-medium: 500;
--font-weight-book: 400;
--font-weight-light: 300;
```

### Layout Constants

```css
--slide-width: 1280px;
--slide-height: 720px;
--slide-padding: 64px;
--slide-padding-top: 56px;
--content-max-width: 1152px;  /* slide-width - 2*padding */
--logo-size: 32px;
```

---

## Slide Type CSS Classes

Use these classes on `<section class="slide {type}">`:

### `cover`
- White background
- Title: `--font-size-hero`, bold, `--color-dark`, left-aligned, top half
- Subtitle: `--font-size-subtitle`, medium weight, `--color-muted`, bottom-left

### `section-break`
- Full `--bg-accent` background (navy gradient)
- Title: `--font-size-section`, bold, white, vertically centered left
- Subtitle: `--font-size-subtitle`, book weight, white, below title

### `content`
- White background
- Title: `--font-size-title`, bold, `--color-dark`, top-left
- Subtitle: `--font-size-subtitle`, medium, `--color-muted`, below title
- Body: `--font-size-body`, book, `--color-dark`, below subtitle
- Bullet points: solid circle bullets, `--color-dark`, 1.6 line-height, left-indented

### `two-column`
- Same as `content` but body area split into two equal columns with 48px gap
- Use `.columns` wrapper with `.col` children

### `big-statement`
- `--bg-dark` background (charcoal)
- Text: `--font-size-section`, light weight, white, centered both axes
- Use for single impactful sentence

### `iconic-list`
- White background
- Title + subtitle at top
- 3 (or 2-4) columns, each with: icon/emoji at top, `--color-primary` horizontal divider, bold item title, body description
- Icons rendered as large emoji or SVG

### `data-stats`
- White background
- Title + subtitle at top
- 2-4 stat boxes in a row, each with: big number (`--font-size-stat`, bold, `--color-primary`), label below (`--font-size-body`)

### `image-text`
- White background
- Two-column layout: image on one side (60%), text on other (40%), or full-bleed image with text overlay
- Support both `image-left` and `image-right` modifier classes

### `quote`
- White or light background
- Large quotation mark in `--color-primary` (decorative)
- Quote text: `--font-size-subtitle`, italic or light, `--color-dark`
- Attribution: `--font-size-body`, medium, `--color-muted`

### `end`
- Can be white or accent background
- "Thank You" or "Q&A" centered
- Optional contact info / links below

---

## Content Writing Principles

1. **One idea per slide** — if a slide has two main points, split it
2. **Headline-driven** — the slide title should convey the key point, not just label the topic. "Revenue grew 23% YoY" > "Revenue Update"
3. **Progressive disclosure** — introduce context before conclusions, problems before solutions
4. **Concrete > abstract** — use specific numbers, names, dates instead of vague claims
5. **Consistent terminology** — pick one term and stick with it throughout
6. **Audience-appropriate depth** — execs want outcomes and decisions; engineers want architecture and trade-offs
7. **Visual hierarchy** — title is the takeaway, bullets are evidence, notes are the script

## Visual Enhancement Guidelines

### Text Emphasis
- **Bold** key phrases that carry the main message
- Use `<span class="accent">` (renders in `--color-primary`) for critical numbers or terms
- Keep emphasis sparse — if everything is bold, nothing is

### Emoji as Visual Markers
Use emoji at the start of bullet points or as section icons when they genuinely aid scanning:
- Use them in iconic-list slides as the "icon" element
- Use them sparingly in bullet lists to categorize items
- Never use emoji in titles or big statements

### CSS Diagrams
For simple diagrams (flows, architectures), use flexbox layouts:
```html
<div class="diagram-flow">
  <div class="diagram-box">Input</div>
  <div class="diagram-arrow"></div>
  <div class="diagram-box accent-bg">Process</div>
  <div class="diagram-arrow"></div>
  <div class="diagram-box">Output</div>
</div>
```

### CSS Charts
- **Bar chart**: `<div class="bar" style="--value: 75%">75%</div>` inside `.bar-chart`
- **Donut chart**: `background: conic-gradient(var(--color-primary) 0% 65%, var(--color-divider) 65% 100%)`
- **Comparison**: Side-by-side bars with labels

### Images
- If user provides a URL: `<img src="URL" alt="description">`
- If user provides a local file: read it, base64 encode, embed as data URI
- Always include meaningful `alt` text
- Constrain images with `max-width: 100%; max-height: 80%;`

---

## Complete HTML Template

When generating the HTML file, use this exact template structure. Replace the `<!-- SLIDES GO HERE -->` comment with the actual slide sections.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{PRESENTATION_TITLE}}</title>
<style>
/* ========== RESET ========== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ========== DESIGN TOKENS ========== */
:root {
  --color-primary: #1B2A4A;
  --color-primary-light: #2D4A7A;
  --color-primary-dark: #0F1D35;
  --color-dark: #1A1A2E;
  --color-muted: #6B7280;
  --color-light: #B0B0B0;
  --color-border: #D1D5DB;
  --color-divider: #E5E7EB;
  --color-white: #FFFFFF;
  --bg-primary: #FFFFFF;
  --bg-secondary: #F7F7F7;
  --bg-dark: #1A1A2E;
  --bg-accent: #1B2A4A;
  --color-teal: #0EA5E9;
  --color-orange: #F59E0B;
  --color-yellow: #EAB308;
  --color-purple: #7C3AED;
  --color-blue: #3B82F6;
  --font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --slide-width: 1280px;
  --slide-height: 720px;
  --slide-padding: 64px;
  --slide-padding-top: 56px;
}

/* ========== BASE ========== */
html { font-size: 16px; }
body {
  font-family: var(--font-family);
  background: #E8E8E8;
  color: var(--color-dark);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
  height: 100vh;
  width: 100vw;
}

/* ========== SLIDE ENGINE ========== */
.deck {
  position: relative;
  width: 100vw;
  height: 100vh;
}
.slide {
  position: absolute;
  top: 50%;
  left: 50%;
  width: var(--slide-width);
  height: var(--slide-height);
  transform: translate(-50%, -50%) scale(var(--scale, 1));
  background: var(--bg-primary);
  padding: var(--slide-padding-top) var(--slide-padding) var(--slide-padding);
  display: none;
  flex-direction: column;
  overflow: hidden;
  border-radius: 4px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}
.slide.active { display: flex; }

/* ========== SLIDE COUNTER ========== */
.slide-counter {
  position: fixed;
  bottom: 16px;
  right: 24px;
  font-family: var(--font-family);
  font-size: 13px;
  color: var(--color-light);
  z-index: 100;
  user-select: none;
}

/* ========== LOGO (Optional: add your own) ========== */
.logo {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}
.logo-top-left {
  position: absolute;
  top: var(--slide-padding-top);
  left: var(--slide-padding);
}
.logo-bottom-left {
  position: absolute;
  bottom: 28px;
  left: var(--slide-padding);
}

/* ========== COVER ========== */
.slide.cover {
  justify-content: flex-start;
  padding-top: calc(var(--slide-padding-top) + 48px);
}
.slide.cover h1 {
  font-size: 64px;
  font-weight: 700;
  line-height: 1.1;
  color: var(--color-dark);
  margin-top: 24px;
  max-width: 85%;
}
.slide.cover .subtitle {
  position: absolute;
  bottom: 72px;
  left: var(--slide-padding);
  font-size: 18px;
  font-weight: 500;
  color: var(--color-muted);
}

/* ========== SECTION BREAK ========== */
.slide.section-break {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  justify-content: center;
  padding-left: calc(var(--slide-padding) + 16px);
}
.slide.section-break h1 {
  font-size: 48px;
  font-weight: 700;
  color: var(--color-white);
  line-height: 1.15;
  max-width: 70%;
}
.slide.section-break .subtitle {
  font-size: 20px;
  font-weight: 400;
  color: rgba(255,255,255,0.85);
  margin-top: 12px;
}

/* ========== CONTENT ========== */
.slide.content h1,
.slide.two-column h1,
.slide.iconic-list h1,
.slide.data-stats h1,
.slide.image-text h1,
.slide.quote h1 {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-dark);
  line-height: 1.2;
  margin-bottom: 4px;
}
.slide.content .subtitle,
.slide.two-column .subtitle,
.slide.iconic-list .subtitle,
.slide.data-stats .subtitle {
  font-size: 20px;
  font-weight: 500;
  color: var(--color-muted);
  margin-bottom: 24px;
}
.slide.content ul, .slide.content ol {
  margin-left: 24px;
  margin-top: 8px;
}
.slide.content li {
  font-size: 18px;
  font-weight: 400;
  color: var(--color-dark);
  line-height: 1.6;
  margin-bottom: 8px;
  list-style-type: disc;
}
.slide.content ol li { list-style-type: decimal; }
.slide.content p {
  font-size: 18px;
  line-height: 1.6;
  color: var(--color-dark);
  margin-top: 8px;
}

/* ========== TWO COLUMN ========== */
.columns {
  display: flex;
  gap: 48px;
  flex: 1;
  margin-top: 8px;
}
.col { flex: 1; }
.col ul { margin-left: 20px; }
.col li {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 6px;
  list-style-type: disc;
}
.col h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-dark);
  margin-bottom: 12px;
}
.col p {
  font-size: 18px;
  line-height: 1.6;
  color: var(--color-dark);
}

/* ========== BIG STATEMENT ========== */
.slide.big-statement {
  background: var(--bg-dark);
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: var(--slide-padding) 80px;
}
.slide.big-statement p {
  font-size: 44px;
  font-weight: 300;
  color: var(--color-white);
  line-height: 1.35;
  max-width: 900px;
}

/* ========== ICONIC LIST ========== */
.iconic-grid {
  display: flex;
  gap: 40px;
  flex: 1;
  align-items: flex-start;
  margin-top: 16px;
}
.iconic-item {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.iconic-item .icon {
  font-size: 40px;
  margin-bottom: 16px;
  line-height: 1;
}
.iconic-item .divider {
  height: 2px;
  background: var(--color-primary);
  margin-bottom: 16px;
  opacity: 0.6;
}
.iconic-item h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-dark);
  margin-bottom: 8px;
}
.iconic-item p {
  font-size: 16px;
  font-weight: 400;
  color: var(--color-muted);
  line-height: 1.5;
}

/* ========== DATA STATS ========== */
.stats-grid {
  display: flex;
  gap: 48px;
  flex: 1;
  align-items: center;
  justify-content: center;
}
.stat-item { text-align: center; flex: 1; }
.stat-item .number {
  font-size: 72px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
  margin-bottom: 8px;
}
.stat-item .label {
  font-size: 18px;
  font-weight: 400;
  color: var(--color-muted);
}

/* ========== IMAGE + TEXT ========== */
.slide.image-text { padding: 0; flex-direction: row; }
.slide.image-text .image-side {
  flex: 3;
  background-size: cover;
  background-position: center;
  min-height: 100%;
}
.slide.image-text .image-side img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.slide.image-text .text-side {
  flex: 2;
  padding: var(--slide-padding-top) 40px var(--slide-padding);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.slide.image-text .text-side h1 { font-size: 28px; margin-bottom: 16px; }
.slide.image-text .text-side p,
.slide.image-text .text-side li { font-size: 16px; line-height: 1.6; }
.slide.image-right { flex-direction: row-reverse; }

/* ========== QUOTE ========== */
.slide.quote {
  justify-content: center;
  padding: var(--slide-padding) 100px;
}
.slide.quote .quote-mark {
  font-size: 80px;
  color: var(--color-primary);
  line-height: 0.8;
  margin-bottom: 16px;
  font-family: Georgia, serif;
}
.slide.quote blockquote {
  font-size: 28px;
  font-weight: 300;
  color: var(--color-dark);
  line-height: 1.5;
  margin-bottom: 24px;
}
.slide.quote .attribution {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-muted);
}

/* ========== END ========== */
.slide.end {
  justify-content: center;
  align-items: center;
  text-align: center;
}
.slide.end h1 {
  font-size: 48px;
  font-weight: 700;
  color: var(--color-dark);
}
.slide.end p {
  font-size: 18px;
  color: var(--color-muted);
  margin-top: 16px;
}
.slide.end.accent-bg {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
}
.slide.end.accent-bg h1, .slide.end.accent-bg p { color: var(--color-white); }

/* ========== UTILITIES ========== */
.accent { color: var(--color-primary); font-weight: 700; }
.accent-bg { background: var(--color-primary); color: var(--color-white); }
.text-center { text-align: center; }
.text-small { font-size: 14px; color: var(--color-muted); }
.mt-auto { margin-top: auto; }
.mb-16 { margin-bottom: 16px; }
.mb-24 { margin-bottom: 24px; }
code {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
pre {
  background: var(--bg-secondary);
  padding: 16px 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 14px;
  line-height: 1.5;
  margin-top: 12px;
}
pre code { background: none; padding: 0; }

/* ========== DIAGRAM HELPERS ========== */
.diagram-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin: 24px 0;
}
.diagram-box {
  padding: 14px 24px;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
  min-width: 120px;
}
.diagram-box.accent-bg {
  border-color: var(--color-primary);
}
.diagram-arrow {
  width: 40px;
  height: 2px;
  background: var(--color-light);
  position: relative;
  flex-shrink: 0;
}
.diagram-arrow::after {
  content: '';
  position: absolute;
  right: 0;
  top: -4px;
  border: 5px solid transparent;
  border-left: 6px solid var(--color-light);
}

/* ========== BAR CHART ========== */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bar-label {
  width: 100px;
  font-size: 14px;
  font-weight: 500;
  text-align: right;
  flex-shrink: 0;
}
.bar-track {
  flex: 1;
  height: 28px;
  background: var(--color-divider);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding-left: 8px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  width: var(--value);
  transition: width 0.6s ease;
}
.bar-fill.teal { background: var(--color-teal); }
.bar-fill.orange { background: var(--color-orange); }
.bar-fill.yellow { background: var(--color-yellow); }

/* ========== DONUT CHART ========== */
.donut-chart {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.donut-chart .donut-hole {
  width: 100px;
  height: 100px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

/* ========== TABLE ========== */
.slide table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
  font-size: 16px;
}
.slide th {
  background: var(--bg-secondary);
  font-weight: 700;
  text-align: left;
  padding: 10px 16px;
  border-bottom: 2px solid var(--color-border);
}
.slide td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-divider);
}

/* ========== SPEAKER NOTES ========== */
.notes { display: none; }
.show-notes .notes {
  display: block;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-dark);
  color: var(--color-white);
  padding: 16px 24px;
  font-size: 14px;
  line-height: 1.5;
  max-height: 25vh;
  overflow-y: auto;
  z-index: 200;
}

/* ========== OVERVIEW MODE ========== */
body.overview .deck {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 24px;
  overflow-y: auto;
  height: 100vh;
  width: 100vw;
}
body.overview .slide {
  position: relative;
  top: auto;
  left: auto;
  transform: none;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 */
  display: flex;
  cursor: pointer;
  font-size: 5px; /* Scale down text proportionally */
  --slide-padding: 16px;
  --slide-padding-top: 14px;
  border: 2px solid transparent;
  transition: border-color 0.15s;
}
body.overview .slide.active { border-color: var(--color-primary); }
body.overview .slide:hover { border-color: var(--color-light); }
body.overview .slide * { font-size: inherit; }
body.overview .slide h1 { font-size: 1.8em; }
body.overview .slide .subtitle { font-size: 1.1em; }
body.overview .slide li, body.overview .slide p { font-size: 1em; }
body.overview .slide-counter { display: none; }
body.overview .notes { display: none !important; }

/* ========== PRINT ========== */
@media print {
  body { background: white; overflow: visible; }
  .deck { display: block; }
  .slide {
    position: relative;
    top: auto;
    left: auto;
    transform: none;
    display: flex !important;
    width: 100%;
    height: auto;
    aspect-ratio: 16/9;
    page-break-after: always;
    box-shadow: none;
    border: 1px solid #eee;
    margin-bottom: 0;
  }
  .slide-counter, .notes { display: none !important; }
}
</style>
</head>
<body>

<div class="deck">

<!-- SLIDES GO HERE -->
<!-- Each slide follows this pattern:

<section class="slide cover active">
  <!-- Optional: add your own logo here -->
  <h1>Presentation Title</h1>
  <p class="subtitle">Presenter Name / Date</p>
  <aside class="notes">Speaker notes go here</aside>
</section>

<section class="slide section-break">
  <h1>Section Title</h1>
  <p class="subtitle">Optional subtitle</p>
</section>

<section class="slide content">
  <h1>Slide Title</h1>
  <p class="subtitle">Subtitle</p>
  <ul>
    <li>Bullet point one</li>
    <li>Bullet point two with <strong>bold emphasis</strong></li>
    <li>Bullet with <span class="accent">colored highlight</span></li>
  </ul>
  <aside class="notes">Speaker notes</aside>
</section>

-->

</div>

<div class="slide-counter"></div>

<script>
(function() {
  const deck = document.querySelector('.deck');
  const slides = Array.from(deck.querySelectorAll('.slide'));
  const counter = document.querySelector('.slide-counter');
  let current = 0;
  let isOverview = false;

  function showSlide(n) {
    current = Math.max(0, Math.min(n, slides.length - 1));
    slides.forEach((s, i) => s.classList.toggle('active', i === current));
    counter.textContent = (current + 1) + ' / ' + slides.length;
    window.location.hash = current + 1;
  }

  function toggleOverview() {
    isOverview = !isOverview;
    document.body.classList.toggle('overview', isOverview);
    if (isOverview) {
      slides.forEach(s => s.style.display = 'flex');
    } else {
      showSlide(current);
    }
  }

  function fitScale() {
    if (isOverview) return;
    const sw = window.innerWidth / 1280;
    const sh = window.innerHeight / 720;
    const scale = Math.min(sw, sh, 1.2);
    document.documentElement.style.setProperty('--scale', scale);
  }

  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    if (isOverview && e.key !== 'Escape' && e.key !== 'o' && e.key !== 'O') return;
    switch(e.key) {
      case 'ArrowRight': case 'ArrowDown': case ' ': case 'Enter':
        e.preventDefault(); showSlide(current + 1); break;
      case 'ArrowLeft': case 'ArrowUp': case 'Backspace':
        e.preventDefault(); showSlide(current - 1); break;
      case 'Home': showSlide(0); break;
      case 'End': showSlide(slides.length - 1); break;
      case 'Escape': case 'o': case 'O':
        toggleOverview(); break;
      case 's': case 'S':
        document.body.classList.toggle('show-notes'); break;
      case 'f': case 'F':
        if (!document.fullscreenElement) document.documentElement.requestFullscreen();
        else document.exitFullscreen();
        break;
    }
  });

  // Click navigation in overview
  deck.addEventListener('click', function(e) {
    if (!isOverview) return;
    const slide = e.target.closest('.slide');
    if (slide) {
      current = slides.indexOf(slide);
      toggleOverview();
      showSlide(current);
    }
  });

  // Touch support
  let touchStartX = 0;
  document.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; });
  document.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) {
      dx > 0 ? showSlide(current - 1) : showSlide(current + 1);
    }
  });

  // Init
  fitScale();
  window.addEventListener('resize', fitScale);
  const hash = parseInt(window.location.hash.slice(1));
  showSlide(hash > 0 ? hash - 1 : 0);
})();
</script>
</body>
</html>
```

---

## Keyboard Shortcuts Reference

Include this as a comment at the top of the generated HTML:

```
<!--
  Keyboard: → ↓ Space Enter = Next | ← ↑ Backspace = Prev
  O/Esc = Overview | S = Speaker Notes | F = Fullscreen
  Home/End = First/Last slide | Touch: swipe left/right
-->
```
