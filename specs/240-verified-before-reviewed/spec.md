# Feature 240 - a review round is not spent on an unverified fix

**Status**: ACCEPTED 2026-09-13 - `spec-fidelity` rounds 1, 2 and 3 CHANGES REQUIRED (eight, seven and two items,
all applied - see Review history), round 4 FAITHFUL. Implementation begins.
**Request**: [`request.md`](request.md), the GM's words verbatim. **Research**: [`research.md`](research.md).
**Peer**: feature 239 (`Diagram (Kuwabata)`) holds the same contract for `spec-fidelity` and spec figures.
The split was agreed between the two sessions and is recorded in `request.md`; this feature touches none of
239's files and consumes 239's `measurements.json` format and its `make figures` re-run rather than
building parallel ones.

## Summary

A `settlement-review` round costs 7 to 25 minutes (`research.md` R1; observed 2026-09-13, method: the review agents' own reported durations across feature 230's rounds). Feature 230 spent fourteen, and its
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
(`research.md` R3). The pair MUST close on a recorded verdict instead: a NOT-REVIEWABLE verdict, a missing verdict, or a verdict
for an engine key the tree has since moved past closes nothing. `scripts/review-gate.sh` keeps its present
rule - a changed pool manifest ships with its notes file changed beside it, escapable with
`REVIEW_GATE_OK` - and additionally refuses a map whose MOST RECENT verdict record is NOT-REVIEWABLE. It is
deliberately not widened to require a fresh PASS for every later engine edit, which the GM did not ask for
and which would force a review round the request exists to save.

### B. The next dispatch is refused until each finding is verified (FR-003 to FR-006)

**FR-003 A `settlement-review` dispatch for a map whose last recorded verdict carries findings MUST be
refused unless every one of those findings is dispositioned.** A finding is dispositioned by exactly one of:
a measurement record (FR-009) whose `verifies` field names the finding's id, whose `subject` is the map, and
which carries its `quantity` and `source` - what was measured and from what, the two things FR-007's first stage
judges (D7);
or an `accepted` disposition carrying a reason of at least two words, for a finding deliberately left as it
is. An `accepted` disposition is an escape in all but name, so it is treated as one: it is logged to
`dev/bypass-log/` the way every other escape here is, listed by `make audit`, and passed to FR-007's first
stage with the verifying records. The refusal names every finding id that has neither, with the path its record would go in. This is the
requirement that holds whether or not the dispatch prompt quotes anything.

