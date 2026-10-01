# Feature 294 - Rethinking the settlement review

**Feature Branch**: none (main, in the clone `diagram-review`)
**Created**: 2026-09-30; scope written 2026-10-01
**Status**: Draft - written for the GM's reading before work begins (request.md, 2026-10-01: *"update the spec with all of
these changes and then I will take a look at it before I have you begin"*). Not yet reviewed by `spec-fidelity`; no plan, no
tasks.
**Request**: [`request.md`](request.md) - the GM's words verbatim: the review's time and tokens, *"as the number of settlements
that we have in our pool grows ... This will become quickly untenable after we branch out into villages and towns and provincial
cities and capital cities"*; *"if our settlement review is checking for anything which a properly implemented placement
algorithm would make impossible, then we should fix the placement algorithm and then stop checking for that thing"*; the
session's seven-item list, agreed (*"I do agree with that list"*); a glyph review that runs *"anytime a new glyph is added to
a map, but then not run at any other time"*; and caste geography, agreement with a building's plan sheet and label placement
*"struck from the subagent review"*.
**Predecessors**: 151 (the pair guard), 231 (review owed only when a manifest moved), 240 (verified before reviewed), 248 (one
map per agent; rendering-only features owe none), 251/255 (tiered checks, the cost census), 257 (a sheet on a map matches the
map), 266/289 (the one caption placer), 287 (placer guarantees), 297 (placement by construction).

## Summary

The `settlement-review` agent (`.claude/agents/settlement-review.md`, Opus at high effort, a 48k-character contract) is owed
for EVERY pool map whose manifest differs from main (`scripts/_review_owed.py`), enforced by the pair guard, the stop hook and
`review-gate.sh`. A shared engine change moves every map, so every map is reviewed every round, and every fix moves the
manifests again. The cost is maps x rounds x one run (43 turns, 6.6 M input tokens a run; `specs/251-*/research.md`), and it
grows with the pool and with the size of each map.

The census of the ledger (research R0 below) found about 260 runs over two months and about 360 distinct findings: ~160
geometric (of which ~117 are now guaranteed by the placer and ~45 are still caught only by the reviewer), ~70 judgment, ~110
paperwork (stale counts in notes prose, missing records, NOT-REVIEWABLE refusals; ~36 runs spent on NOT-REVIEWABLE), ~20
nothing or declined. Several sweeps never fired.

This feature makes the review small, targeted and self-measuring: what a placer can guarantee is guaranteed there and removed
from the review; what is left is judgment, asked only of the maps whose depicted content a feature changed; a new glyph gets
its own review, once; the subjects the GM struck leave the contract and become placer obligations of the tier features that
make them relevant; and the ledger reports each run's cost by itself.

## R0 - the baseline census (2026-10-01)

Taken by an Opus agent over every `settlement-review` row of `docs/review-ledger.md`, hand-deduplicated, so approximate; the
plan re-takes it as a reproducible script (FR-012) before any count below is used as a measurement.

| class | ~count | note |
|---|---|---|
| A geometric, now guaranteed | 117 | feature 287's rules cite settlement-review by name six times; its census stands at 163 of 175 |
| A geometric, still unchecked | 45 | 14 classes, listed under FR-003 |
| B judgment | 70 | ~15 of the ~100 author-missed-and-fixed findings |
| C paperwork | 110 | stale typed counts ~25 times in 269 and 293 alone; ~36 runs NOT-REVIEWABLE |
| D nothing / declined | 20 | |

Never fired: the twin detector, caste/outcast/status zoning, the declared-economy check, the generic-annotation and
Imperial-road label rules; agreement with a Mode A sheet confirmed once. Wall time is recorded on 7 rows only; tokens on none;
the "author had missed?" column is empty from 2026-09-27.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A check the placer guarantees is not asked of the reviewer (Priority: P1)

