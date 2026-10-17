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
| (observed 2026-10-17; method: each recorded run read from its transcript, its ledger row joined by its cost cells) | | | | |
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

**The results** (observed 2026-10-17; method: each run's reply read against the recorded Opus reply, finding by finding; a new
finding checked against the page or sheet before it is called real). "Hit" counts the three Sonnet runs that found a known
finding.

| check | findings case: the known findings and how many of 3 runs found each | clean case: a new finding raised | moves? |
|---|---|---|---|
| spec-fidelity | the GM's "right away" not carried: 0 of 3 (two runs FAITHFUL, one CHANGES REQUIRED on two other points) | none (3 CLEAR) | no |
| glyph-check | the bamboo band a third of the farm's width, not its whole south side: 0 of 3 (one PASS; two NEEDS-WORK on bands standing apart in the scrub) | none (3 PASS) | no |
| impl-drift | the three MISLABELED claims: 3 of 3; the UNCLAIMED well-pocket decision in `canonical_farmstead`: 0 of 3 | one run named two UNCLAIMED sun-band decisions, unchecked | no |
| building-review | E1 the outer court painted over the hearing court: 3 of 3; E2 stale notes: 3 of 3; E3/E4 the squat long-house and barracks (older than the change, filed as a row): 0 of 3 | none (3 PASS) | no |
| modal-form | the source kind named on Depiction: 3 of 3; the off-subject clause in the opening: 0 of 3 | none | no |
| modal-research | each house overstated, and "unrecorded" where Suzhou records the build (ACCURACY 2): 2 of 3 runs found one, 1 of 3 found neither | **real, which Opus missed**: "another farm's grove" where the page says "one farm" (3 of 3) | no |
| modal-depiction | the drawing convention untold (COVERAGE): 3 of 3; "elsewhere shared" read as a mix within one settlement (TRUTH): 0 of 3 | **real, which Opus missed**: the tab gives every shallow well a sweep where the page says about three in four (3 of 3, one run a second item) | no |

