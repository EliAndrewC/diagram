/* The interactive map page (feature 134): hover lights up every feature of a kind, a click opens
   the kind's explanation. Inlined by page.py; the class data is the JSON blob #classes. */
(function () {
  "use strict";
  var svg = document.getElementById("map");
  var data = JSON.parse(document.getElementById("classes").textContent);
  var dialog = document.getElementById("explain");

  // Index the class groups ONCE: a few hundred groups per class at most (a bead run of ~12,000
  // circles is one group), so a hover restyles those subtrees and nothing else.
  var groups = {};
  var all = svg.querySelectorAll("g.f");
  for (var i = 0; i < all.length; i++) {
    var k = all[i].getAttribute("data-k");
    (groups[k] || (groups[k] = [])).push(all[i]);
  }

  var current = null;
  function highlight(key) {
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
  svg.addEventListener("pointerover", function (e) { highlight(keyAt(e.target)); });
  svg.addEventListener("pointerleave", function () { highlight(null); });

  function setText(id, s) { document.getElementById(id).textContent = s || ""; }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function open(key) {
    var d = data[key];
    if (!d) return;
    setText("x-name", cap(d.name));
    setText("x-label", "This is " + d.label_phrase + (d.label_note ? " - " + d.label_note : "."));
    setText("x-what", d.what);
    setText("x-why", d.why);
    var sib = document.getElementById("x-siblings");
    sib.textContent = "";
    var others = Object.keys(d.siblings);
    for (var i = 0; i < others.length; i++) {
      var p = document.createElement("p");
      var b = document.createElement("b");
      b.textContent = cap(d.name) + " and " + (data[others[i]] ? data[others[i]].name : others[i]) + ": ";
      p.appendChild(b);
      p.appendChild(document.createTextNode(d.siblings[others[i]]));
      sib.appendChild(p);
    }
    setText("x-sources", "Sources: " + d.sources.join(", "));
    setText("x-entry", d.entry ? "Record: " + d.entry : "");
    dialog.setAttribute("data-k", key);
    dialog.setAttribute("data-label", d.label);
    // NOT showModal(): a modal dialog makes the rest of the document inert, and Chromium re-styles
    // all ~175,000 elements of the map on every open and close - measured ~1 s and ~50 MB per cycle
    // on Inashiro, enough to crash the tab in the browser test on a tight machine. A non-modal
    // dialog with our own shade behind it costs nothing; Escape and the shade close it below.
    shade.hidden = false;
    dialog.show();
  }
  function closeDialog() { dialog.close(); shade.hidden = true; }
  svg.addEventListener("click", function (e) {
    var key = keyAt(e.target);
    if (key !== null) open(key);
  });
  var shade = document.getElementById("shade");
  document.getElementById("x-close").addEventListener("click", closeDialog);
  shade.addEventListener("click", closeDialog);  // a click outside the modal closes it
  dialog.addEventListener("close", function () { shade.hidden = true; });

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
  }
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
  stage.addEventListener("wheel", function (e) {
    e.preventDefault();
    view.tx -= e.deltaX;
    view.ty -= e.deltaY;
    apply();
  }, { passive: false });
  document.getElementById("zoom").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    var c = center();
    if (b.dataset.z === "in") zoomAt(2, c[0], c[1]);
    else if (b.dataset.z === "out") zoomAt(0.5, c[0], c[1]);
    else fit();
  });
  document.addEventListener("keydown", function (e) {
    if (dialog.open) { if (e.key === "Escape") closeDialog(); return; }
    if (e.ctrlKey || e.metaKey) return;
    var c = center();
    if (e.key === "+" || e.key === "=") zoomAt(2, c[0], c[1]);
    else if (e.key === "-") zoomAt(0.5, c[0], c[1]);
    else if (e.key === "0") fit();
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

  // For the browser test: the same entry points the pointer uses.
  window.l7rMap = {
    highlight: highlight,
    open: open,
    current: function () { return current; },
    classes: Object.keys(groups),
    count: function (key) { return (groups[key] || []).length; },
    zoom: function () { return view.s / view.fit; },
    view: function () { return { s: view.s, tx: view.tx, ty: view.ty, fit: view.fit }; },
    fit: fit,
    fitWidth: fitWidth,
    maxZoom: MAX_ZOOM
  };
})();
