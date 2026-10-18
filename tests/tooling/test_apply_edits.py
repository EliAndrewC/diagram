"""`scripts/record/apply_edits.py` (feature 250 D15): a check report's EDIT and GLOSSARY blocks, applied in one command.

WHAT THESE PROVE. A block whose old text occurs once in a record file is applied; one that occurs twice or not at
all, or names a file outside the record, is REFUSED and nothing is written; `--skip` and `--dry-run` write nothing
for what they name; a glossary term becomes the next numbered file, and one already on file is skipped; the report
is read from plain text or from the last reply in an agent transcript; a report with no block is a usage error.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_apply_edits", REPO / "scripts/record/apply_edits.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ae = _load()


def _tree(tmp_path: pathlib.Path) -> pathlib.Path:
    q = tmp_path / ae.RECORD / "ways" / "010-q.notes.html"
    q.parent.mkdir(parents=True)
    q.write_text("<li>the gloss said stipend</li>\n<li>twice</li><li>twice</li>\n", encoding="utf-8")
    g = tmp_path / ae.TERMS
    g.mkdir(parents=True)
    (g / "0020-koku.json").write_text(json.dumps({"term": "koku", "def": "d", "variants": ["koku"]}), encoding="utf-8")
    (tmp_path / "outside.txt").write_text("the gloss said stipend", encoding="utf-8")
    return q


def _report(path: str, old: str, new: str) -> str:
    return f"EDIT {path}\n<<<\n{old}\n===\n{new}\n>>>\n"


def test_a_report_is_applied_block_by_block_and_refused_where_it_cannot_be_sure(tmp_path, capsys) -> None:
    q = _tree(tmp_path)
    rel = str(q.relative_to(tmp_path))
    report = tmp_path / "r.md"
    report.write_text(
        "quote-check: 2 notes\n"
        + _report(f"`{rel}`", "the gloss said stipend", "the gloss said assessed yield")
        + _report(rel, "twice", "once")
        + _report("outside.txt", "the gloss said stipend", "x")
        + _report(rel, "not there", "x")
        + "GLOSSARY hitoyado | kuchiireya, keian | A placement broker.\n"
        + "GLOSSARY koku | - | already here\n",
        encoding="utf-8",
    )
    assert ae.main([str(report), "--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "assessed yield" in q.read_text(encoding="utf-8") and q.read_text(encoding="utf-8").count("twice") == 2
    assert "occurs 2 times" in out and "not under" in out and "occurs 0 times" in out and "4 refused" not in out
    assert "6 block(s), 3 refused" in out and "then `make glossary`" in out
    added = json.loads((tmp_path / ae.TERMS / "0030-hitoyado.json").read_text(encoding="utf-8"))
    assert added == {"term": "hitoyado", "def": "A placement broker.", "variants": ["hitoyado", "kuchiireya", "keian"]}
    assert "already a glossary term" in out


def test_a_report_saved_with_its_markup_escaped_is_applied(tmp_path, capsys) -> None:
    """Feature 319: reports saved from task notifications carry `&lt;&lt;&lt;`, and every block read as no block."""
    q = _tree(tmp_path)
    report = tmp_path / "returned.md"
    block = _report(str(q.relative_to(tmp_path)), "the gloss said stipend", "the gloss said A &amp; B")
    report.write_text(block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 0
    assert "the gloss said A &amp; B" in q.read_text(encoding="utf-8"), "unescaped once: a record's own &amp; survives"


def test_skip_and_dry_run_write_nothing(tmp_path, capsys) -> None:
    q = _tree(tmp_path)
    report = tmp_path / "r.md"
    report.write_text(_report(str(q), "the gloss said stipend", "changed") + "GLOSSARY new term | | def\n", encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path), "--dry-run"]) == 0
    assert "stipend" in q.read_text(encoding="utf-8") and not list((tmp_path / ae.TERMS).glob("*new-term*"))
    assert ae.main([str(report), "--root", str(tmp_path), "--skip", "1"]) == 0
    assert "stipend" in q.read_text(encoding="utf-8")
    added = json.loads(next((tmp_path / ae.TERMS).glob("*-new term.json")).read_text(encoding="utf-8"))
    assert added["variants"] == ["new term"]
    out = capsys.readouterr().out
    assert "dry run, nothing written" in out and "skipped (--skip)" in out


def test_the_report_is_the_last_reply_of_a_transcript(tmp_path, capsys) -> None:
    q = _tree(tmp_path)
    lines = [
        "not json",
        json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": _report(str(q), "the gloss said stipend", "OLDER")}]}}),
        json.dumps({"type": "user", "message": {"content": "a tool result"}}),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": _report(str(q), "the gloss said stipend", "LAST")}]}}),
        json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read"}]}}),
    ]
    t = tmp_path / "agent.jsonl"
    t.write_text("\n".join(lines), encoding="utf-8")
    assert ae.main([str(t), "--root", str(tmp_path)]) == 0
    assert "LAST" in q.read_text(encoding="utf-8")
    empty = tmp_path / "none.md"
    empty.write_text("quote-check: 3 notes - 3 VERBATIM", encoding="utf-8")
    assert ae.main([str(empty), "--root", str(tmp_path)]) == 2
    missing = tmp_path / "r2.md"
    missing.write_text(_report(ae.RECORD + "ways/999-none.html", "a", "b"), encoding="utf-8")
    assert ae.main([str(missing), "--root", str(tmp_path)]) == 1
    assert "no file" in capsys.readouterr().out


def test_a_block_indented_under_a_numbered_finding_is_applied_without_its_indent(tmp_path) -> None:
    q = _tree(tmp_path)
    report = tmp_path / "r.md"
    block = _report(str(q), "the gloss said stipend", "the gloss said\nassessed yield")
    report.write_text("1. **stipend**, in the notes.\n" + "".join("   " + ln + "\n" for ln in block.splitlines()) + "   GLOSSARY heimin | | Commoners.\n", encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 0
    assert "the gloss said\nassessed yield</li>" in q.read_text(encoding="utf-8")
    assert list((tmp_path / ae.TERMS).glob("*-heimin.json"))


def test_a_modal_s_class_file_is_writable_too(tmp_path, capsys) -> None:
    """D17: a drifted modal's prose is its class docstring, under interactive/classes/."""
    m = tmp_path / ae.MODALS / "fields.py"
    m.parent.mkdir(parents=True)
    m.write_text('class Bund(Kind):\n    """What: A bund is a low earthen ridge.\n    """\n', encoding="utf-8")
    report = tmp_path / "r.md"
    report.write_text(_report(str(m.relative_to(tmp_path)), "A bund is a low earthen ridge.", "A bund is a low ridge of puddled earth."), encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 0
    assert "puddled earth" in m.read_text(encoding="utf-8")
    other = tmp_path / "l7r/diagram/settlement/x.py"
    other.parent.mkdir(parents=True)
    other.write_text("A bund", encoding="utf-8")
    report.write_text(_report(str(other.relative_to(tmp_path)), "A bund", "B"), encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 1 and "not under" in capsys.readouterr().out


def test_a_sheet_modal_s_compound_kinds_file_is_writable_too(tmp_path) -> None:
    """Feature 265: the building-plan sheets' modal prose (feature 262) is under interactive/compound_kinds/."""
    m = tmp_path / ae.SHEET_MODALS / "office.py"
    m.parent.mkdir(parents=True)
    m.write_text('"""What: The tally office counts the rice."""\n', encoding="utf-8")
    report = tmp_path / "r.md"
    report.write_text(_report(str(m.relative_to(tmp_path)), "counts the rice.", "counts the tax rice."), encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 0
    assert "tax rice" in m.read_text(encoding="utf-8")


def test_a_term_another_clone_is_defining_is_refused_and_the_blocks_after_it_still_apply(tmp_path, capsys, monkeypatch) -> None:
    # the reservation's refusal was a traceback that stopped the run mid-report (271 T3 check-b, `Kinki` held by 267)
    q = _tree(tmp_path)
    real = ae._reserve()

    class Held:
        Refusal = real.Refusal

        @staticmethod
        def reserve(*_a, **_k):  # noqa: ANN205
            raise real.Refusal("'Kinki' is already being defined in /elsewhere")

    monkeypatch.setattr(ae, "_reserve", lambda: Held)
    report = tmp_path / "r.md"
    report.write_text("GLOSSARY Kinki | - | A region.\n" + _report(str(q), "the gloss said stipend", "changed"), encoding="utf-8")
    assert ae.main([str(report), "--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "REFUSED - 'Kinki' is already being defined" in out and "2 block(s), 1 refused" in out
    assert "changed" in q.read_text(encoding="utf-8")


def test_a_form_edit_that_drops_research_fixed_wording_is_refused(tmp_path, capsys) -> None:  # noqa: ANN001
    """343's border-court ruling, 2026-10-11: a modal-form EDIT took out the scope words a research round had fixed."""
    modal = tmp_path / "l7r/diagram/interactive/assets/modals/sheet/border-court.md"
    modal.parent.mkdir(parents=True)
    modal.write_text("About: no page on the formal entrance puts a garden there.\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    research = tmp_path / "research-reply.md"
    research.write_text(_report(str(modal.relative_to(tmp_path)), "nothing known of the formal entrance", "no page on the formal entrance"))
    (tmp_path / ".git" / "checks-open.json").write_text(json.dumps({"dispatches": {"t1": {"check": "modal-research", "subjects": ["modal:sheet/border-court"], "t": 1, "reply": str(research)}}}))
    rel = str(modal.relative_to(tmp_path))
    form = tmp_path / "form.md"
    form.write_text("modal-form: border court - 1 finding (1 FIX)\n" + _report(rel, "no page on the formal entrance puts", "nothing known of the formal entrance puts"))
    assert ae.main([str(form), "--root", str(tmp_path)]) == 1
    assert "drops wording a research round fixed" in capsys.readouterr().out
    other = tmp_path / "other.md"  # the same EDIT from another check is not a form round's
    other.write_text("modal-research: border court - 1\n" + _report(rel, "no page on the formal entrance puts", "nothing known of the formal entrance puts"))
    assert ae.main([str(other), "--root", str(tmp_path), "--dry-run"]) == 0


# --- the round settles (feature 335's round arbiter, 2026-10-11) --------------------------------------------------------
# `round:record-format|q:0104@3` and `ask:f335-garden-modal-depiction`: applying a round's own EDIT blocks re-owed the unit
# it answered, the next round read the check's own words back and found nothing, and the round cap fired on that loop.

PAGE = '<h2 id="rooms">Rooms for a parley</h2>\n<ul>\n<li><strong>At Kyakhta each side built a post.</strong><br>The Russians built theirs at the border.</li>\n</ul>\n'
REPLY = "record-format: 3 of 3 words ruled on - 0 VOCABULARY, 0 SESSION NOTE, 1 HISTORY\n"


def _git(d: pathlib.Path, *a: str) -> str:
    import subprocess

    return subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, text=True).stdout


def _repo(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """A clone whose question 0094 changed since main: it owes record-format, as a page under check does."""
    d = tmp_path / "r"
    page = d / ae.RECORD / "questions" / "0094-rooms.html"
    page.parent.mkdir(parents=True)
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@t")
    _git(d, "config", "user.name", "t")
    page.write_text(PAGE.replace("built a post", "built one post"), encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "update-ref", "refs/remotes/origin/main", "HEAD")
    page.write_text(PAGE, encoding="utf-8")
    return d, page


def _owed(d: pathlib.Path) -> list[str]:
    return [u.slug for u in ae._sibling("record_owed").unanswered(d)]


def _answer_now(d: pathlib.Path, check: str = "record-format") -> str:
    ro = ae._sibling("record_owed")
    fp = ro.fingerprints(d, (check,))[f"{check}:0094"]
    ro.write_answer(ro.store(d), f"{check}:0094", fp, "3 of 3")
    return fp


def _apply(d: pathlib.Path, page: pathlib.Path, old: str, new: str, reply: str = REPLY) -> str:
    r = d.parent / "reply.md"
    r.write_text(reply + _report(str(page.relative_to(d)), old, new), encoding="utf-8")
    assert ae.main([str(r), "--root", str(d)]) == 0
    return r.read_text(encoding="utf-8")


def test_the_rounds_own_edit_applied_verbatim_settles_the_unit_it_answered(tmp_path, capsys) -> None:
    d, page = _repo(tmp_path)
    _answer_now(d)
    assert "record-format:0094" not in _owed(d)
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.")
    assert "theirs.</li>" in page.read_text(encoding="utf-8")
    assert "record-format:0094" not in _owed(d), "the round's own words, applied, owe no fourth round"
    assert "record-format:0094: settled with its answered round" in capsys.readouterr().out
    ro = ae._sibling("record_owed")
    assert ro._read(ro.store(d), "record-format:0094")["result"].endswith("; was: 3 of 3"), "the round's counts are kept"
    page.write_text(page.read_text(encoding="utf-8").replace("each side", "every side"), encoding="utf-8")
    assert "record-format:0094" in _owed(d), "a hand edit after it still owes the round"


def test_a_hand_edit_beside_the_rounds_edits_still_owes_the_unit(tmp_path) -> None:
    d, page = _repo(tmp_path)
    _answer_now(d)
    page.write_text(PAGE.replace("each side", "every side"), encoding="utf-8")
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.")
    assert "record-format:0094" in _owed(d)


def test_an_edit_whose_words_the_prepass_raises_anew_still_owes_record_format(tmp_path, capsys) -> None:
    """The arbiter's second clause: settled only when the prepass finds no word that was not already ruled on."""
    d, page = _repo(tmp_path)
    _answer_now(d)
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built a palisade at the border.")
    assert "record-format:0094" in _owed(d)
    assert "its prepass now raises" in capsys.readouterr().out and "palisade" in page.read_text(encoding="utf-8")


def test_edits_applied_before_the_round_is_recorded_settle_when_it_is(tmp_path) -> None:
    """A frozen page takes its round's EDITs BEFORE `make record-checked` (record-edit-hooks.sh): the bundle's answer, at the
    content the check read, settles the words applied after it."""
    d, page = _repo(tmp_path)
    ro = ae._sibling("record_owed")
    read = ro.fingerprints(d, ("record-format",))["record-format:0094"]
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "MANIFEST.md").write_text(f"## Owed\n\nunit: record-format:0094 {read}\n", encoding="utf-8")
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.")
    assert "record-format:0094" in _owed(d), "not answered until the round is recorded"
    assert ro.answer(d, "record-format", "3 of 3", bundle=str(bundle)) == ["record-format:0094"]
    assert "record-format:0094" not in _owed(d)


def test_another_checks_reply_settles_only_its_own_units(tmp_path) -> None:
    d, page = _repo(tmp_path)
    _answer_now(d)
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.", reply="quote-check: 1 note - 1 VERBATIM\n")
    assert "record-format:0094" in _owed(d), "a quote-check round's edits never answer record-format"


def test_a_reply_with_no_counts_line_says_its_units_stay_owed_and_how_to_settle_them(tmp_path, capsys) -> None:
    """Feature 385 T10: three form replies saved with their EDIT blocks alone applied cleanly and settled nothing, silently."""
    d, page = _repo(tmp_path)
    _answer_now(d)
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.", reply="")
    assert "record-format:0094" in _owed(d)
    out = capsys.readouterr().out
    assert "the reply names no check, so the units it answered stay owed" in out
    assert "put the agent's counts line" in out and "at the top of the reply file and run this again" in out
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.")
    assert "record-format:0094" not in _owed(d), "the same blocks, with the counts line, settle the unit"


def test_the_checks_a_reply_answers_are_read_from_its_counts_line() -> None:
    ro = ae._sibling("record_owed")
    assert ro.reply_checks(REPLY) == ("record-format",)
    assert ro.reply_checks("\nmodal-research: Farmhouse - ACCURACY 0 findings") == ("modal-accuracy", "modal-references", "modal-gaps")
    assert ro.reply_checks("EDIT notes/x.md\n<<<") == ()
    # a batch reply opens with prose and names its check on each unit's counts line (feature 385 T21)
    batch = "I judged all three pop-ups unit by unit.\n\nunit: modal-depiction:choice/x 1\n\nmodal-depiction: choice.x - COVERAGE 0 findings; TRUTH 1\n"
    assert ro.reply_checks(batch) == ("modal-depiction",)
    assert ro.reply_checks("Some prose.\nrecord-format notes: none") == (), "a known name with no counts line is no check"


def test_a_block_already_applied_is_not_applied_twice(tmp_path, capsys) -> None:
    """Feature 374 wave 154: a block whose new text holds its old text still found the old text once applied, and a re-run
    wrote it again (a pop-up's `Entry:` path doubled). Its new text standing in the file is the block applied: skipped."""
    q = _tree(tmp_path)
    rel = str(q.relative_to(tmp_path))
    report = tmp_path / "r.md"
    report.write_text("record-format: 1 note\n" + _report(rel, "the gloss said stipend", "the gloss said stipend, a yearly one"), encoding="utf-8")
    ae.main([str(report), "--root", str(tmp_path)])
    ae.main([str(report), "--root", str(tmp_path)])
    assert q.read_text(encoding="utf-8").count("a yearly one") == 1
    assert "already applied" in capsys.readouterr().out


def test_an_edit_applied_by_hand_word_for_word_settles_through_its_reply(tmp_path, capsys) -> None:
    """Feature 385 T21 (the round arbiter's fix on ask:t05-lane-popup-round3): the test is the diff matching the round's EDIT line
    for line, however it was applied - T05 applied 0196's and the pop-ups' EDITs by hand and re-owed both rounds."""
    d, page = _repo(tmp_path)
    _answer_now(d)
    page.write_text(PAGE.replace("The Russians built theirs at the border.", "The Russians built theirs."), encoding="utf-8")
    assert "record-format:0094" in _owed(d), "applied by hand, the unit re-owes"
    before = page.read_text(encoding="utf-8")
    _apply(d, page, "The Russians built theirs at the border.", "The Russians built theirs.")
    assert page.read_text(encoding="utf-8") == before, "the file ends as the hand left it"
    assert "record-format:0094" not in _owed(d), "settled through its reply"
    out = capsys.readouterr().out
    assert "found applied by hand - settled through its reply" in out and "settled with its answered round" in out


def test_a_hand_edit_that_departs_from_the_edit_still_owes(tmp_path) -> None:
    d, page = _repo(tmp_path)
    _answer_now(d)
    page.write_text(PAGE.replace("The Russians built theirs at the border.", "The Russians built theirs, they say."), encoding="utf-8")
    r = d.parent / "reply.md"
    r.write_text(REPLY + _report(str(page.relative_to(d)), "The Russians built theirs at the border.", "The Russians built theirs."), encoding="utf-8")
    assert ae.main([str(r), "--root", str(d)]) == 1, "its old text is gone and its new text is not there: refused"
    assert "record-format:0094" in _owed(d)
