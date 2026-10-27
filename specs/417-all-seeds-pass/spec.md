# Feature 417: all seeds pass - every rule asked before a thing is placed, nothing placed and repaired

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: hamlet, tooling

**Approved**: the GM, 2026-10-24, "we might want to put our claims work on hold and then open a new feature whose goal is "all seeds passing""

Asked "Shall I file the feature with this scope?" once the scope below was settled in the session, the GM replied "Yes please".

**Input**: `request.md`

## The gap (measured 2026-10-24)

Feature 405 T106 (a wood shed's first seat by its household's roll) could not land: each way of giving it room cleared the
map it was for and broke other cohort seeds (53, 53, 51 and 47 of 54; `specs/405-engine-findings-from-385/t106-knots.md`).
The 48 fixed cohort seeds pass because they are the landing gate; seeds the gate has never seen do not. Every fresh seed
rolled since 2026-10-20 (counted from `dev/cohort-log/*.json`: each record's seeds at or above its `fresh_first`, by
`verdict` and `failures`; `make cohort-seeds` prints the per-record rates): **360 of 2,544 failed (14%)** - linear 158 of 546 (29%),
nucleated 166 of 1,257 (13%), dispersed 36 of 741 (5%). A change that moves anything early re-deals every later choice, so
each fixed seed becomes a fresh one, and at 14% a few of 48 break by chance whatever the change was.

By cause (a seed may fail more than one):

| cause | failures | where |
|---|---|---|
| the lane web refused (`WebRefused`) | 114 | `hamletgen/ways/last_resort.py` |
| lane ends knotted (`lane_knots`) | 107 | `cohort_audit`, `ways/knots.py` |
| a site that seats too few households (`SiteRefused`) | 55 | `hamletgen/homesteads/stages.py` |
| a linear village's row rules | 31 | `homesteads/row_rules.py`, asked only of the finished map |
| overlap (`OverlapRefused`) | 19 | `overlap/registry.py` |
| a farmstead part across the brook from its house | 16 | `cohort_audit` only |
| the rest (sink, value errors, groves crossed by lanes, brook, decks, dry exit, water, shade) | 22 | |

