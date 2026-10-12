#!/usr/bin/env python3
"""How long the model takes per turn, against the context it reads - feature 375 amendment 6, FR-033 (`research.md` R5).

    python3 scripts/measure/turn_time.py <session transcript .jsonl> [--record <measurements.json> --key <key>]

A TURN is an assistant reply that follows a tool result: its time is from the tool result to the reply (the model reading
the context and writing). Waits on background work and on the GM are not turns. Each turn's context is the input tokens it
read (cached, cache-written and fresh) and its output tokens are what it wrote. A least-squares fit of time on context and
output says how much of the model time the context's size explains.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys
from datetime import datetime
from typing import Any


def _ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def turns(lines: list[str], ceiling: float = 1200.0) -> list[tuple[int, float, int]]:
    """(context tokens, seconds, output tokens) per turn of the main session (no sidechain), one per request."""
    prev: float | None = None
    seen: set[str] = set()
    out: list[tuple[int, float, int]] = []
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain") or "timestamp" not in d:
            continue
        t = _ts(d["timestamp"])
        content = (d.get("message") or {}).get("content")
        if d.get("type") == "user":
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                prev = t
            continue
        if d.get("type") != "assistant" or prev is None:
            continue
        m = d.get("message") or {}
        rid = str(d.get("requestId") or m.get("id") or "")
        if rid in seen:
            continue
        seen.add(rid)
        u = m.get("usage") or {}
        ctx = int(u.get("cache_read_input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0) + int(u.get("input_tokens") or 0)
        gap = t - prev
        if 0 < gap < ceiling and ctx > 0:
            out.append((ctx, gap, int(u.get("output_tokens") or 0)))
        prev = None
    return out


def fit(points: list[tuple[int, float, int]]) -> tuple[float, float, float]:
    """seconds = a + b * (context / 100k) + c * (output / 1k), least squares by the normal equations (no numpy)."""
    rows = [(1.0, p[0] / 1e5, p[2] / 1e3, p[1]) for p in points]
    n = 3
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(n)] for i in range(n)]
    aty = [sum(r[i] * r[3] for r in rows) for i in range(n)]
    for col in range(n):  # Gauss-Jordan with partial pivoting
        piv = max(range(col, n), key=lambda i: abs(ata[i][col]))
        ata[col], ata[piv], aty[col], aty[piv] = ata[piv], ata[col], aty[piv], aty[col]
        for i in range(n):
            if i != col and ata[col][col]:
                f = ata[i][col] / ata[col][col]
                ata[i] = [a - f * b for a, b in zip(ata[i], ata[col], strict=True)]
                aty[i] -= f * aty[col]
    a, b, c = (aty[i] / ata[i][i] if ata[i][i] else 0.0 for i in range(n))
    return round(a, 2), round(b, 2), round(c, 2)


def summary(points: list[tuple[int, float, int]]) -> dict[str, Any]:
    a, b, c = fit(points)
    total = sum(p[1] for p in points)
    return {
        "turns": len(points),
        "model hours": round(total / 3600, 2),
        "median turn s": round(statistics.median(p[1] for p in points), 1),
        "fit: s fixed, per 100k context, per 1k output": [a, b, c],
        "hours explained by context size": round(sum(b * p[0] / 1e5 for p in points) / 3600, 2),
        "median turn s by context (100k bands)": {
            f"{lo}-{lo + 200}k": round(statistics.median(p[1] for p in points if lo * 1e3 <= p[0] < (lo + 200) * 1e3), 1)
            for lo in range(0, 1000, 200)
            if any(lo * 1e3 <= p[0] < (lo + 200) * 1e3 for p in points)
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--record", default="")
    ap.add_argument("--key", default="")
    a = ap.parse_args(argv)
    points = turns(pathlib.Path(a.transcript).read_text(encoding="utf-8").splitlines())
    if not points:
        print("turn_time: no turns found", file=sys.stderr)
        return 2
    s = summary(points)
    if a.record:
        if not a.key:
            print("turn_time: --record needs --key", file=sys.stderr)
            return 2
        path = pathlib.Path(a.record)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault(a.key, {})["value"] = s
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(s, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
