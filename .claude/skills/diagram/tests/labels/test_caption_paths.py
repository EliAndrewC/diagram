"""Every caption goes through the one placer, except the named exceptions (feature 266, FR-012, SC-002).

The GM, 2026-09-27: *"I also agree with one placer for all labels."* This test is what makes that hold for the next
caption someone writes: a hand-seated `self.label(x, y, ...)` or a raw `<text>` anywhere but the places below fails
here, naming itself. The exempt hand seats are spec D8 - the unscripted town, city and capital tiers, on no live map,
which go through the placer when their tier is scripted (`future-work/cities.md`).
"""

from __future__ import annotations

import ast
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SETTLEMENT = SKILL / "l7r" / "diagram" / "settlement"
COMPOUND = SKILL / "l7r" / "diagram" / "compound.py"

D8_HAND_SEATS = frozenset(
    {
        ("castle_civic.py", "castle"),
        ("castle_civic.py", "flower_field"),
        ("castle_civic.py", "forest_patch"),
        ("castle_civic.py", "hanko"),
        ("castle_civic.py", "martial_hall"),
        ("castle_civic.py", "ministry"),
        ("castle_civic.py", "wall"),
        ("city/civic.py", "governor_mansion"),
        ("city/moat.py", "sluice_gate"),
        ("city/walls.py", "_gate_caption"),
        ("city/waterfront.py", "log_boom"),
        ("civic_grounds/civic.py", "granary"),
        ("civic_grounds/funerary.py", "cemetery"),
        ("civic_grounds/funerary.py", "cremation_ground"),
        ("civic_grounds/funerary.py", "mausoleum"),
        ("civic_grounds/funerary.py", "ossuary"),
        ("civic_grounds/justice.py", "boundary_marker"),
        ("civic_grounds/justice.py", "execution_ground"),
        ("civic_grounds/justice.py", "punishment_spot"),
        ("civic_grounds/lodging.py", "flophouse"),
        ("civic_grounds/lodging.py", "flush_stable_yards"),
        ("fields/features.py", "crescent_pond"),
        ("land/dikes.py", "perimeter_dike"),
        ("shrines_wells/forest.py", "forest"),
        ("shrines_wells/shrines.py", "shrine_hall"),
        ("structures/compounds.py", "manor"),
        ("structures/fixtures/boards.py", "fire_tower"),
        ("structures/ground.py", "pasture"),
        ("structures/urban_fixtures.py", "drum_tower"),
        ("trades.py", "_trade_record"),
        ("trades.py", "border_line"),
        ("water_ways/lanes.py", "street"),
        ("water_ways/wards.py", "quarter"),
    }
)
"""Spec D8: the 33 functions whose 47 hand-seated calls stay until their tier is scripted. It only ever shrinks."""

PHASE_DRAWERS = frozenset({("structures/captions.py", "_draw_queued_label"), ("structures/captions.py", "_draw_seated_caption")})
"""The label phase's two drawers: one replays a D8 hand seat, the other draws what the placer chose."""

RAW_TEXT_SETTLEMENT = frozenset({("finish.py", "label"), ("finish.py", "title"), ("structures/captions.py", "_draw_seated_caption")})
"""Where the settlement engine may write `<text` itself: the caption primitive, the title placard (not a caption - it names
no feature), and the field-name markup the placer seats."""

RAW_TEXT_COMPOUND = {"plain": 1, "emit_svg": 2}
"""`compound.py`'s own `<text`: the title and draft note (`plain`) and the two scale-bar lines. Every caption it draws is
written by `labels.svg.caption_svg` from a placement."""


def _walk(src: str, want) -> dict[str, int]:
    """Count, per enclosing function, the nodes `want` accepts."""
    out: dict[str, int] = {}

    def visit(n: ast.AST, fn: str) -> None:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = n.name
        if want(n):
            out[fn] = out.get(fn, 0) + 1
        for c in ast.iter_child_nodes(n):
            visit(c, fn)

    visit(ast.parse(src), "<module>")
    return out


def _is_self_label(n: ast.AST) -> bool:
    return isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "label" and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"


def _is_raw_text(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) and isinstance(n.value, str) and "<text" in n.value


def hand_seats(root: Path = SETTLEMENT) -> set[tuple[str, str]]:
    return {(str(f.relative_to(root)), fn) for f in root.rglob("*.py") for fn in _walk(f.read_text(), _is_self_label)}


def raw_texts(root: Path = SETTLEMENT) -> set[tuple[str, str]]:
    return {(str(f.relative_to(root)), fn) for f in root.rglob("*.py") for fn in _walk(f.read_text(), _is_raw_text)}


def test_no_caption_is_hand_seated_outside_the_named_exceptions() -> None:
    found = hand_seats()
    assert found, "the walk found no label call at all - it is looking in the wrong place"
    stray = found - D8_HAND_SEATS - PHASE_DRAWERS
    assert not stray, f"a caption seated by hand outside the placer (feature 266 FR-012) - seat it with `seat_caption`/the placer: {sorted(stray)}"
    assert found >= D8_HAND_SEATS, f"a D8 call site is gone - take it off the list, which only shrinks: {sorted(D8_HAND_SEATS - found)}"


def test_no_raw_text_is_written_outside_the_placer() -> None:
    found = raw_texts()
    assert found, "the walk found no <text at all"
    assert found == RAW_TEXT_SETTLEMENT, f"a caption written as raw <text outside the placer (feature 266 FR-012): {sorted(found - RAW_TEXT_SETTLEMENT)}"
    assert _walk(COMPOUND.read_text(), _is_raw_text) == RAW_TEXT_COMPOUND, "compound.py writes a caption outside the placer"


def test_the_path_test_fires_on_a_planted_call(tmp_path: Path) -> None:
    """Shown red: a planted hand seat and a planted raw `<text` are each caught."""
    (tmp_path / "planted.py").write_text('def new_feature(self):\n    self.label(1, 2, "x")\n    return f\'<text x="1">x</text>\'\n')
    assert hand_seats(tmp_path) == {("planted.py", "new_feature")}
    assert raw_texts(tmp_path) == {("planted.py", "new_feature")}
