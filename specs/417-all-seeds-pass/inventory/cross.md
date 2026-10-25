# T03 cross-package searches (session, 2026-10-24)

S1 (each cohort_audit rule, callers in l7r): row_rules, water_rules, bamboo_mismatch, fixtures_on_groves, gardens_east_shaded,
grove_sides_missing, groves_crossed_by_lanes, groves_off_windward, trees_shading_plots, bamboo_shading_plots, lane_knots,
matrix_violations, farmstead_across_brook (inline in cohort_audit:146): NO placer calls any of them. Placers that mention one
carry their own test "the same boxes": fixtures.py:474 / fit.py:572 / fit_index.py:47 (fixtures_on_groves), dispersed.py:222
(gardens_east_shaded), serve.py:474 (groves_crossed_by_lanes), farm_water.py:258 (water_rules), bamboo.py:145
(bamboo_mismatch writes meta for the audit). -> P1 + TWICE candidates, each to confirm against the code.

S2 (whole-web / finished checks inside the run): last_resort.py:159,179,215 (lane_violators, unsettled); settle/stage.py:35,92,96
(unreached_*, unsettled, refuse_unreached); law.py:642-649 and tree.py:593-707 (whole-map reach counts asked of trials -
admission of a candidate against the whole map, to classify); corridors.py:106; knots.py:616; settle/ends.py:194,266;
reach.py:49,79; waterfields/settle.py:74 and seams/close.py:164 (ring_violations, then repair); brook.py:558-569 and
sink.py:448 (brook_violations asked of candidate courses - likely KEPT).
