"""`scripts/_brief_load.py` (feature 274 D1): the questions a page-session brief assigns, the count the write cap rests on.

WHAT THESE PROVE (SC-001). The fixtures are trimmed COPIES of real briefs - their header, their do-not-edit paragraph
and their assignment lists, rewritten into feature 303's form (a question named by its number) - over a fixture record
of empty question files, `record/questions/NNNN-q<n>.html`: 269's V2, C1 and X1 count 9, 6 and 10,
272's S (a range and an id list) 8, and each is refused with its split named; 271's `g1-check-a` and 269's
`h1-check-a` count 2 though their do-not-edit paragraphs name dozens of sections; 250's owed-modal brief of six
sections passes on its declared `check`. A one-line item naming six questions counts six, a number that is no question
on disk is not counted, a code reference is not a question, and a brief assigning nothing is refused.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
FIX = pathlib.Path(__file__).resolve().parent / "fixtures" / "brief_load"
RECORD = FIX / "record"


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_brief_load", REPO / "scripts" / "_brief_load.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bl = _load()


def _brief(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(("name", "want"), [("v2-write.md", 9), ("c1-write.md", 6), ("x1-write.md", 10), ("s-write.md", 8)])
def test_the_costliest_real_write_briefs_count_over_the_cap_and_are_refused(name: str, want: int) -> None:
    kind, n, detail = bl.load(_brief(name), RECORD)
    assert (kind, n) == ("", want), detail
    why = bl.refusal(FIX / name, _brief(name), RECORD)
    assert f"assigns {want} questions" in why and "WRITE_CAP_OK" in why and name.replace("-write", "a-write") in why


def test_v2_counts_each_section_and_the_item_that_names_none() -> None:
    _kind, _n, detail = bl.load(_brief("v2-write.md"), RECORD)
    assert detail == [f"{n:04d}" for n in range(10, 18)] + ["B30"]


@pytest.mark.parametrize("name", ["g1-check-a.md", "h1-check-a.md"])
def test_a_real_check_brief_counts_only_its_questions_not_its_do_not_edit_list(name: str) -> None:
    text = _brief(name)
    assert "Do not edit these sections" in text, "the fixture keeps the paragraph the count must skip"
    assert bl.load(text, RECORD)[1] == 2 and bl.refusal(FIX / name, text, RECORD) == ""


def test_the_owed_modal_brief_of_six_sections_runs_on_its_declared_kind() -> None:
    kind, n, _detail = bl.load(_brief("owed-buildings-1.md"), RECORD)
    assert (kind, n) == ("check", 6) and bl.refusal(FIX / "owed-buildings-1.md", _brief("owed-buildings-1.md"), RECORD) == ""


def test_one_line_naming_six_questions_counts_six_and_only_questions_on_disk_count() -> None:
    six = "## Your items\n\n- A1 one line: `0008`, `0009`, `0010`, `0011`, `0012`, `0013`. M.\n\n## Next\n- Z9 not assigned\n"
    assert bl.load(six, RECORD)[1] == 6
    listed = "## Your items\n- R1 absences in `0215, 0221, 0222, 0223`, and `scripts/x.py:1950-3040` is code\n"
    assert bl.load(listed, RECORD)[2] == ["0215", "0221", "0222", "0223"]
    code = "## Your items\n- C7 the parser at `scripts/x.py:195-304`\n- no id here at all\n"
    assert bl.load(code, RECORD)[2] == ["C7", "no"], "a code reference is not a question; an item with no id counts one"
    off_disk = "## Your items\n- B1 `0020` and `9999`\n"
    assert bl.load(off_disk, RECORD)[2] == ["0020"], "a number that is no question on disk is not counted"
    assert bl.count("## Your items\n- B1 `0020`\n", RECORD / "empty")[1] == ["B1"], "no record, no questions"
    pairs = "**Your pairs:** KIND=X (Q=0030), KIND=Y (Q=0031, 0032)\n"
    assert bl.load(pairs, RECORD)[2] == ["0030", "0031", "0032"]


def test_the_exempt_kinds_pass_and_anything_else_is_refused() -> None:
    big = "## Your items\n" + "".join(f"- B{n:02d} a question\n" for n in range(10, 20))
    for kind in bl.KINDS:
        assert bl.refusal(FIX / "x.md", f"<!-- page-load: kind={kind} -->\n{big}", RECORD) == ""
    assert "not an exempt kind" in bl.refusal(FIX / "x.md", f"<!-- page-load: kind=write -->\n{big}", RECORD)
    assert "assigns nothing" in bl.refusal(FIX / "x.md", "# a brief\n\nDo the work.\n", RECORD), "the count never fails open"
    assert bl.refusal(FIX / "x.md", "## Your items\n- B1 one\n- B2 two\n", RECORD) == ""


def test_split_names_and_the_command_line(capsys) -> None:
    assert bl.split_names(pathlib.Path("v2-write.md"), 9) == ["v2a-write.md", "v2b-write.md", "v2c-write.md"]
    assert bl.split_names(pathlib.Path("group.md"), 5) == ["groupa.md", "groupb.md"]
    assert bl.main([str(RECORD), str(FIX / "g1-check-a.md")]) == 0
    assert bl.main([str(RECORD), str(FIX / "v2-write.md")]) == 1 and "REFUSED" in capsys.readouterr().out
    assert bl.main([]) == 2