Every sweep and validated example in the contract is matched against the placer guarantees (287's census, 297's construction
rules) and the gate's tests. A sweep wholly covered is removed; a sweep partly covered is cut to its uncovered part, which
names the guarantee that covers the rest.

**Acceptance**: a table in research maps each sweep of today's contract to KEPT (judgment), CUT (names the test or guarantee),
MOVED (names the new test from Story 2) or STRUCK (Story 5); the contract carries only KEPT. The contract is measurably
shorter, its size before and after recorded.

### User Story 2 - The geometric findings the reviewer still catches become rules (Priority: P1)

Each still-unchecked geometric class (FR-003) becomes a placer guarantee where a placer decides it, or a gate test where it is
a property of the drawing (record against ink, draw order). Each new rule is first proved to fail on the ledger's recorded
case (the unfixed artifact or a seeded fault), then the map is fixed, then the matching text leaves the contract. The notes'
typed counts are checked against the manifest the same way the census block already is.

**Acceptance**: every FR-003 class has a test that went red on its recorded case and is green on the pool; the contract no
longer asks for any of them.

### User Story 3 - A review is owed for what a feature changed, not for every map that moved (Priority: P1)

A settlement-review is owed for the maps a feature TARGETS when it changes what a map depicts or the form of what it draws -
not for every pool map whose manifest moved. An engine change that only shifts positions within the same rules (a speed
lever, a re-seat, a refactor) owes no agent review: it produces a mechanical report of what moved (counts per kind, the
picture-diff share and box, the guarantee census before and after) which is recorded with the feature and is the GM's to look
at. For tiers larger than a hamlet the targeted set is one representative map per tier unless the feature names more.

**Acceptance**: `_review_owed.py` (or its successor) answers from the feature's declared targets and classification, never
from "a manifest moved" alone; a shared engine change across all five hamlets owes zero reviews and one report; a feature that
adds a kind to Inashiro owes Inashiro alone. The rule is scripted, not remembered (GM 2026-09-13 doctrine).

### User Story 4 - A new glyph gets its own review, once (Priority: P1)

A glyph-legibility review - does the new mark read as what it depicts, and is it confusable with any mark already in the
legend (the manure heap read as a bush, the rack as a woodpile, the privy as the wood shed) - is its own check, dispatched when
a new glyph is added to a map and at no other time. Glyph legibility leaves the settlement-review contract. The check sees the
new glyph on one map where it appears, at the zooms the reader meets, beside the glyphs it could be taken for. Whether a glyph
is new is decided by a script from the delta, not by memory; a feature that is all `research: rendering` still owes it when it
adds a glyph (it is exempt from the settlement-review, not from this).

**Acceptance**: an agent file for the glyph review with its pinned tier; a script that names the new glyphs in a delta; the
dispatch enforced the way the pair guard enforces the settlement-review today; a delta with no new glyph owes none; the
settlement-review contract no longer carries the legibility and mirror sweeps.

### User Story 5 - Caste geography, plan-sheet agreement and label placement leave the review (Priority: P1)

These three are struck from the settlement-review contract. Each becomes an obligation of the placer for the tier where it
is relevant, so it is not lost: caste, outcast and status zoning is a placement rule of the town/city generators when they are
built (recorded in the migration plan's status table and in the tier's research specification it follows); agreement of a
compound's face with its own Mode A sheet is the sheet-matches-map check of feature 257 and any rule that check lacks is added
there; label placement is the one caption placer (features 266, 289) and any placement rule the review carried that the placer
does not is added to the placer.

**Acceptance**: the contract contains none of the three; for each, research names where it now lives (a test, a placer rule,
or a recorded obligation on a named future tier), and a rule the review carried that had no home gets one.

### User Story 6 - A round is not spent on a map that cannot be reviewed, and rounds are capped (Priority: P2)

The FIRST STAGE prerequisites (a green paired gate, a record behind every previous finding) are checked by the dispatching
tooling BEFORE an agent is launched, so a NOT-REVIEWABLE outcome never costs a run. A map gets one review round and at most
one fix-verification round; what remains after that goes to future-work or to the GM through `escalation-check`.

