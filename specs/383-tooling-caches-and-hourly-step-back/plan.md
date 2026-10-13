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
  - A clean file's id is its index blob id (`git ls-files -s -z`; measured at 0.02 s over the repository).
  - A file the work tree changed (`git diff --name-only -z`) is hashed from its bytes, as is an untracked file a caller
    names.
  - Two git processes in all, never one per file.
- `FileFacts(root, name, *code)`: a `ParseCache` keyed per file by `(path, content id)`. Its file name carries `code_sha_of`
  over the extracting code, so a changed extractor starts empty (FR-001).
  - `facts(paths, extract) -> dict[path, value]` extracts only the misses.
  - `facts_batch(paths, extract_many)` passes the misses together, for an extractor that is one subprocess over many files
    (ruff).
- `ResultMemo(root, name, inputs, *code)`: a check's whole answer, kept only for a run that PASSED.
  - The key is the content ids of every file under the declared input trees (tracked and untracked, `.gitignore`d excluded),
    plus the code sha and the Python version.
  - A hit replays the kept output and exits 0. A failing run is never kept, so a refusal is always computed afresh.

`L7R_CACHE_OFF=1` turns both off, as it does `ParseCache` today; it is the comparison every SC-002 test makes.

**D2 - The record and glossary build checks: a memo over their inputs, and the splitter fixed.**
- `make record CHECK=1` and `make glossary CHECK=1` run through `scripts/gates/memo_check.py <name> --inputs <trees> -- <command>`
  (the Makefile's CHECK branch). The inputs are measured, not guessed: the files the check opens, recorded by an audit hook
  during one run (research R1). The memo's inputs are those trees: `research/`, `l7r/`, `pyproject.toml`.
- Every push that does not touch them costs two git listings. One that does pays the build.
- The build itself gets faster too. `split.headings` tested every heading against every comment with `any(...)`: 11.7
  million comparisons, 5.5 s of the profiled 15 s. It now finds each heading's enclosing comment by bisection over the
  sorted comment starts, with the same answer (a test pins it on a page with nested and adjacent comments). This is engine
  code, so it lands by the gated route at the feature's close.

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
  `cat-file --batch`, in place of a `git show` per manifest and an `ls-tree` per folder. The `ls-files` for a moved folder
  reads the same listing.
- **The callers.**
  - `pair-hooks.sh`'s gate-start branch no longer asks it: the gate runs as typed.
  - The stop branch's "a turn may not end on a green gate with reviews owed" is retired.
  - A review dispatch still asks (the guard refuses a dispatch nothing owes, and an early glyph-check).
  - `make verify` asks on request. `review-gate.sh` asks at the push. The checkpoint asks on the hour (D10).
- **The snapshot.** The reviewer's snapshot the gate-start branch took is taken at dispatch, where the dispatch check
  already names the maps (`review_snapshot.py`, unchanged).
- **The suite.** `tests/hooks/test-pair-hooks.sh` asserts the lookup is not run at gate start or at a turn's end (the
  script's own trace marker), and that the push and the checkpoint still refuse what is owed.

**D6 - check-bundle reads the base once and runs its helpers in-process (FR-004).**
- The base revision's files come through a `RevReader` kept in a `ParseCache` under the revision id: a bundle built twice
  over one base reads the base from the cache.
- `run_script` imports the helper (`record_prepass`, `quote_verbatim`, `style_prepass`, `translation_owed`) and calls its
  `main(argv)` with its output captured, in place of a new interpreter; `source_pages.py`, which fetches over the network,
  stays a subprocess.
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
- **The table.** One row per check: name, script, argv, the refusal line `sync-with-main.sh` prints today. The table is the
  order `push_cmd` runs them in today.
- **How a check runs.** Each runs through `runpy.run_path(script, run_name="__main__")` with `sys.argv` set, catching
  `SystemExit`: the same code path as `python3 script args`. `sys.path`, `sys.dont_write_bytecode` and the working directory
  are restored after each.
- **The record and glossary checks.** Run as the memo's command (D2), in-process through `runpy.run_module`.
- **Failure.** The first failing check prints its refusal line and the runner exits 1, as the shell's `die` does.
- **In the shell.** `sync-with-main.sh` calls the runner once in place of the 24 lines; the escapes stay in the shell.
  `LEDGER_ROWS_OK` passes `--skip ledger-owed` after its log line.
- **Left as their own processes:** `entry-gate.sh`, `claims-gate.sh`, `review-gate.sh` and `plan-gate.sh`, which are shell
  scripts with their own refusals; `gate-stamp.py --check`, run under its own escape branch; and anything that runs `make`.
  Each says why at its call.
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
- `CHECKPOINT_OK="<reason>"` is the logged escape, as every hold has one.
- A feature under an hour, or with no event log, is never held.

**D14 - The manual check retires (FR-012).** After phase 3 lands, this session deletes its hourly cron job and says so in
the closing report.

## Research

- **R1 (D2): the record check's inputs.** Measured with an audit hook on `open` during one `record_asset --check`. The
  trees read are recorded in `research.md` with the run. If any input lies outside `research/` and `l7r/`, it is added to
  the memo's inputs.
- **R2: the baseline.** `scripts/measure/push_check_times.py`, two runs each, the second kept, recorded in
  `measurements.json`.

## Phases and landing

Each phase lands its tooling with `make land-tooling` once its tasks are ticked, so other sessions get the faster push while
the feature runs. D2's splitter fix is engine code and lands with the feature's close by the gated route.
