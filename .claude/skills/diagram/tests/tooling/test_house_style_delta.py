"""The house-style DELTA scan, proven to fire (feature 236, the GM's item 4, FR-008 to FR-008c).

The measurement behind the scope is in `specs/236-catch-mistakes-early-and-cheaply/research.md` R4:
192 pre-existing lines in 83 files carry one of these words, so a whole-tree check could not have
landed. What this must catch is what THIS change wrote, including into a file git has never seen -
which is where the motivating failures were.

`tooling`: it builds real git trees and runs git.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

pytestmark = pytest.mark.tooling

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("check_house_style_delta", REPO / "scripts" / "check-house-style-delta.py")
assert _spec and _spec.loader
chk = importlib.util.module_from_spec(_spec)
sys.modules["check_house_style_delta"] = chk
_spec.loader.exec_module(chk)


def _tree(tmp_path: pathlib.Path, base: dict[str, str]) -> pathlib.Path:
    root = tmp_path / "repo"
    root.mkdir()
    for name, body in base.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "x@y"], ["config", "user.name", "x"], ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    subprocess.run(["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    return root


def _write(root: pathlib.Path, name: str, body: str) -> None:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)


def test_a_word_this_change_wrote_is_named_with_its_line(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path, {"docs/a.md": "the color is gray\n"})
    _write(root, "docs/a.md", "the color is gray\nthe centre of the map\n")
    got = chk.findings(root)
    assert got and "docs/a.md:2" in got[0] and "centre" in got[0]


def test_a_pre_existing_line_is_not_in_the_delta(tmp_path: pathlib.Path) -> None:
    """R4's 192 ledgered lines: sweeping them is its own work and wants the GM (spec Out of scope)."""
    root = _tree(tmp_path, {"docs/a.md": "the old colour stays\n"})
    _write(root, "docs/a.md", "the old colour stays\nan added american line\n")
    assert chk.findings(root) == []


def test_an_untracked_file_is_scanned(tmp_path: pathlib.Path) -> None:
    """FR-008: the motivating failures were NEW files written through heredocs."""
    root = _tree(tmp_path, {"docs/a.md": "fine\n"})
    _write(root, "docs/new.md", "a fresh behaviour here\n")
    assert any("docs/new.md:1" in x for x in chk.findings(root))


def test_a_line_inside_a_multi_line_quotation_is_exempt(tmp_path: pathlib.Path) -> None:
    """FR-008a: the changed line carries no opening marker of its own, so the FILE decides."""
    root = _tree(tmp_path, {"research/a.html": "<blockquote>\nfirst line\n</blockquote>\n"})
    _write(root, "research/a.html", "<blockquote>\nfirst line\nthe colour of the sky\n</blockquote>\n")
    assert chk.findings(root) == []


def test_a_code_span_names_the_word_rather_than_using_it(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path, {"docs/a.md": "fine\n"})
    _write(root, "docs/a.md", "fine\nnever write `colour` in prose\n")
    assert chk.findings(root) == []


def test_a_moved_line_is_not_flagged(tmp_path: pathlib.Path) -> None:
    """FR-008b / D7: a 1,000-line-gate split moves content without authoring it."""
    root = _tree(tmp_path, {"big.py": "x = 1\nLABEL = 'the colour knob'\ny = 2\n"})
    _write(root, "big.py", "x = 1\ny = 2\n")
    _write(root, "part.py", "LABEL = 'the colour knob'\n")
    assert chk.findings(root) == []


def test_a_changed_line_owes_the_fix_even_where_a_moved_one_does_not(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path, {"big.py": "LABEL = 'the colour knob'\n"})
    _write(root, "big.py", "LABEL = 'the colour knob and its neighbour'\n")
    assert any("big.py:1" in x for x in chk.findings(root))


def test_the_gm_s_verbatim_request_is_never_flagged(tmp_path: pathlib.Path) -> None:
    root = _tree(tmp_path, {"docs/a.md": "fine\n"})
    _write(root, "specs/236-x/request.md", "the GM wrote colour here\n")
    assert chk.findings(root) == []


def test_a_fixture_is_a_verbatim_record(tmp_path: pathlib.Path) -> None:
    """A recorded corpus of real commands carries the words by necessity; correcting it falsifies it."""
    root = _tree(tmp_path, {"docs/a.md": "fine\n"})
    _write(root, "scripts/fixtures/corpus.json", '{"command": "sed -i s/centre/center/ docs/a.md"}\n')
    assert chk.findings(root) == []


def test_the_word_list_is_the_hook_s_own(tmp_path: pathlib.Path) -> None:
    """One list, read from the hook: a copy drifts, and silently in the permissive direction."""
    words = chk.brit_words()
    hook = (REPO / "scripts" / "house-style-hooks.sh").read_text()
    for w in words:
        assert f'"{w}"' in hook
    assert len(words) > 40


def test_a_moved_table_fails_loudly_rather_than_matching_nothing(tmp_path: pathlib.Path) -> None:
    """A stale reader that quietly returns an empty list would pass every check forever."""
    fake = tmp_path / "hook.sh"
    fake.write_text("# no table here\n")
    with pytest.raises(SystemExit):
        chk.brit_words(fake)


def test_selftest_passes() -> None:
    chk.selftest()
