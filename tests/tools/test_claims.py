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
    for bad in ("a gap - GUESS maybe", f"a gap - GUESS {Q}"):
        with pytest.raises(cl.ClaimError, match="names the drawing page"):
            cl.parse_claim(bad)


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
    assert [u.kind for u in cl.module_units("register(1)\n", "k.py", every_module_unit=True)[2]] == ["module"], "...unless asked (the push's base)"


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


SECTION = """## Wells

<!-- Research: well seat - GUESS -->
<!-- Research: curb size - CONVENTION -->

A well stands by the kitchen,
a few feet out.

- a curb of stone
  around its mouth
- a sweep beside it

| item | band |
|---|---|
| well | 3-4 ft |
| curb | 1 ft |
"""


def test_a_section_claim_is_owed_by_its_own_line_and_the_section_has_its_blocks() -> None:
    """Feature 375 FR-002: the markers stand at the section's head, not beside their rule text, so a section claim's code is
    its own line; the section's words are its core and its blocks, which a triage diffs. Before, one edit anywhere in the
    section re-owed every claim of it."""
    (u,) = cl.doc_units(SECTION, "b.md", None)
    assert u.blocks == ("A well stands by the kitchen, a few feet out.", "- a curb of stone around its mouth", "- a sweep beside it", "| item | band |", "| well | 3-4 ft |", "| curb | 1 ft |")
    (moved,) = cl.doc_units(SECTION.replace("| 1 ft |", "| 2 ft |"), "b.md", None)
    assert moved.core != u.core and [moved.code(c) for c in moved.claims] == [u.code(c) for c in u.claims], "a row moved; no line did"
    (relabeled,) = cl.doc_units(SECTION.replace("curb size - CONVENTION", "curb size - GUESS"), "b.md", None)
    assert relabeled.code(relabeled.claims[1]) != u.code(u.claims[1]) and relabeled.code(relabeled.claims[0]) == u.code(u.claims[0])
    assert cl.section_blocks("# head\ntext\n") == ("# head", "text"), "a heading line is a block of its own"


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
    (tmp / "docs").mkdir(parents=True, exist_ok=True)
    (tmp / "docs" / "buildings.md").write_text("## Walls\n<!-- Research: w - NONE -->\n")
    (tmp / "docs" / "building-programs.md").write_text("### Magistrate's manor (county magistracy)\ntext\n### Other\n")
    return tmp


def test_a_tree_without_the_procedure_documents_reads_its_code(tmp_path: Path) -> None:
    skill = _tree(tmp_path)
    (skill / "docs" / "buildings.md").unlink()
    (skill / "docs" / "building-programs.md").unlink()
    assert all(u.kind != "section" for u, _e in cl.all_units(skill, ""))


def test_the_scope_is_the_import_graph_from_the_hamlet_generator(tmp_path: Path) -> None:
    mods = cl.scope(_tree(tmp_path))
    assert set(mods) == {"l7r.diagram.hamletgen", "l7r.diagram.hamletgen.a", "l7r.diagram.hamletgen.b", "l7r.diagram.shared", "l7r.diagram.other", "l7r.diagram.other.b"}


def test_a_claimed_unit_outside_the_scope_enters_the_index_and_its_unclaimed_neighbors_do_not(tmp_path: Path) -> None:
    # feature 378: the magistracy's code sits outside the hamlet's imports; a unit there that carries its OWN claim is
    # read (so its check reaches the index and the report), its module's other units are not, and a module docstring's
    # claim - which every unit would inherit - brings none in
    skill = _tree(tmp_path)
    (skill / "l7r" / "diagram" / "other" / "c.py").write_text(
        f'"""Research: whole module - NONE"""\nLIMIT = 3\n\n\ndef court():\n    """Research: court size - {Q}"""\n    return LIMIT\n\n\ndef unreached():\n    pass\n'
    )
    outside = [(u.path, u.qualname) for u, _e in cl.claimed_outside(skill, set(cl.scope(skill)))]
    assert outside == [("l7r/diagram/other/c.py", "court")]
    assert ("l7r/diagram/other/c.py", "court") in [(u.path, u.qualname) for u, _e in cl.all_units(skill, "")]
    problems = cl.coverage(cl.all_units(skill, ""), questions={"0033-row-villages-resson.html"})
    assert not [p for p in problems if "other/c.py" in p], "an unclaimed neighbor outside the scope owes no claim"


