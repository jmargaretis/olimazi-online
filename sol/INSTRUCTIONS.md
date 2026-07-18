# SOL work packet — active

**Packet:** #5 · issued 2026-07-18 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md` — including the required REPORT.md format, which
governs your report (this packet defines no report outline of its own).

Owner reviewed packet #4 live and rejected the detail-tile approach. This packet
corrects course. Read `PRODUCT.md` and `DESIGN.md` first; stay inside the locked
framing and existing tokens.

## Owner's verdict on packet #4 (the why)

- The standalone "Details, when they're ready" section **should not exist**. Detail
  belongs INSIDE each section, as slides — not as a separate tile block.
- Sections 2 and 3 are **broken up too much** — the Context/Constraints/Handoff/Record
  tile grid fragments the method instead of presenting it.
- The owner's selected images were missing (they were out of scope for #4; they are
  in scope now — already committed to `olimazi-assets/`).
- The owner wants detail delivered as a **slide presentation he can drag**.

## Packet #5 scope

### 1. Remove the detail-tile mechanic entirely
- Delete the "Details, when they're ready" section (the three owner-content-slot
  placeholder frames) completely.
- Delete the Section 2 detail-tile grid (Context / Constraints / Handoff / Record
  tiles). Their copy moves into slides per §2.
- No `<details>`-based detail tiles remain anywhere. (The pre-existing
  `process-notes` element may stay if it still fits the new layout naturally.)

### 2. Draggable slide decks (the replacement mechanic)
- Extend the existing carousel pattern (as used by Method Effects) with
  **pointer/touch drag**: mouse-drag and swipe advance slides, with the existing
  prev/next buttons and Left/Right arrow keys kept for accessibility. No
  dependencies — vanilla JS, Pointer Events.
- Detail now lives as **slides inside each section's deck**: a section leads with its
  presentation, and deeper context is further slides in the same deck, not a separate
  block. Method copy (context-first / constraints / handoff / record) becomes slides
  in the Section 2 deck.
- Keep each slide's content a single clearly-commented block in `index.html` so the
  owner can drop in future content the same way as before.

### 3. Integrate the owner's approved images (already in `olimazi-assets/`)
Place the new images as slides in the appropriate decks, with captions drawn from the
owner's notes below. Links must be rendered as named links, exactly as given.

**Method Effects deck (10 new):**
- `method-rs3-cad-render.png` — CAD render by [Kevin Grant (@the_kevinator)](https://www.instagram.com/the_kevinator/) for the Rs3 splitter: a true one-off, concept to reality — a single part crossing the front fascia for mounting stability with the most minimal application vs competitors.
- `method-multipiece-sketch.jpg` — An advanced sketch from the owner's rough render, by [Kevin Grant (@the_kevinator)](https://www.instagram.com/the_kevinator/). Early planning; didn't make launch. Multipiece design for one-of-a-kind design flow; 3-piece construction would reduce shipping costs.
- `method-v1-v2-comparison.png` — Dimension layout of a support mounting strut for the S3 splitter ([Kevin Grant](https://www.instagram.com/the_kevinator/)); added integrity to the center aero.
- `method-v1-aero-start.jpg` — The beginnings of the V1/V2 comparison: added integrity to center aero, increasing sturdiness and longevity. Designed to modify only the existing aftermarket part, never the OEM fascia.
- `method-rubber-contact-points.jpg` — 60-durometer rubber contact points protecting painted surfaces; single bolt with a cotter-pin fail-safe.
- `method-abs-coating.jpg` — Baked custom finishing to keep ABS part integrity, via SoCal vendor [Shmaze](https://shmaze.com/) — an engaging group that works with anyone, big outfit or small start-up.
- `method-japan-first-order.jpg` — The logistics: 8 advance purchases to Japan — first order for the brand, via [Hitotsuyama GmbH shop](https://hitotsuyamagmbh.shop-pro.jp/).
- `method-japan-order-support.png` — Supporting shot for the Japan first order (place adjacent to it, or merge into one slide — your judgment).
- `method-promo-campaign.jpg` — From an ad campaign testing a new logo.
- `method-workshop-detail.jpg` — No caption; place where it fits visually.

**Mind/Practice deck (2 new, attach to the existing cooking/practice material):**
- `mind-ribeye-process.jpg` — Cooking process shot, following [this YouTube video](https://youtu.be/lVcTvHTn6Dw): "funny guy to watch; the drying/brining was definitely a home run!" Precedes the result shot.
- `mind-ribeye-result.jpg` — "Was a bit harder than I wanted it to be — should've known a bone-in ribeye is much harder to get even temps."
- These two photos were resized from phone originals; **verify their orientation
  renders correctly** and flag in REPORT.md if either appears rotated.

**Removals (owner's cuts):** remove `method-cad-iso.png`, `method-hero-1.jpg`, and
`method-hero-2.jpg` from the page AND delete the files from `olimazi-assets/`.

### 4. Locked — do not touch
- The bougatsa and Eau d'Ombre blocks: owner's words are "I don't want any changes to
  how this was built. Leave as is in the current state."
- `method-splitter-mural.jpg`, `method-splitter-product.jpg`, `method-garage-front.jpg`,
  `method-hero-3.jpg`, `method-hero-4.jpg`, and the three schedule-e dashboard shots
  stay on the site (captions may move into slides where their sections convert).
- Tokens, framing, contact closer, navigation behavior.

## Out of scope
- New dependencies, payment/download links, this file.
- Any image not named above (more are banked owner-side for future packets).
