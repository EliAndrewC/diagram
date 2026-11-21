# Tasks - feature 451, where the time goes, and the six cheap fixes

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

**Input**: `plan.md` (D1-D17 and each task's section), `research.md` (R1-R12), `data-model.md`, `contracts/refusals.md`, `spec.md`.

Every task is tooling, so every task is `research: rendering`. Each builder task is one guard or one reader, so no builder's context
grows large (the feature's own lesson, User Story 2). A task whose files include a HELD file (research R11: `rust/guard/src/**` but its
tests, `scripts/hooks/*.sh`, the root `Makefile`) says so; its builder runs `make guard-edit FILE=<file> WHY="<reason>"` for each
before the first edit. Every task writes prose or code: American spellings, hyphens only. Each refusal's test is written first and
seen red, then the check deleted and the test seen red again (FR-012).

## Occasions

- none: tooling only - no map feature, sheet, glyph, placement rule or research page changes.

## Dependencies

- T01 before any tick (the plan gate).
- T02 first of the data: every later task reads its detector. T03 next: T07, T08 and T14 read its table and `task` field. T04 before
  T05, T06 (`append_row`) and T09 (`BgEnd`).
- T08 after T02-T07; T09 after T08; T10 after T09; T11 after T10.
- T12 before T13 (one guard). T13 and T14 after T03 (the line's `task`) and T06 (the landing's `end` line naming its tasks, D5), T14
  after T02. T15 before T16 (one file). T17, T18, T19 independent of each other.
- T20 before T21 (the shard form). T22 last.

The order, the GM 2026-11-20 (request.md: "let's prioritize those remaining improvement fixes"): the refusals and the split (T12-T21) before the rest of the data and the readers (T07-T11), since they make the work after them faster; T06, in flight, lands first (T13 and T14 read its `end` line). Lanes: T18 then T14; T15, T16, then T12, T13; then T17, T19, T20, T21; then T07-T11; then T22. Parallel lanes, where two builders are run at once: T05 beside T06
(different crates); T17, T18 and T19 beside each other; T21's two suites beside each other. Two builders never edit one held file at
once.

## Implementation strategy

The refusals and the split first (T12-T21, with T28 after T18), the GM 2026-11-20: performance work before other work, since it
makes the work after it faster. Then the rest of the data and the readers (T07-T11: the retrospective as one command), each refusal
landing on its own, each small; T22 last.

## Tasks

### The plan review

### The event-log data (FR-001 to FR-004)

### The readers (FR-005)

### The refusals (FR-006 to FR-009, FR-011), each red first (FR-012)

### The hook-suite split (FR-010)

### The close

- [ ] T22 [perf] The close: on the first full day of work after T02-T21 land, SC-001 (`make where-time F= SINCE= UNTIL=`, unexplained waiting under a tenth), SC-002 (the day's per-task table from the log against a hand join of the transcripts, each bucket within a tenth), SC-005 (static runs per task, builders' largest contexts, every escape listed), `docs/guards.md`'s knob table complete (D14), then `make feature-report F=451 WRITE=1` (SC-001, SC-002, SC-003, SC-005); and CONTEXT_CAP_TOKENS retuned on the day's per-call speed by context: on 2026-11-20 builders reached their first edit at a median 162k of context (90th percentile 254k, 5 of 99 past 300k) and peaked at a median 498k (99 of 114 past 300k), measured 2026-11-20 (the session's subagent transcripts, the last usage before each builder's first Edit or Write, and its largest) - so at 300k most tasks hand off once; the first real firing stopped T13's builder before any edit; and the plan template's `Performance work?` placeholder (rust/gate/crates/plan/src/plan/template.rs) names FR-013's measurement clause beside its speed clause (T08's blocks review, 2026-11-21); and T55's after-measurement: the closing tail's idle minutes on the tasks after T55 lands, how often its order notice fired and was followed (the guard log's `noticed` rows), and how often its foreground refusal fired and was escaped (its `blocked` and `escaped` rows, T55's item 9)
      research: rendering
      verify: `report.md` holds the three measurements against their bars; a missed bar names its number and the knob it retunes; `make quick`
