"""The Python callers' door to the claims tools in Rust (feature 449 T82, `ask:449-T82-claims`, on the `plan_door` pattern): one
`l7r-gate claims-door` process a run, each function a forwarder and never a fallback, its verbs in order so a read follows its own write
(FR-006). Its caller: `impl_check.py`, named at the phase-3 close; the verbs only `land.py` and `replay_owing.py` asked left with their
Rust ports (feature 449 T121). Deleted with its last caller; named at the phase-3 close if still present.

A row of `current` is an attribute object with the fields its callers read (`claim.pointers`, `unit.path`, ...), every one computed in
Rust; nothing it returns is handed back to the Rust mutated."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"

_door: subprocess.Popen[str] | None = None
_door_env: tuple[str | None, ...] = ()
#: what the door reads from its environment: a changed one is a fresh door
_READ_FROM_ENV = ("L7R_GATE_TREE", "L7R_CACHE_OFF", "HOME")


def _ask(verb: str, *args: Any) -> Any:  # noqa: ANN401 - the verb's JSON
    global _door, _door_env  # noqa: PLW0603 - one process a run (FR-006), but a changed environment is a new one
    wanted = tuple(os.environ.get(k) for k in _READ_FROM_ENV)
    if _door is not None and wanted != _door_env:
        assert _door.stdin is not None
        _door.stdin.close()
        _door.wait()
        _door = None
    if _door is None:
        _door_env = wanted
        _door = subprocess.Popen([str(GATE), "claims-door"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    assert _door.stdin is not None and _door.stdout is not None
    _door.stdin.write(json.dumps({"verb": verb, "args": list(args)}) + "\n")
    _door.stdin.flush()
    line = _door.stdout.readline()
    if not line:
        raise ValueError(f"claims-door: no answer to {verb}")
    said = json.loads(line)
    if "error" in said:
        raise ValueError(said["error"])
    return said["ok"]


def _row(d: dict[str, Any]) -> SimpleNamespace:
    claim = SimpleNamespace(**{**d["claim"], "pointers": tuple(d["claim"]["pointers"])})
    return SimpleNamespace(key=d["key"], uid=d["uid"], code=d["code"], research=d["research"], claim=claim, unit=SimpleNamespace(**d["unit"]))


def __getattr__(name: str) -> Any:  # noqa: ANN401 - `QUESTIONS`, `INDEX`, `STORE`, asked when read
    if name in ("QUESTIONS", "INDEX", "STORE"):
        return _ask("constants")[name]
    raise AttributeError(name)


def current(root: pathlib.Path) -> dict[str, SimpleNamespace]:
    """key -> row for every claim in scope at `root`."""
    return {k: _row(v) for k, v in _ask("current", str(root)).items()}


def owed(root: pathlib.Path, index: Mapping[str, Any], store: Mapping[str, Any]) -> list[tuple[str, str]]:
    """(key, why) for every claim owed a check at `root`, its questions under `root/research/questions`."""
    return [(k, why) for k, why in _ask("owed", str(root), dict(index), dict(store))]


def load_index(path: pathlib.Path) -> dict[str, dict[str, Any]]:
    return _ask("load_index", str(path))


def load_store(path: pathlib.Path) -> dict[str, list[str]]:
    return _ask("load_store", str(path))
