/* motion.js — the motion comp layer (GSAP 3.13 + ScrollTrigger + SplitText).
   Everything animates FROM a hidden state inside a no-preference media
   query, so with reduced motion (or no GSAP at all) the page is the live one. */
(function () {
  if (!window.gsap || !window.ScrollTrigger) return;
  var gsap = window.gsap, ST = window.ScrollTrigger, Split = window.SplitText;
  gsap.registerPlugin(ST);
  if (Split) gsap.registerPlugin(Split);

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var EASE = 'expo.out';

  function split(el, type, mask) {
    if (!Split || !el) return null;
    return Split.create(el, { type: type, mask: mask, linesClass: 'mo-line', wordsClass: 'mo-word', charsClass: 'mo-char' });
  }

  function build() {
    var mm = gsap.matchMedia();

    mm.add({
      motion: '(prefers-reduced-motion: no-preference)',
      fine: '(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)',
      wide: '(min-width: 901px) and (prefers-reduced-motion: no-preference)'
    }, function (ctx) {
      var c = ctx.conditions;
      if (!c.motion) return;

      /* ---------- scroll progress ---------- */
      gsap.to('.mo-progress i', { scaleX: 1, ease: 'none',
        scrollTrigger: { trigger: document.documentElement, start: 0, end: 'max', scrub: .3 } });

      /* ---------- nav: drops in, then tracks the current section ---------- */
      gsap.from('.nav .mark, .nav li', { y: -18, opacity: 0, duration: .9, ease: EASE, stagger: .06, delay: .1 });
      var navUl = $('.nav ul');
      if (navUl) {
        var bar = document.createElement('i'); bar.className = 'mo-navbar'; navUl.appendChild(bar);
        var moveBar = function (a) {
          if (!a) { gsap.to(bar, { opacity: 0, duration: .3 }); return; }
          var ur = navUl.getBoundingClientRect(), ar = a.getBoundingClientRect();
          gsap.to(bar, { x: ar.left - ur.left, width: ar.width, opacity: 1, duration: .6, ease: 'power3.out' });
        };
        ['work', 'learning', 'library'].forEach(function (id) {
          var link = $('.nav a[href="#' + id + '"]'), sec = document.getElementById(id);
          if (!link || !sec) return;
          ST.create({ trigger: sec, start: 'top 45%', end: 'bottom 45%',
            onToggle: function (self) { if (self.isActive) moveBar(link); else if (!ST.getAll().some(function (t) { return t.vars.__nav && t.isActive; })) moveBar(null); },
            __nav: true });
        });
      }

      /* ---------- hero: entrance choreography ---------- */
      var hero = $('.hero'), h1 = $('.hero h1');
      var tl = gsap.timeline({ defaults: { ease: EASE }, delay: .15 });
      var kick = split($('.hero .kicker'), 'chars');
      if (kick) tl.from(kick.chars, { opacity: 0, y: 8, duration: .5, stagger: .018 }, 0);
      var hs = split(h1, 'words,chars', 'chars');
      var q = $('.hero h1 .q');
      if (hs) {
        var body = hs.chars.filter(function (ch) { return !q || !q.contains(ch); });
        tl.from(body, { yPercent: 115, rotateX: -70, duration: 1.1, stagger: .028 }, .1);
      }
      if (q) {
        tl.from(q, { yPercent: -160, rotation: -24, opacity: 0, duration: .9, ease: 'bounce.out' }, .95)
          .fromTo(q, { scale: 1 }, { scale: 1.18, duration: .18, yoyo: true, repeat: 1, ease: 'power2.inOut' }, 1.75);
      }
      tl.from('.hero .rule', { scaleX: 0, duration: .9, ease: 'expo.inOut' }, .85);
      var leadS = split($('.hero .lead'), 'lines', 'lines');
      if (leadS) tl.from(leadS.lines, { yPercent: 105, duration: .95, stagger: .07 }, 1.0);
      tl.from('.hero .lead2', { y: 14, opacity: 0, duration: .8 }, 1.25);
      var asideS = split($('.hero .aside'), 'chars');
      if (asideS) tl.from(asideS.chars, { opacity: 0, duration: .01, stagger: .022, ease: 'none' }, 1.4);
      tl.from('.brandcard', { opacity: 0, duration: .01 }, 1.05)
        .from('.brandcard .row', { x: 28, opacity: 0, duration: .8, stagger: .07 }, 1.05)
        .from('.brandcard .row .k', { color: 'rgba(22,32,42,0)', duration: .6, stagger: .07 }, 1.2);

      /* ---------- hero: the headline lets go as you scroll ---------- */
      if (hs) {
        /* words carry the exit, chars carry the entrance: no shared props */
        var n = hs.words.length;
        gsap.to(hs.words, {
          yPercent: function (i) { return -40 - 90 * Math.abs(i - n / 2) / n; },
          rotateX: 55, opacity: 0, ease: 'none',
          stagger: { each: .06, from: 'center' },
          scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom 15%', scrub: .6 }
        });
      }
      gsap.to(hero, { y: function () { return hero.offsetHeight * .38; }, ease: 'none',
        scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true, invalidateOnRefresh: true } });
      gsap.to('.hero .hgrid', { y: -60, opacity: .15, ease: 'none',
        scrollTrigger: { trigger: hero, start: '20% top', end: 'bottom top', scrub: .6 } });

      /* ---------- section headings: kinetic type ---------- */
      $$('.sh h2, .learn .hub h2, .lib .head h2, footer h2').forEach(function (h) {
        var s = split(h, 'words,chars', 'words');
        if (!s) return;
        gsap.from(s.words, { yPercent: 110, duration: 1.1, ease: EASE, stagger: .06,
          scrollTrigger: { trigger: h, start: 'top 88%', once: true } });
      });
      $$('.sh .aside, .lib .head .hand').forEach(function (a) {
        var s = split(a, 'chars');
        if (!s) return;
        gsap.from(s.chars, { opacity: 0, duration: .01, stagger: .02, ease: 'none',
          scrollTrigger: { trigger: a, start: 'top 90%', once: true } });
      });

      /* ---------- work cards: wipe in, image parallax ---------- */
      $$('.work .card').forEach(function (card, i) {
        var ph = $('.ph', card);
        gsap.fromTo(ph, { clipPath: 'inset(100% 0% 0% 0% round 12px)' },
          { clipPath: 'inset(0% 0% 0% 0% round 12px)', duration: 1.3, ease: 'expo.inOut', delay: i * .12,
            scrollTrigger: { trigger: card, start: 'top 85%', once: true } });
        gsap.from($('.on', card), { y: 30, opacity: 0, duration: 1, ease: EASE, delay: .55 + i * .12,
          scrollTrigger: { trigger: card, start: 'top 85%', once: true } });
        gsap.fromTo(ph, { '--py': '-6%' }, { '--py': '6%', ease: 'none',
          scrollTrigger: { trigger: card, start: 'top bottom', end: 'bottom top', scrub: true } });
      });

      /* ---------- learning: the hub clip opens, lessons roll in ---------- */
      var fig = $('.learn .hub figure');
      if (fig) {
        gsap.fromTo(fig, { clipPath: 'inset(12% 18% 12% 18% round 28px)', scale: .92 },
          { clipPath: 'inset(0% 0% 0% 0% round 12px)', scale: 1, ease: 'none',
            scrollTrigger: { trigger: fig, start: 'top 95%', end: 'top 35%', scrub: .6 } });
      }
      var hubP = $('.learn .hub p');
      var hp = split(hubP, 'lines', 'lines');
      if (hp) gsap.from(hp.lines, { yPercent: 105, duration: 1, ease: EASE, stagger: .06,
        scrollTrigger: { trigger: hubP, start: 'top 88%', once: true } });
      $$('.lip .lesson').forEach(function (li, i) {
        var num = $('.num', li), em = $('em', li);
        var tl2 = gsap.timeline({ scrollTrigger: { trigger: '.lip', start: 'top 82%', once: true }, delay: i * .12 });
        if (num) {
          var target = +num.textContent, o = { v: 0 };
          tl2.to(o, { v: target, duration: .7, ease: 'power2.out',
            onUpdate: function () { num.textContent = (o.v < 9.5 ? '0' : '') + Math.round(o.v); } }, 0);
          tl2.from(num, { yPercent: 100, opacity: 0, duration: .6, ease: EASE }, 0);
        }
        if (em) tl2.from(em, { x: -16, opacity: 0, duration: .8, ease: EASE }, .25);
      });

      /* ---------- library: the band opens like a sheet, shelves deal in ---------- */
      var band = $('.lib .band');
      if (band) {
        gsap.fromTo(band, { clipPath: 'inset(0% 5% 0% 5% round 32px)' },
          { clipPath: 'inset(0% 0% 0% 0% round 0px)', ease: 'none',
            scrollTrigger: { trigger: band, start: 'top bottom', end: 'top 30%', scrub: .6 } });
      }
      var hp2 = split($('.lib .head p'), 'lines', 'lines');
      if (hp2) gsap.from(hp2.lines, { yPercent: 105, duration: 1, ease: EASE, stagger: .06,
        scrollTrigger: { trigger: '.lib .head p', start: 'top 88%', once: true } });
      var shelves = $$('#strip .shelf');
      gsap.from(shelves, { y: 90, rotateY: -18, opacity: 0, transformPerspective: 900, duration: 1.2, ease: EASE,
        stagger: .07, clearProps: 'transform,opacity',
        scrollTrigger: { trigger: '#strip', start: 'top 88%', once: true } });
      gsap.fromTo('#strip', { x: 40 }, { x: -40, ease: 'none',
        scrollTrigger: { trigger: '.strip-wrap', start: 'top bottom', end: 'bottom top', scrub: .8 } });
      gsap.from('.lib .links .vault', { y: 30, opacity: 0, duration: 1, ease: EASE,
        scrollTrigger: { trigger: '.lib .links', start: 'top 92%', once: true } });

      /* ---------- footer: the red i drops into place ---------- */
      var fi = $('footer h2 .ox');
      if (fi) gsap.from(fi, { yPercent: -220, opacity: 0, duration: 1, ease: 'bounce.out', delay: .5,
        scrollTrigger: { trigger: 'footer', start: 'top 70%', once: true } });
      gsap.from('footer .acts > *', { y: 24, opacity: 0, duration: .9, ease: EASE, stagger: .08,
        scrollTrigger: { trigger: 'footer .acts', start: 'top 95%', once: true } });
      gsap.from('footer .av', { rotation: -120, scale: .4, opacity: 0, duration: 1.1, ease: 'back.out(2)',
        scrollTrigger: { trigger: 'footer .row', start: 'top 98%', once: true } });

      /* ---------- fine pointers: cursor-aware light, tilt, magnets ---------- */
      if (c.fine) {
        var spot = document.createElement('div'); spot.className = 'mo-spot'; spot.setAttribute('aria-hidden', 'true');
        var glow = document.createElement('div'); glow.className = 'mo-glow'; glow.setAttribute('aria-hidden', 'true');
        hero.prepend(glow); hero.prepend(spot);
        var mx = gsap.quickTo(hero, '--mx', { duration: .6, ease: 'power3' });
        var my = gsap.quickTo(hero, '--my', { duration: .6, ease: 'power3' });
        gsap.set(hero, { '--mx': hero.offsetWidth / 2, '--my': hero.offsetHeight * .4 });
        var qx = q && gsap.quickTo(q, 'x', { duration: .8, ease: 'power3' });
        var qy = q && gsap.quickTo(q, 'y', { duration: .8, ease: 'power3' });
        var onHero = function (e) {
          var r = hero.getBoundingClientRect();
          mx(e.clientX - r.left); my(e.clientY - r.top);
          spot.classList.add('on'); glow.classList.add('on');
          if (q) {
            var qr = q.getBoundingClientRect(), dx = e.clientX - (qr.left + qr.width / 2), dy = e.clientY - (qr.top + qr.height / 2);
            var d = Math.hypot(dx, dy), k = Math.max(0, 1 - d / 420);
            qx(dx * .06 * k); qy(dy * .06 * k);
          }
        };
        hero.addEventListener('pointermove', onHero);
        hero.addEventListener('pointerleave', function () { spot.classList.remove('on'); glow.classList.remove('on'); if (q) { qx(0); qy(0); } });

        var tilt = function (host, face, max) {
          var glare = document.createElement('span'); glare.className = 'mo-glare'; glare.setAttribute('aria-hidden', 'true');
          face.appendChild(glare);
          gsap.set(face, { '--rx': 0, '--ry': 0 });
          var rx = gsap.quickTo(face, '--rx', { duration: .5, ease: 'power3' });
          var ry = gsap.quickTo(face, '--ry', { duration: .5, ease: 'power3' });
          host.addEventListener('pointermove', function (e) {
            var r = face.getBoundingClientRect(), px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
            rx((.5 - py) * max); ry((px - .5) * max);
            face.style.setProperty('--gx', (px * 100) + '%'); face.style.setProperty('--gy', (py * 100) + '%');
          });
          host.addEventListener('pointerleave', function () { rx(0); ry(0); });
        };
        $$('.work .card').forEach(function (card) { tilt(card, $('.ph', card), 7); });
        $$('#strip button.shelf').forEach(function (s) { var f = $('figure', s); if (f) tilt(s, f, 10); });

        $$('footer .cta, .nav .mark, .lib .links .vault').forEach(function (el) {
          el.classList.add('mo-mag');
          var xTo = gsap.quickTo(el, 'x', { duration: .5, ease: 'power3' }), yTo = gsap.quickTo(el, 'y', { duration: .5, ease: 'power3' });
          el.addEventListener('pointermove', function (e) {
            var r = el.getBoundingClientRect();
            xTo((e.clientX - r.left - r.width / 2) * .25); yTo((e.clientY - r.top - r.height / 2) * .35);
          });
          el.addEventListener('pointerleave', function () { xTo(0); yTo(0); });
        });
      }

      /* wide screens: the hero columns drift apart a touch while leaving */
      if (c.wide) {
        gsap.to('.brandcard', { y: -50, ease: 'none',
          scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: .8 } });
      }
    });

    window.addEventListener('load', function () { ST.refresh(); });
  }

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(build); else build();
})();
