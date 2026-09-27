/* rethink.js - motion for the night hero and the services strip.
   Every tween lives inside gsap.matchMedia with a reduced-motion guard,
   and nothing is hidden in CSS: with reduced motion, or if the CDN fails,
   the page renders complete and still. */
/* ---- round 3: small details that need no library ----
   Buttons, underlines, the nav indicator, the scroll hairline and the copy
   button. Plain JS, so they still work if the GSAP CDN fails. */
(function(){
  var doc = document.documentElement;
  var CTA = '.svc-cta, footer .cta, .ccard .btn, .pane .btn';
  var q = function(s, r){ return [].slice.call((r || document).querySelectorAll(s)); };

  /* primary buttons: label in a span, arrow becomes a pair that swaps */
  q(CTA).forEach(function(b){
    var old = b.querySelector('i'); if (old) old.remove();
    var txt = b.textContent.replace(/\s*→\s*$/, '').trim();
    b.textContent = '';
    var l = document.createElement('span'); l.className = 'cta-l'; l.textContent = txt;
    var a = document.createElement('span'); a.className = 'ar'; a.setAttribute('aria-hidden', 'true');
    a.innerHTML = '<span>→</span><span>→</span>';
    b.appendChild(l); b.appendChild(a);
    /* the red fill grows from where the pointer crossed the edge, and shrinks back out the way it leaves */
    function at(e){
      var r = b.getBoundingClientRect();
      b.style.setProperty('--fx', (e.clientX - r.left) + 'px');
      b.style.setProperty('--fy', (e.clientY - r.top) + 'px');
      b.style.setProperty('--fd', Math.ceil(Math.hypot(r.width, r.height) * 2 + 8) + 'px');
    }
    b.addEventListener('pointerenter', at); b.addEventListener('pointerleave', at);
  });

  /* drawn underline: the line starts on the side the pointer came in from */
  function side(el, e){ var r = el.getBoundingClientRect(); return (e.clientX - r.left) < r.width / 2 ? 'left' : 'right'; }
  q('.u').forEach(function(u){
    u.addEventListener('pointerenter', function(e){ u.style.setProperty('--uo', side(u, e)); });
    u.addEventListener('pointerleave', function(e){ u.style.setProperty('--uo', side(u, e)); });
  });
  q('.card').forEach(function(c){
    var u = c.querySelector('.u'); if (!u) return;
    c.addEventListener('pointerenter', function(e){ u.style.setProperty('--uo', side(c, e)); });
    c.addEventListener('pointerleave', function(e){ u.style.setProperty('--uo', side(c, e)); });
  });

  /* scroll hairline + nav indicator share one rAF */
  var bar = document.createElement('div'); bar.className = 'sp'; bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  var navbar = document.getElementById('navbar'), nav = navbar && navbar.querySelector('.nav'),
      ul = nav && nav.querySelector('ul'), ind = null, links = [];
  if (ul) {
    ind = document.createElement('i'); ind.className = 'nav-ind'; ind.setAttribute('aria-hidden', 'true'); ul.appendChild(ind);
    links = q('a.u[href^="#"]', ul).map(function(a){ return { a: a, s: document.getElementById(a.getAttribute('href').slice(1)) }; })
      .filter(function(o){ return o.s; });
  }
  /* the stuck bar height: content + 14px padding top and bottom + the 1px hairline */
  function navh(){
    if (!nav) return;
    var cs = getComputedStyle(nav);
    var h = nav.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom) + 28 + 1;
    doc.style.setProperty('--navh', Math.round(h) + 'px');
  }
  var cur = null, raf = 0;
  function place(){
    if (!ind) return;
    if (!cur) { ind.classList.remove('on'); return; }
    var ur = ul.getBoundingClientRect(), r = cur.a.getBoundingClientRect();
    ind.style.transform = 'translateX(' + (r.left - ur.left) + 'px) scaleX(' + (r.width / 100) + ')';
    ind.classList.add('on');
  }
  function tick(){
    raf = 0;
    var max = doc.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0) + ')';
    var line = (navbar ? navbar.offsetHeight : 0) + innerHeight * .3, hit = null;
    links.forEach(function(o){ if (o.s.getBoundingClientRect().top <= line) hit = o; });
    if (hit && links[links.length - 1] !== hit && hit.s.getBoundingClientRect().bottom < line) hit = null;
    if (hit !== cur) {
      if (cur) cur.a.removeAttribute('aria-current');
      cur = hit;
      if (cur) cur.a.setAttribute('aria-current', 'location');
      place();
    }
  }
  function soon(){ if (!raf) raf = requestAnimationFrame(tick); }
  addEventListener('scroll', soon, { passive: true });
  addEventListener('resize', function(){ navh(); place(); soon(); });
  addEventListener('load', function(){ navh(); place(); soon(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ navh(); place(); });
  navh(); tick();

  /* a nav jump that ends a few px off (a late layout refresh) settles onto its mark */
  var pending = null;
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    pending = a ? document.getElementById(a.getAttribute('href').slice(1)) : null;
  });
  addEventListener('scrollend', function(){
    if (!pending) return;
    var s = pending; pending = null;
    var d = s.getBoundingClientRect().top - (parseFloat(getComputedStyle(s).scrollMarginTop) || 0);
    if (Math.abs(d) > 3) scrollBy({ top: d, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });

  /* copy the address: one click, a crisp "Copied", read out once */
  var live = document.createElement('span'); live.setAttribute('aria-live', 'polite');
  live.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap';
  document.body.appendChild(live);
  function write(t){
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t);
    return new Promise(function(ok, no){
      var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(ta); ta.select();
      var done = false; try { done = document.execCommand('copy'); } catch (e) {}
      ta.remove(); done ? ok() : no();
    });
  }
  q('[data-copy]').forEach(function(b){
    var tm = 0;
    b.addEventListener('click', function(e){
      e.preventDefault(); e.stopPropagation();
      write(b.getAttribute('data-copy')).then(function(){
        b.classList.add('done'); live.textContent = ''; setTimeout(function(){ live.textContent = 'Copied'; }, 30);
        clearTimeout(tm); tm = setTimeout(function(){ b.classList.remove('done'); }, 1800);
      }, function(){});
    });
  });
})();

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

  /* a refresh mid-scroll cancels a smooth nav jump (the lazy library images
     load on the way down), so refreshes wait until the page is still */
  var lastScroll = 0, rt = 0;
  addEventListener('scroll', function(){ lastScroll = performance.now(); }, { passive: true });
  function refreshSoon(){
    clearTimeout(rt);
    rt = setTimeout(function again(){
      if (performance.now() - lastScroll < 250) { rt = setTimeout(again, 250); return; }
      ScrollTrigger.refresh();
    }, 150);
  }
  addEventListener('load', refreshSoon);
  q('img').forEach(function(im){ if (!im.complete) im.addEventListener('load', refreshSoon, { once: true }); });

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
      /* the lead and the facts land with the headline: the first screen is complete at rest */
      intro.from(lead, { y: 26, autoAlpha: 0, duration: 1 }, 1.0)
           .from(rows, { y: 18, autoAlpha: 0, duration: .8, stagger: .07 }, 1.25);

      /* the garage light passes: a lit copy of the S3 wipes across a dark plate behind a soft beam */
      var lit = s3i.cloneNode(); lit.className = 'rh-lit'; lit.removeAttribute('fetchpriority');
      var beam = document.createElement('span'); beam.className = 'rh-beam';
      s3.appendChild(lit); s3.appendChild(beam); s3.classList.add('sweep');
      /* the sweep waits for the photo to decode, so it never runs over an empty plate */
      var sweep = gsap.timeline({ paused: true });
      sweep.fromTo(s3, { autoAlpha: 0 }, { keyframes: { autoAlpha: [0, .7, .2, 1] }, duration: .6, ease: 'none', immediateRender: true }, 0)
           .fromTo(lit, { clipPath: 'inset(0% 100% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.9, ease: 'power2.inOut', immediateRender: true }, .45)
           .fromTo(beam, { xPercent: -120, autoAlpha: 1 }, { xPercent: 560, duration: 1.9, ease: 'power2.inOut', immediateRender: true }, .45)
           .to(beam, { autoAlpha: 0, duration: .5, ease: 'none' }, 2.0);
      var ready = (lit.decode ? lit.decode() : Promise.resolve()).catch(function(){});
      Promise.race([ready, new Promise(function(r){ setTimeout(r, 2500); })]).then(function(){ gsap.delayedCall(.35, function(){ sweep.play(); }); });
      intro.from(wh, { xPercent: 22, yPercent: 26, clipPath: 'inset(0% 0% 100% 0% round 12px)', duration: 1.3, ease: 'expo.out' }, 1.5)
           .from(whi, { scale: 1.35, duration: 1.8, ease: 'expo.out' }, 1.5);

      KC = kinChars;
      return function(){ KC = []; kin.classList.remove('kin-on'); s3.classList.remove('sweep'); lit.remove(); beam.remove(); };
    });

    /* ============ desktop: pinned, scrubbed story ============ */
    mm.add(PIN, function(){
      var tl = gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: hero, start: 'top top', end: '+=180%', pin: true, scrub: .6, anticipatePin: 1, invalidateOnRefresh: true,
          onUpdate: function(s){ window.__rhScroll = s.progress; } }
      });
      /* one camera move: push in on the car, layers drift at their own depth, then pull back */
      var copy = hero.querySelector('.rh-copy'), card = hero.querySelector('.rh-card');
      tl.fromTo(s3, { scale: 1 }, { scale: 1.06, y: -30, duration: 7, ease: 'power1.inOut' }, 0)
        .fromTo(s3.querySelectorAll('img'), { scale: 1.12 }, { scale: 1, duration: 7, ease: 'power1.out' }, 0)
        .fromTo(wh, { yPercent: 0, xPercent: 0 }, { yPercent: -46, xPercent: -8, duration: 7 }, 0)
        .to(copy, { y: -20, duration: 8 }, 0)
        .to(card, { y: -10, duration: 8 }, 0);
      /* the line re-sets: motion video -> custom AI operating systems -> web design */
      var chars = KC;
      if (chars.length === 3) {
        tl.to(chars[0], { yPercent: -115, stagger: .02, duration: .5, ease: 'power2.in' }, 2.4)
          .fromTo(chars[1], { yPercent: 115 }, { yPercent: 0, stagger: .015, duration: .6, ease: 'power3.out' }, 2.8)
          .to(chars[1], { yPercent: -115, stagger: .012, duration: .5, ease: 'power2.in' }, 5.6)
          .fromTo(chars[2], { yPercent: 115 }, { yPercent: 0, stagger: .02, duration: .6, ease: 'power3.out' }, 6.0);
      }
      /* beat 4 - hand-off: the stage settles back as the strip rises over it */
      tl.to(grid, { y: -70, scale: .9, autoAlpha: .35, transformOrigin: '50% 60%', duration: 2.6, ease: 'power2.in' }, 7.4)
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

    /* ============ the camera keeps moving: services tilt up into view, lift away, work follows ============ */
    mm.add(MOTION, function(){
      var sg = document.querySelector('.svc-grid'), svc = document.querySelector('.svc');
      if (sg) {
        gsap.fromTo(sg, { rotationX: 14, y: 110, scale: .94, transformOrigin: '50% 0%', transformPerspective: 1400 },
          { rotationX: 0, y: 0, scale: 1, ease: 'none', scrollTrigger: { trigger: svc, start: 'top bottom', end: 'top 20%', scrub: .8 } });
        var lifts = [-40, -110, -70];
        q('.svc-tile').forEach(function(t, i){
          gsap.fromTo(t, { '--lift': '0px' }, { '--lift': (innerWidth > 900 ? lifts[i % 3] : -30) + 'px', ease: 'none',
            scrollTrigger: { trigger: sg, start: 'bottom 85%', end: 'bottom top', scrub: .8, invalidateOnRefresh: true } });
        });
      }
      var ww = document.querySelector('#work > .wrap');
      if (ww) gsap.fromTo(ww, { y: 120, scale: .95, transformOrigin: '50% 0%' },
        { y: 0, scale: 1, ease: 'none', scrollTrigger: { trigger: '#work', start: 'top bottom', end: 'top 25%', scrub: .8 } });
    });

    /* ============ fine pointer: primary buttons lean toward the cursor, the label a touch further ============ */
    mm.add(MOTION + ' and (hover: hover) and (pointer: fine)', function(){
      var offs = [];
      q('.svc-cta, footer .cta, .ccard .btn, .pane .btn').forEach(function(b){
        var l = b.querySelector('.cta-l'),
            bx = gsap.quickTo(b, 'x', { duration: .5, ease: 'power3.out' }), by = gsap.quickTo(b, 'y', { duration: .5, ease: 'power3.out' }),
            lx = l && gsap.quickTo(l, 'x', { duration: .5, ease: 'power3.out' }), ly = l && gsap.quickTo(l, 'y', { duration: .5, ease: 'power3.out' });
        function move(e){
          var r = b.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
          bx(dx * .14); by(dy * .22); if (l) { lx(dx * .07); ly(dy * .09); }
        }
        function leave(){
          gsap.to(l ? [b, l] : b, { x: 0, y: 0, duration: .7, ease: 'elastic.out(1, .5)', overwrite: true });
        }
        b.addEventListener('pointermove', move); b.addEventListener('pointerleave', leave);
        offs.push(function(){ b.removeEventListener('pointermove', move); b.removeEventListener('pointerleave', leave); gsap.set(l ? [b, l] : b, { clearProps: 'transform' }); });
      });
      return function(){ offs.forEach(function(f){ f(); }); };
    });

    /* ============ fine pointer: library pictures lean toward the cursor (never mid-drag) ============ */
    mm.add(MOTION + ' and (hover: hover) and (pointer: fine)', function(){
      var offs = [], strip = document.getElementById('strip');
      q('button.shelf').forEach(function(s){
        var f = s.querySelector('figure'); if (!f) return;
        gsap.set(f, { transformPerspective: 700 });
        var rx = gsap.quickTo(f, 'rotationX', { duration: .6, ease: 'power3.out' }), ry = gsap.quickTo(f, 'rotationY', { duration: .6, ease: 'power3.out' });
        function move(e){
          if (strip && strip.classList.contains('drag')) { rx(0); ry(0); return; }
          var r = f.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
          ry(x * 10); rx(-y * 8);
        }
        function leave(){ rx(0); ry(0); }
        s.addEventListener('pointermove', move, { passive: true }); s.addEventListener('pointerleave', leave);
        offs.push(function(){ s.removeEventListener('pointermove', move); s.removeEventListener('pointerleave', leave); gsap.set(f, { clearProps: 'transform' }); });
      });
      return function(){ offs.forEach(function(f){ f(); }); };
    });

    /* ============ desktop pointer: haze follows, cursor ring ============ */
    mm.add(MOTION, function(){ return haze(); });
    mm.add(MOTION + ' and (hover: hover) and (pointer: fine)', function(){ return ring(); });

    ScrollTrigger.refresh();
  }

  /* ---- ambient sodium haze: one raw-WebGL quad at half resolution, paused off screen ---- */
  function haze(){
    var cv = document.createElement('canvas'); cv.className = 'rh-haze'; cv.setAttribute('aria-hidden', 'true');
    var gl = cv.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
    if (!gl) return;
    hero.insertBefore(cv, hero.firstChild);
    var vs = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
    var fs = [
      'precision mediump float;uniform vec2 R;uniform float T;uniform vec2 M;uniform float S;uniform float A;',
      'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
      'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
      'float fb(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return v;}',
      'void main(){vec2 uv=gl_FragCoord.xy/R;float k=R.x/R.y;vec2 p=vec2(uv.x*k,uv.y);float t=T*.035;',
      ' float w=fb(p*1.4+vec2(t,-t*.3));float f=fb(p*1.1+w*1.3+vec2(-t*.7,t*.25));',
      /* slanted shafts from strip lights above, slowly breathing */
      ' float sx=uv.x*k+(1.-uv.y)*.55;float sh=pow(.5+.5*sin(sx*5.2+sin(T*.05)*1.2),10.)*smoothstep(.15,1.,uv.y);',
      ' vec2 m=vec2(M.x*k,M.y);float d=distance(p,m);float pool=exp(-d*d*5.5);',
      ' float top=smoothstep(.2,1.,uv.y);',
      ' float I=f*(.32*top+1.05*pool)+sh*f*.75;I*=(.7+.6*S)*A;',
      ' vec3 c=vec3(1.,.83,.62)*I*.34+vec3(.95,.97,1.)*pool*.02*A;',
      ' gl_FragColor=vec4(c,1.);}'
    ].join('\n');
    function sh(t, s){ var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; }
    var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { cv.remove(); return; }
    gl.useProgram(pr);
    var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var uR = gl.getUniformLocation(pr, 'R'), uT = gl.getUniformLocation(pr, 'T'), uM = gl.getUniformLocation(pr, 'M'),
        uS = gl.getUniformLocation(pr, 'S'), uA = gl.getUniformLocation(pr, 'A');
    var SCALE = .5, mx = .72, my = .62, tx = .72, ty = .62, amp = 0, on = true, raf = 0, t0 = performance.now();
    function size(){ var r = hero.getBoundingClientRect(); cv.width = Math.max(2, Math.round(r.width * SCALE)); cv.height = Math.max(2, Math.round(Math.min(r.height, innerHeight * 1.2) * SCALE)); gl.viewport(0, 0, cv.width, cv.height); }
    function mv(e){ var r = cv.getBoundingClientRect(); tx = (e.clientX - r.left) / r.width; ty = 1 - (e.clientY - r.top) / r.height; }
    function frame(now){
      raf = 0; if (!on) return;
      mx += (tx - mx) * .06; my += (ty - my) * .06; amp = Math.min(1, amp + .012);
      gl.uniform2f(uR, cv.width, cv.height); gl.uniform1f(uT, (now - t0) / 1000); gl.uniform2f(uM, mx, my);
      gl.uniform1f(uS, window.__rhScroll || 0); gl.uniform1f(uA, amp);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      raf = requestAnimationFrame(frame);
    }
    var io = new IntersectionObserver(function(es){ on = es[0].isIntersecting && !document.hidden; if (on && !raf) raf = requestAnimationFrame(frame); });
    io.observe(hero);
    function vis(){ on = !document.hidden; if (on && !raf) raf = requestAnimationFrame(frame); }
    size(); addEventListener('resize', size); addEventListener('pointermove', mv, { passive: true }); document.addEventListener('visibilitychange', vis);
    raf = requestAnimationFrame(frame);
    return function(){ on = false; cancelAnimationFrame(raf); io.disconnect(); removeEventListener('resize', size); removeEventListener('pointermove', mv); document.removeEventListener('visibilitychange', vis); cv.remove(); };
  }

  /* ---- cursor ring: grows on links and cards, says "play" over video ---- */
  function ring(){
    var el = document.createElement('div'); el.className = 'rc'; el.setAttribute('aria-hidden', 'true'); el.innerHTML = '<i></i><b>Play</b>';
    document.body.appendChild(el); document.documentElement.classList.add('rc-on');
    var xs = gsap.quickTo(el, 'x', { duration: .35, ease: 'power3.out' }), ys = gsap.quickTo(el, 'y', { duration: .35, ease: 'power3.out' });
    var HOT = 'a, button, [role="button"], .svc-tile, .card, .shelf, label', VID = 'video, .svc-media, .ph, .clipfig',
        BTN = '.svc-cta, footer .cta, .ccard .btn, .pane .btn', lbl = el.querySelector('b');
    function mv(e){
      xs(e.clientX); ys(e.clientY); el.classList.add('in');
      var t = e.target, v = t.closest && t.closest(VID), h = t.closest && t.closest(HOT),
          bt = !!(t.closest && t.closest(BTN)), sh = !bt && !!(t.closest && t.closest('button.shelf'));
      /* over a primary button the ring steps aside and lets the red fill answer; over a shelf it says View */
      el.classList.toggle('btn', bt);
      el.classList.toggle('view', sh);
      el.classList.toggle('vid', !bt && !sh && !!(v && v.querySelector ? (v.tagName === 'VIDEO' || v.querySelector('video')) : v));
      if (sh) lbl.textContent = 'View'; else if (el.classList.contains('vid')) lbl.textContent = 'Play';
      el.classList.toggle('hot', !!h && !bt && !sh && !el.classList.contains('vid'));
      el.classList.toggle('dark', !!(t.closest && t.closest('.rh, .navbar.on-ink, .pane, .viewer')));
    }
    function out(){ el.classList.remove('in'); }
    function dn(){ el.classList.add('down'); } function up(){ el.classList.remove('down'); }
    addEventListener('pointermove', mv, { passive: true }); document.addEventListener('pointerleave', out);
    addEventListener('pointerdown', dn); addEventListener('pointerup', up);
    return function(){ removeEventListener('pointermove', mv); document.removeEventListener('pointerleave', out); removeEventListener('pointerdown', dn); removeEventListener('pointerup', up); el.remove(); document.documentElement.classList.remove('rc-on'); };
  }
})();
