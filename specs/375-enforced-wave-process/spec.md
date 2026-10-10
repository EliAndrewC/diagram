# Feature 375: The wave process, enforced by the tooling

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Filed - to be taken before feature 374's first wave
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
fires) and by a replay of 372's recorded deltas (SC-001).

- **FR-001 Content-scoped record-check owing.** A pop-up's checks are owed by a drawing or question page's change only where the
  changed block bears on that pop-up's kind: the owing logic (`scripts/record/modal_owed.py`, "a page its Drawing: names
  moved") runs one cheap triage of the changed blocks against the kinds whose `Drawing:`/`Entry:` name the page - as
  `make claims-triage` already does for claims - and owes only the kinds it names. Untouched kinds are cleared on the record.
- **FR-002 Line-scoped claim re-owing.** A claim is owed impl-drift when its own line or the rule text it sits beside changed,
  not when anything in its section changed; a regenerated table (`make building-programs`) re-owes only the rows whose text
  changed. Everything else in the section goes through one triage (`scripts/record/claims.py`, "code changed").
- **FR-003 Decide, then freeze.** (a) **Decide first**: a wave's record checks, review checks and claim checks are refused at
  dispatch (`check-bundle-hooks.sh`, `pair-hooks.sh`) until its plan section carries a spec-fidelity verdict on the approach
  (a short decision preflight, recorded like a plan verdict). (b) **Freeze while checked**: while any check on a page or modal is
  running or unanswered, an Edit to that page or modal is refused (`record-edit-hooks.sh`), except an edit a returned check
  proposed. (c) **Apply once**: a check on a page is not re-dispatched while another check on the same page is outstanding - all
  of a round's checks return, their edits are applied in one pass, then the page is checked once.
- **FR-004 Pre-gate preflight, inside the gate.** `make done` begins with a phase that takes seconds: regenerate the derived files
  (`building-programs.md`, the glossary, the record build), check research pointers, run spec-lint, and run the quick tests
  with coverage on the engine files the delta changed; it stops there on a failure. The gate refuses to report green when a
  tracked file changed while it ran (it hashes the tree at start and end), naming the file.
- **FR-005 Two tool fixes.** (a) The claims-triage reply parser reads only lines that open with `TOUCHES `. (b) A plan verdict
  survives an edit to `plan.md` outside the wave sections and decision lines it ruled on: the plan gate hashes the ruled
  sections, not the whole file.
- **FR-006 File, don't fix, outside the wave's own words.** A check's finding on a block the wave did not change is reported
  apart (bundles mark which blocks changed); `make record-checked` records it as a found row (`audit/found-*.jsonl`) rather than
  leaving an edit owed, and a later edit to that block in the same wave re-owes nothing beyond it. Fixing it stays possible
  through the found row's own wave.
- **FR-007 The escalation filter owed only for what reaches the GM.** `escalation-hooks.sh` arms on a review only for findings
  left open (not fixed, verified, accepted with a reason or filed as a row); a review whose every finding is disposed of owes no
  escalation-check.

## Success criteria

- **SC-001** Replaying feature 372's recorded deltas for waves 106, 108 and 111 through the new owing logic: modal-depiction
  units owed fall by at least two thirds, impl-drift claims owed by at least four fifths, against the counts above.
- **SC-002** Each FR has a test that fails with the old behavior and passes with the new, run by `make hooks-test` or the gate.
- **SC-003** In the first three waves of feature 374: no red gate from a cause FR-004's preflight checks, no page re-checked
  while a check on it was outstanding, and no plan-review BLOCK on a decision the decision preflight had ruled on.
- **SC-004** The dispatches per closed row of feature 374's first batch are recorded beside 372's (~10 per row) in this
  feature's measurements.

## What it does not cover

- Judgment errors inside a decision (wave 108's back-and-forth over Hayakawa's bath was the session's own oscillation). FR-003(a)
  puts the decision to spec-fidelity before the edits, which bounds the cost, but cannot make the first decision right.
- The size of the remaining rows: 153 E3 and 43 E4 rows are real redraws and research passes; this feature makes each cheaper,
  not fewer.

## Decisions Recorded

| decision | class | why |
|---|---|---|
| Enforcement over guidance throughout | this project's decision | the GM, 2026-10-10 (`request.md`); 328's retrospective, held only as intentions, slid back within a day |
