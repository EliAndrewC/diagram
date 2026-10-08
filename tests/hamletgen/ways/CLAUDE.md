# `tests/hamletgen/ways/` - the suite for the `hamletgen/ways/` package

**One file per submodule of the subject**: a change to `ways/touch.py` opens `test_touch.py`, and a new test goes beside
the ones for its own subject. It runs in the quick tier (the top-level tree decides the tier, not this nesting).

## Look here when

| file | look here when |
|---|---|
| `test_bund.py` | the run-on to the bund (`ways/bund.py`), `WorkedGround`, and `meet_end_to_end` |
| `test_checks.py` | the questions asked ABOUT a finished network - unreached houses, shared treads, crossings that land on crop or water |
| `test_clearance.py` | may a way BE here - `clear_runs`, `_clear_link`, `_clear_touch`, `may_write`, the bend and nub judgments |
| `test_corridors.py` | the access tree's roles and the runs the seating reserves (`ways/corridors.py`) |
| `test_doors.py` | a grove farm reached at its front door - `front_door`, `lay_door_paths`, `own_street` |
| `test_dry_exit.py` | the flood fill that finds a track out of the frame over standable ground (`ways/dry_exit.py`) |
| `test_dry_exit_raster.py` | `dry_exit._blocked_cells` rasterized, held to the cell-by-ring scan kept as its oracle |
| `test_fabric.py` | the settlement fabric a way must respect - `_crosses_fabric`, `_fabric_hits`, `_homestead_polys`, `_margin_frame`, `_draw_web` |
| `test_geom.py` | point and segment math on a bare polyline - `polyline_len`, `_turn_deg`, `_components`, the two pushes, `_trim_to_service` |
| `test_indexed_scans_281.py` | the indexed clearance and route scans, each held to a copy of the old scan kept as its oracle |
| `test_joints.py` | two lanes meeting end to end - the fold that becomes a T, the jog pulled straight across a chain of joints, the hook taken off a lane end, and the guards (`keeps_the_web`) that refuse a rewrite losing a junction, splitting the web or stranding a farmhouse |
| `test_knots.py` | lane ends that nearly meet are joined at one point (`ways/knots.py`) and gathered by the settle |
| `test_last_resort.py` | the settle's last resort: drops ordinary lanes only, and refuses by name what only the tree could mend (`ways/last_resort.py`) |
| `test_law.py` | THE LANE LAW (`ways/law.py`): each lane-rule predicate on a constructed lane that keeps the rule and one that breaks it, and the `violations` registry |
| `test_matrix_287.py` | every lane the web lays, re-lays or carries on is admitted by the overlap matrix before it is written |
| `test_route.py` | the router: `_route` going round hard ground, `_unjog`, and the pad multiplier that lets a link take the long way |
| `test_serve.py` | `_lay_web_lane` - one web lane joins the network or is refused - and the web's late passes (`tidy_lane_ends`, `cut_the_overruns`) |
| `test_settle.py` | `settle_the_web` (`ways/settle.py`): each rule of the lane law provoked on constructed lanes and repaired |
| `test_smooth.py` | the smoothing pass (`ways/smooth.py`): the collapse guard for a lane whose every vertex falls inside a knot |
| `test_street.py` | a row village's streets (`ways/street.py`) and the road its street runs out on |
| `test_sweeps.py` | the passes that REMOVE or REPAIR - doubled remnants, steading fouls, end nubs, collinear breaks, orphaned pieces |
| `test_touch.py` | how a lane end meets the network - `_touch_junctions` and the piece-joining it falls back on |
| `test_track.py` | STAGE `stage_track` and `connector_track` - the way out of the frame and through the fabric |
| `test_tree.py` | the access tree as lanes (`ways/tree.py`): `admits`, `settle_tree`, `tree_faults`, `settle_defer`, pruning |
| `test_web.py` | STAGE `stage_web` and the skeleton it starts from - the settlement form roll and the dispersed short-circuit |
| `test_weld.py` | the corner weld (`ways/weld.py`) |
| `_builders.py` | the shared fixtures - `_lanes`, `_StubSettlement`, `_walled_settlement`, `_webbed`, `AdmitsAll`. The wider hamlet builders (`SQUARE`, `a_plan`) still come from `tests/hamletgen/_builders.py` one level up |
