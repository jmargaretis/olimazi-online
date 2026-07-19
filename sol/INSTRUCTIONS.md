# Codex work packet — active

**Packet:** #9 · issued 2026-07-19 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

**Packet #8 (library merges): ACCEPTED.** Note: the operating contract is now
titled "Codex" (formerly "SOL") — same protocol, same file paths.

## Packet #9 scope — finance tracker product naming

The tracker product now has official names (decided 2026-07-19):
- **Rental Manager** — subtext **Sch. E** (the current rental tracker)
- **Business Manager** — subtext **Sch. C** (the upcoming counterpart)

Apply on `index.html` only, in the finance-tracker section:

1. The "Use it" spec row (~line 957): `Rental Schedule E now · small-business
   Schedule C next` → `Rental Manager (Sch. E) now · Business Manager (Sch. C) next`.
2. The "Current work" spec row (~line 809): `Schedule E/C · tested, still being
   refined` → `Rental Manager (Sch. E) / Business Manager (Sch. C) · tested, still
   being refined`.
3. In the tracker card, introduce the product name once in the visible copy —
   e.g. the lede or the paragraph under the `<h3>` gains "Rental Manager" as the
   product's name with "Sch. E" in a smaller/muted treatment consistent with the
   site's existing type system. Keep the h3 "A finance tracker you own" as-is
   (it's the hook, not the name).
4. Leave unchanged: carousel captions and alt text (they describe Schedule E tax
   content — correct terminology), the honesty disclaimer, the mailto CTA, and
   everything outside the finance-tracker section.

## Acceptance
1. Open `index.html` locally; the tracker section shows the Rental Manager /
   Business Manager naming in the two spec rows and once in body copy.
2. `grep -c "Rental Manager" index.html` ≥ 3; no occurrences outside the
   finance-tracker section.
3. No visual regression to the section layout (spec rows still align).

## Out of scope
- Any other page or section; library.html; fonts; colors; this file.
