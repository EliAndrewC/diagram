# Implementation Plan: One Hundred Percent of the Tests Pass (137)

**Input**: `spec.md`. **Constitution**: v2.12.0.

## Summary

Nine pinned seed failures across three pin tables, each fixed at its mechanism (the engine, or a
wrong check with its research), each verified against the whole tripwire, the gate cohort and the
24-seed cohort so no fix rotates a failure onto another seed; the pins removed as they go stale;
the efficiency session's safe work pulled first and after each of its handoffs; this session's
tested fixes handed off in return.

## Technical Context

- The pins: `TRIPWIRE_EXPECTED` (`tools/mapcheck.py`), `GATE_COHORT_EXPECTED`
  (`tests/gate/hamletgen/test_driver.py`), `COHORT_BASELINE` (`hamletgen/driver.py`).
- The measurements already on record (133 T91/T92): seed 33's hole = the belt's column face clears
  the windward-most house CENTER while two garden beds stand 40-55 ft toward the wind inside the
  band (a plot-extent face rotated the hole to seed 41 - dead end recorded in hinterland.py);
  seed 37's stubs = `_smooth_web` cuts knots/hairpins into 2-point stubs 30-35 ft short of the
  spine, and the orphan joiner refuses the links; seed 27 and 43 fail the period's new checks
  (`lanes_bend_like_paths`, `lanes_clear_of_bamboo`, `title_clear_of_features`); seed 44 fails the
  T41 paddy set-back; seed 42 strands a farmhouse through the re-roll ladder; seed 47 is the old
  set; cohort 22/24 pre-date 133.
- Verification per fix: `make maps` (the tripwire), `make test-file FILE=tests/gate/hamletgen/test_driver.py`
  (the gate cohort, 4-wide), `make cohort` (24 seeds); the full unlocked gate once per handoff.
- The efficiency session's clone: `/diagram/.clones/diagram-tests`; pulls by `git fetch` of that
  path and a merge up to the named sha (never a rebase; a real merge commit).

## Constitution Check

VI (verification per fix, the gate per handoff); XII (a rule change carries its research); XIII
(no rotation - the three cohorts measured before a fix is kept); XIV (defects found on the way are
fixed here); XVI (spec reviewed first).

## Order of work

Cheapest, most-shared mechanisms first: (1) the lane-web stubs (37, 43, 47's `lanes_form_one_network`
and `lanes_reach_something`) - one mechanism, four seeds; (2) the bends check on 27/37/43 - decide
whether the check or the web is wrong, with the research; (3) the belt hole on 33 - a thinning
rule in `village_grove` rather than a face dodge; (4) 44's paddy set-back, 42's stranded house,
27's bamboo-on-lane, 43's title, 47's field/road and footbridge; (5) cohort 22/24.
