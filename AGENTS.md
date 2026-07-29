# Codex operating contract (formerly "SOL")

When the owner says “check the site for instructions” (or names the olimazi-online repo), read the active packet in `sol/INSTRUCTIONS.md`.

Execute only that packet’s stated scope, commit the completed work to `main`, then overwrite `sol/REPORT.md` with the required completion report.

Direct changes are authorized only within the packet. Put any out-of-scope idea in `sol/REPORT.md` as a proposal instead of implementing it.

## Required REPORT.md format

Every report uses exactly these sections, in this order. Write "None" under a section rather than omitting it — the reviewer checks your claims against the diff, so a missing section reads as a hidden change.

```markdown
# Codex completion report — packet #N

## Status
COMPLETE | PARTIAL | BLOCKED — one line of summary.

## Changes
Every file touched, with one line each: what changed and why. This list must
match the diff exactly — a file in the diff but not listed here is a protocol
violation.

## Deviations
Anything done differently from the packet's stated instructions, and why.
Includes files touched that the packet didn't name.

## Skipped / unverified
Packet items not done, or done but not verified, and why.

## Blocked / questions
If any packet instruction was ambiguous or impossible: STOP on that item rather
than improvising, and put the question here. A good question beats a guessed
implementation.

## Proposals
Out-of-scope ideas for a future packet. Never implemented.
```

If Status is BLOCKED, commit whatever safe partial work exists plus the report — never leave the repo in a broken state.


## Vault graph snapshots

The mind section's graph is a tabbed set of dated snapshots. To add one:

1. Paste the new traced SVG into a new
   `<div class="graph-snapshot" id="snap-YYYY-MM-DD" role="tabpanel" data-snapshot>`.
2. Add a matching `<button ... data-snap-tab="snap-YYYY-MM-DD">` in `.graph-tabs`,
   newest first.
3. Move `class="is-active"` and `aria-selected="true"` onto the newest tab and panel.
4. Add one `None` to `SECTION_SPECS["mind"]` in `tools/render_section.py` for the new
   tab label. The renderer counts every text slot in the region positionally, including
   text inside HTML comments -- do not put explanatory comments inside a content region.
5. Run `render_section.py --mode build` and confirm `changed fields: none`.

Label each tab with the date the snapshot was actually taken. Never backdate, and never
relabel an older render of the same vault state as an earlier one.
