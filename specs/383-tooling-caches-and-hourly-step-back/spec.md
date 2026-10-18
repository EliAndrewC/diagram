# Feature 383: Tooling caches, one-process push checks, and the hourly step-back

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-12
**Status**: In progress 2026-10-17 - amendment 8 (FR-047). Before it: amendment 7 landed with T56 open (plan D50, **Lands open**): spec FAITHFUL (round 4), plan CLEAR; the stagger withdrawn, a 4th same-type launch within ten seconds sent to the `check-wave` workflow, the Workflow guard holding every unit and declared verify step to the Agent guards, the authorization for the 15 wave jobs; the month's 671 hand-launched waves caused 803 main-session wakes, 1.2 a wave (observed 2026-10-17; research R21), so a workflow saves ~0.2 wakes a wave; the first real wave is measured by `make wave-report`, which the guard names at each run's start. Before it: Done 2026-10-17 - amendment 6 reopened and landed: spec FAITHFUL (round 2), plan CLEAR; the guard refuses a repeated block wherever it sits, only the agent file being reused across launches (research R16); a fan-out launches its first alone, its later launches then writing 2,274 tokens fresh against 5,721 (R18); no 1-hour subagent cache (a test); the root CLAUDE.md 37,985 -> 13,730 characters, research 25,402 -> 20,772, tests 18,157 -> 6,340, every rule kept or reachable (R19); the research-pass agent (R17). Before it: Done 2026-10-17 - amendment 6 landed: spec FAITHFUL, plan CLEAR (round 5); a back-to-back dispatch of an identical prompt writes nothing fresh on its first call, and one with a different prompt only its prompt and environment block, from ~26-29k (observed 2026-10-17; research R13, R14, R16); spec-fidelity without the instruction files found every recorded item, three runs a leg (R14); the modal guidelines in the agent files, bundles held under 2,000 shared characters; the dispatch guard; one copy of the root CLAUDE.md per session and subagent (R15). Before it: Done 2026-10-17 - amendment 5 landed: plan CLEAR (round 4, D31 rewritten for where the gate really runs tooling tests); after a Makefile-only change the gate's full run reuses 1,739 of 1,824 tooling tests with their coverage carried, 167 -> 132 s (m:gate-tooling-makefile-a5); reuse per test, a source-page edit re-runs 15 tests not 219 (observed 2026-10-17; research R12); a soundness defect in reuse fixed (D32b, research R12); 12 tests of code moved off the real record. Before it: Done 2026-10-17 - amendment 4 landed: spec FAITHFUL (round 3), plan CLEAR; five guard suites 2-4x faster with their checks unchanged (research R11); a landing 30.04 -> 27.28 s (m:land-tooling-landing-a4); make parts-sweep (the arbiter's fix). Before it: Done 2026-10-17 - amendment 3 landed: spec FAITHFUL (round 2), plan CLEAR (round 5); no review check moves to Sonnet 5.5 (research R10); always-run tooling files 18 -> 0 of 128; a landing 37.05 -> 30.04 s (m:land-tooling-landing-a3); hooks-test idle 16.06 -> 2.6 s (m:hooks-test-idle); sync-with-main suite 36.23 -> 17.88 s (m:sync-with-main-suite). Before it: Done 2026-10-13 - amendment 2 landed: spec FAITHFUL (round 4), plan block CLEAR (round 2); a landing 113.98 -> 37.05 s (m:land-tooling-landing-before, m:land-tooling-landing-after), tooling reuse 27.58 -> 19.35 s with 18 of 127 files always run (m:land-tooling-tests-reuse-a2), the claims gate 8.53 -> 1.65 s (m:claims-gate-push). Before it: Done 2026-10-13 - amendment 1 landed: spec FAITHFUL (round 3), plan block CLEAR; land-tooling's tooling tests 36.21 -> 27.58 s (606 of 1,796 tests ran with reuse, m:land-tooling-tests-reuse), quote-verbatim's verdicts cached. Before it: Done 2026-10-13 - spec FAITHFUL (round 3), plan CLEAR (round 3), every task ticked; push checks 19.87 s -> 1.92 s (research R6); tooling landed 0906d798a; the GM's review open (the first step-back's note)

**Affects**: tooling, review process

