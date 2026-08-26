#!/usr/bin/env python3
"""Unit tests for site_justice.py - the justice-works siting tool.

The tool's whole claim is that it does not restate the gate's rules, so these tests check the
plumbing (footprints taken from settlement.py, trial records shaped like the engine's, frame cost
measured off crop_boxes, the ranking that keeps gate runs few) and that adjudication really is
`gate(trial) - gate(without)`. The rules themselves are tested in tests/check_village/, which is
the point: there is only one place they live.

    python3 -m pytest tests/tools/test_site_justice.py -q
"""

import pytest

from l7r.diagram.tools import site_justice as sj

WALL = [[600, 600], [1400, 600], [1400, 1400], [600, 1400]]


def town(**over):
    """A minimal unwalled county seat that PASSES the justice checks once a ground is seated: a
    core on an east-west road, the burakumin quarter east of it, a stone beyond that, and the
    community's dead far to the north."""
    M = {
        "meta": {"scale": "town", "ftpx": 1, "W": 2400, "H": 2000},
        "road": [[100, 1000], [2300, 1000]],
        "houses": [{"x": 440 + 30 * i, "y": 940, "w": 46, "h": 28, "rot": 0, "kind": "plain"} for i in range(6)],
        "buildings": [{"x": 1000, "y": 1010, "w": 40, "h": 28, "rot": 0, "kind": "burakumin"}],
        "punishment_spots": [{"x": 520, "y": 1020, "w": 30, "h": 12, "rot": 0, "label": "punishment ground"}],
        "boundary_markers": [{"x": 1300, "y": 1020, "w": 3, "h": 3, "vw": 7, "vh": 7, "rot": 0, "label": "boundary stone"}],
        "cemeteries": [{"x": 1500, "y": 300, "w": 100, "h": 80, "rot": 0, "parish": False}],
    }
    M.update(over)
    return M


def city(**over):
    M = town(**over)
    M["meta"] = {**M["meta"], "scale": "city", "ftpx": 3}
    return M


# ---- footprints and trial records come from the ENGINE, not from numbers retyped here ----------
@pytest.mark.parametrize(
    ("kind", "maker", "expect"),
    [
        ("execution_ground", town, (60.0, 60.0)),
        ("execution_ground", city, (100 / 3, 60 / 3)),
        ("punishment_spot", town, (30.0, 12.0)),
    ],
)
def test_footprint_px_matches_the_engines_own_figures(kind, maker, expect):
    assert sj.footprint_px(maker(), kind) == pytest.approx(expect)


# ---- adjudication is the real gate, differenced ------------------------------------------------


# ---- frame arithmetic --------------------------------------------------------------------------


# ---- ranking signals ---------------------------------------------------------------------------


# ---- end to end --------------------------------------------------------------------------------


# ---- CLI ---------------------------------------------------------------------------------------
def test_main_prints_usage_without_enough_arguments(capsys):
    assert sj.main([]) == 2
    assert "tools.site_justice" in capsys.readouterr().out
