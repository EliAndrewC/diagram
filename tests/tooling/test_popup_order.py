"""Feature 375 amendment 3, FR-019 (SC-011): a pop-up's checks run in order - form, research, depiction - and a round's applied
edits settle the checks before it.

WHAT THESE PROVE. A `modal-research` bundle waits for an owed, unanswered `modal-form`, and a `modal-depiction` bundle for
either; the refusal names the bundle of the check owed first; `CHECK_ORDER_OK` builds it anyway and the MANIFEST says why; a
pop-up owed only its depiction (a drawing page moved) is not held. A research round's EDIT blocks, applied, leave an answered
`modal-form` answered, a depiction round's leave both answered; a hand edit re-owes them; a form round's blocks applied after
research answered leave research owed. Each test fails on the code before the amendment (no hold, no settling across).
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod
    spec.loader.exec_module(mod)
    return mod


mo = _load("_modal_owed")
mb = _load("_modal_bundle")
ro = _load("_record_owed")
ae = _load("_apply_edits")

CLASSES = pathlib.Path(mo.MODAL_DIRS[0])
MODAL = """About: A farmhouse was the dwelling of one farming household.

It was thatched.

Guesses:
- its size on the map: no small house was measured.

Depiction: Drawn as a thatched block.

Drawing: research/questions/0029-farmhouses-minka.drawing.html

