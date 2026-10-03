"""The research claims reader (`tools/claims.py`, feature 316).

What is pinned is what the index's owed-ness rests on: a claim parses or is refused with the grammar; a unit's code
fingerprint moves with its executable code, its claim line and the constants it names, and with nothing else - not a comment,
not formatting, not docstring prose, not a question's renumbering; a module's claims are inherited; the scope follows the
import graph; coverage names every unit with no claim.

Unit forms on source text and a tmp tree, so they run in `make quick`; the real scope's coverage is
`tests/tooling/test_claims_coverage.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.tools import claims as cl

Q = "research/questions/0033-row-villages-resson.html"
D = "research/questions/0033-row-villages-resson.drawing.html"


# ---- the grammar ---------------------------------------------------------------------------------------------


def test_a_pointer_claim_parses_with_its_account() -> None:
    c = cl.parse_claim(f"dry-field share - {Q}, {D}: rolled per settlement")
    assert (c.label, c.backing, c.pointers, c.account) == ("dry-field share", "POINTER", (Q, D), "rolled per settlement")


@pytest.mark.parametrize("cls", ["UNRESEARCHED", "CONVENTION", "CANON", "NONE"])
def test_a_class_claim_parses_and_takes_no_pointer(cls: str) -> None:
    assert cl.parse_claim(f"a thing - {cls}").backing == cls
    with pytest.raises(cl.ClaimError, match="takes no pointer"):
        cl.parse_claim(f"a thing - {cls} {Q}")


def test_a_guess_may_name_the_drawing_page_that_records_it() -> None:
    assert cl.parse_claim("a gap - GUESS").pointers == ()
    c = cl.parse_claim(f"a gap - GUESS {D}: 12 ft")
    assert (c.backing, c.pointers, c.account) == ("GUESS", (D,), "12 ft")
    with pytest.raises(cl.ClaimError, match="names question files or nothing"):
        cl.parse_claim("a gap - GUESS maybe")


def test_a_deviation_names_the_question_it_departs_from() -> None:
    c = cl.parse_claim(f"grove side - DEVIATION {Q}: kept to windward")
    assert (c.backing, c.pointers) == ("DEVIATION", (Q,))
    with pytest.raises(cl.ClaimError, match="not question files"):
        cl.parse_claim("grove side - DEVIATION")


@pytest.mark.parametrize("line", ["no separator here", " - NONE", "label - ", "label - research/questions/x.html", "label - maybe"])
def test_a_malformed_claim_is_refused(line: str) -> None:
    with pytest.raises(cl.ClaimError):
        cl.parse_claim(line)


def test_the_normalized_line_reduces_a_pointer_to_its_heading_id_so_a_renumbering_owes_nothing() -> None:
    a = cl.parse_claim(f"share - {Q}")
    b = cl.parse_claim("share  -  research/questions/0099-row-villages-resson.html")
    assert a.normalized() == b.normalized() == "share - row-villages-resson"
    assert cl.parse_claim(f"x - {D}").normalized() == "x - row-villages-resson.drawing"


def test_the_section_reads_indented_claims_continuations_and_the_one_line_form() -> None:
    doc = f"Purpose.\n\nResearch:\n    a - NONE\n    b - {Q}:\n        continued here\n    c - GUESS\n\nAfter."
    assert cl.section_lines(doc) == ["a - NONE", f"b - {Q}: continued here", "c - GUESS"]
    assert cl.section_lines("Research: one - NONE") == ["one - NONE"]
    assert cl.section_lines("Research: one - NONE\n\nnot indented") == ["one - NONE"]
    assert cl.section_lines("No section.") is None
    assert cl.section_lines(None) is None


def test_a_flat_section_is_read_where_the_header_opens_the_docstring() -> None:
    doc = f"Research: a - NONE\nb - {Q}: long\ncontinued\n\nAfter."  # what `inspect.cleandoc` leaves of an indented section
    assert cl.section_lines(doc) == ["a - NONE", f"b - {Q}: long continued"]
    assert cl.section_lines("Research:\nx - GUESS") == ["x - GUESS"]
    assert cl.strip_section(doc) == "\nAfter." and cl.strip_section("No section.  ") == "No section."


def test_claims_of_reports_a_bad_line_and_an_empty_section() -> None:
    good, errors = cl.claims_of("Research:\n    a - NONE\n    b - perhaps")
    assert [c.label for c in good] == ["a"] and len(errors) == 1
    assert cl.claims_of("Research:\n\nprose")[1] == ["an empty `Research:` section"]


def test_strip_section_leaves_the_prose() -> None:
    assert cl.strip_section("Title.\n\nResearch:\n    a - NONE\n    b - GUESS\nTail.") == "Title.\n\nTail."


# ---- units and fingerprints ----------------------------------------------------------------------------------

SRC = f'''"""A module.

