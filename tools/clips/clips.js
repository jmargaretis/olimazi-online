// Clip scripts for the two social clips. Coordinates are UI pixels in the
// 1440x1008 capture (capture.js). cam: [t, cx, cy, zoom]. cur: [t, x, y, click].
// Callout: [t0, t1, x, y, w, h, text]. Times in seconds.
window.CLIPS = {
  rm: {
    kicker: 'RENTAL MANAGER · SCH. E',
    fps: 30, len: 42.5,
    scenes: [
      { img: 'rm-dash', t0: 0, t1: 13.6,
        head: ['Your Schedule E,', 'reconciled.'], sub: 'From a spreadsheet you own. Sample property shown.',
        cam: [[0, 720, 450, 1], [3.2, 720, 450, 1], [4.0, 540, 380, 1.75], [10.0, 540, 380, 1.75], [10.8, 1040, 380, 1.75], [12.4, 1040, 380, 1.75], [13.1, 720, 450, 1]],
        call: [
          [4.2, 7.4, 284, 268, 475, 55, 'Every Schedule E line, read from the workbook. Rents: $7,150 of $21,550 expected.'],
          [7.4, 10.1, 284, 398, 475, 55, 'Nothing booked yet? Last year’s figure shows, marked as waiting.'],
          [10.9, 12.5, 813, 240, 475, 249, 'Open items stay on screen. The workbook says what it still needs.']],
        cur: [[12.6, 900, 560], [13.35, 118, 208, 1]] },
      { img: 'rm-flow', t0: 13.6, t1: 23.2,
        head: ['Receipts in.', 'One click books.'],
        cam: [[13.6, 720, 450, 1], [14.2, 720, 450, 1], [14.9, 786, 560, 1.3], [21.6, 786, 560, 1.3], [22.2, 720, 450, 1]],
        call: [
          [15.0, 18.4, 286, 380, 1000, 70, 'Captured receipts become proposed rows. Nothing is booked until you click.'],
          [18.4, 21.6, 286, 639, 1000, 144, 'A field the rules could not read shows in red. You fill it first.']],
        cur: [[22.1, 800, 600], [22.95, 117, 259, 1]] },
      { img: 'rm-manage', t0: 23.2, t1: 30.4,
        head: ['Repairs, tenants,', 'vendors.'],
        cam: [[23.2, 720, 450, 1], [23.6, 720, 450, 1], [24.2, 786, 430, 1.3], [27.2, 786, 430, 1.3], [27.7, 786, 620, 1.3], [29.3, 786, 620, 1.3], [29.8, 720, 450, 1]],
        call: [
          [24.3, 27.3, 286, 283, 1000, 256, 'Each tenant issue keeps its thread: the report, the emails, the vendor, the line it books to.'],
          [27.7, 29.4, 286, 649, 1000, 135, 'Work orders carry the quote until the job closes.']],
        cur: [[29.5, 700, 700], [30.2, 117, 309, 1]] },
      { img: 'rm-org', t0: 30.4, t1: 38.0,
        head: ['Ready for', 'your preparer.'],
        cam: [[30.4, 720, 450, 1], [30.8, 720, 450, 1], [31.4, 560, 330, 1.6], [33.9, 560, 330, 1.6], [34.5, 786, 680, 1.3], [38, 786, 680, 1.3]],
        call: [
          [31.5, 34.0, 268, 186, 400, 66, 'Open questions, counted. Export the preparer package when it is clear.'],
          [34.6, 37.9, 266, 584, 1040, 304, 'Still needed: derived from this workbook, not a generic checklist.']],
        cur: [[32.0, 700, 420], [33.2, 356, 233]] },
    ],
    end: { t0: 38.0, title: ['Rental Manager', 'Sch. E'], lines: ['Local files. Deterministic math.', 'Open items visible.'], cta: 'Testers wanted' },
  },

  ops: {
    kicker: 'OLIMAZI OPS · THE CUSTOM BUILD',
    fps: 30, len: 48,
    scenes: [
      { img: 'ops-flow', t0: 0, t1: 9.2,
        head: ['One hub runs', 'the whole brand.'], sub: 'Not technical by background. Built with Claude Code and Codex.',
        cam: [[0, 720, 450, 1], [3.0, 720, 450, 1], [3.7, 880, 400, 1.4], [8.2, 880, 400, 1.4], [8.7, 720, 450, 1]],
        call: [
          [3.8, 6.5, 456, 266, 936, 70, 'Photo in a folder → draft → review → publish. Every number read from its own source.'],
          [6.5, 8.3, 456, 470, 916, 70, 'Every local server probed live. A dead one reads grey, not green.']],
        cur: [[8.3, 700, 500], [9.0, 113, 18, 1]] },
      { img: 'ops-queue', t0: 9.2, t1: 16.4,
        head: ['Nothing posts', 'on its own.'],
        cam: [[9.2, 560, 333, 1.35], [16.4, 560, 333, 1.35]],
        call: [
          [9.7, 13.0, 266, 154, 800, 139, 'A photo dropped in a folder becomes a draft. It waits for a yes.'],
          [13.0, 15.6, 565, 307, 156, 42, 'Drafts waiting on one click. Approving makes a draft in the scheduler, never a post.']],
        cur: [[15.4, 640, 330], [16.2, 118, 336, 1]] },
      { img: 'ops-slides', t0: 16.4, t1: 24.4,
        head: ['Every slide,', 'editable.'],
        cam: [[16.4, 720, 450, 1], [16.8, 720, 450, 1], [17.3, 1010, 420, 1.45], [20.3, 1010, 420, 1.45], [20.9, 560, 450, 1.3], [23.3, 560, 450, 1.3], [23.8, 720, 450, 1]],
        call: [
          [17.4, 20.4, 1128, 444, 252, 70, 'Pick which words go red. The slide rebuilds live.'],
          [20.9, 23.4, 262, 176, 140, 720, 'The whole deck, in order, before anything posts.']],
        cur: [[17.6, 1300, 560], [18.6, 1195, 494, 1], [23.4, 500, 300], [24.2, 51, 18, 1]] },
      { img: 'ops-lp', t0: 24.4, t1: 31.6,
        head: ['The site,', 'section by section.'],
        cam: [[24.4, 720, 450, 1], [24.8, 720, 450, 1], [25.3, 700, 260, 1.5], [27.8, 700, 260, 1.5], [28.3, 1040, 300, 1.5], [30.6, 1040, 300, 1.5], [31.0, 720, 450, 1]],
        call: [
          [25.4, 27.9, 285, 94, 660, 76, 'Each card owns one part of olimazi.online. Edit the words, preview, build, deploy.'],
          [28.3, 30.7, 965, 187, 318, 260, 'The deploy reads the live page back. It flags drift instead of claiming success.']],
        cur: [[30.8, 600, 500], [31.4, 72, 298, 1]] },
      { img: 'ops-pulse', t0: 31.6, t1: 38.0,
        head: ['Every finished thing,', 'dated.'],
        cam: [[31.6, 720, 450, 1], [32.0, 720, 450, 1], [32.5, 700, 300, 1.45], [34.8, 700, 300, 1.45], [35.3, 838, 560, 1.2], [37.0, 838, 560, 1.2], [37.5, 720, 450, 1]],
        call: [
          [32.6, 34.9, 284, 246, 632, 72, '312 finished things in 90 days, read back from the record.'],
          [35.3, 37.1, 266, 420, 1144, 340, 'Where the work actually sat, hour by hour.']],
        cur: [[37.1, 600, 500], [37.8, 118, 375, 1]] },
      { img: 'ops-graph', t0: 38.0, t1: 44.0,
        head: ['A second brain', 'that shows its gaps.'],
        cam: [[38.0, 720, 450, 1], [38.4, 720, 450, 1], [39.0, 560, 250, 1.7], [44, 560, 250, 1.7]],
        call: [
          [39.1, 43.9, 262, 180, 395, 70, '138 files, 222 links. And the 11 nothing points at, in red.']],
        cur: [] },
    ],
    end: { t0: 44.0, title: ['Olimazi', 'ops'], lines: ['Planned in Claude Code.', 'Executed in Codex. Reviewed in Claude Code.'], cta: 'Learning in public' },
  },
};
