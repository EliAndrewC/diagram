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

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

_OPEN = re.compile(r"^\s*- \[ \] (T\d+[^\n]{0,80})", re.M)


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
            return f"feature {self.name!r} has no specs/{self.name}/ directory with a tasks.md"
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
    open_tasks = tuple(m.group(1).strip() for m in _OPEN.finditer(tasks.read_text(encoding="utf-8")))
    faithful = spec.is_file() and "FAITHFUL" in spec.read_text(encoding="utf-8")
    return FeatureStatus(name=name, exists=True, faithful=faithful, open_tasks=open_tasks)
