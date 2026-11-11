"""The step-back bundle's one door to the reviews' port in Rust (feature 449 T89, `ask:449-T89-reviews`): `l7r-gate reviews-door`, one process
a run, three verbs - `gitdir`, `git` and `checkpoint_state` - each function a forwarder and never a fallback. It leaves when T83 ports
`stepback_bundle.py`, its one caller; named at the phase-3 close if still present."""

from __future__ import annotations

import json
import pathlib
import subprocess
from typing import Any

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"

_door: subprocess.Popen[str] | None = None


def _ask(verb: str, *args: Any) -> Any:  # noqa: ANN401 - the verb's JSON
    global _door  # noqa: PLW0603 - one process a run (FR-006)
    if _door is None:
        _door = subprocess.Popen([str(GATE), "reviews-door"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    assert _door.stdin is not None and _door.stdout is not None
    _door.stdin.write(json.dumps({"verb": verb, "args": list(args)}) + "\n")
    _door.stdin.flush()
    line = _door.stdout.readline()
    if not line:
        raise ValueError(f"reviews-door: no answer to {verb}")
    said = json.loads(line)
    if "error" in said:
        raise ValueError(said["error"])
    return said["ok"]


def gitdir(root: pathlib.Path) -> pathlib.Path | None:
    g = _ask("gitdir", str(root))
    return pathlib.Path(g) if g else None


def git(root: pathlib.Path, *args: str) -> str | None:
    return _ask("git", str(root), *args)


def checkpoint_state(root: pathlib.Path) -> dict[str, Any]:
    return _ask("checkpoint_state", str(root))
