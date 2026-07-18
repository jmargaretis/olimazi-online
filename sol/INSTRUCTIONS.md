# SOL work packet — active

**Packet:** #7 · issued 2026-07-18 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

Owner-directed revision from a full slide-order review plus library functionality
alignment. Read `PRODUCT.md` and `DESIGN.md` first; locked framing and tokens.

## Packet #7 scope

### 1. Method Effects deck — owner's exact order (16 → 14 slides)
Rebuild the deck in exactly this sequence:

1. method-splitter-product.jpg
2. method-promo-campaign.jpg
3. method-rs3-cad-render.png
4. method-v1-aero-start.jpg
5. method-v1-v2-comparison.png
6. method-rubber-contact-points.jpg
7. method-multipiece-sketch.jpg
8. method-abs-coating.jpg
9. method-tooling-buck.jpg
10. method-garage-front.jpg
11. method-splitter-mural.jpg
12. method-japan-first-order.jpg
13. method-japan-order-support.png
14. method-hero-3.jpg

**Removed by the owner:** `method-workshop-detail.jpg` and `method-hero-4.jpg` —
remove both slides AND delete both asset files from `olimazi-assets/`.

### 2. Caption corrections (owner's words)
- **method-abs-coating.jpg** — current caption describes coating; the photo is a
  bracing jig. Replace body with the owner's wording: "Custom solution to brace aero
  parts, maintaining form as the parts 'baked' to cure paint." Keep the vendor credit
  as a short trailing sentence with the named link:
  "Finishing by So-Cal vendor [Shmaze](https://shmaze.com/)."
- **method-japan-order-support.png** — add the owner's line "Teaser post before
  launch" as the caption's bold lead (the `<b>` element), keeping the existing
  descriptive text after it.

### 3. So-Cal spelling audit (site-wide)
Replace every "SoCal"/"SOCAL" with "So-Cal" across `index.html` and `library.html`
(the owner finds "SoCal" reads like a typo for "social"). Do not change the URLs,
only display text.

### 4. Library entries — cologne/bougatsa functionality
Rework every library entry to match the main page's cologne/bougatsa mechanic:
- ONE thumbnail per entry, with an "Open notes →" action that opens a native
  `<dialog>` (same pattern as the main page's "Open notes and sources →").
- Multiple images for one subject live INSIDE the dialog, not as separate tiles:
  the two ribeye shots collapse into a single "Ribeye" entry — process shot as the
  tile thumb, result shot + both quotes inside the dialog.
- Thin entries (truck, art, restaurant) follow the SAME structure with short
  dialogs — structure is uniform even when content is light.
- Entry count after rework: 7 (ribeye, '67 Bug, art sketch, art vector, brother's
  truck, restaurant 01, restaurant 02). If the two art entries read better as one
  "Art thread" entry (sketch thumb, vector inside the dialog), you may propose that
  in REPORT.md — do not implement without asking.

### 5. Main-page cologne/bougatsa card form
Match the cologne and bougatsa cards' outer form (frame, corner treatment, thumb
sizing) to the standard card view used on the library page, resolving the current
rounded-vs-squared corner mismatch. Copy, images, captions, and dialog contents of
these two blocks stay EXACTLY as they are — this is a container-styling change only.

## Out of scope
- Fonts/typography (separate decision in progress — do not touch font stacks).
- Any content change to the cologne/bougatsa copy or dialogs.
- New dependencies, payment/download links, this file.