Research: plumbing - NONE
"""
from .consts import WIDTH as W

DEPTH = 4
"""Research: depth - {Q}"""

LIMIT = 9


def f(x):
    """Do it.

    Research: share - {Q}
    """
    # a comment
    return x * DEPTH + W


def g():
    def inner():
        return 1
    return inner()


class K:
    """Research: kind - CONVENTION"""

    SIZE = 3

    def m(self):
        return LIMIT
'''


def _units(src: str = SRC, consts: dict[str, dict[str, str]] | None = None) -> dict[str, cl.Unit]:
    _m, _e, units = cl.module_units(src, "p.py", "pkg.mod", False, consts if consts is not None else {"pkg.consts": {"WIDTH": "Constant(value=1)"}})
    return {u.qualname: u for u in units}


def test_units_cover_functions_methods_classes_and_constants_and_not_a_nested_function() -> None:
    u = _units()
    assert set(u) == {"DEPTH", "LIMIT", "f", "g", "K", "K.m"}
    assert {k: v.kind for k, v in u.items()} == {"DEPTH": "constant", "LIMIT": "constant", "f": "function", "g": "function", "K": "class", "K.m": "method"}


def test_own_claims_win_and_the_rest_inherit_the_modules() -> None:
    u = _units()
    assert [c.label for c in u["f"].claims] == ["share"] and not u["f"].inherited
    assert [c.label for c in u["DEPTH"].claims] == ["depth"]
    assert [c.label for c in u["g"].claims] == ["plumbing"] and u["g"].inherited
    assert u["K.m"].inherited and u["K"].claims[0].backing == "CONVENTION"
    assert u["f"].key(u["f"].claims[0]) == "p.py::f#share"


def test_the_core_ignores_comments_formatting_and_docstring_prose() -> None:
    before = _units()["f"].core
    after = SRC.replace("    # a comment\n", "").replace("    \"\"\"Do it.", "    \"\"\"Do it, said differently.").replace("x * DEPTH + W", "x*DEPTH  +  W")
    assert _units(after)["f"].core == before


def test_the_core_moves_with_the_code_and_with_a_constant_it_names() -> None:
    before = _units()["f"].core
    assert _units(SRC.replace("x * DEPTH + W", "x * DEPTH - W"))["f"].core != before
    assert _units(SRC.replace("DEPTH = 4", "DEPTH = 5"))["f"].core != before
    assert _units(consts={"pkg.consts": {"WIDTH": "Constant(value=2)"}})["f"].core != before
    assert _units(SRC.replace("LIMIT = 9", "LIMIT = 8"))["f"].core == before, "a constant it does not name"
    assert _units()["f"].names == ("DEPTH=Constant(value=4)", "WIDTH=Constant(value=1)")


def test_a_read_through_a_module_alias_counts_and_a_rename_keeps_the_core() -> None:
    src = "from . import law\nimport pkg.other as o\n\n\ndef h():\n    return law.JOIN + o.GAP + law.lower\n"
    consts = {"pkg.law": {"JOIN": "Constant(value=2)"}, "pkg.other": {"GAP": "Constant(value=5)"}}
    _m, _e, units = cl.module_units(src, "w.py", "pkg.w", False, consts)
    assert units[0].names == ("GAP=Constant(value=5)", "JOIN=Constant(value=2)")
    _m, _e, renamed = cl.module_units(src.replace("def h", "def h2"), "w.py", "pkg.w", False, consts)
    assert renamed[0].core == units[0].core and renamed[0].qualname == "h2"
    assert _units(SRC.replace("DEPTH = 4", "DEEP = 4").replace("x * DEPTH", "x * DEEP"))["DEEP"].core == _units()["DEPTH"].core


def test_a_class_core_is_its_own_statements_not_its_methods() -> None:
    before = _units()["K"].core
    assert _units(SRC.replace("return LIMIT", "return LIMIT + 1"))["K"].core == before
    assert _units(SRC.replace("SIZE = 3", "SIZE = 4"))["K"].core != before


def test_a_claims_code_fingerprint_is_the_core_plus_its_line() -> None:
    u = _units()["f"]
    c = u.claims[0]
    assert u.code(c) == _units(SRC.replace("0033-row", "0090-row"))["f"].code(_units(SRC.replace("0033-row", "0090-row"))["f"].claims[0])
    assert u.code(c) != _units(SRC.replace("Research: share", "Research: portion"))["f"].code(_units(SRC.replace("Research: share", "Research: portion"))["f"].claims[0])


def test_a_module_that_calls_at_import_is_a_unit_of_its_own_claims() -> None:
    src = '"""Knobs.\n\nResearch: lane form - GUESS\n"""\nregister(1)\n\n\ndef f():\n    """Research: f - NONE"""\n'
    _m, _e, units = cl.module_units(src, "k.py")
    mod = next(u for u in units if u.kind == "module")
    assert (mod.qualname, [c.label for c in mod.claims], mod.inherited) == ("<module>", ["lane form"], False)
    assert next(u for u in cl.module_units(src.replace("register(1)", "register(2)"), "k.py")[2] if u.kind == "module").core != mod.core
    assert all(u.kind != "module" for u in cl.module_units("register(1)\n", "k.py")[2]), "no module claims, no module unit"


def test_a_parsed_tree_is_accepted_and_an_annotated_constant_counts() -> None:
    import ast

    _m, _e, units = cl.module_units(ast.parse("X: int = 3\n'''Research: x - NONE'''\nY = Z = 1\nlower = 2\n"), "q.py")
    assert [(u.qualname, [c.label for c in u.claims]) for u in units] == [("X", ["x"])]


def test_an_overload_stub_is_not_a_unit_its_implementation_is() -> None:
    src = "import typing\nfrom typing import overload\n\n\n@overload\ndef f(x: int) -> int: ...\n@typing.overload\ndef f(x: str) -> str: ...\ndef f(x):\n    return x\n"
    _m, _e, units = cl.module_units(src, "o.py")
    assert [(u.qualname, u.lineno) for u in units] == [("f", 9)]


def test_resolve_from_handles_absolute_and_relative_imports() -> None:
    import ast

    node = ast.parse("from ..a import b").body[0]
    assert cl.resolve_from("pkg.sub", node) == "pkg.a"  # type: ignore[arg-type]
    assert cl.resolve_from("pkg.sub", ast.parse("from . import b").body[0]) == "pkg.sub"  # type: ignore[arg-type]
    assert cl.resolve_from("pkg.sub", ast.parse("from x.y import b").body[0]) == "x.y"  # type: ignore[arg-type]
    assert cl.import_table(ast.parse("from .c import D as E"), "pkg", True) == {"E": ("pkg.c", "D")}


def test_a_reexported_constant_resolves_to_its_definition() -> None:
    out = cl.reexported({"a": {"X": "1"}, "b": {}, "c": {}}, {"b": {"Y": ("a", "X")}, "c": {"Z": ("b", "Y"), "w": ("b", "nothing")}})
    assert out["c"] == {"Z": "1"} and out["b"] == {"Y": "1"}


# ---- procedure sections ----------------------------------------------------------------------------------------

DOC = f"""# Title

