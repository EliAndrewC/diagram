# Feature Specification: Scale the placement loops - judge what changed, build once, ask an index

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=387-scale-the-placement-loops`)

**Created**: 2026-10-18

**Status**: Draft

**Approved**: the GM, 2026-10-18, "I don't think we need to re-check everything after each addition, and you've already proposed fixes for the others, so please file a feature for this and then make it happen."

**Affects**: hamlet

**Input**: `request.md` - the GM's question, the session's profile of a 40-household roll and its three-bullet diagnosis, and
the GM's approval, verbatim. "All of this" is the three bullets quoted there.

## Why

At 40 households the reference hamlet's stages take 15-20 s a seed, and 10 -> 40 households grows ~5x (observed 2026-10-18;
method: `make perf SCALING=1` and `make perf-profile ... HOUSEHOLDS=40`, `request.md`). No single function is hot; the cost is
in the SHAPE of five loops. The hamlet band stops at 20 households (research question 0001), so 40 is the measuring roll's
size, not a map anyone draws; it matters because the village, town and city tiers will run these same placers at their sizes.

## The three bullets, read literally

1. **"Re-checking everything after each addition"** names three sites: **the way tree** (each candidate household way is
   admitted by judging the whole tree with it), **the web's settling passes** (each pass re-checks the whole lane network),
   **the cell merges** (each paddy-cell merge re-runs every ring rule). The GM: *"I don't think we need to re-check everything
   after each addition"* - at each site an addition is judged on what it can change, not by re-checking everything.
2. **"Rebuilding things that don't change"** names two: **the house layout geometry** (a household's bundle geometry, rebuilt
   for every reach check) and **the sun keep-outs** (rebuilt for every grove). Each is built once for the inputs it depends on
   and reused while those inputs stand.
3. **"One straight scan with no index"** names one: **the bamboo strip check** - a candidate strip is tested against the placed
   boxes, houses, fixtures and lanes NEAR it, found by a spatial index built once, not by walking all of them.

The session's own estimate in the diagnosis ("should cut the 40-household time by well over half") is an estimate, not a bar
the GM set; this feature measures and reports what each change bought (SC-002).

## User scenarios

### User story 1 - a bigger settlement costs in proportion to its size (P1)

The GM asks for a larger settlement and the time it takes grows with its size, not with its size squared.

**Acceptance**: at 10, 20 and 40 households, the number of whole-structure judgements each of the three re-check sites makes
per addition does not grow with the household count (SC-001).

### User story 2 - the maps keep their rules (P1)

Faster placement draws maps held to the same rules: nothing is loosened, coarsened or skipped to buy speed.

**Acceptance**: the cohort and the pool hamlets pass as they did on main (SC-003); where a site's new judgment can give a
different answer from the whole check, the difference is shown on the cohort and recorded at the point of change.

## Requirements

- **FR-001 The way tree.** Admitting a candidate household way judges the way against the tree it joins and the rules the
  addition can break, not the whole tree again; the verdict equals the whole judgment's on the same tree and way.
- **FR-002 The web's settling passes.** A settling pass re-checks only the parts of the lane network an earlier pass, or the
  repair it made, changed (and what those parts' rules reach); a part no change reached keeps its verdict.
- **FR-003 The cell merges.** A paddy-cell merge re-judges the cells and banks the merge changed and their neighbors, not every
  cell's ring rules.
- **FR-004 The bundle geometry.** A household's bundle geometry is built once per household and pose (the inputs it is a
  function of) and reused by every reach check that asks for it.
- **FR-005 The sun keep-outs.** The sun keep-outs a grove is checked against are built once for the map state they read and
  reused across groves until that state changes.
- **FR-006 The bamboo strip check.** A candidate strip asks spatial indexes, built once per pass and kept current as things
  are placed, for what stands near it; the verdict equals the straight scan's.
- **FR-007 Equivalence first.** Each change is proved verdict-equivalent to the code it replaces - by a test that runs both on
  the same inputs - unless it cannot be; a change that alters an answer says so at the point of change and in the plan, and the
  maps it moves are judged against the rules (cohort, pool hamlets), never byte-identity (`l7r/diagram/CLAUDE.md`,
  "Performance").
- **FR-008 No rule loosened.** No check is removed, coarsened, sampled or given a wider tolerance to buy speed
  (`dev/performance.md`: a slow check is INDEXED, never coarsened).
- **FR-009 Measured.** Bookends `make perf LABEL=387-start SCALING=1` before the first engine edit and `-end` after the last,
  taken back to back on a quiet machine where possible, each with its load; per-site profiles at 40 households before and after.
- **FR-010 Recorded.** `dev/performance.md` gets the general rule each site illustrates (judge the addition, build once,
  index the scan), with its measurement.

## Out of scope

- The hamlet household band (10-20, research question 0001) stays; the CLI keeps refusing 40 households. The GM: *"I don't
  want to contradict the research."*
- Rendering the scaling legs (the GM declined: "No thanks").
- Hot spots the diagnosis did not name (the commons byres' clearance checks, open-ground patches, grove index inserts): noted
  in the report as the next candidates, not changed here.
- The memory trades in `dev/performance.md` "Time traded for memory" are not undone.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003) At 10, 20 and 40 households on the four reference seeds, each re-check site's count of
  whole-structure judgements per addition is flat across the sizes (recorded in `measurements.json`).
- **SC-002** (FR-001 - FR-006, FR-009) Each of the six sites' time at 40 households, seed 4, is reported before and after; the
  end bookend's 40-household total is reported against the start's, with both loads.
- **SC-003** (FR-007, FR-008) `make cohort` and the landing cohort pass with no seed newly failing against main; the pool
  hamlets regenerate and pass their gate; each equivalence test is green.
- **SC-004** (FR-010) `dev/performance.md` carries the three rules with their numbers.

## Assumptions

- The five stages are profiled on the reference spec (nucleated, pond), the one the bookends time; the other forms run the
  same placers and are covered by the cohort.
