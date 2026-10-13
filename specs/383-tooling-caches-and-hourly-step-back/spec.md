# Feature 383: Tooling caches, one-process push checks, and the hourly step-back

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-12
**Status**: Done 2026-10-13 - spec FAITHFUL (round 3), plan CLEAR (round 3), every task ticked; push checks 19.87 s -> 1.92 s (research R6); tooling landed 0906d798a; the GM's review open (the first step-back's note)

**Affects**: tooling, review process

**Approved**: the GM, 2026-10-12, "Yes, please file it that way and then go ahead and work it start to finish. Thanks."

**Input**: `request.md` (the GM, 2026-10-12)

## Why

The hourly check of the backlog session (feature 374) measured what a landing's checks cost: about 24 s at every push, most
of it the same work done again - every tracked file parsed, scanned or read again although almost none changed since the
last push. Also every agent transcript ever logged searched for and re-read to cost a check pass whose ledger row was written
weeks ago, and a git process started per file where one would serve. Beyond the push:

- The ledger check also runs on every commit that stages the ledger.
- check-bundle runs before every record check.
- The review lookup runs at every gate start and every turn's end after a green gate.

The GM asked for a caching layer keyed by each file's content, for these tools fixed, the retired old-layout check removed,
the push's checks run in one process, and the hourly check this session has been doing by hand made something every
long-running feature does for itself, on the clock glyph-check already keeps.

## Requirements

### Phase 1 - the caches and the cheap fixes

- **FR-001 One content-keyed extraction cache.** What a check extracts from a file is kept by the file's content (its git
  blob id where the index holds it unchanged, its content hash otherwise) together with the extracting code's own version
  (the code and every project module it imports), and served again while both are unchanged; the file is not re-parsed
  then. One shared mechanism serves every push check that today parses, scans or reads tracked files whole:
  - the research pointer check;
  - the record build check (`make record CHECK=1`) and the glossary build check;
  - the duplicate-definition check and the function-cap check;
  - the conflict-marker check over tracked files;
  - and any other push check whose measured time is mostly per-file work.

  A check's answer is the same with the cache as without it (`L7R_CACHE_OFF=1`), proven by a test per check. A changed file,
  or a changed extractor, is extracted again.
- **FR-002 The ledger check costs a pass once.** A check pass's cost cells, once its transcript is finished, are kept and
  never recomputed. The search for a pass's transcript is not repeated: the transcripts are found by one scan, and only
  passes not yet costed - those logged since the last run - are looked up. The GM's "keeping track of how far back it is
  that our most recent search was for". The answers (which passes are owed, and each owed row) are unchanged.
- **FR-003 The review lookup asks only when it matters, and reads git once.** Which review checks a change owes is asked:
  - at landing (the push);
  - at the hourly checkpoint (FR-008);
  - when a review agent is dispatched, to refuse one not owed;
  - and by `make verify` on request.

  It is no longer asked when a gate starts or at a turn's end after a green gate (the feature 231/248 rule to review on a
  green gate gives way to the hour and the landing, as glyph-check already did in 375 amendment 9). Its reads of the base
  revision are one batched git read, not one process per file.
- **FR-004 check-bundle reads the base once.** The base revision's files a bundle needs are read once per base revision and
  kept, and its helper steps run without starting a new interpreter each. The bundle it writes is unchanged.
- **FR-005 The old-layout check is retired.** No clone uses the old layout (the GM). The check, its self-test, its call at
  the gate and at the push, its tests and the text naming it are removed. History (specs, logs) keeps its words.

### Phase 2 - the push checks in one process

- **FR-006 One process runs the push's Python checks.** The push's Python checks run inside one interpreter, each with the
  same output and exit as when run alone. A refusal still names the check, its fix and its escape. A check that must run as
  its own process says why at the point it is left out.
- **FR-007 A self-test runs when its code changed.** A check's self-test passes once per version of its code - the check and
  every project module it imports, as FR-001 - and is not run again until that changes.

### Phase 3 - the hourly step-back

- **FR-008 One hourly checkpoint for a long-running feature.** The clock glyph-check keeps becomes the feature's checkpoint.
  It runs from the feature's first event in the clone, or its most recent reopening, as today. When an hour has passed since
  the start or the last checkpoint, everything the checkpoint owes comes due together:
  - every review unit then owed (glyph-check, and since FR-003 the others);
  - and a step-back review of the hour.
