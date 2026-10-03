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
    fps: 30, len: 43.5,
    scenes: [
      { img: 'ops-flow', t0: 0, t1: 9.2,
        head: ['One hub runs', 'the whole brand.'], sub: 'Not technical by background. Planned, built and reviewed in separate passes.',
        cam: [[0, 720, 504, 1], [2.6, 720, 504, 1], [3.3, 880, 430, 1.4], [8.2, 880, 430, 1.4], [8.7, 720, 504, 1]],
        call: [
          [3.4, 6.0, 461, 297, 907, 62, 'Photo in a folder → draft → review → publish. Every number read from its own source.'],
          [6.0, 8.3, 461, 500, 907, 63, 'Every local server probed live. A dead one reads grey, not green.']],
        cur: [[8.3, 700, 500], [9.0, 110, 17, 1]] },
      { img: 'ops-queue', t0: 9.2, t1: 17,
        head: ['Nothing posts', 'on its own.'],
        cam: [[9.2, 560, 333, 1.35], [17, 560, 333, 1.35]],
        call: [
          [9.7, 12.2, 262, 192, 660, 28, 'A photo dropped in a folder becomes a draft. It waits for a yes.'],
          [12.2, 14.6, 565, 230, 154, 42, 'Drafts waiting on one click.'],
          [14.6, 16.5, 571, 690, 235, 28, 'Approving makes a draft in the scheduler, never a post.']],
        cur: [[15.6, 640, 500], [16.8, 74, 372, 1]] },
      { img: 'ops-slides', t0: 17, t1: 25.5, swap: [20.6, 'ops-slides-b'],
        head: ['Every slide,', 'editable.'],
        cam: [[17, 720, 504, 1], [17.4, 720, 504, 1], [18.0, 1000, 450, 1.45], [24.6, 1000, 450, 1.45], [25.1, 720, 504, 1]],
        call: [
          [18.1, 20.6, 1128, 484, 250, 64, 'Pick which words go red.'],
          [20.9, 24.4, 486, 320, 410, 172, 'The slide rebuilds live, in the brand type.']],
        cur: [[18.4, 1300, 640], [20.6, 1171, 530, 1], [24.4, 700, 700], [25.3, 50, 17, 1]] },
      { img: 'ops-pulse', t0: 25.5, t1: 32.5,
        head: ['Every finished thing,', 'on record.'],
        cam: [[25.5, 720, 504, 1], [25.9, 720, 504, 1], [26.5, 1000, 300, 1.45], [28.8, 1000, 300, 1.45], [29.4, 800, 620, 1.2], [31.8, 800, 620, 1.2], [32.2, 720, 504, 1]],
        call: [
          [26.6, 28.9, 1314, 108, 104, 30, 'Every finished thing, read back from disk. 483 so far.'],
          [29.5, 31.9, 289, 330, 1097, 520, 'One row per finished thing. Search by what it was for.']],
        cur: [[31.9, 600, 600], [32.4, 95, 370, 1]] },
      { img: 'ops-graph', t0: 32.5, t1: 39,
        head: ['A second brain', 'that shows its gaps.'],
        cam: [[32.5, 720, 504, 1], [32.9, 720, 504, 1], [33.5, 560, 250, 1.7], [35.8, 560, 250, 1.7], [36.4, 900, 700, 1.25], [39, 900, 700, 1.25]],
        call: [
          [33.6, 35.9, 282, 214, 396, 70, '158 files, 327 links. And the 8 nothing points at, in red.'],
          [36.5, 38.9, 1100, 535, 180, 70, 'The unlinked ones are listed, so nothing gets lost.']],
        cur: [] },
    ],
    end: { t0: 39, title: ['Olimazi', 'ops'], lines: ['Planned, built and reviewed', 'in separate passes.'], cta: 'Learning in public' },
  },
};
