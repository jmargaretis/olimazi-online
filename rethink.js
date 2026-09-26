/* rethink.js - motion for the night hero and the services strip.
   Every tween lives inside gsap.matchMedia with a reduced-motion guard,
   and nothing is hidden in CSS: with reduced motion, or if the CDN fails,
   the page renders complete and still. */
(function(){
  var hero = document.querySelector('.rh');
  if (!hero) return;
  var rmq = window.matchMedia('(prefers-reduced-motion: reduce)');
  var navbar = document.getElementById('navbar');

  /* ---- nav turns ink while it sits over the hero ---- */
  function navInk(){
    if (!navbar) return;
    var b = hero.getBoundingClientRect().bottom;
    navbar.classList.toggle('on-ink', b > navbar.offsetHeight + 4);
  }
  addEventListener('scroll', navInk, { passive: true });
  addEventListener('resize', navInk);
  navInk();

  /* ---- service clips: play only while on screen ---- */
  var svclips = [].slice.call(document.querySelectorAll('video.svclip'));
  if (rmq.matches || !('IntersectionObserver' in window)) {
    svclips.forEach(function(v){ v.controls = true; v.preload = 'metadata'; });
  } else {
    var sio = new IntersectionObserver(function(es){
      es.forEach(function(e){
        var v = e.target;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function(){}); } else v.pause();
      });
    }, { threshold: .35 });
    svclips.forEach(function(v){ sio.observe(v); });
  }

  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  var hasSplit = !!window.SplitText;
  if (hasSplit) gsap.registerPlugin(SplitText);

  var q = function(s, root){ return [].slice.call((root || document).querySelectorAll(s)); };
  var h1 = hero.querySelector('.rh-h1'), qm = hero.querySelector('.rh-q'),
      kicker = hero.querySelector('.rh-kicker'), kin = hero.querySelector('.rh-kin'),
      kinItems = q('.rh-kin-i', hero), kinK = hero.querySelector('.rh-kin-k'),
      lead = hero.querySelector('.rh-lead'), rows = q('.rh-card .row', hero),
      s3 = hero.querySelector('.rh-s3'), s3i = s3.querySelector('img'),
      wh = hero.querySelector('.rh-wheel'), whi = wh.querySelector('img'),
      grid = hero.querySelector('.rh-grid');

  var KC = [];
  function padMasks(s){ (s.masks || []).forEach(function(m){ m.classList.add('rh-mask'); }); }
  var MOTION ='(prefers-reduced-motion: no-preference)';
  var PIN = MOTION + ' and (min-width: 1024px) and (min-height: 640px)';

  function refreshSoon(){ ScrollTrigger.refresh(); }
  addEventListener('load', refreshSoon);
  q('img').forEach(function(im){ if (!im.complete) im.addEventListener('load', function(){ ScrollTrigger.refresh(); }, { once: true }); });

  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(start);

  function start(){
    var mm = gsap.matchMedia();

    /* ============ shared: the headline lands, the line re-sets ============ */
    mm.add(MOTION, function(){
      var words = [], kinChars = [];
      if (hasSplit) {
        var sh = SplitText.create(h1, { type: 'words', mask: 'words', wordsClass: 'rh-w' });
        words = sh.words; padMasks(sh);
        kin.classList.add('kin-on');
        kinChars = kinItems.map(function(el){ var s = SplitText.create(el, { type: 'chars', mask: 'chars' }); padMasks(s); return s.chars; });
      } else {
        words = q('.rh-l', h1);
      }
      /* the line under the headline: two of three labels wait below their mask */
      kinChars.forEach(function(c, i){ if (i) gsap.set(c, { yPercent: 115 }); });

      var intro = gsap.timeline({ defaults: { ease: 'expo.out' }, delay: .15 });
      intro.from(kicker, { y: 14, autoAlpha: 0, duration: .8 })
           .from(words, { yPercent: 118, duration: 1.1, stagger: .09 }, '<.1')
           .from(qm, { yPercent: -160, rotate: -24, scale: .4, duration: .9, ease: 'back.out(2.4)' }, '-=.55')
           .from(kinK, { x: -18, autoAlpha: 0, duration: .7 }, '-=.6');
      if (kinChars[0]) intro.from(kinChars[0], { yPercent: 115, duration: .7, stagger: .018 }, '-=.55');
      /* the strip light comes on: the S3 plate flickers up once */
      intro.fromTo(s3, { autoAlpha: 0 }, { keyframes: { autoAlpha: [0, .85, .12, .7, .3, 1] }, duration: 1.1, ease: 'none' }, .35);

      KC = kinChars;
      return function(){ KC = []; kin.classList.remove('kin-on'); };
    });

    /* ============ desktop: pinned, scrubbed story ============ */
    mm.add(PIN, function(){
      var tl = gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: hero, start: 'top top', end: '+=180%', pin: true, scrub: .6, anticipatePin: 1, invalidateOnRefresh: true }
      });
      /* beat 2 - the photo opens from a letterbox slit, the wheel slides under */
      tl.fromTo(s3, { clipPath: 'inset(16% 0% 16% 0% round 16px)', y: 40 }, { clipPath: 'inset(0% 0% 0% 0% round 16px)', y: 0, duration: 3, ease: 'power2.inOut' }, 0)
        .fromTo(s3i, { scale: 1.32, filter: 'brightness(.55)' }, { scale: 1.06, filter: 'brightness(1)', duration: 3.4, ease: 'power1.out' }, 0)
        .fromTo(wh, { xPercent: 38, yPercent: 60, clipPath: 'inset(0% 0% 100% 0% round 12px)' }, { xPercent: 0, yPercent: 0, clipPath: 'inset(0% 0% 0% 0% round 12px)', duration: 2.6, ease: 'power3.out' }, 1.2)
        .fromTo(whi, { scale: 1.4 }, { scale: 1, duration: 3.4, ease: 'power2.out' }, 1.2)
      /* depth: layers keep drifting at different speeds to the end */
        .to(s3, { y: -26, duration: 7 }, 3)
        .to(s3i, { scale: 1, duration: 7 }, 3.4)
        .to(wh, { yPercent: -34, duration: 5.4 }, 4.6)
        .to(h1, { y: -14, duration: 10 }, 0)
      /* beat 3 - the lead and the facts arrive */
        .fromTo(lead, { y: 34, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1.6, ease: 'power2.out' }, 1.8)
        .fromTo(rows, { y: 26, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1.2, stagger: .35, ease: 'power2.out' }, 3.6);
      /* the line re-sets: motion video -> custom AI operating systems -> web design */
      var chars = KC;
      if (chars.length === 3) {
        tl.to(chars[0], { yPercent: -115, stagger: .02, duration: .5, ease: 'power2.in' }, 2.4)
          .fromTo(chars[1], { yPercent: 115 }, { yPercent: 0, stagger: .015, duration: .6, ease: 'power3.out' }, 2.8)
          .to(chars[1], { yPercent: -115, stagger: .012, duration: .5, ease: 'power2.in' }, 5.6)
          .fromTo(chars[2], { yPercent: 115 }, { yPercent: 0, stagger: .02, duration: .6, ease: 'power3.out' }, 6.0);
      }
      /* beat 4 - hand-off: the stage settles back as the strip rises over it */
      tl.to(grid, { y: -30, scale: .985, transformOrigin: '50% 100%', duration: 2, ease: 'power1.in' }, 8)
        .to({}, { duration: .4 }, 10);
    });

    /* ============ phone / tablet / short screens: stacked, no pin ============ */
    mm.add(MOTION + ' and (max-width: 1023px), ' + MOTION + ' and (max-height: 639px)', function(){
      gsap.fromTo(s3i, { scale: 1.22, yPercent: -4 }, { scale: 1.02, yPercent: 4, ease: 'none',
        scrollTrigger: { trigger: s3, start: 'top bottom', end: 'bottom top', scrub: .6 } });
      gsap.fromTo(wh, { yPercent: 30 }, { yPercent: -12, ease: 'none',
        scrollTrigger: { trigger: s3, start: 'top bottom', end: 'bottom top', scrub: .6 } });
      gsap.fromTo(whi, { scale: 1.3 }, { scale: 1, ease: 'none',
        scrollTrigger: { trigger: wh, start: 'top bottom', end: 'bottom 30%', scrub: .6 } });
      gsap.from(lead, { y: 24, autoAlpha: 0, duration: .9, ease: 'power2.out', delay: .6 });
      gsap.from(rows, { y: 20, autoAlpha: 0, duration: .7, stagger: .08, ease: 'power2.out',
        scrollTrigger: { trigger: '.rh-card', start: 'top 88%', once: true } });
      var chars = KC;
      if (chars.length === 3) {
        var kt = gsap.timeline({ defaults: { ease: 'none' },
          scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom 40%', scrub: .6 } });
        kt.to(chars[0], { yPercent: -115, stagger: .02, duration: .5 }, 1)
          .fromTo(chars[1], { yPercent: 115 }, { yPercent: 0, stagger: .012, duration: .6 }, 1.3)
          .to(chars[1], { yPercent: -115, stagger: .012, duration: .5 }, 3)
          .fromTo(chars[2], { yPercent: 115 }, { yPercent: 0, stagger: .02, duration: .6 }, 3.3)
          .to({}, { duration: 1 }, 4);
      }
    });

    /* ============ services strip: staggered entrance ============ */
    mm.add(MOTION, function(){
      var head = document.querySelector('.svc-head h2');
      if (hasSplit && head) {
        var hs = SplitText.create(head, { type: 'words', mask: 'words' }); padMasks(hs);
        gsap.from(hs.words, { yPercent: 115, duration: 1, stagger: .07, ease: 'expo.out',
          scrollTrigger: { trigger: head, start: 'top 85%', once: true } });
      }
      gsap.from('.svc-head .aside', { autoAlpha: 0, x: 20, duration: .9, ease: 'power2.out',
        scrollTrigger: { trigger: '.svc-head', start: 'top 85%', once: true } });
      q('.svc-tile').forEach(function(t, i){
        gsap.from(t, { y: 90, rotateX: 10, autoAlpha: 0, duration: 1.2, delay: (i % 3) * .12, ease: 'expo.out', transformOrigin: '50% 100%',
          scrollTrigger: { trigger: t, start: 'top 92%', once: true } });
        var m = t.querySelector('video, img');
        gsap.fromTo(m, { scale: 1.14 }, { scale: 1, duration: 1.6, delay: (i % 3) * .12, ease: 'expo.out',
          scrollTrigger: { trigger: t, start: 'top 92%', once: true } });
      });
    });

    /* ============ fine pointer: tile tilt with depth ============ */
    mm.add(MOTION + ' and (hover: hover) and (pointer: fine)', function(){
      var offs = [];
      q('.svc-tile').forEach(function(t){
        var rx = gsap.quickTo(t, 'rotationX', { duration: .6, ease: 'power3.out' }),
            ry = gsap.quickTo(t, 'rotationY', { duration: .6, ease: 'power3.out' }),
            m = t.querySelector('.svc-media > *'),
            mx = gsap.quickTo(m, 'xPercent', { duration: .8, ease: 'power3.out' }),
            my = gsap.quickTo(m, 'yPercent', { duration: .8, ease: 'power3.out' });
        function move(e){
          var r = t.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
          ry(x * 9); rx(-y * 7); mx(-x * 3); my(-y * 3);
        }
        function leave(){ rx(0); ry(0); mx(0); my(0); }
        t.addEventListener('pointermove', move); t.addEventListener('pointerleave', leave);
        offs.push(function(){ t.removeEventListener('pointermove', move); t.removeEventListener('pointerleave', leave); gsap.set([t, m], { clearProps: 'transform' }); });
      });
      return function(){ offs.forEach(function(f){ f(); }); };
    });

    ScrollTrigger.refresh();
  }
})();
