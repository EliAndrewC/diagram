"""The edit helper, proven to fire (feature 236, FR-001 and FR-002).

The failure it exists to prevent is not hypothetical: three times in one day a patch script
accumulated its edits and wrote at the end, so a single stale anchor discarded the substantive edits
beside it, silently. Each rule here was written by breaking the corresponding rule in `_patch.py` and
watching a case go red - per-edit writes, the whitespace-insensitive anchor, the refusal to guess
between two matches, and the indent a mid-line match must keep.

No `tooling` marker: it calls functions over temporary files, it runs no make, git or subprocess.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("_patch", REPO / "scripts" / "_patch.py")
assert _spec and _spec.loader
patch = importlib.util.module_from_spec(_spec)
sys.modules["_patch"] = patch
_spec.loader.exec_module(patch)


def test_a_missing_anchor_loses_only_its_own_edit(tmp_path: pathlib.Path) -> None:
    """SC-001: three edits, the second anchor gone; the first and third still land."""
    f = tmp_path / "spec.md"
    f.write_text("alpha one\nbeta two\ngamma three\n")
    report, skipped = patch.apply_edits(
        f, [("alpha one", "ALPHA"), ("a sentence somebody reflowed", "X"), ("gamma three", "GAMMA")]
    )
    assert f.read_text() == "ALPHA\nbeta two\nGAMMA\n"
    assert skipped == 1
    assert [line.split(":")[0] for line in report] == ["applied", "SKIPPED (0 matches)", "applied"]


def test_the_report_names_the_anchor_that_missed(tmp_path: pathlib.Path) -> None:
    """A skip nobody can read is the silent loss again, one step removed."""
    f = tmp_path / "spec.md"
    f.write_text("only this\n")
    report, _ = patch.apply_edits(f, [("a sentence somebody reflowed", "X")])
    assert "a sentence somebody reflowed" in report[0]


def test_an_anchor_matches_across_a_line_wrap(tmp_path: pathlib.Path) -> None:
    """FR-002, measured: four of six recorded misses were an anchor spanning a wrap (R7)."""
    f = tmp_path / "spec.md"
    f.write_text("the sections and keys the new text\nwas written from stay put\n")
    _, skipped = patch.apply_edits(f, [("keys the new text was written from", "keys it came from")])
    assert skipped == 0
    assert "keys it came from" in f.read_text()


def test_an_anchor_that_matches_twice_is_skipped_rather_than_guessed(tmp_path: pathlib.Path) -> None:
    """Which of the two the caller meant is exactly what the script cannot know."""
    f = tmp_path / "spec.md"
    f.write_text("same line\nsame line\n")
    report, skipped = patch.apply_edits(f, [("same line", "different")])
    assert skipped == 1
    assert f.read_text() == "same line\nsame line\n"
    assert "2 matches" in report[0]


def test_a_mid_line_match_keeps_the_block_indent(tmp_path: pathlib.Path) -> None:
    """The recorded indent bug: continuation lines went flush against the margin."""
    f = tmp_path / "spec.md"
    f.write_text("    - a point that needs more\n")
    patch.apply_edits(f, [("a point that needs more", "a point\nand another")])
    assert f.read_text() == "    - a point\n    and another\n"


def test_replacement_lines_that_carry_their_own_indent_are_left_alone(tmp_path: pathlib.Path) -> None:
    """A caller that has said what it wants is not second-guessed."""
    f = tmp_path / "spec.md"
    f.write_text("  x: here\n")
    patch.apply_edits(f, [("here", "here\n      deeper")])
    assert f.read_text() == "  x: here\n      deeper\n"


def test_an_anchor_is_matched_literally_apart_from_its_whitespace(tmp_path: pathlib.Path) -> None:
    """Loosening whitespace must not turn `(a)` or `.` into a pattern."""
    f = tmp_path / "spec.md"
    f.write_text("call f(x) or anything\n")
    _, skipped = patch.apply_edits(f, [("f(.)", "g")])
    assert skipped == 1, "regex metacharacters in an anchor are literal text"
    _, skipped = patch.apply_edits(f, [("f(x)", "g(y)")])
    assert skipped == 0 and "g(y)" in f.read_text()


def test_selftest_passes() -> None:
    patch.selftest()
