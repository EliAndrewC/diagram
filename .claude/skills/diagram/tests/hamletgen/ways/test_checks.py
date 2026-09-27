"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways.checks import brook_fords, gap_segments, served_network, stream_segs, unreached_houses

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


def test_a_ford_is_opened_on_a_straight_reach_and_skipped_on_a_bend() -> None:
    """Feature 261: fords every `spacing` along the brook, on straight reaches only - a deck across a bend is not
    square to both reaches."""
    straight = [(0.0, 0.0), (1000.0, 0.0)]
    fords = brook_fords(straight, 160.0, 20.0)
    assert [round(x) for x, _y in fords] == [80, 240, 400, 560, 720, 880]
    bent = [(0.0, 0.0), (80.0, 0.0), (80.0, 400.0)]  # a right-angle turn 80 px in
    assert brook_fords(bent, 160.0, 20.0) == [(80.0, 160.0), (80.0, 320.0)], "the site at the bend is skipped; the straight reach after it keeps its own"
    assert brook_fords([], 160.0, 20.0) == [] and brook_fords([(5.0, 5.0), (5.0, 5.0)], 160.0, 20.0) == []


def test_a_gap_is_cut_out_of_the_brook_at_each_ford_and_nowhere_else() -> None:
    segs = [((0.0, 0.0), (100.0, 0.0)), ((100.0, 0.0), (200.0, 0.0))]
    cut = gap_segments(segs, [(100.0, 5.0)], 30.0)
    assert all(abs(p[1]) < 1e-9 for s in cut for p in s)
    ends = sorted(round(p[0], 3) for s in cut for p in s)
    assert ends == [0.0, 70.42, 129.58, 200.0], "sqrt(30^2 - 5^2) = 29.58 either side of the ford"
    assert gap_segments(segs, [(100.0, 50.0)], 30.0) == segs, "a ford out of reach cuts nothing"
    assert gap_segments([((3.0, 3.0), (3.0, 3.0))], [(3.0, 3.0)], 30.0) == [((3.0, 3.0), (3.0, 3.0))], "a zero-length piece is kept"
    assert gap_segments([((0.0, 0.0), (10.0, 0.0))], [(5.0, 0.0)], 30.0) == [], "a piece inside the gap is gone"


def test_the_streams_are_read_through_the_fords() -> None:
    class _S:
        M = {"streams": [{"poly": [[0, 0], [200, 0]]}]}
        brook_fords = [(100.0, 0.0)]

    assert len(stream_segs(_S())) == 2, "one stream, one ford, two pieces"


def test_an_oblique_crossing_is_squared_and_a_square_or_short_one_is_left() -> None:
    """Feature 261: a way crossing the brook more than FORD_SQUARE_TOL_DEG off square gets a leg along the brook's
    normal at the crossing; a square crossing, and one whose segment cannot hold the leg, are left as drawn."""
    from l7r.diagram.hamletgen.ways.checks import square_crossings

    brook = [(0.0, 0.0), (0.0, 200.0)]  # a brook running south
    oblique = [(-100.0, 20.0), (100.0, 180.0)]  # crosses at (0, 100), about 39 deg off square
    got = square_crossings(oblique, brook, 10.0)
    assert got[0] == oblique[0] and got[-1] == oblique[-1] and len(got) == 4
    (x1, y1), (x2, y2) = got[1], got[2]
    assert abs(y1 - y2) < 1e-9 and abs(x2 - x1 - 20.0) < 1e-9, "the new leg runs along the normal, west to east"
    back = square_crossings(list(reversed(oblique)), brook, 10.0)
    assert back[1][0] > back[2][0], "walked the other way, the leg runs east to west"
    square = [(-100.0, 100.0), (100.0, 101.0)]
    assert square_crossings(square, brook, 10.0) == square
    short = [(-5.0, 90.0), (5.0, 110.0)]
    assert square_crossings(short, brook, 15.0) == short
    assert square_crossings([], brook, 10.0) == []
    assert square_crossings(oblique, [(0.0, 0.0), (0.0, 0.0)], 10.0) == oblique
