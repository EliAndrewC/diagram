# Feature 240 - a review round is not spent on an unverified fix

**Status**: DRAFT, spec-fidelity round 1 CHANGES REQUIRED (all eight applied, see Review history); round 2 pending
**Request**: [`request.md`](request.md), the GM's words verbatim. **Research**: [`research.md`](research.md).
**Peer**: feature 239 (`Diagram (Kuwabata)`) holds the same contract for `spec-fidelity` and spec figures.
The split was agreed between the two sessions and is recorded in `request.md`; this feature touches none of
239's files and consumes 239's `measurements.json` format and its `make figures` re-run rather than
building parallel ones.

## Summary

A `settlement-review` round costs 7 to 25 minutes (`research.md` R1). Feature 230 spent fourteen, and its
last three were largely spent finding defects the previous round's fix had introduced. The GM's ruling is
that instructions cannot fix this - *"procedures which rely on someone, whether it's a human or an LLM,
remembering to do something are flawed"* - so the tooling must stop the dispatch or make the review exit
in seconds.

**The trigger is the FINDING, not anything the author chooses to write.** A rule keyed on figures quoted
in a dispatch prompt is passed by leaving the figures out, which is a procedure that relies on
remembering to include them. So a review round's findings become a record, and the next dispatch for that
map is refused until every finding carries a record that verifies it - named, re-runnable, and stating
what it read. The reviewer's first stage then judges whether that record CAN verify its finding, and
exits before reading the map when it cannot. Feature 230's two failures are the negative fixtures: the
canopy fix whose measurement read grove clump bases where the finding was about drawn crowns
(`research.md` R2), and the perf explanation that attributed a stage's growth without the counterfactual
that settled it.

## Functional requirements

### A. A review's findings are a record, and a review is counted when it reaches a verdict (FR-001, FR-002)

**FR-001 `settlement-review` MUST write its verdict as a structured record, as its last act.** One record
per map reviewed, under `<clone>/.git/review-verdicts/`: the map, the engine key the review read, the
verdict (PASS, NEEDS-WORK or NOT-REVIEWABLE), and each finding with a stable id, its severity, and a
one-line statement of what is wrong and where. The agent file carries the record's shape; the review's
prose report is unchanged.

**FR-002 A review MUST be counted when it reaches a PASS or NEEDS-WORK verdict for the current engine key,
not when it is dispatched.** Today `scripts/pair-hooks.sh` writes `review_key` in its `pretool` branch,
so a dispatched review counts as done whether it ran, returned NOT-REVIEWABLE, or never returned
(`research.md` R3). The pair MUST close on a recorded verdict instead, and `scripts/review-gate.sh`'s
review-before-ship requirement MUST read the same record. A NOT-REVIEWABLE verdict, a missing verdict, or
a verdict for an engine key the tree has since moved past closes nothing.

### B. The next dispatch is refused until each finding is verified (FR-003 to FR-006)

**FR-003 A `settlement-review` dispatch for a map whose last recorded verdict carries findings MUST be
refused unless every one of those findings is dispositioned.** A finding is dispositioned by exactly one of:
a measurement record (FR-009) whose `verifies` field names the finding's id and whose `subject` is the map;
or an `accepted` disposition carrying a reason of at least two words, for a finding deliberately left as it
is. The refusal names every finding id that has neither, with the path its record would go in. This is the
requirement that holds whether or not the dispatch prompt quotes anything.

**FR-004 A `settlement-review` dispatch that follows findings MUST NOT overlap an unfinished gate.** A first
review of a change keeps feature 151's overlap - the gate and the review start together and the review's
wall time stays off the critical path. A dispatch covered by FR-003 is a review of FIXES, and the GM's own
example is that it should be blocked when *"the unit tests, or some other makefile command"* has not been
done: it is refused unless `make done` is green for the current engine key. The gate is 1 to 6 minutes on
this repository and the round it protects is 7 to 25 (`research.md` R1).

**FR-005 A `settlement-review` dispatch MUST be refused when a map it names is not current with the
engine, or its review snapshot is incomplete.** The generation cache already decides whether a map would
re-roll (`pipeline/regen.py` returns CACHED or REGENERATED), so the check is a key comparison that rolls
nothing. A map whose key has moved, or whose snapshot lacks the `.json`, `.svg`, `.png` or `.html` the
reviewer reads, is named in the refusal with `make map GEN=...`. Feature 230's pass 12 ran against a
snapshot whose renders the roll cache had evicted, and three of five agents rasterized the SVG themselves
to work around it (`research.md` R1).

