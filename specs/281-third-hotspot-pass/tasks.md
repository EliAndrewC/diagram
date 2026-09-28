# Tasks - feature 281, the third hotspot pass

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A1-A8, B1-B2, C). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test; the pool regenerated and compared byte for byte against
`c13a6ebe6` with all of them landed; then the two moving pieces under 276's FR-006 condition; then the measurement and
the record.

## Setup

- [x] T01 The base: `measure.py before` in the clone at `c13a6ebe6` (`measurements.json` before-keys), the `281-start` bookend in `/tmp/base281`, the harness's entry-bucket instrument (plan C), and the committed pool confirmed to regenerate byte-identically in the base worktree
      research: rendering
      verify: DONE. measure.py before at c13a6ebe6 (pool 32.902 s, counts.py from the saved profiles); 281-start bookend 20.6 s in /tmp/base281; the entry-bucket instrument in harness.py (probe on Kashikawa reproduced the direct-caller counts); the committed pool regenerates byte-identically in /tmp/base281 (git status clean over pool/)

## US2 - the ways, the board and the captions ask indexes (P1)

- [x] T02 [US2] The clip through the fabric index in `hamletgen/ways/clearance.py`, with its equality test (A1)
      research: rendering
      verify: DONE. clip_to_clear asks fabric_index(obstacles, margin, (), 0, lines, line_margin).fouled; test_the_clip_through_the_fabric_index_is_the_old_clip over 300 random clips + the exact-margin case
- [x] T03 [P] [US2] The toll's grid sized to the band in `hamletgen/ways/route.py`, with its equality test (A3)
      research: rendering
      verify: DONE. set_crossing cells of max(20, r + 1), in_brook_band reads 3x3; test_the_toll_grid_sized_to_the_band_is_the_old_band at r = 12/30/45/64 incl. exact-radius points
- [x] T04 [P] [US2] The notice board's indexes - `outermost_join` and `RouteReach` - in `settlement/structures/fixtures/_helpers.py`, `siting.py` and `hamletgen/frame.py`, with their equality tests (A4)
      research: rendering
      verify: DONE. outermost_join over seg_reach_index (reach + 1e-6), RouteReach in place_kosatsuba and frame.py; equality tests incl. a way exactly at the reach
- [x] T05 [P] [US2] The watercourse indexes in `hamletgen/ways/sweeps.py` (`_link_home_bank`) and `settlement/rolling/fit.py` (`_rect_on_stream`), with their equality tests (A5)
      research: rendering
      verify: DONE. brook_segment_index/crossing_hits/crossings_parity in ways/geom.py; stream_segment_index cached beside _water_obstacles, rect_touches_stream; equality tests
- [x] T06 [P] [US2] The caption probe's lane index in `settlement/structures/captions.py` and its two many-seat callers, with its equality test (A6)
      research: rendering
      verify: DONE. lane_seat_index + clear_of_lanes; label_seat_clear(lanes=), built once in clear_label_seat and place_kosatsuba; equality test over 3,000 boxes

## US3 - what was computed once is not computed again (P1)

- [x] T07 [US3] Ring indexes shared by content in `hamletgen/clearance.py`, with the build-once and mutated-ring tests (A2)
      research: rendering
      verify: DONE. clearance._RINGS keyed on the ring's points, cleared in reset(); test_a_ring_is_indexed_once_by_its_points_and_a_changed_ring_anew
- [x] T08 [P] [US3] The carve's vertex memo in `waterfields/carve.py`, with its equality test (A7)
      research: rendering
      verify: DONE. _carve_sector's edge_m memo after rspan is live (sector rows moved to waterfields/sector_rows.py for the 1,000-line bar); test_the_vertex_memo_changes_no_plot, banks on and off

## US4 - the windbreak stops re-asking (P2)

- [x] T09 [US4] The windbreak gap fill's memory in `settlement/homestead_parts/stands.py` and `grove_blocks.py`, with its equality test (A8)
      research: rendering
      verify: DONE. _barren gaps skipped, GroveBlocks.static_clear per point; test_the_gap_fill_skips_a_barren_gap_and_seats_the_same_clumps (fewer outline asks, equal clumps)
- [x] T10 [US1] The pool regenerated with A1-A8 landed and B not yet: every live pool manifest byte-identical against `c13a6ebe6` (SC-011, first half)
      research: rendering
      verify: DONE. make maps SCOPE=all with A1-A8: git diff c13a6ebe6 over pool/ empty - every live pool manifest byte-identical

## US3 / US4 - the moving pieces

- [x] T11 [US3] The shared plot edge walked once in `waterfields/carve.py`, with its symmetry and verdict tests and the Decisions note at the point of change (B1)
      research: rendering
      verify: DONE. _quad_in_supply(memo) keyed on the edge's endpoints in tuple order, walked from the lesser (_edge_in_supply); one memo per sector; Decisions note in the docstring; test_a_shared_edge_is_one_verdict... equal to the old verdicts over a 27x13 quad grid round a stroke. On the pool it moved no plot (research R2)
- [x] T12 [US4] The vectorized marsh in `settlement/land/wet.py`, with its compliance and density tests and the Decisions note at the point of change (B2)
      research: rendering
      verify: DONE. marsh_scatter in land/wet.py (numpy throws, inside_many, hit_many at each kind's pads, crescents, the pond's lateral and blade-top tests, the feather); _sparse removed, its reasoning kept at the call site; test_the_vectorized_marsh_keeps_every_keep_out_and_its_density; the pond bank now the whole ring (a defect the moved throws exposed, research R2, Decisions row)
- [x] T13 [US1] The pool regenerated under 276's FR-006 condition: `make done` green, the rescue-rounds scenario and the toys, forms and kinds, the moved maps' research entries, `make cohort N=24` against the base's (SC-011, second half)
      research: rendering
      verify: DONE. pool regenerated with B1-B2: only ink_classes.marsh moved (houses, kinds, form, fields, plots, ways, marsh outlines identical - research R2); rescue-rounds 16/10, toys 10/20, density layouts equal on base and clone; make cohort N=24 24/24 on both; make done green (70 s) after fixing the stream index key and two coverage lines

## Polish

- [ ] T14 `measure.py after` back to back; SC-001 to SC-010 checked on the entry buckets (plan C), base-rerun over after, each bucket's total beside its named count; `make perf LABEL=281-end` and `make perf-report AGAINST=281-start`
      research: rendering
- [ ] T15 `dev/performance.md`: the third pass's section and its residue table, levers priced (FR-011, SC-012)
      research: rendering
