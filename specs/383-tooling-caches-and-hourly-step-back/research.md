# Feature 383 - research

## R1 - what the record build check reads (plan D2)

Measured 2026-10-12 with an audit hook on `open` during one `record_asset --check` in this clone: it opened 29 files under
`l7r/diagram/`, every other file under `research/` (`archive/` 3,222, `sources/` 3,238, `questions/` 1,428, `assets/` 5, and
seven JSON files at the top), and 55 standard-library files. Nothing else in the repository. Of the 29 under `l7r/diagram/`,
the one that is no module is `l7r/diagram/interactive/assets/glossary.json`; it never opens `pyproject.toml`. So the memo's
inputs are `research/` and `l7r/diagram/interactive/assets/`, with the code sha of the module run and every project module it
imports standing for the 28 modules, and the Python version for the standard library. Listing their content ids
(`git ls-files -s`, `git diff --name-only`, the untracked files under them) took 0.04 s (observed 2026-10-12; method: `time`
over the three git listings).

## R2 - the baseline (SC-001)

`m:push-checks-before` in `measurements.json`: the push's checks that read the tree, 19.87 s in all at load 4.2, the record
build check 6.38, the research pointers 4.70, duplicate definitions 1.88, the function cap 1.46, conflict markers 1.25,
the old layout 1.16, the ledger 0.89, the rest under 0.35 each.

## R3 - the rest of the push's checks, and the record's rebuild (plan D2, D3)

Observed 2026-10-12 in this clone; method: each check of `push_checks.py`'s table run twice inside one interpreter
(`run_one`), the second run's wall time kept. Duplicate definitions 0.13 s, stale directories 0.01, file scale 0.16, the
function cap 0.19, the ledger 0.03, entry headings 0.00, research pointers 0.17, partial citations 0.23, the download list
0.04, spec-lint 0.07, the Affects check 0.18, conflict markers 0.32.

- Partial citations, kept per file (the registry write-ups and archive manifest rows read by `access_tags.load`, and the notes
  files): 0.33 s against 0.32 s without (observed 2026-10-12; method: `/usr/bin/time`, second of three runs). Listing the
  content ids of 5,400 small files costs what reading them does. Reverted.
- File scale, profiled (observed 2026-10-12; method: cProfile, one run): the directory census 0.08 s, the line counts 0.06 s.
- The Affects check read every feature twice; read once, 0.25 s to 0.15 s (observed 2026-10-12; method: `/usr/bin/time`).
- The record check (observed 2026-10-12; method: `/usr/bin/time` on `make record CHECK=1`): cold 5.63 s; after one question
  file changed, with each unchanged page's notes kept, 5.15 s; replayed 0.15 s. Unprofiled, the build's setup is 1.76 s and
  its render 3.38 s; the render reads the whole record's link index for every page.

## R4 - the record build's setup, step by step (plan D2)

Observed 2026-10-12 in this clone; method: each step of `site.Build`'s setup timed with `perf_counter`, the second of two runs
in one interpreter, nothing kept. The per-file steps - each reading one file's text alone - go through the store's per-file
memo; the cross-file steps read the whole record and are left to the whole-check memo:

| step | s | kind |
|---|---|---|
| a page's notes (`page_notes`, every page) | 0.52 | per file: kept |
| the URLs of each registry entry and notes file (`archive.cited`, run twice a build) | 0.27 each | per file: kept |
| the registry's items (`Registry`) | 0.33 | per entry: kept (the assembly and split read the whole registry) |
| a page's cross-link and confusables (`page_html`, every page) | 0.40 | cross-file: the pairs and confusables were read once per page (0.31 s of it, observed 2026-10-12; method: perf_counter over the 477 calls); now once per build |
| the archive's manifest rows (`archive.load`) | 0.06 | per file, but cheaper than keeping |
| the questions (`store.load`) | 0.04 | cross-file (tags, sections) |

