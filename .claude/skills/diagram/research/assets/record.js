// The research record's footnote hover (feature 194, GM 2026-09-06): the form ACOUP uses - move the mouse over a
// footnote reference and the note (the source link and its quoted passage) appears beside it - and since feature 209 a
// glossary term shows its definition the same way; move onto the box
// to follow its link; move away, or press Escape, and it goes. Clicking still jumps to the note, and the note's
// back-link returns. One script for every page under research/; loaded with `defer` from each page's <head>.
(function () {
  'use strict';
  var tip = document.createElement('div'); tip.id = 'fntip'; tip.setAttribute('role', 'tooltip'); tip.hidden = true;
  document.body.appendChild(tip);
  var hideTimer = null;
  function keep() { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } }
  function hideSoon() { keep(); hideTimer = setTimeout(function () { tip.hidden = true; }, 180); }
  function show(ref) {
    var id = (ref.getAttribute('href') || '').slice(1); var note = id && document.getElementById(id);
    if (!note) { return; }
    tip.innerHTML = note.innerHTML; place(ref);
  }
  function place(el) {
    tip.hidden = false;
    var r = el.getBoundingClientRect(); var margin = 8;
    var vw = document.documentElement.clientWidth; var vh = document.documentElement.clientHeight;
    var w = tip.offsetWidth; var h = tip.offsetHeight;
    var x = r.left; if (x + w + margin > vw) { x = Math.max(margin, vw - w - margin); }
    var y = r.bottom + 6; if (y + h + margin > vh) { y = r.top - h - 6; } if (y < margin) { y = margin; }
    tip.style.left = (window.scrollX + x) + 'px'; tip.style.top = (window.scrollY + y) + 'px';
  }
  document.querySelectorAll('sup.fn a[href^="#fn-"]').forEach(function (ref) {
    ref.addEventListener('mouseenter', function () { keep(); show(ref); });
    ref.addEventListener('focus', function () { keep(); show(ref); });
    ref.addEventListener('mouseleave', hideSoon);
    ref.addEventListener('blur', hideSoon);
  });
  // GLOSSARY TOOLTIPS (feature 209, GM 2026-09-07: "apply the same kind of tooltip rules to our research sections
  // that we have in our diagram HTML pages"): the map's glossary, derived to assets/glossary.js by `make glossary`
  // and loaded before this script, is wrapped over every occurrence of a term in the page's visible text -
  // headings, prose and footnotes alike - exactly as page.js wraps a modal's explanation: whole-word,
  // case-insensitive, longest variant first, nothing inside code, pre, script or style, and the wrap adds no
  // characters, so a quoted passage keeps its own. The definition shows in the footnote box, placed the same way.
  // The word boundary is written with Unicode classes rather than \b, because a term may carry a macron.
  var glossary = window.RECORD_GLOSSARY || [];
  if (glossary.length) {
    var alts = []; var defs = {};
    glossary.forEach(function (g) { g.variants.forEach(function (v) { alts.push(v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); defs[v.toLowerCase()] = g.def; }); });
    alts.sort(function (a, b) { return b.length - a.length; });
    var glossaryRe = new RegExp('(?<![\\p{L}\\p{N}])(' + alts.join('|') + ')(?![\\p{L}\\p{N}])', 'giu');
    var SKIP = { CODE: true, PRE: true, SCRIPT: true, STYLE: true };
    var root = document.querySelector('main') || document.body;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: function (n) {
      for (var p = n.parentNode; p && p !== root; p = p.parentNode) { if (SKIP[p.nodeName]) { return NodeFilter.FILTER_REJECT; } }
      return NodeFilter.FILTER_ACCEPT;
    } });
    var nodes = []; while (walker.nextNode()) { nodes.push(walker.currentNode); }
    nodes.forEach(function (node) {
      var text = node.nodeValue; var last = 0; var frag = null; var m;
      glossaryRe.lastIndex = 0;
      while ((m = glossaryRe.exec(text)) !== null) {
        if (!frag) { frag = document.createDocumentFragment(); }
        if (m.index > last) { frag.appendChild(document.createTextNode(text.slice(last, m.index))); }
        var span = document.createElement('span'); span.className = 'gl'; span.textContent = m[0];
        span.setAttribute('data-def', defs[m[0].toLowerCase()] || '');
        span.addEventListener('mouseenter', function (e) { keep(); tip.textContent = e.currentTarget.getAttribute('data-def'); place(e.currentTarget); });
        span.addEventListener('mouseleave', hideSoon);
        frag.appendChild(span); last = m.index + m[0].length;
      }
      if (frag) { if (last < text.length) { frag.appendChild(document.createTextNode(text.slice(last))); } node.parentNode.replaceChild(frag, node); }
    });
  }
  tip.addEventListener('mouseenter', keep);
  tip.addEventListener('mouseleave', hideSoon);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { keep(); tip.hidden = true; } });
})();