def test_coverage_names_every_unit_without_a_claim_and_every_missing_question(tmp_path: Path) -> None:
    skill = _tree(tmp_path)
    (skill / "l7r" / "diagram" / "other" / "b.py").write_text(f'"""Research: oops\n"""\ndef thing():\n    """Research: t - {Q}"""\n')
    problems = cl.coverage(cl.all_units(skill, ""), questions=set())
    text = "\n".join(problems)
    assert "l7r/diagram/other/b.py module docstring: `oops` has no `<label> - <backing>`" in text
    assert "l7r/diagram/other/b.py:3 thing: `research/questions/0033-row-villages-resson.html` names no question file" in text
    assert "docs/building-programs.md:1 Magistrate's manor (county magistracy): no claim - add a `<!-- Research:" in text
    assert "shared.py" not in text and "docs/buildings.md:" not in text
    assert cl.coverage(cl.all_units(skill, ""), questions={"0033-row-villages-resson.html"}) == [p for p in problems if "names no question" not in p]


# ---- feature 375 amendment 8, FR-035 (plan D48): each module's units kept by what they read ----------------------------------


class _Memo(dict):
    """The `Memo` interface over a dict (what `record_cache.ParseCache` gives in use)."""

    def get(self, key, make):  # type: ignore[no-untyped-def, override]
        if key not in self:
            self[key] = make()
        return self[key]


def _cache_tree(tmp: Path) -> Path:
    eng = tmp / "l7r" / "diagram"
    (eng / "hamletgen").mkdir(parents=True)
    (eng / "other").mkdir()
    (eng / "hamletgen" / "__init__.py").write_text("from . import a, b\n")
    (eng / "hamletgen" / "consts.py").write_text("from l7r.diagram.shared import X\n")  # re-exports X
    (eng / "hamletgen" / "a.py").write_text('"""Research: all - NONE"""\nfrom l7r.diagram.shared import X\nfrom l7r.diagram.other import b\n\n\ndef reads():\n    return X\n')
    (eng / "hamletgen" / "b.py").write_text('"""Research: all - NONE"""\nfrom .consts import X\n\n\ndef reads_through():\n    return X\n')
    (eng / "shared.py").write_text('"""Research: all - NONE"""\nX = 1\n')
    (eng / "other" / "__init__.py").write_text("")
    (eng / "other" / "b.py").write_text("def thing():\n    pass\n")
    (eng / "other" / "c.py").write_text('def court():\n    """Research: court size - NONE"""\n    return 3\n')
    return tmp


def _run(skill: Path, memo: _Memo | None, spy: list[str]) -> list[tuple[str, str, str, tuple[str, ...]]]:
    spy.clear()
    return [(u.path, u.qualname, u.core, tuple(e)) for u, e in cl.all_units(skill, "", memo=memo)]


