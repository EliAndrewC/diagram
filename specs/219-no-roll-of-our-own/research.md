# Research - 219 no roll of our own

## R1. The audit the GM asked for: every roll a gate makes, and whether it converts (2026-09-08)

Off feature 217's landed census (specs/217 research R2, a COLD run: every shipped generator re-rolled), the seven rolls
a gate made, each with the engine lines its coverage context reached that no other context did:

| roll | requested by | unique lines | of which engine / machinery | converts? |
|---|---|---|---|---|
| Inashiro 4, the immune experiment's perturbed roll | `test_a_map_is_immune...` | 17 | 0 engine / 17 machinery (`rollcache.py` 393-420: `extra_draws`, `_perturbed_manifest`) | RETIRED with its requirement (FR-001): the lines exist only to perturb the roll |
| Polder 12 | the fan-out ratchet (whichever reader asks first) | 8 | 3 engine (`hamletgen/water.py` 414, 475, 574) / 5 machinery (`rollcache.py` 431, 433-435, 531: `_roll_payload`, `hamlet`) | YES (FR-003): each engine line a unit test of the function that owns it, the machinery on stubs, the behavior to the soak tier |
| Inashiro 4, the shipped generator (cold) | `test_the_cli_reports_a_single_hamlet` | **0** | - | NO, as a class (below) |
| Kashikawa 3, the shipped generator (cold) | the sweep | 5 | 5 engine (`ways/serve.py` 109; `ways/web.py` 454, 457; `structures/fixtures/siting.py` 221-222) | NO, as a class |
| Kuwabata 21, the shipped generator (cold) | the overlaps fixture (first reader) | 21 | 21 engine (`water.py` 450-457, 580; `ways/clearance.py` 173; `fields/comb.py` 516-534) | NO, as a class |
| Mizuguchi 23, the shipped generator (cold) | the sweep | 11 | 11 engine (`ways/serve.py` 463; `ways/sweeps.py` 189; `water_ways/lanes.py` 198-211) | NO, as a class |
| Sawada 6, the shipped generator (cold) | the sweep | 11 | 11 engine (`sink.py` 168-169; `ways/route.py` 147-149; `ways/touch.py` 237, 239; `shrines_wells/byres.py` 37, 100; `water_ways/lanes.py` 207-208) | NO, as a class |

**The two rolls of the gate's own both convert**, so the roster ends with no `Roll` row: a warm gate rolls nothing of
its own, a cold gate the five shipped generators. The three polder engine lines: 414 is the stop of the reservoir's
uphill walk when its rim clears the crop (`walk_pond_uphill`, lifted), 475 a dike gap appended where a channel crosses
the ring more than 30 ft from a listed gap (`dike_gaps_at_channels`, lifted), 574 `fit_polder`'s stop when the solved
grid lands inside the acreage tolerance. The five machinery lines are `_roll_payload` and `hamlet`/`report`, which
exist to roll a spec: on stubs (`hg.generate`, `_hamlet_in_child` stood in for) they are covered in milliseconds.

**The five shipped generators, as one class.** The Inashiro cold roll reaches ZERO lines of its own - exactly the shape
the GM asked about - and the other four reach 5 to 21 each. None converts, for one reason that is not a coverage
reason: a shipped map is rolled because it ships. The pool sweep (`test_village_passes_gate`) regenerates each map when
its cache key moved and judges the result, and the gate's readers take the pool's maps rather than rolling their own
(feature 215). Which maps are in the pool is the GM's exhibit decision (217 FR-001a), so the lever on those five cold
rolls is the pool's contents - a map the GM stops shipping stops being rolled - and this feature does not touch it. The
verdict prints each one's count on every cold gate, so the Inashiro zero is seen rather than hidden; what it says is that
the reference's every line is also reached by the other four maps and the unit tests, not that the map should go.

**What the floor's subjects lose.** `tools/hamlet_floor.subjects()` drops Polder 12 (its record came from the roll
cache; the two shipped maps' come from the gen cache). The floor's docstring records that every subject has zero modules
unique to it, so the hamlet-path module set should not move; R2 measures it by the floor's statement count.

## R2. Measured after

(The census on the landed gate, warm and cold; the gate time; the hamlet-path floor's statement count before, 13,012,
and after; the soak tier's polder module by hand.)
