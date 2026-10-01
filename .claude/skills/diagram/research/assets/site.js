// The record's navigation (feature 301, GM 2026-10-01: "navigation on the left-hand side and then the content on the
// right, which takes up most of the page"). The tree is data - window.RECORD_NAV, from the site's nav.js, written by
// `make record` - and this draws it into every page's sidebar: the home page and the single page at the top, then each
// group (the research, how our maps draw it, the tags, the sources) with its sections nested as the table of contents
// nests them (feature 303: `research/contents.json`), the sections around the current page open, the current page
// marked. Data rather than markup on each page because the registry alone has hundreds of entries; a script rather
// than a fetch because the site is opened from disk. Without scripts the sidebar holds a plain link to the contents.
(function () {
  'use strict';
  var nav = window.RECORD_NAV; var side = document.getElementById('sidebar');
  if (!nav || !side) { return; }
  var body = document.body; var root = body.getAttribute('data-root') || '';
  var open = (body.getAttribute('data-part') || '').split(' '); var page = body.getAttribute('data-page') || '';
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) { e.className = cls; } if (text) { e.textContent = text; } return e; }
  function link(text, href, current) {
    var a = el('a', null, text); a.href = root + href;
    if (current) { a.setAttribute('aria-current', 'page'); }
    return a;
  }
  function items(node, list) {
    node.items.forEach(function (it) { var i = el('li'); i.appendChild(link(it[0], it[1], page === it[1])); list.appendChild(i); });
  }
  // One section: its own page in the summary, then its subsections, then its questions. A section this large (the
  // registry's entries) is listed when opened, not on every page load.
  function node(n) {
    var li = el('li');
    var det = el('details'); var isOpen = open.indexOf(n.key) >= 0; if (isOpen) { det.open = true; }
    var sum = el('summary');
    sum.appendChild(link(n.title, n.href, page === n.href));
    det.appendChild(sum);
    var fill = function () {
      if (n.sections.length) { var subs = el('ul', 'parts'); n.sections.forEach(function (s) { subs.appendChild(node(s)); }); det.appendChild(subs); }
      if (n.items.length) { var list = el('ul', 'items'); items(n, list); det.appendChild(list); }
    };
    if (isOpen || n.items.length < 400) { fill(); } else {
      det.addEventListener('toggle', function once() { det.removeEventListener('toggle', once); fill(); });
    }
    li.appendChild(det);
    return li;
  }
  side.textContent = '';
  var top = el('div', 'nav-top');
  top.appendChild(link(nav.title, nav.home, page === nav.home));
  top.appendChild(link('The whole record on one page', nav.all, page === nav.all));
  side.appendChild(top);
  nav.groups.forEach(function (g) {
    side.appendChild(el('h2', null, g.label));
    var list = el('ul', 'parts');
    g.sections.forEach(function (s) { list.appendChild(node(s)); });
    side.appendChild(list);
  });
  var here = side.querySelector('[aria-current="page"]');
  if (here && here.scrollIntoView) { here.scrollIntoView({ block: 'center' }); window.scrollTo(0, 0); }
})();
