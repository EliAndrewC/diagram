"""The rebuilt phases' extension module, built and imported (feature 444 D8).

WHY: a stage rebuilt in Rust is a thin Python function calling `l7r_phases` (FR-010). The module is built from `rust/phases/` by
`scripts/gates/rust_checks.py build` into the gitignored `.rust-ext/`, keyed to the crate's sources, so this loader builds it when
that key moved (a fresh clone, a gate's worktree, a Rust edit) and then imports it: every path that rolls a map - `make map`, the
gate, a cohort - gets the extension its sources say, and the generation key already holds those sources (`gencache.rust_sources`).

Research:
    the extension's loading - NONE: build machinery, no claim about a map
"""

from __future__ import annotations

import functools
import importlib
import importlib.util
import os
import pathlib
import subprocess
import sys
from types import ModuleType

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXT = ROOT / ".rust-ext"
CRATE = ROOT / "rust" / "phases" / "Cargo.toml"


def _stale(root: pathlib.Path = ROOT) -> bool:
    """Has the crate's source id moved since `.rust-ext/` was built (or was it never built)?"""
    spec = importlib.util.spec_from_file_location("rust_checks", root / "scripts" / "gates" / "rust_checks.py")  # the one definition of the build's key
    assert spec and spec.loader
    rust_checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rust_checks)
    mark = root / ".rust-ext" / "l7r_phases.stamp"
    return not mark.is_file() or mark.read_text(encoding="utf-8").strip() != rust_checks.stamp(root / "rust" / "phases" / "Cargo.toml")


@functools.cache
def phases(root: pathlib.Path = ROOT) -> ModuleType:
    """`l7r_phases`, built first if its sources moved. A failed build is loud: no stage falls back to an older module.
    `L7R_RUST_EXT` names another built folder instead, never rebuilt here - FR-012's roll with the `counters` feature off."""
    other = os.environ.get("L7R_RUST_EXT")
    if other:
        sys.path.insert(0, other)
        return importlib.import_module("l7r_phases")
    if _stale(root):
        r = subprocess.run([sys.executable, str(root / "scripts" / "gates" / "rust_checks.py"), "build"], capture_output=True, text=True, cwd=root, check=False)
        if r.returncode != 0:
            raise RuntimeError(f"the Rust phases did not build (rust_checks.py build):\n{r.stdout}{r.stderr}")
    if str(root / ".rust-ext") not in sys.path:
        sys.path.insert(0, str(root / ".rust-ext"))
    return importlib.import_module("l7r_phases")