**Amendment 1 approved**: the GM, 2026-10-13, "Yes please we should definitely skip suites the clone already passed." and "And also, while I realize we don't run it very often, I feel like `quote-verbatim` would benefit from the same caching layer we implemented elsewhere, right?"

**Amendment 5 approved**: the GM, 2026-10-17, "Yes, please file it that way, and then do that work. Thanks."

**Amendment 6 approved**: the GM, 2026-10-17, "Yes. Please file that and then implement it. Thank you."

**Amendment 6 extended**: the GM, 2026-10-17, "that also seems like a token efficiency improvement that we need to make or measure or address or whatever."

**Amendment 6 reopened**: the GM, 2026-10-17, "Yes, go ahead and reopen amendment 6 for all five. Thank you."

**Amendment 7 approved**: the GM, 2026-10-17, "So please take a look at that and then implement its recommendations, because there's some pretty good analysis in there that I think will really help us out."
**Approved**: the GM, 2026-10-17, "And yes it may land without T56."
**Amendment 8 approved**: the GM, 2026-10-17, "Okay sounds good."

**Amendment 4 approved**: the GM, 2026-10-17, "I think I do want a next round uh, for the guard suites running serially, so uh, splitting those up does seem good." and "So yes, please fold those two into the same round as the sweet splitting. and then go ahead and work that."

**Amendment 3 approved**: the GM, 2026-10-17, "Thus, I accept your proposal. Of three things, but I would also like you to add a fourth thing, which is doing those measurements on cheaper models."

**Amendment 2 approved**: the GM, 2026-10-13, "Yes, please. So go ahead and do the savings that you've already measured, no matter what." and "And then go ahead and land whatever timing improvements you are able to figure out."

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

### Amendment 1 - what the clone already passed, and quote-verbatim (`request.md`, Amendment 1)

- **FR-013 A tooling test file the clone passed is not run again on identical inputs.** A tooling test file that passed in the
  clone records what it read - the files it opened and the directories it listed, in its own process and in every Python
  process it started - each by its content. Where `make land-tooling` - the one caller, through a named switch its
  checks set - finds every one of them unchanged, the file is not run again and the run says so; a file that started any other program against the repository is
  always run, since what that program read is not known. A failure is never kept. The guard suites keep the reuse they have.
- **FR-014 quote-verbatim keeps its verdicts by content.** A quotation's verdict is kept by the quoted passage and the page's
  text, under the version of the code that judged it, and served again while both are unchanged; its report is the same with
  the cache as without it.

### Amendment 2 - the files that always ran, and the rest of a landing (`request.md`, Amendment 2)

- **FR-015 A read-only git question is part of what a test file read.** A tooling test file that asked git about the
  repository (for example `git ls-files`, `git diff`, `git log`, `git show`, `git rev-parse`) records each question and its
  answer's digest; where every question asked again in the worktree gets the same answer, and every other input is unchanged,
  the file is reused as under FR-013. A git command that may change the repository, or one whose answer cannot be asked again,
  still makes the file run.
- **FR-016 A Python process a test starts keeps the recording.** A test file whose Python children are started in a way that
  drops the recording (an isolated interpreter, a fresh environment) records what those children read: the recording's variables are put into the environment the test gives the child. A
  child started isolated (`-I`, `-E`, `-S`) ignores that environment and its file runs; no tooling test file does so on the
  amendment's first recording (0 of 126, `scripts/measure/tooling_reuse_time.py`'s causes, measured 2026-10-13; research R8). The measured cost behind FR-015 and FR-016: 29 and 28 of the 102
  test-seconds that always ran (research R8, measured 2026-10-13).
- **FR-017 Each step of a landing is timed.** `make land-tooling` writes each step's time - the worktree, the patch, the guard
  suites, the tooling tests, the push - to its log, so that where a landing's time goes is read from the log and not guessed.
- **FR-018 A landing runs each test once, and its independent checks side by side.** In a landing, a tooling test file that
  `make hooks-test` would run and that the landing's tooling test run also runs runs only once, in the run that can reuse the
  clone's pass; the guard suites and the tooling tests, which share nothing they write, run at the same time. Measured (research R7,
  2026-10-13): the guard suites' step 80.7 s, of which the scripts' pytest files (57 of 60 of them
  tooling files, run again by the next step, 30.2 s) are about 45 s.
