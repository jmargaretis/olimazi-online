// Clip scripts for the two social clips. Coordinates are UI pixels in the
// 1440x1008 capture (capture.js). cam: [t, cx, cy, zoom]. cur: [t, x, y, click].
// Callout: [t0, t1, x, y, w, h, text]. Times in seconds.
window.CLIPS = {
  rm: {
    kicker: 'RENTAL MANAGER · SCH. E',
    fps: 30, len: 57.5,
    scenes: [
      { img: 'rm-dash', t0: 0, t1: 13.6,
        head: ['Your Schedule E,', 'reconciled.'], sub: 'From a spreadsheet you own. Sample property shown.',
        cam: [[0, 720, 450, 1], [3.2, 720, 450, 1], [4.0, 540, 380, 1.75], [10.0, 540, 380, 1.75], [10.8, 1040, 380, 1.75], [12.4, 1040, 380, 1.75], [13.1, 720, 450, 1]],
        call: [
          [4.2, 7.4, 284, 268, 475, 55, 'Every Schedule E line, read from the workbook. Rents: $7,150 of $21,550 expected.'],
          [7.4, 10.1, 284, 398, 475, 55, 'Nothing booked yet? Last year’s figure shows, marked as waiting.'],
          [10.9, 12.5, 813, 240, 475, 249, 'Open items stay on screen. The workbook says what it still needs.']],
        cur: [[12.6, 900, 560], [13.35, 118, 460, 1]] },
      { img: 'rm-phone', t0: 13.6, t1: 20.6,
        head: ['Receipts from', 'your phone.'],
        cam: [[13.6, 720, 450, 1], [14.0, 720, 450, 1], [14.6, 640, 340, 1.3], [16.8, 640, 340, 1.3], [17.3, 886, 500, 1.3], [19.8, 886, 500, 1.3], [20.3, 720, 450, 1]],
        call: [
          [14.7, 17.0, 286, 262, 660, 160, 'Turn it on. The phone gets an address and a one-time code. Same Wi-Fi only.'],
          [17.3, 19.9, 1040, 548, 312, 180, 'Shoot a receipt. It lands in the inbox for Flow. A repeat photo is caught.']],
        cur: [[15.0, 700, 600], [16.2, 600, 540], [19.9, 700, 600], [20.45, 117, 208, 1]] },
      { img: 'rm-flow', t0: 20.6, t1: 30.2,
        head: ['Receipts in.', 'One click books.'],
        cam: [[20.6, 720, 450, 1], [21.2, 720, 450, 1], [21.9, 786, 560, 1.3], [28.6, 786, 560, 1.3], [29.2, 720, 450, 1]],
        call: [
          [22, 25.4, 286, 380, 1000, 70, 'Captured receipts become proposed rows. Nothing is booked until you click.'],
          [25.4, 28.6, 286, 639, 1000, 144, 'A field the rules could not read shows in red. You fill it first.']],
        cur: [[29.1, 800, 600], [29.95, 117, 259, 1]] },
      { img: 'rm-manage', t0: 30.2, t1: 37.4,
        head: ['Repairs, tenants,', 'vendors.'],
        cam: [[30.2, 720, 450, 1], [30.6, 720, 450, 1], [31.2, 786, 430, 1.3], [34.2, 786, 430, 1.3], [34.7, 786, 620, 1.3], [36.3, 786, 620, 1.3], [36.8, 720, 450, 1]],
        call: [
          [31.3, 34.3, 286, 283, 1000, 256, 'Each tenant issue keeps its thread: the report, the emails, the vendor, the line it books to.'],
          [34.7, 36.4, 286, 649, 1000, 135, 'Work orders carry the quote until the job closes.']],
        cur: [[36.5, 700, 700], [37.2, 117, 409, 1]] },
      { img: 'rm-mail', t0: 37.4, t1: 45.4,
        head: ['Replies drafted.', 'You send each one.'],
        cam: [[37.4, 720, 450, 1], [37.8, 720, 450, 1], [38.4, 786, 440, 1.3], [44.4, 786, 440, 1.3], [44.9, 720, 450, 1]],
        call: [
          [38.5, 41, 286, 310, 1000, 150, 'A reply to the tenant, drafted inside the thread. It shows who spoke last.'],
          [41, 42.9, 296, 476, 62, 36, 'Money words get a flag. Rent, deposits, invoices never go out on their own.'],
          [42.9, 44.6, 294, 681, 118, 42, 'Nothing leaves until you click. One click, one mail.']],
        cur: [[43, 700, 600], [43.9, 352, 702], [45.2, 117, 309, 1]] },
      { img: 'rm-org', t0: 45.4, t1: 53,
        head: ['Ready for', 'your preparer.'],
        cam: [[45.4, 720, 450, 1], [45.8, 720, 450, 1], [46.4, 560, 330, 1.6], [48.9, 560, 330, 1.6], [49.5, 786, 680, 1.3], [53, 786, 680, 1.3]],
        call: [
          [46.5, 49, 268, 186, 400, 66, 'Open questions, counted. Export the preparer package when it is clear.'],
          [49.6, 52.9, 266, 584, 1040, 304, 'Still needed: derived from this workbook, not a generic checklist.']],
        cur: [[47, 700, 420], [48.2, 356, 233]] },
    ],
    end: { t0: 53.0, title: ['Rental Manager', 'Sch. E'], lines: ['Local files. Deterministic math.', 'Replies wait for your click.'], cta: 'Testers wanted' },
  },

  ops: {
    kicker: 'OLIMAZI OPS · THE CUSTOM BUILD',
    fps: 30, len: 55.5,
    scenes: [
      { img: 'ops-flow', t0: 0, t1: 9.2,
        head: ['One hub runs', 'the whole brand.'], sub: 'Not technical by background. Built with Claude Code and Codex.',
        cam: [[0, 720, 450, 1], [3.0, 720, 450, 1], [3.7, 880, 400, 1.4], [8.2, 880, 400, 1.4], [8.7, 720, 450, 1]],
        call: [
          [3.8, 6.5, 456, 292, 918, 70, 'Photo in a folder → draft → review → publish. Every number read from its own source.'],
          [6.5, 8.3, 456, 496, 918, 70, 'Every local server probed live. A dead one reads grey, not green.']],
        cur: [[8.3, 700, 500], [9.0, 113, 18, 1]] },
      { img: 'ops-queue', t0: 9.2, t1: 16.4,
        head: ['Nothing posts', 'on its own.'],
        cam: [[9.2, 560, 333, 1.35], [16.4, 560, 333, 1.35]],
        call: [
          [9.7, 13.0, 266, 154, 800, 139, 'A photo dropped in a folder becomes a draft. It waits for a yes.'],
          [13.0, 15.6, 565, 307, 156, 42, 'Drafts waiting on one click. Approving makes a draft in the scheduler, never a post.']],
        cur: [[15.4, 640, 330], [16.2, 118, 336, 1]] },
      { img: 'ops-slides', t0: 16.4, t1: 24.4, swap: [18.8, 'ops-slides-b'],
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
        cur: [[30.8, 600, 500]] },
      { img: 'ops-skill', t0: 31.6, t1: 39.1,
        head: ['Run a skill,', 'one button.'],
        cam: [[31.6, 720, 450, 1], [32.0, 720, 450, 1], [32.6, 450, 470, 1.55], [35.4, 450, 470, 1.55], [35.9, 450, 600, 1.55], [37.9, 450, 600, 1.55], [38.4, 720, 450, 1]],
        call: [
          [32.7, 35.4, 289, 250, 322, 470, 'Finder. Say what you are building. It finds what people use this month and what hooks in.'],
          [35.9, 38.0, 306, 536, 288, 130, 'Pick the model and effort. It runs in the background. No chat window opens.']],
        cur: [[33.0, 640, 640], [34.2, 470, 500], [36.0, 560, 700], [36.7, 475, 590], [37.9, 329, 692], [38.85, 72, 298, 1]] },
      { img: 'ops-pulse', t0: 39.1, t1: 45.5,
        head: ['Every finished thing,', 'dated.'],
        cam: [[39.1, 720, 450, 1], [39.5, 720, 450, 1], [40.0, 700, 300, 1.45], [42.3, 700, 300, 1.45], [42.8, 838, 560, 1.2], [44.5, 838, 560, 1.2], [45.0, 720, 450, 1]],
        call: [
          [40.1, 42.4, 284, 246, 632, 72, '312 finished things in 90 days, read back from the record.'],
          [42.8, 44.6, 266, 420, 1144, 340, 'Where the work actually sat, hour by hour.']],
        cur: [[44.6, 600, 500], [45.3, 118, 375, 1]] },
      { img: 'ops-graph', t0: 45.5, t1: 51.5,
        head: ['A second brain', 'that shows its gaps.'],
        cam: [[45.5, 720, 450, 1], [45.9, 720, 450, 1], [46.5, 560, 250, 1.7], [51.5, 560, 250, 1.7]],
        call: [
          [46.6, 51.4, 262, 180, 395, 70, '138 files, 222 links. And the 11 nothing points at, in red.']],
        cur: [] },
    ],
    end: { t0: 51.5, title: ['Olimazi', 'ops'], lines: ['Planned in Claude Code.', 'Executed in Codex. Reviewed in Claude Code.'], cta: 'Learning in public' },
  },
};
