# Research - 206 Skip the browser tests when nothing they read changed

RENDERING/TOOLING research, nothing physical. Measured in the container on 2026-09-07.

## R1. What the synthetic package costs inside a gate - and it is not 3 GiB

The GM's request rests on *"saving three gigabytes of RAM"*. That number was the ROLLED-PAGE browser tests
(retired earlier the same day): every xdist worker rolled its own Inashiro and Kuwabata and launched its own
Chromium, and the package alone peaked at 3.9 GiB at 8 workers. Measured after the retirement, with the 17
synthetic tests the only browser tests left:

| run | wall | peak in the container | Chromium | Python |
|---|---|---|---|---|
| the package alone, 8 workers | 5.4 s | - | one browser | - |
| `make test-full`, 8 workers | 361 s | 6.8 GiB (idle baseline ~4.0 at the start of that run) | 432 MB, 6 processes, for under 9 s | 3.0 GiB |

So the skip saves about 430 MB for under 9 s of a six-minute run. The gate's remaining memory is the
eight coverage-traced workers and the map rolls, which this feature does not touch. The GM's other grounds
stand: the check is the project's pattern for tests with enumerable inputs (feature 172's `hooks-test`
skip, 188's `page` stamp), it is cheap, and the package grows with every tier that gets a page.

**What the GM's concurrency point actually needs**: one gate peaks near 6.8 GiB in an 8 GiB container, so
two sessions running `make done` at once can reach the cap on their own. That wants a host-wide gate lock
(the mechanism `idle-tests` already uses, feature 136) and is not this feature; recorded here so the number
is not lost.

## R2. What the synthetic tests read

`tests/full/interactive/page_browser/test_synthetic.py` and its `_driver.py` / `conftest.py`:

- `render_page` (`interactive/page.py`) over hand-built strings - so the page writer, `tags.py`, and
  everything `render_page` inlines: `assets/page.js`, `assets/page.css`, the glossary, the place card
  (`place.py`), and the class registry (`classes/*.py`, whose DOCSTRINGS are the modal text the tests
  compare against `CLASSES[key].name`, `.label`, `.caveat`, `.siblings`).
- `sources.research_questions()` at page-write time, which reads `research/*.html` headings to build the
  references modal's links; `test_glossary_terms_carry_their_definition_and_the_references_open_on_top`
  asserts those links exist and point into `RESEARCH_PAGES`.
- The installed Playwright and its Chromium: the whole point of a browser test is the browser.

Not read: any map roll, the pool, the settlement engine. A change there cannot change these tests' outcome.

## R3. Why a skip cannot loosen the coverage floor

Feature 174's lesson - *"a deselected test takes its coverage with it, so there is no arrangement that holds
a 100% floor over a partial suite"* - is about a deselection that HIDES a gap: coverage measured over fewer
tests is lower, never higher. So skipping the browser package can only make the floor STRICTER on that run.
If a Python test that covered a line were ever deleted while the browser package still covered it, the
next gate that skipped the package would go red on that line and say so; it could not go green. Measured
besides: `make cov-file` over `tests/interactive` misses 9 lines of `page.py` (405, 458-459, 672-674,
853-855) and the browser package misses the same 9 - it reaches no engine line the Python tests do not.

## R4. A skip key is not a push obligation

`gate-stamp.py --check`, run by the push, refuses any area whose files changed since `origin/main` without
a matching green stamp. The `browser` key deliberately includes `research/*.html` and the test package (R2),
so if `--check` saw the area, a research edit or a test edit would be refused at push for want of a
`page-check` - a new obligation the GM did not ask for, on files that owe none today (tests-only changes
owe no gate at all: feature 132 FR-024). So `--check` skips the browser area, and the area's docstring says
it is a skip key only.

## R5. The stamp is earned by a run that ran the package

Feature 188 found the hole in its own first draft: a stamp written by a run that did not execute the thing
it vouches for. Here the two earning sites are `make page-check` (always runs the package) and `make done`'s
phases-run exit when the package was not skipped in that run. A `done` that skipped it leaves the stamp
alone: the stamp already equals the key, and rewriting it would be the "re-stamps rather than earns"
pattern the `done` short-circuit's own comment warns about.

## R6. The browser version, read without launching one

`importlib.metadata.version("playwright")` and the `chromium-*` directory names under Playwright's browser
cache (`PLAYWRIGHT_BROWSERS_PATH`, default `~/.cache/ms-playwright`) - the build number is in the directory
name (`chromium-1234` today). Launching a browser to ask its version costs about a second and is exactly
the kind of side effect a stamp check must not have. Playwright absent: the salt is "absent" and the tests
skip themselves anyway.
