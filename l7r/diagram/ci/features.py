"""FR-011: the gated route requires a NAMED, COMPLETE spec-kit feature.

The GM's fourth request: *"if there is a SpecKit feature, then I think our tooling should require
that when we merge something in ... we say what the feature is, and then an automated tooling check
confirms that the feature is indeed complete ... Anything involving the diagram skill is
sufficiently complicated to require a spec kid feature."* So on the gated route there is no "not
part of a feature" declaration: the feature is named the way spec-kit already names it
(`SPECIFY_FEATURE`, or `.specify/feature.json`), its `tasks.md` must have no open box, and its
`spec.md` must carry a FAITHFUL verdict. The direct route (no engine code) needs none of this.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_OPEN = re.compile(r"^\s*- \[ \] (T\d+[^\n]*)", re.M)
#: the repository whose `scripts/speckit-todo.py` states which open box holds a landing - this package's own
REPO = Path(__file__).resolve().parents[3]


def holding(d: Path) -> list[str]:
    """The open boxes of `d/tasks.md` that hold the landing - `speckit-todo.py --holding`'s ONE rule, loaded by path (a script,
    not a package; as `state.py` loads gate-stamp): a `[lands-open]` box the tooling or a reviewed plan put there does not
    hold it (feature 375, plan D18). Batch 2 of 375 was the first gated landing to meet one, and this check refused it while
    the push's own open-task test let it through: two copies of one rule had drifted apart."""
    spec = importlib.util.spec_from_file_location("speckit_todo", REPO / "scripts" / "speckit-todo.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["speckit_todo"] = mod
    spec.loader.exec_module(mod)
    return [str(line) for line in mod.holding(d)]


@dataclass(frozen=True)
class FeatureStatus:
    name: str | None
    exists: bool = False
    faithful: bool = False
    open_tasks: tuple[str, ...] = field(default_factory=tuple)

    @property
    def complete(self) -> bool:
        return self.exists and self.faithful and not self.open_tasks

    @property
    def why(self) -> str:
        if not self.name:
            return "no spec-kit feature is named (export SPECIFY_FEATURE=NNN-slug, or .specify/feature.json) - diagram engine work always has one"
        if not self.exists:
            # `make claim` points .specify/feature.json at a number claimed only to FILE a feature (2026-10-09, 370)
            return (
                f"feature {self.name!r} has no specs/{self.name}/ directory with a tasks.md - if it is only filed, name the"
                " feature this work belongs to: SPECIFY_FEATURE=<NNN-slug> scripts/sync-with-main.sh done"
            )
        problems = []
        if not self.faithful:
            problems.append("spec.md carries no FAITHFUL verdict (constitution XVI)")
        if self.open_tasks:
            shown = "; ".join(self.open_tasks[:3]) + (f"; +{len(self.open_tasks) - 3} more" if len(self.open_tasks) > 3 else "")
            problems.append(f"{len(self.open_tasks)} open task(s) in tasks.md: {shown}")
        if problems:
            return f"feature {self.name}: " + " | ".join(problems)
        return f"feature {self.name} is complete: every task ticked, spec FAITHFUL"


def active_feature(root: Path) -> str | None:
    env = os.environ.get("SPECIFY_FEATURE", "").strip()
    if env:
        return env
    fj = root / ".specify" / "feature.json"
    if fj.is_file():
        try:
            fd = str(json.loads(fj.read_text(encoding="utf-8")).get("feature_directory", ""))
        except ValueError, OSError:
            return None
        return fd.rstrip("/").split("/")[-1] or None
    return None


def feature_status(root: Path, name: str | None) -> FeatureStatus:
    if not name:
        return FeatureStatus(name=None)
    d = root / "specs" / name
    tasks, spec = d / "tasks.md", d / "spec.md"
    if not tasks.is_file():
        return FeatureStatus(name=name, exists=False)
    held = holding(d)
    open_tasks = tuple(t[:80] for m in _OPEN.finditer(tasks.read_text(encoding="utf-8")) if any(h.startswith(t := m.group(1).strip()) for h in held))
    faithful = (spec.is_file() and "FAITHFUL" in spec.read_text(encoding="utf-8")) or spec_accepted(d, name)
    return FeatureStatus(name=name, exists=True, faithful=faithful, open_tasks=open_tasks)


def spec_accepted(d: Path, name: str) -> bool:
    """Did the round arbiter ACCEPT the spec at its review's round cap (feature 379: "accept lets the spec stand as the last round
    left it - the review gate takes the ruling as its verdict")? Read from the feature's own `arbiter.jsonl`. Feature 387 found the
    merge's feature-complete check asking only for the word FAITHFUL in `spec.md`, so a spec the arbiter accepted was refused here
    while the review gate let it through - two readings of one verdict drifted apart, as 375 batch 2 found of the open tasks."""
    log = d / "arbiter.jsonl"
    if not log.is_file():
        return False
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if str(r.get("trigger", "")).startswith(f"round:spec-fidelity|{name}#") and r.get("ruling") == "accept":
            return True
    return False
