"""The pig sty against its farmhouse (feature 374 wave 151, `hamletgen/homesteads/sties.py`, 0049): seated against its
farmstead's walls in the house's frame once the ways stand, to the share's count, passed on where a farm has no room."""

from __future__ import annotations

import types

import pytest

from l7r.diagram.hamletgen.homesteads import sties as st
from l7r.diagram.settlement import Settlement


def _s() -> Settlement:
    s = Settlement(W=800, H=800, seed=3)
    s.meta(name="T", scale="hamlet", ftpx=1)
    return s


def _plan(archetype: str = "valley_paddy") -> types.SimpleNamespace:
    return types.SimpleNamespace(field_archetype=archetype)


HOUSE = {"x": 200.0, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 30.0}


def test_the_frame_turns_with_the_house_and_back() -> None:
    q = st.to_frame((230.0, 210.0), HOUSE)
    assert st.to_world(q, HOUSE) == pytest.approx((230.0, 210.0))
    assert st.to_frame((200.0, 200.0), {"x": 200.0, "y": 200.0}) == (0.0, 0.0), "a house with no rake"


def test_a_part_square_to_the_house_keeps_its_box_and_one_askew_its_bounds() -> None:
    assert st.in_frame({"x": 200.0, "y": 200.0, "w": 10.0, "h": 4.0, "rot": 32.0}, HOUSE) == ((0.0, 0.0, 10.0, 4.0), True)
    box, square = st.in_frame({"x": 200.0, "y": 200.0, "w": 10.0, "h": 4.0, "rot": 118.0}, HOUSE)
    assert square and box[2:] == (4.0, 10.0), "across the house: a quarter turn"
    box, square = st.in_frame({"x": 200.0, "y": 200.0, "w": 10.0, "h": 4.0, "rot": 75.0}, HOUSE)
    assert not square and box[2] > 10.0 * 0.7 and box[3] > 4.0, "askew: the box round its corners"


def test_the_farmstead_is_the_house_its_outbuildings_and_its_plots_parts() -> None:
    M = {
        "retirement_houses": [{"x": 170.0, "y": 200.0, "w": 18.0, "h": 15.0, "rot": 120.0, "of": [200.0, 200.0]}],
        "farm_fixtures": [
            {"kind": "woodpile", "x": 200.0, "y": 170.0, "w": 24.0, "h": 12.0, "rot": 30.0, "of": [200.0, 200.0]},
            {"kind": "privy", "x": 230.0, "y": 170.0, "w": 6.0, "h": 6.0, "rot": 30.0, "of": [200.0, 200.0]},
            {"kind": "privy", "x": 500.0, "y": 500.0, "w": 6.0, "h": 6.0, "rot": 0.0, "of": [480.0, 480.0]},
        ],
        "byres": [{"x": 210.0, "y": 230.0, "w": 16.0, "h": 11.0, "rot": 0}],  # no `of`: not this farm's to know
        "gardens": [{"poly": [[0, 0]], "of": [200.0, 200.0]}],
    }
    walls, parts = st.farmstead(M, HOUSE)
    assert len(walls) == 3 and len(parts) == 4, "the house, the retirement house, the wood shed; and the privy among the parts"


def test_the_stage_draws_the_shares_count_and_passes_a_crowded_farms_sty_on(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _s()
    s.M["houses"] = [dict(HOUSE), {"x": 500.0, "y": 500.0, "w": 46.0, "h": 28.0, "rot": 0.0}, {"x": 650.0, "y": 300.0, "w": 40.0, "h": 26.0}]
    monkeypatch.setattr(st, "fixture_shares", lambda seed, arch: {"sty": 0.67})
    monkeypatch.setattr(st, "quota_carriers", lambda seed, salt, n, p: [True, True, False])
    crowded = s.M["houses"][0]
    real = st.sty_seat
    monkeypatch.setattr(st, "sty_seat", lambda s_, h: None if h is crowded else real(s_, h))
    st.stage_sties(s, _plan())
    drawn = [r for r in s.M["farm_fixtures"] if r["kind"] == "sty"]
    assert len(drawn) == 2 and s.M["meta"]["sty_target"] == 2 and s.M["meta"]["sty_short"] == 0, "the third house kept the first's"
    assert {tuple(r["of"]) for r in drawn} == {(500.0, 500.0), (650.0, 300.0)}
    assert s.top_cls[-1] == "pig sty", "drawn on top, as every fixture"


def test_a_place_the_registry_refuses_moves_along_and_no_place_keeps_none(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _s()
    asked: list[dict] = []

    def admits(key: str, rec: dict) -> bool:
        asked.append(rec)
        return len(asked) > 1

    monkeypatch.setattr(s, "admits", admits)
    rec = st.sty_seat(s, HOUSE)
    assert rec is not None and len(asked) == 2 and (rec["x"], rec["y"]) != (asked[0]["x"], asked[0]["y"])
    assert rec["of"] == [200.0, 200.0] and rec["rot"] == 30.0
    monkeypatch.setattr(s, "admits", lambda key, rec: False)
    assert st.sty_seat(s, HOUSE) is None
    s.M["houses"] = [dict(HOUSE)]
    monkeypatch.setattr(st, "fixture_shares", lambda seed, arch: {"sty": 1.0})
    st.stage_sties(s, _plan())
    assert s.M["meta"]["sty_short"] == 1 and not [r for r in s.M.get("farm_fixtures", []) if r["kind"] == "sty"]


def test_a_sty_keeps_off_its_own_grove() -> None:
    """Feature 374 wave 151: a sty on its farm's grove band failed four cohort rolls (`fixtures_on_groves`, 0036)."""
    M = {"groves": [{"x": 200.0, "y": 170.0, "w": 60.0, "h": 20.0, "rot": 0, "of": [200.0, 200.0]}]}
    _walls, parts = st.farmstead(M, HOUSE)
    assert len(parts) == 2, "the house and its grove band"


def test_the_sty_placer_asks_the_checks_own_band_predicate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T03, plan D18: the placer read a grove band in the house's frame, snapped square under 10 degrees of turn, and
    cohort seed 45's two sties stood 0.5 and 2.7 ft into bands the check reads as recorded. The placer now asks
    `grove_rules.fixture_on_band`, the check's own predicate, and takes the next place where it is on a band."""
    from l7r.diagram.settlement.homestead_parts import grove_rules as gr

    s = _s()
    house = {**HOUSE, "rot": 0.0}
    s.M["houses"] = [house]
    first = st.sty_seat(s, house)
    assert first is not None
    band = {"x": first["x"], "y": first["y"], "w": 4.0, "h": 4.0, "of": [house["x"], house["y"]]}
    s.M["groves"] = [band]
    assert gr.fixture_on_band(first, band) and gr.fixtures_on_groves({"groves": [band], "farm_fixtures": [first]}) == [("sty", band)]
    second = st.sty_seat(s, house)
    assert second is not None and (second["x"], second["y"]) != (first["x"], first["y"]) and not gr.fixture_on_band(second, band)
    assert not gr.fixture_on_band({"x": 0.0, "y": 0.0}, band), "a fixture with no box has no footprint"
    assert gr.grove_bands({"groves": [band, {"x": 1.0}]}) == [band]