- **FR-019 What else the measurement shows is improved and landed.** A step the FR-017 timing shows costing more than a few
  seconds that can be cut without loosening a check is cut in this amendment; one that cannot is recorded with its
  measurement.
- **FR-020 Every other cause of an always-run file is looked at.** Each remaining cause in research R8 - `source-block-hooks.sh`,
  ruff, node, resvg, bash, make, pdftotext, grep, `claude`, a read of a file git ignores - is either made known (the file reused on
  identical inputs) or recorded in the research with its test-seconds and why it cannot be.

### Amendment 3 - the always-run files, tests not imported, the guard suites, and cheaper models (`request.md`, Amendment 3)

- **FR-021 The tooling test files that always run are made known.** Each of the 18 files research R9 left always running
  (about 5 s of a landing's wall time; observed 2026-10-13, method: research R9's test-seconds over the workers) is reused on identical inputs where what its programs read can be recorded or asked
  again; one that cannot is recorded in the research with its seconds and the reason.
- **FR-022 A test file a run will not run is not imported.** Where a run has decided before collection which test files it
  will skip - the tooling tests a landing reuses, the tests `make quick` deselects as unaffected by the change, a targeted run -
  those files are not collected (imported) at all, in every worker. The tests that run, and their results, are the same as
  before. Measured before and after: `make quick`, a targeted `make test-file`, and a landing's tooling run.