**FR-006 A measured figure in a dispatch prompt MUST resolve to a record by feature 239's convention.** A
figure - detected by `scripts/spec-lint.py`'s own `_FIGURE`, imported rather than restated - resolves by
239's key convention to an entry in the measurements file the dispatch names, or carries 239's dated
one-shot label. Figures inside backtick spans are skipped, as in 239's FR-009c. The refusal names each
unresolved figure. This is the weaker of the two dispatch rules (FR-003 is the one a session cannot pass by
omission) and exists so that a figure the author DID quote cannot be a guess.

All four dispatch refusals are escapable with `REVIEW_PREREQ_OK="<why>"` under the project's existing
escape rules - an invocation rather than a mention, a stated reason, logged to `dev/bypass-log/` - for a
map deliberately left in a bad state (a negative fixture, a reproduction).

### C. The reviewer exits before it reads anything (FR-007, FR-008)

**FR-007 `.claude/agents/settlement-review.md` MUST carry a FIRST STAGE that can return NOT-REVIEWABLE.**
Before reading any map, the agent reads the previous verdict's findings and the records that claim to
verify them, and returns NOT-REVIEWABLE - naming the finding and the record, and nothing else - when a
record's `source` cannot support the finding it claims to verify. The judgment is about the SOURCE, and the
canopy case is the worked example the agent file carries: a finding that the notice board stands in the
canopy is verified by a record reading `tree_crowns` or the SVG's drawn ink, and is NOT verified by one
reading a grove's `clumps` with its nominal `r`, because the drawn crowns are jittered off those bases and
reach a median 16.3 ft further (`research.md` R2). The script (FR-003) decides that a record exists; the
agent decides whether it can bear the weight put on it (D1).

**FR-008 The reviewer MUST keep the right to measure independently.** Nothing here removes what has been
this project's best defect-finder: the pass-13 agents re-derived the canopy clearance from scratch, which
is how the proxy was caught. The contract removes the reviewer's need to REBUILD a harness to check a
number it was handed; it keeps the reviewer's distrust of the number.

### D. The record (FR-009)

**FR-009 Measurements are recorded in feature 239's `measurements.json` format, with four fields this
feature adds.** 239's entry carries `value`, `unit`, `command`, `taken`, and optional `note`, `varies` and
`load`. This feature adds `quantity` (what was measured, in words, including the sample it measured over),
`source` (the fields or artifact bytes the harness read), `subject` (the map a record is about) and
`verifies` (the finding id a record verifies, for FR-003). The peer session has adopted `quantity` for spec
figures too; `source`, `subject` and `verifies` are this feature's. Every record this feature's own harness
writes MUST pass 239's `make figures` re-run from a clean checkout, and timing records follow 239's
FR-011c - both requirements are 239's to specify and enforce, and this feature is their consumer (D3).

### E. An attribution names its counterfactual (FR-010)

**FR-010 `make perf-explain` MUST take the attribution's evidence as a STRUCTURED argument, and
`perf-audit` MUST exit early when it is missing.** The command takes either `CONTROL=<measurement key>` - a
recorded run of the same subject with the attributed cause removed or disabled - or
`UNVERIFIED="<reason>"`, an explicit statement that the attribution was not tested, and refuses an
explanation carrying neither. It never parses the explanation's prose (D1). The `perf-audit` agent's first
stage returns NOT-REVIEWABLE when an explanation's `CONTROL` names no record, before any profiling. Feature
230's first explanation is the fixture: it attributed seed 4's web growth to the map on the evidence of a
cumulative-time profile, and the audit's control run - the suspected rule forced to return True - measured
4.70 s against 2.56 s against a 1.34 s baseline and refuted it (`research.md` R2).

## Success criteria

- **SC-001** (FR-001, FR-002) A settlement-review run writes its verdict record; `pair-hooks` closes the
  pair only on a PASS or NEEDS-WORK record for the current engine key and `review-gate.sh` reads the same
  record; a dispatched review that returns NOT-REVIEWABLE, or that is stopped before it returns, leaves the
  pair open and the ship requirement unmet. Proven with each of the three verdicts and with none.
- **SC-002** (FR-003) Feature 230's pass-13 dispatch, rewritten with every figure removed, is still refused,
  and the refusal names the pass-12 finding ids that have no verifying record; the same dispatch proceeds
  once each finding has a `verifies` record or an `accepted` disposition.
- **SC-003** (FR-004) A dispatch following findings is refused while the gate for the current engine key is
  running or red and permitted once it is green; a first review with no prior findings keeps feature 151's
  overlap and is permitted beside a running gate.