- [ ] T49 gate_write_hooks lets through a write into the tree made through a function of the program's own (found by T33's after8 gate replay, 2026-11-20): window#170's `replace_note("citations/urban-features.html", ...)`, whose function writes `R / path` with `R = Path("research")`, and window#172's `sub(<the urban-features record page>, ...)`, writing `Path(f)`, run unread under a running gate, as at HEAD - place such a literal by reading the function's body (which parameter reaches the write, onto what base; a base the program computes fails open, so window#72 stays let through), red first on #170 and #172's shapes, the replay's moves accounted
      research: rendering
- [ ] T51 A program run from a script file (python3 $S/x.py) is not read by make-only's guard-write or the gate's shell-write check (found by T33, 2026-11-20): of the replay's 1,134 rows, 41 scratch scripts whose source a heredoc in the corpora wrote, run through make-only's reader as -c programs, give 5 refusals - window#215's desc195.py rewriting a clone's Makefile, a real guard-file write the guard let through, and 4 false (window#302, #305, #306, #309 read or run house-style-hooks.sh) - and 7 rewrite a clone's research page, test or Makefile the gate would see; measured first - read the script file's text at the call, replayed over the corpora with the 4 false shapes as the let-through baseline - and fixed red first where a move is a correction
      research: rendering
- [ ] T52 The make-call readers that skip shared::make (the 451 T02 class, counted by 451 T36): 10 readers of command text keep their own reading of a make call, measured 2026-11-20 (a grep of rust/, scripts/ and the Makefile, and of rust/ at HEAD for make literals outside tests, process-table, log-field and prose readers and batching_hooks NOT_RECON set apart) - shared/checks/rounds.rs APPLY (make apply-edits FROM=), ledger_hooks appended (make append), claims_file_hooks VERB (make lines or append), make_only_hooks LANDING (land-tooling FILES, arbiter-fix-done LAND) and LABEL_TARGET, measure stepback_bundle/words.rs MAKES and measure_hooks has(make done), each reading a mention such as echo make append as a call; phase_source_hooks search.rs (make phase-read), shared/tree.rs (a segment headed by make) and gate_write_hooks head_of (a make segment left to the shared::make check), each past its own wrapper list, which skips timeout or flock - measured first, each reader against shared::make::invoked on the T02 red shapes and the T33 replay corpus, and moved onto shared::make only where a real command gets a wrong verdict, red first on that shape; lands before T22
      research: rendering
- [ ] T80 The plan hold's write-back restores nothing for a task whose headings are split across the plan, yet reports written back (found by T78 reading the code, 2026-11-21: 51 of 898 task sections across specs/*/plan.md, none in 451's) - measured first by a scratch clone's split-heading section changed under a live hold, then the write-back restores each held block (plan_text.rs's section reading) and says what it restored, red first
      research: rendering
- [ ] T81 [perf] house_style_hooks' million-step timing test fails good work under load (found 2026-11-21 by T78's and T79's builders: its 20 s bound timed out at a load average of 82 while closing checks ran at once, the same crate's other tests green) - measured first how often it has gone red in the event log's Phase lines, then the test pins the step budget it exists to pin by counting steps, not wall time, or with a ceiling sized for a loaded host, red first on a slowed run
      research: rendering
- [ ] T82 The plan bundle's requirement reader reads only '- **FR-NNN**' and misses '**FR-NNN**' with no list dash (found by T48, 2026-11-21: 24 specs, features 129 to 271, write some so; a citation of one gets a NOT FOUND line though its text exists - 449's clause naming 239 the real case) - measured first which live plans cite such a requirement, then the reader takes both forms, red first on a dashless FR
      research: rendering
