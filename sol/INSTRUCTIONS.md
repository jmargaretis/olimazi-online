# SOL work packet — active

**Packet:** #4 · issued 2026-07-17 · authored by Claude (planning side) · SUPERSEDES packet #3
**Protocol:** see `AGENTS.md`. Direct-change authority within scope only.

Packet #3 (streamlining focus pass) was never executed and is replaced by this packet —
its intent is affirmed by the owner and absorbed here, extended with a structural
revision from the owner's written notes. Read `PRODUCT.md` and `DESIGN.md` first; stay
inside the locked framing (personal concept, proof over pitch) and the existing tokens.

## Packet #4 scope — structural revision + focus pass

### 1. Restructure: three primary sections + closer
- **Section 1 (lead presentation):** keep the current first-impression treatment (owner
  likes it). REMOVE the dense expanded-information block. In its place: a set of clean,
  uniformly blocked tiles/photo frames, each with a short placeholder label — content
  arrives later from the owner (see §3). First glance = presentation; detail = opt-in.
- **Section 2:** tighten the blocking — stop the long vertical bleed; cut the
  description to a lead-in (detail moves to tiles/slides per §3). Reconsider the
  action-button placement: propose in REPORT.md if you think they should move, with
  reasoning; do not assume.
- **Section 3:** condense the wordiness. Reduce thumbnail sizes (still readable).
  Keep the "fun learning" material but demote its prominence. Layout of thumbs is
  otherwise fine as-is.

### 2. Removals (owner's kill list)
- **Tax & accounting operations section: remove.** Preserve its copy verbatim in a new
  file `notes/removed-tax-accounting.md` (repo, not the page) — some of it may return
  as Section 2 tiles.
- **Restaurant operations: remove entirely, zero mention anywhere.** Preserve copy in
  `notes/removed-restaurant.md`.
- **Content & automation section: remove**; roll its essence into Section 3 where it
  fits naturally. Propose wording freely — this is the one place light rewriting is in
  scope.
- Reason recorded for all three: the page read too much like a resume; it should read
  like a working lab.

### 3. Tile/slide detail mechanic (Sections 1 and 2)
Build the tile frames so each tile's content (short title, body text, optional image)
is trivially updatable in one obvious place in `index.html` (clearly commented block
per tile). The owner authors detail in documents delivered via the planning side —
no CMS, no new dependencies. Empty tiles must look intentional (placeholder styling
per DESIGN.md), not broken.

### 4. Carried from packet #3 (approved technical cleanups)
- Hero display ceiling: test below 104px for wide-screen balance; ship your best
  judgment, note before/after.
- Token consolidation: collapse the original-palette + mint-override layering into one
  clean token set, rendered output preserved exactly.

### 5. Report
Overwrite `sol/REPORT.md`: sections removed/kept, tile mechanic explanation (how the
owner's future content drops in), button-placement proposal if any, hero value,
token-consolidation confirmation, verification (desktop + mobile + dark mode).

## Out of scope
- `olimazi-assets/` — no additions, deletions, swaps (image curation in progress owner-side;
  assets arrive in a future packet)
- No graph/map insert (considered and dropped by owner)
- New dependencies, payment/download links, this file
