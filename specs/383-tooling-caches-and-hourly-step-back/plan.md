# Implementation Plan: tooling caches, one-process push checks, and the hourly step-back (feature 383)

**Spec**: `spec.md` | **Request**: `request.md` | **Builds on**: `scripts/record/record_cache.py` (feature 375 amendment 3:
`ParseCache`, `RevReader`, `cat_blobs`, `code_sha_of`), the glyph clock (`scripts/reviews/review_owed.py`, 375 amendments 9
and 10), the round arbiter (`scripts/hooks/lib/hm_arbiter.py`, `scripts/reviews/arbiter_bundle.py`,
`.claude/agents/round-arbiter.md`) and its tooling-fix items (feature 379).

## Summary

Phase 1 puts a content-keyed cache under the push's checks:
- a whole-check memo for the record and glossary build checks, whose inputs are a known set of trees;
- per-file facts for the four checks that read every tracked file;
- costed passes kept for the ledger check;
- one batched read of the base for the review lookup and for check-bundle;
- the review lookup taken out of the gate start and the turn's end;
- the old-layout check retired.

Phase 2 runs the push's Python checks in one interpreter and skips a self-test whose code already passed. Phase 3 makes the
glyph clock the feature's hourly checkpoint, owing every due review and a step-back ruling from the round arbiter, and holds
the next `make tick` until both are answered.

## Constitution Check

- I-V: N/A (no UI, no pool content, no SOURCE blocks).
- VI: no generator change. The one engine edit, the record splitter's quadratic comment test, changes no output.
- XII: N/A (no physical decision); every task is `research: rendering`.
- XIII: every check's output is compared with the cache on and off, and before and after the runner; the tooling tests,
  `make hooks-test` and the gate run green before each landing.
- XIV: fixed where found: the splitter's quadratic comment test (D2).
- XVI: built as asked. Where the plan reads a request it states the reading (D8, D11).

## Decisions

### Phase 1

**D1 - Two layers in one module.** `scripts/record/record_cache.py`, already the project's one cache module, gains:

- `content_ids(root, paths=None) -> dict[path, str]`: every tracked file's content id.
  - A clean file's id is its index blob id (`git ls-files -s -z`: 0.02 s over the repository, observed 2026-10-12; method: `time`, two runs).
  - A file the work tree changed (`git diff --name-only -z`) is hashed from its bytes, as is an untracked file a caller
    names.
  - Two git processes in all, never one per file.
- `FileFacts(root, name, *code)`: a `ParseCache` keyed per file by `(path, content id)`. Its file name carries `code_sha_of`
  over the extracting code, so a changed extractor starts empty (FR-001).
  - `facts(paths, extract) -> dict[path, value]` extracts only the misses. The content ids are listed for the directories
    the paths sit in, not the whole repository, for a check that reads one corner of it.
  - `fact(key_text, make)` keeps one value by the text it was made from: what an engine reader is handed as its memo (D2).
  - `facts_batch(paths, extract_many)` passes the misses together, for an extractor that is one subprocess over many files
    (ruff).
- `ResultMemo(root, name, inputs, *code)`: a check's whole answer, kept only for a run that PASSED.
  - The key is the content ids of every file under the declared input trees (tracked and untracked, `.gitignore`d excluded),
    plus the code sha and the Python version.
  - A hit replays the kept output and exits 0. A failing run is never kept, so a refusal is always computed afresh.

`L7R_CACHE_OFF=1` turns both off, as it does `ParseCache` today; it is the comparison every SC-002 test makes.

**D2 - The record and glossary build checks: a memo over what they read, a per-file memo under it, and the splitter fixed.**
- **The memo's inputs are what the build reads, measured (research R1):** `research/`, the engine's glossary assets
  (`l7r/diagram/interactive/assets/`), and the code sha of the module run and every project module it imports
  (`code_sha_of`). So an engine change outside the record's own modules - a 374 batch's placer, a pool generator - no longer
  re-runs it; only a change to the record, its assets or its code does. The inputs live once, as `memo_check.py`'s presets
  `record` and `glossary`, which both the Makefile's CHECK branches and the push's runner (D8) name.
