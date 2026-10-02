// The record's light / dark choice (GM 2026-10-02: "a light mode / dark mode toggle on the left-hand navbar which
// remembers your previous selection"). Loaded in the head, not deferred, so the saved choice is on the page before it
// is painted; with no choice saved the page follows the system's setting (record.css). The button is site.js's.
(function () {
  'use strict';
  var KEY = 'record-theme';
  function saved() { try { return window.localStorage.getItem(KEY); } catch (e) { return null; } }
  function apply(theme) {
    if (theme === 'light' || theme === 'dark') { document.documentElement.setAttribute('data-theme', theme); }
  }
  apply(saved());
  window.RECORD_THEME = {
    current: function () {
      var set = document.documentElement.getAttribute('data-theme');
      if (set) { return set; }
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    },
    set: function (theme) {
      apply(theme);
      try { window.localStorage.setItem(KEY, theme); } catch (e) { /* not remembered: private window or blocked storage */ }
    }
  };
})();