- [ ] T83 shared::tree's walk blanks a quoted word that holds a space or a shell character, and a file tool's destination is then read from the word before it (found by T79, 2026-11-21): through HEAD's main-tree, and T79's, `cp /tmp/a "/diagram/x y"`, `echo x > "/diagram/a b"` and `mv /tmp/a "/diagram/(x)"` are let through while `cp /tmp/a /diagram/x` is refused; 233 of T79's 59,116 broad-corpus commands end a cp, mv, tee or redirect on such a word, 11 of them naming /diagram, measured 2026-11-21 (`/tmp/t79/probes-q.jsonl` through `/tmp/t79/bin-head`, and a pattern count over `/tmp/t79/bx-all.jsonl`); measured first on a corpus, red first
      research: rendering
- [ ] T84 [perf] A builder stops short of ready-to-land and hands its last steps back (measured 2026-11-21 over the night's 29 tasks: 43 builders, about 16 'file this task' asks and every MODE 4 dispatch left to the session, each BLOCK answered by a fresh builder re-reading a handoff) - a builder files its own found defects (make task-add, measured first that two concurrent runs cannot take one number) and dispatches its own MODE 4 review and fixes its findings, its report ready to land; the builder brief carries it and a check refuses a builder report that names an unfiled defect or an undispatched review
      research: rendering
- [ ] T85 [perf] The Stop hook's run-still-going refusal fires on runs a still-running builder started (measured 2026-11-21: 24 of the main session's Stop refusals overnight, each an extra turn on its whole context, beside 45 interim 'waiting on its own work' notices) - finished_run_hooks skips a run whose starting agent is running by set_down_hooks' reading (T65), red first on a builder's background run
      research: rendering
- [ ] T86 [perf] A builder's closing checks go red on another builder's half-done files in the same clone (measured 2026-11-21: about 12 of the night's closing runs red only on another task's in-flight files, each a second make static under STATIC_OK or a verdict left owed, and ready tasks waiting on the slowest to land together) - make closing-checks judges the crates and files the caller's own task changed, another task's red reported apart and not counted, the landing's make done still the whole tree; red first on a clone with two tasks' work
      research: rendering
