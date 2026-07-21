# Site packet — hero content renderer (Mission Control Packet 3, part A)

Authored 2026-07-21 from the approved plan (`Claude OS/inbox/codex-mission-control-plan.md`,
"SOL work packet 3 — Hero content-source pilot"). This is PART A: the deterministic
renderer + HTML markers, built in the site repo. Part B (Mission Control
Open/Preview/Build/Deploy buttons) is wired separately after this is verified.

## Context
The home hero copy is being migrated to an Obsidian-edited content source so John
edits prose in the vault and a renderer patches the site HTML. The content source
already exists (do NOT create it):
`C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy\home-hero.md`
— YAML frontmatter + `#`-heading fields: Kicker, Headline Lead, Headline Accent,
Sub, CTA Label, CTA Href.

The current hero lives in `index.html` at the `header.hero.synthesis-hero` block
(the div containing `.hero-kicker`, the `<h1>` with an inner `<span class="accent">`,
`.hero-sub`, and the `a.btn` CTA). The right-side `<aside class="spec">` is NOT in
scope — leave it untouched.

## Build

### 1. Mark the hero region in index.html
Wrap ONLY the editable hero content (kicker through CTA `<a>`, inside the left
`<div>` of `.hero-grid`) with exact comment markers:
```
<!-- content:home-hero:start -->
...generated hero fields...
<!-- content:home-hero:end -->
```
Do not wrap the `.hero-grid` div or the spec aside. Keep current markup/classes
identical on first render (byte-identical output for unchanged input).

### 2. Renderer CLI: `tools/render_hero.py` (standard library only)
Interface:
```
python tools/render_hero.py --content <path-to-home-hero.md> --mode preview|build [--target <index.html>]
```
- Parse the content MD: read the 6 fields by their `#` headings; validate all
  required fields present and non-empty; validate CTA Href is a non-empty string;
  fail with a clear message + nonzero exit on any missing/empty field.
- Render the hero fragment from a fixed template that reproduces the EXACT current
  markup (`.hero-kicker` div; `<h1>` = Headline Lead + " " + `<span class="accent">`
  Headline Accent `</span>`; `.hero-sub` = Sub; `a.btn` href=CTA Href label + the
  existing `<span class="arr" aria-hidden="true">→</span>`). HTML-escape field text.
- Locate the `content:home-hero:start/end` markers; replace ONLY the content
  between them. Refuse (nonzero exit, no write) if markers are missing or
  duplicated.
- `--mode build`: write the patched index.html in place. `--mode preview`: write
  to `index.preview.html` (a sibling), do not touch index.html.
- Idempotent: running build twice with unchanged content yields byte-identical
  index.html. Print a short summary of which fields changed vs the current file.

### 3. Provenance
On build, write/update `tools/.hero-content-hash` with the SHA-256 of the content
source, so downstream status (Part B) can compare source vs rendered.

## Out of scope
The Mission Control server buttons and git deploy (Part B). The spec aside. Any
other section or copy. New dependencies. Editing the content MD. Committing.

## Acceptance tests (results -> sol/REPORT.md)
1. `render_hero.py --mode build` with the current content produces index.html
   whose hero renders identically to before migration (diff limited to the marker
   comments + within-region formatting; the spec aside and all other sections
   unchanged).
2. Editing "Headline Accent" in a COPY of the content file and running build
   changes only the hero `<span class="accent">` text.
3. Running build twice with unchanged content = byte-identical index.html
   (idempotent).
4. A missing required field aborts with a useful message and nonzero exit, no
   write.
5. Duplicate or missing markers abort the build without changing index.html.
6. `--mode preview` writes index.preview.html and does NOT modify index.html.
7. Serve locally and confirm the rendered hero displays correctly (kicker, split
   headline with mint accent, sub, working CTA).
You cannot commit (read-only .git — expected); leave working-tree changes for
Claude to verify.
