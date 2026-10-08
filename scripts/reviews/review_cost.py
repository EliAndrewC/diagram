#!/usr/bin/env python3
"""What one review run COST, read off its transcript - the ledger's cost cells (feature 294, FR-010).

WHY (feature 294, GM 2026-10-01: the review's "time and tokens"; spec US7: the ledger measures every check by itself). The
ledger recorded wall time on 7 of 133 settlement-review rows and tokens on none (research R0), so "is it pulling its weight"
was an impression. A finished agent's transcript (`<project>/<session>/subagents/agent-<id>.jsonl`) carries every model
call's usage and every line's timestamp; this sums them, so a ledger row's cost is copied from a measurement, never typed.

A streamed reply is written as several lines carrying the SAME call's usage, the last with the whole output count, so each
call is counted once - its last line - by its `requestId` (its message id where a line has none).

Usage: review_cost.py --agent <id> [--root <~/.claude/projects>]
  prints the ledger's two cost cells: `<wall> s` and `<input>k in (<cache read>k cached) / <output>k out`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path.home() / ".claude" / "projects"


def transcript(agent: str, root: Path = DEFAULT_ROOT) -> Path | None:
    """The newest transcript of agent `agent` under `root`, or None."""
    hits = sorted(root.glob(f"*/*/subagents/agent-{agent}.jsonl"), key=lambda p: p.stat().st_mtime)
    return hits[-1] if hits else None


def cost(lines: Sequence[str]) -> dict[str, Any]:
    """{"wall_s", "input", "cache_read", "cache_write", "output", "calls"} summed over a transcript's lines."""
    last: dict[str, dict[str, Any]] = {}
    total = {"input": 0, "cache_read": 0, "cache_write": 0, "output": 0, "calls": 0}
    stamps: list[datetime] = []
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("timestamp"):
            stamps.append(datetime.fromisoformat(str(d["timestamp"]).replace("Z", "+00:00")))
        msg = d.get("message") if isinstance(d.get("message"), dict) else {}
        usage = msg.get("usage")
        key = str(d.get("requestId") or msg.get("id") or "")
        if isinstance(usage, dict) and key:
            last[key] = usage  # a streamed call's lines repeat its usage, the last line's output count the whole
    for usage in last.values():
        total["calls"] += 1
        total["input"] += int(usage.get("input_tokens") or 0) + int(usage.get("cache_read_input_tokens") or 0) + int(usage.get("cache_creation_input_tokens") or 0)
        total["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
        total["cache_write"] += int(usage.get("cache_creation_input_tokens") or 0)
        total["output"] += int(usage.get("output_tokens") or 0)
    wall = (max(stamps) - min(stamps)).total_seconds() if len(stamps) >= 2 else 0.0
    return {"wall_s": round(wall), **total}


def cells(c: dict[str, Any]) -> str:
    """The ledger's two cost cells, `wall | tokens`."""
    return f"{c['wall_s']} s | {c['input'] / 1000:.0f}k in ({c['cache_read'] / 1000:.0f}k cached) / {c['output'] / 1000:.1f}k out"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--agent", required=True, help="the agent id (the Agent tool's result names it)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="the projects directory holding the session transcripts")
    args = ap.parse_args(argv)
    path = transcript(args.agent, Path(args.root))
    if path is None:
        print(f"_review_cost: no transcript for agent {args.agent} under {args.root}", file=sys.stderr)
        return 1
    print(cells(cost(path.read_text(encoding="utf-8").splitlines())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