**Acceptance**: a dispatch with a red gate or a missing record is refused with the missing item named; a third round on the
same map within one feature is refused unless the GM waives it.

### User Story 7 - The ledger measures the review by itself (Priority: P2)

Each review run's wall time and tokens are recorded from the run itself, not typed; every finding carries "author had
missed?" and its class (geometric / judgment / paperwork / nothing); a script reports the totals per feature and per sweep, so
"is it pulling its weight" is answered by a command.

**Acceptance**: a script prints R0's table from the ledger; a review row without cost or class is refused at commit.

### User Story 8 - A cheaper tier is re-tested once the contract is judgment-only (Priority: P3)

With the contract cut to judgment, a cheaper tier (Sonnet, or Opus at lower effort) is run against seeded maps with known
judgment findings, three runs a leg (the standing rule for a judging agent), and adopted only if it finds what Opus finds.

**Acceptance**: the experiment and its verdict are recorded in the ledger and the tier table; the tier changes only on that
result.

### User Story 9 - The tooling says what the GM ruled (Priority: P2)

The GM's 2026-08-29 ruling (*"in general, we don't need that level of review period"*) and this feature's scope are written
into the places that still call the review mandatory for every map: the root `CLAUDE.md` review bullet, `dev/reviews.md`,
the agent's "when you are dispatched" section, `pair-hooks.sh`, `review-gate.sh` and the constitution's wording where it says
the same.

**Acceptance**: no document or guard states an obligation this feature removed (`make stale-terms` over the old trigger).

### Edge Cases

- A feature both adds a glyph and changes layout: owes the glyph review and the targeted settlement-review, one agent each.
- A new kind drawn with an existing glyph: no glyph review (nothing new to read); the kind's placement is the placer's.
- A map new to the pool: a FULL settlement-review, and a glyph review for any glyph it introduces.
- An engine sweep whose mechanical report shows a kind's count collapsing (a class vanishing from a map): the report flags it,
  and a flagged report owes the targeted review of that map - a count change is mechanical, not judgment, so it is the report's
  to catch.
- The hand-authored legacy pool: not reviewed on an engine sweep; reviewed only when a feature targets it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Research maps every sweep, protocol step and validated example of the contract to KEPT / CUT / MOVED / STRUCK
  with the test, guarantee or obligation that replaces it.
