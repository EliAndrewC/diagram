# Feature 375: An efficient process, enforced and measured by the tooling

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Reopened 2026-10-11 for amendment 3 (amendment 2 landed: spec FAITHFUL round 2, plan CLEAR round 3, every task ticked; SC-009 and SC-010 tested; SC-003 and SC-004 carried to 374)

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
  the check finds drawing statements that belong in Depiction; `Entry:` is where it finds the drawing pages a pop-up should
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
  tab or `Drawing:` list, or a pop-up new to the About form, still owes it. The tests fail on today's code.
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

375 closes on SC-001, SC-002, SC-005 and SC-006; SC-003 and SC-004 are held open in 374 by FR-014, since 374 takes no task
until 375 has landed. Amendment 3 closes on SC-011, SC-013 and SC-014; SC-012 needs pop-up rounds run under it, which 374's
next wave is, so it is carried there.

## What it does not cover

- Judgment errors inside a decision (wave 108's back-and-forth over Hayakawa's bath was the session's own oscillation). FR-003(a)
  puts the decision to spec-fidelity before the edits and FR-010's oscillation tripwire catches the reversal, which bounds the
  cost, but neither can make the first decision right.
- Escape variables remain. Every guard keeps its named escape (`*_OK="<reason>"`), each use logged to `dev/bypass-log/` and
  `make audit`, so a slide back is visible, not prevented.
- The size of the remaining rows: 153 E3 and 43 E4 rows are real redraws and research passes; this feature makes each cheaper,
  not fewer.
- The timing requirements (amendment 3): the timing runs were the largest single cost of 374's tool time (2.5 h of 6.25), and
  the GM will discuss relaxing them once this amendment has landed.

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
