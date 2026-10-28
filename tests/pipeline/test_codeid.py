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


# ---- counter blocks (feature 446, FR-001) -----------------------------------------------------------------------------------

_PLAIN = b"def f(xs, ring):\n    n = 0\n    for x in xs:\n        n += x\n    return n\n"


def _free(src: bytes) -> bytes:
    return codeid._mod.debug_free_bytes(src, "m.py")


def test_a_counter_block_is_removed_and_nothing_else_is() -> None:
    counted = _PLAIN.replace(b"    n = 0\n", b'    n = 0\n    if __debug__:\n        OPS["candidate@f"] += len(xs) * len(self.ring)\n        OPS["dist@f"] -= 1\n')
    assert _free(counted) == _free(_PLAIN) and counted != _PLAIN, "a counter block changes nothing that runs without it"
    for form in (b"len(xs)", b"xs.size", b"max(len(xs) - 1, 0)", b"k", b"2"):
        assert _free(_PLAIN.replace(b"    n = 0\n", b'    n = 0\n    if __debug__:\n        OPS["a@f"] += ' + form + b"\n")) == _free(_PLAIN), form
    assert codeid._mod.debug_free_bytes(b"not python", "m.txt") == b"not python" and _free(b"def (") == b"def ("


def test_anything_but_a_counter_in_a_debug_block_is_code() -> None:
    for body in (
        b'        OPS["a@f"] += len(g(xs))\n',  # a call inside len
        b'        OPS["a@f"] += g(xs)\n',  # a call
        b'        OPS["a@f"] += xs.total\n',  # an attribute other than .size
        b'        OPS["a@f"] = 1\n',  # not an augmented assignment
        b'        OPS[key] += 1\n',  # a computed key
        b'        BY_STAGE["a"] += 1\n',  # another target
        b'        n += 1\n',
        b'        OPS["a@f"] *= 2\n',
        b'        OPS["a@f"] += max(xs, 0)\n',
        b'        OPS["a@f"] += self.xs.size\n',  # .size on anything but a bare name
        b'        OPS["a@f"] += len(xs) + 1\n',  # an operator other than *
    ):
        counted = _PLAIN.replace(b"    n = 0\n", b"    n = 0\n    if __debug__:\n" + body)
        assert _free(counted) != _free(_PLAIN), body
    with_else = _PLAIN.replace(b"    n = 0\n", b'    n = 0\n    if __debug__:\n        OPS["a@f"] += 1\n    else:\n        n = 1\n')
    assert _free(with_else) != _free(_PLAIN), "an else runs under -O: code"
    conj = _PLAIN.replace(b"    n = 0\n", b'    n = 0\n    if __debug__ and n:\n        OPS["a@f"] += 1\n')
    assert _free(conj) != _free(_PLAIN), "`if __debug__ and ...` is not a counter block"
