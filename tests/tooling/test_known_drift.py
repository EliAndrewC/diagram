"""A KNOWN DRIFT lands as filed (feature 417, the round arbiter's ruling on ask:417-T29-drifted): a DRIFTED claim whose code the
landing left as the base had it, and whose text names an open task row that names it, is no introduced finding - and a round
arbiter's accept keeps it DRIFTED rather than rewriting it IN-STEP."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import SimpleNamespace

from tests._scripts import script


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


carry = _load("claims_carry")

KEY = "l7r/diagram/hamletgen/ways/law.py::DOORSTEP_FT#a dooryard's reach"
OTHER = "l7r/diagram/hamletgen/ways/law.py::FRAGMENT_FT#shortest way"


def _cx(tmp: pathlib.Path, account: str, base_core: str, verdict: str = "DRIFTED") -> SimpleNamespace:
    claim = SimpleNamespace(account=account)
    return SimpleNamespace(
        INDEX="dev/claims-index.json",
        current=lambda _root: {KEY: SimpleNamespace(claim=claim), OTHER: SimpleNamespace(claim=SimpleNamespace(account="feature 417 T32"))},
        load_index=lambda _p: {KEY: {"verdict": verdict, "core": "c1"}, OTHER: {"verdict": "IN-STEP", "core": "c2"}},
        _git=lambda _root, *a: "abc123\n",
        base_tree=lambda _root, _mb, into: into,
        base_cores=lambda _skill, keep=None: {KEY.rsplit("#", 1)[0]: base_core},
    )


def _tasks(tmp: pathlib.Path, row: str) -> None:
    d = tmp / "specs" / "417-all-seeds-pass"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(f"# Tasks\n\n{row}\n      research: rendering\n", encoding="utf-8")


def test_a_drifted_claim_filed_in_an_open_row_naming_it_with_its_code_unchanged_is_known(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T32 The lanes as the record has them: `DOORSTEP_FT` 80 against 0246's 60, in `ways/`")
    cx = _cx(tmp_path, "60 ft at a house - the settle allows 80, a departure the code keeps until feature 417 T32", "c1")
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T32"}


def test_a_drift_the_landing_made_or_left_unfiled_is_not_known(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T32 The lanes as the record has them: `DOORSTEP_FT` 80 against 0246's 60, in `ways/`")
    filed = "a departure the code keeps until feature 417 T32"
    assert carry.known_drifts(_cx(tmp_path, filed, "c0"), tmp_path) == {}, "the code changed in the landing: the drift is the landing's"
    assert carry.known_drifts(_cx(tmp_path, "a departure, unfiled", "c1"), tmp_path) == {}, "no task named in the claim"
    assert carry.known_drifts(_cx(tmp_path, filed, "c1", verdict="MISLABELED"), tmp_path) == {}, "only a DRIFTED verdict"


def test_a_row_that_does_not_name_the_unit_or_is_ticked_files_nothing(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [x] T32 The lanes: `DOORSTEP_FT` 80 against 0246's 60")
    cx = _cx(tmp_path, "a departure the code keeps until feature 417 T32", "c1")
    assert carry.known_drifts(cx, tmp_path) == {}, "a ticked row is no open fixing task"


def test_a_classified_line_gives_back_its_key() -> None:
    assert carry._key_of(f"{'DRIFTED':<14} {KEY} - the note") == KEY


def test_an_arbiter_accept_keeps_a_drifted_claim_drifted_and_stands_as_in_step_otherwise() -> None:
    acc = _load("claims_accept")
    kept = acc.accept_line(KEY, {"verdict": "DRIFTED", "note": "80 ft against 0246's 60"}, "ask:x")
    assert kept.startswith(f"VERDICT {KEY} DRIFTED - 80 ft against 0246's 60; a known drift accepted")
    assert acc.accept_line(KEY, {"verdict": "MISLABELED"}, "ask:x").startswith(f"VERDICT {KEY} IN-STEP - accepted by the round arbiter")


def test_a_unit_the_base_tree_cannot_see_is_known_only_on_the_arbiter_s_recorded_accept(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T33 The audit as the record has it: `DOORSTEP_FT` 80 against 0246's 60")
    cx = _cx(tmp_path, "a departure the code keeps until feature 417 T33", "c1")
    cx.base_cores = lambda _skill, keep=None: {}
    assert carry.known_drifts(cx, tmp_path) == {}, "no base core and no accept: not known"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"80 ft; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T33"}


def test_an_accepted_drift_whose_text_names_no_task_is_known_on_the_accept(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T33 The audit as the record has it")
    cx = _cx(tmp_path, "every privy kept 15 ft from a well", "c1")
    assert carry.known_drifts(cx, tmp_path) == {}, "no task named and no accept: not known"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"the guests' privy unchecked; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "accepted by the round arbiter"}


def test_an_accept_keeps_a_label_s_own_semicolon_whole() -> None:
    acc = _load("claims_accept")
    known = {"a.md::S#well (\"x\"; y)": 1, "a.md::S#b": 1}
    assert acc.split_semicolon_keys('a.md::S#well ("x"; y);a.md::S#b', known) == ['a.md::S#well ("x"; y)', "a.md::S#b"]
    assert acc.split_semicolon_keys("a.md::S#b;nope", known) == ["a.md::S#b", "nope"], "an unknown piece is named alone"
