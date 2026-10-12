# Feature 375: An efficient process, enforced and measured by the tooling

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Done 2026-10-12 - amendment 9 landed: spec FAITHFUL (round 3), plan CLEAR (round 3); glyph-check due on the feature's hour, all owed units together, or at landing (SC-032, SC-033 tested; SC-034 carried to 374); amendments 1-8 Done

**Approved**: the GM, 2026-10-12, "Yes to reopening the feature with that amendment, but instead of implementing it yourself, please reopen it and the hand off the work to the "Diagram performance" session, since it's already doing some similar work."

**Amendment 9 approved**: the GM, 2026-10-12, "Here's what I think we should do for `glyph-check`: we make it something which is run periodically rather than every time a map changes."

**Amendment 8 approved**: the GM, 2026-10-12, "yes please"

**Amendment 8 rulings**: the GM, 2026-10-12, "I confirm the check-bundle thing is good as you've done it.  it's also fine to do the 10 seeds.  As for the reviews being changed, I'll look at the table when you have it, thanks"

**Amendment 7 approved**: the GM, 2026-10-12, "Yeah, I think I want all of those things. But I agree with you that two, three, six, and eight are a good place to start."

**Amendment 5 approved**: the GM, 2026-10-11, "if it looks like the performance is slowing down to a meaningful degree, that's something you can mention when you say that the work has landed on main, but it doesn't need to be a gate anymore."

**Amendment 4 approved**: the GM, 2026-10-11, "yes please add that as amendment 4"

**Amendment 3 approved**: the GM, 2026-10-11, "So yes, please do all of that as part of amendments to 375."

**Amendment 2 approved**: the GM, 2026-10-11, "it does seem like a whole batch of pop-ups reaching the round cap at once should get a single ruling. because they are likely to be related. And that does sound like it would be more efficient. And then yes, please also do look at that bundle defect."

**Amendment 1 approved**: the GM, 2026-10-10, "yes to each of those possible changes, though for the in-progress features you can probably limit yourself to clones with active sessions, if it helps performance."

**Affects**: review process, tooling

**Input**: `request.md` (the GM, 2026-10-10)

## Why

Feature 372's waves 105-111 cost about 120 agent dispatches for about a dozen ranked rows. Measured from that session's record,
the time went to loops, not fixes:

| loop | measured in 372 (2026-10-10) |
|---|---|
| a drawing-page edit re-owed every pop-up linking the page | ~12 modal-depiction runs came back clean, owed only because 0100's or 0105's drawing page changed elsewhere |
| a page edited after its checks were dispatched | 0105 went through ~4 full rounds of 5-7 checks (wave 108); 0100 ~3 (wave 106) |
| one claim line or a regenerated table re-owed a whole section | impl-drift over 73, 105 and 105 claims in wave 106, nearly all unchanged and IN-STEP |
| decisions taken after editing, not before | the plan review blocked waves 106 (three times), 107, 108 and 111 on decisions that could have been put first |
| red gates from causes a cheap check finds | wave 106's gate red ~6 times: a file edited mid-gate, `building-programs.md` stale twice, stub pointers in found rows, two untested lines |
| small tool defects | the claims-triage parser read the word "TOUCHES" anywhere as a touched claim; a typo in `plan.md` forced a fresh plan review |
| pre-existing defects fixed mid-wave | small fixes a check proposed on blocks the wave never touched, each re-owing a round |
| the escalation filter run on what never reached the GM | `escalation-check` ran several times on drafts it then cut almost entirely |

An earlier retrospective (feature 328's close) named most of these as intentions; none was built into the tooling, and each
slid back. The GM's rule for this feature: **every change is enforced by the tooling - a hook, a gate or the owing logic -
never by a session remembering.**

## Requirements

Each requirement names its enforcement and is proved by a test that fails on the old behavior (constitution: a guard proves it
fires) and by a replay of 372's recorded deltas (SC-001). Thresholds are counted per checked thing (a page, pop-up, sheet, spec
or plan) and per feature - never per "wave", which was feature 372's own way of batching, not a unit every feature has. Where a
requirement needs the unit of work a check belongs to, that unit is a **task** of the feature's `tasks.md` (372's waves were
each one task).

- **FR-001 Content-scoped record-check owing.** A pop-up's checks are owed by a drawing or question page's change only where the
  changed block bears on that pop-up's kind: the owing logic (`scripts/record/modal_owed.py`, "a page its Drawing: names
  moved") runs one cheap triage of the changed blocks against the kinds whose `Drawing:`/`Entry:` name the page - as
  `make claims-triage` already does for claims - and owes only the kinds it names. Untouched kinds are cleared on the record.
- **FR-002 Line-scoped claim re-owing.** A claim is owed impl-drift when its own line or the rule text it sits beside changed,
  not when anything in its section changed; a regenerated table (`make building-programs`) re-owes only the rows whose text
  changed. Everything else in the section goes through one triage (`scripts/record/claims.py`, "code changed").
- **FR-003 Decide, then freeze.** (a) **Decide first**: a feature's record checks, review checks and claim checks are
  refused at dispatch (`check-bundle-hooks.sh`, `pair-hooks.sh`) until the decisions of the task they belong to carry a
  spec-fidelity verdict on the approach - the plan section for that task where the plan has one (a short decision preflight,
  recorded like a plan verdict), else the plan's own plan-stage verdict. (b) **Freeze while checked**: while any check on a page or modal is
  running or unanswered, an Edit to that page or modal is refused (`record-edit-hooks.sh`), except, once every check outstanding on
  that page or modal has returned, the edits those checks proposed, applied in one pass. (c) **Apply once**: a check on a page is not re-dispatched while another check on the same page is outstanding - all
  of a round's checks return, their edits are applied in one pass, then the page is checked once.
- **FR-004 Pre-gate preflight, inside the gate.** `make done` begins with a phase that takes seconds: regenerate the derived files
  (`building-programs.md`, the glossary, the record build), check research pointers, run spec-lint, and run the quick tests
  with coverage on the engine files the delta changed; it stops there on a failure. The gate refuses to report green when a
  tracked file changed while it ran (it hashes the tree at start and end), naming the file.
- **FR-005 Two tool fixes.** (a) The claims-triage reply parser reads only lines that open with `TOUCHES `. (b) A plan verdict
  survives an edit that adds or changes no decision (a typo, a wording fix); any edit that adds or changes a decision, ruled or
  new, anywhere in `plan.md` voids it.
- **FR-006 File, don't fix, outside the change's own words.** A check's finding on a block the feature did not change is
  reported apart (bundles mark which blocks changed); `make record-checked` files it as an open row of the feature (or a filed
  feature) rather than leaving an edit owed. Fixing it stays possible as that row's own change.
- **FR-007 The escalation filter owed only for what reaches the GM.** `escalation-hooks.sh` arms on a review only for findings
  left open (not fixed, verified, accepted with a reason or filed as a row); a review whose every finding is disposed of owes no
  escalation-check.

### Measurement (the base the rest is judged by)

