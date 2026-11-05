"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _nuc_village, _village, seat_homestead


def test_nucleated_cluster_is_grove_less_with_yards_and_gardens():

    s = _nuc_village()
    s.lane([(300, 180), (322, 620)], width=5, clearance=11, worn=True)  # the WORN (unpaved) lane branch
    # SEATED ON A LATTICE AT THE PITCH, as the Rust seating records its households (feature 444 T30): no fit test asked here
    for gx in range(380, 640, 100):
        for gy in range(200, 720, 90)[:4]:
            seat_homestead(s, gx, gy)
    drawn = s.farmsteads()
    assert drawn >= 10
    assert s.M["lanes"] and s.M["lanes"][0]["worn"] is True  # worn lane recorded
    assert not s.M["groves"]  # nucleated -> NO per-house grove
    assert len(s.M["threshing_yards"]) >= drawn - 1  # each homestead keeps a yard
    assert len(s.M["gardens"]) >= drawn - 1  # ... and an (adaptive-side) garden


def test_rect_hits_detects_a_pure_edge_crossing():
    # the _rect_hits edge-cross arm: a plus-sign where neither shape has a corner/vertex inside the
    # other, but their edges cross - the corner-in / vertex-in fast paths both miss, so only the
    # per-edge segments_cross catches it. Plus a bbox-disjoint poly to exercise the early reject.
    s = _crop_settlement()
    assert s._rect_hits((500, 500, 200, 40), [[(480, 400), (520, 400), (520, 600), (480, 600)]])
    assert not s._rect_hits((500, 500, 40, 40), [[(900, 900), (950, 900), (950, 950), (900, 950)]])


def test_rect_on_water_blocks_a_solid_part_on_an_irrigation_line():
    # the homestead solver rejects a house/yard/garden that lands on a channel/ditch/stream, but NOT the grove
    s = _crop_settlement()
    s.M["field_ditches"] = [{"poly": [(400, 300), (400, 500)], "role": "drain", "w": 6, "field": "f"}]
    s.M["channels"] = [{"poly": [(600, 300), (600, 500)], "w": 2.5}]
    s.M["streams"] = [{"poly": [(800, 300), (800, 500)], "w": 9}]
    assert s._rect_on_water((400, 400, 24, 16)) is True  # garden straddling the drain -> seg_dist branch
    assert s._rect_on_water((360, 400, 100, 10)) is True  # a wide rect an edge of which the ditch CROSSES far from any corner -> segments_cross branch
    assert s._rect_on_water((600, 400, 20, 14)) is True  # on the feeder channel
    assert s._rect_on_water((800, 400, 20, 14)) is True  # on the stream
    assert s._rect_on_water((500, 400, 24, 16)) is False  # dry ground between them -> clear
    # the grove (fields=False) is exempt - it may hug a bund/ditch; the solid parts (fields=True) are not
    assert s._rect_blocked((400, 400, 24, 16), fields=False) is False
    assert s._rect_blocked((400, 400, 24, 16), fields=True) is True


def test_rect_on_water_skips_a_degenerate_course_and_far_ones():
    # the collision pre-filter: a degenerate (<2-point) course is dropped from _water_obstacles (it has no
    # segment and would crash the bbox min/max on an empty poly), and a course whose bbox is nowhere near
    # the rect is skipped without any seg_dist / crossing math.
    s = _crop_settlement()
    s.M["streams"] = [
        {"poly": [(100, 100)], "w": 9},  # degenerate: single point -> skipped
        {"poly": [(1500, 1300), (1500, 1400)], "w": 9},
    ]  # real, but far from the probe rect
    assert s._water_obstacles() == [(s.M["streams"][1]["poly"], 9 / 2 + 5, (1500, 1300, 1500, 1400))]
    assert s._rect_on_water((400, 400, 24, 16)) is False  # far course bbox-rejected -> clear


def test_garden_beds_clear_rejects_a_bed_on_a_neighbor():
    # the neighbor-footprint hit branch: a shifted bed landing on an actual drawn structure is rejected
    s = Settlement(800, 800, seed=5)
    s.meta(name="B", scale="village", ftpx=2, toscale=True)
    assert s._garden_beds_clear([(100, 100, 20, 14)], others=[(104, 102, 20, 14)]) is False
    assert s._garden_beds_clear([(100, 100, 20, 14)], others=[(300, 300, 20, 14)]) is True