- **FR-002**: The contract keeps only KEPT items. Its "the gate can see / you must see" table is rewritten to the new line.
- **FR-003**: The still-unchecked geometric classes become rules, each proved red on its recorded case first: (1) record
  against ink (a snapped gate, a hit polygon over the banks, a head-race record past its ink, houses inside the toe polygon);
  (2) ruled or plumb edges on non-brook shapes (marsh limit, shrine grove, clearings); (3) woodpile seating (end-on, off the
  wall, on a neighbor's gable); (4) parallel twin watercourses (12-32 ft apart in the ledger rows of 08-26 T11, 145 and 230, observed by the reviewer); (5) draw order and translucency ghosting;
  (6) reed-fringe gaps; (7) page hit regions taking a neighbor's area; (8) lane tread to house-wall clearance; (9) a privy or
  heap seated without the wind; (10) acute lane merges; (11) side-by-side footbridges; (12) drawn area against rolled area;
  (13) house bearings bunching; (14) brook share off the frame. A class the research shows to be a judgment after all moves to
  KEPT with the reason recorded.
- **FR-004**: A check that every count stated in a map's notes prose agrees with its manifest.
- **FR-005**: The settlement-review is owed per feature for its targeted maps when it changes depicted content or form;
  otherwise not. The feature declares its targets; the script refuses a layout-moving feature that declares none.
- **FR-006**: An engine sweep produces the mechanical report of User Story 3 and records it with the feature; a flagged
  collapse owes the targeted review.
- **FR-007**: The glyph review: its own agent, its own scripted trigger (a glyph new to the delta), its own enforcement; never
  dispatched otherwise.
- **FR-008**: Glyph legibility, the mirror rule, caste geography, Mode A sheet agreement and label placement leave
  the settlement-review contract; each has a recorded home (FR-001).
- **FR-009**: Prerequisites are checked before dispatch; a map gets at most two rounds per feature without a GM waiver.
- **FR-010**: Review cost (wall, tokens) and finding class are recorded per run and per finding without hand-typing the cost.
- **FR-011**: The documents and guards in User Story 9 state the new rule and nothing older.
- **FR-012**: R0 is re-taken by a script, which then serves as User Story 7's report.
- **FR-013**: The cheaper-tier experiment of User Story 8, after FR-002.

### Key Entities

- **Review contract**: the agent file; after this feature, judgment only.
- **Glyph review**: a new agent and trigger.
- **Targets**: the maps a feature declares it changes.
- **Sweep report**: the mechanical what-moved record for an engine sweep.
- **Ledger row**: per finding, with class, author-missed and per-run cost.

## Success Criteria *(mandatory)*

- **SC-001**: A shared engine change that moves all five hamlets' manifests, with no change to depicted content, owes zero
  settlement-review runs (today: five per round).
- **SC-002**: Every FR-003 class has a red-then-green test; the contract asks for none of them.
- **SC-003**: The contract is at most half its current 48k characters (a target; the measurement is the FR-001 table, and a
  larger residue is accepted if every KEPT item is judgment).
- **SC-004**: A dispatch that would have returned NOT-REVIEWABLE is refused before launch on the recorded 280 and 293 cases
  replayed.
- **SC-005**: The ledger report reproduces R0 within the hand census's error and adds cost per feature.
- **SC-006**: A feature adding one glyph owes exactly one glyph review; a feature adding none owes none.

## Decisions Recorded

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The settlement-review is owed per targeted map for content/form changes, not per moved manifest | deliberate deviation from feature 231's trigger | GM 2026-10-01 (request.md); R0's cost | `_review_owed.py`, this spec |
| Glyph legibility is its own review, run only when a glyph is added | deliberate deviation from the single review | GM 2026-10-01 | the new agent file, this spec |
| Caste geography, Mode A sheet agreement, label placement leave the review for the placers | deliberate deviation | GM 2026-10-01 | the contract, the migration plan, 257, the caption placer |
| At most two rounds per map per feature | guess (from R0's round pattern: later rounds mostly paperwork and fix fallout) | R0 | `dev/reviews.md` |
| One representative map per tier above hamlet | guess | GM's scaling concern; to be measured when a second village exists | `_review_owed.py` |

No decision here changes what a map draws, except the FR-003 rules, each of which records its own decision at its point of
change when it is built.

## Open questions for the GM

1. **A redrawn glyph.** The request says a glyph review when a new glyph is ADDED. Does a substantially redrawn existing glyph
   owe one too? As written, no (the literal request); the session's recommendation is yes, since a redrawn mark can be newly
   confusable, but only on the GM's word.
2. **Label wording.** The GM struck label PLACEMENT. The contract also judges label WORDING (a label that says something
   obvious, a generic annotation). Captions are declared per kind in code (feature 286), so the session's recommendation is to
   strike wording too and make "which kinds carry a caption" a declared rule; as written, wording stays KEPT.
3. **The sweep report.** Recorded with the feature and left for the GM to look at when they choose, or shown to the GM at the
   feature's landing? As written, recorded and named in the landing summary.

## Assumptions

- The pool stays five scripted hamlets, one village shrine and five magistracies while this is built; the representative-per-
  tier rule is written now and measured when a second map of a larger tier exists.
- The existing guards (pair, review-gate, stop hook) are amended rather than replaced; their escapes and logging stay.

## Review history

(none yet)