- **FR-008 An event log written by hooks.** Every tool call appends one line to a per-feature log (time, session, feature, tool,
  category: edit, quick test, test file, gate, record check, review check, claims check, spec-kit step, other subagent - and the
  subagent's type and its return). The gap between a tool's result and the next call is the model's own thinking and writing.
  Written as it happens, so it survives context compaction, session changes and Claude Code's pruning of old transcripts.
- **FR-009 `make feature-report F=NNN`.** A mechanical table, in seconds, from the event log, `dev/run-log/`, the review ledger,
  the record-check answers and git: wall time split into thinking, editing, quick tests, test files, gates, waiting on each kind
  of subagent, and writing the spec (when it was written in the same session); the dispatches, rounds per checked thing, red
  gates and BLOCKED reviews; rows or tasks closed; and the cascade ratio - checks dispatched per line of the feature's own
  diff. Every feature gets one, however small, and its own cost is a row of it. No route closes a feature until
  its report is written into the feature's directory: the last `make tick`, a status line turned `Done`, and `make gm-reviewed`
  each refuse without it, and the push refuses a feature whose status reads closed without it.
- **FR-010 Tripwires.** Hooks fire the moment a pattern appears, not on a timer:
  - the same check on the same thing reaching its round cap (record checks capped at two rounds like review checks; today they
    have no cap);
  - a passage of a file returning to an earlier version within the feature (A -> B -> A), computed from the file's history;
  - a second red gate in a row;
  - the cascade ratio passing a set threshold;
  - the full gate or a test file run where the quick tier covers the change.
  A tripwire dispatches the round arbiter (FR-011); it does not stop the feature.

### Escalation without stopping

- **FR-011 The round arbiter.** A defined agent (its contract in `.claude/agents/`, its tier pinned) replaces the GM's waiver at a
  round cap or tripwire. It judges the process, not the work (its unit is the checked thing - a page, pop-up, sheet, spec or plan - never a task), from a bundle the tooling builds: each round's findings marked new,
  repeated or reversing an earlier fix; the diffs between rounds; the cascade chain (which edit re-owed which checks); the
  oscillation flags; the feature's request and spec. It rules one of: **continue** (one more round, naming what it must look
  at); **accept** (the state stands; what is left is filed as rows or accepted with a reason, and the unit closes); **process
  fault** (a loop, oscillation or disproportionate cascade: the unit stops, the fault is filed as a tooling row, the feature
  goes on elsewhere). One ruling per unit per trigger, binding: the session can neither re-dispatch it for another answer nor
  overrule an accept. Its cost is a row of the feature report.
