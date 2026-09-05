/* The interactive map page (feature 134): hover lights up every feature of a kind, a click opens
   the kind's explanation. Inlined by page.py; the class data is the JSON blob #classes. */
(function () {
  "use strict";
  var svg = document.getElementById("map");
  var payload = JSON.parse(document.getElementById("classes").textContent);
  var data = payload.classes;
  var glossary = payload.glossary || [];
  // GLOSSARY TOOLTIPS (GM 2026-08-28): every occurrence of a glossary term in an explanation is
  // wrapped so hovering it shows the definition. Built as DOM nodes, never innerHTML of the text.
  var glossaryRe = null;
  var glossaryDef = {};
  if (glossary.length) {
    var alts = [];
    glossary.forEach(function (g) { g.variants.forEach(function (v) { alts.push(v.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")); glossaryDef[v.toLowerCase()] = g.def; }); });
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
      if (m.index > last) el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var span = document.createElement("span");
      span.className = "gl";
      span.textContent = m[0];
      span.setAttribute("data-def", glossaryDef[m[0].toLowerCase()] || "");
      span.addEventListener("mouseenter", function () { showTip(span); });
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
  svg.addEventListener("pointerover", function (e) { highlight(keyAt(e.target)); });
  svg.addEventListener("pointerleave", function () { highlight(null); });
  function unpin() { pinned = null; highlight(null); }

  function setText(id, s) { document.getElementById(id).textContent = s || ""; }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  var refsDialog = document.getElementById("references");
  function open(key) {
    var d = data[key];
    if (!d) return;
    if (refsDialog.open) refsDialog.close();
    setText("x-name", cap(d.name));
    // THE PRESUMPTION OF ACCURACY (feature 156, GM 2026-08-29). `lead` is empty for everything the
    // record calls accurate, so the modal opens with what the feature IS; a deviation or a guess
    // still leads with its liberty, because that is the case worth a reader's attention. The
    // caveat - the liberty an accurate class's own record discloses - goes AFTER the why.
    var label = document.getElementById("x-label");
    fillText(label, d.lead);
    label.hidden = !d.lead;
    fillText(document.getElementById("x-what"), d.what);
    fillText(document.getElementById("x-why"), d.why);
    // WHAT IS TRUE OF THIS MAP ONLY (feature 156): authored in the settlement's own .notes.md and
    // headed so it cannot be read as a general fact about the kind. Absent on nearly every class of
    // nearly every map, and then the section is not there at all.
    var onmap = document.getElementById("x-onmap");
    fillText(onmap, d.on_this_map || "");
    onmap.hidden = !d.on_this_map;
    // VERBATIM - the lead-in is part of the string now (page.py CAVEAT_LEAD, place.py BASIS_LEAD).
    // A renderer that prepended "On the drawing:" to every caveat also prepended it to the place
    // card's basis, which is about where the card's claims come from and not about the drawing.
    var caveat = document.getElementById("x-caveat");
    fillText(caveat, d.caveat || "");
    caveat.hidden = !d.caveat;
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
    // THE LINK COUNTS QUESTIONS (feature 180): what the references modal will list. The "Record: ..."
    // footer that used to follow it is gone (GM 2026-09-05) - the pointer stays in the registry.
    var refs = document.getElementById("x-refs");
    refs.hidden = !d.questions.length;
    refs.textContent = d.questions.length ? "See references (" + d.questions.length + ")" : "";
    dialog.setAttribute("data-k", key);
    dialog.setAttribute("data-label", d.label);
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
  function closeDialog() { if (refsDialog.open) refsDialog.close(); hideTip(); dialog.close(); shade.hidden = true; unpin(); }
  // a sibling link's hover lights the OTHER class while the pointer is on it; the pin resumes after
  function peek(other) { var keep = pinned; pinned = null; highlight(other); pinned = keep; }
  function unpeek() { var keep = pinned; pinned = null; highlight(keep); pinned = keep; }
  // THE REFERENCES MODAL (GM 2026-08-28): a second dialog. SINCE FEATURE 180 (GM 2026-09-05) IT LISTS
  // QUESTIONS, NOT SOURCES: one link per research section the class was written from, to that section
  // on the public GitHub rendering of the record - "a list of questions we've asked with links to the
  // appropriate places". The sources are one click further, on the page that answers the question; a
  // casual reader is not met with a wall of them.
  // IT REPLACES THE EXPLANATION RATHER THAN STACKING ON IT (feature 181, GM 2026-09-05: "when it is
  // smaller, it just looks really weird. So I think that the original modal should disappear. But then
  // if I click on the 'Return to Farmhouse writeup' button, then the current modal closes and the
  // original modal reappears"). HIDDEN, not closed: the explanation's `close` event is what releases the
  // pinned highlight and the shade, and the reader has not left the feature - they have gone one level
  // deeper into it - so the map stays lit and shaded behind (spec D1/FR-002). The class comes off in the
  // references dialog's own `close` listener below, which every way back runs through: the button, the
  // title link, Escape, `closeDialog`, and a fresh `open()`.
  function openRefs() {
    var key = dialog.getAttribute("data-k");
    var d = data[key];
    if (!d || !d.questions.length) return;
    // THE TITLE IS THE WAY BACK (feature 181): "<Name> references", the name a link doing exactly what
    // the return button does - one handler, two triggers (spec D2). Only the word is the link (D3).
    var title = document.getElementById("r-name");
    title.textContent = "";
    var back = document.createElement("a");
    back.id = "r-back"; back.href = "#"; back.className = "back";
    back.textContent = cap(d.name);
    back.addEventListener("click", function (e) { e.preventDefault(); returnToWriteup(); });
    title.appendChild(back);
    title.appendChild(document.createTextNode(" references"));
    var list = document.getElementById("r-list");
    list.textContent = "";
    d.questions.forEach(function (q) {
      var p = document.createElement("p");
      var a = document.createElement("a");
      a.href = q.url; a.target = "_blank"; a.rel = "noopener"; a.className = "q";
      a.textContent = q.text;
      p.appendChild(a);
      list.appendChild(p);
    });
    // THE BUTTON SAYS WHERE IT GOES (GM 2026-09-05: "just saying close might make it seem like we are
    // closing all of the modals instead of just this one").
    setText("r-close", "Return to " + cap(d.name) + " writeup");
    hideTip();  // the word it pointed at is about to be hidden with its dialog
    dialog.classList.add("behind");
    refsDialog.show();
  }
  function returnToWriteup() { refsDialog.close(); }
  document.getElementById("x-refs").addEventListener("click", function (e) { e.preventDefault(); openRefs(); });
  document.getElementById("r-close").addEventListener("click", returnToWriteup);
  refsDialog.addEventListener("cancel", function (e) { e.preventDefault(); returnToWriteup(); });
  // ...and however the references close, the explanation comes back (feature 181)
  refsDialog.addEventListener("close", function () { dialog.classList.remove("behind"); });
  svg.addEventListener("click", function (e) {
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
    if (refsDialog.open) { if (e.key === "Escape") { e.preventDefault(); refsDialog.close(); } return; }
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

  // For the browser test: the same entry points the pointer uses.
  window.l7rMap = {
    highlight: highlight,
    open: open,
    current: function () { return current; },
    pinned: function () { return pinned; },
    openRefs: openRefs,
    classes: Object.keys(groups),
    count: function (key) { return (groups[key] || []).length; },
    zoom: function () { return view.s / view.fit; },
    view: function () { return { s: view.s, tx: view.tx, ty: view.ty, fit: view.fit }; },
    fit: fit,
    fitWidth: fitWidth,
    maxZoom: MAX_ZOOM
  };
})();
