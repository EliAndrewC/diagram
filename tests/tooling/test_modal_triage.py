"""`scripts/record/modal_triage.py` - a page's edit owes a pop-up's checks only where it bears on that pop-up (feature 375, FR-001).

Feature 372 measured about twelve `modal-depiction` runs that came back clean, owed only because a drawing page each named had
changed somewhere it never read. Before this feature every kind naming a moved page was owed in full; now it owes a triage of
the page's changed blocks first, and a reply that does not name it answers it.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_modal_checks import FARMHOUSE, _commit, _load, _tree

mo = _load("_modal_owed")
mb = _load("_modal_bundle")
mt = _load("modal_triage")
ro = _load("record_owed")

DRAWN = FARMHOUSE.replace("    Name: farmhouse", "    Depiction: The map draws every house alike.\n\n    Name: farmhouse").replace(
    "    Entry: research/questions/0029-farmhouses-minka.html",
    "    Entry: research/questions/0029-farmhouses-minka.html\n    Drawing: research/questions/0029-farmhouses-minka.drawing.html",
)
PAGE = '<h2 id="how-our-maps-draw-farmhouses">How our maps draw farmhouses</h2>\n<p>The roof shape is a knob.</p>\n<p>Wells stand by the door.</p>\n'
DEP = "modal-depiction:hamlet/farmhouse"


@pytest.fixture
def drawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    root = _tree(tmp_path, DRAWN)
    (root / "research/questions/0029-farmhouses-minka.drawing.html").write_text(PAGE, encoding="utf-8")
    _commit(root)
    monkeypatch.setenv("RECORD_CHECKS_DIR", str(tmp_path / "store"))
    return root


def _edit(root: pathlib.Path, old: str, new: str) -> None:
    f = root / "research/questions/0029-farmhouses-minka.drawing.html"
    f.write_text(f.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def test_a_moved_drawing_page_owes_a_triage_not_the_check(drawn: pathlib.Path) -> None:
    """The old behavior: a moved page owed every kind naming it its full check. Now it owes a triage, which `modal-bundle`
    honors, and the triage's bundle shows only the changed block."""
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    base = ro.merge_base(drawn)
    ((slug, why, fp),) = mo.owed(drawn, base)
    assert slug == DEP and mt.triage_only(why)
    assert [s for s, _w, _f in mt.pending(drawn, base, ro.store(drawn))] == [DEP]
    m = mo.find(drawn, "Farmhouse")
    assert "owe(s) only a TRIAGE" in mt.refusal(drawn, m, "modal-depiction") and mt.refusal(drawn, m, "modal-form") == ""
    manifest, n = mt.bundle(drawn, drawn.parent / "t")
    text = manifest.read_text(encoding="utf-8")
    assert n == 1 and "> Wells stand by the kitchen." in text and "Removed blocks (no longer on the page):\n\n> Wells stand by the door." in text
    assert "roof shape" not in text and "- UID `hamlet/farmhouse` (modal-depiction): About - A farmhouse" in text
    assert "Depiction - The map draws every house alike." in text
    assert "make modal-triage" in ro.command(ro.ru.Unit(slug, why, fp))


def test_a_reply_that_does_not_name_a_pop_up_answers_it_and_one_that_does_sends_it_on(drawn: pathlib.Path) -> None:
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    store, base = ro.store(drawn), ro.merge_base(drawn)
    manifest, _n = mt.bundle(drawn, drawn.parent / "t")
    units = json.loads((manifest.parent / "triage.json").read_text())["units"]
    assert mt.record(store, units, "No pop-up is touched; nothing TOUCHES hamlet/farmhouse - here.\n") == []
    assert ro.answered(store, DEP, units[DEP]) and ro._read(store, DEP)["result"] == "triage: untouched"
    assert mt.pending(drawn, base, store) == [] and mt.bundle(drawn, drawn.parent / "t2") == (None, 0)
    _edit(drawn, "the kitchen", "the back door")
    manifest, _n = mt.bundle(drawn, drawn.parent / "t3")
    units = json.loads((manifest.parent / "triage.json").read_text())["units"]
    msgs = mt.record(store, units, "TOUCHES hamlet/farmhouse - the well's seat\nTOUCHES hamlet/nothing - stray\n")
    assert msgs == ["refused: `hamlet/nothing` is not a pop-up of this triage", f"touched: {DEP} - the well's seat"]
    assert mt.pending(drawn, base, store) == [], "named: owed the full check, not another triage"
    assert mt.refusal(drawn, mo.find(drawn, "Farmhouse"), "modal-depiction") == ""


def test_the_triage_diffs_against_what_the_last_check_read(drawn: pathlib.Path) -> None:
    """A unit answered from a bundle keeps the pages that bundle read; the next triage shows only what changed since then."""
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    out = drawn.parent / "dep"
    assert mb.bundle(drawn, "Farmhouse", "modal-depiction", str(out), reason="checked in full") == 0
    assert ro.answer(drawn, "modal-depiction", "COVERAGE 0", str(out)) == [DEP]
    assert "research/questions/0029-farmhouses-minka.drawing.html" in ro._read(ro.store(drawn), DEP)["pages"]
    _edit(drawn, "The roof shape is a knob.", "The roof shape is rolled.")
    manifest, _n = mt.bundle(drawn, drawn.parent / "t")
    text = manifest.read_text(encoding="utf-8")
    assert "> The roof shape is rolled." in text and "kitchen" not in text, "the well's change was read by the last check"


def test_the_command_line(drawn: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert mt.main(["--root", str(drawn), "bundle", "--out", str(drawn.parent / "t")]) == 0
    assert "no pop-up is owed a triage" in capsys.readouterr().out
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    assert mt.main(["--root", str(drawn), "bundle", "--out", str(drawn.parent / "t")]) == 0
    assert "1 unit(s); dispatch one ad-hoc agent" in capsys.readouterr().out
    (drawn.parent / "r.txt").write_text("TOUCHES `hamlet/farmhouse` - the well\n")
    assert mt.main(["--root", str(drawn), "record", "--bundle", str(drawn.parent / "t"), "--reply", str(drawn.parent / "r.txt")]) == 0
    assert "1 of 1 unit(s) sent on to their checks" in capsys.readouterr().out
    assert mt.keep(drawn, "research/questions/no-such.html") == ""