THE PATTERN. The lane web is laid and then repaired: `settle_the_web` (`ways/settle/stage.py`) loops sixteen repair steps (seventeen entries in `STEPS`, `settle_husks` twice)
until a round changes nothing, drops the ordinary lanes it cannot mend and refuses the map otherwise (feature 287 M4 chose
this to replace the driver's re-roll). One repair can undo another, which is why seed 7's knot fix and Sawada's knot fought.
Other rules are asked only of a finished map, so the generator never knows it broke them. Placement (297), the field (302)
and the overlap registry's `admits` (287 M8) were rebuilt to ask before placing, but feature by feature: no rule of the
constitution says so, and the pattern survives elsewhere.

## The rule (the method of this feature)

1. Every rule a map keeps is ONE predicate, asked of a candidate before it is placed: a placer offers only what the rule
   admits.
2. Nothing is placed and then repaired.
3. A finished-map check is a backstop that calls the same predicate; it lives in the cohort and the tests, never in the
   generator's run, and its firing is an engine defect.
4. Where no candidate is admitted, the answer is more room (the GM, 2026-10-12, "room before packing"), never a repair.

## User Scenarios & Testing

### User Story 1 - The GM rolls any seed and gets a map (Priority: P1)

Whatever seed, size or form the GM asks for, the generator produces a map that keeps every rule; no seed is refused and no
map ships with a broken rule.

**Why this priority**: it is the goal (the GM: "a solid baseline where everything already there functions as expected").

**Independent Test**: a large block of fresh seeds, never used by the gate, rolled at the cohort's sizes and forms; count
failures.

**Acceptance Scenarios**:

1. **Given** the engine at this feature's close, **When** a fresh block of the agreed size is rolled across every form,
   **Then** none fails.
2. **Given** a seed that failed in the 2026-10-24 tally, **When** it is rolled again, **Then** it passes.

### User Story 2 - A change to one stage does not break seeds elsewhere (Priority: P1)

A session changes where something sits (405 T106's seat turn is the case) and the fixed cohort and a fresh block still
pass, because the later stages place by their rules on whatever ground they are dealt.

**Independent Test**: re-apply T106's seat turn on the closed engine and roll the cohort and a fresh block.

**Acceptance Scenarios**:

1. **Given** the closed engine, **When** T106's seat turn (reverted 2026-10-24) is applied, **Then** the fixed cohort and a
   fresh block pass, or a failure names a rule the seat turn itself breaks.

### User Story 3 - Later features are held to "all seeds pass" (Priority: P2)

Once the rate is at its target, a landing that makes any fresh seed fail is refused (the GM: "we can make 'all
seeds pass' a hard requirement for later features, including when we resume feature 405").

**Acceptance Scenarios**:

1. **Given** the target is met, **When** an engine change makes a fresh seed fail, **Then** `make land` refuses it and names
   the seed and the rule.

### User Story 4 - There is less code, not more (Priority: P2)

The repair passes, any rule coded twice and the checks the generator runs mid-map are deleted; each rule is one predicate
(the GM: "That's extra code to maintain, extra tests, and extra tokens").

**Acceptance Scenarios**:

1. **Given** the inventory (FR-002), **When** the feature closes, **Then** every entry in it is deleted or rebuilt to ask
   before placing; an entry the session believes must stay goes to `spec-fidelity` as a proposed exception (MODE 1) and
   stays only on a LEGITIMATE ruling.

### User Story 5 - A roll costs an order of magnitude less (Priority: P1)

The GM, 2026-10-26 (`request.md`, "Speed first"): "we should explicitly make it one of the goals of 417 to get the kind of
order of magnitude decrease that we believe should be possible based on the feature that we just completed". Feature 427 cut a
40-household roll from 62.6M Python calls (observed 2026-10-26, method: `make perf-fanout`, 427's T01 survey) to 29,717,755 once its
families outside the lanes landed (its T09; its T10, the web's pairwise chains, waits on this feature's lane conversions) (observed 2026-10-27, method: `make perf-fanout` at fb19852b5, `dev/perf-log/20261027T030656Z-fanout-417-start.txt`) by
removing per-pair overhead; what is left is structural. Placing
then repairing is this feature's FR-004 to FR-006. Search by trial is not: a placer lays a candidate out in full - a homestead
with its fixtures, a way traced and pulled taut, a well through the registry - and only then refuses it, and a whole-network
check is asked again of the whole network as it grows. Measured 2026-10-26 (method: `make perf-profile SEED=39 HOUSEHOLDS=40`,
profiled seconds): the households' ways traced and judged 1.6 s, the seating's 160 placements and 416 full reach measures for 40
houses 1.6 s, the web's settle 1.13 s, and its `served_network` check asked 45 times over every pair of lanes 0.86 s. The GM
orders the work speed first, "because once we make things faster, then it will be easier to make them correct, because we will
be able to iterate much more quickly."

**Independent Test**: `make perf-fanout` at 40 households, seed 39, totals at most SC-009's bound; the profiles show no placer
laying out in full a candidate a test needing no layout refuses.

### Edge Cases

- A rule that can only be judged on the whole map (a lane laid after a house crossing that house's grove): the LATER placer
  asks it of its own candidate against what already stands; the finished-map check stays as the backstop.
- A site too small for its households: more room within the research; a number with no research behind it is a knob to move
  (the GM, 2026-10-12).
- A hand-drawn or frozen map: out of scope (frozen maps need not run, feature 392).
- Maps change: they are held to the research claims and the rules, not to identical output.

## Requirements

### Functional Requirements

- **FR-001 (measure)**: the fresh-seed failure rate is measured on a block large enough to show a rate near zero (its size
  set in the plan from the measured cost of a block), by form and by cause, at the start and after each task that changes
  the engine.
- **FR-002 (inventory)**: every repair pass, every rule asked only of a finished map, every rule coded more than once and
  every finished-map check run inside the generator is listed, each with where it is and which of the rule's four points it
  breaks.
- **FR-003 (the rule)**: the rule above becomes a principle of the constitution, in text the GM approves.
- **FR-004 (the lane web)**: lanes are laid only where the lane law admits them; the settle's repair steps and the passes
  that repair a laid web are deleted. Each lane-law rule stays one predicate in `law.py`.
- **FR-005 (rules into their placers)**: each rule now asked only of a finished map (row rules, a farmstead part across the
  brook, groves crossed by lanes, and the rest the inventory finds) is asked by the placer that could break it.
- **FR-006 (one check per rule)**: each finished-map check calls its placer's predicate, and runs in the cohort and the
  tests only; a second implementation of a rule is deleted; every check the generator runs on what it has already placed is
  deleted - what stays in the generator is the predicate asked of a candidate before it is placed.
- **FR-007 (room, never repair)**: where a placer finds no admitted candidate, the remedy is more room within the research.
- **FR-008 (no regression)**: the fixed cohort, the pinned rows and the pool maps keep passing at every landing; the
  research claims hold.
- **FR-009 (the hard requirement)**: once SC-001 is met, the fresh block runs inside `make land` BEFORE the push, and
  `make land` refuses an engine landing any of whose fresh seeds fails, naming the seed and the rule (this replaces feature
  415 D5's "a rate, never a refusal", under which the fresh block runs after the push).
- **FR-010 (the claims work on hold)**: no task of a claims feature that changes the engine - 405, 372, 384 and any other
  claims feature the session finds - is started until this feature closes.
- **FR-011 (feature 394, folded in - the GM 2026-10-24: "Yes fold 394 into 417")**: with FR-009, and as 394 specified:
  every archetype form's seeds - the unrolled field forms (polder, dike-pond: `ROLLED_ARCHETYPES` holds only the valley
  fan) as well as the rolled ones - are run and recorded per seed, keyed on the engine (a cached seed is not rerun); a
  landing's seeds are compared with HEAD's, and newly red seeds are listed with their form and failure; the gated route
  refuses a NEWLY red seed (green at HEAD, red at the landing) that no filed row (in an open feature) or arbiter waiver names,
  the refusal naming the seed, its form and the command to file the row or ask the arbiter; a seed red at
  HEAD and still red is not refused, one red at HEAD and green at the landing is reported fixed, and a form new to the
  archetypes is recorded, not judged, on its first landing. 394's deferral ("once we are in a place where we think that all
  seeds should pass, then I want that feature to be implemented") is met by building it after SC-001. FR-011's exemptions (a filed row or waiver, a seed already red at HEAD) apply
  only to the forms FR-008 and FR-009 do not hold to zero - the unrolled field forms; a rolled-form seed that fails is refused
  under FR-008 / FR-009 whatever HEAD shows or a row says.

- **FR-012 (search by construction; the GM 2026-10-26, `request.md` "Speed first")**: every placer that lays a candidate out
  in full and then refuses it, and every check asked again of a whole network as it grows, is listed (as FR-002 listed the
  repair passes), each with its measured calls; where a candidate set is offered, the refusals that need no layout are asked of
  the whole set at once (an array, a raster or an index) before any candidate is laid out, and a network check is asked of
  what changed, not of the whole network again.
- **FR-013 (speed first; the GM 2026-10-26)**: the tasks that cut a roll's calls - FR-012's, and FR-004's and FR-006's where
  they delete repair work - are worked before the tasks that only make seeds pass, ordered by the calls each removes.

### Key Entities

- **A rule**: one predicate; its placer; its finished-map check.
- **A fresh block**: seeds the gate has never used, rolled at the cohort's sizes and forms.
- **The inventory**: the list FR-002 makes, the feature's task list grows from it.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005, FR-006, FR-007): no failures on the agreed fresh block across every form (0 of N; N in the plan, at least 500).
- **SC-002** (FR-004): the lane web has no repair loop: a settled web needs no changes after it is laid.
- **SC-003** (FR-005, FR-006): every rule has one implementation, asked by its placer and by its finished-map check.
- **SC-004** (FR-004, FR-006): the engine is smaller at close than at start, by the lines of the passes deleted.
- **SC-005** (FR-009): a landing that makes a fresh seed fail is refused.
- **SC-006** (FR-011; 394's SC-001/SC-002): a test landing that turns one unrolled-form seed red with no filed row is refused,
  naming the seed and its form; the same landing with a filed row naming it lands.
- **SC-007** (FR-002, FR-003, FR-010): the inventory lists every repair pass, rule asked only of a finished map, rule
  coded more than once and finished-map check run inside the generator, each with where it is and which of the rule's four
  points it breaks, and every entry that breaks a point has a task; the principle is in the
  constitution in the GM's approved words, and `make task-start` refuses an engine task of a held feature.
- **SC-008** (FR-008): every engine landing of this feature passes the fixed cohort, the pinned rows and the pool maps, and
  the research-claims round (`make land`).

- **SC-009** (FR-012, FR-013, User Story 5): a 40-household roll (seed 39, `make perf-fanout`) makes at most 6.3M Python
  calls - a tenfold cut from feature 427's start of 62.6M (observed 2026-10-26, method: `make perf-fanout`, 427's T01 survey).
  The bound is a GUESS at what a by-construction engine reaches (the session's estimate 2026-10-26: 3-6M, from a few hundred
  candidate seats a house each asked a couple of dozen indexed questions); stage times are reported beside it and gate nothing
  (feature 427 FR-006). The GM saw this bound and its baseline in the session's proposal ("SC-009: at most 6.3M ... a tenfold cut
  from 427's start of 62.6M") before answering "Sounds great. I confirm that this is good" (`request.md`).

## Assumptions

- The unrolled field forms (polder, dike-pond) are guarded against regression (FR-011); turning them on, and holding them
  to zero failures, is a later choice, as `ROLLED_ARCHETYPES`' own note says ("opt-in until their cohort is green").
- The cohort's sizes, forms and pins are the population "any seed" means; a new form or tier is a later feature's.
- The fixed 48 stay the landing gate; the fresh block is added beside them, not in place of them.
- Timings are a flag, never a gate (375 amendment 5, feature 427 FR-006); the call count is this feature's goal (SC-009), watched
  by feature 427's call-count watch. (Before 2026-10-26 this read "a by-construction placer may be slower"; the GM's speed goal
  replaced it.)

## Review history

- spec-fidelity round 1 (2026-10-24): CHANGES REQUIRED - the hold named only 405 where the GM held "our claims work" (FR-010
  now holds 405, 372 and any other claims feature that changes the engine; 372's status says so); "or kept with a recorded
  reason" was an exception the session granted itself (now a MODE 1 ruling); FR-009 could not refuse a landing whose fresh
  block runs after the push (now runs before it, and any fresh failure refuses, User Story 3 aligned); FR-006's "only to
  trigger a repair or a refusal" narrowed the approved deletion (now every check the generator runs on what it placed); the
  approval line stopped before the feature's name (now quoted through "all seeds passing", "Yes please" noted). Its aside
  taken: sixteen repair steps, not fifteen; the tally's method stated.
- spec-fidelity round 2 (2026-10-24): CHANGES REQUIRED - FR-010's catch-all ("any other the inventory finds") could find
  no feature, since the inventory lists code, and 384 (match the research, the remainder) was not held: 384 named, the
  catch-all made "any other claims feature the session finds", and 384's status says ON HOLD.
- spec-fidelity round 3 (2026-10-24): CHANGES REQUIRED - the hold was spliced into the middle of 384's status sentence, so
  "until 385 closes" followed the GM's quote; the sentence rejoined, the hold after it.
- spec-fidelity round 4 (2026-10-24): FAITHFUL.
- spec-fidelity amendment round 1 (2026-10-24, the 394 fold): CHANGES REQUIRED - FR-011's exemptions (a filed row, a seed
  red at HEAD) conflicted with FR-008/FR-009's zero on the rolled forms (now limited to the unrolled field forms); the fold
  dropped 394's listing with form and failure, "in an open feature" and the refusal naming the form (restored; SC-006 names
  the form).
- spec-fidelity amendment round 2 (2026-10-24): FAITHFUL.
- spec-fidelity SC round 1 (2026-10-24, spec-lint's FR names on each SC): CHANGES REQUIRED - SC-001 cannot measure FR-008
  (now SC-008); SC-007's first clause measured only the tasks (now FR-002 in full). Aside taken: SC-004 names FR-004.
- spec-fidelity SC round 2 (2026-10-24): FAITHFUL.
- spec-fidelity-verify speed-first amendment round 1 (2026-10-26; the hook's round 2 of the pass - the NOT-REVIEWABLE
  return before it reviewed nothing and does not count): CHANGES REQUIRED - User Story 5 says feature 427 cut a 40-household
  roll "to 30,974,895", but the cited log (`dev/perf-log/20261026T222703Z-fanout-427-T09-start.txt`) is the survey from the
  START of 427's T09. Commit 7307453e2 added that log, and its message records a further cut made after it ("field 4.07M ->
  2.93M at 40 hh"). The same paragraph's profile seconds were taken after T09 (fb19852b5), so the passage mixes two engine
  states. The fix: say the count is from T09's start and that T09 then cut the field, or cite a new all-stages
  `make perf-fanout` at 40 households (none taken after T09 is in `dev/perf-log/`). The rest of the amendment matches the
  GM's "Speed first" words and his confirmation: User Story 5, FR-012, FR-013, SC-009 (62.6M confirmed, 62,648,969 in the
  T01 survey) and the last Assumption.
- spec-fidelity-verify speed-first amendment round 2 (2026-10-26; the hook's round 2 of the pass, as round 1 was): CHANGES REQUIRED - round
  1's item is RESOLVED in substance: 29,717,755 at 40 households is line 159 of
  `dev/perf-log/20261027T030656Z-fanout-417-start.txt`, taken at fb19852b5 after 427's T09 landed (f28012335). But the new
  words "once its last task landed" are false: 427's T10 (the web's pairwise chains, waiting on this feature's lane
  conversions) and T11 (its bookend) are open in `specs/427-call-volume-refactors/tasks.md`. Say "once its families outside
  the lanes landed (its T09; T10, the web's pairwise chains, waits on this feature's lane conversions)", as `request.md`
  puts it. And `inventory/trial.md` row 2 gives homesteads as 6.9M. The survey it cites gives 6,537,670 at 40 (6.5M); 6.9M
  (6,940,802) is an earlier log's count. Its other stage totals match the survey. SC-009's new sentence is true: the session's proposal of 2026-10-26 said "at most 6.3M Python calls, a tenfold
  cut from 427's start of 62.6M" before the GM confirmed. That proposal is in the session transcript, not `request.md`;
  this does not block. The plan.md, tasks.md T14 and `inventory/trial.md` changes match the GM's 2026-10-25 and 2026-10-26 words.
- spec-fidelity-verify speed-first amendment round 3 (2026-10-26; the hook's round 3 of the pass): FAITHFUL - round 2's two
  items RESOLVED: User Story 5 now says 427 reached 29,717,755 "once its families outside the lanes landed (its T09; its
  T10 ... waits on this feature's lane conversions)", true against `specs/427-call-volume-refactors/tasks.md` (T09 ticked,
  T10 and T11 open) and `request.md`'s "landed its families outside the lanes"; `inventory/trial.md` row 2 reads 6.5M, the
  survey's 6,537,670 at 40. T56's task line and plan block now name the notice board's seats (trial.md rows 6-11) in place of
  the labels, which trial.md lists as needing no task. plan.md's D5 note (FR-013 governs the order; the list matches the
  Order section and the GM's 2026-10-26 confirmation) and the D11 AMENDED and T16 item 1 wording (downloaded research
  checked first, a research pass where nothing was looked for, then a GUESS or a tunable knob) follow the GM's 2026-10-25
  and 2026-10-26 words. That plan text's Decisions block is still BLOCKED in `plan-review.json` until a spec-fidelity plan
  review rules on it again; this round records no plan verdict.
