# Feature 294 - Rethinking the settlement review

**Feature Branch**: none (main, in the clone `diagram-review`)
**Created**: 2026-09-30; scope written 2026-10-01, revised the same day on the GM's answers
**Status**: Taken up 2026-10-01 (request.md: *"Please work feature 294 from start to finish"*); first drafted for the GM's reading (*"update the spec with all of
these changes and then I will take a look at it before I have you begin"*). Accepted - FAITHFUL at round 3 (2026-10-01).
**Request**: [`request.md`](request.md) - the GM's words verbatim: the review's time and tokens, *"as the number of settlements
that we have in our pool grows ... This will become quickly untenable after we branch out into villages and towns and provincial
cities and capital cities"*; *"if our settlement review is checking for anything which a properly implemented placement
algorithm would make impossible, then we should fix the placement algorithm and then stop checking for that thing"*; the
session's seven-item list, agreed (*"I do agree with that list"*); caste geography, agreement with a building's plan sheet and
label placement *"struck from the subagent review"*; and, on the draft, that the glyph review was *"an example of something
that would be run only when a new element is added to the map"*, so the feature includes *"an audit of the checks that we are
doing to ask ourselves whether other things follow the same logic and thus should be moved into separate checks which only run
under certain circumstances"*; a glyph review also on a redraw and when *"the rules for how a glyph works change
substantially"*; label wording with no check of its own; and no what-moved report *"unless that is a report which the subagent
reviewers need in order to more efficiently do their job"*.
**Predecessors**: 151 (the pair guard), 231 (review owed only when a manifest moved), 240 (verified before reviewed), 248 (one
map per agent; rendering-only features owe none), 251/255 (tiered checks, the cost census), 257 (a sheet on a map matches the
map), 266/289 (the one caption placer), 286 (captions declared), 287 (placer guarantees), 297 (placement by construction).

## Summary

The `settlement-review` agent (`.claude/agents/settlement-review.md`, Opus at high effort, a 49,960-character contract, observed 2026-10-01; method: `wc -c`) is owed
for EVERY pool map whose manifest differs from main (`scripts/_review_owed.py`), enforced by the pair guard, the stop hook and
`review-gate.sh`. A shared engine change moves every map, so every map is reviewed every round, and every fix moves the
manifests again. The cost is maps x rounds x one run (43 turns, 6.6 M input tokens a run; `specs/251-*/research.md`), and it
grows with the pool and with the size of each map.

The census of the ledger (R0 below) found about 260 runs over two months and about 360 distinct findings: ~160 geometric (of
which ~117 are now guaranteed by the placer and ~45 are still caught only by the reviewer), ~70 judgment, ~110 paperwork (stale
counts in notes prose, missing records, NOT-REVIEWABLE refusals; ~36 runs spent on NOT-REVIEWABLE), ~20 nothing or declined.
Several sweeps never fired.

This feature replaces "review every map that moved, for everything" with three things:

