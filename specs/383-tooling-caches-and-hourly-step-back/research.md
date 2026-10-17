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
| (observed 2026-10-13; method: each step run alone in the worktree, timed by hand) | |
| `git worktree add --detach` | 1.4 s |
| `make hooks-test` (4 guard suites stale, 42 unchanged; then the scripts' pytest files, 60, 57 of them `tests/tooling`, `-n 4`, no reuse) | 80.7 s |
| of which: the deps loop (37 `hookdeps.py --deps` calls) | 6.1 s |
| of which: the four suites alone - sync-with-main 33.2, review-gate 22.1, entry-gate 18.9, gate-stamp 4.4 (run in parallel: about 33 s) | |
| of which: the scripts' pytest files (by difference; 28.1 s as one `make test-file` at the full worker count) | about 45 s |
| `make test-file FILE=tests/tooling` with reuse (606 of 1,798 tests ran) | 30.2 s |
| `scripts/sync-with-main.sh render-sync`, nothing to render | 0.8 s |

Landings in the event log (observed 2026-10-13; method: the `ms` of every `make land-tooling` event in `.git/l7r-events/`): four runs, median 153.8 s. So the guard suites' step is the largest, and 57
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

Over the run's workers (8), the 41.4 test-seconds are about 5 s of wall time in a landing (observed 2026-10-13; method: the test-seconds divided by the workers).

**A landing, step by step** (SC-013; FR-017's log, `<git dir>/land-tooling-steps.jsonl`, two real landings 2026-10-13):

| step | before (13:47, load 3.49) | after (13:58, load 3.44) |
|---|---|---|
| key | m:land-tooling-landing-before | m:land-tooling-landing-after |
| prepare | 0.26 s | 0.26 s |
| worktree | 1.38 s | 1.39 s |
| patch | 0.51 s | 0.55 s |
| guard-suites | 70.06 s | 17.92 s (side by side with the next) |
| tooling-tests | 25.11 s | 25.07 s (370 of 1,801 tests ran) |
| checks (wall) | 95.17 s (the two in turn) | 25.11 s |
| push | 16.68 s | 9.74 s |
| total | 113.98 s | 37.05 s |

What the two landings differ in besides the cuts (observed 2026-10-13; method: the two landings' logs, and the R7 and clone runs named): the before ran four stale guard suites and the scripts' pytest phase over 60
files (57 of them tooling files, run again in the next step); the after ran one stale suite and that phase over the 3 files
outside `tests/tooling/`. A landing with the before's four suites stale would take their 33 s (research R7) beside the
tooling tests' 25 s - about 35 s of checks. The tooling tests' 25 s ran on cores shared with the guard suites; the same reuse
run alone in the clone takes 12.9 s (297 tests). Of a tooling run, startup and collection are 4.5 s, and the reuse decision
1.4 s more (every worker reads the content ids and asks the git questions).

**The push** (FR-019, observed 2026-10-13, method: each command timed alone in a fresh worktree at main, load 2; m:claims-gate-push): the claims gate was 8.56 s of it - it parsed
every module of the base tree again on every push. Its units are now kept by module content (`claims.base_cores`, a
`claims_base_by_module` memo), 1.65 s warm, its output byte-identical with `L7R_CACHE_OFF=1`. The rest: the push's Python
checks in one process 2.46 s, `entry-gate.sh` 1.70 s, `git fetch` 0.18 s, `review-gate.sh`, `plan-gate.sh` and `make
perf-review` under 0.1 s each; the push itself and render-sync (0.8 s) are network and lock time.

**Found on the way and fixed:** the reuse summary line never printed under xdist (the workers deselect, the controller did
not know) - the workers now report it; `make append` judged a review-ledger row only at the commit, which a commit in the same
command as the append passed unjudged - the row is now linted before it is appended.

**Remaining, recorded** (FR-019; observed 2026-10-13, method: the measurements above): the tooling tests' 18 always-run files (41.4 test-seconds, about 5 s of wall, the table
above); startup and collection 4.5 s; the guard suites a landing's files reach (each runs whole, 4 to 33 s, beside the tooling
tests now); the push's network and lock time.

## R10 Amendment 3 - review checks on Sonnet 5.5

**The cases** (observed 2026-10-17; method: `scripts/measure/model_trial.py`, each recorded Opus run joined to its ledger row by
its cost cells, the newest replayable run with findings the session then fixed and the newest clean one). Each case is a
separate clone at the commit the recorded run read (the recording clone's reflog), with its bundle frozen from the run's own
inputs (a bundle unchanged since the run) or its review snapshot rebuilt there (the map drawn at that commit and at main's tip
of the time, from the mirror's reflog; the dispatch read back from the recorded transcript). Only the tested agent's copy
names `claude-sonnet-5-5`; every hook is off. Three runs a case.

| check | case | recorded run (start, UTC) | commit read | the recorded Opus verdict and findings (its ledger row) |
|---|---|---|---|---|
| spec-fidelity | findings | 2026-10-17T12:23 | 053c01c58 | CHANGES REQUIRED - 1: the GM's right away not carried |
| spec-fidelity | clean | 2026-10-17T12:26 | e7555d74e | CLEAR - - |
| glyph-check | findings | 2026-10-13T08:27 | 03cef6f31 | NEEDS-WORK - bands a third of the farm wide (58-79 ft of 222-249); floating between farms; tile cut at the band edge |
| glyph-check | clean | 2026-10-12T15:07 | 8d6545c01 | PASS - none |
| impl-drift | findings | 2026-10-11T09:54 | 1faad0c08 | IN-STEP 6, MISLABELED 3 - LANE_ROOM_FT, WAY_IN_FT and dispersed_layout's 32 ft and 36 ft claimed as research where 0036's drawing page records GUESS; well pocket UNCLAIMED |
| impl-drift | clean | 2026-10-11T09:57 | 1faad0c08 | IN-STEP 10 - nothing |
| building-review | clean | 2026-10-10T13:36 | 7817f4a30 | PASS - E1, E2 verified; N1, N2 nitpicks |
| modal-form | findings | 2026-10-13T04:10 | ca9c595f8 | 0 FIX, 2 NOTE - a source kind named in Depiction; an off-subject clause in the opening |
| modal-form | clean | 2026-10-12T20:19 | 2cf5a3ee0 | 0 findings - none |
| modal-research | findings | 2026-10-13T02:04 | 828f5b626 | ACCURACY 2, REFERENCES 1, GAPS 2 - each house overstated; the build said unrecorded where Suzhou records it; the kabata's other uses |
| modal-research | clean | 2026-10-13T07:59 | ef549b6f5 | ACCURACY 0, REFERENCES 0, GAPS 0 - none |
| modal-depiction | findings | 2026-10-13T02:15 | 828f5b626 | COVERAGE 1, TRUTH 1, LINKS 0 - the drawing convention untold; "elsewhere shared" read as a mix within one settlement |
| modal-depiction | clean | 2026-10-13T11:24 | 6cf8300c5 | COVERAGE 0, TRUTH 0, LINKS 0 - clean; the 0196 page does not name the reserved ways, drawn as lanes on the finished map |
| building-review | findings | 2026-10-10T10:25 | 72ba8035a | NEEDS-WORK - E1 the outer court's yard painted over the moved court (fixed, a zone-overlap test); E2 notes stale (fixed); E3 the long-house squat (a found row); E4 the barra |
