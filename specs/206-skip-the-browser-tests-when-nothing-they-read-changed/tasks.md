# Tasks - 206 Skip the browser tests when nothing they read changed

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` (tooling; nothing physical).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 2 of 5: round 1 struck the BROWSER_ALL=1 override as unrequested (the same ruling as the done short-circuit's FORCE=); round 2 verified the key against the package's actual imports and found nothing missing or added
- [x] T02 `gate-stamp.py`: the `browser` area (FR-001), the area-aware exclusion, the browser salt, `--check`
      ignores it (FR-004); the why at each point
      research: rendering
      verify: DONE. DONE. gate-stamp.py: AREAS['browser'] (interactive/*.py, assets/*, the test package, research/*.html; RAW; SKIP_ONLY_AREAS), _excluded/_area_files take the area name, _salt reads the Playwright version and the chromium-* build directories, hash_files takes the salt, _area_key shared by write/fresh/check, --check skips SKIP_ONLY areas; selftest and scripts/test-gate-stamp.sh green; the diff is 67+/21- after the formatter's churn on untouched lines was backed out
- [x] T03 Makefile: `BROWSER_SKIP` on the `test` recipe (FR-002); `page-check` and `done`'s phases-run exit
      earn the stamp (FR-003)
      research: rendering
      verify: DONE. DONE. BROWSER_SKIP (recursive, --fresh browser -> --ignore=tests/full/interactive/page_browser) on both pytest lines of the test recipe with one printed line; page-check writes the browser stamp after page; done's phases-run exit writes it only when BROWSER_SKIP was empty; the short-circuit writes none; no override flag
- [x] T04 `tests/tooling/test_browser_skip.py` (FR-006); SC-002 shown once
      research: rendering
      verify: DONE. DONE. tests/tooling/test_browser_skip.py: 6 tests (the area's files incl. conftest.py and a research page, nothing engine or pool; stale on css/page.py/test/research edits and on a salt change, not on settlement/houses.py; --check passes a research+test delta with no stamp; the real salt names the browser; the test recipe carries the skip twice and announces it, BROWSER_ALL absent; page-check and done's exit write, the short-circuit does not); tests/tooling whole dir 409 passed. SC-002: make page-check green wrote the stamp (--fresh browser rc 0); one byte appended to page.css -> rc 1; restored -> rc 0; the skip line itself observed in the make test-full of T06
- [x] T05 the record (FR-007): `interactive/CLAUDE.md`, `tests/CLAUDE.md`, root `CLAUDE.md`
      research: rendering
      verify: DONE. DONE. interactive/CLAUDE.md Verifying, tests/CLAUDE.md interactive row, root CLAUDE.md gate-skip bullet; the why in gate-stamp.py's area comment and the Makefile's BROWSER_SKIP comment
- [x] T06 `make hooks-test` green, `make done` green (SC-003); land DIRECT
      research: rendering
      verify: DONE. DONE. make test-full green with the skip live: the line 'browser tests: already green against exactly what they read - skipped' printed, 3,022 passed (the 17 browser tests left out, the 6 new tooling tests in), coverage 100% on both floors, 365 s; make hooks-test green (2 suites re-run, 19 unchanged); make done itself short-circuits on this delta (no engine content changed) so the phases-run stamp site is proved by test_browser_skip.py's recipe assertions; landing DIRECT
