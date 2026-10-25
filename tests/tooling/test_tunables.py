"""`make tunables` (feature 417 T28, D31): every claim whose value is ours - GUESS, UNRESEARCHED, CONVENTION - listed for a fixing
pass, derived from the claims, never kept by hand."""

from __future__ import annotations

import importlib.util
import sys
from types import SimpleNamespace

from tests._scripts import script


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("tunables", script("tunables"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tunables"] = mod
    spec.loader.exec_module(mod)
    return mod


tu = _load()


def _row(backing: str, account: str) -> SimpleNamespace:
    return SimpleNamespace(claim=SimpleNamespace(backing=backing, account=account))


ROWS = {
    "l7r/a.py::f#angle": _row("GUESS", "20 deg, the page's; searched, silent"),
    "l7r/a.py::f#reach": _row("UNRESEARCHED", "40 ft past a meeting"),
    "l7r/b.py::g#width": _row("CONVENTION", "a lane drawn 5 ft"),
    "l7r/b.py::g#order": _row("UNRESEARCHED", "the nearer end first"),
    "l7r/b.py::g#cited": _row("POINTER", "3 ft, the page's"),
    "l7r/b.py::g#none": _row("NONE", "plumbing, 4 ft"),
    "l7r/c.py::h#missing": SimpleNamespace(claim=None),
}


def test_only_the_values_that_are_ours_with_a_figure_are_listed_searched_first() -> None:
    found = tu.tunables(ROWS)
    assert [(lab, key) for lab, key, _a in found] == [
        ("GUESS", "l7r/a.py::f#angle"),
        ("UNRESEARCHED", "l7r/a.py::f#reach"),
        ("CONVENTION", "l7r/b.py::g#width"),
    ], "a cited value, NONE, a unit with no claim and an account with no figure are not listed"


def test_all_keeps_a_claim_with_no_figure_and_path_narrows() -> None:
    assert ("UNRESEARCHED", "l7r/b.py::g#order", "the nearer end first") in tu.tunables(ROWS, figures_only=False)
    assert [k for _l, k, _a in tu.tunables(ROWS, "l7r/b.py")] == ["l7r/b.py::g#width"]


def test_the_render_says_what_the_list_is_for_and_counts_by_label() -> None:
    text = tu.render(tu.tunables(ROWS))
    assert text.splitlines()[0].startswith("tunables: GUESS 1, UNRESEARCHED 1, CONVENTION 1 - values no source states: a goal and a knob")
    assert "  GUESS        l7r/a.py::f#angle - 20 deg, the page's; searched, silent" in text
    assert tu.render(tu.tunables(ROWS), count=True).count("\n") == 0
    assert tu.render([]).startswith("tunables: none")


SRC = '''
def place(x):
    gap = 14.0
    margin = 6.0
    pts = x[3]
    return x * 1.0 + gap + margin + 0.5 + 1e-9
'''


def test_inline_numbers_its_unit_never_states_are_found_and_stated_or_trivial_ones_are_not() -> None:
    found = tu.unstated(SRC, {"place": "lane off the water - UNRESEARCHED: 14 ft"})
    assert [(fn, v) for fn, _line, v in found] == [("place", 6.0)], "14 is stated; 3 is a subscript; 1, 0.5 and 1e-9 are trivial"
    assert [v for _f, _l, v in tu.unstated(SRC, {})] == [14.0, 6.0], "a unit with no claim states nothing"


def test_the_inline_render_counts_by_file() -> None:
    found = [("l7r/a.py", 3, "f", 14.0), ("l7r/a.py", 9, "g", 6.0), ("l7r/b.py", 2, "h", 7.5)]
    text = tu.render_inline(found)
    assert text.splitlines()[0].startswith("tunables --inline: 3 number(s) in 2 file(s) no claim states - ours by default")
    assert "  l7r/b.py:2 h 7.5" in text
    assert tu.render_inline(found, count=True).splitlines()[1] == "      2  l7r/a.py"
