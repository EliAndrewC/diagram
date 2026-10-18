"""`hamletgen/pondbank.py` - a tail pond's bank, bare or planted sparsely with mulberry and cudrania (feature 385 T08, 0061)."""

from __future__ import annotations

import math
import types

import pytest

from l7r.diagram.hamletgen import pondbank as pb
from l7r.diagram.hamletgen.consts import POND_BANK_CROWN_FT, POND_BANK_PITCH_FT, POND_BANKS
from l7r.diagram.hamletgen.plan import HamletSpec
from l7r.diagram.hamletgen.sink import SINK_FRINGE
from l7r.diagram.settlement import Settlement

POND = (400.0, 400.0, 80.0, 50.0)


def _plan(seed: int = 1, pond: tuple[float, float, float, float] | None = POND, form: str | None = None) -> types.SimpleNamespace:
    return types.SimpleNamespace(spec=types.SimpleNamespace(seed=seed, pond_bank=form), sink_pond=pond)


def _s() -> Settlement:
    s = Settlement(W=800, H=800, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    return s


def test_the_form_is_rolled_or_given_and_no_pond_has_no_bank() -> None:
    assert pb.pond_bank(_plan(pond=None)) == ""
    assert {pb.pond_bank(_plan(seed=k)) for k in range(40)} == set(POND_BANKS), "both forms come up across seeds"
    assert pb.pond_bank(_plan(seed=3, form="bare")) == "bare" and pb.pond_bank(_plan(seed=3, form="planted")) == "planted"


def test_a_spec_names_only_a_bank_the_generator_draws() -> None:
    with pytest.raises(ValueError, match="pond_bank"):
        HamletSpec(name="T", seed=1, households=12, pond_bank="hedged")


def test_the_seats_stand_beyond_the_reeds_about_a_pitch_apart() -> None:
    s = _s()
    seats = pb.bank_seats(s, POND)
    cx, cy, rx, ry = POND
    off = SINK_FRINGE + POND_BANK_CROWN_FT
    for x, y in seats:
        assert ((x - cx) / (rx + off)) ** 2 + ((y - cy) / (ry + off)) ** 2 == pytest.approx(1.0), "on the ring a crown beyond the fringe"
    gaps = [math.dist(a, b) for a, b in zip(seats, seats[1:] + seats[:1], strict=True)]
    assert sum(gaps) / len(gaps) == pytest.approx(POND_BANK_PITCH_FT, rel=0.2)


def test_a_seat_is_refused_on_a_roof_a_tread_the_crop_a_stream_or_off_the_canvas() -> None:
    s = _s()
    r = POND_BANK_CROWN_FT
    assert pb.seat_free(s, 600.0, 600.0, r), "open ground"
    assert not pb.seat_free(s, 2.0, 600.0, r), "off the canvas"
    s.M["houses"].append({"x": 600.0, "y": 600.0, "w": 40.0, "h": 20.0})
    assert not pb.seat_free(s, 600.0, 612.0, r), "a crown on a roof"
    s.lane([[100.0, 200.0], [700.0, 200.0]], width=5, clearance=7)
    assert not pb.seat_free(s, 300.0, 202.0, r), "a trunk on a tread"
    s.M.setdefault("fields", []).append({"outline": [[100.0, 650.0], [300.0, 650.0], [300.0, 750.0], [100.0, 750.0]]})
    assert not pb.seat_free(s, 200.0, 700.0, r), "a trunk in the crop"
    s.M.setdefault("streams", []).append({"poly": [[500.0, 300.0], [500.0, 500.0]], "w": 9.0})
    assert not pb.seat_free(s, 503.0, 400.0, r), "a trunk in a stream"
    assert pb.seat_free(s, 520.0, 400.0, r), "beside it is free"


def test_a_planted_bank_draws_its_trees_in_turn_and_records_them() -> None:
    s = _s()
    pb.stage_pond_bank(s, _plan(form="planted"))
    trees = s.M["pond_bank_trees"]
    assert len(trees) == len(pb.bank_seats(s, POND)) == s.M["meta"]["pond_bank_trees"] and s.M["meta"]["pond_bank"] == "planted"
    assert [t[3] for t in trees[:4]] == ["mulberry", "cudrania", "mulberry", "cudrania"]
    assert len(s.M["tree_crowns"]) == 3 * len(trees), "every crown in tree_crowns, for the structure tests"
    assert "pond-bank tree" in s.out_cls


def test_a_tree_whose_seat_is_taken_is_left_out_and_a_bare_bank_draws_none() -> None:
    s = _s()
    s.M["houses"].append({"x": 400.0, "y": 400.0 - 50.0 - SINK_FRINGE - POND_BANK_CROWN_FT, "w": 200.0, "h": 30.0})
    pb.stage_pond_bank(s, _plan(form="planted"))
    assert 0 < s.M["meta"]["pond_bank_trees"] < len(pb.bank_seats(s, POND))
    bare = _s()
    pb.stage_pond_bank(bare, _plan(form="bare"))
    assert bare.M["meta"]["pond_bank"] == "bare" and bare.M["meta"]["pond_bank_trees"] == 0 and "pond_bank_trees" not in bare.M
    none = _s()
    pb.stage_pond_bank(none, _plan(pond=None))
    assert "pond_bank" not in none.M["meta"]