The record check after one question's edit, the memo warm: 4.85 s, against 5.46 s with nothing kept (observed 2026-10-12;
method: `/usr/bin/time` on `make record CHECK=1`, `L7R_CACHE_OFF=1` for the second). The render, which reads the whole record's
link index for every page, is the rest.

## R5 - the step-back replayed on two past hours (SC-008)

Observed 2026-10-13; method: `make step-back TRIGGER=... TRANSCRIPT=... SINCE= UNTIL=` on the backlog session's own transcript and
event log (read only), each bundle handed to the `round-arbiter` agent with the instruction not to record (a replay).

- **Batch 13's hour, 22:15 to 23:15 UTC 2026-10-12** (the bamboo strip): `change-route`. "The strongest signal is packing ...
  it never asked whether the farmstead has room. The numbers it is fitting against are `PART_GAP_FT = 2.0`, the `(0.0, 1.0)`
  offset ladder, the strip's reach (`within_reach_of`) and the bundle's seat margin ... none of them research-tagged". Route:
  more room in the farmstead lot first, not a longer ladder, a smaller gap, a shorter strip or a lower prevalence. It also
  gave a `tooling_fix` (`make test-file ARGS=` so a probe needs no temporary test file) and a `for_gm` (three shipped maps
  declare homestead bamboo with none drawn). The hour the GM named as the worked example is named, with its numbers.
- **A quiet hour, 21:15 to 22:15 UTC 2026-10-12**: `continue` - no oscillation, no packing ("the session kept their labels and
  defended none of them"). It gave one `tooling_fix` (flag a map whose meta records an element drawn while its ink classes
  have none), from a missed review the session found by hand that hour.

## R6 - the push's checks after phases 1 and 2 (SC-001)

`m:push-checks-runner-after`: the runner, one process, 1.92 s - against `m:push-checks-before`'s 19.87 s for the same checks
(gate-stamp and the closing check added). Run as separate processes they now sum to 3.43 s (`m:push-checks-separate-after`):
the content-keyed cache took 16.4 s off, and one process took 1.5 s more.

## R7 Where a landing's time goes (amendment 2, measured 2026-10-13 by hand)

A worktree at origin/main (2026-10-13 09:22, load 1.8 -> 5.1), each step of `make land-tooling` run alone in it:

