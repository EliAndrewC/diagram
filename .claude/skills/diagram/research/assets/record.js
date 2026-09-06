// The research record's footnote hover (feature 191, GM 2026-09-06): the form ACOUP uses - move the mouse over a
// footnote reference and the note (the source link and its quoted passage) appears beside it; move onto the box
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
    tip.innerHTML = note.innerHTML; tip.hidden = false;
    var r = ref.getBoundingClientRect(); var margin = 8;
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
  tip.addEventListener('mouseenter', keep);
  tip.addEventListener('mouseleave', hideSoon);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { keep(); tip.hidden = true; } });
})();
