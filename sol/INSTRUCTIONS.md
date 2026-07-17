# SOL work packet — active

**Packet:** #3 · issued 2026-07-17 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`. Direct-change authority within scope only; out-of-scope ideas → proposals in `sol/REPORT.md`.

## Context

Owner feedback on the live site: **a bit too busy, still lacking some focus.** This packet is a streamlining pass — the goal is subtraction and hierarchy, not new material. Read `PRODUCT.md` and `DESIGN.md` (your packet #2 capture) before touching anything; every change must stay inside the locked framing (personal concept, proof over pitch) and the existing token system.

## Packet #3 scope

### 1. Focus pass on `index.html`
Reduce visual competition so each section reads with one clear focal point:
- Tighten hierarchy: one dominant element per section; demote or trim anything competing with it.
- Where a section shows several images at similar weight, pick a lead and reduce the rest (smaller, fewer, or grouped) — do **not** delete image files or add new ones (see out of scope).
- Trim copy only where it directly serves de-busying (shorter intros, cut redundant lines). No rewrites of meaning or voice.
- **Whole-section removal is not authorized.** If you believe a section should go entirely, make the case in `REPORT.md` as a proposal instead.

### 2. Your packet #2 proposals — two are approved as part of this pass
- **Display scale (your proposal 3):** test a lower hero ceiling than 104px for wide-screen balance; ship the value you judge best, note before/after in the report.
- **Token consolidation (your proposal 2):** collapse the original-palette-plus-mint-override layering in `index.html` into one clean token set, **preserving rendered output exactly**. This is a refactor, not a restyle.
- (Proposal 1, the accessibility/contrast audit, is deferred to a future packet — don't start it.)

### 3. Report
Overwrite `sol/REPORT.md`: what was cut/demoted and why, the hero-scale decision, confirmation the token consolidation is render-identical, and any proposals (including sections you'd remove outright).

## Out of scope
- `olimazi-assets/` — no additions, deletions, or swaps. Image curation is underway on the owner's side (a vault image bucket with per-image notes and permissions); a future packet will carry any asset changes.
- New sections, new content, new dependencies, copy rewrites beyond trims
- Payment/download links
- This file
