"""`scripts/_brief_load.py` (feature 274 D1): the questions a page-session brief assigns, the count the write cap rests on.

WHAT THESE PROVE (SC-001). The fixtures are trimmed COPIES of real briefs - their header, their do-not-edit paragraph
and their assignment lists - over a fixture record of one empty fragment a page: 269's V2, C1 and X1 count 9, 6 and 10,
272's S (a range and an id list) 8, and each is refused with its split named; 271's `g1-check-a` and 269's
`h1-check-a` count 2 though their do-not-edit paragraphs name dozens of sections; 250's owed-modal brief of six
sections passes on its declared `check`. A one-line item spanning six sections counts six, a range is expanded
against the fragments on disk, a code reference is not a section, and a brief assigning nothing is refused.
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
    assert detail == [f"vegetation/{s}" for s in ("010", "030", "050", "090", "110", "120", "150", "154")] + ["B30"]


@pytest.mark.parametrize("name", ["g1-check-a.md", "h1-check-a.md"])
def test_a_real_check_brief_counts_only_its_questions_not_its_do_not_edit_list(name: str) -> None:
    text = _brief(name)
    assert "Do not edit these sections" in text, "the fixture keeps the paragraph the count must skip"
    assert bl.load(text, RECORD)[1] == 2 and bl.refusal(FIX / name, text, RECORD) == ""


def test_the_owed_modal_brief_of_six_sections_runs_on_its_declared_kind() -> None:
    kind, n, _detail = bl.load(_brief("owed-buildings-1.md"), RECORD)
    assert (kind, n) == ("check", 6) and bl.refusal(FIX / "owed-buildings-1.md", _brief("owed-buildings-1.md"), RECORD) == ""


def test_one_line_spanning_six_sections_counts_six_and_a_range_expands_on_disk() -> None:
    six = "## Your items\n\n- A1 one line: `fields/010`, `020`, `030`, `040`, `050`, `060`. M.\n\n## Next\n- Z9 not assigned\n"
    assert bl.load(six, RECORD)[1] == 6
    ranged = "## Your items\n- R1 absences in `religion-and-death/090-128`, and `scripts/x.py:195-304` is code\n"
    assert bl.load(ranged, RECORD)[2] == [f"religion-and-death/{s}" for s in ("090", "100", "110", "128")]
    code = "## Your items\n- C7 the parser at `scripts/x.py:195-304`\n- no id here at all\n"
    assert bl.load(code, RECORD)[2] == ["C7", "no"], "a code reference is not a section; an item with no id counts one"
    under_main = "## Your items\n- B1 `towns/020`\n- B2 its range 100-200 and `090`\n"
    assert bl.load(under_main, RECORD)[2] == ["towns/020", "towns/090"], "the main page's range expands to no fragment"


def test_the_exempt_kinds_pass_and_anything_else_is_refused() -> None:
    big = "## Your items\n" + "".join(f"- B{n:02d} a question\n" for n in range(10, 20))
    for kind in bl.KINDS:
        assert bl.refusal(FIX / "x.md", f"<!-- page-load: kind={kind} -->\n{big}", RECORD) == ""
    assert "not an exempt kind" in bl.refusal(FIX / "x.md", f"<!-- page-load: kind=write -->\n{big}", RECORD)
    assert "assigns nothing" in bl.refusal(FIX / "x.md", "# a brief\n\nDo the work.\n", RECORD), "the count never fails open"
    assert bl.refusal(FIX / "x.md", "## Your items\n- B1 one\n- B2 two\n", RECORD) == ""


def test_pages_are_the_record_s_directories_and_a_shared_last_segment_is_no_alias(tmp_path: pathlib.Path) -> None:
    assert "cities/defenses" in bl.pages(RECORD) and "sources" not in bl.pages(RECORD) and "sources/010-works-cited" not in bl.pages(RECORD)
    for p in ("a/x", "b/x", "c/y"):
        (tmp_path / p).mkdir(parents=True)
        (tmp_path / p / "010-q.html").write_text("", encoding="utf-8")
    alias = bl._aliases(bl.pages(tmp_path))
    assert "x" not in alias and alias["y"] == "c/y"
    assert bl.load("## Your items\n- B1 `y/010`\n", tmp_path)[2] == ["c/y/010"]
    assert bl.count("## Your items\n- B1 `nowhere/010`\n", tmp_path / "empty")[1] == ["B1"], "no record, no pages"


def test_split_names_and_the_command_line(capsys) -> None:
    assert bl.split_names(pathlib.Path("v2-write.md"), 9) == ["v2a-write.md", "v2b-write.md", "v2c-write.md"]
    assert bl.split_names(pathlib.Path("group.md"), 5) == ["groupa.md", "groupb.md"]
    assert bl.main([str(RECORD), str(FIX / "g1-check-a.md")]) == 0
    assert bl.main([str(RECORD), str(FIX / "v2-write.md")]) == 1 and "REFUSED" in capsys.readouterr().out
    assert bl.main([]) == 2
