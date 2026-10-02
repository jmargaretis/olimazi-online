# Rebuild diff — what the new front page still has to pull from the old site

Published 2026-10-02. New build = the locked S3 hero (dark, dot octopus, cover-flow tiles).
Old site kept at `index-s7.html` (same assets) and git tag `site-s7-live-2026-10-02`.
John points out fixes 2026-10-03; this is the checklist to work from.

## Links and buttons not wired yet
- [ ] "Get in touch" (hero CTA) and footer "Get in touch" — no handler. Old site opened the contact card.
- [ ] "The short story →" and "Read the story" — no handler. Old site opened the story pane.
- [ ] Top nav Work / Library / Story — anchors to `#` only. Old site had `#work`, `#learning`, `#library`.
- [ ] Contact card: `mailto:hello@olimazi.online` and the Rental Manager test mailto
      (`?subject=Test Rental Manager (Sch. E)`) — both missing.
- [ ] YouTube link (Learning in public, watch?v=yGRtK08BdIs) — missing.
- [ ] `vault.html` link (Library) and `tester.html` link — now orphaned, nothing points at them.
- [ ] Favicon, title and meta description — carried over. Done.

## Sections in the old site, not in the new build
- [ ] `#work` "The work, then and now." — Method Effects card, Rental Manager card (clip-rm.mp4 + poster).
- [ ] `#learning` "One hub, running." — clip-ops.mp4, "Learning in public", the five lesson headings.
- [ ] `#library` "Current state of mind." — shelves: Kairos (video), Dog Studios x7, Bougatsa,
      Eau d'Ombre, Excuse Me x3, Ribeye x2, sketch + vector, '67 Bug, restaurant x2, RS wheel,
      brothers' truck, Condo Avenue.
- [ ] Detail panes: `t-method` gallery (8 images), `t-rental`, `t-learning`, contact card, story pane, viewer with prev/next.

## Media
- [ ] New build inlines its 9 tile images as base64 (1.2 MB page). Move to `assets/` when the layout settles.
- [ ] Old `clip-ops.mp4` and all `ops-*` captures still show the old octopus watermark. Only the Flow
      tile was reshot today. Re-run `tools/clips/capture.js ops` + `render.js ops` after the launchpad restarts.
- [ ] Fonts: new build loads Anton + Inter Tight from Google. Old site used local Satoshi + Architects Daughter.

## Tile look
- Logo tile ("The short story") no longer gets the red ring when active. The ring was #C0392B,
  not coral, but on the white card it read as coral. Drop shadow stays. Revert: remove `.t.av` rule
  and the `av` branch in `flow()`.
