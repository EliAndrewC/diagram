"""Feature 287, water W32: the fit's legality commands both flanks of the fork (`flanks_commanded`)."""

from __future__ import annotations

from l7r.diagram.hamletgen.water.fit import flanks_commanded


def _net(reach_b: float, extent_b: float = 400.0) -> dict:
    # the fall runs +y (down_deg 90), so the cross axis is x: flank A to the -x side of the fork at x=0, flank B to the +x
    plots = [{"poly": [(-400.0, 100.0), (-10.0, 100.0), (-10.0, 120.0)]}, {"poly": [(10.0, 100.0), (extent_b, 100.0), (10.0, 120.0)]}]
    channels = [{"role": "main", "pts": [(0.0, 0.0), (-300.0, 50.0)]}, {"role": "main", "pts": [(0.0, 0.0), (reach_b, 50.0)]}, {"role": "drain", "pts": [(0.0, 0.0), (900.0, 0.0)]}]
    return {"fork": (0.0, 0.0), "plots": plots, "channels": channels}


def test_a_flank_whose_supply_is_trimmed_short_is_uncommanded() -> None:
    """Canal B trimmed to 60 ft on a wide fan: its flank's 400 ft of plots are owed 120 ft of supply - illegal. The drain's
    reach counts for nothing."""
    assert not flanks_commanded(_net(60.0), 90.0)
    assert flanks_commanded(_net(130.0), 90.0)


def test_a_one_sided_fan_commands_no_second_flank_and_a_net_with_no_fork_is_not_judged() -> None:
    assert not flanks_commanded(_net(130.0, extent_b=120.0), 90.0), "120 ft of plots on the B side: no flank there"
    assert flanks_commanded({"plots": [], "channels": []}, 90.0)
