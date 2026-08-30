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

| `labels_within_image` / `no_label_overlaps` (the REACH half) | `tests/settlement/test_label_placement.py::test_a_tilted_labels_reach_is_its_rotated_quad_not_its_unrotated_box` | `label_aabb` made to return the unrotated box -> RED |

*Note on that last row:* it carries the REACH the two rules depend on, not the rules entire. Containment
against the frame and pairwise non-overlap still need their own destinations; what is proven here is that a
tilted caption's reach is its rotated quad, which is the quantity both rules measure and the one
`dev/gate.md` records being got wrong ("a tilted caption as a ROTATED QUAD" vs "an axis-aligned bounding
box" - measuring the wrong one made every seat look illegal and the fallback took a worse one).

| `no_structure_on_paddy` | `tests/settlement/test_field_keepout.py` (point, gap and rect arms) | `_field_blocks_point` and `_field_blocks_rect` each short-circuited -> RED |
| `dry_plots_clear_of_paddies` | same module - one segment emits both, and one keep-out guarantees both | same mutations -> RED |

| `no_structure_on_stream` | `tests/settlement/test_way_and_water_corridors.py` (registration + refusal) | river's `corridors.append` removed -> RED; `_near_corridor` short-circuited -> RED |
| `houses_clear_of_lanes` | same module | lane's `corridors.append` removed -> RED |
| `no_farmhouse_stands_on_a_lane` | same module (the `width/2 + 11` setback, which is what clears building CORNERS) | same mutations -> RED |

| `irrigation_channels_hairline` | `tests/settlement/test_water_width_ladder.py` | channel default width raised off the floor -> RED |
| `watercourses_wider_than_ditches` | same module (the ladder's ORDER, which is the part that is not a legibility deviation) | same mutation -> RED |

| `settlement_declares_a_land_fall` | `tests/gate/test_generator_contracts.py` | a map declaring neither a fall nor per-field falls fails the assertion |
| `households_consistent` | same module | seated count against the spec's ask |
| `farmhouse_sizes_vary` | same module (effective footprint, so BOTH size encodings count) | - |
| `settlement_records_cluster_seeding` | same module | the shape record removed from `homesteads.py` -> RED |
| `byre_form_declared` | same module | allowed forms read off the engine, not guessed |

| `polder_fills_its_bbox` | `tests/waterfields/test_polder_geometry.py` (4 seeds) | - |
| `polder_floor_is_ring_interior` | same module | - |
| `polder_edges_wander` | same module | `lwander` made to return (0, 0) -> RED |
| `polder_dike_gapped_at_sluices` | same module | - |

| `village_windbreak_present` | `tests/hamletgen/test_hinterland.py` (belt suite) | `belt_polygon` made to return [] -> RED |
| `village_windbreak_embraces_cluster` | same suite (the belt's centre projects along +wind) | same mutation -> RED |
| `village_windbreak_scales_with_cluster` | same suite (a 12-house cluster gets more belt than a 3-house one) | same mutation -> RED |
| `village_windbreak_is_continuous` | same suite (the belt spans a ragged fringe rather than one lobe) | same mutation -> RED |

| `tree_crowns_not_subsumed` | `tests/settlement/test_canopy_seating.py` | `_crown_seat_clear` made to allow everything -> RED |
| `structures_clear_of_trees` | same module (`_crown_covers` over a recorded roof) | - |
| `wells_clear_of_trees` | same module (`_crown_covers` over a wellhead) | - |

| `settlement_has_wells` | `tests/hamletgen/test_wells.py` (floor, ceiling, and the 2-20 households-per-well band) | `well_target` divisor changed -> RED |

| `wells_off_the_wet_toe` | `tests/settlement/test_well_ground.py` (water, pond, dry plot, and the DRAWN-head margin) | the pond arm of `_well_ground_clear` removed -> RED |

| `pond_clear_of_field` | `tests/settlement/test_well_ground.py` (pond section) | `self.ellipses.append` removed from `pond()` -> RED |
| `pond_clear_of_paddies` | same module - one registry, so one guarantee serves both | same mutation -> RED |

| `farmhouses_reach_a_way` | `tests/hamletgen/test_unreached_houses.py` (11 unit tests) PLUS `tests/gate/test_reach_predicate_matches_the_check.py` (equivalence on 5 live maps and their perturbed copies) | done at T02 - the check's body LIFTED, with the equivalence test that dies with the check |

| `lanes_clear_of_dry_plots` | `tests/hamletgen/test_lane_clipping.py` (`clip_to_clear`, whose obstacle list is envelope + crops + fabric + wet toe together) | clipping disabled -> RED |

| `delivery_ditches_taper` | `tests/waterfields/test_comb_topology.py` (4 seeds) | `_canal_ft` made to return one weight -> RED |
| `water_channels_obtuse_turns` | same module | - |
| `field_ditches_terminate` | same module (the builder's half: there IS a run to land) | - |

## Already carried by an existing test - dropped against it, not rewritten

| check | carried by | proof |
|---|---|---|
| `hamlet_has_kosatsuba` | `tests/settlement/test_structures.py` (the `place_kosatsuba` suite) | board never placed -> RED |
| `caption seating (lane clearance)` | `tests/settlement/test_structures.py` | `pick_caption_seat` renamed out from under its callers -> RED |

| `village_has_kosatsuba` / `town_has_kosatsuba` / `city_has_kosatsuba` | `tests/settlement/test_structures.py` (the `place_kosatsuba` suite) | board never placed -> RED (proved earlier in this feature) |

*Why one entry for three:* `place_kosatsuba` is tier-agnostic - the GM's 2026-07-24 ruling is that EVERY
settlement tier carries the board, and the placer auto-sites it from the same manifest route fields at every
scale. The three check names are one guarantee wearing three scale labels, so one proof serves them. What
differs by tier is the COUNT (a city draws the set: the principal board plus one per main gate), and that is
`city_kosatsuba_per_gate`, a separate rule still owed.

| `ways_cross_water_on_a_deck` | `tests/settlement/test_bridge_sources.py` | the one-deck dedup removed from `bridge()` -> RED; undrawn conduits offered -> RED |

| `sluice_gates_on_water` | `tests/settlement/test_sluice_gates.py` | the gate's `sluice_gates` append removed -> RED |
| `channel_gates_at_water_junctions` (recording half) | same module | same mutation -> RED; the span mutation -> RED |

## Still owed

The remaining checks, by group, are in `destinations.json`. The split that governs the work:

- **~101 migrate-only** (`FIRES-HAND-ONLY`): the placer guarantees the rule today. Each needs its
  destination proven - by probe if an existing test carries it, by a new test if not.
- **~36 placer bugs** (`FIRES`): a scripted artifact still trips the check, so the placer does NOT
  guarantee it. Each is a repair, not a migration.
- **4 keeps** documented in feature 163's `placer-reads.md`.
