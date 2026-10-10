# Feature Specification: The implementation brought to the research - the rows feature 328 left open

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=372-match-the-research-remaining`)

**Created**: 2026-10-10

**Status**: Draft (specified 2026-10-10 from its filed form)

**Input**: `request.md` - feature 328's request, carried on: bring the implementation to the research it cites, easiest
first, for the code the scripted hamlets, the magistracies and the country shrines execute; split off 328 at its wave 97
(328's FR-011) and started at once, *"pick up where you left off"*.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The fixes go on where 328 stopped (Priority: P1)

The GM, back from 328's landing, finds the next rows of the ranking being fixed in order, each wave verified as 328's were,
and each batch landing on main as it closes, so other work branches off it.

**Independent Test**: the ranking's open rows fall wave by wave; `make claims-report` shows their findings gone and no new
one; each batch's commits are on main.

### User Story 2 - The GM's decisions are gathered, not waited on (Priority: P1)

What only the GM can decide is collected here and put to the GM at the feature's end or when the GM asks, never blocking
the work in between (328's goal amendment).

**Independent Test**: every held item names what was searched and found; no task waits on an answer while other rows stand
open.

### Edge Cases

328's edge cases hold unchanged (a fix that would change the research instead; a hand-drawn Mode A sheet; a fix that changes
many maps; a newly failing cohort seed is a regression, reverted with its measurement).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (the starting point)**: the work list is everything listed under "What it carries" below - 328's ranking's open
  in-scope rows at wave 97 (`specs/328-match-the-research/ranking.json`, rows with no wave and not deferred), the findings
  the claims gate counted as introduced at 328's landing, the waived zigzag, the found rows, the efficiency item. 328's
  tiers (its FR-003) and its order stand; a row fixed here is marked with its wave in 328's ranking (`audit/waves.json`), so
  one ranking stays the one record.
- **FR-002 (328's rules carried)**: 328's FR-002 (the measure is implementation work), FR-003 (tiers), FR-004 (the direction
  of a fix), FR-005 (verification per fix, batched), FR-008 (the record of decisions, in this spec's Decisions Recorded),
  FR-009 (hand-drawn maps) and FR-010 (scope) apply here as written there.
- **FR-003 (waves land per batch)**: a batch of 4-5 waves closes as 328's did (the gate, the occasions, one timing pair and
  its `perf-audit`) and LANDS when it closes: this feature's tasks are the current batch's, so the open-task refusal clears
  at each close. A batch is never stacked unpushed behind another (the GM's reason for the split).
- **FR-004 (the usage cap)**: 328's FR-007, at the cap the GM last set for this work, `90%` of the weekly window (armed with
  `~/.claude/hooks/usage_cap.py`).
- **FR-005 (decisions)**: a question for the GM is recorded with what was searched and found, and work moves to the next
  row; the held list is put to the GM at the feature's end (FR-002's exception path still goes to `spec-fidelity` first).
- **FR-006 (the filed features)**: a filed feature listed below is folded in only when the GM chooses it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): after each wave, every row it took re-checks IN-STEP under `impl-drift`, and `make
  claims-report`'s count of in-scope findings falls by at least that many with no new one.
- **SC-002** (FR-003): every closed batch is on main, its gate green, its pair band recorded and audited.
- **SC-003** (FR-004, FR-005): at the cap or the end, the clone holds no uncommitted work and no unrecorded verdict, and the
  held list for the GM is complete.
- **SC-004** (FR-001, FR-006): at the end, `make claims-report` shows 0 in-scope findings outside the DEFERRED units, or each
  that remains names its held decision.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|

## Assumptions

- 328's records (`ranking.json`, `measurements.json`, `audit/`, `claims-followup.md`) are the starting state and stay in
  328's directory; this feature's measurements are its own `measurements.json`.
- The cohort baseline is 52 of 54 at 328's landing (seeds 10 and 20 refused).

## What it carries

- **The open rows of 328's ranking at wave 97**, in ranking order: 204 rows in scope (`kept` 166, `mode-a` 38) - 161 E3,
  42 E4 (a research pass under the record's own checks before any code change) and 1 E2 held for the GM (`fixture_quota`).
  The ranking, its audit and every record stay in `specs/328-match-the-research/` (`ranking.json`, `ranking.md`,
  `audit/`, `measurements.json`); a row this feature fixes is marked with its wave there or carried over, as its plan
  decides. Each row's fix text carries what 328 measured and tried (the held E3 rows name their reverted waves and
  measurements: waves 83-86, 91, 96).
- **The findings the claims gate counted as introduced at 328's landing** (`introduced-at-328-landing.txt`, 25 and the two touch.py findings of its last re-check, against
  main at wave 8): the re-checks of 328's waves found them, most of them rows of the ranking above, some not ranked (new
  claims the re-checks asked for, and drifts on rows a wave had closed - `belt_law` holes, the unkept yard's south band,
  `build_polder`'s low rows). 328 landed with them by the GM's split (`CLAIMS_OK` naming it); each is a row here.
- **Sawada's zigzag across a joint** (328's T137, lanes 1/3, on the strict `_ZIGZAGS_WAITING`), WAIVED by the GM for 328's
  landing (*"Waive it"*, 328's `request.md`): its fix - re-lay a household's way at seating so it never arrives inside another's
  dooryard (328's plan, wave 54; two seating guards tried and reverted) - is an open E3 row here.
- **A found row from 328's close**: the 40-household roll of seed 25, refused through 328's batch 3 (its T140), draws at
  328's close but carries one lane knot under the cohort's knot rule (lanes 1 and 2, 23.8 ft apart;
  m:t140-seed25-at-head) - the knot rule of 0081 held at 40 households.
- **Every decision still owed to the GM** (the GM, 2026-10-10: *"Anything that we'd need by decision for the existing feature
  can be spun out into the other feature"*): the whole "Held for the GM" section of 328's `claims-followup.md` - among them
  the `bath_seat` settlement choice, row 427's `fixture_quota`, wave 86's privy over the sty, 0006's one-season decision,
  the items raised for the GM's information (waves 80, 82, 94, and the two readings of 0246's serving reach) - and two
  raised at 328's close: the Mode A wells, drawn as location markers the GM confirmed on 2026-07-21 against 0196's curb of
  about 4 ft (`docs/buildings.md`, Scale), and wave 97's charcoal store kept where it stood across its loading apron
  (m:wave97-ubame-charcoal; spec-fidelity ruled it LEGITIMATE, raised under constitution XVI).

- **An efficiency item from 328's landing pair**: `capacity.field_distances` (wave 20's seat-order tie toward the field)
  computes a ring distance for every free grid point but uses it only to break ties within one grid pitch - 0.166 s of the
  homesteads stage at 40 households, seed 47 (m:landing-pair-40hh-field-tie in 328's records); compute it only for the tied
  candidates.

## The filed features, sorted (328's close, 2026-10-10)

The GM asked which of `make speckit-todo`'s filed features relate to this work and which are future work for the tiers that
are not hamlets. A feature is folded into this one only as the GM chooses.

**Related - the scripted hamlets, the magistracies and country shrines, or the research behind them:**

- *A drawn thing that disagrees with its research* (closest to this feature): 353 (the shared byre on the commons rolled
  on no evidence), 357 (the modern-only items left on the hamlets, e.g. wayside stones), 358 and 359 (the settlement-reviews'
  measured findings on the scripted hamlets - the privy's sun-side share, a far-row grove and its strip), 360 (a tree run
  crossing water off square is refused, not straightened), 362 (the connector through the belt's windward corner), 341 and
  342 (Mode A door glyphs outside their walls; the torii drawn in elevation where the procedure says plan), 335 (the
  magistracies' rear strips), 368 (three loose ends in the privy record, 0047).
- *Research questions owed on the magistracy sheets*: 336 (Takayama's guest route), 337 (a roofed hearing court's size),
  338 (the Koseki middle gate), 339 (Hayakawa's stepped landing), 343 (is the receiving court "swept"), 352 (a lane between
  a house and its own grove).
- *Presentation on the hamlet and sheet pages*: 340 (the program example's captions), 346 (lighting a watercourse paints
  over what crosses it), 348 (hamlet labels in the zoomed-out hit map), 349 (rename `grave island` to `field grave`), 355
  (the head race's width and hue at the tap), 356 (two ways meeting where the material changes), 361 (the notes census and
  the storehouse annexes).
- *A new knob the GM has ruled on*: 369 (the season a hamlet's fields show).
- *Tooling, any tier*: 345 (the push-time roll-review agent), 347 (measure 274's write cap), 370 (a function-length gate),
  371 (a ledger row for every recorded review verdict, filed by 328's session).

**Future work for the tiers that are not hamlets** (owed at their conversion, or a direction): 331 (fold `city/civic.py`),
332 (town, city and capital captions through the one placer), 333 and 334 (the scripted city; the frozen cities' modern-only
forms), 344 (fabric-first generation, a research direction), 350 and 351 (a village's funerary grounds and headman's gate;
its shrine grove), 354 (seasonal maps, deferred by the GM), 363 (the kiln glyph, on the towns), 364-367 (the frozen towns:
modern-only forms, the enclosed-fan floor, generator parity, the deep audit's items).

## How it starts (328's precedent)

The cohort baseline is 52 of 54 (`make cohort N=48`, seeds 10 and 20 refused) and a newly failing seed is a regression,
reverted with its measurement (328's precedent). The wave cycle, the batch close every four or five waves, and the review
occasions are 328's (`specs/328-match-the-research/plan.md`).
