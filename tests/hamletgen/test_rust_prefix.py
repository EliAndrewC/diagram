"""`hamletgen/rust_prefix.py` (feature 444 amendment 5, FR-019; SC-012): the Rust stages derived from `rust/phases/src/`, held to
the front of `STAGES`, a roll through them alone that keeps each failing stage's input, and the reads a check makes of a map."""

from __future__ import annotations

import copy
import pathlib
import pickle

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen import rust_prefix as rp
from l7r.diagram.hamletgen.driver import STAGES


def _wf(s: object, plan: object) -> None:  # a stand-in water_frame: writes the plan's form into the meta, rolls no map
    s.M.setdefault("meta", {})["settlement_form"] = plan.settlement_form  # type: ignore[attr-defined]


_wf.__name__ = "stage_water_frame"


def test_the_rust_stages_are_derived_from_the_crate_and_held_to_the_front(tmp_path: pathlib.Path) -> None:
    assert [rp.stage_name(st) for st in rp.rust_stages()] == ["water_frame"], "the port T19 landed, and only it"
    (tmp_path / "field.rs").write_text("")
    (tmp_path / "pyrand.rs").write_text("")  # a helper module, no stage
    got = rp.rust_stages(src=tmp_path)
    assert [rp.stage_name(st) for st in got] == ["field"]
    assert rp.off_the_front(STAGES, got) == ["field"], "field without water_frame before it: not the front"
    assert rp.off_the_front(STAGES, list(STAGES[:2])) == []


def _plan(seed: int = 5) -> object:
    return copy.deepcopy(hg.plan_site(hg.HamletSpec(name="X", seed=seed, households=12)))


def test_a_roll_stops_where_the_rust_stages_end_and_a_failing_stage_leaves_its_input() -> None:
    plan = _plan()
    s, failed, err, trace = rp.roll_through(plan, [_wf])
    assert failed is None and err is None and s.M["meta"].get("settlement_form"), "water_frame ran and wrote the plan's meta"
    assert [name for name, _f, _w in trace] == ["water_frame"] and "meta.settlement_form" in trace[0][2], "what it wrote, traced"

    def boom(_s: object, _plan: object) -> None:
        raise ValueError("no seat")

    boom.__name__ = "stage_boom"
    s, failed, err, trace = rp.roll_through(_plan(), [_wf, boom])
    assert failed == "boom" and isinstance(err, ValueError) and trace[-1][0] == "boom" and trace[-1][2] == set()
    s2, plan2 = pickle.loads(trace[-1][1])  # noqa: S301 - the module's own fixture
    assert s2.M["meta"].get("settlement_form") == s.M["meta"].get("settlement_form"), "the state boom started from: water_frame's"
    s3, failed, _e, trace = rp.roll_through(plan2, [], start=(s2, plan2))
    assert failed is None and s3 is s2 and trace == []


def test_what_the_fresh_map_holds_and_what_a_check_reads() -> None:
    assert rp.held({"lanes": [], "houses": [[1, 2]], "meta": {"a": 1, "b": None}}) == {"houses", "meta.a"}, "an empty part holds nothing"
    after = {"lanes": [[0, 0]], "houses": [], "meta": {"a": 1, "b": 3, "c": 4}}
    seen: set[str] = set()
    M = rp.Reads(after, seen)
    assert M.get("lanes") == [[0, 0]] and M["meta"]["b"] == 3 and M["meta"].get("zz") is None and "houses" in M
    assert rp.owned_reads(seen) == {"lanes", "meta.b", "meta.zz", "houses"}
