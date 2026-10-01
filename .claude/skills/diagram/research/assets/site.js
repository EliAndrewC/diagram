// The record's navigation (feature 301, GM 2026-10-01: "navigation on the left-hand side and then the content on the
// right, which takes up most of the page"). The tree is data - window.RECORD_NAV, from the site's nav.js, written by
// `make record` - and this draws it into every page's sidebar: the home page and the single page at the top, every
// part of the record grouped, the current part open with its questions, the current page marked. Data rather than
// markup on each page because the registry alone has hundreds of entries; a script rather than a fetch because the
// site is opened from disk. Without scripts the sidebar holds a plain link to the contents.
(function () {
  'use strict';
  var nav = window.RECORD_NAV; var side = document.getElementById('sidebar');
  if (!nav || !side) { return; }
  var body = document.body; var root = body.getAttribute('data-root') || '';
  var part = body.getAttribute('data-part') || ''; var page = body.getAttribute('data-page') || '';
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) { e.className = cls; } if (text) { e.textContent = text; } return e; }
  function link(text, href, current) {
    var a = el('a', null, text); a.href = root + href;
    if (current) { a.setAttribute('aria-current', 'page'); }
    return a;
  }
  side.textContent = '';
  var top = el('div', 'nav-top');
  top.appendChild(link(nav.title, nav.home, page === nav.home));
  top.appendChild(link('The whole record on one page', nav.all, page === nav.all));
  side.appendChild(top);
  nav.groups.forEach(function (g) {
    side.appendChild(el('h2', null, g.label));
    var list = el('ul', 'parts');
    g.parts.forEach(function (p) {
      var li = el('li');
      var det = el('details'); if (p.dir === part) { det.open = true; }
      var sum = el('summary');
      sum.appendChild(link(p.title, p.dir + '/index.html', page === p.dir + '/index.html'));
      det.appendChild(sum);
      if (p.dir === part || p.items.length < 400) {
        var items = el('ul', 'items');
        p.items.forEach(function (it) { var i = el('li'); i.appendChild(link(it[0], it[1], page === it[1])); items.appendChild(i); });
        det.appendChild(items);
      } else {
        // a part this large is listed when opened, not on every page load (the registry's entries)
        det.addEventListener('toggle', function once() {
          det.removeEventListener('toggle', once);
          var items = el('ul', 'items');
          p.items.forEach(function (it) { var i = el('li'); i.appendChild(link(it[0], it[1], false)); items.appendChild(i); });
          det.appendChild(items);
        });
      }
      li.appendChild(det); list.appendChild(li);
    });
    side.appendChild(list);
  });
  var here = side.querySelector('[aria-current="page"]');
  if (here && here.scrollIntoView) { here.scrollIntoView({ block: 'center' }); window.scrollTo(0, 0); }
})();
