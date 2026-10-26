"""The docstring-blind code id (feature 426, D2): what runs moves it, what a function says about itself does not."""

from __future__ import annotations

from l7r.diagram.pipeline import codeid

BASE = b'''"""A module."""

X = 3
"""Research: a constant's claim - GUESS"""


@deco
def f(a, b=2):
    """f's docstring."""
    return a + b  # a comment


class C:
    """C."""

    y = 1

    def m(self):
        return self.y
'''


def _ids(src: bytes):  # noqa: ANN202
    got = codeid.split_ids(src)
    assert got is not None
    return got


def test_docstrings_comments_blank_lines_and_formatting_keep_every_id() -> None:
    quiet = (
        BASE.replace(b'"""A module."""', b'"""A module, reworded."""')
        .replace(b"GUESS", b"CONVENTION: relabeled")
        .replace(b"f's docstring.", b"f's docstring, with a claim line added.")
        .replace(b"# a comment", b"# another comment")
        .replace(b"    return a + b", b"\n    return (a\n            + b)")
    )
    assert _ids(quiet) == _ids(BASE)
    assert codeid.semantic_bytes(quiet, "m.py") == codeid.semantic_bytes(BASE, "m.py")


def test_a_changed_number_name_default_or_decorator_moves_the_id_it_belongs_to() -> None:
    top, funcs, classes = _ids(BASE)
    assert classes == {"C"} and set(funcs) == {"f", "C.m"}
    assert _ids(BASE.replace(b"X = 3", b"X = 4"))[0] != top, "a constant is the top level"
    assert _ids(BASE.replace(b"return a + b", b"return a - b"))[1]["f"] != funcs["f"], "a body"
    assert _ids(BASE.replace(b"b=2", b"b=5"))[1]["f"] != funcs["f"], "a default"
    assert _ids(BASE.replace(b"@deco", b"@other"))[1]["f"] != funcs["f"], "a decorator"
    moved = _ids(BASE.replace(b"return a + b", b"return a - b"))
    assert moved[0] == top and moved[1]["C.m"] == funcs["C.m"], "a function's change moves only that function"
    assert _ids(BASE.replace(b"y = 1", b"y = 2"))[0] != top, "a class attribute is the top level"


def test_a_file_that_does_not_parse_is_its_bytes_and_a_non_python_file_is_too() -> None:
    assert codeid.split_ids(b"def (:") is None
    assert codeid.semantic_bytes(b"def (:", "m.py") == b"def (:"
    assert codeid.semantic_bytes(b"# a Makefile line", "Makefile") == b"# a Makefile line"


def test_the_engine_reads_the_one_module_the_gates_load() -> None:
    """The shim loads `scripts/gates/codeid.py` once: a second load is the module already loaded, which gate-stamp shares."""
    assert codeid._load() is codeid._mod and codeid.semantic_bytes is codeid._mod.semantic_bytes
