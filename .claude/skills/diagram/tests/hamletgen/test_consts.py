"""Guards on the researched constants - the couplings that are stated in prose and would otherwise
drift silently."""

from l7r.diagram.hamletgen.consts import BUNDLE_PITCH, MIN_WEB_GAP, WEB_CLEARANCE, WEB_REACH_FT
from l7r.diagram.hamletgen.ways import WEB_REACH_FT as _WEB_REACH


def test_the_web_reach_is_the_pages_100_ft_in_the_generator_and_in_the_gate() -> None:
    """THREE copies of one number, and this is what stops them drifting.

    `WEB_REACH_FT` is what the generator lays the web to satisfy, `_WEB_REACH` is what
    `farmhouses_reach_a_way` measures against, and both are 0246's "every farmhouse within 100 ft of one" (feature
    328: they were `BUNDLE_PITCH` while the pitch was 100; the pitch is 0038's 92 now). The gate deliberately does not import the generator's constant (a check that reads
    the value it is checking cannot catch that value being wrong), so the coupling has to live
    somewhere, and it lives here.

    If you are changing the reach, change all three and say why in `consts.py` - the number is
    derived from research, not tuned to make maps pass."""
    assert WEB_REACH_FT == 100.0
    assert _WEB_REACH == WEB_REACH_FT


def test_the_lane_clearances_are_the_lane_pages_figures() -> None:
    """Both clearances are 0246's (feature 328): the connector and spur keep a lane's middle 7 ft off a garden fence
    (`LANE_CLEARANCE`), and a web lane takes its 18 ft room between homesteads (`WEB_CLEARANCE`). The 40 ft once held off a
    lane the houses front was derived from the drawn minka's half-diagonal, a figure no page gives."""
    from l7r.diagram.hamletgen.consts import LANE_CLEARANCE

    assert (LANE_CLEARANCE, WEB_CLEARANCE) == (40.0, 18.0)  # 0246's 7 ft to a fence, held as a center corridor (feature 328 wave 7)


def test_the_web_only_threads_a_gap_a_person_can_walk() -> None:
    """`MIN_WEB_GAP` is the least room between two steadings a web lane will be cut through - a
    3 ft tread plus a hand's breadth each side, doubled for the two neighbors. It must stay well
    under the pitch, or there would be no gap in an ordinary row that qualifies."""
    assert 0 < MIN_WEB_GAP < BUNDLE_PITCH / 2