- **FR-012 Landed, the GM's review after.** A feature that has to-review or held items lands with exactly one box open, the
  GM's review; a feature with none has no such box. `make gm-review` lists, by
  feature, two kinds: **held** (work on the item cannot go on until the GM decides - today's held rows, absorbed) and **to review**
  (work went on and landed; the GM may overturn: every arbiter ruling and every accepted finding). A feature whose only open item
  is that review reads `Done - GM review pending` in `make speckit-todo`; `make gm-reviewed F=NNN` closes it, and a ruling the GM
  overturns becomes a row of an open feature. The waivers the GM gives in requests (`REVIEW_ROUNDS_OK`) are no longer needed for
  round caps.
- **FR-013 The advisor, told what to watch.** The advisor takes no instructions and runs only when the working session calls it, so
  it is not the monitor; the tripwires and the arbiter are. `CLAUDE.md` names the patterns of FR-010 so an advisor call sees them,
  and the arbiter's bundle is what a session hands it.

- **FR-014 A measurement carried to a later feature is held by the tooling.** A success criterion measured in another
  feature's work is declared in this spec as carried (`Carried: <SC> -> <feature> <measurements key>`); that feature cannot
  close (every route of FR-009) while its `measurements.json` lacks the key, and `make speckit-todo` shows the carry.

### Amendment 1 (`request.md`, Amendment 1)

Both changes are this feature's: FR-015 closes a gap FR-001 left, and FR-016 is the process's own tooling for seeing where
work stands; the GM approved both in one answer.

- **FR-015 A pop-up check is owed only by what it reads.** FR-001's triage named a pop-up and owed every check of it, so an edit
  to a question page re-owed the pop-up's `modal-depiction` and an edit to a drawing page re-owed its research checks
  (`modal-research`'s accuracy, references and gaps) - measured on feature 343's kept triage, 11 of its 61 units (each
  reply line attributed by where its quoted block appears; spec review round 1). Now a changed block owes a check only when
  it is on a page that check reads: a question page (its `Entry:`) owes the research checks, a drawing page (its `Drawing:`)
  owes `modal-depiction`; a line whose block stands on both pages, or names no page, owes both (failing toward checking).
  And an edit to the pop-up itself owes `modal-depiction` only when it changes what that check reads of the pop-up: the
  pop-up new to the About form, or its Depiction tab, its `Drawing:` list, its About or its `Entry:` changed (About is where
  the check finds drawing statements that belong in Depiction - SUPERSEDED by FR-028, amendment 6: About no longer owes it; `Entry:` is where it finds the drawing pages a pop-up should
  link - feature 319's plan-review case, a missing drawing link landing with every check green). An edit to its Guesses alone
  owes `modal-form` and the research checks, not `modal-depiction`.
- **FR-016 An open feature's state as its session clone holds it.** `make speckit-todo` shows each open feature as a session
  clone it reads (below) holds it when that differs from main - its spec accepted, its plan written, tasks ticked - in the section
  that state belongs to, marked with the clone it is in and that it has not landed. Which clones it reads is decided by a
  measurement (the GM: "you can probably limit yourself to clones with active sessions, if it helps performance"): the
  listing's time reading every clone against reading only the active ones is recorded, and the limit is kept only if it
  helps. Display only: what the push, `make tick` and the closing check read is unchanged.

### Amendment 2 (`request.md`, Amendment 2)

- **FR-017 A batch reaching the round cap together gets one ruling.** When several units are owed a round-cap ruling at the
  same time - a batch of pop-ups (or pages) whose checks reached the cap together, as 343's 15 pop-ups did - one command
  builds ONE arbiter bundle covering the batch, each unit with its own rounds and edits, and the round arbiter returns ONE
  ruling for the batch with an exception for any unit it rules differently. The batch is every round trigger owed at the time
  (a spec review's own rounds excepted - one spec, ruled alone), plus any round the session names that it is asking about
  ahead of its cap (FR-018's case, as 343's 13 form checks were); an unrelated unit in it is the arbiter's to except.
  Recording the ruling records each trigger's (the batch's, or its exception), so every hold, closure and GM-review row works
  per unit as before. The tooling steers to it: while more than one round trigger of a batch is owed, the refusal names the
  batch command, and a single trigger's ruling is refused, pointing to the batch; a unit is ruled alone only when no other
  trigger of its batch is owed.
- **FR-018 A round trigger's bundle carries its rounds.** An arbiter bundle for a round trigger shows that unit's rounds,
  replies and edits whether or not the guard recorded the trigger as owed (the unit is read from the trigger itself) - 343's
  session asked ahead for 13 form checks' third round, and each bundle reached the arbiter with no round history.

### Amendment 3 (`request.md`, Amendment 3)

The GM asked for three things after the measurement in `request.md`: the pop-up checks' structural cause of round-3 caps
fixed, as a speculative fix measured afterwards; `modal-bundle`, `check-bundle`, `claims-owed` and `record-owed` made fast;
`hooks-test` skipping what a change did not touch. The timing requirements are not part of it (the GM: "let's talk about
that after you make the other changes").

- **FR-019 A pop-up's checks run in order, and a round's applied edits settle the checks before it.** The structural cause,
  measured on 374's and 352's clones (`research.md` R2): a pop-up's three checks run together, each proposes edits, and the edits
  applied re-owe the other two - every second and third round there was owed because the pop-up itself had changed, and
  `modal-form` proposed edits in nearly every second round in the research clone, re-owing the other two. (In 374 most
  second rounds were `modal-depiction`'s, 19 of 29 units, and 13 of those 19 pop-ups had no other check at all: owed by the
  pop-up's own words changing, which ordering does not reach and feature 335's settling of a check's own edits may.) A check is already not re-owed by its OWN applied edits (feature 335: `make apply-edits` settles the reply's
  own units). Now:
  (a) A pop-up's checks run in one order: `modal-form` (its words and their order), then `modal-research` (whether those
  words are supported), then `modal-depiction` (whether the Depiction tab tells the drawing, read last because the research
  round may move a drawing statement). A check's bundle for a pop-up is refused while a check before it in the order is owed
  on that pop-up and unanswered, the refusal naming that check's bundle command. An escape, `CHECK_ORDER_OK="<why>"`, builds
  it anyway and is recorded in the bundle's MANIFEST. A check owed nothing before it (a page only its `Drawing:` names
  moved, say) is not held: the order is read off what is owed, never off the check asked for.
  (b) When a round's own EDIT blocks are applied, each check BEFORE the replying check in the order settles with its answer
  as the replying check's own units do - where that check was answered at the words before those blocks and the blocks alone
  moved them. A unit changed any other way stays owed.
  (c) A round's blocks settle nothing of a check AFTER the replying one: that check reads the edited words next.
  This is the speculative fix the GM asked for, ordering all three checks; SC-012 measures it on the next pop-up rounds.
- **FR-020 The record tooling's shared cost is paid once per content.** The four commands spend most of their time in the
  same work, measured on 374's delta (`request.md`): re-reading the whole record at the merge base and at the working tree
  on every call (about 1.7 s of parsing), one `git` process per file for the pop-ups and the entry-drift classes at the base
  (299 and 177 processes; the two stages took 1.25 s and 0.76 s), and re-parsing every engine module for the research
  claims (the `all_units` stage, 7.29 s timed in-process on a loaded container - more than `claims-owed`'s whole 6.9 s
  run earlier; `m:375-a3-record-tooling-before`, `research.md` R1). Now:
  (a) a question page's, notes file's or write-up's parse is kept by its content and by the source of the code that parses
  it - the parsing module and every project module it imports, transitively - so an unchanged file is parsed once, not
  once per call and per revision;
  (b) a revision's files are read in one `git` batch, never one process per file;
  (c) the engine's research claims are kept by the content of every engine module and procedure document they are read from
  and the source of the claim readers and every project module they import, transitively;
  (d) a command builds only what it prints (a pop-up's bundle computes that pop-up's owed lines, not the whole delta's,
  where its result is the same).
  A cache never changes an answer: any change to a file or to the code that reads it misses, and each command's output is
  the same with and without it.
- **FR-021 `hooks-test` runs only what a change touched.** Measured (`m:375-a3-hooks-test-before`, `research.md` R3): the
  guard suites already run only when a file they depend on changed (feature 172), but the Python test files that test
  `scripts/` run all together (74 s) whenever anything under `scripts/` or `tests/hooks/` changed, so a merge from main
  touching one script reran every one of them. Each now runs only when it, a `conftest.py` above it, or a file it depends on
  changed: the scripts it names and what those use, derived transitively as the guard suites' dependencies are
  (`tests/hooks/hookdeps.py`), and all of `scripts/` for a file whose script paths cannot be derived (it builds them at run
  time). Failing toward running, as feature 172's derivation does. `HOOKS_ALL=1` and the gate (which runs these files
  anyway) are unchanged.

### Amendment 4 (`request.md`, Amendment 4)

- **FR-022 The longest guard suite runs its cases in parallel parts.** `test-sync-with-main.sh` stays held to the whole tree
  (FR-021 and feature 172: no static reading sees which scripts its push path reaches), so every script change re-runs it,
  and it is the long pole of a parallel `hooks-test`: 230 s run alone, 202 s with its cases timed one by one, the longest
  66 s (`m:375-a3-hooks-test-before`, `research.md` R3). It has 26 headed cases (25 numbered - 11 and 12 each used twice -
  and `W`; the roll-cache block runs inside the case before it), and each builds its own fixture; the helpers several share
  (`yes_`, `no_`, `rref`, `in_progress`) are defined once before the cases. Now the cases run in parallel parts, each
  part with its own temporary directory, `HOME` and guard log, so the suite takes about its longest part's time. Every check
  still runs and is counted - the suite prints the same pass line with the same count as today's - and a failure in any
  part, or a case that never reports, fails the suite. `SYNC_PARTS=1` runs the cases one after another.

### Amendment 5 (`request.md`, Amendment 5)

The GM's answers on the timing requirements (`request.md`), the last superseding the first where they differ: performance is
recorded and flagged, never a gate. The cohort is not part of it.

- **FR-023 Performance is recorded and flagged, never a gate.** The bookends are taken and kept as before (`make perf
  LABEL=<NNN>-start` / `-end`, one file each under `dev/perf-log/`), and the bands are still computed and printed - by
  `make perf-report`, by `perf-gate` and at the push - but none of them refuses anything: no push, no gate and no `make
  tick` waits on a band, and the band records (`perf-explain`, `perf-confirm`, `perf-audit`, `perf-arbiter`, `perf-signoff`)
  are no longer owed. They stay available for an investigation the GM or a session chooses. Where a pair crosses the
  band-1 line, the push prints a FLAG naming the seeds and percentages and the machine's state at both ends of both
  snapshots, with the caveat that load may explain it, and the session says so in the message that reports the landing.
- **FR-024 Each snapshot records the machine's state at its start and its end.** Available and total RAM
  (`/proc/meminfo`), the load averages over 1, 5 and 15 minutes, and the free and total disk on the clone's filesystem - a
  reading before the first roll and one after the last, nothing during the run. Each stage is also timed in CPU time
  (`time.process_time()`) beside its wall time, and an untimed warm-up roll comes first (measured, the first roll in a process
  counts another thread's start-up work as its own: 6.26 s of CPU in 4.47 s of wall, `research.md` R4). Bands and the flag
  read the CPU seconds where both snapshots have them, the wall seconds otherwise, and say which.
- **FR-025 The band-1 line is 5%, in every environment.** The GM: "let's extent it from 2% to 5% for the jitter". Locally
  the line was 0.0% and on CodeBuild 2.0%; both become 5.0%, an increase at or under it unflagged. Bands 2 and 3 keep their
  lines as labels of how much slower a pair looks.
- **FR-026 The scaling leg runs only when asked for.** `make perf` rolls the reference hamlet at its 15 households on its four
  seeds, nothing more. `make perf SCALING=1` adds the 10-, 20- and 40-household legs, for investigating the algorithm; a
  pair is banded on the legs only where both snapshots carry them, as today.
- **FR-027 The trend says when.** `make perf-report` lists every snapshot - its time, label, commit, totals - with the load
  and free RAM at its start and end beside it, so a run taken under load reads as one, and a real slowdown can be placed
  between two snapshots and so between two commits.
- Every text that states the gate says what FR-023 says - the set a grep over the always-loaded and on-demand docs finds
  (`perf-audit|perf bands|band-1|perf_review.py --check|blocks as a regression|perf-arbiter`): constitution principle VI,
  the root `CLAUDE.md` (the push row and the gate row of the guards table), `l7r/diagram/CLAUDE.md`, `dev/performance.md`,
  `docs/guards.md`, `docs/efficiency-tooling.md`, `scripts/container/append-system-prompt.md` (its standing order to run
  `perf-audit` on every band of 1 or more), `.claude/agents/perf-audit.md` and `.claude/agents/round-arbiter.md`.

### Amendment 6 (`request.md`, Amendment 6)

The GM approved dropping About from what owes `modal-depiction`: FR-015 put it there in the session's words, not the GM's.

- **FR-028 About no longer owes `modal-depiction`.** An edit to a pop-up owes `modal-depiction` only when it changes what that
  check judges: the pop-up new to the About form, or its Depiction tab, its `Drawing:` list or its `Entry:`
  (FR-015's other triggers, unchanged). An edit to its About alone - or to About and Guesses - owes `modal-form` and the research
  checks, not `modal-depiction`, and so adds no round to `modal-depiction`'s count on that pop-up (a round is counted per
  dispatch, and a check not owed is not dispatched). `modal-depiction` reports nothing from About: the About side of M13 (a
  sentence about how the map draws the thing, found in About) is `modal-form`'s finding alone, and the move of that sentence
  to the Depiction tab owes `modal-depiction` in its turn. The depiction fingerprint (`scripts/record/modal_owed.py`
  `depiction_fingerprint`) drops About, and `modal-depiction`'s contract its M13 About sentence. The change re-owes nothing by
  itself: a depiction answer recorded under FR-015's formula stands where what FR-028 still counts - the Depiction tab,
  `Drawing:`, `Entry:` and the drawing pages - is unchanged since it was recorded. Feature 343's rows 83 and 84 (the two
  declined fixes, overturned into this feature's `found.jsonl`) close with it on their About part; their Guesses, Name and
  Form part was built under amendment 1 (c9999e64e), and row 83's `Covers` is not a line `modal-depiction` reads.

### Amendment 7 (`request.md`, Amendment 7)

The GM's first four (2, 3, 6, 8) and the measurement of the fifth (1); amendment 8 takes the rest.

- **FR-029 The cohort rolls only what changed.** `make cohort` rolled every seed through `generate` on every run, so a
  feature's "before" leg rolled unchanged code again each wave and its "after" leg re-rolled seeds the change never reached:
  109 minutes of 374's tool time, six seeds at a time on one worker under the memory cap (`m:375-a7-cohort-cost`,
  `research.md` R5). Now each cohort seed is served from the roll cache (`pipeline/rollcache.py`, keyed by the
  engine functions the roll executed and the files it read, path-independent since feature 167) when nothing it executes
  changed, and rolled otherwise; the cohort's own checks still run on every seed's report, served or rolled. The "before"
  leg, rolled in a detached worktree at the merge base, reads and writes the same store as the clone, so a second wave's
  "before" leg rolls nothing. And each cohort run writes a structured record - per seed: served or rolled, its verdict, the
  failures it found, the engine commit - under `dev/cohort-log/`, one file a run, so that whether fewer seeds would find the
  same failures can be counted. No such record exists today (374's findings by seed are in its plan's prose), so the seed
  count is decided in amendment 8, put to the GM with that record.
- **FR-030 The overlap census runs when asked for.** `make perf` ran `make census` after every snapshot - 74 s of its 97 s,
  measured 2026-10-12 (`research.md` R5) - because feature 306 made it "a standing check run beside `make perf`" (its FR-006,
  from its review round 1). Nothing reads its output. `make census` runs it; `make perf` no longer does.
- **FR-031 The next three guard suites run in parallel parts where their cases are independent.** After a script change
  `hooks-test` now waits on `test-pair-hooks.sh` (82 s), `test-batching-hooks.sh` (72 s) and `test-entry-gate.sh` (67 s)
  (`m:375-a3-hooks-test-before`, R3). Each is split into parallel parts as `test-sync-with-main.sh` was (FR-022): each part with
  its own temporary directory, `HOME` and guard log, every check still run and counted, today's pass count printed, a failed
  or unreported case failing the suite. Where a suite's cases depend on an earlier case's state, it splits only at the
  boundaries a measured scan finds, or stays serial, and the plan says which, with the scan's result.
- **FR-032 The gate's shortcut does not leave the push a gate short.** `make done`'s "already verified" shortcut checks only
  the engine content's record and re-stamps only the `diagram` area, so after a change under `scripts/` alone it answered
  green while the push's green-gate check refused on the `hooks` area (measured 2026-10-12, landing `impl_check.py`'s fix).
  Now the shortcut runs `make hooks-test` when the `hooks` stamp is stale and is green only if that is.
