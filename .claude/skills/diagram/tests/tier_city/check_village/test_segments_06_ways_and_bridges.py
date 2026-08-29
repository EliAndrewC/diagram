"""tier city tests split out of `tests.check_village.test_segments_06_ways_and_bridges` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import f_only


@pytest.mark.tiers("city")
def test_map_frame_hugs_its_content():
    """GM 2026-08-10: a stale per-side crop override (south=240, east=700) left dead margin on
    two flanks. Each side of the view needs real drawn content within 260 ft of the edge."""
    tight = {
        "meta": {"scale": "city", "ftpx": 3, "view": [0, 0, 900, 900]},
        "buildings": [{"x": 20, "y": 20, "w": 8, "h": 6, "rot": 0, "kind": "laborer"}, {"x": 880, "y": 880, "w": 8, "h": 6, "rot": 0, "kind": "laborer"}],
    }
    assert "map_frame_hugs_its_content" not in f_only(tight, "map_frame_hugs_its_content")
    loose = {
        "meta": {"scale": "city", "ftpx": 3, "view": [0, 0, 900, 3000]},
        "buildings": [{"x": 20, "y": 20, "w": 8, "h": 6, "rot": 0, "kind": "laborer"}, {"x": 880, "y": 400, "w": 8, "h": 6, "rot": 0, "kind": "laborer"}],
    }
    assert "map_frame_hugs_its_content" in f_only(loose, "map_frame_hugs_its_content")