- **A rebuild reuses each unchanged file's parse.** A miss runs the build IN the memo's process and hands the record store a
  `FileFacts` as its `MEMO` (`store.Memo`, a protocol with a no-op default, so every other caller keeps nothing). Every setup
  step that reads one file's text alone goes through it (research R4): a page's notes, the URLs of each registry entry and
  notes file (`archive.cited`, asked twice a build - the second is served from the memo), and each registry entry's item.
  The cross-file steps are named with their figures in R4: `page_html`'s cross-link pairs and confusables (now read once per
  build, not once per page), the questions' load, the archive's manifest rows (per file, but cheaper than keeping). Then the
  render, which reads the whole record's link index, registry and works for every page and so stays under the whole-check
  memo. Measured: cold 5.5 s, after one question's edit 4.9 s, replayed 0.15 s.
- **The splitter is fixed.** `split.headings` tested every heading against every comment (`any(...)`), quadratic; it now
  finds a heading's enclosing comment by bisection over the sorted comment starts, with the same answer (a test pins it on
  adjacent and edge-placed comments). Setup fell from 8.3 s to 2.7 s under the profiler (observed 2026-10-12; method:
  cProfile of one `record_asset --check`). Engine code: it lands by the gated route at the feature's close.

**D3 - The four whole-tree checks: per-file facts, resolved each run.**
- **research pointers.** The per-file fact is the list of candidate lines `(line_no, line, flags)`, taken after the SOURCE
  and quotation blanking, by the same filter as today.
  - `problems()` runs on the candidates against the current record each run. Questions and sections come and go; the file
    did not change.
  - The filter's `mapping.number` alternation is built from `research/moved-303.json`, so that file's content id is part of
    the extractor's key.
- **duplicate defs.** The per-file fact is the duplicates found.
- **function cap.** Two per-file facts: ruff's findings for the cap rule, from one ruff run over the misses only with the
  same config, and `suppression_problems`. `pyproject.toml`'s content id is in the key; the config-level check runs every
  time (one file).
- **conflict markers (`hm_conflict --tracked`).** The per-file fact is `has_conflict`. The exemption declarations are read as
  today.

Each check's command, arguments and output are unchanged. SC-002's tests run each check over a fixture repository and over
this one with `L7R_CACHE_OFF=1` and without, change one file, and assert a fresh extraction.
- **The rest of the push's checks, measured in one process (research R3).** Inside the runner (D8) the interpreter start is
  gone, so what is left of each is its own work. Over 0.1 s: file scale 0.16 s, partial citations 0.23 s, the Affects check
  0.18 s. Each was profiled:
  - **partial citations**: 5,400 small files read (the registry write-ups and the archive manifest rows). Kept per file, it
    took 0.33 s against 0.32 s: listing their content ids costs what reading them does. Not cached; recorded as tried.
  - **file scale**: a directory census (0.08 s) and a line count of each `.py` (0.06 s). The line count is the only per-file
    part, and its listing would cost most of it. Not cached.
  - **the Affects check** (`speckit-todo.py --check`) read every feature twice, once per question it asks. It now reads them
    once and hands the list to both: 0.25 s to 0.15 s.

**D4 - The ledger check costs a pass once (FR-002).**
- `settled()` keeps each costed pass's cells in `<git common dir>/l7r-cache/ledger-settled.json`, keyed by
  `(agent, segment)`. Beside the cells it keeps the transcript's path, size and mtime.
- A kept pass is served while its transcript's size and mtime are unchanged: a resumed agent appends, which changes both,
  and a finished one never does.
- A pass not yet kept is the only one whose transcript is looked up. The lookup is one listing of
  `*/*/subagents/agent-*.jsonl` made at most once per run, not a glob per pass.
- So a run where every pass is already costed reads no transcript. The answers are unchanged: the same `settled` result is
  fed to `distinct` and `unanswered`. The ledger hook's commit-time call benefits without change.

