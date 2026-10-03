# Codex work packet — active

**Packet:** #13 · issued 2026-10-02 · authored by Claude (planning side)
**Branch:** `port-everything` — commit there. Never touch `main`, never push.
**Protocol:** AGENTS.md; report in the required REPORT.md format. Stage by file name, never `git add -A`.

## Packet #13 scope — click-through audit of the ported site, then fix

`index.html` is the new dark hero build with the OLD site ported below it inside
`<div class="s7">` (old CSS scoped with the `.s7` prefix, old inline script). The
reference for what must be present is `index-s7.html` in this folder (the old site,
also live at https://olimazi.online/index-s7.html). `notes/rebuild-diff-2026-10-02.md`
lists what was already known to be missing.

### 1. Click through everything, both files
Playwright is installed (python and node). Open
`file:///C:/Users/jmarg/work/olimazi-online/index.html` at desktop 1440x900 and phone
390x844, then `index-s7.html` the same way. Click every nav link, every hero tile and
the detail pane, every Open / arrow / `data-pane` / `data-contact` control, the library
viewer and its thumbnails, the rental manager pane, the story pane, the contact card,
the footer links. Write down what the old site has that the port lacks or breaks.

### 2. Fix the owner's findings (all four are required)
1. **"Slides missing details. Slides missing."** Slide sets, decks, captions and image
   references in the library and viewer are incomplete versus `index-s7.html`. Make
   every one of them exist and render in the port. Check every image path resolves on disk.
2. **"No links."** Links in the old site (external, GitHub, social, mailto, the rental
   manager tester invite, LinkedIn, library items) are missing or dead in the port.
   Restore all of them. Every href must resolve; no `#` stubs unless the old site had them.
3. **"Rental manager missing a bunch of items."** Compare the rental pane/section in
   `index-s7.html` with the port and restore everything missing: feature list, tester
   invitation, screenshots, buttons, text.
4. **"Don't like having to click on 'open'. I want the 'x' I have for closing."**
   Content shows directly on a tile click, with no extra "Open" step. Closing stays the
   existing "x" (`#x`) pattern the hero pane already uses. Remove "Open" buttons in the
   ported sections where they only gate content that can simply be shown; reuse the same
   close behaviour and markup. Do not invent a new close control.

### 3. Hard rules
- `#C0392B` is the only red.
- These two lines stay byte-identical: the CSS line starting
  `.oc2{position:absolute;left:-2.2vw;` and
  `var TF={cw:14,gap:107,depth:84,tilt:60,sA:1.43,s1:.98,s2:.82,dim:.37,fade:1,shadow:2};`.
  Do not change hero layout numbers.
- Keep the HubSpot contact form wiring as is.
- Never name Claude or any AI app in site copy. Faceless brand: no owner name anywhere.

### 4. Verify, then report
Playwright after fixing: zero page errors; every control opens its content; every local
href/src resolves on disk; external hrefs are http(s). Save screenshots of the fixed
states to `C:\Users\jmarg\My Drive\Claude\Site plan 2026-09-27\` with prefix `codex-`.
Commit on `port-everything`; end the commit message with
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
REPORT.md must list: the diff (found / fixed / still open), the commit hash, the
screenshot paths.