**FR-004 A `settlement-review` dispatch that follows findings MUST NOT overlap an unfinished gate.** A first
review of a change keeps feature 151's overlap - the gate and the review start together and the review's
wall time stays off the critical path. A dispatch covered by FR-003 is a review of FIXES, and the GM's own
example is that it should be blocked when *"the unit tests, or some other makefile command"* has not been
done: it is refused unless `make done` is green for the current engine key. A green gate took 56 to 67 s
across the four of feature 230's own (m:230-green-gate-min-s, m:230-green-gate-max-s), and the round it protects
took 7 to 25 minutes (`research.md` R1; the rounds observed 2026-09-13, method: the review agents' reported durations).

**FR-005 A `settlement-review` dispatch MUST be refused when a map it names is not current with the
engine, or the artifacts the reviewer will read are incomplete.** The generation cache already decides whether a
map would re-roll (`pipeline/regen.py` returns CACHED or REGENERATED), so the check is a key comparison that
rolls nothing. Completeness is judged WHERE THE REVIEWER READS: the review snapshot when the dispatch names one
(`.git/review-snapshot/<map>/`), and the pool folder otherwise, each needing the `.json`, `.svg`, `.png` and
`.html`. And a named snapshot must be OF THE CURRENT MAP: it records no key of its own, so it is current when its
manifest and SVG are byte-identical to the pool folder's, whose key the cache has just confirmed - a snapshot taken
before a fix is not. A map whose key has moved, or whose pool folder is incomplete, is named in the refusal with
`make map GEN=...`; a named snapshot that is incomplete or of an older map is refused with the two ways to a
whole, current one - re-take it with `make verify`, or run `make map GEN=...` and dispatch against the pool
folder without naming the snapshot.
Feature 230's pass 12 ran against a snapshot whose renders the roll cache had evicted, and three of five agents
rasterized the SVG themselves to work around it (`research.md` R1).

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
verify them, together with any `accepted` dispositions (FR-003), and returns NOT-REVIEWABLE - naming the
finding and the record, and nothing else - when a record's `source` cannot support the finding it claims
to verify. It also reads its paired gate's recorded result before its first map, between maps where it reviews more
than one, and again immediately before writing its verdict, and records NOT-REVIEWABLE on a red gate - the
last of those is the one that matters in the one-map-per-agent shape, because it stops a review of a red
gate from counting under FR-002 (D6). The judgment is about the SOURCE, and the
canopy case is the worked example the agent file carries: a finding that the notice board stands in the
canopy is verified by a record reading `tree_crowns` or the SVG's drawn ink, and is NOT verified by one
reading a grove's `clumps` with its nominal `r`, because the drawn crowns are jittered off those bases and
reach a median 16.3 ft further (`research.md` R2; observed 2026-09-12 by feature 230's pass-13 reviewers, method: each drawn crown edge in `tree_crowns` measured to its nearest clump base on Sawada). The script (FR-003) decides that a record exists; the
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
**Ordering, stated so it is not mistaken for enforcement:** nothing checks those two properties until 239
implements `make figures`, and 239 is still in specification review. If this feature is implemented first,
its records are written in the right shape and re-run by nothing until then; FR-003 still refuses a finding
with NO record, which does not depend on 239 at all.

### E. An attribution names its counterfactual (FR-010)

**FR-010 `make perf-explain` MUST take the attribution's evidence as a STRUCTURED argument, and
`perf-audit` MUST exit early when it is missing.** The command takes either `CONTROL=<measurement key>` - a
recorded run of the same subject with the attributed cause removed or disabled - or
`UNVERIFIED="<reason>"`, an explicit statement that the attribution was not tested, and refuses an
explanation carrying neither. It never parses the explanation's prose (D1). An `UNVERIFIED` reason is logged
and listed under the project's existing escape rules. The `perf-audit` agent's first stage returns
NOT-REVIEWABLE when a `CONTROL` names no record, before any profiling; and on `UNVERIFIED` it runs the
counterfactual ITSELF before any other work - the GM's *"numbers generated by the reviewer"* - returning
NOT-REVIEWABLE if it cannot, so an untested attribution never reaches a full audit. Feature
230's first explanation is the fixture: it attributed seed 4's web growth to the map on the evidence of a
cumulative-time profile, and the audit's control run - the suspected rule forced to return True - measured
4.70 s against 2.56 s against a 1.34 s baseline and refuted it (`research.md` R2; observed 2026-09-13 by the perf-audit agent, method: the web stage timed at the bookend commit with the rule live and forced True).

## Success criteria

- **SC-001** (FR-001, FR-002) A settlement-review run writes its verdict record; `pair-hooks` closes the
  pair only on a PASS or NEEDS-WORK record for the current engine key, and a dispatched review that returns
  NOT-REVIEWABLE, or that is stopped before it returns, leaves the pair open. `review-gate.sh` refuses a
  changed map whose most recent verdict is NOT-REVIEWABLE and still passes one whose notes file changed
  beside it with no verdict record at all. Proven with each of the three verdicts and with none.
- **SC-002** (FR-003) Feature 230's pass-13 dispatch, rewritten with every figure removed, is still refused,
  and the refusal names the pass-12 finding ids that have no verifying record; the same dispatch proceeds
  once each finding has a `verifies` record or an `accepted` disposition, and each `accepted` disposition
  lands an entry in `dev/bypass-log/` that `make audit` lists.
- **SC-003** (FR-004) A dispatch following findings is refused while the gate for the current engine key is
  running or red and permitted once it is green; a first review with no prior findings keeps feature 151's
  overlap and is permitted beside a running gate.
- **SC-004** (FR-005) A dispatch naming a map whose generation key has moved, or whose artifacts are incomplete
  where the reviewer will read them, is refused in under 5 seconds naming that map and its remedy, and permitted
  once the map is regenerated and the copy the reviewer reads is whole and current: the pool folder, or a snapshot
  re-taken after the regeneration. Proven on a real pool map, both ways, in states the harness sets up itself: a
  render-less pool folder refused when the dispatch names no snapshot; a whole snapshot of the current map
  permitted when named; a whole snapshot of an OLDER map (its SVG differing from the pool's) refused when named.
- **SC-005** (FR-006) A figure outside a backtick span with no record and no one-shot label is refused and
  named; the same figure with a record or a dated one-shot label is permitted; the same figure inside a
  backtick span is skipped. `REVIEW_PREREQ_OK` with a reason permits all four refusals and is logged; a bare
  token is refused.
- **SC-006** (FR-007, FR-008) The agent file's first stage, given feature 230's canopy finding with a record
  whose `source` is the grove's clumps, returns NOT-REVIEWABLE naming that record; given a record whose
  `source` is `tree_crowns`, it proceeds; it instructs the agent to read its paired gate's result before its
  first map, between maps, and immediately before writing its verdict, and to record NOT-REVIEWABLE on red -
  proven with a gate that is green at dispatch and red by verdict time, whose verdict is NOT-REVIEWABLE and
  does not close the pair; and the file still states, in words a test
  finds, that the reviewer may measure independently.
- **SC-007** (FR-009) Every record written for a `verifies` disposition carries `quantity`, `source`,
  `subject` and `verifies`, proven now. That this feature's `measurements.json` also passes 239's
  `make figures` is OWED once 239 implements that command and is OUTSIDE this feature's completion: FR-009's
  ordering note is why, and FR-003 does not depend on it.
- **SC-008** (FR-010) `make perf-explain` refuses an explanation with neither `CONTROL` nor `UNVERIFIED`,
  accepts each, refuses a `CONTROL` naming no record, and logs an `UNVERIFIED` reason where `make audit`
  lists it; the `perf-audit` file's first stage returns NOT-REVIEWABLE on a `CONTROL` naming no record, and
  on `UNVERIFIED` instructs the agent to run the counterfactual itself before any other work.
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
  duplicate 239, and they were handed back to that session rather than built twice. Asked directly whether 239
  touches `perf-explain`, `perf_review.py` or `perf-audit`, that session answered that it touches none of
  the perf machinery, and gave its complete file list (`request.md`): nothing under perf, nothing in
  `settlement-review.md`, nothing in `pair-hooks.sh`.
- **D4 The figure detector is imported from `spec-lint.py`, not copied.** 239's check 5 keys on the same
  definition (239's D4), and that session has undertaken to announce any change to `_FIGURE` or `_UNIT_ALT`
  before it lands.
- **D5 A review is counted at its verdict, not its dispatch - and this changes features 151 and 231.**
  Dispatch-time completion was sound while every dispatched review ran to a report. A review that can exit
  early makes it unsound: the early exit would otherwise count as the review a Mode B map owes, which is the
  exact hole the early exit exists to close.
- **D6 The overlap is kept for a first review and removed for a review of fixes - and a first review checks
  its own gate.** Feature 151 put the review beside a running gate to keep its wall time off the critical
  path, and for a first review that still holds; it is a standing GM ruling this request did not reopen. A
  review of fixes is the round this feature is about, and a green gate before it took 56 to 67 s against a
  round of 7 to 25 minutes (`research.md` R1, m:230-green-gate-min-s, m:230-green-gate-max-s; the rounds observed 2026-09-13, method: the review agents' reported durations). A first review whose paired gate goes RED is handled by the
  reviewer rather than a hook, because a hook cannot stop a running agent: FR-007's first stage reads the
  paired gate's recorded result before its first map and again between maps, and returns NOT-REVIEWABLE the
  moment it reads red. What still ships nothing broken is the gate stamp at push and the engine key moving
  once the red is fixed - not FR-002 alone, whose key a red gate does not move; so FR-007 also re-reads the
  paired gate IMMEDIATELY BEFORE WRITING ITS VERDICT (FR-001's last act) and records NOT-REVIEWABLE on red,
  which stops a review of a red gate from counting. **The residue, for the GM once the implementation
  runs, stated as it actually is:** the agent file dispatches ONE MAP PER AGENT, so in practice there is no
  "between maps" - only the check before the map and the one before the verdict run. A first review whose
  paired gate goes red after dispatch therefore spends each agent's WHOLE round before it finds out; the
  verdict-time check stops that round from counting, and saves none of its wall time. Closing the time cost
  would mean giving up feature 151's overlap for first reviews too, which is the GM's ruling to revisit, not
  this feature's.
- **D7 Amended during implementation (2026-09-13), three readings made concrete by measurement.**
  (a) FR-005's completeness is judged where the reviewer reads - the snapshot when the dispatch names one, the
  pool folder otherwise, and a named snapshot must also be of the current map - its manifest and SVG equal to the
  pool's. Measured on Inashiro (`research.md` R5): a gate leaves every clone pool map without its `.png` and
  `.html`, and snapshots stay on disk, so neither "the snapshot must be whole" (a dispatch without `make verify`
  has none) nor "either place whole" (an old whole snapshot passes a dispatch whose reviewer reads the render-less
  pool folder - the pass-12 failure) says what FR-005 is for; and without the currency clause a snapshot taken
  before a fix passed once `make map` refreshed the pool, so the reviewer read the map without the fix. And the remedy the
  refusal names, `make map GEN=...`, restored the render-less cache entry; `make map` now rolls such a hit
  uncached, so the named remedy works. (b) A record verifies a finding (FR-003) only when it carries `quantity`
  and `source` as well as `verifies` and `subject`, because FR-007's first stage judges the `source` and a record
  without one gives it nothing to judge (SC-007). (c) 239's convention as it landed: `measurements.json` holds bare
  keys, a paragraph cites `m:<key>`, and a one-shot label is a date AND a method; FR-006 and FR-010's `CONTROL`
  follow it.

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
- **Round 2, CHANGES REQUIRED, seven items, all applied.** (1) The gate-duration figure was cited to R1, which
  did not hold it: measured by a committed harness from the gate's own run log, recorded in
  `measurements.json`, and in measuring it the harness found R1's own count wrong - it said 22 gates
  totalling 1,443 s, a truncated listing, on round 2's own run. (2) D6 corrected: FR-002
  does not protect shipping on a red gate, the gate stamp does; and the reviewer now checks its own paired
  gate before its first map and between maps (FR-007), with the residue marked for the GM. (3) The
  `review-gate.sh` clause narrowed to refusing a NOT-REVIEWABLE latest verdict, keeping its present rule.
  (4) On `UNVERIFIED`, `perf-audit` runs the counterfactual itself before anything else, and the reason is
  logged. (5) An `accepted` disposition is logged and listed like any escape. (6) SC-007 split into what is
  provable now and what is owed once 239's `make figures` exists. (7) R3's stale requirement id corrected.
- **Round 3, CHANGES REQUIRED, two items, both applied.** (1) The harness that corrected R1 measured the
  WRONG SET: the run log is committed and merged from main, so a time window over it held every session's
  gates, and ten of its thirty-six were features 229, 231, 232, 233 and 236's - including the 402 s run and
  five of the nine green ones. It now selects each record by its own `commit` field against feature 230's
  commits, closes the window at landing, and states both in `quantity` and `source`: feature 230's own gates
  are 26, 1,663 s, the longest 381 s, four green at 56 to 67 s (m:230-gates-that-ran, m:230-gate-total-s, m:230-gate-max-s,
  m:230-green-gate-min-s, m:230-green-gate-max-s; the 402 s run is another feature's, on round 3's own run). The first re-selection counted 25; the one it
  missed was a gate run at a merge INTO the 230 clone, and the selection now includes those. That is this
  feature's own failure mode - correct arithmetic over the wrong quantity - arriving twice in the harness built
  to record figures honestly, which is the best argument in this record for making the source a field.
  (2) D6's residue restated: agents are dispatched one map apiece, so the between-maps check rarely runs, and
  FR-007 now re-reads the paired gate immediately before writing its verdict so a review of a red gate does not
  count; the time it spends is stated as unrecovered.
- **Round 4, FAITHFUL.** It re-ran the harness, checked the 402 s record and both merge records by hand, and found the
  figures agree in every place they are quoted. Its two minor notes are taken: the record's `source` now says exactly
  which merges its pattern matches, and this status line names all four rounds.
- **Amendment round 1 (after acceptance; the counter reset), CHANGES REQUIRED, four items, all applied.** (1)
  FR-005's completeness judged where the reviewer reads, not "either place whole", which passed a stale snapshot
  beside a render-less pool folder; FR-005, SC-004 and D7(a) rewritten and the check changed to match. (2) FR-003
  carries D7(b)'s `quantity` and `source` itself. (3) Two one-shot labels in `research.md` began with a capital and
  did not match 239's pattern; lowered. (4) The Review history's round labels separated, rounds 3 and 4 citing
  their own keys.
- **Amendment round 2, CHANGES REQUIRED, two items, both applied.** (1) A named snapshot was judged whole but not
  current, so one taken before a fix passed once the pool was refreshed; FR-005, SC-004 and D7(a) now require it
  to equal the pool's manifest and SVG, and the check does. (2) Two R5 figures did not come from their command,
  which measured whatever state the clone was in and wrote nothing; the harness now sets up and restores every
  state itself and records its own figures.
- **Amendment round 3, CHANGES REQUIRED, one item, applied.** SC-004's "permitted once the map is regenerated"
  no longer held for a named snapshot, which stays refused as an older map until re-taken; it now says the copy the
  reviewer reads must be whole and current. Its aside taken too: the older-snapshot refusal names `make map GEN=...`
  in its second remedy, as FR-005 does.
- **Amendment round 4, FAITHFUL.** Round 3's item resolved; nothing new introduced.
