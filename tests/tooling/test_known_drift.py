"""A KNOWN DRIFT lands as filed (feature 417, the round arbiter's ruling on ask:417-T29-drifted): a DRIFTED claim whose text names
an open task row that names it is no introduced finding - whether or not the landing changed its code, recorded for the GM
(feature 430 T06, D6) - and a round arbiter's accept keeps it DRIFTED rather than rewriting it IN-STEP."""

from __future__ import annotations

import importlib.util
import json
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


def test_a_drift_left_unfiled_is_not_known(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T32 The lanes as the record has them: `DOORSTEP_FT` 80 against 0246's 60, in `ways/`")
    filed = "a departure the code keeps until feature 417 T32"
    assert carry.known_drifts(_cx(tmp_path, filed, "c0"), tmp_path) == {KEY: "417 T32"}, "feature 430 D6: its code changed, still known"
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
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T33"}, "feature 430 D6: the open row naming it alone, no base core needed"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"80 ft; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T33"}


def test_an_accepted_drift_whose_text_names_no_task_is_known_on_the_accept(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T33 The audit as the record has it")
    cx = _cx(tmp_path, "every privy kept 15 ft from a well", "c1")
    assert carry.known_drifts(cx, tmp_path) == {}, "no task named and no accept: not known"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"the guests' privy unchecked; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "accepted by the round arbiter"}


def test_an_accepted_drift_on_code_the_landing_changed_is_known(tmp_path: pathlib.Path) -> None:
    _tasks(tmp_path, "- [ ] T32 The lanes: `DOORSTEP_FT` 80 against 0246's 60")
    cx = _cx(tmp_path, "a departure the code keeps until feature 417 T32", "c0")
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T32"}, "feature 430 D6: the code changed and no accept - still known on its row"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"80 ft; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T32"}, "the arbiter's accept stands whatever the base holds"


def test_an_accept_keeps_a_label_s_own_semicolon_whole() -> None:
    acc = _load("claims_accept")
    known = {"a.md::S#well (\"x\"; y)": 1, "a.md::S#b": 1}
    assert acc.split_semicolon_keys('a.md::S#well ("x"; y);a.md::S#b', known) == ['a.md::S#well ("x"; y)', "a.md::S#b"]
    assert acc.split_semicolon_keys("a.md::S#b;nope", known) == ["a.md::S#b", "nope"], "an unknown piece is named alone"


def test_the_task_a_claim_names_last_is_its_row_and_an_accept_stands_where_that_row_misses_it(tmp_path: pathlib.Path) -> None:
    """ask:417-T50-claims: "the track lays no spur (feature 417 T50) ... a departure the code keeps until feature 417 T32" - the
    row is T32's, the task named last; and where no row names the unit, the arbiter's recorded accept still makes it known."""
    _tasks(tmp_path, "- [ ] T32 The lanes: `DOORSTEP_FT` 80 against 0246's 60\n- [ ] T50 The track lays no field spur")
    cx = _cx(tmp_path, "the track lays no spur (feature 417 T50), a departure the code keeps until feature 417 T32", "c1")
    assert carry.known_drifts(cx, tmp_path) == {KEY: "417 T32"}, "the row named last, which names the unit"
    cx = _cx(tmp_path, "a departure (feature 417 T32) said elsewhere, until feature 417 T50", "c1")
    assert carry.known_drifts(cx, tmp_path) == {}, "the row named last misses the unit and nothing accepted it"
    cx.load_index = lambda _p: {KEY: {"verdict": "DRIFTED", "core": "c1", "note": f"no spur; {carry.ACCEPTED} (ask:x) to land as filed"}}
    assert carry.known_drifts(cx, tmp_path) == {KEY: "accepted by the round arbiter"}, "the accept stands"


LINE = f"{'DRIFTED':<14} {KEY} - 60 ft at a house, until feature 417 T32"


def _gate_with_one_known(tmp: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    _tasks(tmp, "- [ ] T32 The lanes as the record has them: `DOORSTEP_FT` 80 against 0246's 60, in `ways/`")
    monkeypatch.setattr(carry, "classified", lambda cx, root: ([], [LINE], [], []))
    monkeypatch.setattr(carry, "known_drifts", lambda cx, root: {KEY: "417 T32"})
    monkeypatch.setattr(carry, "filed", lambda root: {})
    monkeypatch.setattr(carry, "active_feature", lambda root: None)


def test_a_known_drift_unrecorded_refuses_with_the_command_and_recorded_it_warns(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 430 T06 (D6; proposal 6, approved by the GM 2026-10-26): a known departure lands with no arbiter round, recorded and
    listed for the GM - `make claims-known` writes the row into its task's feature's gm-review.jsonl, and `make gm-review` lists it."""
    _gate_with_one_known(tmp_path, monkeypatch)
    refuse, warn = carry.gate(None, tmp_path)
    assert refuse == [f"known: {LINE} - a known drift (417 T32) to record for the GM: `make claims-known` (make land runs it)"], refuse
    written = carry.record_known(None, tmp_path, now="2026-10-26T00:00:00Z")
    assert written == [f"417-all-seeds-pass T32: {KEY}"]
    rows = (tmp_path / "specs" / "417-all-seeds-pass" / "gm-review.jsonl").read_text(encoding="utf-8")
    assert '"kind": "known-drift"' in rows and KEY in rows
    assert "GM review (make gm-reviewed F=417)" in (tmp_path / "specs" / "417-all-seeds-pass" / "tasks.md").read_text(encoding="utf-8")
    refuse, warn = carry.gate(None, tmp_path)
    assert refuse == [] and any("known drift (417 T32)" in w for w in warn), (refuse, warn)


def test_a_triage_of_three_or_fewer_claims_goes_straight_to_impl_drift(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 430 T06 (D6; proposal 6, approved by the GM 2026-10-26: "skip claims-triage for bundles of a few claims"): a
    triage of `TRIAGE_SKIP_MAX` claims or fewer writes the impl-drift bundle of the same claims and puts the skip on the ledger;
    one more is triaged as before."""
    cl = _load("claims")
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "review-ledger.md").write_text("| date | check |\n", encoding="utf-8")
    monkeypatch.setattr(cl, "current", lambda root: {})
    monkeypatch.setattr(cl, "load_index", lambda p: {})
    monkeypatch.setattr(cl, "load_store", lambda p: {})
    monkeypatch.setattr(cl, "_git", lambda root, *a: str(tmp_path))
    keys = [f"l7r/x.py::f{i}#c" for i in range(cl.TRIAGE_SKIP_MAX + 1)]
    owed = {"n": cl.TRIAGE_SKIP_MAX}
    monkeypatch.setattr(cl, "owed", lambda cur, index, qdir, store: [(k, next(iter(cl.TRIAGED))) for k in keys[: owed["n"]]])
    bundled: list[list[str]] = []
    real_main = cl.main
    monkeypatch.setattr(cl, "main", lambda argv: bundled.append(argv) or 0 if "bundle" in argv else real_main(argv))
    monkeypatch.setattr(cl, "triage_bundle", lambda *a: "TRIAGE BUNDLE")
    monkeypatch.setattr(cl.claims_flight, "mark", lambda root, out: None)
    assert real_main(["--root", str(tmp_path), "triage"]) == 0
    assert bundled and "--units" in bundled[0] and ",".join(keys[:3]) in bundled[0], bundled
    skip = json.loads((tmp_path / cl.SKIPS).read_text(encoding="utf-8").splitlines()[-1])
    assert skip["claims"] == 3 and skip["keys"] == keys[:3], "the skip recorded in its own file"
    assert (tmp_path / "dev" / "review-ledger.md").read_text(encoding="utf-8") == "| date | check |\n", "never a ledger row (the ledger guard refuses one)"
    bundled.clear()
    owed["n"] = cl.TRIAGE_SKIP_MAX + 1
    assert real_main(["--root", str(tmp_path), "triage"]) == 0 and bundled == [], "four claims: triaged as before"