- [ ] T87 make-only refuses a guard file's name written in a scratch tree as a guard file written from the shell (found by T79, 2026-11-21): `guard_file_hooks::held` holds a path by its name alone (`/Makefile`, `/dev/work-budget.json`, ...), so `printf x > /tmp/q/Makefile` is refused through HEAD's make-only, and with T79's mktemp place `T=$(mktemp -d); ...; printf ... > $T/Makefile` (tx#953, ux#2204) and a copy of `dev/work-budget.json` into a `$(mktemp -d)` preview (ux#1106, ux#1107) are too - each a builder's scratch fixture, measured 2026-11-21 (`/tmp/t79/probes-mk.jsonl` through `/tmp/t79/bin-head` and `/tmp/t79/bin-r`, T79's replay); whether a copy outside the project's trees is held, measured first on the guard log's firings, red first
      research: rendering
- [ ] T88 [perf] Builders run three at once only 26% of the time because tasks are dispatched and landed in batches (measured 2026-11-21 over the night's 580 minutes from each agent's span: 3 builders 153 min, 2 141, 1 220, none 66 - a mean of 1.65; a batch's early builders sit done while the slowest holds the landing, T48 and T78 CLEAR for hours behind T79) - (a) a task lands on its own when ready, its gate run on HEAD plus its own commit apart from the clone's other unfinished work (the cost measured first: a cold detached checkout's make static took 2,321 s, so whether the clone's build cache serves it), after T86; (b) the Stop hook names the next independent open task when a builder slot frees (fewer than the knob's builders running and an open task touching no running task's files), so dispatch rolls; occupancy measured before and after
      research: rendering
- [ ] T89 py_c judges a `python3 -c` program that writes a place it computes from `sys.argv` where the shell stands (found by T79, 2026-11-21): `cd <mirror>/research/questions; python3 -c "...open(sys.argv[2],'w')..." a /tmp/q/a.txt` is refused through HEAD's main-tree and T79's, and with T79's loop reading three corpus commands that run one in a loop's body, each writing scratch, are refused (bx#54240, bx#58694, ux#2209), measured 2026-11-21 (`/tmp/t79b/judge/probe-mt.jsonl` through `/tmp/t79/bin-head` and `/tmp/t79/bin-r4`); the program's `sys.argv[N]` read as the command's N-th word, red first
      research: rendering
- [ ] T90 gate-write reads a target's command from its segment, which the walk cuts at 120 characters, so a `make` behind more than 120 characters of `VAR=value` prefixes is refused as a shell write of `.` under a running gate (found by T79, 2026-11-21): `L7R_FEATURE_DIRECTORY=... L7R_PAGE_SESSION=... L7R_CONTINUE=... make rust-test ...` through HEAD's gate-write and T79's (ux#1371, `/tmp/t79b/judge/probe-gw5.jsonl`), measured 2026-11-21; the command's head as its own field of the walk's target, red first
      research: rendering
- [ ] T91 T79's bind rule refuses two kinds of scratch write HEAD allowed (found by T79's second plan review, 2026-11-21): a name assigned twice in straight-line code is judged at each value, so D=/diagram/x; D=/tmp/y; touch $D/f standing in the mirror is refused though bash writes scratch; and past the 64-binding cap a name falls back to D6, so a loop over 65 or more literal scratch values is refused (63 pass) - a straight-line reassignment with no branch between reads its last value, and a loop past the cap is judged value by value rather than by D6, red first on both, a mirror value at either end still refused
      research: rendering
- [ ] T92 An arbiter's accept on one task's plan round records CLEAR for every changed block of the plan (found 2026-11-21: make arbiter-ruled on ask:451-T79-third-plan-round replied '28 plan block(s) recorded CLEAR', where the question was T79's section alone) - measured first which blocks that accept cleared and whether any held an unreviewed decision, then an accept with REVIEW=plan clears the blocks its question names, red first on a plan with a second task's changed block; and the reverse: an accept on one task's round does not stand as that task's verdict in the store the tick and push read, so T84's replay read T33, T46, T67 and T79 as BLOCKED though each had a round-arbiter accept (ask:451-T33-third-round, T46-fourth-round, T67- and T79-third-plan-round; specs/451-time-retro-and-efficiency/arbiter.jsonl) - an accept records the task's verdict as the arbiter's accept, red first; and T84's builder-stop guard reads the same store, so the fix covers it too (T84's plan review, 2026-11-21)
      research: rendering
- [ ] T93 [perf] The event log's Bash lines carry no write paths, so T86's closing checks cannot subtract another task's shell-written files (found by T86, 2026-11-21: Edit/Write lines named 127 of the 796 files the night's landings changed, T58 0 of 619, Bash writes leaving no path) - event_log_hooks writes each Bash call's write targets (shared::tree's walk, already computed by the guards) on its PostToolUse line, red first; T86's subtraction reads them
      research: rendering
- [ ] T94 The land crate's tests read the session's PLAN_REVIEW_OK and write the real guard log (found by T84, measured 2026-11-21 from the guard log's plan-gate rows naming the fixture feature 449-x)
      research: rendering
- [ ] T95 make closing-checks' BLOCKED tag misses a coverage red (found by T86's builder, 2026-11-21: blocked() in scripts/gates/closing-checks.sh reads only --> and Diff in lines, not cover's 'lines no test reaches', so a guard-crate cover red on another task's files went untagged) - blocked() reads cover's file lines too, and a coverage red whose every uncovered line is another task's file is tagged BLOCKED, red first in tests/hooks/test-closing-checks.sh
      research: rendering
