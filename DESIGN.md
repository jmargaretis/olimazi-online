---
name: Olimazi
description: A personal working lab for showing what one person can build with AI.
colors:
  wall: "#16202A"
  wall-2: "#1C2731"
  paper: "#DDE3E6"
  paper-2: "#D3DADE"
  kraft: "#B5C0C8"
  ink: "#16202A"
  ink-soft: "#4E5C68"
  plate: "#E6EBEE"
  plate-2: "#D8DFE3"
  coral: "#C23A2B"
  coral-bright: "#FF4A2E"
  tape: "rgba(220, 228, 232, .55)"
  stamp: "rgba(22, 32, 42, .78)"
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

Source of truth for tokens is `styles.css` `:root` (branch `steel`, 2026-08-17). This file describes what is live; it is not a spec. Basis: `Claude OS/projects/olimazi-landing/plans/BASIS-steel-restyle-2026-08-17.md`.

## Overview

**Creative North Star: "Slate & Red — machined editorial."** Grey-slate grounds, flat plates, 1px hairlines, 3px ink rules, square-cut photo thumbs with shallow depth. Nothing is rotated, taped, or torn. Red is an accent for one element per viewport. Warmth comes from the photographs (sodium light, asphalt, mural), not from the palette. Editorial layout, not app layout. The old paste-up collage (tilt, tape, torn scraps, fanned stacks) is retired.

## Colors

- **wall / wall-2** — page ground, ink-slate. Hero, 02, contact, footer.
- **paper / paper-2** — slate sheets, 01 and 03. Straight edges with a 1px hairline top and bottom.
- **kraft** — the hairline colour and the second notepad tone. Also the offset card behind each library stack.
- **ink / ink-soft** — text on paper. Body `ink-soft` on `paper` is 5.3:1.
- **plate / plate-2** — flat matte plates: typewriter cards, vault note, sticker and tag fills, thumb mounts.
- **coral** (`#C23A2B`) — the accent on light surfaces: sign red, links, section numerals, FOR LEASE, the mono labels above cards. Large type and marks only; fails contrast as body text.
- **coral-bright** (`#FF4A2E`) — the accent on dark surfaces: focus ring, selection, "aided by Ai?", the "NO. n" ledger numbers on the wall.
- **tape / stamp** — legacy translucent tokens. Tape is `display: none` on the live page.
- `--yellow`, `--red`, `--mint` are aliases that resolve to the two accent tokens. Do not add a third accent. Yellow and mint are gone.

**The Existing Tokens Rule.** Use the custom properties in `styles.css`; do not introduce a parallel palette. `--coral` and `--coral-bright` are the only accent. The slate is grey, never blue.

## Anti-blue/orange rules

Blue/orange happens when a saturated cool fill sits next to a saturated warm fill in equal amounts. Every rule below blocks that.

1. **Ratio 70 / 25 / 5.** Slate paper + ink-slate wall = 70. Dim text, rules, tape = 25. Coral = 5. Coral is never a surface.
2. **Coral never touches slate ground directly as a fill.** Coral appears as text on ink (`#16202A`), as text on slate paper, or as a thin rule. No coral buttons on `#DDE3E6`. No coral panels.
3. **The slate is grey, not blue.** `#DDE3E6` and `#16202A` are the only grounds. No `#8A9BA8` Nano blue, no gradients that push toward blue, no cool photo tints. Photo backdrops stay `grayscale(.5)` at 12 % like today.
4. **One coral per viewport.** At any scroll position at most one coral element carries the eye (a numeral, a link, a headline word, a FOR LEASE word). If two show, one becomes ink.
5. **Warmth comes from the photographs**, not from the palette (sodium light, asphalt, mural). This is the "urban-futuristic, warm" note from DESIGN.md.
6. **Kill test:** screenshot every section, desaturate it 100 %. If the layout still reads, coral is doing its job as accent, not as colour-blocking.

## Elements

