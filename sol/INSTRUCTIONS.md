# SOL work packet — active

**Packet:** #6 · issued 2026-07-18 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

Owner reviewed packet #5 live. The deck mechanic stays; this packet corrects the
items below. Read `PRODUCT.md` and `DESIGN.md` first; locked framing and tokens.

## Packet #6 scope

### 1. Drag becomes touch-only
Keep swipe on touch devices; remove mouse dragging on desktop entirely (check
`event.pointerType` — only `"touch"` engages the drag path). Buttons and arrow keys
remain everywhere. Remove the `cursor: grab` styling on desktop.

### 2. Method Effects deck — one reorder + captions
Keep the existing slide order EXCEPT: move `method-v1-v2-comparison.png` (currently
slide 04) directly in front of `method-multipiece-sketch.jpg` (currently slide 03).
No other order changes — the owner will direct further reordering in later packets.

**Caption fix (owner's note was dropped in #5):** the tooling-buck slide caption must
carry the owner's words: "[Akra Plastics](https://akra-plastics.com/) — SoCal
manufacturer who were extremely helpful in dealing with me as a small player. Awesome
outfit and easy to work with. This was my aluminum 'Buck' for my RS3 splitter."
Named link required.

Note: `method-rs3-cad-render.png`, `method-japan-order-support.png`, and
`method-multipiece-sketch.jpg` were re-cropped planning-side (phone chrome removed)
and are already committed — verify they render well at deck size; no further edits.

### 3. Schedule E project (desktop) — copy into slides
The prose outside the deck bleeds too long on desktop. Cut it to a short lead-in;
the detail moves into the slide captions. Replace the three generic dashboard captions
with the owner's words (light tightening allowed, meaning intact):

- `schedule-e-summary.jpg` — "While doing work with business tax prep, I serviced a
  client who needed maintenance for a partnership group in the real estate industry
  (Form 8825 activity). Applied that to my real-world active management of a couple
  rental properties — an easy-to-use system with activity sorted in real time, ready
  to pass off to an accountant or bookkeeper."
- `schedule-e-expenses.jpg` — "Running list of attention items, coded, works with an
  engine under the hood back and forth. Instead of diving deep into an Excel file —
  easier to visualize for most."
- `schedule-e-open-items.jpg` — "System considers PY activity, creating an expected
  drip of information or truth going forward. Built with alerts for what might be
  missing and for deadlines."

### 4. Section 3 flow
The break between "Current state of mind" and the small-subjects material reads as
two separate sections. Remove the hard rule/page-break feel and make it flow as one;
add a subtle faded downward arrow (existing tokens, low opacity, respects
reduced-motion) leading the eye to the cologne and bougatsa blocks.

### 5. Ribeye — off the main page
Remove the ribeye deck from `index.html` entirely. Its two images move to the
library page (see §6). The main page's small-subjects area keeps only the cologne
and bougatsa blocks (locked, untouched).

### 6. New page: `library.html` (minimal)
A simple secondary page matching the site's tokens/typography/theme toggle, linked
from the end of Section 3 (something like "More in the library →") and from the
footer if one exists. Purpose line at top: an archive of ongoing learning material —
things worth keeping that aren't headline work. No CMS, no dependencies; each entry
one commented block, same editing pattern as the decks. **Presentation: entry
thumbnails mimic the cologne/bougatsa blocks on the main page — same thumb size,
frame treatment, and caption pattern.** Entries (images already in
`olimazi-assets/`), owner's captions:

- `mind-ribeye-process.jpg` — Cooking process shot, following
  [this YouTube video](https://youtu.be/lVcTvHTn6Dw): "funny guy to watch; the
  drying/brining was definitely a home run!" (Keep the orientation correction it
  had on the main page.)
- `mind-ribeye-result.jpg` — "Was a bit harder than I wanted it to be — should've
  known a bone-in ribeye is much harder to get even temps."

- `library-67-bug.jpg` — Personal-use '67 classic Bug, restored by the owner —
  shared simply because it's worth sharing.
- `library-art-sketch.jpg` — A sample of the owner's own art.
- `library-art-vector.jpg` — Same art thread: taken from sketch to vector the
  old-school way.
- `library-brothers-truck.jpg` — "My brother's truck." More pictures and a
  parts-added detail coming later.
- `library-restaurant-01.jpg` — From restaurant operations years: represents chaos
  and the ability to confront and manage high-stress environments.
- `library-restaurant-02.jpg` — Restaurant operations, held for future context.

Restaurant items live ONLY here — still zero restaurant mention on `index.html`.
Verify orientation of all six (several are phone photos); flag any that render
sideways in REPORT.md.

## Out of scope
- Any change to the bougatsa / Eau d'Ombre blocks (locked).
- New dependencies, payment/download links, this file.
- Any image not named above.