## One
<!-- Research: walls - {Q} -->
Text.

### One sub
<!-- a note -->
More.

## Two
<!-- Research: gates - nope -->

##### deep
"""


def test_doc_units_are_sections_with_comment_claims() -> None:
    units = cl.doc_units(DOC, "b.md", None)
    assert [(u.qualname, [c.label for c in u.claims], len(u.errors)) for u in units] == [("One", ["walls"], 0), ("One sub", [], 0), ("Two", [], 1)]
    assert cl.doc_units(DOC.replace("More.", "More!"), "b.md", None)[1].core != units[1].core
    assert cl.doc_units(DOC.replace("<!-- a note -->", "<!-- another -->"), "b.md", None)[1].core == units[1].core


def test_doc_units_restricted_to_named_tops_take_their_subtree() -> None:
    units = cl.doc_units(DOC, "b.md", ("One",))
    assert [u.qualname for u in units] == ["One", "One sub"]


# ---- scope and coverage ----------------------------------------------------------------------------------------


def _tree(tmp: Path) -> Path:
    eng = tmp / "l7r" / "diagram"
    (eng / "hamletgen").mkdir(parents=True)
    (eng / "other").mkdir()
    (eng / "hamletgen" / "__init__.py").write_text("from . import a\n")
    (eng / "hamletgen" / "a.py").write_text("import l7r.diagram.shared\nfrom l7r.diagram.other.b import thing\nfrom os import path\n")
    (eng / "hamletgen" / "b.py").write_text("from . import a  # a is queued twice before it is read\n")
    (eng / "shared.py").write_text('"""Research: all - NONE"""\nX = 1\n')
    (eng / "other" / "__init__.py").write_text("")
    (eng / "other" / "b.py").write_text("def thing():\n    pass\n")
    (eng / "other" / "c.py").write_text("def unreached():\n    pass\n")
    (eng / "__pycache__").mkdir()
    (tmp / "buildings").mkdir()
    (tmp / "buildings.md").write_text("## Walls\n<!-- Research: w - NONE -->\n")
    (tmp / "buildings" / "programs.md").write_text("### Magistrate's manor (county magistracy)\ntext\n### Other\n")
    return tmp


def test_a_tree_without_the_procedure_documents_reads_its_code(tmp_path: Path) -> None:
    skill = _tree(tmp_path)
    (skill / "buildings.md").unlink()
    (skill / "buildings" / "programs.md").unlink()
    assert all(u.kind != "section" for u, _e in cl.all_units(skill, ""))


def test_the_scope_is_the_import_graph_from_the_hamlet_generator(tmp_path: Path) -> None:
    mods = cl.scope(_tree(tmp_path))
    assert set(mods) == {"l7r.diagram.hamletgen", "l7r.diagram.hamletgen.a", "l7r.diagram.hamletgen.b", "l7r.diagram.shared", "l7r.diagram.other", "l7r.diagram.other.b"}


def test_coverage_names_every_unit_without_a_claim_and_every_missing_question(tmp_path: Path) -> None:
    skill = _tree(tmp_path)
    (skill / "l7r" / "diagram" / "other" / "b.py").write_text(f'"""Research: oops\n"""\ndef thing():\n    """Research: t - {Q}"""\n')
    problems = cl.coverage(cl.all_units(skill, ""), questions=set())
    text = "\n".join(problems)
    assert "l7r/diagram/other/b.py module docstring: `oops` has no `<label> - <backing>`" in text
    assert "l7r/diagram/other/b.py:3 thing: `research/questions/0033-row-villages-resson.html` names no question file" in text
    assert "buildings/programs.md:1 Magistrate's manor (county magistracy): no claim - add a `<!-- Research:" in text
    assert "shared.py" not in text and "buildings.md:" not in text
    assert cl.coverage(cl.all_units(skill, ""), questions={"0033-row-villages-resson.html"}) == [p for p in problems if "names no question" not in p]
