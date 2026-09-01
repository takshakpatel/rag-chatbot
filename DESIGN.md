# Design

<!-- impeccable:design-schema 1 -->

## Surface

`frontend/src/app/page.tsx` + components — the Lumen chat UI (the "Lumen" glassmorphism surface).

## Mode

Operate. The visitor completes a task: uploading documents and asking questions that return cited, grounded answers. Scanability, trust, and precision outrank expression; brand lives in precise details.

## Visual World

Modern SaaS Glassmorphism (the "Lumen" Glass Studio). Panels are frosted glass floating over a slow-drifting aurora field. The interface is a luminous workspace: translucent cards (`backdrop-blur` + saturate), hairline inner-top gloss, soft outer glow, and large rounded radii. A self-owned violet→cyan→green brand gradient carries primary actions and identity. Depth/abyssal metaphor is retired in favor of a clean, airy, app-like surface.

## Palette

Dark-first with a full light re-theme. The ground is a soft aurora (`--bg-base` + four colored glow orbs) whose color sits *behind* the glass so the blur reads. Glass fills are translucent white (dark: `white/6`–`10`; light: `white/42`–`60`) with an inner top highlight and hairline border. Semantic accents stay honest: `thermo` cyan for links/active, `verified` green for success, `refusal` amber for turn-downs, `hold` violet for retrieval. The brand gradient (`bg-brand`, violet `#8b7cf6` → cyan `#4cc9f0` → green `#5ae0a0`) is reserved for the product mark, send/upload buttons, and reply dots.

| Role | Token | Value (dark) |
|------|-------|------|
| Aurora ground | `--bg-base` | `#0b1020` |
| Glass fill | `--glass-bg` | `rgba(255,255,255,0.06)` |
| Raised glass | `--glass-bg-strong` | `rgba(255,255,255,0.10)` |
| Hairline line | `--glass-line` | `rgba(255,255,255,0.12)` |
| Inner gloss | `--glass-gloss` | `rgba(255,255,255,0.16)` |
| Brand start | — | `#8b7cf6` |
| Brand end | — | `#5ae0a0` |
| Active | `thermo` | `#4cc9f0` |
| Verified | `verified` | `#5ae0a0` |
| Refusal | `refusal` | `#f4a261` |
| Hold / retrieval | `hold` | `#a78bfa` |
| Prose | `ink` | `#c9e0ee` |
| Dim prose | `ink-dim` | `#8aa6bd` |

## Theme

Dark-first with a full light re-theme (`<html class="theme-light">`), toggled from the header and persisted in `localStorage` (key `rag-deepdive-theme`, applied pre-paint to avoid flash). All color tokens are CSS variables consumed by Tailwind via `rgb(var(--*-rgb) / <alpha-value>)`, so opacity modifiers work and every component re-themes without re-editing. Glass variables (`--glass-*`, `--orb-*`, `--bg-base`) are re-declared per theme: light uses pastel orbs and brighter/warmer white glass. The aurora drift animation is disabled under `prefers-reduced-motion`.

## Typography

| Role | Face | Usage |
|------|------|-------|
| Body prose | Inter (400/500) | Answer copy, prompts, labels |
| Measurements | IBM Plex Mono (400/500/600) | Readout digits, state tags, citation indices. `font-variant-numeric: tabular-nums`. |

## Layout

Single fluid column centered in a constrained gutter. Header is a floating glass bar (brand mark left, online status + theme toggle right). Below it a glass upload card, then the main chat glass panel that fills remaining height with three zones: scrollable messages, readout tile row, and a floating glass input dock. All panels share the rounded-2xl glass language.

## Components

### BrandMark
A rounded `bg-brand` tile with a white teardrop-diamond mark — the product's only use of the gradient as a filled shape.

### SourcePins (citations)
Inline rounded citation chips (dot + two-digit index + filename). Clicking expands a glass panel with the exact source snippet, chunk index, and full path. Image sources carry an `IMG` chip.

### Readouts
Responsive row of glass metric tiles (State, Sources hit, Candidates, Latency). Digits use IBM Plex Mono with `tabular-nums`; a `digit-snap` animation acknowledges each settled value. A state dot recolor carries meaning without being color-only.

### MessageBubble
User messages are a right-aligned `bg-brand` pill with white text. Assistant answers are a glass tile under a small gradient reply mark, with a `glass-tile` body; refusals tint the tile `refusal`. Citations render as `SourcePins`.

### IngestPanel
A glass upload card: dashed dropzone + brand "Upload" button + removable file chips + inline error line. Logic unchanged (multipart upload, dedupe by name+size).

### Chat
Orchestrates the conversation: empty state → dragging → VERIFIED/TURN readout. Measures latency client-side, ticks the readout during retrieval, maps sources for citation chips.

## States

- EMPTY: centered brand drop mark + "Ask anything about your documents".
- LOADING: pulsing brand dot + "Retrieving · reading your sources" with ticking readout.
- ANSWERED: green state dot, glass response tile, source pins populated.
- REFUSED: amber state dot + amber response text.

## Browser Surfaces

- `::selection`: thermocline cyan on the darker ink.
- `input, textarea caret-color`: thermocline cyan.
- Scrollbar: translucent thumb over the aurora; thermocline hover.
- Focus rings: 2px solid thermocline, 2px offset.

## Signature Interaction

1. **Frosted glass panels**: every surface is translucent over the drifting aurora, so the background is always faintly present and layered.
2. **The brand gradient as guarded identity**: reserved for the mark, send/upload, and reply dots — never decor.
3. **Live measured readouts**: metric tiles tick during retrieval and settle into a final readout.

## Anti-patterns Avoided

- No emoji; all icons are drawn SVG in one consistent stroke weight.
- No gradient *text*; the gradient only fills guarded shapes.
- Glass is a real layered surface over a colored field, never blurring flat color.
- No decorative left-borders or hard offset shadows; depth comes from inner gloss + soft glow.
- Muted text tinted from the ink hue (`ink-dim`), not neutral gray.
- Inter retained as Operate body grotesk per craft-floor exception; IBM Plex Mono is the distinctive measurement face.

## Contract

Seed: `d6159bf5`. User-picked challenger (competitive alternate from direction roll). Build is code-led. Major direction pivoted on request from the Deep-Dive Depth Profile to modern glassmorphism ("Glass Studio"); the depth ruler and abyssal surfaces were retired, the citation component renamed `DepthPins` → `SourcePins`. The product is now branded **Lumen**. Contract emitted in root layout HTML comment.