**D5 - The review lookup: asked where it matters, read once (FR-003).**
- **The reads.** `_at_base` and `_existed` go through one `RevReader` over the pool trees at the base: one `ls-tree` and one
  `cat-file --batch`, in place of a `git show` per manifest and an `ls-tree` per folder. A feature's `tasks.md` at the base,
  asked up to six times a lookup, is read once per run.
- **The callers.**
  - `pair-hooks.sh`'s gate-start branch no longer asks it: the gate runs as typed.
  - The stop branch's "a turn may not end on a green gate with reviews owed" is retired.
  - A review dispatch still asks (the guard refuses a dispatch nothing owes, and an early glyph-check).
  - `make verify` asks on request. `review-gate.sh` asks at the push. The checkpoint asks on the hour (D10).
- **The snapshot.** The reviewer's snapshot and per-unit prompt files the gate-start branch wrote (by rewriting `make done`
  into `make verify`, or by taking the snapshot itself) are written by `make verify`, unchanged, which the checkpoint's hold
  (D13) and the push's refusal name: a review comes due at the hour or the landing, and `make verify` is the gate plus the
  units it owes. A plain `make done` runs as typed.
- **The suite.** `tests/hooks/test-pair-hooks.sh` asserts the lookup is not run at gate start or at a turn's end (the
  script's own trace marker), and that the push and the checkpoint still refuse what is owed.

**D6 - check-bundle reads the base once and runs its helpers in-process (FR-004).**
- The base revision's files come through a `RevReader` kept in a `ParseCache` under the revision id: a bundle built twice
  over one base reads the base from the cache.
- `run_script` imports the helper (`record_prepass`, `quote_verbatim`, `style_prepass`, `translation_owed`, `source_pages`)
  and calls its `main(argv)` with its output captured and the working directory set, in place of a new interpreter.
  `source_pages` imports only the standard library and carries its own fetch timeout, so nothing needs a process of its own.
- The revision's record files (`record_owed.read_at`) are kept by the commit and the names read (`rev-files`, two revisions'
  worth at most): a commit never changes, and one bundle read the base's record three times.
- The bundle's files are compared byte for byte with today's (SC-005).

**D7 - The old-layout check is retired (FR-005).** Removed:
- `scripts/gates/check-old-layout.py`;
- its calls in `scripts/sync-with-main.sh` and in the Makefile's `static`;
- its tests;
- its mentions in `scripts/CLAUDE.md`, `docs/guards.md` and `docs/efficiency-tooling.md`;
- the `_moves.py` table only it reads, if nothing else reads it (measured in the task).

Specs and logs keep their words (the house rule for history).

### Phase 2

