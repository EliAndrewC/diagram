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
  // WHERE A NOTE COMES FROM (feature 211, GM 2026-09-07): the notes live on the page's CITATIONS PAGE
  // (research/citations/<name>.html), and a reference points there ("citations/<name>.html#fn-n"). The hover
  // reads the note from window.RECORD_CITATIONS - the script `make citations` derives from that page, loaded
  // before this one - because a page opened from disk cannot fetch a sibling file. A note still in the page
  // (the synthetic test page, an older page) is read from the page, as before.
  function noteHtml(ref) {
    var href = ref.getAttribute('href') || ''; var id = href.slice(href.indexOf('#') + 1);
    var note = id && document.getElementById(id);
    if (note) { return note.innerHTML; }
    var table = window.RECORD_CITATIONS || {};
    return Object.prototype.hasOwnProperty.call(table, id) ? table[id] : '';
  }
  function show(ref) {
    var html = noteHtml(ref);
    if (!html) { return; }
    tip.innerHTML = html; wrapGlossary(tip, false); place(ref);
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
  document.querySelectorAll('sup.fn a[href*="#fn-"]').forEach(function (ref) {
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
  var glossaryRe = null; var defs = {};
  if (glossary.length) {
    var alts = [];
    glossary.forEach(function (g) { g.variants.forEach(function (v) { alts.push(v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); defs[v.toLowerCase()] = g.def; }); });
    alts.sort(function (a, b) { return b.length - a.length; });
    glossaryRe = new RegExp('(?<![\\p{L}\\p{N}])(' + alts.join('|') + ')(?![\\p{L}\\p{N}])', 'giu');
  }
  var SKIP = { CODE: true, PRE: true, SCRIPT: true, STYLE: true };
  // Wrap every term under `root`. In the page (`live`), a wrapped term shows its definition in the box on hover;
  // inside the box itself (feature 211: a note arriving from the derived script was never in the page, so it is
  // wrapped when shown) the term is marked and carries its definition as a title, because the box cannot hover
  // over itself.
  function wrapGlossary(root, live) {
    if (!glossaryRe) { return; }
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
        var def = defs[m[0].toLowerCase()] || '';
        if (live) {
          span.setAttribute('data-def', def);
          span.addEventListener('mouseenter', function (e) { keep(); tip.textContent = e.currentTarget.getAttribute('data-def'); place(e.currentTarget); });
          span.addEventListener('mouseleave', hideSoon);
        } else {
          span.setAttribute('title', def);
        }
        frag.appendChild(span); last = m.index + m[0].length;
      }
      if (frag) { if (last < text.length) { frag.appendChild(document.createTextNode(text.slice(last))); } node.parentNode.replaceChild(frag, node); }
    });
  }
  wrapGlossary(document.querySelector('main') || document.body, true);
  tip.addEventListener('mouseenter', keep);
  tip.addEventListener('mouseleave', hideSoon);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { keep(); tip.hidden = true; } });
})();
