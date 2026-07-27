# Work order — ink-bleed / splatter edges on the work-project tiles

## Goal

The two carousels in the "main work" section currently render each image as a clean
rounded rectangle with a soft drop shadow. The reference look (reckon.house) instead has
the image **bleed outward past its own edge in a tight irregular ink-splatter**, so the
photo dissolves into the page rather than stopping at a crisp border.

Build that. This is an exploration — if it can't be done cleanly, say so and explain why
rather than shipping something approximate.

## Where

**Repo:** `C:\Users\jmarg\work\olimazi-online` (never read or write anything under
`C:\Users\jmarg\OneDrive\`).

- `index.html:485-500` — the tile framing CSS block (`/* ---- floating-plate tile framing ---- */`)
- `index.html:364-385` — base carousel CSS
- `index.html:903-1000` — Method Effects carousel markup (12 slides)
- `index.html:1023-1035` — Rental Manager carousel markup (4 slides)

Serve with the repo's existing local server and view at `http://localhost:8399/`.

## How the reference does it

Each reckon.house tile is a `div.blot-ink` holding an **oversized copy of the same image**
clipped by an irregular ink-blot alpha mask (`-webkit-mask-image` / `mask-image` with a
blot PNG or SVG), sitting *behind* the main `img`. The mask's ragged edge is what produces
the splatter; the inner image stays rectangular with a large border-radius.

## The one real constraint that makes this non-obvious

CSS cannot read a value out of an `img`'s `src`, so a mask layer that must show *that
tile's own image* needs the URL passed in per tile. The supported way to do that here is
an **inline custom property on the figure**:

```html
<figure class="carousel-slide" data-slide style="--bleed:url(olimazi-assets/method-splitter-product.jpg)">
```

This is safe. See the next section for why — read it before touching markup.

## HARD CONSTRAINT — the content build system

`tools/render_section.py` re-renders parts of `index.html` from Markdown in the vault. It
splits the marked region with:

```python
TOKEN_RE = re.compile(r"(<[^>]+>|['\"])")
```

Every non-tag, non-quote, non-blank token is a **text slot**, zipped positionally against
a hardcoded list in `SECTION_SPECS["main-work"]`. If the number of text slots changes, the
build raises `RenderError: section structure changed`.

What this means:

- **Adding or changing an ATTRIBUTE is safe** — attributes live inside a `<...>` tag token
  and are never text slots. `style="--bleed:url(...)"`, `class`, `data-*` are all fine.
- **Adding or removing visible TEXT is not safe** without also editing the spec list.
- **Adding a new element that contains text is not safe.** An empty element
  (e.g. `<div class="blot-ink"></div>`) contributes no text token and is fine.

Prefer a solution that adds only attributes and empty elements. If you genuinely must add
text, update `SECTION_SPECS["main-work"]` in `tools/render_section.py` in the same change,
adding a `None` entry at the matching position.

**Proof of correctness — required:**

```
python tools\render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\main-work.md" --mode build
```

must print `changed fields: none`. That command only READS from OneDrive — that read is
expected and allowed. Do not write anything there.

## Performance constraint — this already caused a crash once

An earlier version of this framing used an infinite CSS `animation` on `.carousel-media`
plus `will-change: transform` on every slide. In grid mode ("View all" opens all 12 Method
tiles at once) that put 12 large images on 12 permanent GPU compositor layers, on top of a
fixed full-viewport SVG background and a `backdrop-filter: blur(12px)` nav. Switching
color theme repainted all of it and the machine nearly locked up; one tile rendered blank.

So:

- **No infinite animations.** No `will-change` outside an active drag.
- Masks and filters are expensive. If the bleed costs a `filter: blur()` per tile, apply it
  to the **single visible tile only** — in grid mode (`.work-project-carousel.is-grid`,
  12 tiles simultaneously) either drop the effect or use a pre-baked static mask with no filter.
- Test the theme toggle **while grid mode is open** before reporting done.

Also note: do **not** add `loading="lazy"` to these images. Inactive slides are
`display:none`, so lazy images never load and the tile renders blank on reveal. This was
tried and reverted.

## Also in scope

The tilt was removed at the owner's request — tiles are now flat. Keep them flat.
The drop shadow stays; it's wanted. Do not reintroduce rotation or perpetual motion.

## Deliverable

If the effect works: the CSS/markup change, plus a one-paragraph note on the technique and
its cost. If it doesn't work cleanly: a written explanation of what you tried, what broke,
and what the effect would actually require (e.g. hand-authored per-image mask assets).

Do not commit, do not push.

## Scope of "done" — read this before reporting

**You cannot close out the performance constraint yourself.** The visual result and the
grid-mode theme-toggle behavior require eyes on a live browser, and the last version of
this exact effect was reported working and then nearly locked the machine up. Do not
repeat that.

So:

- **Build the effect and stop.** Report it as *built, pending visual verification* — never
  as done.
- **Do** run and report every check you can prove mechanically:
  - `python tools\render_section.py --content "C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\main-work.md" --mode build`
    prints `changed fields: none` (read-only against OneDrive; no writes there).
  - No infinite `animation` anywhere in the changed CSS.
  - No `will-change` outside `.carousel.is-dragging`.
  - No `loading="lazy"` added to any carousel image.
  - Text-slot count unchanged (attributes and empty elements only), or
    `SECTION_SPECS["main-work"]` updated with matching `None` entries in the same change.
- **Hand back explicitly**, in the final report, the list of things a human must verify in
  the browser at `http://localhost:8399/`:
  1. The bleed actually reads as a tight ink splatter, not a blur halo.
  2. Open Method Effects "View all" grid mode (12 tiles) and toggle the color theme —
     watch for lockup, repaint stalls, or a blank tile.
  3. Single-slide view renders correctly on first reveal of a previously-inactive slide.
- State the **per-tile cost** of your technique plainly: how many mask layers, whether any
  `filter: blur()` runs, and what happens to that cost when 12 tiles are visible at once.
  If the effect needs a filter per tile, say so and say what you did about grid mode.
