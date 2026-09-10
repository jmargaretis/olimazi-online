# Packet 14 completion report — Library as a generated collection

## Status

COMPLETE — the feature and library collections are generated from seven repo-local records, with tests and byte-stability checks passing.

## CLI contract

`tools/render_collection.py` accepts exactly:

```text
python tools/render_collection.py --mode preview|build [--library-root <dir>]
```

There is no positional content argument. `--library-root` defaults to the module-level `LIBRARY_ROOT` constant for the production vault path; no code in this packet read or wrote that path. Preview writes `index.preview.html` and `library.preview.html`. Build writes `index.html`, `library.html`, and `tools/.library-content-hash`. Success returns 0 and prints a JSON object with per-page change booleans; user-correctable errors return 1 and print a JSON error object to stderr.

The receipt hashes the bytes of every top-level record file after sorting the parsed records by slug. Files under `_edits/` are excluded because they are section-source handoff files, not library records.

## Record schema

Each top-level `tools/library-seed/<slug>.md` file uses schema `olimazi-site-copy/library-item/v1`.

Required frontmatter:

- `schema`
- `slug`
- `status` (`active` or `draft`)
- `placement` (`feature` or `library`)
- `order` (integer)
- `chip`
- `feature_slot` (`1` or `2`) only when `placement: feature`

Required body fields:

- `Title`
- `Summary`
- `Dialog Chip`
- `Dialog Intro`
- `Card Image`
- `Card Image Alt`
- `Dialog Image`
- `Dialog Image Alt`

Optional body fields:

- paired `Notes Heading` and `Notes Body`
- `Detail Heading` with contiguous `Detail Item 1..N`
- contiguous `Source 1..N`, each `Label | URL`
- `Card Orientation`
- `Dialog Close Label`

CTA text is rejected as an authored field and is derived in one function. Draft records render nowhere. Active feature records render only on `index.html`; active library records render only on `library.html`, sorted by `(order, slug)`. More than two active feature records, duplicate active feature slots, missing required image fields, noncontiguous numbered fields, and incomplete optional block pairs are hard errors.

## Changes

- `index.html` — placed the existing Library CTA in its own disjoint `content:mind-tail` region after the generated feature-card region.
- `library.html` — added generated-region markers around the existing tile grid and dialog block; generated item markup remains byte-identical.
- `tools/render_section.py` — added the data-only `mind-tail` `SectionSpec`; no function, parser, or CLI logic changed.
- `tools/render_collection.py` — added the stdlib-only collection parser, validator, CTA derivation, HTML generator, preview/build CLI, and combined content receipt.
- `tools/.library-content-hash` — added the build receipt for the seven sorted record files.
- `tools/library-seed/cologne.md` — migrated the Cologne feature card and dialog verbatim, including both image fields, alts, sources, and close label.
- `tools/library-seed/bougatsa.md` — migrated the Bougatsa feature card and dialog verbatim, including both image fields, alts, sources, and close label.
- `tools/library-seed/ribeye.md` — migrated the Ribeye library card and dialog verbatim, including distinct card/dialog images and card orientation.
- `tools/library-seed/bug.md` — migrated the classic Bug library card and dialog verbatim, including its non-derived close label.
- `tools/library-seed/art-thread.md` — migrated the Art thread library card and dialog verbatim.
- `tools/library-seed/truck.md` — migrated the truck library card and dialog verbatim, including its non-derived close label.
- `tools/library-seed/restaurant.md` — migrated the Restaurant Operations library card and dialog verbatim, including distinct card/dialog images and its non-derived close label.
- `tools/library-seed/_edits/mind.md` — staged the intended vault-side `mind` source with only the legend and practice fields retained.
- `tools/library-seed/_edits/dialogs.md` — staged the intended vault-side `dialogs` source with only Contact fields retained.
- `tools/library-seed/_edits/mind-tail.md` — staged the new vault-side source containing the moved `Library CTA`.
- `tests/test_render_collection.py` — added seven unittest cases for lifecycle placement, feature limits, all CTA branches, and absent optional DOM.
- `REPORT-14.md` — documented the implementation, migration handoff, verification, and checkout-specific decisions.
- `PACKET-14-library-collection.md` — deleted after all implementation and verification work completed, as required by the packet.

## Exact vault-source removals

Claude should remove these fields from the production `mind.md`:

- `Cologne Chip`
- `Cologne Title`
- `Cologne Summary`
- `Cologne CTA`
- `Recipe Chip`
- `Recipe Title`
- `Recipe Summary`
- `Recipe CTA`
- `Library CTA` (moved to the new `mind-tail.md`)

Claude should remove these fields from the production `dialogs.md`:

- `Cologne Chip`
- `Cologne Title`
- `Cologne Intro`
- `Cologne Heading 1`
- `Cologne Body 1`
- `Cologne Heading 2`
- `Cologne Item 1`
- `Cologne Item 2`
- `Cologne Item 3`
- `Cologne Link YouTube`
- `Cologne Link Fragrantica`
- `Cologne Link Writeup`
- `Cologne Link Comment`
- `Recipe Chip`
- `Recipe Title`
- `Recipe Intro`
- `Recipe Heading 1`
- `Recipe Body 1`
- `Recipe Heading 2`
- `Recipe Item 1`
- `Recipe Item 2`
- `Recipe Item 3`
- `Recipe Link Source`
- `Recipe Link Comment`

The corresponding staged post-migration files are under `tools/library-seed/_edits/`. No path under `C:\Users\jmarg\OneDrive\` was accessed.

## Decisions and ambiguities

- The checkout already had the feature/dialog region split and the obsolete Cologne/Recipe slot deletions in commit `d32eb2c`; the current `mind` spec has 24 slots and the current region has exactly 24 text nodes. Deleting any additional `None` slots would break the required `mind` build, so the only remaining authorized `render_section.py` change was the required data-only `mind-tail` entry.
- The packet says to match `render_section.py` while also saying “stdout JSON only,” but the checked-out section renderer prints plain text. The collection CLI follows the packet’s more explicit JSON requirement and matches the section renderer’s 0/1 exit-code behavior.
- The checked-out section renderer additionally requires `site_repo` in source frontmatter. The three `_edits` files use the repo-local path, keeping the production vault path out of staged source files.
- The Ribeye dialog’s YouTube link remains inline in `Dialog Intro`, not a `Source` field. This preserves both the existing inline-link DOM and its derived `Open notes →` CTA.
- Feature records carry `order` values because `order` is part of the stated record schema, although feature ordering uses only `feature_slot`.

## Verification

- Collection build completed successfully and generated both pages.
- The complete `library.html` diff against HEAD contains only four marker-comment additions.
- Current feature-card-through-CTA content and feature dialog region match their HEAD counterparts byte-for-byte after ignoring only marker placement.
- `render_section.py` build checks for `mind` and `dialogs` each reported `changed fields: none`.
- Seven unit tests pass.
- Two consecutive collection builds each report both pages unchanged.
- `git diff --check` passes.
- The packet file was deleted only after these checks.

## Deviations

None.

## Skipped / unverified

The sandbox-created empty directory `tests/tmpladv49e2/` could not be removed because the Windows sandbox denied directory access after `tempfile` created it. The test was rewritten to avoid temporary filesystem use, its generated Python cache was removed, and the inaccessible empty directory is not part of the Git diff.

## Blocked / questions

None.

## Proposals

None.
