#!/usr/bin/env python3
"""`make fix-yield F=<feature>` - is each tooling fix doing anything, read by what its tools did since it was made
(feature 385 T119; rebuilt on `make tool-yield` by feature 406 T06, D165).

WHY (the GM 2026-10-19): each fix's yield measured "so a fix that saves nothing is retired", and then, of the 22 that read
"saves nothing" on T119's command rate: "Whether or not it's doing something for us should be a measurable question". T119
compared a regex's minutes per session hour before and after a fix, a rate that moves with the mix of work and that a fix
which is USED raises; 45 of its measures were assigned after the fact. Feature 406 retired that reading.

A fix's tools are the guards, checks, targets, reviews and registered steps in the files of the commit that settled it (the
settling note's leading hash, or the commit naming its trigger), mapped by `tool_yield.tools_of`. Each tool is read since the
settling: uses, interventions, likely misfires, with FR-001's "no outcome record" and "too new". Each fix then takes the first
reading that holds, in D166's order: too new to say (made under 7 days ago); doing something (a tool with interventions net of
its misfires); no outcome record (a tool whose record cannot show one, or no tool found); record too new (a tool first seen
under 7 days ago); doing nothing.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reviews"))
import stepback_bundle as sb  # noqa: E402
import tool_yield as ty  # noqa: E402

DAY = 86400.0


def fixes(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Every ruling naming a fix, with its settling (`fix_of` rows: done or declined): its status, when, and its note."""
    settled = {str(r["fix_of"]): r for r in rows if r.get("fix_of")}
    out = []
    for r in rows:
        if r.get("tooling_fix"):
            s = settled.get(str(r.get("trigger")), {})
            out.append({**r, "status": s.get("status", "open"), "settled": s.get("utc", ""), "note": s.get("note", ""), "test": s.get("test", "")})
    return out


def _git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def settling_commit(root: Path, fix: Mapping[str, Any]) -> str:
    """The commit that made the fix: the hash its settling note opens with; else the newest commit up to its settling that names
    its trigger exactly (`@2` is not `@29`); else the newest one up to then that touched the test its settling names."""
    m = re.match(r"\s*([0-9a-f]{7,40})\b", str(fix.get("note") or ""))
    if m and subprocess.run(["git", "-C", str(root), "cat-file", "-e", m.group(1) + "^{commit}"], capture_output=True).returncode == 0:
        return m.group(1)
    until = [f"--until={fix['settled']}"] if fix.get("settled") else []
    trigger = "".join(c if c.isalnum() or c in "-:@/#_ ,=" else "\\^" if c == "^" else f"[{c}]" for c in str(fix.get("trigger") or ""))
    # the clone's own commit before a landing's, which carries every file landed with it (`make land-tooling`, feature 379)
    found = _git(root, "log", "-20", "--format=%h %s", *until, "-E", f"--grep={trigger}([^0-9]|$)", "HEAD").splitlines() if trigger else []
    own = [line.split(" ", 1)[0] for line in found if not line.split(" ", 1)[-1].startswith("Tooling from ")]
    sha = (own or [line.split(" ", 1)[0] for line in found] or [""])[0]
    if not sha and fix.get("test"):
        sha = _git(root, "log", "-1", "--format=%h", *until, "HEAD", "--", str(fix["test"])).strip()
    return sha


def tools_of_fix(root: Path, fix: Mapping[str, Any]) -> set[tuple[str, str]]:
    sha = settling_commit(root, fix)
    if not sha:
        return set()
    files = _git(root, "show", "--name-only", "--format=", sha).split()
    return ty.tools_of(root, files, _git(root, "show", "-U0", "--format=", sha, "--", "Makefile"))


def verdict(fix: Mapping[str, Any], tools: Mapping[tuple[str, str], ty.Tally], now: float) -> dict[str, Any]:
    """One fix's reading and its tools' numbers since it was made (D165, D166)."""
    row: dict[str, Any] = {"trigger": fix.get("trigger"), "fix_minutes": fix.get("fix_minutes"), "tools": []}
    if fix.get("status") != "done":
        return {**row, "reading": f"not made ({fix.get('status')})"}
    made = sb._ts(str(fix["settled"]))  # noqa: SLF001
    for (kind, name), tool in sorted(tools.items()):
        uses, hits, misses = tool.since(made)
        recorded = tool.outcome_record and bool(tool.first)
        row["tools"].append({"kind": kind, "name": name, "first": tool.first, "uses": uses, "hits": hits, "misses": misses, "recorded": recorded})
    t = row["tools"]
    if now - made < 7 * DAY:
        reading = "too new to say"
    elif any(x["hits"] - (0 if x["kind"] in ("check", "step") else x["misses"]) > 0 for x in t):
        reading = "doing something"
    elif not t or any(not x["recorded"] for x in t):
        reading = "no outcome record" + ("" if t else " (no tool found in its settling commit)")
    elif any(now - x["first"] < 7 * DAY for x in t):
        reading = "record too new"
    else:
        reading = "doing nothing"
    return {**row, "made": made, "reading": reading}


def _day(t: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(t)) if t else "-"


def table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = ["| fix (trigger) | made | cost ruled (min) | reading | its tools since it was made: uses / interventions / likely misfires |", "|---|---|---|---|---|"]
    for r in rows:
        tools = "; ".join(
            f"{x['kind']} {x['name']} (first seen {_day(x['first'])}): "
            + (f"{x['uses']} / {x['hits']} / {'no outcome record' if x['kind'] in ('check', 'step') else x['misses']}" if x["recorded"] else "no outcome record")
            for x in r["tools"]
        )
        minutes = r.get("fix_minutes") if r.get("fix_minutes") is not None else "-"
        lines.append(f"| {r['trigger']} | {_day(r.get('made', 0.0))} | {minutes} | {r['reading']} | {tools or '-'} |")
    return "\n".join(lines) + "\n\n(the numbers are `make tool-yield`'s, counted from each fix's settling; an intervention is a refusal, a rewrite, a finding or a failed run)\n"


def report(root: Path, feature_dir: Path, now: float | None = None, guard_log: Path | None = None) -> str:
    """The yield table of a feature's fixes, read from its arbiter record and `make tool-yield`'s numbers."""
    fx = fixes(sb._lines(feature_dir / "arbiter.jsonl"))  # noqa: SLF001
    if not fx:
        return "(no tooling fix ruled)\n"
    every = ty.collect(root, guard_log)
    now = now if now is not None else time.time()
    rows = []
    for f in fx:
        keys = tools_of_fix(root, f) if f.get("status") == "done" else set()
        rows.append(verdict(f, {k: every[k] for k in keys if k in every}, now))
    return table(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("feature")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    dirs = sorted((root / "specs").glob(f"{args.feature}*"))
    if len(dirs) != 1:
        print(f"fix-yield: no single specs/{args.feature}* directory", file=sys.stderr)
        return 2
    print(report(root, dirs[0]), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
