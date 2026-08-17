(function () {
  var box = document.getElementById("lightbox");
  var img = document.getElementById("lightbox-img");
  var cap = document.getElementById("lightbox-cap");
  var closeBtn = document.getElementById("lightbox-close");
  var lastFocus = null;

  var prevBtn = document.getElementById("lightbox-prev");
  var nextBtn = document.getElementById("lightbox-next");
  var group = [], index = -1;

  function show(trigger) {
    var full = trigger.getAttribute("data-full");
    var thumb = trigger.querySelector("img");
    img.src = full;
    img.alt = thumb ? thumb.alt : "";
    cap.innerHTML = trigger.getAttribute("data-cap") || "";
  }
  function step(delta) {
    if (group.length < 2) return;
    index = (index + delta + group.length) % group.length;
    show(group[index]);
  }
  function open(trigger) {
    /* forward/back only inside a photo pile (Method Effects); single shots stay single */
    var pile = trigger.closest(".pile");
    group = pile ? Array.prototype.slice.call(pile.querySelectorAll("[data-full]")) : [];
    index = group.indexOf(trigger);
    var multi = group.length > 1;
    prevBtn.hidden = !multi; nextBtn.hidden = !multi;
    show(trigger);
    lastFocus = trigger;
    box.hidden = false;
    box.classList.add("open");
    document.body.style.overflow = "hidden";
    closeBtn.focus();
  }
  prevBtn.addEventListener("click", function (e) { e.stopPropagation(); step(-1); });
  nextBtn.addEventListener("click", function (e) { e.stopPropagation(); step(1); });
  var touchX = null;
  box.addEventListener("touchstart", function (e) { touchX = e.changedTouches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX; touchX = null;
    if (Math.abs(dx) > 40) { e.preventDefault(); step(dx < 0 ? 1 : -1); }
  });
  function close() {
    box.classList.remove("open");
    box.hidden = true;
    img.src = "";
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  document.querySelectorAll("[data-full]").forEach(function (el) {
    el.addEventListener("click", function () { open(el); });
  });
  /* one handler: any click inside the open lightbox closes it
     (matches the "click anywhere to close" hint; no double-fire) */
  box.addEventListener("click", function () {
    if (!box.hidden) close();
  });
  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
    if (e.key === "Tab") { e.preventDefault(); closeBtn.focus(); }
  });
})();


/* ---- tester breakout ---- */
(function () {
  var tv = document.getElementById("testerview");
  var opener = document.getElementById("tester-open");
  var closeBtn = document.getElementById("tester-close");
  if (!tv || !opener) return;
  function close() { tv.classList.remove("open"); tv.hidden = true; document.body.style.overflow = ""; opener.focus(); }
  opener.addEventListener("click", function (e) {
    e.preventDefault();
    tv.hidden = false; tv.classList.add("open");
    document.body.style.overflow = "hidden"; closeBtn.focus();
  });
  closeBtn.addEventListener("click", close);
  tv.addEventListener("click", function (e) { if (e.target === tv) close(); });
  document.addEventListener("keydown", function (e) { if (!tv.hidden && e.key === "Escape") close(); });
})();

/* ---- library stacks: built from the JSON manifest above ---- */
(function () {
  var manifest = JSON.parse(document.getElementById("library-manifest").textContent);
  var grid = document.getElementById("stack-grid");
  var view = document.getElementById("stackview");
  var svImg = document.getElementById("sv-img");
  var svCount = document.getElementById("sv-count");
  var svTitle = document.getElementById("sv-title");
  var svCap = document.getElementById("sv-cap");
  var svBody = document.getElementById("sv-body");
  var svLinks = document.getElementById("sv-links");
  var cur = { stack: null, i: 0 };
  var lastFocus = null;

  var FRONT = ["ai", "recipes"]; /* front-facing stacks; everything else is in library.html */
  function entries(stack) { return stack.items.filter(function (it) { return !it.slide; }).length; }
  manifest.stacks.forEach(function (stack, n) {
    if (FRONT.indexOf(stack.id) < 0) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "stack";
    btn.setAttribute("aria-label", stack.label + " — " + entries(stack) + (entries(stack) === 1 ? " entry" : " entries") + ", click to browse");
    btn.innerHTML =
      '<span class="card"><span class="frame"><img src="' + stack.items[0].src + '"' +
      (stack.items[0].pos ? ' style="object-position:' + stack.items[0].pos + '"' : '') +
      ' alt="" loading="lazy"></span>' +
      '<span class="count">' + entries(stack) + "</span></span>" +
      '<span class="label">' + stack.label + "</span>";
    btn.addEventListener("click", function () { lastFocus = btn; show(stack, 0); });
    grid.appendChild(btn);
  });

  function show(stack, i) {
    cur.stack = stack; cur.i = i;
    var item = stack.items[i];
    svImg.src = item.src;
    svImg.alt = item.title || "";
    svCount.textContent = stack.label + " · " + (i + 1) + " / " + stack.items.length;
    svTitle.textContent = item.title || "";
    svCap.textContent = item.cap || "";
    svBody.innerHTML = (item.body || []).map(function (p) { return "<p>" + p + "</p>"; }).join("");
    svLinks.innerHTML = (item.links || []).map(function (l) {
      return '<a href="' + l.href + '" target="_blank" rel="noopener">' + l.t + " ↗</a>";
    }).join("");
    document.getElementById("sv-prev").disabled = i === 0;
    document.getElementById("sv-next").disabled = i === stack.items.length - 1;
    view.hidden = false;
    view.classList.add("open");
    document.body.style.overflow = "hidden";
    document.getElementById("sv-close").focus();
  }
  function closeView() {
    view.classList.remove("open");
    view.hidden = true;
    svImg.src = "";
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  document.getElementById("sv-prev").addEventListener("click", function () { if (cur.i > 0) show(cur.stack, cur.i - 1); });
  document.getElementById("sv-next").addEventListener("click", function () { if (cur.i < cur.stack.items.length - 1) show(cur.stack, cur.i + 1); });
  document.getElementById("sv-close").addEventListener("click", closeView);
  view.addEventListener("click", function (e) { if (e.target === view) closeView(); });
  document.addEventListener("keydown", function (e) {
    if (view.hidden) return;
    if (e.key === "Escape") closeView();
    if (e.key === "ArrowLeft" && cur.i > 0) show(cur.stack, cur.i - 1);
    if (e.key === "ArrowRight" && cur.i < cur.stack.items.length - 1) show(cur.stack, cur.i + 1);
  });
})();
