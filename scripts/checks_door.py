"""The Python callers' door to the check state and the round arbiter in Rust (feature 449 T86, `ask:449-T86-door`): one `l7r-gate checks-door` process a run, its verbs in order so a read follows its own write (FR-006), each
function a forwarder and never a fallback. Writes - `record_answer`, `trip`, `keep_batches` - are the same Rust functions, under the same locks, as the guards'. Deleted with its last caller; named at the phase-3 close if still present."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from collections.abc import Iterable, Mapping
from typing import Any

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"

_door: subprocess.Popen[str] | None = None
_door_env: tuple[str | None, ...] = ()
#: what the door reads from its environment: a caller that changes one of them mid-run (`land.py` exports SPECIFY_FEATURE) gets a fresh door
_READ_FROM_ENV = ("L7R_FEATURE_DIRECTORY", "SPECIFY_FEATURE", "RECORD_CHECKS_DIR", "HOME", "L7R_GATE_TREE", "GUARD_LOG_DIR")


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
        _door = subprocess.Popen([str(GATE), "checks-door"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    assert _door.stdin is not None and _door.stdout is not None
    _door.stdin.write(json.dumps({"verb": verb, "args": list(args)}) + "\n")
    _door.stdin.flush()
    line = _door.stdout.readline()
    if not line:
        raise ValueError(f"checks-door: no answer to {verb}")
    said = json.loads(line)
    if "error" in said:
        raise ValueError(said["error"])
    return said["ok"]


def _path(named: str | None) -> pathlib.Path | None:
    return pathlib.Path(named) if named else None


def __getattr__(name: str) -> Any:  # noqa: ANN401 - `ROUND_CAP` and `PAGE_CHECKS`, asked when read
    if name in ("ROUND_CAP", "PAGE_CHECKS"):
        return _ask(name)
    raise AttributeError(name)


def load(path: pathlib.Path) -> dict[str, Any]:
    return _ask("load", str(path))


def state_path(cwd: str) -> pathlib.Path | None:
    return _path(_ask("state_path", cwd))


def _blocks(reply: str) -> list[tuple[str, str, str]]:
    return [(p, o, n) for p, o, n in _ask("_blocks", reply)]


def _reply_of(transcript: str, last: str) -> str:
    return _ask("_reply_of", transcript, last)


def subject_of_path(path: str) -> str:
    return _ask("subject_of_path", path)


def notes_of_manifest(text: str) -> set[str]:
    return set(_ask("notes_of_manifest", text))


def subjects_of_manifest(text: str) -> list[str]:
    return _ask("subjects_of_manifest", text)


def feature_dir(root: pathlib.Path, trigger: str = "") -> pathlib.Path | None:
    return _path(_ask("feature_dir", str(root), trigger))


def unit_of(trigger: str) -> str:
    return _ask("unit_of", trigger)


def owed(root: pathlib.Path) -> dict[str, dict[str, Any]]:
    return _ask("owed", str(root))


def aside(root: pathlib.Path) -> list[str]:
    return _ask("aside", str(root))


def rulings(root: pathlib.Path, trigger: str = "") -> dict[str, dict[str, Any]]:
    return _ask("rulings", str(root), trigger)


def _round_no(trigger: str) -> int:
    return _ask("_round_no", trigger)


def batch_triggers(root: pathlib.Path, extra: Iterable[str] = ()) -> list[str]:
    return _ask("batch_triggers", str(root), list(extra))


def reversal(events: list[Mapping[str, Any]], path: str, old: str, new: str) -> bool:
    return _ask("reversal", events, path, old, new)


def fix_hold(d: pathlib.Path) -> str:
    return _ask("fix_hold", str(d))


def record_answer(root: pathlib.Path, check: str, slugs: list[str]) -> None:
    _ask("record_answer", str(root), check, slugs)


def trip(root: pathlib.Path, trigger: str, kind: str, unit: str, detail: str, now: float | None = None, review: str = "") -> bool:  # noqa: PLR0913 - the verb's words
    return _ask("trip", str(root), trigger, kind, unit, detail, now, review)


def keep_batches(root: pathlib.Path, batches: Mapping[str, list[str]]) -> None:
    _ask("keep_batches", str(root), dict(batches))
