"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways.checks import served_network, unreached_houses

from .._builders import SQUARE


def test_a_shallow_crossing_is_distinguished_from_a_square_one() -> None:
    """A way may cross a ditch - that is what a plank is for - but not at a slant."""
    ditch = ((0.0, 0.0), (100.0, 0.0))
    assert not hg.shallow_crossing((50.0, -50.0), (50.0, 50.0), *ditch)  # square
    assert hg.shallow_crossing((0.0, -10.0), (100.0, 10.0), *ditch)  # a slant
    assert not hg.shallow_crossing((0.0, 100.0), (100.0, 100.0), *ditch)  # never meets it


def test_a_way_that_misses_the_watercourse_lands_on_nothing() -> None:
    """`crossing_lands_on_crop` answers about the CROSSING POINT, so a way that never meets the
    course has no crossing point and no verdict to give."""
    assert not hg.crossing_lands_on_crop((0.0, 0.0), (10.0, 0.0), (0.0, 50.0), (10.0, 50.0), [SQUARE])
    # ...and one that meets it inside the crop does
    assert hg.crossing_lands_on_crop((700.0, 300.0), (700.0, 900.0), (400.0, 700.0), (1000.0, 700.0), [SQUARE])


def test_served_network_grows_from_the_LONGEST_lane_when_no_connector_is_drawn() -> None:
    """Feature 174. The seed is the connector where one exists - every scripted hamlet draws one, so
    the fallback had never run. A map with no connector still has a network, and the rule it serves
    ("a check satisfiable by an island rewards drawing an island") needs the biggest island, not the
    first. Both branches asserted: with a connector present the connector wins even when shorter.
    """
    short = {"pts": [(0.0, 0.0), (10.0, 0.0)]}
    long_ = {"pts": [(0.0, 500.0), (400.0, 500.0)]}
    segs = served_network([short, long_])
    assert segs == [((0.0, 500.0), (400.0, 500.0))], "the longer isolated lane is the network"

    segs = served_network([{**short, "connector": True}, long_])
    assert segs == [((0.0, 0.0), (10.0, 0.0))], "a drawn connector seeds the network however short it is"


def test_unreached_houses_is_empty_when_no_lane_network_was_drawn() -> None:
    """The rule does not apply to a map with no ways - a dispersed hamlet draws none by design, so
    the answer is 'no complaint', not 'every house unreached'."""
    # `meta.generated_by` is what makes the rule APPLY at all - without it the function returns at
    # its first guard and never reaches the one this test is for. (Measured: the first version of
    # this test passed while covering nothing, which a FULL run caught and the assertion did not.)
    meta = {"generated_by": "hamletgen", "settlement_form": "nucleated"}
    M = {"meta": meta, "houses": [{"x": 0.0, "y": 0.0}, {"x": 900.0, "y": 900.0}], "lanes": []}
    assert unreached_houses(M) == [], "no network drawn, so the rule has nothing to measure against"
    assert unreached_houses({"meta": {**meta, "settlement_form": "dispersed"}, "houses": M["houses"]}) == [], "a dispersed hamlet has no internal network by definition"
    reached = {"meta": meta, "houses": [{"x": 50.0, "y": 0.0}], "lanes": [{"pts": [(0.0, 0.0), (100.0, 0.0)], "connector": True}]}
    assert unreached_houses(reached) == [], "a house on the network is not reported"
    stranded = {"meta": meta, "houses": [{"x": 50.0, "y": 5000.0}], "lanes": [{"pts": [(0.0, 0.0), (100.0, 0.0)], "connector": True}]}
    assert unreached_houses(stranded) == [(50, 5000, 5000)], "and one the network does not reach IS"


# ---- feature 276 FR-005: the PathChecker answers exactly what path_violations does ------------------------------


def test_the_path_checker_counts_what_path_violations_counts_on_inashiros_candidates() -> None:
    """Every candidate path the track stage asked about on Inashiro seed 4, with the water, crop and pond it asked
    against - captured from a real roll into a fixture, so the equality is proved on the inputs the stage actually
    meets (four argument sets, 83 paths; the largest holds 21 crop rings and 523 water segments)."""
    import json
    import pathlib

    from l7r.diagram.hamletgen.ways.checks import PathChecker, path_violations

    sets = json.loads((pathlib.Path(__file__).resolve().parents[2] / "fixtures" / "track_candidates_inashiro_seed4.json").read_text())
    asked = 0
    for entry in sets:
        a = entry["args"]
        avoid = [[tuple(p) for p in poly] for poly in a["avoid"]]
        pond = tuple(a["pond"]) if a["pond"] else None
        brook = [(tuple(p), tuple(q)) for p, q in a["brook"]]
        waters = [(tuple(p), tuple(q)) for p, q in a["waters"]]
        chk = PathChecker(avoid, pond, brook, waters)
        for path in entry["paths"]:
            pts = [tuple(p) for p in path]
            assert chk.violations(pts) == path_violations(pts, avoid, pond, brook, waters)
            asked += 1
    assert asked >= 80, "non-vacuity: the fixture's paths were all asked"


def test_the_path_checker_matches_on_random_water_crop_and_brook() -> None:
    """Random geometry with every clause live - a pond, brook segments, crop rings, many water segments - so the
    prune is tested where a real map might not reach (a brook, a path wholly inside a crop ring)."""
    import random

    from l7r.diagram.hamletgen.ways.checks import PathChecker, path_violations

    r = random.Random(276)
    for _ in range(40):

        def seg():  # type: ignore[no-untyped-def]
            x, y = r.uniform(0, 1000), r.uniform(0, 1000)
            return ((x, y), (x + r.uniform(-120, 120), y + r.uniform(-120, 120)))

        waters = [seg() for _ in range(60)]
        brook = [seg() for _ in range(6)]
        avoid = []
        for _ in range(5):
            cx, cy, rr = r.uniform(100, 900), r.uniform(100, 900), r.uniform(20, 90)
            avoid.append([(cx + rr, cy - rr), (cx + rr, cy + rr), (cx - rr, cy + rr), (cx - rr, cy - rr)])
        pond = (r.uniform(0, 1000), r.uniform(0, 1000), 30.0, 20.0)
        chk = PathChecker(avoid, pond, brook, waters)
        for _ in range(10):
            path = [(r.uniform(0, 1000), r.uniform(0, 1000)) for _ in range(r.randint(2, 6))]
            assert chk.violations(path) == path_violations(path, avoid, pond, brook, waters)
        inside = [(avoid[0][0][0] - 5, avoid[0][0][1] + 5), (avoid[0][0][0] - 6, avoid[0][0][1] + 8)]  # wholly inside a ring
        assert chk.violations(inside) == path_violations(inside, avoid, pond, brook, waters)
