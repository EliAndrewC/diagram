"""`scripts/format-changed.sh` (feature 385 T68, plan D87): `make test-file` formats the Python the clone changed, and only that."""

from __future__ import annotations

import pathlib
import subprocess

import pytest

from tests._scripts import script

pytestmark = pytest.mark.tooling
MESSY = "x  =  1\n"


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True)


def test_the_changed_python_is_formatted_and_the_untouched_is_not(tmp_path: pathlib.Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "old.py").write_text(MESSY)  # messy at the base: nobody touched it
    (tmp_path / "edited.py").write_text("y = 2\n")
    (tmp_path / "gone.py").write_text("z = 3\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "base")
    (tmp_path / "edited.py").write_text(MESSY)
    (tmp_path / "new.py").write_text(MESSY)
    (tmp_path / "gone.py").unlink()
    out = subprocess.run([str(script("format-changed.sh"))], cwd=tmp_path, capture_output=True, text=True, check=True).stdout
    assert (tmp_path / "edited.py").read_text() == "x = 1\n" and (tmp_path / "new.py").read_text() == "x = 1\n"
    assert (tmp_path / "old.py").read_text() == MESSY
    assert out.startswith("test-file: formatted ") and "edited.py" in out and "new.py" in out
    again = subprocess.run([str(script("format-changed.sh"))], cwd=tmp_path, capture_output=True, text=True, check=True).stdout
    assert again == "", "nothing left to format: silent"
