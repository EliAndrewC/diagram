#!/usr/bin/env python3
"""Feature 376: is a research group's cost a FIXED part spread over fewer things (376's premise, from 347's R3), or a
cost PER THING that rose? Reads 347's collected sessions (run `specs/347-.../measure/run_all.sh` first; its
sessions-*.json are not committed). Prints, for each selection, a least-squares fit of a complete group's cost
against its things checked - fixed part + per-thing part - for write sessions, check sessions, agents and the total;
then the tool calls and carried tokens per thing, before 274 against the research groups after it.

Usage: fixed_and_marginal.py > results.txt
"""

import bisect
import collections
import importlib.util
import json
import pathlib
import re
import statistics

M347 = pathlib.Path(__file__).resolve().parents[2] / "347-measure-feature274-write-cap-line-reads" / "measure"
_s = importlib.util.spec_from_file_location("c274", M347.parents[1] / "274-leaner-research-sessions/measure/collect.py")
c274 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(c274)
SEL = [("r1", None, "2026-09-27T22:30", "R1 window (before 274)"), ("r1", {"269"}, "2026-09-27T22:30", "269 before 274"),
       ("post", {"269"}, "9999", "269 after 274"), ("post", {"269", "280", "291", "317"}, "9999", "research groups after 274")]


def load(which, feats, until):
    S = [s for s in json.loads((M347 / f"sessions-{which}.json").read_text()) if s["start"] < until and (not feats or s["feature"] in feats)]
    G = {r["group"]: r for r in json.loads((M347 / f"groups-{which}{'-' + '-'.join(sorted(feats)) if feats else ''}.json").read_text())}
    return [s for s in S if G.get(s["group"], {}).get("complete")], G


def fits():
    print("| selection | groups | write M | check M | agents M | total M |")
    print("|---|---|---|---|---|---|")
    for which, feats, until, label in SEL:
        S, G = load(which, feats, until)
        groups = sorted({s["group"] for s in S})
        th = [G[g]["things"] for g in groups]
        cols = []
        for part in ("write", "check", "agents", "total"):
            if part in ("agents", "total"):
                ys = [G[g][part] for g in groups]
            else:
                ys = [sum(s["tot"] for s in S if s["group"] == g and s["kind"] == part) for g in groups]
            f = statistics.linear_regression(th, ys)
            cols.append(f"{f.intercept / 1e6:.2f} + {f.slope / 1e6:.3f}/thing")
        print(f"| {label} | {len(groups)} | " + " | ".join(cols) + " |")


def tools(which, feats, until):
    S, G = load(which, feats, until)
    things = sum(G[g]["things"] for g in {s["group"] for s in S})
    calls, carry = collections.Counter(), collections.Counter()
    for s in S:
        rs = [r for r in c274.recs(pathlib.Path.home() / f".claude/projects/-diagram--clones-{s['clone']}/{s['sid']}.jsonl") if not r.get("isSidechain")]
        tss = [x["ts"] for x in c274.msgs(rs)]
        tr, _ = c274.tools(rs)
        for t in tr:
            m = re.search(r"\bmake\s+([a-z][\w-]*)", str(t["inp"].get("command", ""))) if t["name"] == "Bash" else None
            k = ("make " + m.group(1)) if m else ("bash other" if t["name"] == "Bash" else t["name"])
            calls[k] += 1
            carry[k] += t["chars"] // 4 * (len(tss) - bisect.bisect_right(tss, t["ts"]))
    return things, calls, carry


fits()
a, b = tools(*SEL[0][:3]), tools(*SEL[3][:3])
print(f"\nper thing checked: before 274 ({a[0]} things) -> research groups after ({b[0]} things)\n")
print("| tool | calls a thing | carried K a thing |")
print("|---|---|---|")
for k in sorted(set(a[1]) | set(b[1]), key=lambda k: -(b[2][k] / b[0] - a[2][k] / a[0]))[:14]:
    print(f"| {k} | {a[1][k] / a[0]:.2f} -> {b[1][k] / b[0]:.2f} | {a[2][k] / a[0] / 1e3:.0f} -> {b[2][k] / b[0] / 1e3:.0f} |")
