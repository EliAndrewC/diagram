# FR-009: where each retired rule now lives

One row per check. A check is not deleted until this file gives it a destination and the destination has
been PROVEN - either a new test seen RED against the unfixed placer, or an existing test shown by mutation
to already carry the rule.

## The method, and why it is mutation rather than reading

Two questions have to be answered per check, and only one of them can be answered by reading:

1. **Which placer guarantees this rule?** Read the check, read the placer. No shortcut.
2. **Is the rule ALREADY carried by a test?** This looks answerable by reading and is not. A test that
   *mentions* the subject may assert nothing about the rule; a test that never names it may guard it
   exactly. `specs/166-retire-the-check-battery/covered_by.py` answers it by MUTATION: break the placer's
   guarantee, run the suite with the battery's own tests excluded, and see whether anything goes red.

The battery's own tests are excluded deliberately - they are what is being retired, so a rule only they
catch is precisely a rule with no home yet.

**This changed the shape of the work.** The plan assumed 101 migrations each needing a new test. The first
probes show existing placer suites already carry some of them, and those drop against a named test instead.

## Retired, with a new test written and proven

| check | destination | proof |
|---|---|---|
| `bamboo_stands_clear_of_paddies` | `tests/hamletgen/test_hinterland.py::test_bamboo_blocked_refuses_ground_inside_the_crop` + `_keeps_its_pad_off_the_crop_edge` | crop arm cut from `bamboo_blocked` -> both RED |
| `gardens_clear_of_channels` | `tests/settlement/test_homestead_parts.py::test_a_garden_is_refused_on_a_no_build_corridor` + `test_a_watercourse_registers_the_corridor_the_garden_consults` | corridor arm cut from `_garden_fits` (line-targeted, enclosing `def` asserted) -> RED |
| `title_has_placard` | `tests/settlement/test_label_placement.py::test_the_title_records_a_placard` | placard key renamed -> RED |
| `scalebar_matches_declared_scale` | `..::test_the_scalebar_reports_the_declared_scale` (3 rungs of the ladder) | `bar_ft` offset by one -> RED |
| `title_clear_of_features` | `..::test_the_blank_spot_scan_refuses_a_box_that_covers_an_obstacle` + `_returns_nothing_when_the_window_is_full` | `_box_clear`'s rect arm short-circuited -> RED |

## Already carried by an existing test - dropped against it, not rewritten

| check | carried by | proof |
|---|---|---|
| `hamlet_has_kosatsuba` | `tests/settlement/test_structures.py` (the `place_kosatsuba` suite) | board never placed -> RED |
| `caption seating (lane clearance)` | `tests/settlement/test_structures.py` | `pick_caption_seat` renamed out from under its callers -> RED |

## Still owed

The remaining checks, by group, are in `destinations.json`. The split that governs the work:

- **~101 migrate-only** (`FIRES-HAND-ONLY`): the placer guarantees the rule today. Each needs its
  destination proven - by probe if an existing test carries it, by a new test if not.
- **~36 placer bugs** (`FIRES`): a scripted artifact still trips the check, so the placer does NOT
  guarantee it. Each is a repair, not a migration.
- **4 keeps** documented in feature 163's `placer-reads.md`.
