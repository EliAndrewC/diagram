"""`hamletgen/phases_ext.py` (feature 444 D8): the Rust phases' module loaded from another built folder when `L7R_RUST_EXT` names
one, built first when its stamp is stale, and a failed build loud - never a fall back to an older module."""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from l7r.diagram.hamletgen import phases_ext


@pytest.fixture(autouse=True)
def _loaded() -> None:
    """The real module imported once first, as any roll imports it (its stamp current, so no build): the paths below then
    import the module already loaded rather than a second build of it."""
    phases_ext.phases()


def test_another_built_folder_is_put_first_and_never_rebuilt(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L7R_RUST_EXT", str(tmp_path))
    monkeypatch.setattr(phases_ext, "_stale", lambda root=None: pytest.fail("an override is never rebuilt"))
    monkeypatch.setattr(sys, "path", list(sys.path))
    assert phases_ext.phases.__wrapped__(tmp_path).__name__ == "l7r_phases"
    assert sys.path[0] == str(tmp_path)


def test_a_stale_stamp_builds_first_and_a_failed_build_is_loud(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_RUST_EXT", raising=False)
    monkeypatch.setattr(phases_ext, "_stale", lambda root: True)
    monkeypatch.setattr(sys, "path", list(sys.path))
    ran: list[list[str]] = []

    def build(cmd: list[str], **_kw: object) -> subprocess.CompletedProcess[str]:
        ran.append(cmd)
        return subprocess.CompletedProcess(cmd, 0 if len(ran) == 1 else 1, "", "maturin said no")

    monkeypatch.setattr(phases_ext.subprocess, "run", build)
    assert phases_ext.phases.__wrapped__(tmp_path).__name__ == "l7r_phases"
    assert ran[0][-1] == "build" and str(tmp_path / ".rust-ext") in sys.path
    with pytest.raises(RuntimeError, match="did not build"):
        phases_ext.phases.__wrapped__(tmp_path)