- **FR-033 The gate's run record does not refuse the landing.** Every `make done` writes a record under `dev/run-log/`, a
  tracked file, and `sync-with-main.sh done` refuses an uncommitted tree - so each landing after a gate cost a commit by hand
  and a second try. `sync-with-main.sh` itself says "the procedure never writes your commit for you". The record is the
  gate's, not the session's work: `make done` commits its own record, that one path alone, as `the gate's run record
  (<result>)`, and stages nothing else.
- **FR-034 Model time against context size, measured.** From 374's transcript (`research.md` R5): 1,385 turns, 1.9 hours of
  model time from each tool result to the next reply; per turn about 1.6 s fixed, 0.25 s per 100,000 tokens of context and
  3.3 s per 1,000 tokens written - context size accounted for about half an hour in all. (The 6.5 hours the session first
  put to the GM counted the waits on background runs and on the GM as model time.) Recorded; nothing is built for it.

### Amendment 8 (`request.md`, Amendment 8)

Amendment 7's items 4, 5 and 7, and the cohort's seed count it carried. Items 7 and the seed count are the GM's to choose; this
amendment builds what puts each before him with the data.

- **FR-035 The claims are cached per module.** `make claims-owed`, `claims-report` and every reader of `scripts/record/claims.py`'s
  units read them from one cache keyed by every engine source together (amendment 3, plan D29), so one engine edit - a comment
  - recomputed all of them: 11.9 s against 1.0 s warm, measured 2026-10-12 (`m:375-a8-claims-cold`, `research.md` R7). Each
  module's units are now kept by what they are computed from - the module's own source and what it reads of the others'
  constants - so an edit recomputes only the units it can change, and the result is the one an uncached run gives.