- **FR-009 The step-back is the round arbiter, on the hour.** The step-back review is dispatched to the round arbiter, the
  same independent agent that rules on tripwires (the GM's "hourly arbiter"), on a bundle a script builds from the session's
  own record of the hour:
  - where the time went (thinking, tools by command, waits, subagents);
  - the dispatches, review rounds and verdicts;
  - the guard refusals;
  - the task in progress.

  It answers:
  - Is the session going in circles, or oscillating between approaches?
  - Is it packing features against a number nobody researched, where more room would settle it ("Room before packing")?
  - Is a step slow or a guard misfiring enough to be worth a tooling fix?
  - Is anything too big for the session, for the GM?
- **FR-010 Its findings are acted on.**
  - A finding of a loop or of packing is binding, as a ruling is: it names the route to change and the session changes it.
  - A tooling fix is an open item held as an arbiter's `tooling_fix` is (feature 379): made with its test and landed, or
    declined as an overhaul to the GM's review.
  - Anything for the GM is a row of the GM's review.
  - An hour with nothing to change records that and adds nothing to the GM's review.
- **FR-011 Held, not optional.** While the checkpoint is due, the feature's next `make tick` refuses until the step-back's
  ruling is recorded and every review unit it owes has been dispatched, naming the commands. A feature under an hour owes
  none of it.
- **FR-012 The manual check retires.** Once phase 3 has landed, this session's hand-run hourly check of the backlog session
  is stopped.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-005, FR-006, FR-007) The push's checks: from about 24 s, the measurement the GM saw
  (observed 2026-10-13; method: each check timed alone in this clone, load about 6), re-measured at the feature's claim as
  19.87 s (`m:push-checks-before`, research R2), to under 6 s, measured with R2's command
  (`scripts/measure/push_check_times.py`, warm) so that before and after are comparable. Each phase's own measurement is
  recorded in `measurements.json`.
- **SC-002** (FR-001) For every check the cache serves: its output over the repository is identical with the cache on and
  off. A file changed after a cached run, and a changed extractor, each produce a fresh extraction (tests).
- **SC-003** (FR-002) The ledger check over the clone's pass log answers as before, and its run with every pass already
  costed reads no transcript (a test); measured before and after.
- **SC-004** (FR-003) A gate start and a turn's end after a green gate run no review lookup (the guard suite); the push and
  the hourly checkpoint still refuse what is owed; one lookup starts at most a few git processes, not one per file
  (measured).
- **SC-005** (FR-004) A bundle built twice over the same base is identical to today's, and the second build reads the base
  from the cache.
- **SC-006** (FR-006, FR-007) Every push check, run in the one process, gives the same output and exit as run alone, on a
  passing tree and on a tree seeded to fail each. A self-test kept as passed runs again when a module its check imports
  changes (a test).
- **SC-007** (FR-008, FR-009, FR-010, FR-011) In a fixture clone:
  - an hour into a feature, `make tick` refuses, naming the step-back and the owed reviews;
  - the bundle carries the hour;
  - a ruling with a tooling fix opens an item that holds the next tick;
  - a quiet ruling adds nothing to the GM's review;
  - under an hour, nothing is held.
- **SC-008** (FR-009) The step-back run on the recorded hour of 374's batch 13 (the bamboo strip: five seating-order routes
  and two probes, room never tried) names the packing and the number; run on a quiet hour of the same session, it finds
  nothing to change.
- **SC-009** (FR-012) The closing report says this session's hourly cron job was deleted, and the session's job list
  shows none.

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-12): CHANGES REQUIRED, one item, applied: FR-007's "its code" is the check and every
  project module it imports, as FR-001; SC-006 tests that a changed imported module re-runs a kept self-test.
- spec-fidelity-verify, Mode 3, round 2 (2026-10-12): CHANGES REQUIRED, one item, applied: SC-001 named two baselines as one;
  it now keeps the GM's 24 s, names the claim-time re-measurement (`m:push-checks-before`, 19.87 s) and measures the after
  with the same command.

## Decisions Recorded

- **The record check's inputs are measured, not guessed** (research R1, an audit hook on `open`): `research/`, the glossary
  assets and the import closure of the module run. Map drawing convention: N/A - tooling.
- **Partial citations are not cached** (research R3): keeping 5,400 small files per file cost what reading them does (0.33 s
  against 0.32 s, observed 2026-10-12; method: `/usr/bin/time`, research R3). Tried, measured, reverted; the plan review ruled the narrowing LEGITIMATE.
- **The record's render is not cached per page**: every page reads the whole record's link index, so the whole-check memo is
  its cache; each per-file setup step goes through the store's memo (research R4).
- **The step-back is the round arbiter** on an `hour` trigger (the GM's "hourly arbiter"); a quiet `continue` adds no row to
  the GM's review.
- **No escape on the checkpoint hold** (plan review round 1): the 379 tooling-fix hold beside it has none either.
- **Phases landed together**: phases 1-3's tooling landed in one `make land-tooling` (0906d798a) once phase 3's tasks were
  ticked, because one Makefile change carried all three; the engine edits (the splitter's bisection, the store's memo
  protocol) land with the feature's close by the gated route.
- **Found while working**: `make land-tooling` cannot see the clone's own review-ledger rows, so a feature's review passes
  read as owed in its worktree; landed under `LEDGER_ROWS_OK` with the reason, and named in the closing report for a fix.
