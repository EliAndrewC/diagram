# Implementation Plan: The paddy is not four to six inches deep

**Branch**: none - `SPECIFY_FEATURE=160-paddy-water-depth` | **Date**: 2026-08-29 | **Spec**: [spec.md](spec.md)

## Summary

Prose and records only. Replace a false depth claim in seven places, drop a mis-citation, register
the two sources actually read, and write the finding down. Nothing drawn changes.

## Technical Context

**Language/Version**: Python 3.14 | **Dependencies**: none new | **Testing**: pytest

**Single-artifact target**: `pool/hamlets/inashiro.gen.py` - the reference hamlet, whose page shows
the corrected modal. No other map is rolled: the change is text in a shared registry, so every map's
page picks it up at its next regeneration without this feature touching it.

**Every step is two steps**: T4 is the reference settlement; the pool needs no step of its own,
because no generator behavior changes and no manifest key can move (the ink census counts class
KEYS, and no key changes).

## Performance bookends

**NOT APPLICABLE, stated rather than skipped.** This feature changes string literals and comments.
No code path, no geometry, no loop. `make perf` would measure two runs of identical execution and
attribute the difference to whatever else the box was doing - which is exactly the trap feature 159
recorded when its bookends read -59.2% on contention alone. The gate's `perf-gate` still runs.

## Constitution Check

- **I, II**: N/A - no webapp UI in this repository.
- **III, IV, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world prose, no setting
  entities.
- **V. Protecting the GM's Writing (NON-NEGOTIABLE)**: PASS - no SOURCE markers touched.
- **VI. Verify Before Reporting Done**: PASS - `make done`; the reference hamlet regenerated and its
  modal read; the browser suite exercises the page. No `settlement-review`: the drawing does not
  change, which is the GM's standing ruling of 2026-08-29.
- **X. Python Discipline (NON-NEGOTIABLE)**: PASS - ruff, pyrefly, pytest, coverage. The registry
  test that lists the classes carrying NO caveat must be updated, since `paddy` gains one; that test
  exists precisely so adding a caveat is a deliberate act.
- **XI. Japanese Authenticity**: PASS - 中干し (nakaboshi) is quoted with its reading and gloss.
- **XII. Historical Grounding (NON-NEGOTIABLE)**: PASS. Opening bookend: the `source-reader` pass of
  2026-08-29, with quotes, two new `SOURCES.md` keys and both negatives (no pre-modern figure; the
  contradicted citation). Closing bookend: the class's `caveat`, which puts the provenance in front
  of the reader, and the Decisions Recorded table.
- **XIII. No Known Regressions (NON-NEGOTIABLE)**: PASS - green gate; nothing drawn moves.
- **XIV. Fix Defects Where You Find Them (NON-NEGOTIABLE)**: this feature IS one, and it carries a
  second (FR-007, the check comment carrying the same wrong shape without the number).
- **XVI. Build What Was Asked (NON-NEGOTIABLE)**: spec-fidelity round 1 FAITHFUL, including on the
  question of whether "correct it" answers a request that offered two other branches.
- **XVIII. A Guard Owes a Test**: N/A - no guard script changes.

## Phase 1 - design

**The replacement sentence.** Not a different number in the same shape - the shape was the larger
error. The modal says a shallow sheet of water, an inch or so for most of the season, and says the
sheet is not constant: drained on purpose at midsummer until the mud cracks, and again before
harvest. One clause for the staging, not an agronomy essay (spec-fidelity's boundary).

**The provenance goes in `caveat`, not in `what`.** Feature 156's machinery: the modal leads with
what the thing IS and shows the liberty under the why. The liberty here is that the depths and the
drying stages are modern extension figures with no pre-modern record behind them, and that the map
draws one moment of a cycle. `paddy` leaves the "no caveat" list in `tests/interactive/test_classes.py`.

**The four sibling texts are one sentence repeated four times.** Fixing one and leaving three is the
failure mode that rule exists for (feature 152 recorded it), so all four change together.
