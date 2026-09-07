# Feature 206 - skip the browser tests when nothing they read changed

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5; round 1 struck the `BROWSER_ALL=1` flag from
FR-002) - cleared for implementation (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - what the package costs, what it reads, why a skip cannot loosen
the coverage floor, and why the skip key must not become a push obligation.
**Predecessors**: feature 172 (`hooks-test` skips the suites whose guards did not change - the stamp pattern
this copies); 188 (the `page` stamp and `make page-check`); 174 (the gate runs everything under the floor).

## Summary

The GM: *"Do we have logic in place to skip them if the content which they are testing has not changed? ...
this is about saving memory, not saving time ... having these kinds of checks... to prevent us from running
unnecessary tests will only become more useful as this project matures."* The 17 synthetic-page browser tests
in `tests/full/interactive/page_browser/` run on every gate that runs at all. This feature gives them a stamp:
a green run records a key over everything the tests read, and the gate's test phase leaves the package out
while that key is unchanged, saying so in one line. Nothing else about the gate changes.

## Functional requirements

- **FR-001 The browser key.** `scripts/gate-stamp.py` gains a `browser` area whose files are everything the
  synthetic tests read: every `.py` under `l7r/diagram/interactive/` (the page writer, the registry whose
  docstrings are the modals, tags, glossary, sources, place, raster), the two assets under
  `interactive/assets/`, the test package `tests/full/interactive/page_browser/` itself, and `research/*.html`
  (the references modal's links are built from the record's headings at page-write time). Hashed by BYTES
  like the `page` area, because the registry's docstrings are page prose. The key is salted with the
  installed Playwright version and the installed Chromium build, read without launching a browser, so a
  browser upgrade re-runs the tests.
- **FR-002 The skip.** The gate's test phase (`make test`, which `make done` and `make test-full` call)
  passes `--ignore=tests/full/interactive/page_browser` when the `browser` stamp matches the current key,
  and prints one line saying the package was skipped and why. When the key differs, or no stamp exists,
  the package runs exactly as today - and nothing else: no flag forces either direction (round 1 of the
  spec review struck a `BROWSER_ALL=1` override as unrequested, the same ruling the `done` short-circuit
  records for its `FORCE=`; the way to run the package on demand is `make page-check`, which always does).
- **FR-003 Earning the stamp.** The stamp is written only by a run that RAN the package and went green:
  `make page-check` (which always runs it), and `make done`'s phases-run exit when the package was not
  skipped in that run. The already-verified short-circuit writes no browser stamp (it ran nothing), and a
  `make done` that skipped the package leaves the stamp as it found it.
- **FR-004 A skip key, not a push obligation.** `gate-stamp.py --check`, which the push runs, ignores the
  `browser` area: a change to a research page or a test file must not be refused at push for want of a
  browser stamp. The existing obligations (`diagram`, `hooks`, `page`) are unchanged.
- **FR-005 The floor is untouched.** No coverage configuration changes. A skipped package can only lower
  measured coverage, never hide an uncovered line, so the 100% floor still tells the truth (research R3).
- **FR-006 Tests.** Tooling tests prove: the `browser` area's file list contains the page script, the
  stylesheet, the page writer, a registry module, a test module of the package and a research page, and
  nothing under `tests/` is excluded from it; the stamp goes stale when any one of those files changes and
  when the browser salt changes; `--check` passes a delta that changes only a research page with no browser
  stamp present; the Makefile's `test` recipe carries the skip, `page-check` and `done`'s phases-run exit
  write the browser stamp, and the short-circuit does not. The skip is shown to fire once (SC-002).
- **FR-007 The record.** The why at each point of change (the area's comment in `gate-stamp.py`, the
  Makefile variable), a line in `interactive/CLAUDE.md` "Verifying", the `full/` row of `tests/CLAUDE.md`,
  and the root `CLAUDE.md` bullet that lists what `make done` skips.

## Success criteria

- **SC-001** On a gate where nothing in the browser key changed since the last green run that included the
  package, the test phase's pytest line carries the ignore and the package's 17 tests are not collected.
- **SC-002** Shown once: a green `make page-check`, then `make test-full` with the package skipped; then one
  byte of `page.css` changed and the package runs.
- **SC-003** `make done` green; the tooling tests green; `make hooks-test` green for the guard script.

## Decisions Recorded

- **D1 - a separate area, not a wider `page`.** The `page` stamp is what the push DEMANDS of an asset edit;
  this key is what the gate may SKIP. Widening `page` to the whole interactive package would have made a
  page-writer edit owe `page-check` at push on top of the gate it already owes. Two questions, two areas.
- **D2 - the key is conservative.** `research/*.html` is in it because the synthetic references test builds
  its links from the record's headings; a research edit therefore re-runs the package (5 s of one worker).
  The GM may narrow the key; the record says why it is wide.
- **D3 - the browser version is in the key.** The tests exist to catch the page misbehaving in a browser;
  a browser upgrade is an input. Read from the Playwright package version and the installed Chromium build
  directory, never by launching a browser.
- **D4 - `test-full` on its own does not stamp.** It stamps nothing today (no `diagram` stamp either); the
  two earning sites are `page-check` and `done`, as for `page`.