- **FR-036 A check bundle does not redo the record's work.** `make check-bundle Q=` took 6.1 s warm (15.2 s cold, the page
  cache filling; `m:375-a8-check-bundle`, R7). Timed by phase: `record_prepass` 3.2 s, nearly all of it recounting the whole
  record's word frequencies (`corpus_frequency`, 2.96 s under the profiler), `quote_verbatim` 0.46 s, the other git reads
  1.1 s, and the bundle's own owed check 1.3 s, the translation pairs among it (0.9 s). Starting a helper's interpreter and its
  imports is about 0.09 s each (0.35 s for four). The word frequencies and the translation pairs are kept by the content they
  read - the record's pages, and a revision's tree - and reused while that is unchanged; the bundle's files are the ones an
  uncached run writes. This builds the goal of the GM's item 5 ("check-bundle in-process") rather than its letter: folding the
  helpers into one process saves their start, about 0.2 s of a 6.1 s bundle, where caching was predicted to save about
  3.7 s and, measured old against new at one load, saved about 1 s: 3.7 s to 2.8 s (`m:375-a8-check-bundle-after`, R7 - the
  profiler had inflated the word count's share, and the 6.1 s was taken at load 6) (Decisions Recorded; the GM confirmed it, 2026-10-12: "I confirm the check-bundle thing is good as you've done it").
- **FR-037 The review checks' yield, put to the GM.** A kept command prints, per review check from `dev/review-ledger.md`: its
  passes, the findings acted on (fixed, filed) and those dismissed (verified as fine, accepted, declined), the findings its
  author had missed, its hours and tokens - over a period and across the features in it. The session puts that table to the GM
  with the checks whose yield is lowest for their cost; no check is changed, dropped or moved to another tier here: that is
  the GM's choice, and a change he makes is its own amendment or feature in his words.
- **FR-038 The cohort's seed count, from its record.** A kept command reads `dev/cohort-log/` and prints, per failure the
  cohort found, the seeds that found it and the features' changes they were rolled on, how many changes the records span, and
  the fewest first seeds that would have found every failure. Put to the GM - one change, the first ten seeds finding every
  failure - he chose ten (2026-10-12: "it's also fine to do the 10 seeds"): `make cohort` rolls the first ten seeds and the six
  pinned rows by default, where it rolled 48; `N=` still asks for more. The command stays, for the next look at the count.

### Amendment 9 (`request.md`, Amendment 9)

`glyph-check` run on the hour, the GM's sketch made the rule.

- **FR-039 A glyph check is due on the hour, not on each occasion.** Its occasions are found as today (`review_owed.py`: an
  element new to a map or sheet, a glyph redrawn, an element re-placed) and kept as owed, but an owed glyph unit is DUE - so
  that the pair guard and the stop hook ask for its dispatch - only when an hour of the FEATURE's time has passed: counted
  from the feature's start in the clone (its first event there), and from each glyph dispatch made for it after that - a
  dispatch from before the feature began never makes one of its units due - or when the work lands. A change made directly,
  with no feature, owes its glyph units at landing. Then every
  glyph unit owed at that moment is due together and is dispatched together, one unit per agent as feature 248 has it, and
  their findings are fixed together; a fix that redraws or re-places an element owes that element again, which comes due on
  the next hour or at landing. So a feature that runs past an hour checks its glyphs once an hour, on what the map is by then,
  and a feature that lands inside its first hour checks them once, at landing. The landing still owes every glyph unit an
  answer (`review-gate.sh`, as today). Measured on the ledger since 2026-09-26 (R8): 158 glyph-check passes, 124 of them PASS,
  46 a second round or later - a check run after each wave and again after each fix.
- **FR-040 The hour is visible, and kept.** `make verify` and the stop hook's message name the glyph units owed but not yet due
  and when they come due, so a session knows what is waiting; and the pair guard refuses a glyph-check dispatch before its unit
  is due (the escape, as every guard's, takes a reason), so a session does not slip back into checking after each wave.
- **FR-041 Only `glyph-check`.** The other review checks (`settlement-review`, `building-review`, `size-audit`, `fix-check`) are
  owed on their occasions as today.


## Success criteria

- **SC-001** (FR-001, FR-002, FR-006) Replaying feature 372's recorded deltas for waves 106, 108 and 111 through the new owing logic: modal-depiction
  units owed fall by at least two thirds, impl-drift claims owed by at least four fifths, against the counts above.
- **SC-002** (spec-wide: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014) Each FR has a test that fails with the old behavior and passes with the new, run by `make hooks-test` or the gate.
- **SC-003** (FR-003, FR-004; carried to 374) In feature 374's first three tasks: no red gate from a cause FR-004's preflight checks, no page
  re-checked while a check on it was outstanding, and no plan-review BLOCK on a decision the decision preflight had ruled on.
  `Carried: SC-003 -> 374 sc003-375-first-three-tasks`.
- **SC-004** (FR-001, FR-002, FR-003; carried to 374) The dispatches per closed row of feature 374's first three tasks, recorded beside 372's (~10 per
  row). `Carried: SC-004 -> 374 sc004-375-dispatches-per-row`.
- **SC-005** (FR-008, FR-009) `make feature-report` runs in under ten seconds on feature 372's record and on a one-task feature, and reproduces
  this spec's measured table within its stated rounding.
- **SC-006** (FR-010, FR-011, FR-012) Replaying 372's waves 106 and 108: the tripwires fire on 0105's and 0100's third rounds and on the bath bullet's
  A -> B -> A, and no round past the cap needed a GM waiver.
- **SC-007** (FR-015) Replaying feature 343's kept triage (61 units, its reply restated with the page each quoted block stands
  on): `modal-depiction` of `sheet/main-gate` and `sheet/residence` (named only for question-page blocks) and the research
  units of `sheet/door`, `sheet/guest-quarters` and `sheet/side-gate` (named only for drawing-page blocks) are not owed; every
  other named unit, `sheet/nakamon`, `sheet/garden` and `sheet/genkan`'s depiction among them, is. An edit to a pop-up's
  Guesses alone owes `modal-form` and the research checks but not `modal-depiction`; an edit to its About, `Entry:`, Depiction
  tab or `Drawing:` list, or a pop-up new to the About form, still owes it (its About clause SUPERSEDED by SC-021,
  amendment 6). The tests fail on today's code.
- **SC-008** (FR-016) With a fixture main and session clones, one holding a feature's accepted spec and ticked tasks: `make
  speckit-todo` lists that feature in the clone's section, marked with its clone and not landed, and a clone holding the
  same files as main adds nothing; if the measurement keeps the active-only limit, an inactive clone's change is not shown.
  `--holding`, `--closed-by-status` and `CHECK=1` give what they gave before. The measurement is a key of
  `measurements.json`.
- **SC-009** (FR-017) In 343's shape - several pop-ups at the cap on more than one check, one round asked about ahead and named
  to join: one bundle carries them all (the asked-ahead one included, a spec review's round not), each with its rounds; one
  batch ruling with one exception records every trigger - the exception's unit under its own ruling, the rest under the
  batch's - each releasing its own hold and adding its GM-review row; meanwhile the refusal names the batch command, and a
  single trigger's ruling is refused, pointing to it. The tests fail on today's code.
- **SC-010** (FR-018) A bundle for a round trigger the guard never recorded as owed carries that unit's rounds (replaying the
  shape of 343's form-check bundles). The test fails on today's code.
- **SC-011** (FR-019) On a fixture pop-up owed all three checks: a `modal-research` bundle is refused while `modal-form` is
  unanswered, and a `modal-depiction` bundle while either is, each refusal naming the bundle command of the check owed first;
  with `CHECK_ORDER_OK` each is built and its MANIFEST says why; a pop-up owed only `modal-depiction` (a page its `Drawing:`
  names moved) is not held. Applying a `modal-research` reply's EDIT blocks leaves `modal-form` answered, and a
  `modal-depiction` reply's leaves both answered; a hand edit after either re-owes them; a `modal-form` reply's blocks
  applied after `modal-research` answered leave `modal-research` owed. The tests fail on today's code.
- **SC-012** (FR-019; carried to 374) The pop-up check dispatches per checked unit on the next pop-up rounds, counted by the
  same script as the baseline (`scripts/measure/popup_rounds.py` over a clone's kept dispatch records;
  `m:375-a3-popup-rounds-before`, R2): 374's clone 71 dispatches over 34 units (2.09; 29 units with a second round, 4 with a
  third), the research clone's 169 over 82 (2.06; 70 and 11). The fix WORKED if dispatches per unit fall below 1.5 and at
  most one unit in twenty reaches a third round (the baseline's 4 of 34 and 11 of 82 are about one in eight); it HELPED if
  either falls but not both that far; it FAILED if neither falls below the baseline.
  `Carried: SC-012 -> 374 sc012-375-a3-popup-rounds`.
- **SC-013** (FR-020) On 374's delta (its pushed HEAD 61a52f3c8 in a detached worktree, its answer store copied), the four
  commands - `record-owed`, `check-bundle Q=0190` (`NO_QUOTES=1`), `modal-bundle KIND=hamlet/notice-board
  FOR=modal-depiction`, `claims-owed` - timed back to back with today's code and the new, alternating, three runs each, the
  load recorded at both ends (one run each before the change: 6.0 s, 6.0 s, 6.7 s and 6.9 s, R1): each new median with the
  caches warm at most half today's median, and no new cold median above today's; each command's output byte-identical with
  and without the caches. A test per cache shows a changed file and a changed reading module (an imported one too) each
  miss. The times are a key of `measurements.json`.
- **SC-014** (FR-021) With a fixture: a change to one script runs only the test files that depend on it, a file that builds
  its script paths runs on any change under `scripts/`, an unchanged tree runs none, and `HOOKS_ALL=1` runs them all. Measured
  over main's last ten commits touching `scripts/`: the test files each would have run, against all of them today - a key of
  `measurements.json` beside `m:375-a3-hooks-test-before` (R3).

- **SC-015** (FR-022) Today's `test-sync-with-main.sh` (at bfe25f2da, the commit before the change, in a detached worktree)
  and the new one in parts, timed alternately, three runs each, the load recorded: the new median at most half today's, and
  every run of either passing exactly today's count of checks (123 at bfe25f2da). Five runs in parts in a row all green with
  that count, and one with `SYNC_PARTS=1` with it too. With one case made to fail, the suite fails and names the check; with
  one case made to exit before reporting, the suite fails and names the case. Keys of `measurements.json` beside
  `m:375-a3-hooks-test-before` (R3).

- **SC-016** (FR-023) A pair in band 3 (and one in band 1) no longer refuses the push, `perf-gate` or `make tick`: `perf-review
  --check` exits 0 and prints the FLAG with the seeds, percentages and both ends' machine state; with no band, no flag. The
  tests fail on today's code.
- **SC-017** (FR-024) A snapshot carries `machine_before` and `machine_after` (available and total RAM, three load averages,
  free and total disk) and each stage's CPU seconds beside its wall seconds, after an untimed warm-up roll; a pair is banded on
  CPU seconds where both have them, on wall seconds otherwise, the report naming which. The wall-against-CPU measurement
  that led here is `research.md` R4, a key of `measurements.json`. Tests fail on today's code.
- **SC-018** (FR-025) A test pair whose total and every seed rose 5 percent is unflagged, in both environments; one seed at 5.1
  percent is flagged band 1. The test fails on today's code (0 and 2 percent lines).
- **SC-019** (FR-026) `make perf` without `SCALING=1` records no scaling rows (four rolls and the warm-up, not sixteen); with
  it, the legs as today. Tests fail on today's code.
- **SC-020** (FR-027) `make perf-report` prints each snapshot's start and end load and free RAM beside its totals; a snapshot
  from before FR-024 prints dashes there. The test fails on today's code.

- **SC-021** (FR-028) A pop-up whose About alone changed is owed `modal-form` and not `modal-depiction`; one whose Depiction,
  `Drawing:` or `Entry:` changed is owed `modal-depiction` as today; a depiction answer recorded under FR-015's formula still
  answers its pop-up after an About edit, and not after an `Entry:` edit; an About-only edit between two depiction rounds adds
  no round on that pop-up; a `modal-form` bundle carries M13's About rule. Replaying the About-only pop-up edits since
  2026-10-05 - 43 of 221 by the kept replay at the reopening commit - owes no `modal-depiction` (`m:375-a6-about-only-replay`,
  `research.md` R6). The owing tests (the About edit, the
  recorded answer, the round count) fail on today's code; the `modal-form` bundle's already passes.
- **SC-022** (FR-029) A cohort run writes its per-seed record (served or rolled, verdict, failures, commit); a cohort run twice
  on unchanged code rolls nothing the second time; after a change to one stage's
  code, only the seeds whose rolls executed it roll again; each seed's verdict served equals its verdict rolled fresh
  (`GATE_NO_CACHE=1`); a "before" leg in a detached worktree after a clone's own run of the same base rolls nothing. The
  cohort's time before and after on 374's delta, two waves, is a key of `measurements.json` (R1, R5). Tests fail on today's
  code.
- **SC-023** (FR-030) `make perf` runs no census; `make census` runs it as before. The test fails on today's code.
- **SC-024** (FR-031) Each of the three suites, today's file against the new in parts, alternating, three runs each: every
  run passes today's count of checks; a suite split has its median at most half today's. A suite split or left serial
  carries its scan's result: each case run alone in a fresh process, and for each that fails alone the shortest run of its
  predecessors that passes - a chain kept in order in one part; a suite left serial names the dependence that keeps it so. A forced
  failure and a case that exits early each fail a split suite, named. Keys of `measurements.json` beside
  `m:375-a3-hooks-test-before` (R3).
- **SC-025** (FR-032) After a change under `scripts/` alone, with the engine's record green, `make done` runs `hooks-test`
  and stamps `hooks`, and the push's green-gate check passes; with nothing changed it runs nothing. The test fails on today's
  code.
- **SC-026** (FR-033) After `make done`, the tree is clean except for what the session left, and the record is committed
  alone with its message; a staged change of the session's is left staged and uncommitted. The test fails on today's code.
- **SC-027** (FR-034) R5's figures are a key of `measurements.json`, re-derivable by a kept script from the transcript.
- **SC-028** (FR-035) After a one-line edit to one engine module, `make claims-owed` takes at most twice its warm time, and the
  units it reads equal an uncached run's; an edit to a module-level constant another module reads recomputes that module too.
  The time before and after is a key of `measurements.json` (R7). Tests fail on today's code.
- **SC-029** (FR-036) `make check-bundle Q=` on a second question after a first, alternating today's code and the new, three
  runs each, is measured and recorded (`m:375-a8-check-bundle-after`, R7). The bar first written here - at most half of today's
  6.1 s - came from the profile's prediction of about 3.7 s saved, and the 6.1 s was taken at load 6; the alternating run gave
  3.7 s to 2.8 s at one load, about 25% saved, so the half was NOT met and the result stands as measured; the bundle's files equal an uncached run's; an edit to a record page makes the next
  bundle recount. Tests fail on today's code.
- **SC-030** (FR-037) The yield command prints the table FR-037 names over the ledger since 2026-09-26, its rows re-derivable
  from the ledger; the table is a key of `measurements.json`, and the GM is given it.
- **SC-031** (FR-038) The seed command prints, over today's records, the failures found (seeds 10 and 20, `WebRefused`) and that
  the records span one feature's change; a test with records from three changes names the fewest first seeds that find every
  failure. `make cohort` with no `N=` rolls seeds 1 to 10 and the six pinned rows. The test fails on today's code.
- **SC-032** (FR-039) In a fixture clone with a glyph unit owed: before the hour it is owed and not due (the pair guard and the
  stop hook ask for nothing); at the feature's hour, or at landing, every glyph unit then owed is due; after a glyph dispatch
  the clock restarts, and a unit owed again by a fix waits for the next hour; a clone whose last glyph dispatch was more than
  an hour before the feature began does not make the feature's first unit due before the feature's first hour; a change with no
  feature owes its units at landing; the push refuses a glyph unit with no answer, as today. Tests fail on today's code.
- **SC-033** (FR-040) `make verify` prints each glyph unit waiting and the time it comes due; the pair guard refuses a glyph
  dispatch before its unit is due, and passes it with the escape and a reason. Tests fail on today's code.
- **SC-034** (FR-041) A settlement-review, building-review, size-audit or fix-check unit is due as soon as it is owed, as today.
  Measured after: glyph-check passes per hour of a long feature, from the ledger and the event log, against R8's figures.
  `Carried: SC-034 -> 374 sc034-375-a9-glyph-per-hour` (374, the open long feature with map work, measures it).

375 closes on SC-001, SC-002, SC-005 and SC-006; SC-003 and SC-004 are held open in 374 by FR-014, since 374 takes no task
until 375 has landed. Amendment 3 closes on SC-011, SC-013 and SC-014; SC-012 needs pop-up rounds run under it, which 374's
next wave is, so it is carried there. Amendment 4 closes on SC-015. Amendment 5 closes on SC-016 to SC-020. Amendment 6 closes on SC-021. Amendment 7 closes on SC-022 to SC-027. Amendment 8 closes on SC-028 to SC-031. Amendment 9 closes on SC-032 to SC-034.

## What it does not cover

- Judgment errors inside a decision (wave 108's back-and-forth over Hayakawa's bath was the session's own oscillation). FR-003(a)
  puts the decision to spec-fidelity before the edits and FR-010's oscillation tripwire catches the reversal, which bounds the
  cost, but neither can make the first decision right.
- Escape variables remain. Every guard keeps its named escape (`*_OK="<reason>"`), each use logged to `dev/bypass-log/` and
  `make audit`, so a slide back is visible, not prevented.
- The size of the remaining rows: 153 E3 and 43 E4 rows are real redraws and research passes; this feature makes each cheaper,
  not fewer.
- The cohort's cost (amendment 5): reusing its "before" leg per main commit, or rolling fewer seeds, was offered to the GM as
  a measurement and is not part of amendment 5, which settled the timing requirements.
- The cohort's seed count (amendment 7): decided in amendment 8, with the per-seed record FR-029 starts keeping; the claims'
  per-module cache, `check-bundle` (built as its record work cached - Decisions Recorded) and the review checks' yield are
  amendment 8's too.
- Amendment 8 changes no review check: FR-037 puts the table to the GM ("I'll look at the table when you have it"), and a
  change he chooses is its own amendment or feature. The seed count is his ten (FR-038). `check-bundle`'s helpers stay separate processes - see Decisions Recorded, "check-bundle's record work
  cached (amendment 8)".

## Decisions Recorded

| decision | class | why |
|---|---|---|
| Enforcement over guidance throughout | this project's decision | the GM, 2026-10-10 (`request.md`); 328's retrospective, held only as intentions, slid back within a day |
| One feature for enforcement, measurement and escalation | this project's decision | the GM, 2026-10-10: "all part of one feature because conceptually this is all under the same umbrella" |
| A round arbiter in place of the GM's waiver; the GM reviews after landing | this project's decision | the GM, 2026-10-10: progress should not stop at a round cap; the GM wants features to land without waiting on review |
| The unit of work a check belongs to is a task, never a wave | spec-fidelity round 1, 2026-10-10 | a feature without waves has tasks; 372's waves were each one task |
| SC-003 and SC-004 carried to 374 and held there by FR-014 | spec-fidelity round 1, 2026-10-10 | 374 takes no task until 375 lands, and a feature with an open task lands nothing: keeping 375 open for them would stall both |
| Tripwires on events, not an hourly timer | this project's decision | a pattern is caught when it happens; a timer fires mid-action and asks the looping session to judge itself |
| The order form, research, depiction (amendment 3) | this project's decision, on the GM's "order the checks" (review round 1 offered it and the session took it) | form first: a form edit can carry a fact (374's residence-corridor round 2 had `modal-research` catch a comparison modal-form's rewording introduced), so the substance checks read form's words. Depiction last: it reads About for drawing statements, which a research round may move. Ordering only form left research and depiction re-owing each other, the same cause on two checks (the review's item 1) |
| Ordering on the pop-ups, not a fourth round's cap or a merged check (amendment 3) | the GM, 2026-10-11 | the GM asked for the speculative fix and a measurement after it ("perhaps it's worth trying to make the speculative fix and measuring it afterwards"); the three checks keep their own contracts |
| Caches keyed by content and by the reading code's own source, never by time (amendment 3) | this project's decision | a cache that outlives a change to its reader serves the old answer; keyed so, a fix to the parser is a miss, and an unchanged file is never read twice |
| `check-bundle`'s record work cached, its helpers left as processes (amendment 8, FR-036) | a deviation from the letter of the GM's approval, under his standing "goal over directions"; the GM confirmed it, 2026-10-12: "I confirm the check-bundle thing is good as you've done it" | approved: "check-bundle in-process" (the session's own sketch). Measured (`m:375-a8-check-bundle`, `research.md` R7): the helpers' start is about 0.2 s of a 6.1 s bundle, the recomputed word frequencies and translation pairs predicted at about 3.7 s - measured after at one load, the cache saved about 1 s (3.7 s to 2.8 s, `m:375-a8-check-bundle-after`), still five times the helpers' start. Built: the cache. The measured figure goes to the GM at landing, with FR-037's table, and a `make accept` row carries it to `make gm-review`. Folding the helpers in as well is not ruled out by the measurement - it was left out for its cost (about 0.2 s saved) against the work, and is the GM's to ask for |

## Review history

- Round 1 (spec-fidelity, 2026-10-10): CHANGES REQUIRED - seven items: FR-003(b) against (c); FR-005(b) let a new decision keep
  an old verdict; "a change" undefined (now a task); SC-003/SC-004 held by tooling (FR-014); the GM's box only where owed;
  FR-009 on every closing route; the escape-variable limit and the escalation row.
- Round 2 (spec-fidelity, verify, 2026-10-10): FAITHFUL - all seven resolved; FR-014 faithful as the enforcement of the GM's
  rule. Asides taken: request.md's framing count; "the unit" of FR-011 is the checked thing (a page, pop-up, sheet, spec or
  plan), not the task; 374's measuring tasks do not count among its first three.
- Lint-only edit after round 2 (2026-10-10, no requirement changed): each success criterion names the FRs it measures, as
  `spec-lint` asks; SC-002 names all fourteen.
- spec-fidelity, amendment 1 round 1 (2026-10-10, the counter reset): CHANGES REQUIRED. Applied: `modal-depiction` stays owed
  by an About or `Entry:` edit (it reads both; feature 319's case), only a Guesses-only edit dropped; FR-016's active-only
  limit is decided by a recorded measurement, as the GM's "if it helps performance" made it; SC-007 names the cleared units by
  uid (the measured leak 11 of 61, each line attributed by where its block stands); this entry.
- spec-fidelity-verify, amendment 1 round 2 (2026-10-11): CHANGES REQUIRED - FR-016's first sentence still said "active". Applied: "a session clone it reads"; plan D22 follows.
- spec-fidelity-verify, amendment 1 round 3 (2026-10-11): FAITHFUL - round 2's item resolved.
- spec-fidelity, amendment 2 round 1 (2026-10-11, the counter reset): CHANGES REQUIRED. Applied: the approval line quotes both
  of the GM's sentences; FR-017 states what a batch is (every owed round trigger but a spec review's, plus rounds named as
  asked ahead) and that the tooling steers to it (the refusal names the batch; a single ruling is refused while its batch is
  owed); SC-009 replays 343's shape and tests the refusal. The aside (a ruling row asked ahead lost its unit) is fixed with
  FR-018's parser.
- spec-fidelity-verify, amendment 2 round 2 (2026-10-11): FAITHFUL - round 1's three items and its aside resolved.
- spec-fidelity, amendment 3 round 1 (2026-10-11, the counter reset): CHANGES REQUIRED. Applied: FR-019 orders all three
  checks (form, research, depiction), each later check's applied edits settling every earlier one, not form alone; SC-012
  says what counts as the fix working and is counted by a kept script; SC-013 times today's code and the new back to back,
  three runs each, with the load; FR-020's claims figure is the timed `all_units` stage; a cache's key covers the reading
  code's imports transitively; R2 reconciles the "about 20" put to the GM.
- spec-fidelity-verify, amendment 3 round 2 (2026-10-11): CHANGES REQUIRED. Applied: FR-019's 374 sentence says what the
  records show (13 of the 19 pop-ups with a second depiction round had no other check: owed by their own words); the
  `all_units` stage is recorded in `m:375-a3-record-tooling-before` and R1 with its load; the pop-up baseline is counted from
  snapshots kept in `popup-rounds/` by a command `make figures` re-runs; plan D27, D29 and D31 follow FR-020 and SC-013. Also:
  the escape is `CHECK_ORDER_OK` (it lets any check run ahead of the order, not only form); FR-021(b) and SC-014 take on the
  longest guard suite, measured while answering this round (`m:375-a3-hooks-test-before`, R3).
- spec-fidelity-verify, amendment 3 round 3 (2026-10-11): CHANGES REQUIRED - round 2's four items resolved and the escape's
  rename faithful; FR-021(b), running the longest guard suite in parallel parts, was not asked for (the GM asked that
  `hooks-test` skip what a change did not touch; this speeds up a suite that a change DID touch). Applied: FR-021 is the skip
  alone, SC-014 counts files only, plan D32 is removed; the parallel split goes to the GM as a proposal with R3's measurement.
- spec-fidelity-verify, amendment 3 round 4 (2026-10-11): FAITHFUL - round 3's item resolved; plan D30's fuller account of
  the derivation stays within FR-021.
- spec-fidelity, amendment 4 round 1 (2026-10-11, the counter reset): CHANGES REQUIRED. Applied: SC-015 times today's suite
  (bfe25f2da, a detached worktree) against the new one in parts and pins today's count of checks (123) on every run, so a
  split that drops a section fails; the case count is the file's (26 headed cases; the timing table keyed by ordinal), and
  the shared helpers are named. The review's "already red" was a copy run outside a worktree: today's file in its own
  worktree passed its 123 checks (150 s).
- spec-fidelity-verify, amendment 4 round 2 (2026-10-11): FAITHFUL - round 1's two items resolved; today's suite re-run at
  bfe25f2da in its own worktree passed its 123 checks.
- spec-fidelity, amendment 5 round 1 (2026-10-11, the counter reset): CHANGES REQUIRED. Applied: the closing bullet names
  every text that states the gate, found by its grep (the system prompt's standing order to run perf-audit, the root
  CLAUDE.md's rows, docs/efficiency-tooling.md added); "What it does not cover" says the cohort stays out, not the timing;
  SC-018 pins 5 and 5.1 percent.
- spec-fidelity-verify, amendment 5 round 2 (2026-10-11): FAITHFUL - round 1's three items resolved; the wider grep finds no
  other text stating the gate as a rule.
- spec-fidelity, amendment 7 round 1 (2026-10-12, the counter reset): CHANGES REQUIRED. Applied: the cohort's 109 minutes is
  `m:375-a7-cohort-cost`; FR-029 has the cohort keep a per-seed record and carries the seed count to amendment 8 (and "What
  it does not cover" says so); SC-024 asks for the scan's result for any suite split or left serial; turn_time's bands are
  labeled 200k.
- spec-fidelity-verify, amendment 7 round 2 (2026-10-12): FAITHFUL - round 1's items resolved. Aside taken into the plan: the
  cohort's record commits itself as the gate's does, or it brings the uncommitted-tree refusal back.
