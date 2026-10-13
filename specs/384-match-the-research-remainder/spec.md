# Feature Specification: Match the research - the remainder (the work feature 374 left open)

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=384-match-the-research-remainder`)

**Created**: 2026-10-13

**Status**: Filed - the open work of feature 374 (itself 372's and 328's remainder), moved here at the GM's word; not resumed
until the GM has decided how the work should go faster ("How it starts")

**Approved**: the GM, 2026-10-13, "move all of the remaining work to a new feature and then close out this feature and land it on main"

**Affects**: hamlet, magistracy, research record

**Input**: `request.md` - the GM, 2026-10-13: finish the task in hand, then *"move all of the remaining work to a new feature
and then close out this feature and land it on main. because I think that we probably need to figure out how to make this go
faster"*; 328's, 372's and 374's requests carry over unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The fixes go on where 374 stopped, faster (Priority: P1)

The GM, having decided how the work should go faster, finds the next rows of 328's ranking being fixed, each verified as 374's
were, and each batch landing on main as it closes.

**Independent Test**: the ranking's open rows fall wave by wave (`audit/waves.json` marks each with its wave); `make
claims-report` shows their findings gone and no new one; each closed batch's commits are on main.

### User Story 2 - The web carries a re-deal of the seats (Priority: P1)

The rows that move where homesteads are seated (787, 777 and the E3 seating rows) wait on one found row: re-dealt seats knot or
refuse the lane web on a few cohort seeds. With the web settled, those rows land with no waiver.

**Independent Test**: a 48-seed cohort with the wave 155 patch applied fails no seed that passes at HEAD (`m:w156-redeal-cohort`
is the baseline: HEAD 50/54, patched 49/54).

### Edge Cases

374's edge cases hold unchanged (a fix that would change the research instead; a hand-drawn Mode A sheet; a fix that changes
many maps; a newly failing cohort seed is a regression, reverted with its measurement; a guard that refuses correct work is
fixed, not escaped).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (the starting point)**: the work list is everything under "What it carries" below - 328's ranking's open rows at
  374's close (`specs/328-match-the-research/ranking.json`, rows with no wave: 325, E0 8, E1 36, E2 64, E3 158, E4 59), 374's
  open tasks and its carried items. 328's tiers and order stand; a row fixed here is marked with its wave in 328's ranking
  (`audit/waves.json`), waves numbered on from 374's (the next is wave 156), so one ranking stays the one record.
- **FR-002 (the rules carried)**: 374's FR-002 to FR-007 apply here as written there (`specs/374-match-the-research-continued/spec.md`),
  as amended by 375 (the performance pair a flag stated at landing) and 383 (the hourly step-back), except where the GM's
  decision on speed (FR-003) changes them.
- **FR-003 (speed first)**: no wave is taken until the GM has decided how the work should go faster (the request: *"we probably
  need to figure out how to make this go faster"*). Measured for that decision (374's event log, `make feature-report F=374`):
  328's `waves.json` gained nine rows from 2026-10-12 18:00 to 374's close (batches 15-18, which landed between 01:40 and
  07:57 on 2026-10-13 by their commits); batch 19 (row 787) was built, measured and reverted.
- **FR-004 (the usage cap)**: 374's FR-003, the cap at 90% of the weekly window, armed with `~/.claude/hooks/usage_cap.py`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002): after each wave, every row it took re-checks IN-STEP under `impl-drift`, and `make claims-report`'s
  count of in-scope findings falls by at least that many with no new one.
- **SC-002** (FR-002): every closed batch is on main, its gate green, its performance flag stated at landing.
- **SC-003** (FR-001): at the end, `make claims-report` shows 0 in-scope findings outside the DEFERRED units; the held list goes to
  the GM through `escalation-check`, and a row the GM rules should stay becomes a Decisions Recorded row.
- **SC-004** (User Story 2): the re-deal cohort (`m:w156-redeal-cohort`'s method) fails no seed that passes at HEAD before wave
  155 re-lands.

## What it carries

- **374's open tasks**:
  - T48 (wave 156): the web carries a re-deal of the seats - the found row `settle_the_web#a re-deal of the seats`
    (`audit/found-wave149.jsonl`, E4), which rows 777 and 787 wait on (ask:w155-cohort-seed10). Its baseline is measured
    (`m:w156-redeal-cohort` in 374's `measurements.json`).
  - T47 (wave 155): the pocket well off its farmstead - built, measured (`m:w155-wells`) and reverted on the round arbiter's
    ruling; its whole diff is `specs/374-match-the-research-continued/w155-pocket-attempt.patch`, re-landed once T48 lands, no waiver.
  - T33 (wave 141): the polder and the dike-pond rolled beside the valley fan once their rolls are green (0019, 0020).
  - T99: the ranking's remaining open rows, batch by batch.
- **Four cohort seeds failing at HEAD** (found by T48's 48-seed baseline, 2026-10-13; constitution XIV, fixed in the first
  batch): 17 and 21 (WebRefused, nucleated), 40 (`row_rules` farm_not_on_its_street, linear), 45 (`fixtures_on_groves`: a pig
  sty on its own farm's grove bands, dispersed - the sty seated by wave 151).
- **374's "What it carries" items still open**: every held decision for the GM (374's spec, "Every decision still owed to the
  GM", and 374's `gm-review.jsonl`), the items carried from 372, and the tooling gaps not yet fixed - as listed in 374's spec.
- **The GM's open question from 374**: whether the three hand-drawn magistracy sheets can be redrawn as smaller compounds
  around a 49-67 tsubo residence (the session's recommendation: yes).

## How it starts

When the GM has decided how the work should go faster (FR-003): `make task-start`, the first batch's plan section with its
decisions (`make decide`), the four pre-existing cohort failures first, then T48.
