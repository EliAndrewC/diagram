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
- [ ] T48 The bundle reads ids inside a clause naming another feature as the reviewed feature's (the round arbiter on ask:451-T46-fourth-round, accept, 2026-11-20): '<ids> in N's' / '<ids> of feature N' fall to the reviewed feature's bare reading; measured first - how often such a clause names a feature other than the reviewed one across specs/*/plan.md and plan-done.md - and fixed (read as N's, carried or named NOT FOUND, red first) only if a real one hands a reviewer the wrong text
      research: rendering
- [ ] T49 gate_write_hooks lets through a write into the tree made through a function of the program's own (found by T33's after8 gate replay, 2026-11-20): window#170's `replace_note("citations/urban-features.html", ...)`, whose function writes `R / path` with `R = Path("research")`, and window#172's `sub(<the urban-features record page>, ...)`, writing `Path(f)`, run unread under a running gate, as at HEAD - place such a literal by reading the function's body (which parameter reaches the write, onto what base; a base the program computes fails open, so window#72 stays let through), red first on #170 and #172's shapes, the replay's moves accounted
      research: rendering
- [ ] T51 A program run from a script file (python3 $S/x.py) is not read by make-only's guard-write or the gate's shell-write check (found by T33, 2026-11-20): of the replay's 1,134 rows, 41 scratch scripts whose source a heredoc in the corpora wrote, run through make-only's reader as -c programs, give 5 refusals - window#215's desc195.py rewriting a clone's Makefile, a real guard-file write the guard let through, and 4 false (window#302, #305, #306, #309 read or run house-style-hooks.sh) - and 7 rewrite a clone's research page, test or Makefile the gate would see; measured first - read the script file's text at the call, replayed over the corpora with the 4 false shapes as the let-through baseline - and fixed red first where a move is a correction
      research: rendering
- [ ] T52 The make-call readers that skip shared::make (the 451 T02 class, counted by 451 T36): 10 readers of command text keep their own reading of a make call, measured 2026-11-20 (a grep of rust/, scripts/ and the Makefile, and of rust/ at HEAD for make literals outside tests, process-table, log-field and prose readers and batching_hooks NOT_RECON set apart) - shared/checks/rounds.rs APPLY (make apply-edits FROM=), ledger_hooks appended (make append), claims_file_hooks VERB (make lines or append), make_only_hooks LANDING (land-tooling FILES, arbiter-fix-done LAND) and LABEL_TARGET, measure stepback_bundle/words.rs MAKES and measure_hooks has(make done), each reading a mention such as echo make append as a call; phase_source_hooks search.rs (make phase-read), shared/tree.rs (a segment headed by make) and gate_write_hooks head_of (a make segment left to the shared::make check), each past its own wrapper list, which skips timeout or flock - measured first, each reader against shared::make::invoked on the T02 red shapes and the T33 replay corpus, and moved onto shared::make only where a real command gets a wrong verdict, red first on that shape; lands before T22
      research: rendering
- [ ] T78 The plan hold refuses a shell write that shares only template text with the held section (found by T77, 2026-11-21: 7 of 18 replayed Bash plan-hold refusals matched only text every section shares, such as the table rule or Found and left, all live holds and foreground calls - good work refused) - first checks_hooks restores held text on PostToolUseFailure as on PostToolUse (today a foreground write followed by a failing command is never restored, the pre-call refusal its only guard), red first; then planhold counts only text unique to the held section for a live hold and a foreground call, a pending hold or a background call still refused on shared text, red first on a template-only write
      research: rendering
- [ ] T79 shared::tree's walk splits a `\`-continued line and a `${VAR}`'s braces into segments of their own, and reads a `$(mktemp)` directory toward the mirror (found by T50, 2026-11-21): from /tmp, `D=<mirror>; cp /tmp/a ${D}/b` and `cp /tmp/a \` with `<mirror>/b` on the next line are let through by main-tree while `$D/b` and the one-line form are refused; `T=$(mktemp -d); cp /tmp/a $T/clone` standing in the mirror is refused (D6), a scratch write - every tool's write behind it, the twelve git subcommands failing open there since T50 (D-d, D-e); measured first on a corpus, red first; and an unresolved place is settled one way for every tool - after T50 an unresolved cp target is still read toward the mirror while an unresolved git place is not placed at all (T50's plan review, 2026-11-21)
      research: rendering
