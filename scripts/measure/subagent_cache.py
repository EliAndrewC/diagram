#!/usr/bin/env python3
"""What subagents write to the prompt cache fresh, and what they could have read from it (feature 383 amendment 6, FR-036).

The GM, 2026-10-17: *"it's very, very important that any context that subagents share in common is put either into their
system prompt, ideally, or ... at the very beginning of the prompt, such that it is much more likely to be cached"*. A
prompt is cached as a PREFIX: what every dispatch of a check shares is read from the cache only while nothing that differs
comes before it. A defined agent's file is its system prompt, first in every dispatch; the prompt and what the agent reads
come after it. So the question this asks of the transcripts is where each type's tokens are WRITTEN (1.25x the input rate at
the 5-minute tier subagents get) against READ (0.1x):

    subagent_cache.py [--since YYYY-MM-DD] [--root ~/.claude/projects/-diagram]

per agent type: its runs; for a dispatch made under five minutes after one of the same type in the same session (the cache's
lifetime), what its FIRST call read from the cache and wrote fresh - a defined agent writes only its prompt and the harness's
environment block, ~2.5-3.5k tokens; and how much text its bundles' manifests repeat (`shared_text`), which belongs in the
agent file. Then the whole spend in base-input units. Research: specs/383-tooling-caches-and-hourly-step-back/research.md R13.
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import sys
from collections.abc import Iterable, Iterator

#: base-input units per token at the 5-minute cache tier subagents get (their usage reports `ephemeral_5m` writes)
RATES = {"write": 1.25, "read": 0.1, "input": 1.0, "output": 5.0}
#: a dispatch this soon after one of its type in the same session finds that one's prefix cached
WINDOW_S = 300
#: a manifest line counts toward repeated text from this length: shorter ones are headings and separators
LINE_MIN = 40
ROOT = pathlib.Path.home() / ".claude" / "projects" / "-diagram"


def _records(path: pathlib.Path) -> Iterator[dict]:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            yield d


def _text(body: object) -> str:
    if isinstance(body, str):
        return body
    if isinstance(body, list):
        return "".join(b.get("text", "") for b in body if isinstance(b, dict))
    return ""


def run_of(path: pathlib.Path) -> dict | None:
    """One subagent run: its type, session, start, each call's usage (once per request) and the first MANIFEST.md it read."""
    meta = path.with_name(path.name[: -len(".jsonl")] + ".meta.json")
    try:
        kind = json.loads(meta.read_text(encoding="utf-8")).get("agentType") or "?"
    except OSError, ValueError:
        return None
    start, calls, seen, manifest, pending = "", [], set(), "", set()
    for d in _records(path):
        start = start or d.get("timestamp", "")
        m = d.get("message") or {}
        u, rid = m.get("usage"), d.get("requestId") or m.get("id")
        if u and rid not in seen:
            seen.add(rid)
            calls.append(u)
        for b in m.get("content") if isinstance(m.get("content"), list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") == "Read" and str((b.get("input") or {}).get("file_path", "")).endswith("MANIFEST.md"):
                pending.add(b.get("id"))
            if b.get("type") == "tool_result" and b.get("tool_use_id") in pending and not manifest:
                manifest = _text(b.get("content"))
    if not calls or not start:
        return None
    return {"kind": kind, "session": path.parent.parent.name, "start": start, "calls": calls, "manifest": manifest}


def runs(root: pathlib.Path, since: str) -> list[dict]:
    out = [r for f in sorted(root.glob("*/subagents/agent-*.jsonl")) if (r := run_of(f)) and r["start"] >= since]
    return sorted(out, key=lambda r: r["start"])


def _at(stamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def back_to_back(rs: Iterable[dict]) -> dict[str, list[dict]]:
    """Per type, the runs made under WINDOW_S after one of their type in the same session - each found that one cached."""
    last: dict[tuple[str, str], datetime.datetime] = {}
    out: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rs:
        key, t = (r["session"], r["kind"]), _at(r["start"])
        if key in last and (t - last[key]).total_seconds() < WINDOW_S:
            out[r["kind"]].append(r)
        last[key] = t
    return out


def _lines(text: str) -> set[str]:
    """A text's lines of LINE_MIN characters or more, the Read tool's line-number prefix dropped."""
    out = set()
    for raw in text.splitlines():
        line = raw.split("\t", 1)[-1].strip() if "\t" in raw[:12] else raw.strip()
        if len(line) >= LINE_MIN:
            out.add(line)
    return out


def shared_text(a: str, b: str) -> int:
    """Characters of the lines (LINE_MIN or longer) both texts hold - what two bundles of one check repeat."""
    return sum(len(line) for line in _lines(a) & _lines(b))


def repeated(manifests: list[str], share: float = 0.8) -> int:
    """Characters of the lines at least `share` of the manifests hold."""
    if len(manifests) < 2:
        return 0
    counts = collections.Counter(line for m in manifests for line in _lines(m))
    return sum(len(line) for line, n in counts.items() if n >= share * len(manifests))


def _sum(calls: Iterable[dict], key: str) -> int:
    return sum(int(c.get(key) or 0) for c in calls)


def spend(rs: Iterable[dict]) -> dict[str, float]:
    tot = collections.Counter()
    for r in rs:
        tot["write"] += _sum(r["calls"], "cache_creation_input_tokens")
        tot["read"] += _sum(r["calls"], "cache_read_input_tokens")
        tot["input"] += _sum(r["calls"], "input_tokens")
        tot["output"] += _sum(r["calls"], "output_tokens")
    return {**{k: float(v) for k, v in tot.items()}, "units": sum(tot[k] * RATES[k] for k in RATES)}


def report(rs: list[dict]) -> str:
    pairs = back_to_back(rs)
    by: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rs:
        by[r["kind"]].append(r)
    rows = [f"{'type':24} {'runs':>5} {'b2b':>4} {'1st read':>9} {'1st write':>9} {'repeated':>9} {'units/run':>10}"]
    for kind, krs in sorted(by.items(), key=lambda kv: -spend(kv[1])["units"]):
        p = pairs.get(kind, [])
        first = lambda key: sum(int(r["calls"][0].get(key) or 0) for r in p) // len(p) if p else 0  # noqa: E731
        rep = repeated([r["manifest"] for r in krs if r["manifest"]])
        rows.append(f"{kind[:24]:24} {len(krs):>5} {len(p):>4} {first('cache_read_input_tokens'):>9} {first('cache_creation_input_tokens'):>9} {rep:>9} {spend(krs)['units'] / len(krs):>10.0f}")
    s = spend(rs)
    rows.append(
        f"\nall: {len(rs)} runs; written {s.get('write', 0):,.0f}, read {s.get('read', 0):,.0f}, output {s.get('output', 0):,.0f} tokens"
        f" = {s['units']:,.0f} base-input units (a write {RATES['write']}x, a read {RATES['read']}x, output {RATES['output']}x: the 5-minute tier)"
    )
    rows.append(
        "b2b = dispatches under 5 minutes after one of their type in the same session; '1st write' is what such a one still wrote"
        " fresh (a defined agent: ~2.5-3.5k - its prompt and the environment block). 'repeated' = characters in 80% of its"
        " manifests: that text belongs in the agent's file (CLAUDE.md, the review checks)."
    )
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default=(datetime.date.today() - datetime.timedelta(days=7)).isoformat())
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    rs = runs(pathlib.Path(a.root), a.since)
    if not rs:
        print(f"subagent-cache: no subagent runs under {a.root} since {a.since}")
        return 0
    print(f"subagent-cache: subagent runs since {a.since}\n")
    print(report(rs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
