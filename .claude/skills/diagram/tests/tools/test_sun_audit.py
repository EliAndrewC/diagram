"""`make sun-audit` - the sun and belt-presence measurement read off a manifest (feature 133 T10)."""

import json

from l7r.diagram.tools import sun_audit


def _M():
    return {
        "meta": {"scale": "hamlet", "ftpx": 1, "view": [100, 0, 900, 900]},
        "houses": [{"x": 400, "y": 400, "w": 46, "h": 28}, {"x": 400, "y": 470, "w": 46, "h": 28}, {"x": 700, "y": 400, "w": 46, "h": 28}],
        "threshing_yards": [{"x": 400, "y": 430, "w": 36, "h": 26, "of": [400, 400]}],  # bottom 443, neighbor wall 456: 13 ft
        "gardens": [{"x": 700, "y": 400, "w": 22, "h": 24, "of": [700, 400]}, {"x": 250, "y": 400, "w": 22, "h": 24, "of": [400, 400]}],
        "village_groves": [
            {"role": "windbreak", "r": 14, "clumps": [[120, y] for y in range(300, 601, 25)] + [[200, 400]], "poly": []},
            {"role": "copse", "r": 11, "clumps": [[230, 400]], "poly": []},
        ],
    }


def test_south_gaps_skip_the_own_house_and_report_the_neighbor():
    M = _M()
    got = sun_audit.south_gaps(M["threshing_yards"], M["houses"], 1.0)
    assert got == [(400, 430, 13.0)]
    beds = sun_audit.south_gaps(M["gardens"], M["houses"], 1.0)
    assert beds[0][2] is None, "a bed with only its own house south of it has no neighbor"


def test_west_gaps_read_windbreak_clumps_only():
    M = _M()
    belts = [g for g in M["village_groves"] if g["role"] == "windbreak"]
    got = sun_audit.west_gaps(M["gardens"], belts, 1.0)
    assert got[1] == (250, 400, 25.0), "the clump at 200 is 25 ft west of the bed's west edge 239 (r 14)"
    assert got[0] == (700, 400, 475.0), "the lane has no far limit - the nearest clump in it is reported at any distance"
    assert sun_audit.west_gaps(M["gardens"], [], 1.0)[0][2] is None, "no belt, no gap"


def test_belt_presence_measures_depth_from_the_view_edge_on_the_belts_side():
    M = _M()
    pres = sun_audit.belt_presence(M["village_groves"][0], M["houses"], M["meta"]["view"])
    assert pres["axis"] == "x" and pres["edge"] == 100
    assert pres["off_page"] == 0 and pres["blank"] == 0
    assert 34 in pres["depths"] and max(pres["depths"]) == 114, "120 + 14 - 100 = 34 per band; the 200 clump's band reaches 114"
    assert sun_audit.belt_presence({"clumps": [], "r": 14}, M["houses"], M["meta"]["view"]) is None


def test_report_names_the_offenders(tmp_path, capsys):
    M = _M()
    out = sun_audit.report(M)
    assert "under 39: [(400, 430, 13)]" in out and "under 50: [(250, 400, 25)]" in out
    assert "blank bands 0" in out
    p = tmp_path / "m.json"
    p.write_text(json.dumps(M))
    assert sun_audit.main([str(p)]) == 0
    assert "sun-audit" in capsys.readouterr().out
    M["village_groves"][0]["clumps"] = []
    assert "no face" in sun_audit.report(M)
