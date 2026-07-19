# Codex work packet — active

**Packet:** #10 · issued 2026-07-19 · authored by Claude (planning side)
**Packet #9 (product naming): ACCEPTED** — commit 66d3d17.
**Protocol:** AGENTS.md (Codex operating contract); report in required REPORT.md format.

## Packet #10 scope — Rental Manager tester page

A dedicated tester-recruitment page: `tester.html` (linked from the finance-tracker
section's CTA on index.html, replacing the bare mailto as the primary path).

### 1. The page — speak to ONE person
The self-managing rental owner: 1-5 properties, does their own books, dreads
rebuilding Schedule E from bank statements every spring. Copy leads with THEIR
day ("rent comes in by Zelle, the plumber got paid half in cash..."), not with AI.
Sections, using the site's existing type/palette system:
1. **Who this is for / not for** — for: self-managing landlords wanting their books
   in files they own; not for: large portfolios, property managers with existing
   software, anyone wanting tax advice.
2. **What Rental Manager is** — local-file organizer: deterministic math, open
   items kept visible, one dashboard, everything stays on your machine. Product
   name treatment: "Rental Manager" with muted "Sch. E" subtext (matches #9).
3. **What testing involves** — honest effort statement: load your data (or the
   included sample), run it for a few weeks, answer structured check-ins;
   feedback milestones, not vibes.
4. **Privacy & ownership** — no cloud, no account, files are yours, John never
   sees your books unless you share a redacted screenshot; not tax advice —
   confirm figures with your preparer (reuse the honesty-strip styling).
5. **Sign-up** — a short mailto-based application with a structured subject and
   prefilled body template (name, # of properties, how you track today, comfort
   with local files). Keep mailto for now — John's call on a form service later —
   but the prefilled body makes it one click + fill-blanks, not compose-from-scratch.
6. Footer note: "Business Manager (Sch. C) is next — same approach for
   small-business books." with the same mailto template flagged INTEREST: SCH C.

### 2. index.html touch
Change the tracker card's CTA from the raw mailto to `tester.html`
("I'm interested in testing →" keeps its label). No other index changes.

### Acceptance
1. `tester.html` renders with site nav/footer, palette, and type; readable on
   mobile width.
2. CTA on index.html routes to it; the page's apply link opens a prefilled email.
3. Copy contains zero unexplained jargon (a landlord who has never heard of
   Olimazi can follow it); "Rental Manager" naming consistent with #9.

### Out of scope
- The "Trace the transaction" interactive hero → future packet #11.
- Forms services, email-list tooling, analytics.