Name: farmhouse
Covers: houses
Sources: not recorded
Entry: research/questions/0029-farmhouses-minka.html
"""
Q0029 = '<h2 id="farmhouses-minka">Farmhouses (minka)</h2>\n<!-- tags: subject=homesteads; level=foundational -->\n<p>A farmhouse was the dwelling of one household.</p>\n'
D0029 = '<h2 id="farmhouses-minka-drawing">How our maps draw farmhouses</h2>\n<p>A block with a thatch hatch.</p>\n'


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def _tree(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """A clone whose farmhouse pop-up is new to the About form since main: it owes all three checks."""
    root = tmp / "repo"
    (root / CLASSES).mkdir(parents=True)
    (root / CLASSES / "homestead.py").write_text("class Farmhouse(Kind):\n    key = 'farmhouse'\n", encoding="utf-8")
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    (q / "0029-farmhouses-minka.html").write_text(Q0029, encoding="utf-8")
    (q / "0029-farmhouses-minka.drawing.html").write_text(D0029, encoding="utf-8")
    (q / "0029-farmhouses-minka.notes.html").write_text("<li>notes</li>", encoding="utf-8")
    dev = root / "dev"
    dev.mkdir()
    (dev / "modals.md").write_text("M1. The reader.\n", encoding="utf-8")
    (dev / "modals-particular.md").write_text("P1. Particular.\n", encoding="utf-8")
    (root / "research" / "assets").mkdir(parents=True)
    (root / "research" / "assets" / "glossary-variants.txt").write_text("minka\tfarmhouse\n", encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
    _git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    f = root / mo.modal_file(str(CLASSES / "homestead.py"), "farmhouse")
    f.parent.mkdir(parents=True)
    f.write_text(MODAL, encoding="utf-8")
    return root, f


def _answer(root: pathlib.Path, *checks: str) -> None:
    """Record each named unit check answered at its fingerprint now, as `make record-checked` would."""
    for u in ro.units(root):
        if u.check in checks:
            ro.write_answer(ro.store(root), u.slug, u.fingerprint, "clean")


def _unanswered(root: pathlib.Path) -> set[str]:
    return {u.check for u in ro.unanswered(root)}


def _apply(root: pathlib.Path, modal: pathlib.Path, first_line: str, old: str, new: str) -> None:
    reply = root.parent / "reply.md"
    rel = modal.relative_to(root)
    reply.write_text(f"{first_line}\n\nEDIT {rel}\n<<<\n{old}\n===\n{new}\n>>>\n", encoding="utf-8")
    assert ae.main([str(reply), "--root", str(root)]) == 0


RESEARCH = ("modal-accuracy", "modal-references", "modal-gaps")


def test_the_order_is_form_research_depiction_and_each_settles_only_the_checks_before_it() -> None:
    assert mo.ORDER == ("modal-form", "modal-research", "modal-depiction")
    assert mo.earlier_units(("modal-form",)) == ()
    assert mo.earlier_units(RESEARCH) == ("modal-form",)
    assert mo.earlier_units(("modal-depiction",)) == ("modal-form", *RESEARCH)
    assert mo.earlier_units(("record-format",)) == () and mo.earlier_units(("modal-form", "modal-depiction")) == ()


def test_research_and_depiction_wait_for_the_checks_before_them(tmp_path: pathlib.Path, capsys, monkeypatch) -> None:
    monkeypatch.delenv("CHECK_ORDER_OK", raising=False)
    root, _f = _tree(tmp_path)
    assert {"modal-form", "modal-depiction", *RESEARCH} <= _unanswered(root)
    assert mb.bundle(root, "hamlet/farmhouse", "modal-research", str(tmp_path / "r")) == 3
    err = capsys.readouterr().err
    assert 'make modal-bundle KIND="hamlet/farmhouse" FOR=modal-form' in err and "CHECK_ORDER_OK" in err
    assert mb.bundle(root, "hamlet/farmhouse", "modal-depiction", str(tmp_path / "d")) == 3
    assert "FOR=modal-form" in capsys.readouterr().err, "the check owed FIRST is named"
    assert not (tmp_path / "r").exists() and not (tmp_path / "d").exists(), "nothing is copied before the refusal"
    assert mb.bundle(root, "hamlet/farmhouse", "modal-form", str(tmp_path / "f")) == 0
    _answer(root, "modal-form")
    assert mb.bundle(root, "hamlet/farmhouse", "modal-research", str(tmp_path / "r")) == 0
    assert mb.bundle(root, "hamlet/farmhouse", "modal-depiction", str(tmp_path / "d")) == 3
    assert "FOR=modal-research" in capsys.readouterr().err
    _answer(root, *RESEARCH)
    assert mb.bundle(root, "hamlet/farmhouse", "modal-depiction", str(tmp_path / "d")) == 0
    assert "check-order-escape" not in (tmp_path / "d" / "MANIFEST.md").read_text(encoding="utf-8")


def test_the_escape_builds_it_and_the_manifest_says_why(tmp_path: pathlib.Path, monkeypatch) -> None:
    root, _f = _tree(tmp_path)
    monkeypatch.setenv("CHECK_ORDER_OK", "x")
    assert mb.bundle(root, "hamlet/farmhouse", "modal-research", str(tmp_path / "r")) == 3, "a one-word reason is no reason"
    monkeypatch.setenv("CHECK_ORDER_OK", "a backfill the GM asked for")
    assert mb.bundle(root, "hamlet/farmhouse", "modal-research", str(tmp_path / "r")) == 0
    assert "check-order-escape: a backfill the GM asked for" in (tmp_path / "r" / "MANIFEST.md").read_text(encoding="utf-8")


def test_a_pop_up_owed_only_its_depiction_is_not_held(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("CHECK_ORDER_OK", raising=False)
    root, _f = _tree(tmp_path)
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "the pop-up lands")
    _git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    d = root / "research" / "questions" / "0029-farmhouses-minka.drawing.html"
    d.write_text(D0029.replace("thatch hatch", "thatch hatch and a smoke hole"), encoding="utf-8")
    owed = {u.check for u in ro.units(root) if u.check.startswith("modal-")}
    assert owed == {"modal-depiction"}, owed
    assert mb.bundle(root, "hamlet/farmhouse", "modal-depiction", str(tmp_path / "d"), reason="the triage is not under test") == 0


def test_a_research_rounds_edits_settle_form_and_a_depiction_rounds_settle_both(tmp_path: pathlib.Path) -> None:
    root, f = _tree(tmp_path)
    _answer(root, "modal-form")
    _apply(root, f, "modal-research: Farmhouse - ACCURACY 1 findings", "It was thatched.", "It was thatched with rice straw.")
    assert "rice straw" in f.read_text(encoding="utf-8")
    assert "modal-form" not in _unanswered(root), "the research round's blocks alone moved the formed words"
    _answer(root, *RESEARCH)
    _apply(root, f, "modal-depiction: Farmhouse - COVERAGE 1", "It was thatched with rice straw.", "It was thatched with rice straw, as drawn.")
    left = _unanswered(root)
    assert "modal-form" not in left and not set(RESEARCH) & left, "a depiction round settles both checks before it"
    f.write_text(f.read_text(encoding="utf-8").replace("one farming household", "one farming family"), encoding="utf-8")
    left = _unanswered(root)
    assert "modal-form" in left and set(RESEARCH) <= left, "a hand edit after it owes them again"


def test_a_form_rounds_edits_settle_nothing_after_it(tmp_path: pathlib.Path) -> None:
    root, f = _tree(tmp_path)
    _answer(root, "modal-form", *RESEARCH)
    _apply(root, f, "modal-form: Farmhouse - 1 FIX", "It was thatched.", "Its roof was thatched.")
    left = _unanswered(root)
    assert set(RESEARCH) <= left, "research reads the formed words next"


def test_an_earlier_check_unanswered_before_the_blocks_stays_owed(tmp_path: pathlib.Path, capsys) -> None:
    root, f = _tree(tmp_path)
    _apply(root, f, "modal-research: Farmhouse - ACCURACY 1 findings", "It was thatched.", "It was thatched with rice straw.")
    assert "modal-form" in _unanswered(root), "never pending: a later form answer would answer words form never read"
    assert "modal-form:hamlet/farmhouse: still owed" in capsys.readouterr().out


@pytest.fixture(autouse=True)
def _no_triage_store(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("RECORD_CHECKS_DIR", raising=False)
    monkeypatch.setenv("L7R_CACHE_OFF", "1")


def test_a_bundle_computes_only_its_own_pop_ups_units(tmp_path: pathlib.Path) -> None:
    """FR-020(d): a pop-up's bundle reads its own units, not the whole delta's."""
    root, _f = _tree(tmp_path)
    scoped = ro.units(root, families=("modal",), uid="hamlet/farmhouse")
    assert scoped and all(u.check.startswith("modal-") and u.subject == "hamlet/farmhouse" for u in scoped)
    assert ro.units(root, families=("modal",), uid="hamlet/nothing") == []
    assert {u.slug for u in scoped} == {u.slug for u in ro.units(root) if u.check.startswith("modal-")}