1. what a placer or a test can decide is decided there, and leaves every review;
2. what needs judgment is split into **triggered checks**, each run only when the thing it judges is new or changed - the
   glyph check (an element added whatever its mark, a glyph redrawn, or an element's placement rule substantially changed) is the first, and an audit of every
   check we run decides which others follow the same logic;
3. what remains as a whole-map review runs only on the occasion it exists for (a map new to the pool, or whatever the audit
   finds), never because an engine change moved a manifest.

An engine change that only moves things within the same rules owes no review and produces no report: the GM looks at the map.

## R0 - the baseline census (2026-10-01)

Taken by an Opus agent over every `settlement-review` row of `docs/review-ledger.md`, hand-deduplicated, so approximate; the
plan re-takes it as a reproducible script (FR-013) before any count below is used as a measurement.

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

### User Story 1 - The audit: every check we run, sorted by what it needs and when it is owed (Priority: P1)

Every check the map reviews run - each sweep, protocol step and validated example of `settlement-review`, and of the other map
reviews (`building-review`, `size-audit`) - is put through the same questions, recorded as one
table in research:

1. **Can a placer or a test decide it?** Then it is CUT (an existing guarantee or test covers it, named) or MOVED (a new rule,
   User Story 2).
2. **Was it struck by the GM?** Then STRUCK (User Story 5).
3. **If it needs judgment, what is the occasion on which its answer can change?** The glyph check's answer changes only when an
   element new to the map is added (whatever its mark), a glyph is redrawn, or an element is placed by substantially different
   rules; at any other time it would re-judge the same thing. Each
   judgment check names its occasion (a new element, a new form of an existing element, a new map, a new tier, a new caption
   type, a new compound sheet, ...) and becomes TRIGGERED on it - its own check, run then and never otherwise - or stays in a
   whole-map review only when its answer genuinely depends on the whole map changing (the twin detector, "does this read as a
   place"), with that occasion named.
4. **Has it ever fired?** R0's count per check is recorded beside it. A check that has never fired is kept only with a stated
   reason (it guards a tier not yet built, for instance), and its trigger is that tier.

**Acceptance**: the table covers every check in the three agent files with a verdict (CUT / MOVED / STRUCK / TRIGGERED on
<occasion> / WHOLE-MAP on <occasion>) and its R0 count; the agent files carry only what the table assigns them; each TRIGGERED
check exists as its own check with its own trigger (User Story 4).

### User Story 2 - The geometric findings the reviewer still catches become rules (Priority: P1)

Each still-unchecked geometric class (FR-003) becomes a placer guarantee where a placer decides it, or a gate test where it is
a property of the drawing (record against ink, draw order). Each new rule is first proved to fail on the ledger's recorded
case (the unfixed artifact or a seeded fault), then the map is fixed, then the matching text leaves the contract. The notes'
typed counts are checked against the manifest the same way the census block already is.

**Acceptance**: every FR-003 class has a test that went red on its recorded case and is green on the pool; no review asks for
any of them.

### User Story 3 - No review is owed because a manifest moved (Priority: P1)

The trigger "a pool map's manifest differs from main" is retired. A review is owed only on an occasion the audit assigned to
it: a triggered check on its occasion, a whole-map review on its occasion. An engine change that moves things within the same
rules - every element still placed under rules it has already been judged under (a speed lever, a re-seat, a refactor) - owes
nothing, and produces no report of what moved - the GM looks at the map, which tells them more than a report would. A report of what moved is built only if the
audit finds a triggered check needs one as its input (for example, where on the map the changed element now stands, so the
check looks there and not at the whole sheet). A new or substantially changed placement rule is NOT the same rules: it is an
occasion, and owes the glyph check for the elements it re-places (the GM's tannery case) and any other triggered check the
audit assigns to that occasion.

**Acceptance**: `_review_owed.py` (or its successor) answers from occasions, never from "a manifest moved"; a shared engine
change across all five hamlets with no new or changed element owes zero runs; for tiers larger than a hamlet, a triggered check
looks at one map where the element appears unless the feature names more.

### User Story 4 - A triggered check runs on its occasion and at no other time (Priority: P1)

The first triggered check is the **glyph check**: does the mark read as what it depicts, is it confusable with a mark already
in the legend (the manure heap read as a bush, the rack as a woodpile, the privy as the wood shed), and does it look right
where it now stands. Its occasions:

- an element new to the map is added, whatever its mark (a new glyph, or an existing glyph in a new role);
- an existing glyph is redrawn;
- the rules for where or how a glyph's element is placed change substantially (the GM's example: tanneries moved from inside
  the city to along the water - the same mark, in a new setting it has never been judged in).

Every triggered check the audit produces follows the same shape: its own agent (or a shared agent with a per-check contract),
its own pinned tier, a scripted answer to "is it owed" from the feature's delta and declarations, the dispatch enforced the way
the pair guard enforces the review today, and it looks at the changed element on one map where it appears, at the zooms the
reader meets, beside what it could be confused with. Where a script cannot tell a substantial change from a minor one (a
placement rule rewritten versus a constant tuned), the feature's task declares the element and the kind of change, and the
script refuses a delta that touches an element's drawing or placement code with no declaration. A feature that is all
`research: rendering` is not exempt from a triggered check (a redraw is rendering).

**Acceptance**: the glyph check and every other TRIGGERED row of the audit exists with its trigger; a delta with no occasion owes
none of them; a delta that adds, redraws or re-places one element owes exactly the checks whose occasion it is, once.

### User Story 5 - Caste geography, plan-sheet agreement and label placement and wording leave the review (Priority: P1)

These are struck from the settlement-review contract, with no check of their own. Each becomes an obligation of the placer
for the tier where it is relevant, so it is not lost: caste, outcast and status zoning is a placement rule of the town/city
generators when they are built (recorded in the migration plan's status table and in the tier's research specification);
agreement of a compound's face with its own Mode A sheet is the sheet-matches-map check of feature 257, and any rule that check
lacks is added there; label placement is the one caption placer (features 266, 289), and any placement rule the review carried
that the placer does not is added to it. Label WORDING (a label that says the obvious, a generic annotation) goes too: captions
are declared per element in code (feature 286). If wording defects are later seen slipping through, the remedy is a triggered
check on a new caption type, as the GM said, not a return to the whole-map review.

**Acceptance**: no review contract contains any of the four; for each, research names where it now lives (a test, a placer
rule, a declared caption, or a recorded obligation on a named future tier), and a rule the review carried that had no home
gets one.

### User Story 6 - A round is not spent on a map that cannot be reviewed, and rounds are capped (Priority: P2)

The FIRST STAGE prerequisites (a green paired gate, a record behind every previous finding) are checked by the dispatching
tooling BEFORE an agent is launched, so a NOT-REVIEWABLE outcome never costs a run. A check gets one round and at most one
fix-verification round per feature; what remains goes to future-work or to the GM through `escalation-check`.

**Acceptance**: a dispatch with a red gate or a missing record is refused with the missing item named; a third round of the
same check on the same subject within one feature is refused unless the GM waives it.

### User Story 7 - The ledger measures every check by itself (Priority: P2)

Each run's wall time and tokens are recorded from the run itself, not typed; every finding carries "author had missed?", its
class (geometric / judgment / paperwork / nothing) and the check that raised it; a script reports the totals per feature and
per check, so "is it pulling its weight" is answered by a command - including for each new triggered check, which is how a
check that never fires is noticed.

**Acceptance**: a script prints R0's table from the ledger; a review row without cost, class or check is refused at commit.

### User Story 8 - A cheaper tier is re-tested once the checks are judgment-only (Priority: P3)

With each contract cut to judgment and narrowed to its occasion, a cheaper tier (Sonnet, or Opus at lower effort) is run
against seeded cases with known judgment findings, three runs a leg (the standing rule for a judging agent), per check, and
adopted only where it finds what Opus finds.

**Acceptance**: the experiment and its verdict per check are recorded in the ledger and the tier table; a tier changes only on
that result.

### User Story 9 - The tooling says what the GM ruled (Priority: P2)

The GM's 2026-08-29 ruling (*"in general, we don't need that level of review period"*) and this feature's scope are written
into the places that still call the review mandatory for every moved map: the root `CLAUDE.md` review bullet and guard table,
`dev/reviews.md`, the agent's "when you are dispatched" section, `pair-hooks.sh`, `review-gate.sh` and the constitution's
wording where it says the same.

**Acceptance**: no document or guard states an obligation this feature removed (`make stale-terms` over the old trigger).

### Edge Cases

- A delta with several occasions (a new glyph and a substantially re-placed existing one): each owed check runs once per
  element, in parallel.
- A new element drawn with an existing glyph: the glyph check is owed for the new element (an element new to the map is the
  occasion, whatever its mark - a shared mark is exactly the confusability the check exists for).
- A map new to the pool: the whole-map review, plus the triggered checks for any element new to the legend.
- A minor tweak to an element (a color, a constant within its band): no occasion; the task's declaration says so.
- The hand-authored legacy pool: a hand-drawn Mode B map owes no review on any occasion, since it will be converted to
  scripted generation; a hand-drawn Mode A sheet (a magistracy, a country shrine) keeps its review (the GM, 2026-10-01,
  request.md; amended after acceptance).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The audit of User Story 1 over `settlement-review`, `building-review` and `size-audit`, as one research table
  with a verdict, an occasion and an R0 count per check.
- **FR-002**: Each agent file keeps only what the audit assigns it; the settlement-review's "the gate can see / you must see"
  table is rewritten to the new line.
- **FR-003**: The still-unchecked geometric classes become rules, each proved red on its recorded case first: (1) record
  against ink (a snapped gate, a hit polygon over the banks, a head-race record past its ink, houses inside the toe polygon);
  (2) ruled or plumb edges on non-brook shapes (marsh limit, shrine grove, clearings); (3) woodpile seating (end-on, off the
  wall, on a neighbor's gable); (4) parallel twin watercourses (12-32 ft apart observed 2026-08-26 to 2026-09-13; method: the reviewer's measurement, ledger rows 08-26 T11, 145, 230); (5) draw order and translucency ghosting;
  (6) reed-fringe gaps; (7) page hit regions taking a neighbor's area; (8) lane tread to house-wall clearance; (9) a privy or
  heap seated without the wind; (10) acute lane merges; (11) side-by-side footbridges; (12) drawn area against rolled area;
  (13) house bearings bunching; (14) brook share off the frame. A class the research shows to be a judgment after all goes
  back through the audit with the reason recorded.
- **FR-004**: A check that every count stated in a map's notes prose agrees with its manifest.
- **FR-005**: "A manifest moved" is retired as a trigger; a review is owed only on an occasion the audit assigned.
- **FR-006**: No what-moved report is built, unless the audit finds a triggered check needs one as input; then it is built as
  that check's input, not for the GM.
- **FR-007**: The glyph check, on its three occasions (an element added, whatever its mark; a glyph redrawn; an element's placement rules
  substantially changed), and every other
  TRIGGERED check of the audit: own contract, pinned tier, scripted owed-answer from the delta and the task's declarations,
  enforced dispatch.
- **FR-008**: Caste geography, Mode A sheet agreement, label placement and label wording leave every review contract with no
  check of their own; each has a recorded home.
- **FR-009**: Prerequisites are checked before dispatch; a check gets at most two rounds per subject per feature without a GM
  waiver.
- **FR-010**: Review cost (wall, tokens), finding class and raising check are recorded per run and per finding without
  hand-typing the cost.
- **FR-011**: The documents and guards in User Story 9 state the new rule and nothing older.
- **FR-012**: The cheaper-tier experiment of User Story 8, per check, after FR-002.
- **FR-013**: R0 is re-taken by a script, which then serves as User Story 7's report.

### Key Entities

- **Check**: one question a review asks, with its verdict and occasion from the audit.
- **Occasion**: the change to a map on which a check's answer can change (an element added, redrawn or re-placed; a new map; a
  new tier; ...).
- **Triggered check**: a judgment check run only on its occasion; the glyph check is the first.
- **Whole-map review**: what remains of `settlement-review`, run only on its own occasion.
- **Declaration**: a task's statement of the elements it adds, redraws or re-places, and how.
- **Ledger row**: per finding, with class, author-missed, raising check and per-run cost.

## Success Criteria *(mandatory)*

- **SC-001** (FR-005): A shared engine change that moves all five hamlets' manifests with no occasion owes zero review runs (today: five
  per round).
