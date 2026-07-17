# SOL work packet — active

**Packet:** #1 · issued 2026-07-17 · authored by Claude (planning side)
**Trigger:** the owner prompted you to "check GitHub for instructions" — this file is those instructions.
**Authority:** you may change files directly, but ONLY within the scope listed below. Anything outside scope: do not change it — write the idea as a proposal in `sol/REPORT.md` instead.

## How this protocol works (applies to every future packet)

1. `sol/INSTRUCTIONS.md` always holds the single active packet. Execute it, commit your work to `main`, then overwrite `sol/REPORT.md` with your completion report.
2. Your report must contain: what you changed (file list), the preview URL, anything you skipped and why, and any out-of-scope proposals.
3. Never expand your own scope. Never delete or rewrite this file — the planning side overwrites it when the next packet is issued (git history preserves old packets).
4. One packet at a time. If instructions are ambiguous, choose the conservative reading and note the ambiguity in your report.

## Packet #1 scope

### 1. Codify the protocol
Create `AGENTS.md` at the repo root describing the working mode above (trigger phrase → read `sol/INSTRUCTIONS.md` → execute within scope → commit → write `sol/REPORT.md`; direct-change authority only within a packet's scope; out-of-scope = proposal in REPORT.md). Keep it short — it's an operating contract, not documentation.

### 2. Site purpose (carries over an unanswered question)
Frame the site as **presenting a concept** — Olimazi as a personal brand exploring what one person can build with AI — rather than selling a product or offering a tools platform. This is the standing recommendation; the owner has not formally locked it. If this framing materially changes copy you'd otherwise write, note it in REPORT.md so it can be confirmed or reversed next packet.

### 3. Product section: the tracker
Add a section (or page, your judgment) to the site presenting the first concrete Olimazi build — a self-owned, local-first finance tracker for rental (Schedule E) and small-business (Schedule C) bookkeeping:

- **The story angle** (matches the site purpose): built with AI in days, not months; the books live in files the user owns; deterministic math that costs nothing to run; the same AI assistant that keeps the books also handles the rest of life. Position against subscription bookkeeping SaaS without naming competitors.
- **Visuals:** reuse the existing `olimazi-assets/schedule-e-*.jpg` screenshots.
- **Call to action:** a "free download coming soon" placeholder + a tester-interest mailto link (use the site's existing contact address; do not add a form or any third-party embed).
- **Honesty box:** one short line that it's an organizer, not tax advice, and users should confirm figures with their preparer.

### 4. Brand
Use the repo's existing design tokens and fonts exactly (the `:root` palette in `index.html`, Satoshi / Architects Daughter, including dark-mode variants). Do not introduce new colors or fonts. If the Schedule E screenshots clash with the palette, present them neutrally (framed card, caption) and note the clash in REPORT.md — do not restyle the screenshots.

### 5. Report
Overwrite `sol/REPORT.md` per the protocol.

## Out of scope (do not touch)
- Everything in `olimazi-assets/` except referencing existing images
- Any external service, form embed, analytics, or dependency
- Payment/download links (the tracker repo doesn't exist yet)
- This file