**D8 - One runner (FR-006).** `scripts/gates/push_checks.py <root> [--skip <name>...]`:
- **The table.** One row per check: name, script, argv, the refusal line `sync-with-main.sh` printed, whether it is a
  self-test, and a path it needs (the record and glossary rows need `research/sources`, as the shell's `if [ -d ... ]` did).
  Every Python check of the old block is a row, in its order: duplicate defs, file scale, stale dirs, the function cap, the
  ledger, entry headings, research pointers, partial citations, the download list, spec-lint, the Affects check, conflict
  markers, the record and glossary builds (`memo_check.py record|glossary`, the presets of D2), the green-gate stamp and
  the closing check.
- **How a check runs.** Each runs through `runpy.run_path(script, run_name="__main__")` with `sys.argv` set, catching
  `SystemExit`: the same code path as `python3 script args`. `sys.path`, `sys.argv` and the working directory are restored
  after each; a self-test's stdout is dropped, as the shell's `>/dev/null` did.
- **Failure.** The first failing check prints its refusal line (`sync-with-main: ...`) and the runner exits 1, as `die` did.
- **The escapes stay in the shell**, logged as before: `LEDGER_ROWS_OK` passes `--skip ledger-owed`, `GATE_STAMP_OK` passes
  `--skip "gate-stamp selftest" --skip gate-stamp`.
- **The closing check** (`close_check.py --push origin/main...HEAD`) is a row too, after gate-stamp: a pass or a refusal with
  an escape - `CLOSE_OK` passes `--skip closing` - and its refusal is logged to the guard log as the shell logged it.
- **Every other Python process `push_cmd` starts, and why it stays one** (said at the call): the shell gates
  (`entry-gate.sh`, `claims-gate.sh`, `review-gate.sh`, `plan-gate.sh`) are shell scripts, not Python checks. After the
  fetch, the feature pointer read (`python3 -c`), `speckit-todo.py --holding` and `--closed-by-status`,
  `make perf-review`, `make ci-status` and `make ci-merge` each produce a VALUE the shell's own branches read - which
  features are in progress, the performance flag, the remote route - not a pass or a refusal
  to fold into the runner, and they run after the fetch the checks precede. `hm_escape.py reason-ok` runs only when an
  escape is set. `make render-sync` runs on main after the landing, not as a check.
- **Proof (SC-006).** A test runs every check alone and in the runner, on this tree and on fixture trees seeded to fail
  each, comparing output and exit. A second test keeps a self-test as passed, changes a module its check imports, and sees the
  self-test run again.

The GM's "the 35 separate Python startups" is read as the push's checks, which is where they were counted.

**D9 - A self-test runs once per version of its code (FR-007).** The runner keeps `<git common dir>/l7r-cache/selftests.json`:
`{script: code_sha_of(script)}` for each self-test that passed. One whose code sha is kept is skipped; a failing one is never
kept. `L7R_CACHE_OFF=1` runs them all.

### Phase 3

**D10 - The checkpoint (FR-008).**
- `review_owed.py` gains `checkpoint(root, now) -> Checkpoint(due: bool, since: float, hour_no: int)`:
  - The feature's start is `feature_start` (first event or latest reopening, as today).
  - The last checkpoint is the clock's `checkpoint_at`, written when a step-back ruling is recorded.
  - Due when an hour (`GLYPH_HOUR_S`, renamed `CHECKPOINT_S` with the old name kept as an alias) has passed since the later
    of the two.
- Glyph-check's own due rule reads the same clock: its batch opens at the checkpoint. A feature with no event log, or under
  its hour, owes nothing.
- At the checkpoint, every owed review unit is due (`owed(root, checkpoint=True)`): the glyph units and, since D5, the
  others.

**D11 - The step-back is the round arbiter on an `hour` trigger (FR-009).**
- **The trigger.** `make step-back` records `hour:<feature>@<n>` (`hm_arbiter.trip`, kind `hour`) and builds its bundle with
  `scripts/reviews/stepback_bundle.py`, the way `make arbiter-ask` does for an ask.
- **The bundle** (`MANIFEST.md` plus files) is mechanical:
  - The hour's window: the last checkpoint, or the start, to now.
  - The session: the event log's `sid` gives the transcript, `~/.claude/projects/<project>/<sid>.jsonl`.
  - Where the time went: model time, tool time by normalized command (`make <target>` or the program), waits and subagent
    time. These are `scripts/measure/turn_time.py`'s and the hourly log's measures, made a module.
  - The dispatches and verdicts from the event log, and the guard refusals from the guard log.
  - The task in progress (`make task-start`'s record) and the feature's open boxes.
  - The session's own words in the hour: its assistant text, each command it ran (no tool output), and the numbers it
    edited, capped at about 40k characters, newest kept.
- **The contract.** `.claude/agents/round-arbiter.md` gains an "An hour trigger" section with the four questions of FR-009
  and its rulings:
  - `continue`: nothing to change;
  - `change-route`: a binding `what`, naming the loop or the unresearched number and the route to take, Room before packing
    first;
  - plus the optional `tooling_fix` and `for_gm` fields.
- **For a replay** (SC-008), the bundle builder takes `--transcript`, `--since` and `--until`.

The GM's "hourly arbiter" is read as this agent: it judges the process from outside, and its rulings already bind and reach
the GM's review.

**D12 - What a ruling does (FR-010).** `record_ruling` for an `hour` trigger:
- writes `checkpoint_at` (D10);
- a `change-route` ruling is binding as any ruling is, and its `what` goes on the GM's review;
- a `tooling_fix` opens a 379 item (tick and close held until `arbiter-fix-done`/`-declined`);
- a `for_gm` adds a GM-review row;
- a `continue` with neither field adds no GM-review row (the one exception to "the GM reviews every ruling", stated in the
  contract).

**D13 - The hold (FR-011).**
- `scripts/tick-task.py` asks `checkpoint(root)`. While it is due, it refuses unless both hold:
  - an `hour` ruling is recorded for this hour;
  - every review unit due at the checkpoint has been dispatched since the checkpoint opened (the pair state's `dispatched`).
- The refusal names `make step-back` and the owed units' dispatch commands.
- There is no escape. The hold is "not optional" (FR-011), and the session in a loop is the one the step-back exists to
  catch; the 379 tooling-fix hold it sits beside has none either.
- A feature under an hour, or with no event log, is never held.

**D14 - The manual check retires (FR-012).** After phase 3 lands, this session deletes its hourly cron job and says so in
the closing report.

## Research

- **R1 (D2): the record check's inputs.** Measured with an audit hook on `open` during one `record_asset --check`. The
  trees read are recorded in `research.md` with the run. If any input lies outside `research/` and `l7r/`, it is added to
  the memo's inputs.
- **R3: the rest of the checks, and the record's rebuild.** Each push check timed inside one process (D3), and the record
  check's cold, edited and replayed runs (D2), recorded in `research.md`.
- **R2: the baseline.** `scripts/measure/push_check_times.py`, two runs each, the second kept, recorded in
  `measurements.json`.

## Phases and landing

Each phase lands its tooling with `make land-tooling` once its tasks are ticked, so other sessions get the faster push while
the feature runs. D2's splitter fix is engine code and lands with the feature's close by the gated route.

## Amendment 1 (FR-013, FR-014)

**D15 - A tooling test file's reads, recorded (FR-013).** `tests/tooling/_test_deps.py`, a pytest plugin `make test-file`
loads (`-p`), with `L7R_TEST_DEPS=record` its default:
- in each test worker an audit hook notes, for the tooling test file running, every file opened for reading and every
  directory listed under the repository; a compiled module read (`__pycache__/*.pyc`) stands for its source;
- every Python process a test starts imports `tests/tooling/_deps_site/sitecustomize.py` (on PYTHONPATH; it runs the system's
  own sitecustomize first) and notes its reads the same way, each written as first seen, never only at exit;
- a program that is not a recording Python process marks the file `opaque` unless its working directory (and any `-C`) is
  outside the repository and no argument names a path inside it (the plan review: `git worktree add /tmp/x HEAD` run in the
  repository names an outside path and reads the repository). Three exceptions read nothing of the repository's content:
  `git init <dir>` and `git clone <src> <dst>` (judged by the paths they name), `git rev-parse` asking only where the
  repository is (`--show-toplevel`, `--git-common-dir` and their kind), and `sleep`, `true`, `false`, `echo`. A Python child
  run isolated or with the recording dropped from its environment is opaque;
- when every test of a file ran and passed - none of them deselected, by `-k`, a marker or a reuse (checked from pytest's
  deselections, so the gate's `-m tooling` run counts only where it really ran whole files), and no node id named - its
  reads are kept by content in
  `<git common dir>/l7r-cache/tooling-test-passes.json`: a file by its git blob id (`record_cache.content_ids`, a changed file
  hashed as git would, so the same bytes match in a clone and its worktree), a directory by its entries (tracked and
  untracked, the ignored aside), the interpreter's version beside them. Reads of the content caches (`.git/l7r-cache/`) are
  left out: every entry there is keyed by what it holds. A failure removes the file's entry.

**D16 - Reused by `make land-tooling` alone (FR-013).** `land-tooling.sh` runs its checks with `L7R_TEST_DEPS=reuse`, the one
switch, and nothing else sets it; a reuse run records what it ran, as the gate's tooling run (`-m tooling`, which selects whole
files) and `make test-file` record, so the clone usually has passes to reuse. A kept file is deselected where the interpreter matches, nothing was opaque, nothing it read
is a file git ignores, and every file and directory reads the same now; the run prints how many files and tests it reused.
The guard suites keep their own reuse (`make hooks-test`). Measured on this clone's commit, in a fresh worktree, by
`scripts/measure/tooling_reuse_time.py`: `m:land-tooling-tests-reuse`, 27.58 s with reuse (606 tests ran) against 36.21 s
without (1,796); 88 of 126 test files reusable.

**D17 - quote-verbatim's verdicts (FR-014).** `verdict(passage, page)` is kept in a `ParseCache` named by the module's code
sha (`quote-verdicts-<sha>.pickle`), keyed by the passage and the page text's sha256; `main` opens it and saves it. The
report is compared byte for byte with `L7R_CACHE_OFF=1`.

## Amendment 2 (FR-015 to FR-020)

**D18 - A git question kept with its answer (FR-015).** The child rule moves to one standard-library module both recorders
import, `tests/tooling/_deps_site/l7r_dep_rules.py` (`judge`), so the test's process and its Python children judge alike. A
`git` started against the repository whose subcommand is read-only (`ls-files`, `ls-tree`, `show`, `diff`, `log`, `rev-parse`,
`merge-base`, `cat-file`, `status`, `rev-list`, `diff-tree`, `diff-index`, `for-each-ref`, `show-ref`, `grep`, `blame`,
`describe`, `name-rev`, `check-ignore`, `hash-object` without `-w`), that reads no standard input (`--stdin`, `--batch`) and
writes no file (`--output`, `blame --contents`), and that no location variable steers (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, the object
and common directories, `GIT_NAMESPACE`) is a QUESTION: its working directory and arguments, the repository's path written
`{ROOT}`. When a pass is kept, each question is asked once in the clone under `GIT_OPTIONAL_LOCKS=0` (so a `status` leaves the index alone) and the digest of its
answer kept (exit status,
output and errors, the path written `{ROOT}`); at reuse each is asked again in the worktree, once however many files asked it,
and the file is reused only where every answer is the same. Every other git command against the repository is opaque, as
before. The answer is taken at the end of the run, not as the test saw it: the tests do not write the repository (a write
there is a git command, opaque, or a file opened for writing) - measured: `git status --porcelain --ignored` of the clone is the
same before and after a whole tooling run (research R9).

**D19 - A Python child adopted (FR-016).** `subprocess.Popen`'s audit event carries the environment the test passes, before
the child starts; a Python child given its own environment has the recording's three variables and the shim's PYTHONPATH put
into that environment in place (`l7r_dep_rules.adopt`), so it records itself. One started with `-I`, `-E` or `-S` ignores
them and stays opaque (0 of 126 files, research R8). An `os.open` by a relative name (`shutil.rmtree` working under a
directory handle) is not a read of the repository: it was what made four files look as if they read `.git`.

**D20 - The ignored reads made known (FR-020).** Two reads under `.git` are content caches, keyed by what they hold, and join
`CACHE_READS`: the gate stamp's `semantic-id-cache.json` and the translation pairs' `ParseCache`. The tooling tests run under
one fixed `SPECIFY_FEATURE` (`tests/tooling/conftest.py`), so no test reads the clone's own `.specify/feature.json`.
`test_makefile_recipe_comments` checks the tracked Makefiles (`git ls-files`) - it also read the stale agent worktrees'
Makefiles under `.claude/worktrees/`, which are no part of the repository. Each remaining cause is then looked at in turn and
either replayed as D18 does git (a program that only reads and prints) or recorded in research R9 with its test-seconds and
why it cannot be.

**D21 - Each step timed (FR-017).** `land-tooling.sh`'s `step <name>` writes `land-tooling: step <name> <s> s` to its log and,
at the end, one JSON line per landing to `<git dir>/land-tooling-steps.jsonl` (outcome, load, steps): prepare (fetch, merge
base, the patch), worktree, patch (applied and committed), guard-suites (`make hooks-test`), tooling-tests (the tooling run
and any test file landed outside it), push - the two checks each their own step (the plan review: one figure cannot show
where the time goes), before D22 and after it. It lands first and alone, so the next landing is the
before of SC-013.

**D22 - A landing runs each test once, its two checks side by side (FR-018).** `make hooks-test` takes `HOOKS_PYTEST_SKIP=<path
prefix>`: its scripts' pytest phase leaves out the files under it. `land-tooling.sh` passes `tests/tooling/`, because its
tooling run covers that whole tree with reuse; so a tooling file runs at most once, in the run that can reuse it. The guard
suites and the tooling tests run as two background jobs, each to its own log, joined before the push; both must pass, and
both logs are kept in the landing's log with each job's seconds. They share no write: the pass store is written by the
tooling run alone (the hooks-test pytest phase in a landing holds only the files outside `tests/tooling/`, which the plugin
does not track), the guard suites' stamps by the guard suites. `make hooks-test`'s pytest phase loads the plugin too, so a
clone's own `make hooks-test` records passes a landing can reuse.

**D23 - What the after-measurement shows (FR-019).** After D18-D22, a landing is measured (SC-013) and each step over a few
seconds is looked at; a cut that loosens no check is made in this amendment, the rest recorded in research R9 with its
seconds.

## Amendment 3 (FR-021 to FR-024)

**D24 - The Sonnet 5.5 trials, first (FR-024).** Feature 251's seeded-run method (`specs/251-tiered-subagent-checks/
measure/seeded.py`, research R5) becomes a maintained tool, `scripts/measure/model_trial.py`: `catalog <agent>` lists the
recorded runs of a check from the session transcripts, joined to their ledger rows; `prepare <transcript> <out>` builds a
detached worktree at the last commit before the recorded run, copies the current agent files in with the tested model
written into that copy's frontmatter (`model: claude-sonnet-5-5`, the worktree's copy only), and rewrites the prompt's paths;
`run <out> [--runs 3]` starts each headless session in the worktree (`claude -p --agent <name>`, hooks off: research R4) in
the background; `usage` folds each run's turns and tokens. A recorded run whose prompt names a bundle outside the repository
(`/tmp/l7r-check/...`) is prepared only if the bundle still exists or the tool that built it can build it again at that
commit; otherwise the case is not chosen.
- **Cases**, per check: one recorded Opus run with findings the session then acted on (its ledger row says `fixed`, so the
  findings were real), and one recorded clean run (no finding, not overturned later). Seven checks, two cases, three Sonnet
  runs a case: 42 runs.
- **Scoring**, by the session against the recorded reply, case by case, written to research R10: each known finding HIT or
  MISSED per run; on the clean case, each new finding a FALSE ALARM unless checked and found real; turns, input and output
  tokens and wall time against the recorded run's.
- **The rule** (the doctrine of feature 251): a check moves to Sonnet only when all three runs of its findings case hit every
  known finding and no run of its clean case raises a false alarm; else it stays on Opus. The tier table
  (`tests/test_agent_models.py`), the agent file, `docs/spec-kit-and-reviews.md` (a section "Models tried", one row per check:
  what was tried, when, the result, where recorded) and a pointer from `CLAUDE.md`'s review paragraph to that section carry the
  result, either way.
- **Order**: T24 (the tool and the cases) and T25 (the runs and the scoring) are the amendment's first tasks; the runs go to
  the background and T26 onward proceed beside them.

**D25 - Not importing what will not run (FR-022).** Each runner decides before collection where it can: the tooling plugin
answers `pytest_ignore_collect` for every file its reuse skips (the decision moves from `pytest_collection_modifyitems` to
`pytest_configure`, made once per process from the same store), so a reused file is never imported, in any worker. testmon
already ignores the files it deselects; why `make quick` still spends its time collecting (14.3 s with no test to run,
observed 2026-10-17, method: `make quick` on an unchanged tree, load 3) is measured first with
`scripts/measure/collect_cost.py` (pytest's own collection time, per worker, with and without xdist, with `-X importtime`), and
the cut follows what it finds - the worker start, a conftest's imports, or testmon's own database read. The tests that run and
their results are compared with the cut off and on (SC-016).

**D26 - What every other program reads, recorded by the C library (FR-021).** A system trace cannot be taken here: `strace`
is refused in the container (no ptrace capability, with or without sudo; observed 2026-10-17, method: `strace -f -e
trace=openat true`). But every program the 18 files start - bash, make, node, resvg, pdftotext, grep, ruff - is linked
dynamically to the C library (observed 2026-10-17, method: `ldd` on each), so a recorder PRELOADED into it sees what it opens:
- `tests/tooling/_deps_site/l7r_file_log.c`, built by the plugin with `gcc -shared` into the git common directory's cache when
  absent or older than its source, wraps the C library's ways in to a path - `open`, `open64`, `openat`, `openat64`,
  `__open_2`, `__open64_2`, `__openat_2`, `__openat64_2`, `fopen`, `fopen64`, `stat`, `lstat`, `fstatat`, `statx`, `access`,
  `faccessat`, `opendir`, `readlink`, `readlinkat`, `execve`, and `syscall` for `openat`/`statx` called by number (libuv's way
  for node) - and writes each path under the repository, as Python's recorder does, to the same per-test log
  (`<test file>\t<kind>\t<path>`): opened for reading as `file`, a directory opened or listed as `dir`, a stat or access as
  `file` (its content, or `absent`). A path opened by a directory handle is resolved through `/proc/self/fd`.
- Every child a test starts gets `LD_PRELOAD` (and the log's variables) in its environment - the inherited one, or the one the
  test gives it, put there in place as D19 adopts a Python child - so a program and everything it starts is recorded. A child
  that is a git question stays a question (D18); a child whose environment drops `LD_PRELOAD` before it runs, a statically
  linked program, or one run where the recorder could not be built stays unknown, and its file runs.
- The recorder is VALIDATED before any file is reused on it: on the whole tooling run, every Python child carries both
  recorders, and for each, every file Python's audit hook saw opened must be in what the preloaded recorder saw (a test fails
  on any gap, and the gap is the bug). A file whose reads are still unknown after this is recorded in research R10 with its
  seconds and the measured reason.

**D27 - The guard suites by what their cases read, and the slow one by its long case (FR-023).** Measured first (2026-10-17;
method: `hookdeps.py --deps` for each of the 44 suites, `git log` of each input since 2026-10-03, each suite and each
sync-with-main case timed alone):
- the inputs most suites share - `guardlog.sh`, `hm_escape.py`, `hm_shape.py`, `writer-alive.sh`, each an input of 42 suites -
  changed once or twice each in two weeks, so narrowing them saves little; they are left whole, and nothing a suite checks is
  dropped. The suite that re-runs is the one whose own script moved: `sync-with-main.sh` changed in 27 commits, and its suite
  is the slowest (36.2 s at 4 parts);
- its long pole is ONE case, `case_11` (27.9 s alone, 17 pushes in a row across three fixtures): it is split into three cases,
  each on its own fixture, the case weights are set to today's measured seconds, and the parts go 4 -> 8. Every check still
  runs and is counted (124);
- `review-gate` (21.8 s) and `entry-gate` (19.8 s) run their gate a dozen times in sequence against one clone each; parallel
  parts would need a clone each (2 s) and run only when those gates move - recorded, not split;
- `make hooks-test` prints which suites ran and each one's seconds, longest first, so a landing's log says where its guard
  time went (`tests/hooks/hookrun.sh` times each suite).