"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""


def test_a_tail_run_alongside_another_way_is_cut_where_it_came_alongside() -> None:
    """Feature 261: `along_tail` finds where a lane's end starts running beside another way (within 14 ft, nearly parallel,
    30 ft or more); `cut_at_tail` ends it there, on its snap onto that way. A short approach or a crossing is no tail."""
    from l7r.diagram.hamletgen.ways.sweeps import along_tail, cut_at_tail

    way = [(0.0, 0.0), (300.0, 0.0)]
    lane = [(100.0, 200.0), (100.0, 10.0), (220.0, 10.0)]  # comes down to the way, then runs 120 ft beside it
    k = along_tail(lane, way)
    assert k is not None
    cut = cut_at_tail(lane, k, way)
    assert cut[0] == lane[0] and abs(cut[-1][1]) < 1e-9 and cut[-1][0] <= 112.0, "ends on the way where it came alongside"
    assert along_tail([(100.0, 200.0), (100.0, 10.0)], way) is None, "an approach that meets the way square is no tail"
    assert along_tail([(0.0, 50.0), (300.0, 50.0)], way) is None, "a lane 50 ft off is not alongside"
    assert along_tail(lane, [(5.0, 5.0)]) is None
    # feature 293 (Inashiro in the earlier 293 pass): a tail that runs back along a way to that way's own VERTEX is nearest
    # there to the other reach meeting at it; judged against that reach alone it was no tail, and a 95 ft retrace shipped
    bent = [(0.0, 100.0), (100.0, 0.0), (300.0, 0.0)]  # the way turns at (100, 0)
    retrace = [(300.0, 150.0), (300.0, 6.0), (100.0, 0.0)]  # comes down to it, then runs back along it to the vertex
    assert along_tail(retrace, bent) is not None
    # feature 293 on 291 (Mizuguchi's field spur): a tail that meets its way at an angle for its last few feet - inside
    # `_ALONG_FT` - and runs beside it before that is walked through the approach; a square T past it is still none
    spur = [(420.0, 100.0), (400.0, 10.0), (160.0, 10.0), (153.0, 0.0)]  # 10 ft off the way, then 12 ft at 55 degrees onto it
    assert along_tail(spur, way) is not None
    assert along_tail([(150.0, 200.0), (150.0, 0.0)], way) is None, "a square T is no tail past its approach either"


def test_a_doubled_tail_that_overran_the_way_ends_at_the_crossing() -> None:
    """Feature 261 (settlement-review of Sawada): a tail that crossed the way and ran on beside it is ended AT the
    crossing, not snapped back onto the way behind it - the snap drew a hook."""
    from l7r.diagram.hamletgen.ways.sweeps import along_tail, cut_at_tail

    other = [(0.0, 0.0), (200.0, 0.0)]
    lane = [(100.0, -60.0), (100.0, 6.0), (60.0, 6.0)]  # crosses at (100, 0), then runs back 40 ft beside it
    k = along_tail(lane, other)
    assert k is not None
    assert cut_at_tail(lane, k, other)[-1] == (100.0, 0.0)


def test_a_cut_on_a_later_leg_keeps_the_vertices_before_it() -> None:
    """`cut_at_tail` on a lane whose cut sample lies on its THIRD leg: the vertices before the cut are kept, in order, and
    the one past it goes with the tail."""
    from l7r.diagram.hamletgen.ways.sweeps import cut_at_tail

    got = cut_at_tail([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)], 5, [(0.0, 6.0), (60.0, 6.0)])
    assert got[:3] == [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)] and (30.0, 0.0) not in got
