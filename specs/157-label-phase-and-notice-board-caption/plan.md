# Implementation Plan: the label phase, and a notice-board caption that stands beside its board

**Feature**: `157-label-phase-and-notice-board-caption`
**Spec**: [spec.md](spec.md) | **Request (verbatim)**: [request.md](request.md) | **Measurements**: [research.md](research.md)
**Created**: 2026-08-29

## Summary

Two changes, in one feature because the second is only safe to judge once the first exists.

1. **A LABEL PHASE.** A settlement's captions stop being drawn by the feature that owns them and are
   QUEUED instead. One phase, running after every map feature has been placed, drains the queue.
   The hamlet pipeline gets a named `stage_labels` after `stage_notice`; every other tier gets the
   same phase from `finish()`, which runs it as the last thing it does. On a hamlet the phase is
   byte-neutral by construction (nothing is placed between the board and the phase), which is what
   lets the second change be attributed cleanly.
2. **A CAPTION THAT STANDS BESIDE ITS SUBJECT.** The notice board's seat search is fixed in the
   three ways `research.md` measured: a lateral ladder scaled to the caption rather than to the
   subject, a perpendicular ladder that steps over the one legal rung, and a structural probe that
   collapses the caption's rotated quad to a bounding box three times its thickness.

## Technical Context

**Language**: Python 3.14. **Entry points**: `make quick`, `make map`, `make maps`, `make done`.
**Files at the center of it**:

| file | what changes |
|---|---|
| `l7r/diagram/settlement/core.py` | the label queue, beside the existing `_captions` list |
| `l7r/diagram/settlement/structures/captions.py` | `place_labels()` - the phase itself |
| `l7r/diagram/settlement/structures/fixtures.py` | `kosatsuba()` queues instead of drawing; the seat search moves to its own method and is fixed |
| `l7r/diagram/settlement/finish.py` | `finish()` calls `place_labels()` where the `_captions` flush used to be inlined |
| `l7r/diagram/hamletgen/driver.py`, `frame.py` | `stage_labels`, last in `STAGES` |
| `l7r/diagram/check_village/segments_08d_kosatsuba_and_paddy_basins.py` | the new check |
| `dev/placement.md`, `hamletgen/CLAUDE.md`, `settlement/structures/CLAUDE.md` | the phase, recorded where the next reader meets it |

## Constitution Check

