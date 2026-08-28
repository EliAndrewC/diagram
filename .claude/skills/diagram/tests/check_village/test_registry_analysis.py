"""Unit tests for the branches of registry_analysis the live corpus never exercises.

The fixture-equality test in test_registry_derive.py runs the whole derivation against the real
segment modules, which covers most of the analysis; these snippets hit the constructs the corpus
happens not to contain (With/Try bodies, opaque check names, second-order helper chains), so the
analysis stays fully proven for the segment shapes a future check might legitimately use.
"""

import ast
import types

import pytest

from l7r.diagram.check_village import registry as reg
from l7r.diagram.check_village.registry_analysis import _check_names, _DerivationError, _derive_fields, _exposed_reads


def test_check_name_resolves_through_local_assignment_and_counts_opaque():
    src = "nm = unresolvable(x)\ncheck(nm, True)\nnm2 = 'bar'\ncheck(nm2, True)\n"
    checks, opaque = _check_names(ast.parse(src), {})
    assert checks == ["bar"]
    assert opaque == 1


def test_exposed_reads_threads_with_blocks():
    src = "with opener(p) as f:\n    y = f.read() + q\n"
    exposed, bound = _exposed_reads(ast.parse(src).body, set())
    assert {"p", "q"} <= exposed
    assert "f" not in exposed
    assert {"f", "y"} <= bound


def test_exposed_reads_walks_every_try_block():
    src = "try:\n    a = b\nexcept ValueError:\n    c = d\nelse:\n    e = g\nfinally:\n    h = k\n"
    exposed, _ = _exposed_reads(ast.parse(src).body, set())
    assert {"b", "d", "g", "k"} <= exposed


def test_helper_fixpoint_propagates_through_helper_calling_helper(tmp_path):
    (tmp_path / "segments_01_chain.py").write_text(
        "def _seg_0001__setup(*, acc=None, inner=None, outer=None):\n"
        "    def inner():\n"
        "        acc.append(1)\n"
        "    def outer():\n"
        "        inner()\n"
        "    return _kept(locals(), ('acc', 'inner', 'outer'))\n"
        "def _seg_0002__caller(*, outer=None, acc=None):\n"
        "    outer()\n"
        "    return _kept(locals(), ('acc',))\n"
    )
    fields = _derive_fields(tmp_path)
    # calling `outer` mutates `acc` one indirection deep - the fixpoint must carry it through
    assert "acc" in fields["_seg_0002__caller"].needs


def test_import_scan_guards_duplicate_segment_across_modules(tmp_path, monkeypatch):
    (tmp_path / "segments_01_a.py").write_text("")
    (tmp_path / "segments_02_b.py").write_text("")
    fake = types.SimpleNamespace(_seg_0001__x=object())
    monkeypatch.setattr(reg, "_PKG_DIR", tmp_path)
    monkeypatch.setattr(reg, "import_module", lambda name, package=None: fake)
    with pytest.raises(_DerivationError, match="duplicate segment name"):
        reg._segment_functions()


def test_derive_rows_guards_import_vs_ast_disagreement():
    names = {r.fn.__name__ for r in reg.GATE_SEGMENTS}
    with pytest.raises(_DerivationError, match="disagree"):
        reg._derive_rows(names | {"_seg_9999__ghost"})


def test_check_names_follow_a_helper_that_emits() -> None:
    import ast

    from l7r.diagram.check_village.registry_analysis import _check_names

    node = ast.parse('def seg():\n    check("a", True)\n    helper(M)\n').body[0]
    names, _n = _check_names(node, {"helper": ["b"]})
    assert set(names) >= {"a", "b"}


def test_guard_scales_reads_every_shape_of_leading_guard() -> None:
    """Feature 145's scale derivation, feature 146's proof: each guard shape the reader can write, and the
    shapes that admit every scale (a data guard, a mixed body, a non-literal comparand)."""
    import ast

    from l7r.diagram.check_village.registry_analysis import SCALES, URBAN_SCALES, _guard_scales

    def seg(guard: str, body: str = "        pass\n") -> ast.FunctionDef:
        src = f"def _seg_x(*, M=None):\n    if {guard}:\n{body}    return _kept(locals(), ())\n"
        return ast.parse(src).body[0]  # type: ignore[return-value]

    assert _guard_scales(seg("URBAN")) == URBAN_SCALES
    assert _guard_scales(seg("not URBAN")) == tuple(s for s in SCALES if s not in URBAN_SCALES)
    assert _guard_scales(seg("scale in ('city', 'capital')")) == ("city", "capital")
    assert _guard_scales(seg("scale == 'hamlet'")) == ("hamlet",)
    assert _guard_scales(seg("scale not in ('city', 'capital')")) == tuple(s for s in SCALES if s not in URBAN_SCALES)
    assert _guard_scales(seg("scale != 'hamlet'")) == tuple(s for s in SCALES if s != "hamlet")
    assert _guard_scales(seg("URBAN and M")) == URBAN_SCALES  # the first term of an `and`
    assert _guard_scales(seg("scale in ('atlantis',)")) == ("atlantis",)  # an unknown name is taken at its word
    assert _guard_scales(seg("scale in (1, 2)")) is None  # not strings
    assert _guard_scales(seg("scale in M")) is None  # not a literal
    assert _guard_scales(seg("M.get('houses')")) is None  # a data guard admits every scale
    src = "def _seg_y(*, M=None):\n    if URBAN:\n        pass\n    check('x', True)\n    return _kept(locals(), ())\n"
    assert _guard_scales(ast.parse(src).body[0]) is None, "a MIXED body (a guard then a hamlet check) admits every scale"  # type: ignore[arg-type]