**What it cost** (observed 2026-10-17; method: `model_trial.py usage`, the recorded run's tokens from its own transcript, the
Sonnet runs' from their own result, dollars as the CLI reports them):

| case | Opus recorded, input tokens | Sonnet, each run's input tokens | Sonnet seconds | Sonnet $, three runs |
|---|---|---|---|---|
| spec-fidelity findings / clean | 164k / 234k | 127k, 122k, 123k / 133k, 95k, 133k | 19-24 | 0.25 / 0.26 |
| glyph-check findings / clean | 1,159k / 713k | 238k, 256k, 195k / 156k, 258k, 186k | 25-44 | 0.35 / 0.32 |
| impl-drift findings / clean | 78k / 109k | 218k, 134k, 134k / 229k, 221k, 169k | 30-54 | 1.04 / 0.87 |
| building-review findings / clean | 1,490k / 1,136k | 252k, 257k, 253k / 110k, 108k, 113k | 14-45 | 0.49 / 0.16 |
| modal-form findings / clean | 26k / 24k | 59k each / 56k each | 10-30 | 0.41 / 0.32 |
| modal-research findings / clean | 180k / 274k | 212k, 313k, 427k / 458k, 680k, 496k | 47-88 | 0.71 / 0.98 |
| modal-depiction findings / clean | 74k / 125k | 70k each / 280k, 168k, 213k | 19-42 | 0.26 / 0.86 |

**Reading it.** By the rule (every known finding in all three runs, no false alarm), no check moves: each missed at least one
finding Opus had caught, in all three runs or in most. Two things beside the rule: Sonnet found two real modal errors Opus
had missed, three runs of three each - so the Opus record is not a perfect oracle either, and the misses run both ways; and on
the glyph and building checks Sonnet read a fifth of what Opus read (it skipped the SVG and the pack audit the contract asks
for), which is where both its saving and its misses come from. On the record checks it often read MORE than Opus.

A setup fault, recorded so the next trial avoids it: the first glyph and building runs all returned NOT-REVIEWABLE because a
case's clone had no gate record and the contract stops on a red `make review-paired-gate`; `model_trial.py snapshot` now writes
the gate stamp in the case's clone (the dispatch of the recorded run says the gate was green), and those four cases ran again.

**Tests not imported (FR-022)** (observed 2026-10-17; method: `make collect-cost TREE=quick`, a probe plugin in every process
counting the test modules it imported, load 1.4-2.0):

| run | time | test modules imported per process | tests |
|---|---|---|---|
| (observed 2026-10-17; method: `make collect-cost TREE=quick`, a probe plugin per process) | | | |
| quick as make runs it (testmon selecting, 6 workers), nothing changed | 3.87-4.15 s | 5 in each of 6 workers | none ran |
| the same, no workers | 1.62 s | 5 | none ran |
| collection only, no testmon | 5.44 s | 283 | 9,433 |

So `make quick` already does not import what testmon rules out, in every worker: the first `make quick` of the day's 14.3 s
with no test run (observed 2026-10-17, method: `make quick` on an unchanged tree at load 3, the clone idle four days) was a
cold start, and the next was 7.0 s whole (pytest 2.3 s of it). What is left is the six workers' start when testmon selects
little (about 2.5 s); testmon decides after xdist has fixed the worker count, and a pre-pass to decide costs 1.6 s on every
run that does select tests - not cut. A targeted `make test-file` collects only the files named. The incremental gate
collects everything on purpose (its merge needs every collected node id, `ci/selection.remember_all`); a cut there is a
change to its bookkeeping - not made here. The tooling plugin decided after collection: it now answers
`pytest_ignore_collect` for each reused file, and a reuse run in the clone went 12.9 -> 10.7 s (296 tests ran, observed
2026-10-17, method: `L7R_TEST_DEPS=reuse make test-file FILE=tests/tooling`, back to back).

**The always-run files (FR-021)** (observed 2026-10-17; method: `scripts/measure/tooling_reuse_time.py`): every child is now
recorded - a git question replayed, a Python child adopted, any other program by the preloaded C recorder (`strace` is
refused in the container: no ptrace). Each run checks the C recorder against Python's on every Python child; the one gap
found (a Python child's `os.open` for writing, recorded as a read by Python's own recorder) was Python's, and fixed. Always
run: 18 of 127 -> 0 of 128. Of the 128, five still do not reuse in a fresh worktree because they read machine state a worktree
lacks - `.gencache` (test_gencache), `.git/info/exclude` through ruff's gitignore (test_lint_scope, test_push_checks),
`.coverage` and `.git/verification-state.json` through make (test_soak_suite), the `.git` directory listed
(test_content_cache). In a fresh worktree at HEAD: with reuse 18.39 s, 61 tests ran; without 37.37 s, 1,806 (load 8.1; the
same measurement before this amendment: 19.35 s, 297 ran, load 5.5). In the clone, a reuse run is 7.0 s (26 tests). The rest
of the fresh worktree's time is its cold byte-code: every module compiled again.

**The guard suites (FR-023)** (observed 2026-10-17; methods as plan D27 says):

| what | before | after |
|---|---|---|
| (observed 2026-10-17; method: each suite timed alone, the landings replayed against `hookdeps.py --deps`) | | |
| sync-with-main suite (the slowest) | 36.2 s at 4 parts; `case_11` alone 27.9 s | 17.9 s at 8 parts, `case_11` split in three, weights measured (124 checks either way) |
| sync-with-main and gate-stamp re-run by a tooling landing | 42 of 44 landings (inputs: the whole `scripts/` tree) | only when a file they read changed - traced: after a change to `clone-sync-hooks.sh`, gate-stamp no longer ran |
| suites traced | - | 38 of 44 (the six left read the repository through git or a file git ignores, and keep `hookdeps.py`'s key) |
| `make hooks-test` with nothing to run | 16.1 s (the user-level hook's self-test 7.5 s every time; one `--deps` process per suite 5.9 s) | 2.6 s |
| every suite at once (`HOOKS_ALL=1`, traced) | - | 129 s |

Next, by the per-suite seconds `make hooks-test` now prints (observed 2026-10-17, method: a re-trace of every suite, load
about 6): main-tree 57.8 s, no-poll 52.0 s, finished-run 40.1 s, pair 27.3 s - each runs only when what it read changes, but
each is one long serial run where sync-with-main's parts show the way.

A file added to `scripts/`: the fixture's own `scripts` directory listed is read as the repository's (the plan review's
design note, round 5), and a trace taken by an older recorder counts as stale.

A defect made and caught on the way, recorded: an edit replacing the per-suite key lost one of its two halves to a refused
edit, so for one run every suite's key was the hash of nothing; the next run re-ran each suite whose traced reads had moved
and rewrote the stamps, and the recipe now treats a missing key as never fresh.

**A landing, after amendment 3** (SC-016, SC-017; FR-017's log, observed 2026-10-17 13:54, load 4.06; m:land-tooling-landing-a3):
prepare 0.22, worktree 1.39, patch 0.40, guard-suites 2.76 and tooling-tests 18.58 side by side (checks 18.62), push 9.41 -
30.04 s, against 37.05 s after amendment 2 and 113.98 s before it. 121 of the 128 tooling files reused (1,692 tests); what
ran is the two files that read machine state a worktree lacks (`.gencache`, `.coverage`), and those the change itself reached.
Two last reads were made known on the way: the cache directory itself opened (`.git/l7r-cache`, which marked test_content_cache
as reading git's state), and a file under `.git/` (ruff's `.git/info/exclude`) now keyed by its content in the git common
directory a worktree shares with its clone. The tooling step is now the landing's long pole; of its 18.6 s, the tests that
ran are a few seconds and the rest is the workers' start and a fresh checkout's first imports.

## R11 Amendment 4 - the serial guard suites, and the tooling tests a landing still runs

**The guard suites (FR-025, SC-019)** (observed 2026-10-17; method: each suite run alone under `time`, load 3-5, its check count
from its own summary line, before = the committed suite, after = the changed one):

| suite | before | after | checks (same both) | what changed |
|---|---|---|---|---|
| (observed 2026-10-17; method: each suite alone under `time`, its own summary line) | | | | |
| main-tree | 57.7 s | 18.9 s | 83 | its 173-command corpus (42 of the 56 s) judged eight rows at a time |
| no-poll | 48.4 s | 12.2 s | 113 | sections as cases in parallel parts (`tests/hooks/parts.sh`), helpers hoisted, a stderr file and guard log per part |
| finished-run | 39.1 s (4.9 s of CPU) | 11.3 s | 65 | each fixed settle sleep a readiness poll, at most the old sleep; stable over five runs |
| pair | 23.5 s | 12.8-17.4 s | 88 | its two 15 s cases split at their own resets, weights measured, 4 -> 8 parts |
| review-gate | 21.8 s | 8.9 s | 43 | sections as cases in parts, a shared constant moved before them |
| sync-with-main | 17.9 s | 18.1 s | 124 | its runner moved to `tests/hooks/parts.sh`, shared |

Every split suite also passes at 1, 2 and 3 parts. Doing so found a dependency older than this amendment: pair's case_02
assumed no green gate and case_04 leaves one, so with the measured weights dealing case_04 first into the same part, case_02
failed; case_02 now clears the gate record before its check.

A defect made and caught (observed 2026-10-17; method: the laptop's memory watch and the run's own failure): the first `make hooks-test HOOKS_ALL=1` after the splits ran eight suites of up to eight parts each and
hit the containers' shared 10 GB memory cap (memguard killed a process of another session's container; a timed sync-with-main
check failed under the load). `make hooks-test` now sets `PARTS_MAX` to the cores shared by the suites running (one suite up to
8 parts, eight suites 2 each), which `parts.sh` and pair's runner honor. Every suite at once (`HOOKS_ALL=1`, observed 2026-10-17,
peak 8.6 GB used): 162 s, all 46 green, against 129 s this morning - with every suite running the machine is saturated and
parts only share it; the splits pay where a few suites run, which is every ordinary `make hooks-test` and every landing.

**The whole-repository tooling tests (FR-026)** (observed 2026-10-17; method: `--durations` in this clone and a fresh worktree):
- test_content_cache's whole-repository test, 9.4 s, is one test per check run side by side - the pointer check 6.0 s, the
  conflict check 3.6 s - each still comparing the cache-off, cold and warm answers over the whole repository, the off and cold
  runs together. The pointer check's own uncached run is 5.1 s, the floor: three rewrites of its line filter measured slower
  than it over all 22,439 tracked files (3.77, 4.93 and 4.83 s against 3.34 s, the same lines found) and were reverted.
- test_open_questions' real-tree test, 4.8 s: the tool is 3.4 s of it; a rewrite of its labeled-line scan measured 3.40 ->
  3.30 s and was reverted; the two calibration loops (1 s) are what its CPU bound is judged by and stay.

**A landing's tooling run, its start (FR-027)** (observed 2026-10-17; method: a fresh worktree at the clone's HEAD, runs back to
back, load 3-5):
- workers: a run with everything reusable but 20 tests took 7.4 s at 10 workers, 5.5 s at 6 (the default here), 5.1 s at 2,
  6.0 s at 1 - the count is not where the time is;
- the reuse decision once in the controller, handed to the workers: 13.86-13.99 s against 13.90 s without - no gain, reverted;
- byte-code compiled first: 18.9 s against 17.6-17.8 s without - no gain;
- what is left: pytest and xdist import in 0.18 s; a run of one small file is 2.0 s (make, pytest, the workers' start) and the
  reuse decision 1.2 s more; the rest is the tests that read the whole repository, which re-run whenever main or the clone
  moved since the clone's last recording (right after a recording, a fresh worktree at the same commit reuses all but the two
  files that read machine state).

**A landing, after amendment 4** (SC-020; FR-017's log; m:land-tooling-landing-a4, observed 2026-10-17 15:59, load 4.26): prepare
0.19, worktree 1.48, patch 0.65, guard-suites 3.09 beside tooling-tests 14.94 (checks 14.98), push 9.98 - 27.28 s, against
30.04 s after amendment 3 (load 4.06; m:land-tooling-landing-a3). An earlier landing the same hour, at load 6.3, was 27.97 s
(tooling-tests 15.41). The tooling step went 18.6 -> 15 s: the whole-repository test that set its floor now runs as two.

What the suites' splits do not change: when many suites run together the machine is the limit. In the clone's own `make
hooks-test` before that landing, 13 suites re-ran at once and sync-with-main took 71.6 s at 2 parts (observed 2026-10-17, method:
the run's per-suite line, load about 6), where it is 18 s alone - the parts cap shares the cores, it cannot add them.

**The arbiter's tooling fix on the hour's step-back** (hour:383@3): `make parts-sweep` runs each split suite at 1, 2, 3 and 8
parts and reports any count whose summary differs (`tests/hooks/parts_sweep.sh`, its test `tests/tooling/test_parts_sweep.py`,
which plants a case-order dependency and sees it found). Run on the five split suites (observed 2026-10-17, method: `make
parts-sweep`): every one the same at every count, 773 s in all - a command to run when a suite's cases change, never the gate.

## R12 Amendment 5 - the gate's tooling tests, a pass per test, and the tests that read the record

**Where the gate runs the tooling tests (FR-028)** (observed 2026-10-17; method: the Makefile's `test` recipe, `tests/conftest.py`,
`l7r/diagram/ci/incremental.py` read; the baseline's `coverage.db` against its `tests.json`):
- not through `make tooling`, as plan D31 first said: inside the gate's one coverage run, collected whenever the run is floored
  (`L7R_TESTS_FULL`), and run only on a FULL plan - a moved tooling hash forces one, and a full plan's coverage becomes the next
  baseline by itself (feature 207 D1);
- all 1,796 of the baseline's tooling node ids carry engine coverage contexts, so a test simply left out would take its
  coverage out of the floors that run and out of the next baseline; the gate therefore carries a reused test's coverage from
  the baseline (`incremental carry`), and judges reuse against the reads that PRODUCED that coverage, kept beside the baseline,
  not against the clone's store, which a later run may have re-recorded on different content.

**A defect in reuse, found by measuring (D32b)** (observed 2026-10-17; method: a one-line edit to `l7r/diagram/ci/delta.py`, a
reuse run of the whole tree, the edit reverted):
- before: 36 tests ran and most of `test_delta.py`'s 55 were reused against the changed module - a module is opened once per
  worker, and a test that only called code another had imported never recorded it (the per-file store of amendments 1-4
  reused `test_delta.py` whole, the same hole wider; 30 module-level imports of `l7r` modules were missing from their test
  file's reads);
- after: each code object a key runs is that key's read (`sys.monitoring` PY_START, re-armed per key), and a wide fixture
  defined in a test module is that file's read; the same edit re-runs 178 tests. Landed as tooling at once (every landing's
  reuse rests on it).

**A pass kept per test (FR-029, SC-022)** (observed 2026-10-17; method: `make test-file FILE=tests/tooling` to record, then
`L7R_TEST_DEPS=reuse` runs of the whole tree, timed):
- the store: 21.7 MB with each test's read set kept whole, 10.7-10.8 MB with each content kept once (D32a);
- an unchanged tree: 1,825 of 1,827 reused, 6.5 s, against a 55.7 s record (two tests read files git ignores and always run);
- one research source page edited: 15 tests ran in 13.6 s; per file it would have been 219 tests in 12 files (before the
  moves below, 16 per test).

**The gate after a Makefile-only change (SC-021)** (observed 2026-10-17; method: a comment line appended to the Makefile, the
gate's test phase run as `make done` runs it, `make test-full FROM_DONE=1`, the Makefile restored; the run before it was the
same phase with nothing reusable):
- the plan went full ("the tooling changed"); 1,739 of 1,824 tooling tests were reused, 102 files not collected, and their
  coverage carried - the 85 that ran are the tests whose kept reads hold the Makefile (87 in the baseline after) and one that
  reads a file git ignores; every floor at 100%, the baseline saved;
- the phase took 132 s, against 167 s for the same phase with no tooling test reusable.
- a first probe reused nothing: a merge from main between the two gates changed files under `tests/tooling/`, and against the
  baseline it saved 1,739 were reusable - the measurement above is the probe repeated with nothing else moved.

**The tests of code that read the record (FR-030)** (observed 2026-10-17; method: each test's kept reads outside `l7r/`, `scripts/`,
`tests/` and the configuration, before the move from the per-test store, after from a fresh record):

| test | data files read before | after | how |
|---|---|---|---|
| (observed 2026-10-17; the kept reads) | | | |
| test_check_bundle: 7 tests on the bundler | 475-4,656 | 155 | `tests/tooling/_record_subset.py`: the questions they name, the entries those cite, the record's own files |
| test_bundle_owed: 3 tests on the owed list | 1,414 each | 80 | the same, three questions |
| test_sources::test_the_import_command | 2,143 | 9 (none of the record) | a registry of its own |
| test_translation_owed::test_the_command_scopes_to_one_question | 1,411 | 10 (none of the record) | a record of its own, in a fresh repository |

Kept on the real tree, their subject being its data: every registry key has a state, the real match table parses, every
pointer resolves, every link in a live document resolves, the open-questions list of the real tree, the candidate list over the
real entry (rarity is measured against the whole record), the access tags' unreadable set, and the two whole-repository
equivalence tests (the content cache, the push checks in one process), which compare two code paths over every tracked file on
purpose. `test_lint_scope`'s root run re-runs only when a file is added or removed (it lists directories), and
`test_sources` now re-runs one test, not 43, on a page edit.

## R13 Amendment 6 - what subagents write fresh, and why

(observed 2026-10-17; method: every subagent transcript since 2026-10-10 under `~/.claude/projects/-diagram/*/subagents/`,
1,312 runs, typed by their `.meta.json`; per call, the usage's `cache_read_input_tokens` and `cache_creation_input_tokens`;
"back to back" = a dispatch of the same type from the same session under 5 minutes after the one before, the cache's lifetime
for subagents - their writes are all `ephemeral_5m`; spend in base-input units at the 5-minute tier's rates, a write 1.25,
a read 0.1, output 5; the scripts become `make cache-audit`)

| (observed 2026-10-17; the method above) | back-to-back pairs | first call read from cache | first call written fresh |
|---|---|---|---|
| modal-depiction | 169 | 4,138 | 2,676 |
| impl-drift | 83 | 5,959 | 2,317 |
| spec-fidelity (keeps CLAUDE.md) | 72 | 8,181 | 25,829 |
| general-purpose (ad hoc) | 42 | 20,492 | 29,191 |
| record-format | 17 | 8,312 | 3,132 |

- A defined agent's file is its system prompt and is read from cache by the next dispatch of its type; what it writes fresh,
  ~2.5-3.5k tokens, is the prompt and the harness's environment block.
- spec-fidelity and the ad-hoc agents carry the instruction files (CLAUDE.md, the nested ones, the memory index), and that
  ~22-25k is written fresh even back to back: it is not in the cached prefix.
- (observed 2026-10-17; the method above) Of all subagent spend since 2026-10-10 (~131M base-input units: 68.7M written, 398M read, 1.04M output), spec-fidelity's
  instruction files are about 12% (written fresh at 309 dispatches and carried through ~10 calls each), the ad-hoc agents'
  about 3.5% (120 runs; 98 of them the claims and modal triage).
- The modal checks' manifests (223, 61 and 55 read) repeat 15-17k characters in at least 80% of them - `dev/modals.md`, the
  guidelines, copied into every bundle after the unique prompt: about 1.3%. No other check's manifests repeat more than a few
  lines; impl-drift's runs re-read the same drawing pages, but those follow the unit, not the check.

