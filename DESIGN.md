---
name: Olimazi
description: A personal working lab for showing what one person can build with AI.
colors:
  wall: "#211f1b"
  wall-2: "#2a2722"
  paper: "#f1e9d6"
  paper-2: "#e6dabe"
  kraft: "#c8a878"
  ink: "#1b1812"
  ink-soft: "#4a4436"
  yellow: "#f2c230"
  red: "#c23a2b"
  tape: "rgba(244, 227, 166, .62)"
  stamp: "rgba(27, 24, 18, .78)"
  mint-alt: "#58bd9a"
typography:
  display:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontWeight: 900
  headline:
    fontFamily: "Satoshi, Segoe UI, system-ui, sans-serif"
    fontWeight: 700
  body:
    fontFamily: "Segoe UI, system-ui, sans-serif"
  type:
    fontFamily: "Courier New, Courier, monospace"
  hand:
    fontFamily: "Segoe Print, Ink Free, Bradley Hand, Marker Felt, cursive"
spacing:
  gutter: "28px"
  wrap-max: "1140px"
---

# Design System: Olimazi

Source of truth for tokens is `styles.css` `:root` (updated 2026-08-17 — the mint graph-paper system this file used to document is retired). This file describes what is live; it is not a spec. The Phase 2 spec (type scale, spacing rhythm, three-reds usage, one decorative vocabulary) supersedes it when written.

## Overview

**Creative North Star: "Paste-up collage"** — a dark painted-brick wall with pasted paper sheets, taped photos, torn scraps, typewriter cards, and marker notes. Direction going forward: urban-futuristic, warm — sodium and neon in the photograph, warm amber against cold blue. Editorial layout, not app layout.

## Colors

- **wall / wall-2** — page ground, near-black painted brick.
- **paper / paper-2** — pasted sheets, cream and aged cream.
- **kraft** — kraft-brown scraps.
- **ink / ink-soft** — print ink, headline and body copy.
- **yellow** — taxi / caution-tape yellow. The accent. Stays.
- **red** — FOR-LEASE sign red. Links and marks on paper.
- **tape / stamp** — translucent tape strips and rubber-stamp overlays.
- **mint-alt** — the old brand mint. Defined as a complementary alternate only (`--mint`); it must not appear as an accent on the live site.

**The Existing Tokens Rule.** Use the custom properties in `styles.css`; do not introduce a parallel palette.

## Typography

- **display** — Satoshi Black/Bold (self-hosted `assets/Satoshi-*.otf`). Headlines, stickers, nav.
- **body** — Segoe UI / system sans.
- **type** — Courier New. Typewriter cards and captions.
- **hand** — Segoe Print / Ink Free. Marker notes on the wall.

No webfont dependencies. IBM Plex Mono and Architects Daughter are retired from the main page.

## Banned cues (no-AI-cue rule)

No film grain, no `backdrop-filter`, no glass cards, glow blobs, neon halos, pill CTAs, bento grids, or type wordmarks as the logo. The drawn Olimazi logo is never the URL mark; the type mark is. Removed 2026-08-17: `.grain` overlay and every `backdrop-filter`.

## Structure

- `index.html` — markup and the library manifest JSON only.
- `styles.css` — all styles.
- `site.js` — lightbox and stack viewer.
- `assets/` — the only asset tree. Tear masks and fiber overlays live at `assets/tear-mask-{a,b}.png`, `assets/tear-fiber-{a,b}.png`; sheet edge at `assets/sheet-edge.svg`.

## Secondary pages

`library.html` and `tester.html` still carry the legacy mint / graph-paper styling (own `:root`, Google Fonts IBM Plex Mono + Architects Daughter). They are re-poured in Phase 3; until then their palette is not the brand palette.

## Do's and Don'ts

- **Do** lead with real photographs, screenshots, and the real logo.
- **Do** preserve keyboard controls, visible focus, reduced-motion behavior, semantic structure, and alt text.
- **Don't** turn Olimazi into a tools platform, a SaaS sales page, or a pitch-led AI landing page.
- **Don't** introduce new colors, fonts, dependencies, or decorative treatments outside a written spec.