- **FR-023 A guard suite runs only where what it reads changed.** Which guard suites ran in the recorded landings, and why
  (the landing's own files, or main moving), is measured; a suite re-run though nothing its cases read changed has its inputs
  narrowed, or the suite is split so each part has its own; the slow suites (sync-with-main, review-gate, entry-gate) are
  looked at first. Nothing a suite checks is dropped.
- **FR-024 The checks never tried on a cheaper model are tried on Sonnet 5.5.** spec-fidelity, glyph-check, impl-drift,
  building-review, modal-form, modal-research and modal-depiction are each run on Sonnet 5.5 against recorded Opus runs with
  known findings, three runs a leg (the doctrine of feature 251 and `tests/test_agent_models.py`), and their cost compared. A
  check whose Sonnet runs find every known finding moves to Sonnet in its file and the tier table; one that misses stays on
  Opus. Every result, either way, is recorded where the next session looks: the tier table, `docs/spec-kit-and-reviews.md`, and
  a pointer from `CLAUDE.md`, so the record of which checks were tried is not lost again.
  These trials come FIRST (the GM: "we should do that pretty much right away"): they start before FR-021 to FR-023 and
  are not held behind them.

### Amendment 4 - the serial guard suites, and the tooling tests a landing still runs (`request.md`, Amendment 4)

- **FR-025 A slow guard suite runs in parallel parts.** Every guard suite over 20 s run alone - main-tree 57.7 s, no-poll 48.4 s,
  finished-run 39.1 s, pair 23.5 s and review-gate 21.8 s (observed 2026-10-17, method: each suite run alone under `time`,
  load about 4) - is dealt into parts that run at the same time, as sync-with-main's are, or, where its time is waiting
  rather than work, has the wait in its tests cut, without changing what the guard does or which checks run; every check
  still runs and is counted.
- **FR-026 The tooling tests that read the whole repository take less time.** The tests a landing cannot reuse because they read
  the whole repository - the longest, test_content_cache's whole-repository comparison (9.4 s) and test_open_questions on the
  real tree (4.8 s; observed 2026-10-17, method: a fresh worktree's tooling run with per-test times) - are split into parts
  that run in parallel, or made faster in their own work, and each still checks its property over the whole repository
  (test_content_cache's is SC-002's whole-repository proof).
- **FR-027 A landing's tooling run starts faster.** What a fresh checkout's tooling run spends before and around its tests - the
  workers' start, collection, the reuse decision in every worker, the first imports - is measured part by part, and each part
  that can be cut without changing which tests run or their results is cut.

### Amendment 5 - the gate's tooling run reuses, and reuse per test (`request.md`, Amendment 5)

- **FR-028 The gate's tooling run reuses what passed.** When the gate's tooling hash changes, its run of the tooling tests
  reuses each test's pass on identical inputs, as `make land-tooling` does, so a Makefile edit re-runs only the tests that read
  what changed. The hash covers every file under `scripts/`, its subdirectories included.
- **FR-029 A pass is reused per test.** Each tooling test's reads are kept on its own, and a test is reused when its own reads
  are unchanged; a test file is imported only when one of its tests will run. What every test of a file depends on - the file
  itself, the `conftest.py` files above it, the test configuration and the reuse plugin's own code - is part of each test's
  reads.
- **FR-030 Tests of code that read the real repository are moved to fixtures, case by case.** Where, after FR-029, a test whose
  subject is code still re-runs on edits to the repository's data, it reads a fixture instead; a test whose subject is the
  repository's data keeps reading it. Each moved test is listed with what it read before and after.

### Amendment 6 - what subagents share is cached (`request.md`, Amendment 6)

- **FR-031 spec-fidelity runs without the project's instruction files.** It launches without CLAUDE.md, the nested
  CLAUDE.md files and the memory index, as every other defined agent does; what it needs from them is written in its agent
  file, which is its system prompt. The agent-tier test names no exception.
- **FR-032 Text every bundle of a check repeats lives in that check's agent file.** A bundle carries only what is particular
  to its unit; the static text each bundle of a check repeats - first, the modal guidelines the three modal checks' manifests
  carry - moves into the agent file.
- **FR-033 A recurring ad-hoc dispatch becomes a defined agent.** The claims triage and the modal triage, dispatched as
  general-purpose agents carrying the whole instruction context, get agent files of their own (their manifests' standing
  instructions, a pinned tier, no CLAUDE.md), and the commands that prompt their dispatch name them.
- **FR-034 A block repeated across dispatches is refused, wherever it sits.** An Agent dispatch whose prompt repeats a large
  identical block of an earlier dispatch of the session is refused, wherever the block sits in the prompt - a subagent's first
  message has no cache breakpoint, so only its system prompt is reused across launches (research R16) - with the fix: move the
  shared text into the agent's file, its system prompt. A prompt identical to an earlier one as a whole is not refused.
  (Corrected by the reopening: it read "after a part that differs ... put the shared text first, or in an agent file".)
- **FR-035 Bundles are tested for shared text.** A test builds two bundles of each check kind and fails when their identical
  text passes a small limit.
- **FR-036 The cache is measured and the rule written.** `make subagent-cache` reports, per agent type, from the subagent
  transcripts: the tokens a dispatch writes fresh on its first call, against a dispatch of the same type minutes before, and the
  manifests' repeated text. CLAUDE.md states the rule - shared context in the agent file; text placed first in a launch prompt is not reused
  across launches (research R16) - and names the guard.

- **FR-037 A session loads the project's instructions once.** A session started in the repository's checkout that works in its
  clone does not load the clone's copy of the root CLAUDE.md beside the checkout's, nor do the subagents it dispatches load it
  when they work with files in the clone; the clone's nested CLAUDE.md files still load where they are needed. gm-assistant has
  the same layout; its settings are that repository's, so this feature reports the exclusion line for it to the GM rather than
  editing it.
- **FR-038 No 1-hour subagent cache.** A test fails when a project setting, an agent file or the container's setup turns on a
  1-hour subagent prompt cache (`experimental.cacheTtl`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`).
- **FR-039 A fan-out launches one first.** (Withdrawn by FR-042, amendment 7: research R20.) When several dispatches of one agent type go out together, the first goes alone and
  the rest follow once it has started, so they read its cached prefix; the dispatch rules say so and a guard holds it.
- **FR-040 CLAUDE.md is an always-on core plus an index.** The root CLAUDE.md (and each nested one) keeps the rules a session
  needs before it knows to open a doc, one line each, and an index; the rest moves VERBATIM into topic docs that open with
  "Load this file when:". An independent agent enumerates every rule of the old files with a verdict (kept, moved and
  reachable, moved but unreachable, dropped, changed), every one not kept-or-reachable is fixed, and a test holds that every
  hook message quoting CLAUDE.md still resolves.
- **FR-041 The month's general-purpose job families are swept.** Each family of general-purpose launches in the transcripts is
  classed - recurring, so given a defined agent or pointed at the existing one; or one-off - and the list is recorded.
### Amendment 7 - waves through Workflow (`request.md`, Amendment 7)

- **FR-042 The hand-stagger is removed.** "Launch one first" (FR-039) leaves CLAUDE.md, the docs and the dispatch guard: the
  extra main-session turn it forces re-reads the whole context, which costs more than the prefix it saves (research R20).
- **FR-043 A wave of 4 or more agents of one type runs as a Workflow, each agent typed.** Every `agent()` call passes
  `agentType`, so its definition (`omitClaudeMd`, its few tools) applies rather than the workflow's default subagent; the main
  session gets one notification for the wave; per-item follow-up is a `pipeline()` stage; each agent returns a `schema` object,
  not prose. A saved workflow, `check-wave`, carries a wave of typed checks: its arguments are the agent type and the units
  (each a label and its prompt), and it returns one object per unit - its label, its verdict word and its reply text (which the
  answer-recording commands read whole). Its per-item follow-up is `pipeline()` stages of its own, so the main session sees
  one finished result: (1) a FAILED unit - one that came back null (its agent died after the tool's retries, or was skipped; a
  reply that misses the schema is retried by the tool itself, so a non-null reply is a valid one) - is re-launched once with the
  same prompt; (2) a VERIFY step is declared with its unit (`then: [{agentType, prompt}]`, each type one of the wave jobs) and
  runs after it with the earlier reply appended to its declared prompt as data. Every prompt a run will launch - unit, re-launch
  and declared verify step - is known when the run starts, so every one is guarded then (FR-045) and recorded as a dispatch.
  Two or three agents of one type stay plain Agent calls in one message.
- **FR-044 The appended system prompt authorizes it, narrowly.** `scripts/container/append-system-prompt.md` pre-authorizes
  `Workflow` for a wave of 4 or more agents of one of the NAMED recurring wave jobs - source-applicability, quote-check,
  settlement-review, entry-drift, modal-depiction, record-format, impl-drift, modal-research, building-review, source-reader,
  glyph-check, modal-form, round-arbiter, and the claims-triage and modal-triage agents that replaced general-purpose waves -
  with `agentType` on every call, and nothing broader (no general-purpose fleets, new kinds of fan-out or deep research without the GM's request); a test holds
  that the text exists and names only those jobs, each with a file in `.claude/agents/`.
- **FR-045 Hooks hold it, and a wave keeps every guard a check has.** An Agent launch that is the 4th of one type within about
  ten seconds is refused with the Workflow form in the message (`WAVE_OK` with a reason passes); a `Workflow` whose script calls
  `agent(` without `agentType` is refused (`GP_OK` passes); and every unit of a `check-wave` run is held by the same per-dispatch
  guards an Agent call of its type is (model, repeated block, bundle and owed check, decide-first, freeze, round caps, review
  occasions, escalation), its launch and return recorded as an Agent call's are; a `Workflow` whose script calls a typed
  `agent(` of a type those guards cover other than through `check-wave` is refused: a guard the hooks of the Agent tool apply is
  never skipped because the check ran in a workflow (research R20: no PreToolUse or PostToolUse Agent hook fires for an agent a
  workflow spawns). Each hook has its suite cases.
- **FR-046 The first real wave is measured.** A wave of 4 or more real checks run through `check-wave`: each agent's
  first-request read and write (the 2nd and later read the definition's prefix and write no ~35k), the main session's wakes
  during the wave (one), against the last hand-launched wave of the same check.
### Amendment 8 - a plan review carries the GM's words its blocks answer (`request.md`, Amendment 8)

- **FR-047 A plan-review bundle carries the request from the amendment its blocks answer onward.** `request.md` in the bundle
  holds the feature's original request (what comes before its first amendment heading) and every amendment section from the
  EARLIEST one the blocks under review answer through the last - a later amendment can change what an earlier one asked, so
  none after it is left out - and `request-index.md` holds the heading and first line of each section left out. The amendment
  a block answers is the one its heading names, else the one whose spec section holds the requirements it cites; a block that
  answers none (the original plan) gets the whole request, as does a request with no amendment headings. A spec-delta bundle
  for later spec rounds and a spec archive are NOT built: later rounds read ~0 characters of the spec since the round hook's
  diff, and first rounds ~2.4k per agent (research R22).

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

- **SC-010** (FR-013) A tooling test file passed in a clone is skipped in a worktree with identical inputs, and runs when a file
  it read, a directory it listed or a module a child process opened has changed, or when it started another program against
  the repository; a failing run records nothing. `make land-tooling`'s checks measured before and after on the same landing.
- **SC-011** (FR-014) quote-verbatim's report on a question is byte-identical with the cache on and off, and a second run is
  measured against the first; and a quotation is judged afresh when the quoted passage, the page's text or the judging
  code changes (a test).
- **SC-012** (FR-015, FR-016, FR-020) A tooling test file whose only always-run cause was a read-only git question or a Python child
  is reused in a worktree with identical inputs, and runs when a git answer changes (a test with a fixture repository) or a
  file its child read changes; a git command that writes still makes the file run. The count of tooling test files that
  always run, before (38 of 126, research R8) and after, each printed by `scripts/measure/tooling_reuse_time.py`.
- **SC-014** (FR-020) For each other cause in research R8, either the files it kept running are reused on identical inputs
  (they leave the after count of SC-012), or the research records the cause with its test-seconds and why it cannot be made
  known.
- **SC-013** (FR-017, FR-018, FR-019) `make land-tooling` measured step by step from FR-017's log, with the load: before, on a
  real landing made with the timing and none of the cuts; after, on a real landing with them; each tooling test file runs at most once in the landing (its log); the guard suites and the tooling
  tests overlap in time (their step times in the log).

- **SC-015** (FR-021) The count of tooling test files that always run, before (18 of 127, research R9) and after, printed by
  `scripts/measure/tooling_reuse_time.py`; each one left with its test-seconds and reason in the research.
- **SC-016** (FR-022) The same tests pass with and without the collection skip (counts compared); `make quick`, a targeted
  `make test-file` and a landing's tooling run timed before and after on the same tree, back to back, with the load.
- **SC-017** (FR-023) The guard suites each recorded landing ran, with why; for each suite narrowed or split, a test that
  an edit outside its new inputs leaves it skipped and one inside runs it; a landing measured before and after.
- **SC-018** (FR-024) Per check: the recorded cases, each finding found or missed by each of the three Sonnet runs, turns and
  cost against the Opus run; the tier each check ends on; `tests/test_agent_models.py` green with the table matching the
  files.

- **SC-019** (FR-025) Each split or wait-cut suite timed whole before and after, its check count the same; `make hooks-test` with every suite
  (`HOOKS_ALL=1`) timed before and after.
- **SC-020** (FR-026, FR-027) The tooling run in a fresh worktree at the clone's HEAD timed before and after, with the tests that
  ran and the longest single test; the start-up parts measured; a real landing measured before (m:land-tooling-landing-a3) and
  after, step by step.

- **SC-021** (FR-028) After a Makefile-only change, the gate's tooling phase runs only the tests that read the Makefile (count
  and time before and after); a change under `scripts/<dir>/` changes the tooling hash (a test).
- **SC-022** (FR-029, FR-030) An edit to one research source page re-runs only the tests that read it - test_sources' count before
  (43, the whole file) and after; an edit to a `conftest.py` re-runs every test below it (a test); a landing's tooling step
  measured before (m:land-tooling-landing-a4) and after.

- **SC-023** (FR-031, FR-033) A spec-fidelity dispatch made minutes after another writes on its first call what a defined
  agent's does - before ~25.8k tokens (observed 2026-10-17; research R13), after measured the same way; the claims and modal
  triage the same against general-purpose's ~29.2k (research R13). And spec-fidelity without the files still finds what it
  found with them: feature 251's spec, round 1, three runs a leg with and without, scored by an independent reader (the
  condition `tests/test_agent_models.py` recorded for removing the exception, specs/256 research R6).
- **SC-024** (FR-032, FR-035) The modal checks' manifests repeat at most the test's limit - before 15-17k characters repeated in most
  manifests (research R13) - and the bundle test fails on a seeded repeated block.
- **SC-025** (FR-034, FR-036) The guard refuses a unique sentence followed by a shared 10 KB (suite cases; the reopening's SC-027 replaces what it said of a block placed first); `make subagent-cache` prints every agent type's numbers, and its total subagent spend before and after; CLAUDE.md states
  the rule and names the guard, and no longer names spec-fidelity as keeping the instruction files.

- **SC-026** (FR-037) A session started in `/diagram` that reads a file in its clone carries one copy of the root CLAUDE.md, not
  two - before both (research R15), after one, measured the same way - and a nested one still loads; and a subagent it
  dispatches that reads a file in the clone, one with `omitClaudeMd` and one without, is measured the same way before and after
  (if subagents never load the clone's copy, that is recorded as the answer to the GM's question).
- **SC-027** (FR-034, FR-036) The guard refuses a shared block placed first as well as one after a unique sentence, passes a
  wholly identical prompt, and names only the agent-file fix (suite cases, red on the guard landed before the reopening); and
  CLAUDE.md's rule and guard row, `docs/guards.md` and `docs/spec-kit-and-reviews.md` name only the agent-file fix, none saying to
  put shared text first.
- **SC-028** (FR-038, FR-039) The TTL test fails on a seeded 1-hour setting; a staggered fan-out's later launches read the
  first's prefix from the cache, measured against a fan-out sent together (first-request read and write per launch) - kept as
  R18's measurement; FR-039 is withdrawn and nothing enforces it.
- **SC-029** (FR-040) The root CLAUDE.md's size before (37,662 characters when filed, 37,985 at the trim after main added a
  line; observed 2026-10-17; `wc -c`) and after, and a fresh
  session's first request before and after; the enumeration's verdicts with none left dropped or unreachable.
- **SC-030** (FR-041) The families' table: launches per family since 2026-09-19, the last date each recurred, and what each
  became.
- **SC-031** (FR-042, FR-045) The guard no longer refuses a second launch within seconds of a cold first; it refuses the 4th
  same-type launch within the guard's window (a design number, ten seconds) and passes the 3rd, a different type, and `WAVE_OK`; a `Workflow` script with an untyped
  `agent(` is refused and `GP_OK` passes, and one calling a guarded type outside `check-wave` is refused (suite cases); and a `check-wave` unit a guard of its type would refuse is refused,
  with the guard's own message, a declared verify step's included; a unit that returned nothing is re-launched once by
  `check-wave` and no more, and a declared verify step runs after its unit with the reply appended (a test of the workflow file).
- **SC-032** (FR-044) The test fails when the authorization is missing, names an agent with no file, or names a job outside the
  list.
- **SC-033** (FR-045) A `check-wave` run's units are recorded launched and returned as Agent calls' are (the freeze holds while
  one runs), a re-launched unit (it pairs to the same dispatch) and a verify step (it pairs by its declared prompt, which its
  launched prompt begins with) included - a test on recorded hook payloads, and the event log of the measured wave.
- **SC-034** (FR-043, FR-046) The measured wave, run through `check-wave` with every agent typed: per-agent first-request read and write, and the main session's wakes, against the last
  hand-launched wave of its check (research).
- **SC-035** (FR-047) A plan review of the newest amendment's block on 383 carries the original request and that amendment
  alone, a fraction of the whole (measured on the bundle), with every other section's heading in `request-index.md`; a block of
  an earlier amendment carries it and every later one; a block of the original plan, or a feature with no amendments, the whole
  request (tests of the bundle builder).

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-12): CHANGES REQUIRED, one item, applied: FR-007's "its code" is the check and every
  project module it imports, as FR-001; SC-006 tests that a changed imported module re-runs a kept self-test.
- spec-fidelity-verify, Mode 3, round 2 (2026-10-12): CHANGES REQUIRED, one item, applied: SC-001 named two baselines as one;
  it now keeps the GM's 24 s, names the claim-time re-measurement (`m:push-checks-before`, 19.87 s) and measures the after
  with the same command.

- spec-fidelity-verify, Mode 3, round 3 (2026-10-12): FAITHFUL; its aside applied (D8 and T09 carry the test that a changed
  imported module re-runs a kept self-test).
- Amendment 1, spec-fidelity-verify, round 1 (2026-10-13): CHANGES REQUIRED, four items, applied: SC-011 tests that a changed
  passage, page or code is judged afresh; the approval line quotes both of the GM's sentences; FR-013's reuse is one named
  switch, `make land-tooling` its one caller; this history's round 3 line.

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
