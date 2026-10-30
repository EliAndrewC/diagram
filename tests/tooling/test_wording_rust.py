"""`scripts/gates/wording.py` on the Rust phases (feature 444 T17, `dev/rust-tooling.md` "a wording-only change"): a wording-only
task may change a `.py` file's comments and docstrings, never what runs - and a `.rs` file is code, so ANY change to one, a comment
included, is a change in what runs until the code id reads Rust's token stream (that row's own proof)."""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "gates"))
import wording  # noqa: E402

pytestmark = pytest.mark.tooling


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)


def test_a_rust_file_changed_even_in_a_comment_is_a_change_in_what_runs(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    (root / "rust" / "phases" / "src").mkdir(parents=True)
    rs = root / "rust" / "phases" / "src" / "field.rs"
    rs.write_text("/// The field.\npub fn field() {}\n")
    _git(root.parent, "init", "-q", str(root))
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "base", "--date", "2026-01-01T00:00:00")
    rs.write_text("/// The comb field.\npub fn field() {}\n")
    _git(root, "commit", "-qam", "a doc comment only")
    assert wording.changed_in_what_runs(root, "2026-06-01T00:00:00Z") == ["rust/phases/src/field.rs"]
