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
- [ ] T50 shared::tree's git_write reads 12 writing git subcommands as reads (found by T33, 2026-11-20): worktree, clone, init, switch, bisect, sparse-checkout, submodule, config, fetch, notes, update-ref, symbolic-ref - T33 added them and the replay of 1,134 commands caught no real write with them (only 2 false refusals, fixed) while a review found four misreadings (fetch -n is --no-tags; one value-option list for all twelve; config --global writes outside the repository), so T33 dropped them; measured first on a corpus that runs them in the mirror or a clone, each subcommand's options read from its own -h, added only where a move is a correction, red first; git stash list and show are reads since T33 (fixed there)
      research: rendering
- [ ] T51 A program run from a script file (python3 $S/x.py) is not read by make-only's guard-write or the gate's shell-write check (found by T33, 2026-11-20): of the replay's 1,134 rows, 41 scratch scripts whose source a heredoc in the corpora wrote, run through make-only's reader as -c programs, give 5 refusals - window#215's desc195.py rewriting a clone's Makefile, a real guard-file write the guard let through, and 4 false (window#302, #305, #306, #309 read or run house-style-hooks.sh) - and 7 rewrite a clone's research page, test or Makefile the gate would see; measured first - read the script file's text at the call, replayed over the corpora with the 4 false shapes as the let-through baseline - and fixed red first where a move is a correction
      research: rendering
- [ ] T52 The make-call readers that skip shared::make (the 451 T02 class, counted by 451 T36): 10 readers of command text keep their own reading of a make call, measured 2026-11-20 (a grep of rust/, scripts/ and the Makefile, and of rust/ at HEAD for make literals outside tests, process-table, log-field and prose readers and batching_hooks NOT_RECON set apart) - shared/checks/rounds.rs APPLY (make apply-edits FROM=), ledger_hooks appended (make append), claims_file_hooks VERB (make lines or append), make_only_hooks LANDING (land-tooling FILES, arbiter-fix-done LAND) and LABEL_TARGET, measure stepback_bundle/words.rs MAKES and measure_hooks has(make done), each reading a mention such as echo make append as a call; phase_source_hooks search.rs (make phase-read), shared/tree.rs (a segment headed by make) and gate_write_hooks head_of (a make segment left to the shared::make check), each past its own wrapper list, which skips timeout or flock - measured first, each reader against shared::make::invoked on the T02 red shapes and the T33 replay corpus, and moved onto shared::make only where a real command gets a wrong verdict, red first on that shape; lands before T22
      research: rendering
- [ ] T54 [perf] The stale-terms guard refuses a review on a common word (found 2026-11-20): an FR-013 amendment's spec review was refused with 66 candidates, every one the word 'end' in history (plan-done.md) and other tasks' sections the amendment did not touch - a refusal on correct work, which costs an escape each time; measured first (the candidates of recent refusals, how many named text the change made untrue), then the subject read from what the change moved, not a bare common word, red first on this case
      research: rendering
- [ ] T56 [perf] make events-refile leaves 23 lines in 385's log (found by T53, 2026-11-21): a 451 T47 builder's review agents, briefed with a task id and no feature, matched 385's T47 start of 2026-10-18 and were filed in 385's log; T53's writer now gives a start over 72 hours old no feature, but the refile (rust/gate/crates/measure event_log/refile.rs) still reads the old rule, so they stay - the refile shares the writer's rule (one reader, not a copy), a dry run shows the 23 moving, red first; then the real refile run once T53 and this land
      research: rendering
- [ ] T59 [perf] The guard's SubagentStop tok field is short (found by T10, 2026-11-21: short on 16 of the 17 stops that carry one, against the transcript's last messages) - the writer (rust/guard/src/guards/event_log_hooks/fields.rs) reads the tokens before the transcript's last messages are written; measured first which messages it misses, then the field matches the transcript's sum, red first; T10's reader already takes the transcript's sum first, so no report reads it wrong meanwhile; and a stop with no tok at all whose transcript has rows (262 of 279 stops carry none, T10's plan review, 2026-11-21) is measured too - absent since the field began is the same defect, before it is history
      research: rendering
- [ ] T60 The context cap names a builder's handoff under the call's working directory, so a builder whose shell was reset to /diagram writes it in the mirror's .git (found 2026-11-21: T10's handoff at /diagram/.git/l7r-handoffs/, the mirror being no workspace) - context_cap_hooks resolves the handoff directory from the session's clone (shared::session, as clone_sync_hooks routes an edit) rather than the cwd, red first on a call from /diagram
      research: rendering
- [ ] T61 [perf] The wait's proof-of-life check ends a live wait as gone (found by T55's builder, 2026-11-21: a wait on a log appended only between checks ended at 55 s with exit 3, saying the run was gone, while it ran) - measured first which of the waits the hook rewrites read a file that is quiet between checks, then the check asks the run's own process (the /proc walk finished_run_hooks uses) rather than the file's growth, red first on a quiet log over a live run
      research: rendering
- [ ] T63 [perf] The make-only guard refuses a read-only Python heredoc over the event log as a guard-file write (found by T58's builder, 2026-11-21: a script that only opened files for reading, run under the escape) - measured first which of the guard's refusals in its log were of read-only scripts, then a heredoc that opens no file for writing (no open(..., 'w'/'a'), no write_text, no shutil, no os.replace) passes, red first on the refused script's shape
      research: rendering
- [ ] T64 [perf] T55's order notice counts a code edit already landed (found 2026-11-21: the main session told at every make decide that its Makefile edit of 2026-11-20T15:48:51Z has no closing-checks after it, that edit landed hours before) - the notice reads the caller's last code edit since the task's last landing (static_runs_hooks' own landed rule), red first on an edit before a landing
      research: rendering
- [ ] T67 The README guard refuses a cp of a hook's source to /tmp (found by T58's builder, 2026-11-21: cp rust/guard/src/guards/readme_hooks.rs /tmp/... refused as a README write) - the guard reads the destination's name, not the source's, red first on that cp
      research: rendering
- [ ] T68 [perf] The context cap reads an advisor call's usage as the builder's context (found by T64's builder, 2026-11-21: a transcript row carrying an advisor call holds the advisor's iteration in message.usage, so l7r_shared context::usage_of read 297,622 on a context of about 148k) - measured first how many builder refusals since T12 followed an advisor row, then the cap reads the builder's own iteration alone, red first on an advisor row's shape
      research: rendering