- **SC-002** (FR-006, FR-007): A feature that adds one glyph owes exactly the checks whose occasion that is, on one map, once; the same for a
  redraw, for a substantial re-placement (the tannery case, seeded), and for a new element that reuses an existing glyph
  (seeded), and no what-moved report is built for any of them unless the audit recorded that check as needing one as its input, in which case it is built into that check's dispatch only; a triggered check's dispatch otherwise carries its element and the one map it stands on (FR-006).
- **SC-003** (FR-003, FR-004): Every FR-003 class, and FR-004's count check, has a red-then-green test; no review asks for any of them.
- **SC-004** (FR-001, FR-002, FR-008): Every check in the three agent files has an audit verdict; the settlement-review contract is at most half its
  current 49,960 characters (observed 2026-10-01; method: `wc -c` on the agent file) (a target; a larger residue is accepted if every remaining item is whole-map judgment).
- **SC-005** (FR-009): A dispatch that would have returned NOT-REVIEWABLE is refused before launch on the recorded 280 and 293 cases
  replayed.
- **SC-006** (FR-010, FR-013): The ledger report reproduces R0 within the hand census's error and adds cost per feature and per check.
- **SC-007** (FR-011): No document or guard User Story 9 names states an obligation this feature removed (`make stale-terms` over
  the old trigger finds none).