| step | time |
|---|---|
| `git worktree add --detach` | 1.4 s |
| `make hooks-test` (4 guard suites stale, 42 unchanged; then the scripts' pytest files, 60, 57 of them `tests/tooling`, `-n 4`, no reuse) | 80.7 s |
| of which: the deps loop (37 `hookdeps.py --deps` calls) | 6.1 s |
| of which: the four suites alone - sync-with-main 33.2, review-gate 22.1, entry-gate 18.9, gate-stamp 4.4 (run in parallel: about 33 s) | |
| of which: the scripts' pytest files (by difference; 28.1 s as one `make test-file` at the full worker count) | about 45 s |
| `make test-file FILE=tests/tooling` with reuse (606 of 1,798 tests ran) | 30.2 s |
| `scripts/sync-with-main.sh render-sync`, nothing to render | 0.8 s |

Landings in the event log: four `land-tooling` runs, median 153.8 s. So the guard suites' step is the largest, and 57
files of its pytest phase run twice in a landing - once there, without reuse, once in the tooling test run.

## R8 Which tooling test files always run, and what they cost (amendment 2, measured 2026-10-13)

Method: `make test-file FILE=tests/tooling` in this clone with `PYTEST_ADDOPTS="--junitxml=<out>"` (per-test times, summed per
file, over 8 workers), against the kept passes in `.git/l7r-cache/tooling-test-passes.json` (each file's `opaque` programs, and
any read of a file git ignores). 126 files kept, 38 of them always run; their tests take 101.7 of the run's 174.7
test-seconds. By the program that makes a file run, in test-seconds:

| cause | test-seconds |
|---|---|
| git asked about the repository | 28.9 |
| a Python child that drops the recording (`python3`) | 28.3 |
| `source-block-hooks.sh` | 16.3 |
| git and ruff | 5.9 |
| node | 4.7 |
| resvg | 4.1 |
| bash | 2.9 |
| bash and claude | 2.9 |
| ruff | 2.5 |
| make | 1.8 |
| a file git ignores, read | 1.6 |
| pdftotext | 1.0 |
| grep and pdftotext | 0.4 |
| bash and make | 0.3 |

The git-only files, largest first: test_content_cache 13.6, test_open_questions 4.9, test_check_bundle 2.9, ci/test_state 1.8,
test_bundle_owed 1.2, test_downloads 0.9, test_record_prepass_and_size_table 0.8, test_translation_owed 0.6, the rest under 0.6.
Some of them also read a file git ignores (ci/test_state `.git/semantic-id-cache.json`, test_check_bundle `.git/record-checks/`),
which keeps them running until that read is known too. `scripts/measure/tooling_reuse_time.py` prints the file counts again. On amendment 2's first recording with Python children adopted
(2026-10-13), 0 of 126 files ran a child isolated (`-I`, `-E`, `-S`).

## R9 Amendment 2 - what was made known, what stays, and a landing step by step

**The tests write nothing in the repository** (the premise of plan D18, measured 2026-10-13): `git status --porcelain --ignored`
of this clone was identical before and after a whole tooling run (1,800 tests, `L7R_TEST_DEPS=off`), and no file outside `.git`
and the byte-code and lint caches was newer after it than before, but the session's own edits made during the run.

**Made known** (each file now reused on identical inputs, plan D18-D20): every file whose only cause was a git question or a
Python child; four files that seemed to read `.git` (an `os.open` by name under `shutil.rmtree`'s directory handle, resolved
against the repository); two content caches under `.git` (`semantic-id-cache.json`, the translation pairs' `ParseCache`); the
clone's `.specify/feature.json` (the tooling tests now run under one fixed `SPECIFY_FEATURE`); the stale agent worktrees'
Makefiles (`test_makefile_recipe_comments` now checks the tracked ones).

**Stays** (FR-020): each program below is what its test file exists to run, or writes what it produces, so its reads cannot be
asked again as a git question is; making each known would mean modeling what that program reads. Test-seconds measured
2026-10-13 (`make test-file` of the 18 files with `--junitxml`, `L7R_TEST_DEPS=off`, load about 4), 41.4 in all:

| file | program | test-seconds | why it stays |
|---|---|---|---|
| test_guard_firing_log | `source-block-hooks.sh` and every other guard (bash) | 16.5 | the guards are the subject; a bash script's reads (its sourced libraries, the tools it pipes through) are not seen by any recorder here |
| test_push_checks | ruff | 5.6 | ruff on the test's own temporary files: those are gone or changed when a landing would ask again, so the same question is not the same input |
| test_modal_checks | node | 4.7 | the modal checks' script is the subject; node's reads are not recorded |
| pipeline/test_gencache | resvg | 3.1 | it writes the render it produces |
| test_page_session | bash, claude | 2.9 | the page-session runner (bash) and a stand-in `claude` are the subject |
| test_function_cap | ruff | 2.1 | as test_push_checks |
| test_plan_gate, test_hm_checks, test_one_gate, test_setup_ensure | bash | 3.1 | a guard or gate script is the subject |
| test_archive, test_archive_ops | pdftotext, grep | 1.4 | pdftotext writes its text file; grep with it on the archive's own fixture files |
| test_soak_suite, test_invocation, test_make_docs, test_coord, test_gate_record_and_shortcut, test_test_file_target | make | 1.8 | make runs recipes in the repository; what they read is not known |

Over the run's workers (8), the 41.4 test-seconds are about 5 s of wall time in a landing.