| gate | verdict |
|---|---|
| **I. Accessibility-First Viewports** | N/A - no UI in this repository |
| **II. Bold, Intentional Design** | N/A - same reason; map style is governed by the skill's doctrine and reviewed under VI |
| **III. Pool Data Conventions** | N/A - no new recurring generated content; existing pool maps are regenerated in place |
| **IV. One Canonical Home for GM Source** | N/A - no SOURCE blocks added or moved |
| **V. Protecting the GM's Writing** | PASS - no task touches a SOURCE block |
| **VI. Verify Before Reporting Done** | PASS - `make map` on Kuwabata, then `make maps` for the tier sweep (two steps, two tasks); `make done` at the end; an independent `settlement-review` before anything ships, paired with the gate via `make verify` (feature 151) |
| **VII. De-Localized Generation** | N/A - no pool prose |
| **VIII. Direct Voice** | N/A - no in-world content |
| **IX. Setting Integration** | N/A - no setting claims; see the note in the spec's Decisions Recorded on why no research pass is owed |
| **X. Python Discipline** | PASS - ruff, `ruff format --check`, pyrefly, pytest, 100% on the hamlet-path floor; red-green on the new check (its negative fixture is frozen from today's Kuwabata manifest and must go red before the fix lands) |
| **XI. Japanese Authenticity** | N/A - no new kanji |
| **XII. Record the Why / the reader who will click** | PASS - the Decisions Recorded table in the spec, four rows, each a **deviation** with its recorded home; each also lands as a comment at its point of change |
| **XIII. No Known Regressions** | PASS - baseline taken in a detached worktree before the first edit; the pool sweep and the 48-seed cohort are compared against it |
| **XIV. Fix Defects Where You Find Them** | PASS - the bounding-box probe (research R2c) is fixed here rather than filed |
| **XV. Keep Going** | PASS |
| **XVI. Do the Literal Thing / spec reviewed by someone else** | PASS - `spec-fidelity` reviewed `spec.md` against `request.md` before implementation |
| **XVII. A README is the GM's** | N/A |
| **XVIII. A guard has a test companion** | N/A - no new guard script; the new gate check has its test and its negative fixture |

## Design decisions

### D1 - the queue holds DATA, not a closure

A queued caption is a small record - kind, and the payload its placer needs - not a captured
lambda. Two reasons: CLAUDE.md's inner-function rule (*"an inner function that is hard to test gets
lifted out"*), and because a closure captured at `kosatsuba()` time would freeze the very map state
the phase exists to re-read.

### D2 - the phase dispatches by KIND, through a one-entry table

`place_labels()` maps a request's kind to the method that seats it. With one labeled feature today
the table has one row, and a new labeled feature adds a row rather than a branch. The table is not a
registry that restates what code declares (clause 14) - it is the phase's own ORDERING and dispatch
decision, which is exactly the ordered-data carve-out.

### D3 - the drain order, and why priority is NOT in it

Queued fixture captions in call order, then the deferred `place_caption` seats in call order, then
the road caption. That is today's relative order preserved exactly, and it keeps the recorded rule
that the most-constrained caption is seated first and the road - which has by far the most room to
move - yields last.

**Priority is deliberately not built** (the GM: *"that will not apply here"*). When a map has
competing labels, priority becomes one more key in front of the call-order sort in this one function.
That sentence is the extension point, recorded here and in the function's docstring.

### D4 - `finish()` runs the phase; a phase already run is a no-op

The hamlet pipeline names the phase as a stage so the pipeline reads honestly ("after the final map
feature is added, there is a final phase"). Every other tier is a hand-authored script with no
pipeline, so `finish()` runs the same phase as the last thing it does. Draining an empty queue does
nothing, so a hamlet is not labeled twice.

### D5 - what the seat search changes, and what it must NOT

Three fixes, all inside the tilted branch of the notice board's seat search:

- **the lateral ladder keeps its REACH and loses its coarseness.** The reach is load-bearing and the
  reason is recorded in the code: a board in a lane crotch has no legal seat on the perpendicular
  line at all, and five cohort seeds are in that position. So the lateral axis is sampled finely
  from 0 outward, and the far seats stay reachable - they are simply no longer the ONLY alternatives
  to a single rung at 0.
- **the perpendicular ladder is sampled finely.** Measured: Kuwabata's only legal seat below the
  board is at a 14 px standoff, between the ladder's 11 and 16.
- **the ranking states the GM's rule.** Among legal seats, least displacement ALONG the caption's
  baseline wins, and the standoff across it breaks the tie - so the caption ends up directly beside
  the board, as close as the ground allows. Straight-line distance, which is what ranks seats today,
  cannot tell a 39 px slide from a 39 px standoff.

### D6 - the new check's threshold is MEASURED, not chosen in advance

`caption_stands_beside_its_referent` bounds how far a caption may stand along its own baseline from
the thing it names. The bound is set from the lateral offsets the FIXED placer actually produces
across the pool and the 48-seed cohort, plus a stated margin - not from a number picked before the
sweep. The reason is the conflict the measurement exposed: the far lateral seats exist for boards in
a lane crotch, and a bound chosen on Kuwabata alone could forbid the only legal seat those maps have.
So the task order is: fix the placer, sweep, read the distribution, then write the number and the
sentence explaining it.

The check is scoped to the notice-board caption family, and `research.md` R3 records why, with the
eight town and city captions of other families that the same rule would fail today and what
extending it to them would cost.

### D7 - what is deliberately NOT changed

`captions_clear_the_ways_they_stand_on` (gate 0617) measures the caption's UNROTATED recorded box.
For a tilted caption that is not the shape drawn, and the seat probe deliberately measures the same
unrotated box so that placer and check read one source. Making both rotation-aware is a real
improvement and it reflows every tilted caption in the pool, which is a different feature with its
own sweep. **Accepted, with the alternative priced**: the cost of leaving it is that a tilted
caption is judged slightly conservatively against a lane (its true quad is thinner than the box);
the cost of fixing it here is a pool-wide caption reflow inside a feature about something else.
Recorded at the probe.

## Phases

**Phase 0 - baseline.** Detached worktree at HEAD; `make done` and the cohort recorded there, so
"regression" is a measurement and not a memory.

**Phase 1 - the label phase.** Queue, `place_labels`, `stage_labels`, `finish()`. Verified by
regenerating the reference hamlet and Kuwabata and proving the manifests are BYTE-IDENTICAL - the
phase move alone must change nothing at hamlet scale.

**Phase 2 - the seat search.** The three fixes, with the Kuwabata manifest as the acceptance
artifact.

**Phase 3 - the sweep and the check.** `make maps`, the cohort, the measured threshold, the new
check, its negative fixture frozen from today's Kuwabata manifest.

**Phase 4 - the record and the review.** Comments at each point of change, the docs, the pool
notes, `make verify` (gate + independent `settlement-review`, paired), then the stop-work procedure.