- **SC-008** (FR-012): Each check's tier experiment and its verdict are recorded in the ledger and the tier table, and a tier
  changes only where every run of the cheaper tier (Sonnet, or Opus at lower effort) finds what Opus finds.

## Decisions Recorded

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| "A manifest moved" no longer owes a review; reviews are owed on occasions | deliberate deviation from feature 231's trigger | GM 2026-10-01 (request.md); R0's cost | `_review_owed.py`, this spec |
| Judgment checks split into triggered checks by occasion, decided by an audit; the glyph check first | deliberate deviation from the single review | GM 2026-10-01 | the audit table, the agent files |
| The glyph check fires on add, redraw and substantial re-placement | deliberate deviation | GM 2026-10-01 (the tannery example) | the glyph check's contract |
| Caste geography, Mode A sheet agreement, label placement and wording leave the reviews | deliberate deviation | GM 2026-10-01 | the contracts, the migration plan, 257, the caption placer, 286 |
| No what-moved report for the GM | deliberate deviation from the draft | GM 2026-10-01: looking at the map does more | this spec |
| At most two rounds per check per subject per feature | guess (from R0's round pattern: later rounds mostly paperwork and fix fallout) | R0 | `dev/reviews.md` |
| A triggered check above hamlet tier looks at one map where the element appears | guess | GM's scaling concern; measured when a second village exists | the owed-script |

No decision here changes what a map draws, except the FR-003 rules, each of which records its own decision at its point of
change when it is built.

## Questions answered by the GM (2026-10-01)

1. A redrawn glyph owes the glyph check, and so does a substantial change to the rules placing it (User Story 4).
2. Label wording leaves the review with no check of its own; a triggered check on a new caption type if it is later seen to
   slip (User Story 5).
3. No what-moved report for the GM; only as a check's input if one needs it (User Story 3, FR-006).

## Assumptions

- The pool stays five scripted hamlets, one village shrine and five magistracies while this is built; the one-map-per-element
  rule above hamlet tier is written now and measured when a second map of a larger tier exists.
- The existing guards (pair, review-gate, stop hook) are amended rather than replaced; their escapes and logging stay.
- The audit covers the map reviews (`settlement-review`, `building-review`, `size-audit`); the record checks (`quote-check`,
  `record-format`, `source-reader`, `source-applicability`, `entry-drift`) already fire on a changed entry, which is their
  occasion, and are out of scope.

## Review history

- Round 1 (spec-fidelity, 2026-10-01): CHANGES REQUIRED, 4 items - User Story 3's example "a new rule that moves what it
  governs" exempted the GM's tannery case that User Story 4 requires; the edge case making a new element drawn with an existing
  glyph owe the glyph check only conditionally (NOT LEGITIMATE: a new element is the occasion, whatever its mark); User Story
  1's "where the same question arises" narrowing its own acceptance; the contract's size unlabeled and stale (48k vs 49,960).
  Addressed: the example struck and a new or changed placement rule stated as an occasion; an element new to the map owes the
  glyph check whatever its mark (User Story 4, FR-007, SC-002 seeded); the phrase struck; the size measured and labeled.
- Round 2 (spec-fidelity-verify, 2026-10-01): CHANGES REQUIRED, 1 item - the item-2 fix not carried into User Story 1's audit
  question 3 and the Summary, which still said "a glyph added". Addressed: both now say an element added whatever its mark.
- Round 3 (spec-fidelity-verify, 2026-10-01): FAITHFUL. Every passage stating the glyph check's occasion agrees.
- Amendment pass, round 1 (spec-fidelity-verify, 2026-10-01): CHANGES REQUIRED, 2 items - the legacy-pool edge case faithful to
  the GM's ruling; SC-004's labels FR-011 and FR-012, and SC-002's label FR-006, name requirements those criteria do not
  measure. Addressed: FR-011 and FR-012 off SC-004, measured by new SC-007 and SC-008; SC-002 extended with FR-006's clause.
- Amendment pass, round 2 (spec-fidelity-verify, 2026-10-01): CHANGES REQUIRED, 2 items - SC-004's labels fixed and SC-007
  faithful; SC-002's new clause dropped FR-006's "unless a check needs it as input" exception and named an undefined "unit";
  SC-008 narrowed User Story 8's cheaper tier to Sonnet and recorded outside the ledger. Addressed: both replaced with the
  reviewer's wording.
- Amendment pass, round 3 (spec-fidelity-verify, 2026-10-01): FAITHFUL - SC-002's FR-006 clause keeps the as-input exception
  and names "element"; SC-008 names both cheaper tiers and records in the ledger and the tier table. The amendment is accepted.
