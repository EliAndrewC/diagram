"""`scripts/_apply_edits.py` (feature 250 D15): a check report's EDIT and GLOSSARY blocks, applied in one command.

WHAT THESE PROVE. A block whose old text occurs once in a record file is applied; one that occurs twice or not at
all, or names a file outside the record, is REFUSED and nothing is written; `--skip` and `--dry-run` write nothing
for what they name; a glossary term becomes the next numbered file, and one already on file is skipped; the report
is read from plain text or from the last reply in an agent transcript; a report with no block is a usage error.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_apply_edits", REPO / "scripts" / "_apply_edits.py")
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
    other = tmp_path / ".claude/skills/diagram/l7r/diagram/settlement/x.py"
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
