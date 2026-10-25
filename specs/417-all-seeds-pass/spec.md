# Feature 417: all seeds pass - every rule asked before a thing is placed, nothing placed and repaired

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: hamlet, village, tooling

**Approved**: the GM, 2026-10-24, "Should we just get rid of it as part of this new feature we're scoping?"

Answered with the scope this spec files, the GM replied "Yes please".

**Input**: `request.md`

## The gap (measured 2026-10-24)

Feature 405 T106 (a wood shed's first seat by its household's roll) could not land: each way of giving it room cleared the
map it was for and broke other cohort seeds (53, 53, 51 and 47 of 54; `specs/405-engine-findings-from-385/t106-knots.md`).
The 48 fixed cohort seeds pass because they are the landing gate; seeds the gate has never seen do not. Every fresh seed
rolled since 2026-10-20 (`make cohort-seeds`, `dev/cohort-log/`): **360 of 2,544 failed (14%)** - linear 158 of 546 (29%),
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

THE PATTERN. The lane web is laid and then repaired: `settle_the_web` (`ways/settle/stage.py`) loops fifteen repair steps
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

Once the rate is at its target, a landing that raises the fresh-seed failure rate is refused (the GM: "we can make 'all
seeds pass' a hard requirement for later features, including when we resume feature 405").

**Acceptance Scenarios**:

1. **Given** the target is met, **When** an engine change makes a fresh seed fail, **Then** `make land` refuses it and names
   the seed and the rule.

### User Story 4 - There is less code, not more (Priority: P2)

The repair passes, any rule coded twice and the checks the generator runs mid-map are deleted; each rule is one predicate
(the GM: "That's extra code to maintain, extra tests, and extra tokens").

**Acceptance Scenarios**:

1. **Given** the inventory (FR-002), **When** the feature closes, **Then** every entry in it is deleted, or rebuilt to ask
   before placing, or kept with a recorded reason.

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
  tests only; a second implementation of a rule is deleted; a check the generator runs mid-map only to trigger a repair or a
  refusal is deleted.
- **FR-007 (room, never repair)**: where a placer finds no admitted candidate, the remedy is more room within the research.
- **FR-008 (no regression)**: the fixed cohort, the pinned rows and the pool maps keep passing at every landing; the
  research claims hold.
- **FR-009 (the hard requirement)**: once SC-001 is met, `make land` refuses an engine landing whose fresh block fails, naming
  the seed and the rule (this replaces the 2026-10-24 "a rate, never a refusal" for the fresh block).
- **FR-010 (405 on hold)**: no feature 405 task is started until this feature closes.

### Key Entities

- **A rule**: one predicate; its placer; its finished-map check.
- **A fresh block**: seeds the gate has never used, rolled at the cohort's sizes and forms.
- **The inventory**: the list FR-002 makes, the feature's task list grows from it.

## Success Criteria

- **SC-001**: no failures on the agreed fresh block across every form (0 of N; N in the plan, at least 500).
- **SC-002**: the lane web has no repair loop: a settled web needs no changes after it is laid.
- **SC-003**: every rule has one implementation, asked by its placer and by its finished-map check.
- **SC-004**: the engine is smaller at close than at start, by the lines of the passes deleted.
- **SC-005**: a landing that makes a fresh seed fail is refused.

## Assumptions

- The cohort's sizes, forms and pins are the population "any seed" means; a new form or tier is a later feature's.
- The fixed 48 stay the landing gate; the fresh block is added beside them, not in place of them.
- Speed is a flag, never a gate (375 amendment 5); a by-construction placer may be slower and is mentioned if it is.
