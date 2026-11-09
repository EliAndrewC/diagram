"""The Python callers' door to the delta in the Rust gate (feature 449 T063 slice 2): `rust/gate/src/delta.rs` holds the one list of engine
paths, the delta and the engine key. This module holds no list, no git call and no hash, only the `Delta` type `decision.py` takes, until
T064 ports that and T071 the incremental gate. Each call is one process; a caller with many paths passes them all to `engine_paths` (FR-006)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

GATE = Path(__file__).resolve().parents[3] / "scripts" / "gates" / "l7r-gate.sh"


def gate(root: Path, *args: str, stdin: str = "") -> str:
    """The binary's stdout, run in `root`; a failure raises, so a caller never reads a missing answer as an empty one."""
    return subprocess.run([str(GATE), *args], cwd=root, input=stdin, capture_output=True, text=True, check=True).stdout


def engine_paths(root: Path, paths: list[str]) -> list[str]:
    """Those of `paths` that are engine code, by the one list, in one process."""
    return gate(root, "delta", "engine-paths", stdin="".join(f"{p}\n" for p in paths)).splitlines()


@dataclass(frozen=True)
class Delta:
    base: str
    files: tuple[str, ...]
    engine: tuple[str, ...]

    @property
    def route(self) -> str:
        return "GATED" if self.engine else "DIRECT"

    @property
    def reason(self) -> str:
        if not self.files:
            return "no commits of our own since main - nothing to push"
        if self.engine:
            shown = ", ".join(self.engine[:4]) + (f" (+{len(self.engine) - 4} more)" if len(self.engine) > 4 else "")
            return f"{len(self.engine)} engine path(s) in our delta: {shown}"
        return f"{len(self.files)} file(s) changed, none of them diagram engine code - docs, specs or config only"


def compute_delta(root: Path, base_ref: str = "origin/main") -> Delta:
    """The files our own commits changed since we diverged from `base_ref`."""
    got = json.loads(gate(root, "delta", "compute", base_ref))
    return Delta(base=got["base"], files=tuple(got["files"]), engine=tuple(got["engine"]))


def engine_key(root: Path, tree: str) -> str:
    """The verification key of a tree or commit."""
    return gate(root, "delta", "key", tree).strip()


def engine_key_worktree(root: Path) -> str:
    """The verification key of the working tree."""
    return gate(root, "delta", "key", "worktree").strip()
