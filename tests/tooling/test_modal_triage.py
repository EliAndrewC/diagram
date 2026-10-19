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

REPO = pathlib.Path(__file__).resolve().parents[2]

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
    assert "1 unit(s); dispatch the `modal-triage` agent" in capsys.readouterr().out
    (drawn.parent / "r.txt").write_text("TOUCHES `hamlet/farmhouse` - the well\n")
    assert mt.main(["--root", str(drawn), "record", "--bundle", str(drawn.parent / "t"), "--reply", str(drawn.parent / "r.txt")]) == 0
    assert "1 of 1 unit(s) sent on to their checks" in capsys.readouterr().out
    assert mt.keep(drawn, "research/questions/no-such.html") == ""


def test_a_transcript_reply_is_read_for_its_last_reply(drawn: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    # read raw, a transcript's TOUCHES lines sit inside JSON strings and every pop-up was answered untouched (385 T07)
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    assert mt.main(["--root", str(drawn), "bundle", "--out", str(drawn.parent / "t")]) == 0
    capsys.readouterr()
    said = {"type": "assistant", "message": {"content": [{"type": "text", "text": "TOUCHES `hamlet/farmhouse` - the well"}]}}
    (drawn.parent / "r.jsonl").write_text(json.dumps(said) + "\n")
    assert mt.main(["--root", str(drawn), "record", "--bundle", str(drawn.parent / "t"), "--reply", str(drawn.parent / "r.jsonl")]) == 0
    assert "1 of 1 unit(s) sent on to their checks" in capsys.readouterr().out


FIX = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "modal-triage-343"
Q99 = "research/questions/0099-the-hearing-court-shirasu.html"
Q104 = "research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html"
D104 = "research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html"


def test_343s_triage_owes_a_check_only_for_the_pages_it_reads(tmp_path: pathlib.Path) -> None:
    """Feature 375 amendment 1, SC-007: the kept triage of feature 343 (61 units). The old reply named pop-ups, and every check of
    a named pop-up was owed - 11 units for pages their checks never read. Restated with the page each block stands on, a
    question page owes the research checks and the drawing page owes depiction; the old page-less reply still owes them all."""
    units = json.loads((FIX / "triage.json").read_text())["units"]
    pages = {s: [D104] if s.startswith("modal-depiction") else [Q99, Q104] for s in units}
    old = mt.record(tmp_path / "old", units, (FIX / "reply.md").read_text(), pages)
    new = mt.record(tmp_path / "new", units, (FIX / "reply-paged.md").read_text(), pages)
    owed_old = {m.split(" ")[1] for m in old if m.startswith("touched")}
    owed_new = {m.split(" ")[1] for m in new if m.startswith("touched")}
    cleared = owed_old - owed_new
    assert cleared == {"modal-depiction:sheet/main-gate", "modal-depiction:sheet/residence"} | {
        f"{c}:sheet/{u}" for c in ("modal-accuracy", "modal-references", "modal-gaps") for u in ("door", "guest-quarters", "side-gate")
    }, "the 11 units of 61 owed only for a page their check never reads"
    assert len(cleared) == 11 and owed_new < owed_old
    for kept in ("modal-depiction:sheet/nakamon", "modal-depiction:sheet/garden", "modal-depiction:sheet/genkan", "modal-depiction:sheet/door"):
        assert kept in owed_new, f"{kept}: its block stands on the drawing page - still owed"
    assert ro.answered(tmp_path / "new", "modal-depiction:sheet/main-gate", units["modal-depiction:sheet/main-gate"])
    # a line naming no page owes every check of its pop-up (failing toward checking); a unit with no recorded pages too
    assert {m.split(" ")[1] for m in mt.record(tmp_path / "bare", units, "TOUCHES sheet/door - something\n", pages) if m.startswith("touched")} == {s for s in units if s.endswith(":sheet/door")}
    assert mt.record(tmp_path / "nopages", {"modal-depiction:sheet/door": "f"}, f"TOUCHES sheet/door @ {Q104.split('/')[-1]} - x\n", {}) == ["touched: modal-depiction:sheet/door - x"]


def _kind(root: pathlib.Path, old: str, new: str) -> None:
    f = next((root / "l7r").rglob("*.py"), None)
    for p in (root / "l7r").rglob("*.py"):
        if old in p.read_text(encoding="utf-8"):
            f = p
    assert f is not None
    f.write_text(f.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def test_depiction_is_owed_by_the_words_it_reads(drawn: pathlib.Path) -> None:
    """Feature 375 amendment 1, SC-007 (FR-015), as amendment 6 (FR-028, SC-021) amends it: a Guesses edit alone owes
    `modal-form` and the research checks, not depiction; so does an About edit alone (a drawing statement in About is
    `modal-form`'s M13 finding); a Depiction or Entry: edit still owes it."""
    base = ro.merge_base(drawn)
    _kind(drawn, "no small house was measured.", "no small house was ever measured.")
    owed = {s.split(":")[0] for s, _w, _f in mo.owed(drawn, base)}
    assert "modal-form" in owed and "modal-accuracy" in owed and "modal-depiction" not in owed
    _kind(drawn, "It was thatched.", "It was thatched with rice straw.")
    owed = {s.split(":")[0] for s, _w, _f in mo.owed(drawn, base)}
    assert "modal-form" in owed and "modal-depiction" not in owed, "an About edit alone owes modal-form, not depiction (FR-028)"
    _kind(drawn, "The map draws every house alike.", "The map draws every house alike, thatched.")
    assert [w for s, w, _f in mo.owed(drawn, base) if s == DEP] == ["its Depiction, Drawing: or Entry: changed"]


def test_depiction_owed_by_is_the_one_rule() -> None:
    """FR-028: the predicate `owed()` and the replay (`scripts/measure/depiction_replay.py`) share."""

    def modal(**tags: str) -> object:
        return mo.Modal("K", "k", "l7r/diagram/interactive/assets/modals/hamlet/k.md:1", {"About": "a", "Entry": "e", "Depiction": "d", **tags})

    was = modal()
    assert mo.depiction_owed_by(None, was), "new to the About form"
    assert not mo.depiction_owed_by(was, modal(About="b")) and not mo.depiction_owed_by(was, modal(Guesses="g"))
    assert all(mo.depiction_owed_by(was, modal(**{t: "x"})) for t in ("Entry", "Depiction", "Drawing"))


def test_the_bundle_records_the_pages_each_unit_reads(drawn: pathlib.Path) -> None:
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    manifest, _n = mt.bundle(drawn, drawn.parent / "t")
    data = json.loads((manifest.parent / "triage.json").read_text())
    assert data["pages"] == {DEP: ["research/questions/0029-farmhouses-minka.drawing.html"]}
    # the reply form is the agent's contract, its system prompt (feature 383 amendment 6, plan D36); the MANIFEST names it
    assert "For the `modal-triage` agent" in manifest.read_text(encoding="utf-8")
    assert len(manifest.read_text(encoding="utf-8").split("\n## ", 1)[0]) < 400, "what every triage bundle repeats is one line"
    assert "TOUCHES <uid> @ <page file name>" in (REPO / ".claude" / "agents" / "modal-triage.md").read_text(encoding="utf-8")


def test_a_page_the_bundle_never_showed_owes_everything(tmp_path: pathlib.Path) -> None:
    """The plan review of amendment 1: a misnamed or bare page must fail toward checking, never clear the pop-up."""
    units = {"modal-depiction:sheet/door": "f1", "modal-accuracy:sheet/door": "f2"}
    pages = {"modal-depiction:sheet/door": [D104], "modal-accuracy:sheet/door": [Q104]}
    msgs = mt.record(tmp_path, units, "TOUCHES sheet/door @ 0104 - the river door\n", pages)
    assert sorted(m.split(" ")[1] for m in msgs) == sorted(units)
    msgs = mt.record(tmp_path / "b", units, f"TOUCHES sheet/door @ {D104.split('/')[-1]} - the river door\n", pages)
    assert [m.split(" ")[1] for m in msgs] == ["modal-depiction:sheet/door"]


def test_an_about_or_guesses_edit_after_the_check_answered_does_not_reowe_depiction(drawn: pathlib.Path) -> None:
    """The plan review of amendment 1, and amendment 6 (FR-028, SC-021): from a pop-up whose Depiction already differs from the
    base and whose depiction was answered, a later Guesses or About edit keeps it answered - so no depiction dispatch is owed,
    and none adds a round to its count - while an Entry: edit re-owes it."""
    base = ro.merge_base(drawn)
    store = ro.store(drawn)
    _kind(drawn, "The map draws every house alike.", "The map draws every house alike, thatched.")
    (slug, _w, fp) = next(u for u in mo.owed(drawn, base) if u[0].startswith("modal-depiction"))
    ro.write_answer(store, slug, fp, "PASS")
    _kind(drawn, "no small house was measured.", "no small house was ever measured.")
    _kind(drawn, "It was thatched.", "It was thatched with rice straw.")
    (_s, _w, fp2) = next(u for u in mo.owed(drawn, base) if u[0].startswith("modal-depiction"))
    assert fp2 == fp and ro.answered(store, slug, fp2), "a Guesses or About edit leaves what depiction judges unchanged"
    assert DEP not in {u.slug for u in ro.unanswered(drawn)}, "nothing owed, so the bundle hook lets no depiction round through"
    _kind(drawn, "0029-farmhouses-minka.html\n", "0029-farmhouses-minka.html, research/questions/0030-x.html\n")
    (_s, _w, fp3) = next(u for u in mo.owed(drawn, base) if u[0].startswith("modal-depiction"))
    assert fp3 != fp and not ro.answered(store, slug, fp3), "an Entry: edit re-owes it"
    assert DEP in {u.slug for u in ro.unanswered(drawn)}


def test_modal_form_holds_m13s_about_side_and_depiction_reports_nothing_from_about() -> None:
    """FR-028, SC-021: M13 rides in every `modal-form` bundle (its guidelines) and its contract; `modal-depiction`'s says it
    reports nothing from About. (Passes on today's code: modal-form's M13 line landed 2026-10-12.)"""
    root = pathlib.Path(__file__).resolve().parents[2]
    assert "**M13." in (root / mb.GUIDELINES["standard"]).read_text(encoding="utf-8")
    form = (root / ".claude/agents/modal-form.md").read_text(encoding="utf-8")
    assert "does NOT belong in About: it goes on the Depiction tab" in " ".join(form.split())
    depiction = " ".join((root / ".claude/agents/modal-depiction.md").read_text(encoding="utf-8").split())
    assert "report nothing from About" in depiction and "sits in About instead belongs here" not in depiction


def test_a_triage_answer_keeps_a_baseline_and_the_next_change_shows_alone(drawn: pathlib.Path) -> None:
    """Feature 385 T02 (plan D11): the triage's own "untouched" answer keeps the page it showed, so the next triage diffs
    against that - T01's one-word fix re-showed both of its new bullets to every pop-up, because the untouched answers had
    erased the blobs and every unit fell back to the merge base."""
    store = ro.store(drawn)
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    manifest, _n = mt.bundle(drawn, drawn.parent / "t")
    data = json.loads((manifest.parent / "triage.json").read_text())
    assert "(against the merge base (no check has read it yet))" in manifest.read_text(encoding="utf-8")
    assert mt.record(store, data["units"], "nothing touched\n", data["pages"], data["blobs"]) == []
    assert "research/questions/0029-farmhouses-minka.drawing.html" in ro._read(store, DEP)["pages"], "the shown page kept"
    _edit(drawn, "the kitchen", "the hearth")
    manifest, _n = mt.bundle(drawn, drawn.parent / "t2")
    text = manifest.read_text(encoding="utf-8")
    assert "> Wells stand by the hearth." in text and "Wells stand by the kitchen." in text.split("Removed blocks")[1]
    assert "Wells stand by the door." not in text, "the change already triaged is not shown again"
    assert "(against the version these pop-ups' last check read)" in text


def test_the_default_listing_marks_what_is_already_answered() -> None:
    """Feature 385 T02 (plan D12): the full listing read as owed after one quote-check batch had answered its unit; each answered
    unit is now marked, and the header says how many are still unanswered."""
    a, b = ro.ru.Unit("quote-check:0081.drawing#unfootnoted", "a block changed", "f1"), ro.ru.Unit("record-format:0081", "words", "f2")
    text = ro.report([a, b], None, {a.slug})
    assert text.startswith("record-owed: 2 unit(s) owed by the delta, 1 still unanswered")
    assert f"  [answered] {a.slug}" in text and f"  {b.slug}  - words" in text
    assert "still unanswered" not in ro.report([a, b], None), "the --unanswered form as before"


def test_several_pop_ups_of_one_check_are_bundled_for_one_agent(drawn: pathlib.Path) -> None:
    """Feature 385 T02 (plan D12): T01 sent one agent per pop-up to read one changed page; several KIND=s for one check now
    write one top MANIFEST over each pop-up's own bundle, carrying their unit lines, each answered from its own bundle."""
    _edit(drawn, "Wells stand by the door.", "Wells stand by the kitchen.")
    out = drawn.parent / "batch"
    assert mb.bundles(drawn, ["Farmhouse", "Farmhouse"], "modal-depiction", str(out), reason="checked in full") == 0
    top = (out / "MANIFEST.md").read_text(encoding="utf-8")
    assert "owed-checks: modal-depiction" in top and top.count("MANIFEST.md`") == 2 and f"unit: {DEP} " in top
    subs = sorted(p for p in out.iterdir() if p.is_dir())
    assert len(subs) == 2 and all((s / "MANIFEST.md").is_file() for s in subs)
    assert ro.answer(drawn, "modal-depiction", "COVERAGE 0", str(subs[0])) == [DEP], "answered from its own bundle"


def test_a_depiction_edit_states_an_absence_in_the_pages_own_words() -> None:
    """Feature 385 T03, the round arbiter's tooling fix on ask:t03-popups-round3: a checker's own fix paraphrased a page's
    absence into a stronger claim and cost a second round on four pop-ups."""
    root = pathlib.Path(__file__).resolve().parents[2]
    depiction = " ".join((root / ".claude/agents/modal-depiction.md").read_text(encoding="utf-8").split())
    assert "quotes the cited page's own absence wording verbatim" in depiction and "never a paraphrase of it" in depiction


def test_the_default_bundle_is_the_clones_own() -> None:
    """The round arbiter on hour:397@3: two clones shared `/tmp/l7r-check/modal-triage`, and one overwrote the other's bundle."""
    assert mt.default_out(pathlib.Path("/diagram/.clones/money")) != mt.default_out(pathlib.Path("/diagram/.clones/backlog"))
    assert mt.default_out(pathlib.Path("/diagram/.clones/money")).name == "modal-triage-money"
