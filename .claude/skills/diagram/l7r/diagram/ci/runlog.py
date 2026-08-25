"""The remote run-log entry (FR-020) and month-to-date spend, from LOCAL records only.

Same directory and shape as the Makefile's `LOGRUN` entries (`dev/run-log/<utc>-<pid>.json`), plus
`where`, `build_id`, `minutes` and `cost_usd`. Month-to-date is summed from these files - never
from Cost Explorer, which costs money per call (plan, design note 3) - and cross-checked once
against the console (SC-005).
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from l7r.diagram.ci import config

RUN_LOG = "dev/run-log"


def _short_head(skill: Path) -> str:
    out = subprocess.run(["git", "-C", str(skill), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip()


def write_remote(skill: Path, target: str, scope: str, seconds: int, result: str, build_id: str, minutes: float, reason: str = "") -> Path:
    os.makedirs(skill / RUN_LOG, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{time.time_ns() // 1000 % 1000000:06d}"
    entry = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target": target,
        "scope": scope,
        "seconds": int(seconds),
        "result": result,
        "commit": _short_head(skill),
        "where": "codebuild",
        "build_id": build_id,
        "minutes": round(minutes, 2),
        "cost_usd": round(minutes * config.RATE_PER_MIN, 4),
        "reason": reason,
    }
    path = skill / RUN_LOG / f"{ts}-{os.getpid()}.json"
    path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    return path


def remote_entries(skill: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for f in sorted(glob.glob(str(skill / RUN_LOG / "*.json"))):
        try:
            r = json.loads(Path(f).read_text(encoding="utf-8"))
        except ValueError:
            continue
        if r.get("where") == "codebuild":
            rows.append(r)
    return rows


def month_to_date(skill: Path, now: str | None = None) -> float:
    month = (now or time.strftime("%Y-%m", time.gmtime()))[:7]
    return round(sum(float(r.get("cost_usd", 0.0)) for r in remote_entries(skill) if str(r.get("utc", "")).startswith(month)), 4)


def remote_spend_report(skill: Path) -> str:
    rows = remote_entries(skill)
    lines = ["\033[1mRemote spend\033[0m (dev/run-log/, where=codebuild)"]
    for r in rows[-15:]:
        lines.append(f"  {r['utc']}  {str(r['scope']):<9} {float(r['minutes']):>5.1f} min  ${float(r['cost_usd']):>5.2f}  {str(r['result']):<24} {r['build_id']}")
    if not rows:
        lines.append("  (no remote runs yet)")
    lines.append(f"  month-to-date: ${month_to_date(skill):.2f} over {sum(1 for r in rows if str(r.get('utc', '')).startswith(time.strftime('%Y-%m', time.gmtime())))} run(s) this month")
    return "\n".join(lines)
