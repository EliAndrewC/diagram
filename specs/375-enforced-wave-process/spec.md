# Feature 375: An efficient process, enforced and measured by the tooling

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Filed - to be taken before feature 374's first wave; it applies to every feature, not to waves alone

**Owed at**: now

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

An earlier retrospective (feature 328's close) named most of these as intentions; none was built into the tooling, and each
slid back. The GM's rule for this feature: **every change is enforced by the tooling - a hook, a gate or the owing logic -
never by a session remembering.**

## Requirements

Each requirement names its enforcement and is proved by a test that fails on the old behavior (constitution: a guard proves it
fires) and by a replay of 372's recorded deltas (SC-001). Thresholds are counted per checked thing (a page, pop-up, sheet, spec
or plan) and per feature - never per "wave", which was feature 372's own way of batching, not a unit every feature has.

- **FR-001 Content-scoped record-check owing.** A pop-up's checks are owed by a drawing or question page's change only where the
  changed block bears on that pop-up's kind: the owing logic (`scripts/record/modal_owed.py`, "a page its Drawing: names
  moved") runs one cheap triage of the changed blocks against the kinds whose `Drawing:`/`Entry:` name the page - as
  `make claims-triage` already does for claims - and owes only the kinds it names. Untouched kinds are cleared on the record.
- **FR-002 Line-scoped claim re-owing.** A claim is owed impl-drift when its own line or the rule text it sits beside changed,
  not when anything in its section changed; a regenerated table (`make building-programs`) re-owes only the rows whose text
  changed. Everything else in the section goes through one triage (`scripts/record/claims.py`, "code changed").
- **FR-003 Decide, then freeze.** (a) **Decide first**: a feature's record checks, review checks and claim checks for a change are
  refused at dispatch (`check-bundle-hooks.sh`, `pair-hooks.sh`) until the plan section for that change carries a spec-fidelity
  verdict on the approach (a short decision preflight, recorded like a plan verdict). (b) **Freeze while checked**: while any check on a page or modal is
  running or unanswered, an Edit to that page or modal is refused (`record-edit-hooks.sh`), except an edit a returned check
  proposed. (c) **Apply once**: a check on a page is not re-dispatched while another check on the same page is outstanding - all
  of a round's checks return, their edits are applied in one pass, then the page is checked once.
- **FR-004 Pre-gate preflight, inside the gate.** `make done` begins with a phase that takes seconds: regenerate the derived files
  (`building-programs.md`, the glossary, the record build), check research pointers, run spec-lint, and run the quick tests
  with coverage on the engine files the delta changed; it stops there on a failure. The gate refuses to report green when a
  tracked file changed while it ran (it hashes the tree at start and end), naming the file.
- **FR-005 Two tool fixes.** (a) The claims-triage reply parser reads only lines that open with `TOUCHES `. (b) A plan verdict
  survives an edit to `plan.md` outside the sections and decision lines it ruled on: the plan gate hashes the ruled
  sections, not the whole file.
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
  diff. Every feature gets one, however small, and its own cost is a row of it. The last `make tick` of a feature refuses until
  its report is written into the feature's directory.
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
  round cap or tripwire. It judges the process, not the work, from a bundle the tooling builds: each round's findings marked new,
  repeated or reversing an earlier fix; the diffs between rounds; the cascade chain (which edit re-owed which checks); the
  oscillation flags; the feature's request and spec. It rules one of: **continue** (one more round, naming what it must look
  at); **accept** (the state stands; what is left is filed as rows or accepted with a reason, and the unit closes); **process
  fault** (a loop, oscillation or disproportionate cascade: the unit stops, the fault is filed as a tooling row, the feature
  goes on elsewhere). One ruling per unit per trigger, binding: the session can neither re-dispatch it for another answer nor
  overrule an accept. Its cost is a row of the feature report.
- **FR-012 Landed, the GM's review after.** A feature lands with one box open: the GM's review. `make gm-review` lists, by
  feature, two kinds: **held** (work on the item cannot go on until the GM decides - today's held rows, absorbed) and **to review**
  (work went on and landed; the GM may overturn: every arbiter ruling and every accepted finding). A feature whose only open item
  is that review reads `Done - GM review pending` in `make speckit-todo`; `make gm-reviewed F=NNN` closes it, and a ruling the GM
  overturns becomes a row of an open feature. The waivers the GM gives in requests (`REVIEW_ROUNDS_OK`) are no longer needed for
  round caps.
- **FR-013 The advisor, told what to watch.** The advisor takes no instructions and runs only when the working session calls it, so
  it is not the monitor; the tripwires and the arbiter are. `CLAUDE.md` names the patterns of FR-010 so an advisor call sees them,
  and the arbiter's bundle is what a session hands it.

## Success criteria

- **SC-001** Replaying feature 372's recorded deltas for waves 106, 108 and 111 through the new owing logic: modal-depiction
  units owed fall by at least two thirds, impl-drift claims owed by at least four fifths, against the counts above.
- **SC-002** Each FR has a test that fails with the old behavior and passes with the new, run by `make hooks-test` or the gate.
- **SC-003** In feature 374's first three changes: no red gate from a cause FR-004's preflight checks, no page re-checked
  while a check on it was outstanding, and no plan-review BLOCK on a decision the decision preflight had ruled on.
- **SC-005** `make feature-report` runs in under ten seconds on feature 372's record and on a one-task feature, and reproduces
  this spec's measured table within its stated rounding.
- **SC-006** Replaying 372's waves 106 and 108: the tripwires fire on 0105's and 0100's third rounds and on the bath bullet's
  A -> B -> A, and no round past the cap needed a GM waiver.
- **SC-004** The dispatches per closed row of feature 374's first batch are recorded beside 372's (~10 per row) in this
  feature's measurements.

## What it does not cover

- Judgment errors inside a decision (wave 108's back-and-forth over Hayakawa's bath was the session's own oscillation). FR-003(a)
  puts the decision to spec-fidelity before the edits and FR-010's oscillation tripwire catches the reversal, which bounds the
  cost, but neither can make the first decision right.
- The size of the remaining rows: 153 E3 and 43 E4 rows are real redraws and research passes; this feature makes each cheaper,
  not fewer.

## Decisions Recorded

| decision | class | why |
|---|---|---|
| Enforcement over guidance throughout | this project's decision | the GM, 2026-10-10 (`request.md`); 328's retrospective, held only as intentions, slid back within a day |
| One feature for enforcement, measurement and escalation | this project's decision | the GM, 2026-10-10: "all part of one feature because conceptually this is all under the same umbrella" |
| A round arbiter in place of the GM's waiver; the GM reviews after landing | this project's decision | the GM, 2026-10-10: progress should not stop at a round cap; the GM wants features to land without waiting on review |
| Tripwires on events, not an hourly timer | this project's decision | a pattern is caught when it happens; a timer fires mid-action and asks the looping session to judge itself |
