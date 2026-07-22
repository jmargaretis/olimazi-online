# Site copy inventory — packet 12-C

Line references below point to the pristine pre-migration snapshot
`tools/.index.pre-migration.html`. A “slot” is one owner-editable Markdown field;
where fixed HTML links or literal quote marks divide a sentence, the visible
sentence is intentionally represented by more than one slot.

## Existing home-hero pilot (unchanged)

- Lines 803–806 — Kicker, Headline Lead, Headline Accent, Sub, CTA Label, and
  CTA Href. These six slots already live in the external `home-hero.md` source
  and remain owned by `tools/render_hero.py`.

## hero-spec

- Line 810 — Name Label, Name, and Name Description.
- Line 811 — Prior Work Label and Prior Work.
- Line 812 — Current Work Label and Current Work.
- Line 813 — Current Loop Label and Current Loop.
- Line 814 — Status Label and Status.

## main-work

- Lines 830, 832–833 — Section Label, Heading, and Intro.
- Line 843 — Method Slide 01 Title and Caption.
- Line 849 — Method Slide 02 Title and Caption.
- Line 855 — Method Slide 03 Title, Caption Lead, linked Credit Label, and
  Caption Tail.
- Line 861 — Method Slide 04 Title and Caption.
- Line 867 — Method Slide 05 Title, Caption Lead, linked Credit Label, and
  Caption Tail.
- Line 873 — Method Slide 06 Title and Caption.
- Line 879 — Method Slide 07 Title, Caption Lead, linked Credit Label, and
  Caption Tail.
- Line 885 — Method Slide 08 Title, Caption Before Quote, Quoted Word, Caption
  Before Credit, and linked Credit Label. The two literal quote marks and final
  period stay fixed to preserve the existing bytes.
- Line 891 — Method Slide 09 Title, linked Credit Label, Caption Before Quote,
  Quoted Word, and Caption Tail. The two literal quote marks stay fixed.
- Line 897 — Method Slide 10 Title and Caption.
- Line 903 — Method Slide 11 Title and Caption.
- Line 909 — Method Slide 12 Title, Caption Lead, and linked Credit Label; the
  final period stays fixed after the link.
- Line 915 — Method Slide 13 Title and Caption.
- Line 921 — Method Slide 14 Title and Caption.
- Lines 927–930 — Method Status, Method Heading, Method Body 1, and Method Body 2.
- Lines 932–934 — Method Period Label/Period, Built Label/Built, and Reach
  Label/Reach.
- Lines 937, 939–943 — Method Notes Label and Method Note 1 through Method Note 5.
- Lines 953–956 — Tracker Status, Heading, Lede, Product Name, Product Schedule,
  and Body.
- Lines 958–960 — Tracker Own Label/Value, Trust Label/Value, and Use Label/Value.
- Lines 963–966 — Tracker Download Label, Testing CTA, Disclaimer Lead, and
  Disclaimer Tail.
- Line 971 — Tracker Slide 01 Title and Caption.
- Line 973 — Tracker Slide 02 Title and Caption.
- Line 975 — Tracker Slide 03 Title and Caption.
- Line 977 — Tracker Slide 04 Title and Caption.
- Line 979 — Tracker Slide 05 Title and Caption.

## method

- Lines 991, 993–994 — Section Label, Heading Lead, Heading Accent, and Lede.
- Lines 1000–1002 — Slide 01 Label, Title, and Body.
- Lines 1007–1009 — Slide 02 Label, Title, and Body.
- Lines 1014–1016 — Slide 03 Label, Title, and Body.
- Lines 1021–1023 — Slide 04 Label, Title, and Body.

## mind

- Lines 1033–1035 — Section Label, Heading, and Intro.
- Lines 1214–1217 — Legend Schedule E and C, Legend Olimazi Design, Legend
  Method Effects, and Legend Everything Else.
- Lines 1222–1223 — Practice Heading and Practice Intro.
- Line 1228 — Cologne Chip, Title, Summary, and CTA.
- Line 1232 — Recipe Chip, Title, Summary, and CTA.
- Line 1235 — Library CTA.

## dialogs

- Lines 1245–1256 — Cologne Chip, Title, Intro, Heading 1, Body 1, Heading 2,
  Item 1 through Item 3, and the four visible Link labels.
- Lines 1267–1276 — Recipe Chip, Title, Intro, Heading 1, Body 1, Heading 2,
  Item 1 through Item 3, Source Link label, and Comment Link label.
- Lines 1285–1301 — Contact Chip, Heading, Intro, Form Label, six visible Option
  labels, CTA, and Direct Email label.

The three dialogs fit the marker-and-field pattern cleanly, so none are deferred.

## contact

- Lines 1308–1310 — Label, Heading, and Intro.
- Lines 1312, 1315–1320 — Form Label and six visible Option labels.
- Lines 1322–1324 — CTA and Direct Email label.

## Excluded

- Lines 6–7 — page description and title are document/SEO metadata, not visible
  section prose.
- Line 535 — the skip-link label is navigation chrome.
- Lines 539–725 and 779–781 — background formulas, diagram labels, and field
  notes are decorative SVG artwork rather than routine site copy.
- Lines 787–794 — wordmark, navigation labels, Contact, Theme, and its icon are
  site chrome or control labels.
- Lines 819–824 — the repeated marquee phrase is decorative and entirely
  `aria-hidden`.
- Lines 830, 991, and 1033 — section indices (`01 / 03`, etc.) are structural
  sequence metadata. The adjacent section labels are migrated.
- Lines 842–920, 968–981, 1037, 1227, 1231, 1240–1284 — image `alt` text,
  `aria-label` text, dialog labelling attributes, and carousel descriptions are
  accessibility/asset metadata rather than visible prose. They remain coupled
  to their images and controls.
- Lines 924, 981, and 1026 — Previous/Next labels, live slide counts, and their
  aria labels are carousel navigation strings.
- Lines 1039–1210 — generated vault-graph node labels and dates are visualization
  data. The owner-facing graph legend is migrated.
- Line 1219 — the down arrow is a decorative, `aria-hidden` glyph.
- Lines 1244, 1266, and 1284 — dialog close glyphs and close aria labels are
  control strings.
- Lines 1292–1297 and 1315–1320 — option `value` attributes remain structural
  email-subject values; only the visible option labels are migrated.
- Lines 1299 and 1322 — arrow spans are `aria-hidden` decorative glyphs; their
  adjacent CTA labels are migrated.
- Lines 1330–1334 — footer wordmark, pronunciation, copyright line, Library,
  and email are persistent identity/navigation chrome, not section prose.
- Lines 1337–1470 — JavaScript identifiers, fallback strings, generated email
  subject/body text, and carousel counts are behavioral strings, not owner copy.
- Throughout — HTML comments, asset paths, href/mailto destinations, IDs,
  classes, data attributes, link targets, and punctuation that structurally
  borders fixed links or literal quote marks are markup/behavior, not fields.

## Deferred

None. All six named packet sections, including all three dialogs, are migrated.
