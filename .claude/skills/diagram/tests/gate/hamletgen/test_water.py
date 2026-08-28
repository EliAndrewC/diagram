"""gate tests split out of `tests.hamletgen.test_water` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import point_in_poly, seg_dist

# SERVED FROM THE ROLL CACHE (feature 135): each polder is ~50-100 s to roll and nothing here patches the engine,
# so `rollcache.hamlet` serves the plan and finished manifest while every function the roll executed is unchanged,
# and rolls for real the moment one moves. The assertions run on the served map either way.


@pytest.mark.rolls_map
def test_a_polder_inlets_mouth_is_pulled_INSIDE_the_crop() -> None:
    """THE RATCHET for `draw_comb_field`'s constructed inlet end (2026-08-15).

    That end is not clipped from an anchor - it is BUILT, as the main channel's last point stepped
    70 px straight downhill, which is a COMB's geometry. On a polder the main is the ring canal
    running ALONG the high edge, so its last point is a corner and the step skims the boundary:
    seed 19 landed the mouth 2.6 px inside where `channel_field_anchored` wants 10, and no amount of
    moving the sluice changed it, because the anchor is not what sets this end.

    Seed 19 is chosen deliberately - it is the case that needed the pull (seed 3 needs it at 6.0 px,
    seed 8 does not need it at all), so this test exercises the branch rather than merely passing."""
    _plan, M = rollcache.hamlet(hg.HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90))
    env = [(float(a), float(b)) for a, b in M["fields"][0]["outline"]]
    n = len(env)
    fed = [c for c in M["channels"] if (c.get("to") or {}).get("kind") == "field"]
    assert fed, "the polder is fed by a channel from its header reservoir"
    for c in fed:
        end = c["poly"][-1]
        assert point_in_poly(end[0], end[1], env), f"the inlet mouth {end} must finish INSIDE the crop"
        gap = min(seg_dist(end[0], end[1], env[k], env[(k + 1) % n]) for k in range(n))
        assert gap >= 10.0, f"the mouth is {gap:.1f} px from the outline; the rule wants 10 so the field paints over it"


@pytest.mark.rolls_map
def test_a_polder_reservoir_backs_off_until_its_rim_clears_the_crop() -> None:
    """The seat is measured from the ring canal's HEAD, so anything that moves that head moves the
    reservoir - trimming the ring's doubling-back stub did exactly that and slid the pond onto the
    crop. A fixed stand-off from a moving anchor is the pinned-constant mistake in miniature, so the
    rim is tested and the pond walks uphill until it is clear.

    Seed 12 is chosen because it NEEDS the walk (one step at falls 0 and 180); seeds 3, 8, 19 and 22
    clear on the first try, so testing one of those would exercise nothing."""
    plan, M = rollcache.hamlet(hg.HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0))
    pond = M.get("pond")
    assert pond, "the polder's water source is its header reservoir"
    rim = [(pond[0] + pond[2] * math.cos(a), pond[1] + pond[3] * math.sin(a)) for a in (k * math.pi / 8 for k in range(16))]
    assert not any(point_in_poly(q[0], q[1], list(plan.envelope)) for q in rim), "no part of the rim may lie on the crop"
    # ...and it stays UPHILL of the field, which is the rule the walk must not trade away
    dx, dy = plan.fall
    assert pond[0] * dx + pond[1] * dy < min(p[0] * dx + p[1] * dy for p in plan.envelope), "the source sits above what it waters"


@pytest.mark.rolls_map
def test_a_polder_hamlet_draws_its_grid_dike_and_reservoir() -> None:
    """THE SECOND FIELD ARCHETYPE (GM 2026-08-13), pinned at what it currently guarantees.

    The polder is WORK IN PROGRESS - it has two named gate failures in `build_polder`'s own geometry
    (see hamletgen.md) - so this does not assert a clean gate, which would be a lie. It asserts the
    things the substrate is already responsible for and which no other test covers: that the grid is
    solved to the acreage the households imply, that every household is seated, that the defining
    perimeter dike exists, and that the header reservoir sits OUTSIDE the crop rather than in it,
    which two earlier versions of the siting got wrong in two different ways."""
    plan, M = rollcache.hamlet(hg.HamletSpec(name="Polder", seed=8, households=16, field_archetype="polder_grid"))
    assert plan.field_archetype == "polder_grid"
    assert M["meta"]["field_archetype"] == "polder_grid"
    assert abs(plan.acres - plan.target_acres) / plan.target_acres < 0.12, f"{plan.acres:.1f} acres against a {plan.target_acres:.1f} target"
    assert plan.placed == plan.spec.households
    assert M.get("dikes"), "a polder without its perimeter dike is not a polder"
    assert len(M.get("sluice_gates") or []) == len(M["dikes"][0]["gaps"]) >= 2, "a gate at every cut of the dike (feature 139 A7)"
    pond = M.get("pond")
    assert pond, "the header reservoir is the polder's water source"
    assert not point_in_poly(pond[0], pond[1], list(plan.envelope)), "the reservoir sits BESIDE the crop, never in it"


@pytest.mark.rolls_map
def test_a_dike_pond_hamlet_is_ponds_in_a_diked_block_with_wet_flanks() -> None:
    """THE THIRD FIELD ARCHETYPE (feature 139, Kuwabata): the polder carried to the wholesale
    dike-pond conversion. Asserts what the archetype is responsible for beyond the polder: the
    overlay record, the dike-pond parcels, the declared arrangement, and the waterward fringe
    (declared AND wet, so `polder_waterward_flanks_wet` has teeth rather than skipping)."""
    plan, M = rollcache.hamlet(hg.HamletSpec(name="Dikepond", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic"))
    m = M["meta"]
    assert m["field_archetype"] == "mulberry_dike_fishpond" and m["pond_layout"] == "mosaic"
    assert any(r["overlay"] == "mulberry_fishpond" and r["count"] >= 20 for r in M["land_use"])
    assert M.get("dikeponds"), "the ponds are recorded as dike-ponds"
    assert 1 <= sum(1 for d in M["dikeponds"] if d.get("kind") == "fry") <= 3, "a few of the smallest parcels are fry nursery ponds (feature 139 A5)"
    assert plan.placed == plan.spec.households
    assert set(m["waterward"]) and set(m["waterward"]) <= {"N", "E", "S", "W"}
    assert sum(1 for q in M["marshes"] if q.get("role") == "waterside") == len(m["waterward"])
    # no threshing yards on a no-rice hamlet (feature 139 T41, GM 2026-08-28) - declared and drawn so
    assert m["work_yards"] is False and M["threshing_yards"] and all(y.get("kind") == "forecourt" for y in M["threshing_yards"])