- **Tilt** — none. `.r-l1…r-r3` resolve to 0°. Grid-true everywhere.
- **Cards** (typewriter cards, vault note) — `plate` fill, 1px `kraft` hairline, 3px `ink` rule on top, no shadow. Margin scrawl is a mono coral label above the text.
- **Thumbs / tiles** (Method pile, RM shots, library stacks) — square-cut image inside a 6px `plate` mount with a 1px hairline; shallow drop shadow for depth; hover lifts 3px and turns the hairline coral. Count badge square. Captions mono. Library stacks show one straight offset card behind, never a fan.
- **Notepads** (the five in 02) — a ledger: one hairline-ruled list on the wall, two-column grid (mono coral-bright "NO. n" + system sans body). No tabs, no clip-path.
- **Sheets** (01, 03) — straight edge, 1px hairline.
- **Marquee** — ink band, paper hairlines, paper text; still crawls; level.
- **Sign CTA** — ink plate, paper kicker, coral word.
- **Stickers** (nav, contact) — 2px radius, 1px border, no shadow; primary = ink fill.
- **Hand / marker font** — mono at small size for scrawls, stack labels, spray line. Marker survives only on the hero "aided by Ai?" — coral.
- **Section 03 backdrop** — faded photo, same treatment as 01 and 02. The vault-graph SVG is gone.

## Typography

- **display** — Satoshi Black/Bold (self-hosted `assets/Satoshi-*.otf`). Headlines, stickers, nav.
- **body** — Segoe UI / system sans.
- **type** — Courier New. Typewriter cards, captions, labels, numerals.
- **hand** — Segoe Print / Ink Free. Only the hero "aided by Ai?".

No webfont dependencies. IBM Plex Mono and Architects Daughter are retired from every page.

## Banned cues (no-AI-cue rule)

No film grain, no `backdrop-filter`, no glass cards, glow blobs, neon halos, pill CTAs, bento grids, or type wordmarks as the logo. The drawn Olimazi logo is never the URL mark; the type mark is — type mark only, never the drawn logo. No tilt, no tape, no torn edges. Removed 2026-08-17: `.grain` overlay and every `backdrop-filter`.

## Structure

- `index.html` — markup. The library manifest moves out to `library.json`.
- `styles.css` — all styles. `:root` tokens at top; the "STEEL RESTYLE" blocks at the end override the paste-up treatments (to be folded into the base rules in the consolidate pass).
- `site.js` — lightbox, stack viewer, library loader.
- `assets/` — the only asset tree. Tear masks and fiber overlays (`assets/tear-*.png`, `assets/sheet-edge.svg`) are no longer referenced by the live rules.

## Library

The library stacks on the home page and on `library.html` render from one file, `library.json` at the repo root. See `LIBRARY-HOWTO.md`.

- `front: true` on exactly two stacks — those two show on the home page, in file order.
- `retired: true` on an item — hidden on both pages, kept in the file as archive. Delete the line to remove it for real.
- First non-retired item in a stack is its cover thumb.
- Adding a post = add an item object + drop the image in `assets/`. Rotate = edit `library.json`, commit, push.

## Secondary pages

`tester.html` carries the same tokens as `styles.css :root` in its own `<style>` (self-hosted Satoshi, Courier for mono; no Google Fonts, no theme toggle, no graph paper). `library.html` is re-poured from `library.json` with `library.css`, which imports `styles.css` and has no `:root` of its own.

## Do's and Don'ts

- **Do** lead with real photographs, screenshots, and the real logo.
- **Do** preserve keyboard controls, visible focus, reduced-motion behavior, semantic structure, and alt text.
- **Don't** turn Olimazi into a tools platform, a SaaS sales page, or a pitch-led AI landing page.
- **Don't** introduce new colors, fonts, dependencies, or decorative treatments outside a written spec.
- **Don't** tilt, tape, or tear anything. Don't put coral on a surface.
