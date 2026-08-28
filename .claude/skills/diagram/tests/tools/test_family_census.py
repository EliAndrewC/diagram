"""`family_census` (feature 139): families and kinds present in one manifest and absent in the other."""

from __future__ import annotations

import json
from pathlib import Path

from l7r.diagram.tools import family_census as fc


def _m(**kw: object) -> dict[str, object]:
    return {"meta": {"name": "X"}, "labels": [[1, 2]], **kw}


def test_families_list_kinds_where_records_carry_one() -> None:
    f = fc.families(_m(farm_fixtures=[{"kind": "privy"}, {"kind": "bath"}], houses=[{"x": 1}], marshes=[{"role": "toe"}], empty=[]))
    assert f == {"farm_fixtures": {"privy", "bath"}, "houses": {"*"}, "marshes": {"toe"}}


def test_census_reports_each_side_and_the_kinds_inside_a_shared_family() -> None:
    a = _m(farm_fixtures=[{"kind": "privy"}, {"kind": "bath"}], dry_plots=[[0, 0]], houses=[{}])
    b = _m(farm_fixtures=[{"kind": "privy"}], dikes=[{"outline": []}], houses=[{}])
    c = fc.census(a, b)
    assert c["only_a"] == ["dry_plots", "farm_fixtures:bath"]
    assert c["only_b"] == ["dikes"]
    assert c["both"] == ["farm_fixtures", "farm_fixtures:privy", "houses"]


def test_report_names_both_maps_and_says_none_when_nothing_differs(tmp_path: Path) -> None:
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(_m(houses=[{}]) | {"meta": {"name": "Alpha"}}))
    pb.write_text(json.dumps(_m(houses=[{}]) | {"meta": {"name": "Beta"}}))
    out = fc.report(pa, pb)
    assert "A = Alpha" in out and "B = Beta" in out and "in Alpha only (0): none" in out and "in Beta only (0): none" in out


def test_main_prints_the_report(tmp_path: Path, capsys: object) -> None:
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(_m(houses=[{}])))
    pb.write_text(json.dumps(_m(byres=[{}])))
    assert fc.main(["--a", str(pa), "--b", str(pb)]) == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "- houses" in captured.out and "- byres" in captured.out