def test_relax_gardens_south_skips_a_bundle_without_gardens():
    # defensive: a homestead bundle whose geom carries no garden beds is simply skipped (no shift, no error)
    s = Settlement(800, 800, seed=1)
    s.meta(name="V", scale="village", ftpx=2)
    rec = {"x": 100, "y": 100, "w": 23, "h": 14, "geom": {"house": (100, 100, 23, 14), "yard": (100, 120, 20, 16)}}  # no "gardens" key
    s._relax_gardens_south([rec])
    assert "gardens" not in rec["geom"]


def test_relax_gardens_south_nudges_an_east_shaded_garden_south():
    # a garden on the E lee side with a neighbor grove hard against its east, open ground south -> it shifts S
    s = Settlement(800, 800, seed=1)
    s.meta(name="V", scale="village", ftpx=2)
    s.grove_rects = [(340, 300, 16, 40)]  # a neighbor grove arm just east of the garden
    beds = [(320, 300, 12, 12)]  # garden east edge x=326; tree west edge=332 (in band)
    rec = {"x": 300, "y": 300, "w": 23, "h": 14, "geom": {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "gardens": list(beds)}}
    s._relax_gardens_south([rec])
    assert rec["geom"]["gardens"][0][1] > 300  # the bed moved SOUTH to clear the east tree
    # ...and a bundle that carries its parts' drawn boxes (269 B18) moves the bed's box with the bed
    rec = {"x": 300, "y": 300, "w": 23, "h": 14, "geom": {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "gardens": list(beds)}}
    rec["geom"]["boxes"] = {"house": (300, 300, 23, 14), "yard": (300, 322, 20, 12), "shed": None, "gardens": [(320, 300, 13, 13)]}
    s._relax_gardens_south([rec])
    moved = rec["geom"]["gardens"][0][1] - 300
    assert moved > 0 and rec["geom"]["boxes"]["gardens"][0][1] == 300 + moved, "the drawn box moved as far as the bed"


# ---- _rect_blocked: the hill/pond ELLIPSE branch -------------------------------------------
def test_rect_blocked_by_a_hill_or_pond_ellipse():
    s = _village()
    s.ellipses.append((300, 300, 80, 60))  # a hill/pond footprint
    assert s._rect_blocked((300, 300, 40, 26), fields=False) is True  # bed center inside the ellipse


# ---- _garden_beds_clear: a bed landing on a paddy ------------------------------------------
def test_garden_beds_clear_rejects_a_bed_on_a_paddy():
    s = _nuc_village()  # field_polys carries a paddy over the east half (x >= 640)
    assert s._garden_beds_clear([(880, 400, 30, 20)], []) is False  # bed sits in the paddy


# ---- feature 118: the composed RollingMixin surface ----------------------------------------------
# The one thing a package split can break SILENTLY. A member dropped by the transformer yields a
# package that imports cleanly, type-checks cleanly under mypy --strict, and draws nothing - it
# surfaces only when whichever generator calls that member happens to run. A member defined TWICE
# yields a working import, a clean typecheck, and one silently dead implementation, because the MRO
# just picks the first base. Contract: specs/118-rolling-package/contracts/mixin-surface.md.

_ROLLING_SURFACE = frozenset(
    {
        # public - called from pool gens, wip/, other engine modules and tests
        "farmsteads",
        "sun_corridor",
        "west_sun_lane",
        # private - reached through self., including from OUTSIDE the package
        "_bbox_of",
        "_bundle_geom",
        "_east_trees",
        "_farmsteads_bundle",
        "_garden_beds",
        "_garden_beds_clear",
        "_poly_bboxes",
        "_rect_blocked",
        "_rect_corners",
        "_rect_hits",
        "_rect_on_water",
        "_relax_gardens_south",
        "_water_obstacles",
        # class-level DATA, not a callable - a callable-only census would not notice it going
        # missing, which is the extra test feature 112 had to write after the fact
        "_NUC_SIDES",
    }
)


def _own_members(cls: type) -> set[str]:
    """Every non-dunder name this class body defines - data attributes included, not just callables."""
    return {k for k in vars(cls) if not k.startswith("__")}


def _rolling_sub_mixins() -> list[type]:
    from l7r.diagram.settlement.rolling import RollingMixin

    return [c for c in RollingMixin.__mro__ if c is not RollingMixin and c is not object]


