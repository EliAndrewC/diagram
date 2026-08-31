# `tests/hamletgen/ways/` - the suite for the `hamletgen/ways/` package

Split from the 1,541-line `tests/hamletgen/test_ways.py` by feature 173 (constitution Principle X
clause 13, which covers a TEST file exactly as it covers source - v1.6.1, GM 2026-08-16: you load a
test file to modify one test the way you load a source file to use one function, so nothing about
being a test changes the economics).

**One file per submodule of the subject**, and the mapping was DERIVED rather than chosen: each test
went to the module holding the majority of the names it exercises. So the way to find a test is to
name the thing it tests - a change to `ways/touch.py` opens `test_touch.py` - and a new test goes
beside the ones for its own subject.

Runs in the quick tier, unchanged: the tier is decided by the top-level tree (`tests/` versus
`tests/gate/`, `tests/full/`, `tests/tooling/`, `tests/tier_*`), so a nested directory under
`tests/hamletgen/` is selected exactly as the flat file was.

## Look here when

| file | look here when |
|---|---|
| `test_checks.py` (21) | the questions asked ABOUT a finished network - unreached houses, shared treads, crossings that land on crop or water |
| `test_clearance.py` (125) | may a way BE here - `clear_runs`, `_clear_link`, `_clear_touch`, `may_write`, the bend and nub judgments |
| `test_fabric.py` (210) | the settlement fabric a way must respect - `_crosses_fabric`, `_fabric_hits`, `_homestead_polys`, `_margin_frame`, `_draw_web` |
| `test_geom.py` (468) | point and segment math on a bare polyline - `polyline_len`, `_turn_deg`, `_components`, the two pushes, `_trim_to_service` |
| `test_route.py` (94) | the router: `_route` going round hard ground, `_unjog`, and the pad multiplier that lets a link take the long way |
| `test_serve.py` (154) | getting a way to a house that has none - `_lay_web_lane` and the straggler search |
| `test_sweeps.py` (247) | the passes that REMOVE or REPAIR - doubled remnants, steading fouls, end nubs, collinear breaks, orphaned pieces |
| `test_touch.py` (39) | how a lane end meets the network - `_touch_junctions` and the piece-joining it falls back on |
| `test_track.py` (19) | STAGE `stage_track` and `connector_track` - the way out of the frame and through the fabric |
| `test_web.py` (117) | STAGE `stage_web` and the skeleton it starts from - the settlement form roll and the dispersed short-circuit |
| `_builders.py` | the shared fixtures - `_lanes`, `_StubSettlement`, `_walled_settlement`, `_webbed`. The wider hamlet builders (`SQUARE`, `a_plan`) still come from `tests/hamletgen/_builders.py` one level up |