@pytest.fixture
def spied(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []
    real = cl.module_units

    def spy(source, path, *a, **k):  # type: ignore[no-untyped-def]
        calls.append(path)
        return real(source, path, *a, **k)

    monkeypatch.setattr(cl, "module_units", spy)
    return calls


def test_the_kept_units_equal_an_uncached_run_and_a_second_run_computes_none(tmp_path: Path, spied: list[str]) -> None:
    skill, memo = _cache_tree(tmp_path), _Memo()
    plain = _run(skill, None, spied)
    assert _run(skill, memo, spied) == plain and len(spied) == 8, "every module computed once into the memo"
    assert _run(skill, memo, spied) == plain and spied == [], "and none again"


def test_a_comment_recomputes_its_own_module_alone(tmp_path: Path, spied: list[str]) -> None:
    skill, memo = _cache_tree(tmp_path), _Memo()
    _run(skill, memo, spied)
    f = skill / "l7r" / "diagram" / "other" / "b.py"
    f.write_text(f.read_text() + "# a comment\n")
    _run(skill, memo, spied)
    assert spied == ["l7r/diagram/other/b.py"]


def test_a_constant_recomputes_its_readers_direct_and_through_a_package_and_not_the_rest(tmp_path: Path, spied: list[str]) -> None:
    skill, memo = _cache_tree(tmp_path), _Memo()
    _run(skill, memo, spied)
    (skill / "l7r" / "diagram" / "shared.py").write_text('"""Research: all - NONE"""\nX = 2\n')
    after = _run(skill, memo, spied)
    assert {"l7r/diagram/shared.py", "l7r/diagram/hamletgen/a.py", "l7r/diagram/hamletgen/b.py"} <= set(spied), "the reader through consts too"
    assert "l7r/diagram/other/b.py" not in spied and "l7r/diagram/other/c.py" not in spied
    assert after == _run(skill, None, spied), "and what it keeps is what an uncached run gives"


def test_a_module_moving_into_the_scope_is_recomputed_there(tmp_path: Path, spied: list[str]) -> None:
    skill, memo = _cache_tree(tmp_path), _Memo()
    _run(skill, memo, spied)
    a = skill / "l7r" / "diagram" / "hamletgen" / "a.py"
    a.write_text(a.read_text().replace("from l7r.diagram.other import b\n", "from l7r.diagram.other import b, c\n"))
    after = _run(skill, memo, spied)
    assert "l7r/diagram/other/c.py" in spied, "c entered the scope: its units are the scope's, not claimed_outside's"
    assert after == _run(skill, None, spied)


def test_the_cores_hash_is_the_modules_own_and_the_cache_keys_hash_is_another() -> None:
    """A key helper named `_sha`, defined below the module's own, replaced it for every core and fingerprint - every claim
    would have read as moved (caught 2026-10-12 by comparing all 4,050 cores against the commit before)."""
    import hashlib

    assert cl._sha("x") == hashlib.sha256(b"x").hexdigest()[:16]
    assert cl._key_sha("x") == hashlib.sha256(b"x").hexdigest() and cl._key_sha("a", "b") != cl._key_sha("a\x00b", "")


def test_a_claimed_dictionary_s_claims_are_keyed_by_their_own_line_and_its_entries_are_blocks() -> None:
    """Feature 385 T83 (plan D103): one entry added to `_OVERLAP_EXEMPT` at T08 re-owed all 17 of its claims."""
    src = 'X = {\n    "a": "one",\n    "b": "two",\n}\n"""Research: rule one - CONVENTION: x"""\n'
    added = src.replace('    "b": "two",\n', '    "b": "two",\n    "c": "three",\n')
    (u,) = [x for x in cl.module_units(src, "m.py")[2] if x.qualname == "X"]
    (v,) = [x for x in cl.module_units(added, "m.py")[2] if x.qualname == "X"]
    assert u.blocks == ("'a': 'one'", "'b': 'two'") and len(v.blocks) == 3
    assert u.code(u.claims[0]) == v.code(v.claims[0]), "an entry added leaves the claim's own code"
    assert u.core != v.core, "...while the core moves, which owes the triage"
    plain = 'Y = (1, 2)\n"""Research: rule two - CONVENTION: y"""\n'
    (w,) = [x for x in cl.module_units(plain, "m.py")[2] if x.qualname == "Y"]
    spread = 'B = {"a": 1}\nZ = {**B, "c": 3}\n"""Research: rule three - CONVENTION: z"""\n'
    (z,) = [x for x in cl.module_units(spread, "m.py")[2] if x.qualname == "Z"]
    assert z.blocks == ("**B", "'c': 3")
    assert w.blocks == () and w.code(w.claims[0]) != cl._sha("section-claim\x1f" + w.claims[0].normalized()), "not a dict: as before"
