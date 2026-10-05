/* The interactive map page (feature 134): hover lights up every feature of a kind, a click opens
   the kind's explanation. Inlined by page.py; the class data is the JSON blob #classes. */
(function () {
  "use strict";
  var svg = document.getElementById("map");
  var payload = JSON.parse(document.getElementById("classes").textContent);
  var data = payload.classes;
  var glossary = payload.glossary || [];
  // RASTER MODE (feature 200): below a screen scale the map is one image of the whole picture and the
  // hovered class alone is drawn lit as vector above it; the pointer is answered from a class id map.
  // `r` is 0 on a page written without resvg, and then the page never leaves vector mode.
  var raster = payload.raster || { r: 0 };
  var rasterReady = false;  // both the picture and the id map decoded (FR-016) - never raster before
  var idmap = null;
  var firstMode = null;     // what the very first apply() chose - the browser test asserts "vector"
  var readyAt = null;       // ms after navigation when raster mode became available (recorded, T06)
  // GLOSSARY TOOLTIPS (GM 2026-08-28): every occurrence of a glossary term in an explanation is
  // wrapped so hovering it shows the definition. Built as DOM nodes, never innerHTML of the text.
  var glossaryRe = null;
  var glossaryDef = {};
  var cased = {};  // a "cased" term's variants match only as written: `ochiba` never wraps the manor Ochiba (feature 265)
  if (glossary.length) {
    var alts = [];
    glossary.forEach(function (g) { g.variants.forEach(function (v) { if (g.cased) { cased[v.toLowerCase()] = v; } alts.push(v.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")); glossaryDef[v.toLowerCase()] = g.def; }); });
    alts.sort(function (a, b) { return b.length - a.length; });
    glossaryRe = new RegExp("\\b(" + alts.join("|") + ")\\b", "gi");
  }
  function fillText(el, text) {
    el.textContent = "";
    if (!text) return;
    if (!glossaryRe) { el.textContent = text; return; }
    var last = 0, m;
    glossaryRe.lastIndex = 0;
    while ((m = glossaryRe.exec(text)) !== null) {
      if (cased[m[0].toLowerCase()] !== undefined && cased[m[0].toLowerCase()] !== m[0]) continue;
      if (m.index > last) el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var span = document.createElement("span");
      span.className = "gl";
      span.textContent = m[0];
      span.setAttribute("data-def", glossaryDef[m[0].toLowerCase()] || "");
      // `this`, never `span`: `var` is shared by every pass of this loop, so a handler that named `span` showed the
      // LAST term's definition for every term in the paragraph (found by feature 250's tooltip test, 2026-09-27)
      span.addEventListener("mouseenter", function () { showTip(this); });
      span.addEventListener("mouseleave", hideTip);
      el.appendChild(span);
      last = m.index + m[0].length;
    }
    if (last < text.length) el.appendChild(document.createTextNode(text.slice(last)));
  }
  var dialog = document.getElementById("explain");

  // THE GLOSSARY TOOLTIP LIVES OUTSIDE THE DIALOGS (feature 182, GM 2026-09-05: "if that word is at the
  // edge of the modal, then it gets cut off, and the modal gains a horizontal scroll bar ... the tool tip
  // itself should be outside of the modal ... it should not extend off the right or left of the page
  // itself"). It used to be a CSS ::after box on the word, and nothing drawn INSIDE a dialog can escape
  // it: the dialog is centered with a transform, which makes it the containing block of every fixed
  // descendant, so even position: fixed stayed inside its overflow: auto. So there is ONE #tip element,
  // a sibling of the dialogs, placed in viewport coordinates from the hovered word's box: below the word,
  // shifted along the line to stay TIP_MARGIN px inside the viewport, above the word when below would
  // leave it, and never wider than the viewport allows. It follows the word when the dialog scrolls
  // (repositioned, not hidden - the CSS box moved with the word, and so does this one) and goes away
  // when the pointer leaves the word or the dialog closes.
  var tip = document.getElementById("tip");
  var tipFor = null;
  var TIP_MARGIN = 8;  // a guess at a legibility constant (spec D3)
  function placeTip() {
    if (!tipFor) return;
    var r = tipFor.getBoundingClientRect();
    var W = window.innerWidth, H = window.innerHeight;
    tip.style.maxWidth = (W - 2 * TIP_MARGIN) + "px";
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.max(TIP_MARGIN, Math.min(r.left, W - w - TIP_MARGIN));
    var top = r.bottom + 4;
    if (top + h > H - TIP_MARGIN) top = r.top - 4 - h;
    top = Math.max(TIP_MARGIN, Math.min(top, H - h - TIP_MARGIN));  // neither fits: inside the viewport, over the word
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  }
  function showTip(span) { tipFor = span; tip.textContent = span.getAttribute("data-def") || ""; tip.hidden = false; placeTip(); }
  function hideTip() { tipFor = null; tip.hidden = true; }
  document.addEventListener("scroll", placeTip, true);  // capture: the dialog's own scroll does not bubble

  // Index the class groups ONCE: a few hundred groups per class at most (a bead run of ~12,000
  // circles is one group), so a hover restyles those subtrees and nothing else.
  var groups = {};
  var all = svg.querySelectorAll("g.f");
  for (var i = 0; i < all.length; i++) {
    var k = all[i].getAttribute("data-k");
    (groups[k] || (groups[k] = [])).push(all[i]);
    // A PART lights with what it is part of (feature 264): a sheet's hearth carries data-in="kitchen", so the
    // kitchen's highlight takes the hearth in too, while the hearth's own lights no kitchen.
    var ins = all[i].getAttribute("data-in");
    if (ins) ins.split("|").forEach(function (p) { (groups[p] || (groups[p] = [])).push(all[i]); });
  }

  var current = null;
  var pinned = null;  // the class whose modal is open keeps its highlight until the modal closes (GM 2026-08-28)
  function highlight(key) {
    if (pinned !== null && key !== pinned) return;
    if (key === current) return;
    var gs, j;
    if (current !== null) {
      gs = groups[current] || [];
      for (j = 0; j < gs.length; j++) gs[j].classList.remove("on");
    }
    current = key;
    if (key !== null) {
      gs = groups[key] || [];
      for (j = 0; j < gs.length; j++) gs[j].classList.add("on");
    }
    svg.setAttribute("data-hl", key === null ? "" : key);
  }
  function keyAt(target) {
    var g = target && target.closest ? target.closest("g.f") : null;
    return g ? g.getAttribute("data-k") : null;
  }
  // THE LINK HAND OVER WHAT CAN BE CLICKED (GM 2026-09-26): a kind with an explanation turns the cursor into
  // the pointer a link shows, except the broad kinds - grassland, marsh, paddies, copses, windbreaks, woodland
  // commons - which carry `plain` (page.py PLAIN_CURSOR) and keep the arrow, as does bare ground. Set from the
  // key under the pointer, not by CSS on the groups, because in raster mode the groups are hidden and the id
  // map answers instead (below, `keyAtPoint`).
  var cursorKey;
  function cursorFor(key) {
    if (key === cursorKey) return;
    cursorKey = key;
    stage.style.cursor = key !== null && data[key] && !data[key].plain ? "pointer" : "";
  }
  function pointAt(key) { cursorFor(key); highlight(key); }
  svg.addEventListener("pointerover", function (e) { if (mode() !== "raster") pointAt(keyAt(e.target)); });
  svg.addEventListener("pointerleave", function () { pointAt(null); });
  function unpin() { pinned = null; highlight(null); }

  function setText(id, s) { document.getElementById(id).textContent = s || ""; }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function open(key) {
    var d = data[key];
    if (!d) return;
    setText("x-name", cap(d.name));
    // THE ABOUT FORM (feature 319): the About tab's paragraphs; the title card has none and shows its what and why
    var about = document.getElementById("x-about");
    about.textContent = "";
    (d.about || []).forEach(function (para) { var p = document.createElement("p"); fillText(p, para); about.appendChild(p); });
    about.hidden = !(d.about && d.about.length);
    var guesses = document.getElementById("x-guesses");
    guesses.textContent = "";
    (d.guesses || []).forEach(function (g) { var li = document.createElement("li"); fillText(li, g); guesses.appendChild(li); });
    document.getElementById("t-guesses").hidden = !(d.guesses && d.guesses.length);
    document.getElementById("t-refs").hidden = !d.questions.length;
    fillLinks("r-list", d.questions);
    // THE DEPICTION TAB (feature 319 plan D13): its paragraphs, then the "how our maps draw it" pages; absent when both are empty
    var dep = document.getElementById("x-depiction");
    dep.textContent = "";
    (d.depiction || []).forEach(function (para) { var p = document.createElement("p"); fillText(p, para); dep.appendChild(p); });
    fillLinks("d-list", d.drawing || []);
    document.getElementById("t-depict").hidden = !((d.depiction && d.depiction.length) || (d.drawing && d.drawing.length));
    // NO LEAD (feature 319): a class's classification is per statement in its own text, so nothing is announced above
    // it. The title card's body is its what and why (`place.place_card`); a class has neither.
    fillText(document.getElementById("x-what"), d.what || "");
    fillText(document.getElementById("x-why"), d.why || "");
    // WHAT IS TRUE OF THIS MAP ONLY (feature 156): authored in the settlement's own .notes.md and
    // headed so it cannot be read as a general fact about the kind. Absent on nearly every class of
    // nearly every map, and then the section is not there at all.
    // THE TITLE CARD'S CHOICES AND FACTS (feature 319, plan D10): each choice this settlement made, its value a link that opens
    // the value's own modal in this dialog; then the settlement's own sentences. Only the card carries them.
    var choicesEl = document.getElementById("x-choices");
    choicesEl.textContent = "";
    (d.choices || []).forEach(function (c) {
      var p = document.createElement("p");
      p.appendChild(document.createTextNode(c.name + ": "));
      if (c.k && data[c.k]) {
        var a = document.createElement("a");
        a.href = "#" + c.k;
        a.className = "choice";
        a.setAttribute("data-k", c.k);
        a.textContent = c.value;
        a.addEventListener("click", function (e) { e.preventDefault(); open(c.k); });
        p.appendChild(a);
      } else {
        p.appendChild(document.createTextNode(c.value));
      }
      choicesEl.appendChild(p);
    });
    choicesEl.hidden = !(d.choices && d.choices.length);
    var factsEl = document.getElementById("x-facts");
    factsEl.textContent = "";
    (d.facts || []).forEach(function (f) { var p = document.createElement("p"); fillText(p, f); factsEl.appendChild(p); });
    factsEl.hidden = !(d.facts && d.facts.length);
    var onmap = document.getElementById("x-onmap");
    fillText(onmap, d.on_this_map || "");
    onmap.hidden = !d.on_this_map;
    // THE TITLE CARD'S BASIS (spec 156 FR-008a), VERBATIM - its lead-in is part of the string (place.py BASIS_LEAD)
    var basis = document.getElementById("x-basis");
    fillText(basis, d.basis || "");
    basis.hidden = !d.basis;
    // SIBLINGS ARE LINKS (GM 2026-08-28): "Not to be confused with the X" - hovering X lights X on
    // the map (the pinned highlight yields while the pointer is on the link), clicking X opens X's
    // modal in place of this one. Each modal's own text stays its own.
    var sib = document.getElementById("x-siblings");
    sib.textContent = "";
    if (d.siblings.length) {
      var p = document.createElement("p");
      p.appendChild(document.createTextNode("Not to be confused with "));
      d.siblings.forEach(function (other, i) {
        if (i > 0) p.appendChild(document.createTextNode(i === d.siblings.length - 1 ? " or " : ", "));
        var a = document.createElement("a");
        a.href = "#" + other;
        a.className = "sib";
        a.setAttribute("data-k", other);
        a.textContent = "the " + (data[other] ? data[other].name : other);
        a.addEventListener("mouseenter", function () { peek(other); });
        a.addEventListener("mouseleave", function () { unpeek(); });
        a.addEventListener("click", function (e) { e.preventDefault(); unpeek(); open(other); });
        p.appendChild(a);
      });
      p.appendChild(document.createTextNode("."));
      sib.appendChild(p);
    }
    showTab("about");
    dialog.setAttribute("data-k", key);
    // NOT showModal(): a modal dialog makes the rest of the document inert, and Chromium re-styles
    // all ~175,000 elements of the map on every open and close - measured ~1 s and ~50 MB per cycle
    // on Inashiro, enough to crash the tab in the browser test on a tight machine. A non-modal
    // dialog with our own shade behind it costs nothing; Escape and the shade close it below.
    pinned = key;
    highlight(key);
    shade.hidden = false;
    dialog.show();
  }
  // hideTip() here as well as in the `close` listener: `close()` dispatches its event on a later task,
  // and the box should not outlive the dialog by even a frame (feature 182)
  function closeDialog() { hideTip(); dialog.close(); shade.hidden = true; unpin(); }
  // a sibling link's hover lights the OTHER class while the pointer is on it; the pin resumes after
  function peek(other) { var keep = pinned; pinned = null; highlight(other); pinned = keep; }
  function unpeek() { var keep = pinned; pinned = null; highlight(keep); pinned = keep; }
  // THE TABS (feature 319, GM 2026-10-03): About, Guesses, References in ONE dialog. A tab with nothing to show is not
  // drawn; the dialog opens on About every time. The references used to be a second dialog that replaced this one
  // (features 180, 181) with a "Return to <X> writeup" button; the tab strip is the way back now.
  var tabs = { about: "t-about", guesses: "t-guesses", depict: "t-depict", refs: "t-refs" };
  var panels = { about: "p-about", guesses: "p-guesses", depict: "p-depict", refs: "p-refs" };
  function showTab(name) {
    Object.keys(tabs).forEach(function (t) {
      var on = t === name;
      var b = document.getElementById(tabs[t]);
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.classList.toggle("on", on);
      document.getElementById(panels[t]).hidden = !on;
    });
    hideTip();  // the word it pointed at may be on the panel just hidden
  }
  Object.keys(tabs).forEach(function (t) {
    document.getElementById(tabs[t]).addEventListener("click", function () { showTab(t); });
  });
  // THE REFERENCES ARE QUESTIONS (feature 180, GM 2026-09-05): one link per research question the class was written
  // from, opening its answer in the record's site in a new tab; the sources are one click further, on that page.
  function fillLinks(id, qs) {
    var list = document.getElementById(id);
    list.textContent = "";
    qs.forEach(function (q) {
      var p = document.createElement("p");
      var a = document.createElement("a");
      a.href = q.url; a.target = "_blank"; a.rel = "noopener"; a.className = "q";
      a.textContent = q.text;
      p.appendChild(a);
      list.appendChild(p);
    });
  }
  svg.addEventListener("click", function (e) {
    if (mode() === "raster") return;  // the stage's own click handler answers from the id map
    var key = keyAt(e.target);
    if (key !== null) open(key);
  });
  var shade = document.getElementById("shade");
  document.getElementById("x-close").addEventListener("click", closeDialog);
  shade.addEventListener("click", closeDialog);  // a click outside the modal closes it
  dialog.addEventListener("close", function () { shade.hidden = true; unpin(); hideTip(); });

  // ---- ZOOM AND PAN (spec FR-013, GM 2026-08-28: "zoom in significantly more ... zoom out ... to a
  // degree that the entire settlement is visible all within the browser viewport"). The map is
  // moved by resizing the <svg> to vb * s and placing it at (tx, ty) - a LAYOUT, not a CSS
  // transform: a transform makes Chromium rasterize the whole scaled map as one layer, which at
  // 16x on a 16 MB map is a ~28,000 px square texture and crashed the tab in the browser test;
  // a resized SVG is painted per visible tile like any document. The page OPENS at the
  // view the GM saw before zoom existed - the map fitted to the viewport's WIDTH ("zoomed in now");
  // FIT (the whole map inside the viewport) is the floor; MAX_ZOOM times fit is the ceiling - the
  // GM left the maximum open ("I'm not sure precisely how much"), so 16x fit is a recorded judgment
  // (spec Decisions Recorded): on Inashiro in a 1400 x 1000 viewport that is ~11x the opening view,
  // one foot at ~9 screen px, a bund bean ~25 px across.
  var MAX_ZOOM = 16;
  var stage = document.getElementById("stage");
  var vb = svg.viewBox.baseVal;
  var view = { s: 1, tx: 0, ty: 0, fit: 1 };
  // SCROLLING STOPS AT THE MAP'S EDGE (GM 2026-08-28: "We should be able to scroll to the edge of the
  // map, but not beyond it"): along an axis where the map is larger than the viewport its edge may
  // reach the viewport's edge and no further; where it is smaller it sits centered. Applied to every
  // move - wheel, drag, zoom - so no path can leave the map behind.
  function clamp() {
    var W = stage.clientWidth, H = stage.clientHeight;
    var mw = vb.width * view.s, mh = vb.height * view.s;
    view.tx = mw <= W ? (W - mw) / 2 : Math.min(0, Math.max(W - mw, view.tx));
    view.ty = mh <= H ? (H - mh) / 2 : Math.min(0, Math.max(H - mh, view.ty));
  }
  function apply() {
    clamp();
    svg.style.width = (vb.width * view.s) + "px";
    svg.style.height = (vb.height * view.s) + "px";
    svg.style.left = view.tx + "px";
    svg.style.top = view.ty + "px";
    svg.setAttribute("data-zoom", (view.s / view.fit).toFixed(3));
    // THE SWITCH (feature 200, FR-004/FR-006): raster while the image would not be upsampled - screen
    // scale (CSS px per map px) times the device's pixel ratio at or under the image's px per map px -
    // and never before both images are decoded. On Kuwabata in a 1400 x 1000 viewport that is the opening
    // view and the first "+" on a DPR-1 screen, the opening view only on a DPR-2 screen (spec D5).
    var m = mode();
    if (firstMode === null) firstMode = m;
    svg.setAttribute("data-mode", m);
  }
  function mode() { return rasterReady && view.s * (window.devicePixelRatio || 1) <= raster.r ? "raster" : "vector"; }
  function fit() {
    var W = stage.clientWidth, H = stage.clientHeight;
    view.fit = Math.min(W / vb.width, H / vb.height);
    view.s = view.fit;
    view.tx = (W - vb.width * view.s) / 2;
    view.ty = (H - vb.height * view.s) / 2;
    apply();
  }
  function fitWidth() {  // the opening view: the map as wide as the viewport, top-aligned - what the page showed before it could zoom
    var W = stage.clientWidth, H = stage.clientHeight;
    view.fit = Math.min(W / vb.width, H / vb.height);
    view.s = Math.max(view.fit, W / vb.width);
    view.tx = (W - vb.width * view.s) / 2;
    view.ty = 0;
    apply();
  }
  function zoomAt(factor, cx, cy) {
    var s2 = Math.min(view.fit * MAX_ZOOM, Math.max(view.fit, view.s * factor));
    if (s2 === view.s) return;
    var r = s2 / view.s;
    view.tx = cx - (cx - view.tx) * r;
    view.ty = cy - (cy - view.ty) * r;
    view.s = s2;
    if (view.s === view.fit) { fit(); return; }
    apply();
  }
  function center() { return [stage.clientWidth / 2, stage.clientHeight / 2]; }
  // THE WHEEL SCROLLS, IT DOES NOT ZOOM (GM 2026-08-28: "I don't want scrolling to zoom - I still
  // want scrolling to scroll"): a wheel turn pans the map by the wheel's own travel, exactly as a
  // document scrolls. Zoom is the buttons and the keys only.
  function onWheel(e) {
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) {  // the browser's pinch / Ctrl+wheel zoom gesture becomes OUR zoom, about the pointer (GM 2026-08-28: one way of zooming)
      var r = stage.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * 0.01), e.clientX - r.left, e.clientY - r.top);
      return;
    }
    view.tx -= e.deltaX;
    view.ty -= e.deltaY;
    apply();
  }
  stage.addEventListener("wheel", onWheel, { passive: false });
  // ...AND THE SHADE SCROLLS THE MAP BEHIND IT (GM 2026-08-29: "when my mouse is not over top of the
  // actual modal itself, ... the map, which is in the background, will then scroll"). The shade is a
  // SIBLING of the stage covering the whole viewport, so with an explanation open every wheel turn
  // outside the dialog landed on the shade and bubbled to <body>, not to the stage - the map sat
  // still and the page looked frozen. The same handler on the shade makes "not over the modal" mean
  // the map, exactly as it does with the modal closed. Over the dialog itself the event never
  // reaches the shade (z-index 10 above 9), so the dialog's own overflow keeps scrolling its text.
  shade.addEventListener("wheel", onWheel, { passive: false });
  document.getElementById("zoom").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    var c = center();
    if (b.dataset.z === "in") zoomAt(2, c[0], c[1]);
    else if (b.dataset.z === "out") zoomAt(0.5, c[0], c[1]);
    else fit();
  });
  // Ctrl/Cmd + / - / 0 are INTERCEPTED and drive our zoom instead of the browser's (GM 2026-08-28:
  // "it would be better if there was only one way of zooming"). The browser's menu zoom cannot be
  // intercepted from a page; the keyboard and Ctrl+wheel can.
  document.addEventListener("keydown", function (e) {
    if (dialog.open) { if (e.key === "Escape") closeDialog(); return; }
    var c = center();
    if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomAt(2, c[0], c[1]); }
    else if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomAt(0.5, c[0], c[1]); }
    else if (e.key === "0") { e.preventDefault(); fit(); }
  });
  // NO DRAG-TO-PAN (GM 2026-08-28: "I don't need to click and drag so we can get rid of that and
  // make the mouse a normal pointer"): the wheel scrolls, the buttons and keys zoom, and a press is
  // only ever a click.
  window.addEventListener("resize", function () {  // keep the zoom, re-derive the floor
    var W = stage.clientWidth, H = stage.clientHeight;
    view.fit = Math.min(W / vb.width, H / vb.height);
    if (view.s <= view.fit) fit(); else apply();
  });
  fitWidth();

  // ---- RASTER MODE (feature 200). The picture's href is set HERE rather than in the markup so its
  // `load` cannot fire before the listener exists; the id map is drawn into a canvas once and read per
  // move. The page has already painted the vector picture above (fitWidth), at today's cost, and
  // switches when both are decoded (FR-016) - the two pictures are the same to the eye, so the switch
  // is invisible. Hit-testing in raster mode: the pixel of the id map under the pointer names the class;
  // a value one off the palette's grid (a PNG round trip) snaps back; anything else is no class.
  function keyAtPoint(clientX, clientY) {
    if (!idmap) return null;
    var r = stage.getBoundingClientRect();
    var px = Math.floor((clientX - r.left - view.tx) / view.s), py = Math.floor((clientY - r.top - view.ty) / view.s);
    if (px < 0 || py < 0 || px >= idmap.w || py >= idmap.h) return null;
    // red names the class on the palette's first row; green counts the rows past it (feature 264 - raster.py
    // PALETTE_STEP), and a first-row class keeps the red-only key it always had
    var at = (py * idmap.w + px) * 4, v = idmap.d[at], w = idmap.d[at + 1];
    var snapped = Math.round(v / raster.step) * raster.step, gsnap = Math.round(w / raster.step) * raster.step;
    if (Math.abs(v - snapped) > 1 || Math.abs(w - gsnap) > 1) return null;
    return raster.palette[gsnap === 0 ? String(snapped) : snapped + "," + gsnap] || null;
  }
  stage.addEventListener("pointermove", function (e) { if (mode() === "raster") pointAt(keyAtPoint(e.clientX, e.clientY)); });
  stage.addEventListener("click", function (e) {
    if (mode() !== "raster") return;
    var k = keyAtPoint(e.clientX, e.clientY);
    if (k !== null) open(k);
  });
  if (raster.r > 0) {
    var pending = 2;
    var arm = function () { if (--pending === 0) { rasterReady = true; readyAt = performance.now(); apply(); } };
    var pic = document.getElementById("raster");
    pic.addEventListener("load", arm, { once: true });
    pic.setAttribute("href", raster.picture);
    var im = new Image();
    im.onload = function () {
      var c = document.createElement("canvas");
      c.width = im.width; c.height = im.height;
      var g = c.getContext("2d", { willReadFrequently: true });
      g.drawImage(im, 0, 0);
      idmap = { w: im.width, h: im.height, d: g.getImageData(0, 0, im.width, im.height).data };
      arm();
    };
    im.src = raster.idmap;
  }

  // For the browser test: the same entry points the pointer uses.
  window.l7rMap = {
    mode: mode,
    firstMode: function () { return firstMode; },
    rasterReady: function () { return rasterReady; },
    readyAt: function () { return readyAt; },
    keyAtPoint: keyAtPoint,
    highlight: highlight,
    open: open,
    current: function () { return current; },
    cursor: function () { return stage.style.cursor || "auto"; },
    pinned: function () { return pinned; },
    showTab: showTab,
    classes: Object.keys(groups),
    count: function (key) { return (groups[key] || []).length; },
    zoom: function () { return view.s / view.fit; },
    view: function () { return { s: view.s, tx: view.tx, ty: view.ty, fit: view.fit }; },
    fit: fit,
    fitWidth: fitWidth,
    maxZoom: MAX_ZOOM
  };
})();
