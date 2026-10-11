"""`make test-file` with no FILE refuses, naming the variable (2026-10-10: `F=` was typed, FILE stayed empty and pytest
collected the whole suite while the containers were near their memory cap)."""

from __future__ import annotations

import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_an_empty_file_refuses_with_the_variable_s_name() -> None:
    # NEVER inherit the outer make's MAKEFLAGS: run under `make test-file FILE=<this file>`, the inner make took that FILE,
    # re-ran this test, and recursed until memguard killed 385 processes (2026-10-10). `FILE=` pins it empty besides.
    env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "MAKEOVERRIDES", "FILE")}
    r = subprocess.run(["make", "-s", "-C", str(ROOT), "test-file", "F=tests/tooling", "FILE="], capture_output=True, text=True, check=False, env=env, timeout=60)
    assert r.returncode == 2
    assert "make test-file FILE=tests/<path>" in r.stderr and "the variable is FILE, not F" in r.stderr
