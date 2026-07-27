# Work order: Mission Control multi-section wiring (packet 12-D)

## Context

Packet 12-C (committed) migrated all `index.html` prose into marker-wrapped regions with content sources + a generic renderer `tools/render_section.py` (CLI-compatible with `tools/render_hero.py`). Content sources now live in the vault at `C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\` — seven files: `home-hero.md` (the existing pilot) plus `hero-spec.md`, `main-work.md`, `method.md`, `mind.md`, `contact.md`, `dialogs.md`. Card commands are specified in `tools/mission-control-cards.snippet.md`.

Mission Control is a local panel in the vault at `C:\Users\jmarg\OneDrive\Documents\Claude OS\inbox\launchpad\` — `mission_control.py` (Python HTTP server) + `launchpad.html` (the panel UI). It currently supports ONE site-copy card ("Site — Home hero"): status (BUILT/EDITED/DRIFT), Preview, Build, and Deploy endpoints, where Deploy git-commits + pushes and then **live-verifies** the copy actually appears on https://olimazi.online/ before reporting DEPLOYED.

## Goal

Extend Mission Control so all six new sections get the same card treatment: per-section status, Preview, Build, and gated Deploy with live-verify — without changing the hero pilot's behavior.

## Hard constraints

1. **Write only inside this repo.** The vault (including `inbox\launchpad\`) is read-only for you. Read the current `mission_control.py` and `launchpad.html` from the vault, produce the updated versions as **complete staged replacement files** in `tools/mission-control-staging/` (same filenames). The verifier installs them.
2. **Do not commit or push.**
3. **Do not break the hero pilot.** The home-hero card, its endpoints, and `render_hero.py` usage must behave exactly as today. Prefer leaving the hero code path untouched and adding generic multi-section support alongside it.
4. **No fragment-template duplication.** The hero's DRIFT check duplicates the renderer's HTML template inside `mission_control.py`; do NOT replicate that pattern six times. For new sections, determine expected region content by reusing `tools/render_section.py` (import it as a module, or invoke it in preview mode against a scratch copy and compare regions). One source of truth for markup.
5. Follow the existing code's style (it is terse; match it) and keep the server dependency-free (stdlib only).

## Per-section behavior (mirror the hero semantics)

- **Status:** BUILT (content hash matches `tools/.<section>-content-hash` and region matches renderer output), EDITED (content changed since last build), DRIFT (region doesn't match renderer output or markers broken), UNKNOWN (error). Same JSON shape as hero status.
- **Preview:** render to `index.preview.html`; must not modify `index.html` (assert byte-equality before/after like `hero_preview` does).
- **Build:** render into `index.html`, update the section's hash file.
- **Deploy:** refuse unless status is BUILT; scope = `index.html` + that section's hash file; git add/commit/push (commit message: `Build <section> from content source`); then live-verify by fetching the live URL and checking a distinctive probe string from that section's current field values (pick the longest field value as probe; document this). Report DEPLOYED only on live confirmation, mirroring `hero_deploy`.

## Panel UI

Add six cards to `launchpad.html` following the existing "Site — Home hero" card's markup/JS pattern, titled per `tools/mission-control-cards.snippet.md` ("Site — Hero spec", "Site — Main work", "Site — Method", "Site — Mind", "Site — Contact", "Site — Dialogs"). Reuse the hero card's status polling and button wiring — generalize the JS rather than copy-pasting six blocks if the existing structure allows it cleanly.

## Verification (you must run)

Port binding may be blocked in your sandbox — do NOT rely on running the live server. Instead:

1. Import your staged `mission_control.py` as a module (temporarily adjusting paths as needed) and call each new section's status function directly against the real repo state → all should report BUILT.
2. Simulate an edit (in a scratch copy of a content source, not the vault) → status function on the scratch shows EDITED.
3. Verify the staged file still contains the hero endpoints unchanged (diff the hero-related functions against the vault original — report the diff as empty or explain every hunk).
4. Syntax-check `launchpad.html` changes (well-formed, all six cards present, no duplicate element IDs).

## Deliverables

- [ ] `tools/mission-control-staging/mission_control.py` — complete replacement file
- [ ] `tools/mission-control-staging/launchpad.html` — complete replacement file
- [ ] Final summary: what changed in each file, verification results per the four checks above, and anything the verifier must test by hand after installing (e.g., live server smoke test steps)
