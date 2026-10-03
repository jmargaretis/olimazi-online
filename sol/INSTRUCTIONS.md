# Codex work packet — active

**Packet:** #11 · issued 2026-07-21 · authored by Claude (planning side)
**Packet #10 (tester page): ACCEPTED** — tester.html live at olimazi.online/tester.html.
**Numbering note:** "Trace the transaction" (reserved as #11 in the #10 notes) shifts
to packet #12 — this small gallery packet takes #11 since it ships first.
**Protocol:** AGENTS.md (Codex operating contract); report in required REPORT.md format.

## Packet #11 scope — Rental Manager carousel: Organizer + Management slides

The tracker product now has four surfaces; the site's Rental Manager section only
shows the old summary view. Add the two new product pages to the existing
carousel in index.html.

### 1. New assets (already in olimazi-assets/ — do NOT regenerate)
- `rental-manager-organizer.png` (952×1190) — the Client Organizer page: filing
  flags with confirmed/unconfirmed chips, extension callout, owner/preparer cards.
- `rental-manager-management.png` (952×1190) — the Management page: issue board
  (AC repair sample case), documents table with expiry badge.
Both are framed fixture screenshots (fake "12 Sample Street" data only — same
family as `rental-manager-dashboard.png`).

### 2. Carousel slides (index.html, Rental Manager section)
Add two `figure.carousel-slide` entries after the existing summary/dashboard
slides, matching the existing slide markup pattern exactly (img.carousel-media +
figcaption.carousel-caption with a <b> lead):
- **Organizer slide** — caption lead "Client Organizer". Body (match the site's
  first-person operator voice, 2–3 sentences): the trust layer — the page shows
  what the workbook believes (addresses, contacts, filing status) so the owner
  confirms it before trusting the numbers; built in the spirit of a CPA client
  organizer, ready to hand to a preparer.
- **Management slide** — caption lead "Management view". Body: the day-to-day side
  of the same records — tenant issues, vendors, and documents with expiry
  warnings, kept next to the books instead of in a separate app.
If the carousel uses dot/arrow controls driven by slide count, confirm they pick
up the new slides automatically; adjust only what the existing mechanism requires.

### 3. Alt text
Meaningful alts: "Client Organizer page — filing flags and preparer card, sample
property" / "Management page — tenant issue board and documents, sample property".

## Out of scope
Any copy change outside the two new captions (hero copy is a separate pending
decision); tester.html; any other section; image regeneration; new dependencies;
this file.

## Acceptance test (results → REPORT.md)
1. index.html contains exactly two new carousel-slide figures referencing the two
   new PNGs, matching existing markup pattern; git diff confined to the carousel
   block.
2. Slide count/controls work with the added slides (inspect the carousel JS/CSS
   mechanism and state how it handles the count).
3. Alt text present on both images.
4. No real personal data in captions (fixture/sample framing only).
5. Serve locally (python -m http.server) and confirm the section renders with the
   new slides reachable via the carousel controls.
You cannot commit (read-only .git — expected); leave working-tree changes for
Claude to verify, John to accept, then commit/push.