- **SC-004** (FR-005) A dispatch naming a map whose generation key has moved, or whose snapshot is missing
  its render, is refused in under 5 seconds naming that map and `make map GEN=...`, and permitted once the
  map is regenerated. Proven on a real pool map, both ways.
- **SC-005** (FR-006) A figure outside a backtick span with no record and no one-shot label is refused and
  named; the same figure with a record or a dated one-shot label is permitted; the same figure inside a
  backtick span is skipped. `REVIEW_PREREQ_OK` with a reason permits all four refusals and is logged; a bare
  token is refused.
- **SC-006** (FR-007, FR-008) The agent file's first stage, given feature 230's canopy finding with a record
  whose `source` is the grove's clumps, returns NOT-REVIEWABLE naming that record; given a record whose
  `source` is `tree_crowns`, it proceeds; and the file still states, in words a test finds, that the reviewer
  may measure independently.
- **SC-007** (FR-009) This feature's own `measurements.json` passes 239's `make figures`, and every record
  written for a `verifies` disposition carries `quantity`, `source`, `subject` and `verifies`.
- **SC-008** (FR-010) `make perf-explain` refuses an explanation with neither `CONTROL` nor `UNVERIFIED`,
  accepts each, and refuses a `CONTROL` naming no record; the `perf-audit` file's first stage returns
  NOT-REVIEWABLE on a `CONTROL` naming no record.
- **SC-009** (spec-wide) `make done` green; every guard this feature adds or changes has a suite proven to
  FIRE by deleting the guard and watching a test go red.

## Decisions recorded

- **D1 A script decides shape; an agent decides adequacy.** Whether a record exists, names a finding and
  re-runs is decidable and belongs in a hook. Whether its source can support its finding is judgment and
  belongs in the agent's first stage. And nothing here makes a script read prose: FR-010's evidence is a
  structured argument precisely so that no command has to decide whether a sentence "names a cause".
- **D2 Two layers, each the other's backstop.** The hook cannot see a dispatch that reaches the agent by
  another route; the agent cannot save the seconds the hook saves.
- **D3 What belongs to feature 239, by agreement.** 239 owns `spec-fidelity`, `scripts/spec-lint.py`, the
  tasks template, the house-style guard, `make figures` (the re-run that proves a recorded command runs from
  a clean checkout) and FR-011c (a timing record's machine state and quiet threshold). This feature's own
  first draft specified the last two as requirements of its own; spec-fidelity round 1 found them to
  duplicate 239, and they were handed back to that session rather than built twice. Whether 239 touches
  `perf-explain`, `perf_review.py` or `perf-audit` was asked of that session directly; the answer is
  recorded in `request.md`.
- **D4 The figure detector is imported from `spec-lint.py`, not copied.** 239's check 5 keys on the same
  definition (239's D4), and that session has undertaken to announce any change to `_FIGURE` or `_UNIT_ALT`
  before it lands.
- **D5 A review is counted at its verdict, not its dispatch - and this changes features 151 and 231.**
  Dispatch-time completion was sound while every dispatched review ran to a report. A review that can exit
  early makes it unsound: the early exit would otherwise count as the review a Mode B map owes, which is the
  exact hole the early exit exists to close.
- **D6 The overlap is kept for a first review and removed for a review of fixes.** Feature 151 put the review
  beside a running gate to keep its wall time off the critical path, and for a first review that still holds.
  A review of fixes is the round this feature is about, and a green gate before it costs 1 to 6 minutes
  against a round of 7 to 25. What remains un-enforced, stated so it is not mistaken for solved: a FIRST
  review whose paired gate later goes red still runs to its end, because a hook cannot stop a running agent.
  FR-002 makes its verdict count for nothing, which protects the ship requirement; the wall time it spent is
  not recovered.

## Review history

- **Round 1, CHANGES REQUIRED, eight items, all applied.** (1) The trigger moved from figures in the prompt
  to the round's findings (FR-003), because a figures rule is passed by omission. (2) The GM's unit-tests
  example addressed against the existing overlap (FR-004, D6). (3) The timing-record requirement handed to
  239 (D3). (4) The run-from-repository requirement cut back to 239's `make figures` (FR-009, D3). (5) The
  perf precondition keyed on a structured argument rather than prose, with a `perf-audit` first stage, and the
  split with 239 asked and recorded (FR-010, D3). (6) The figure rule aligned to 239's key convention,
  one-shot label and backtick skip (FR-006). (7) A NOT-REVIEWABLE return prevented from counting as a review
  (FR-002, D5), which the pair's dispatch-time `review_key` would otherwise have allowed. (8) The orphaned
  requirement named in a criterion (SC-006) and the time budget given a number (SC-004).
