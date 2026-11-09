"""The Python callers' door to the plan gate in Rust (feature 449 T066, `ask:449-T066-scope`): each function one `l7r-gate plan` call, a
forwarder and never a fallback, until its last caller is ported (phase 3)."""

from __future__ import annotations

import functools
import json
import os
import pathlib
import subprocess
from typing import Any

GATE = pathlib.Path(__file__).resolve().parent / "gates" / "l7r-gate.sh"


def _run(*args: str, stdin: str | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(GATE), "plan", *args], input=stdin, capture_output=True, text=True, check=False, env=env)


def _ask(*args: str, stdin: str | None = None, env: dict[str, str] | None = None) -> Any:  # noqa: ANN401 - the verb's JSON
    done = _run("door", *args, stdin=stdin, env=env)
    if done.returncode == 2:
        raise PermissionError(done.stderr.strip())
    if done.returncode != 0:
        raise ValueError(done.stderr.strip())
    return json.loads(done.stdout)


@functools.lru_cache(maxsize=8)  # a loop over live holds asks one plan once (`ask:449-T066-scope` condition 4)
def task_sections(plan_text: str) -> dict[str, str]:
    return dict(_ask("task-sections", stdin=plan_text))


@functools.lru_cache(maxsize=8)
def blocks(plan_text: str) -> list[tuple[str, str, int]]:
    return [(k, b, at) for k, b, at in _ask("blocks", stdin=plan_text)]


def wording_only(section: str) -> bool:
    return bool(_ask("wording-only", stdin=section))


def active_task(root: pathlib.Path) -> tuple[pathlib.Path | None, str]:
    named, task = _ask("active-task", str(root))
    return (pathlib.Path(named) if named else None), str(task)


def touched_features(root: pathlib.Path, rng: str) -> list[str]:
    return list(_ask("touched-features", str(root), rng))


def tick_permitted(spec_dir: pathlib.Path, root: pathlib.Path, escape: str | None) -> tuple[bool, str]:
    env = {k: v for k, v in os.environ.items() if k != "PLAN_REVIEW_OK"}
    if escape:
        env["PLAN_REVIEW_OK"] = escape
    ok, message = _ask("tick-permitted", str(spec_dir), str(root), env=env)
    return bool(ok), str(message)


def archive(spec_dir: pathlib.Path) -> list[str]:
    return list(_ask("archive", str(spec_dir)))


def arbiter_accept(spec_dir: pathlib.Path, trigger: str) -> list[str]:
    return list(_ask("accept", str(spec_dir), trigger))


def resolve(feature: str, root: pathlib.Path) -> pathlib.Path | None:
    named = _ask("resolve", feature, str(root))
    return pathlib.Path(named) if named else None


def approach_refusal(spec_dir: pathlib.Path, root: pathlib.Path, task: str) -> str | None:
    return _ask("approach-refusal", str(spec_dir), str(root), task)


def approach_ruled(root: pathlib.Path, trigger: str) -> str | None:
    return _ask("approach-ruled", str(root), trigger)


def owe_in_flight(root: pathlib.Path, trigger: str, part: str) -> str:
    """Charge `trigger` to every in-flight task of the active feature; the messages ("" when no task is active)."""
    return subprocess.run([str(GATE), "plan", "approach", "owe-in-flight", trigger, part], cwd=root, capture_output=True, text=True, check=False).stdout.strip()