def test_no_member_of_the_pre_split_rolling_surface_is_lost():
    # (the placer, the bundle fit and the seed forms the Python seating used left the surface with it, feature 444 T30)
    # SUPERSET, not equality, deliberately: a later decomposition legitimately adds named private
    # helpers, and equality would turn every such change into a contract edit - training a reader to
    # bump the frozenset without thinking, which is the reflex that lets a real subtraction through.
    from l7r.diagram.settlement.rolling import RollingMixin

    composed = set().union(*(_own_members(c) for c in RollingMixin.__mro__))
    assert composed >= _ROLLING_SURFACE, f"missing={sorted(_ROLLING_SURFACE - composed)}"


def test_no_rolling_member_is_defined_in_two_sub_mixins():
    # C1 cannot see this: a name defined in two bases still appears in the union, so a duplicate
    # passes C1, passes the import, passes mypy --strict, and runs whichever definition the MRO
    # reaches first - leaving the other as dead code a future reader will edit believing it is live.
    # The transformer refuses such a partition, but the transformer is a one-shot script; this test
    # outlives it and covers the member somebody adds by hand later.
    seen: dict[str, str] = {}
    dupes: list[str] = []
    for cls in _rolling_sub_mixins():
        for name in _own_members(cls):
            if name in seen:
                dupes.append(f"{name} in both {seen[name]} and {cls.__name__}")
            seen[name] = cls.__name__
    assert not dupes, f"defined twice: {sorted(dupes)}"


def test_no_shipped_hamlet_carries_a_cremation_ground_shrine_or_headman() -> None:
    """FR-003 (feature 273): within its district the village alone keeps the shrine, the headman's house and the
    cremation ground, and no shipped hamlet carries any of them."""
    import glob
    import json

    for path in glob.glob("pool/hamlets/*/*.json"):
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
        assert not m.get("cremation_grounds") and not m.get("shrines") and not m.get("religious"), path
        assert not any(h.get("role") == "headman" for h in m.get("houses", [])), path


# ---- feature 276 FR-003: the placed-house index answers every fit rule exactly as the linear scans did -------------


class _AllOf:
    """A stand-in for a PointGrid that returns every entry: the linear scan the index replaced."""

    def __init__(self, entries):  # type: ignore[no-untyped-def]
        self.entries = list(entries)

    def near(self, *_a, **_k):  # type: ignore[no-untyped-def]
        return self.entries


def test_a_house_moved_in_place_is_not_answered_from_its_old_box() -> None:
    """`_solve_homestead` moves a record; the house index must see the move (the list's version is bumped there)."""
    from l7r.diagram.settlement.rolling import fit

    houses = fit.Indexed([{"x": 100.0, "y": 100.0, "w": 30.0, "h": 20.0}])
    assert fit.houses_meeting(houses, (90, 90, 110, 110))
    houses[0]["x"] = 900.0
    houses._bump()
    assert not fit.houses_meeting(houses, (90, 90, 110, 110)) and fit.houses_meeting(houses, (890, 90, 910, 110))


def test_a_bundles_parts_are_turned_and_boxed_as_the_turn_helpers_turn_and_box_them() -> None:
    """`_bundle_geom` takes its turn's cosine and sine once for every part: each part's center is where `turn_about` carries
    it and each box is `turned_box`'s, at several turns - and the yard, rolled once per seat, is the same for every side."""
    from l7r.diagram.settlement._geom import turn_about
    from l7r.diagram.settlement.rolling.bearing import turned_box

    s = _nuc_village()
    for rot in (0.0, 7.5, -23.0, 90.0):
        for side in s._NUC_SIDES:
            flat = s._bundle_geom(500.0, 500.0, 46.0, 28.0, side, True, rot=0.0)
            geom = s._bundle_geom(500.0, 500.0, 46.0, 28.0, side, True, rot=rot)
            for k in ("yard", "shed"):
                ((x, y),) = turn_about([(flat[k][0], flat[k][1])], 500.0, 500.0, rot)
                assert geom[k] == (x, y, flat[k][2], flat[k][3])
                assert geom["boxes"][k] == turned_box(geom[k], rot)
            assert [turned_box(g, rot) for g in geom["gardens"]] == geom["boxes"]["gardens"]
            assert geom["yard"][2:] == s._bundle_geom(500.0, 500.0, 46.0, 28.0, "SE", True, rot=rot)["yard"][2:]
