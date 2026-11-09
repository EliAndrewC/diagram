#!/usr/bin/env python3
"""Feature 347: where a complete group's cost per thing checked goes - write sessions, check sessions, agents - and
how many things a group checks, for each selection R3 compares. Run analyze.py for each selection first (it writes the
groups-*.json this reads); run_all.sh does both.

Medians over complete groups; write turns per thing is the write session's turns over its group's things.
"""

import collections
import json
import pathlib
import statistics

H = pathlib.Path(__file__).parent
SELECTIONS = [  # (sessions file, start before, features, label) - the same selections as run_all.sh
    ("r1", "2026-09-27T22:30", None, "R1 window (before 274)"),
    ("r1", "2026-09-27T22:30", {"269"}, "269 before 274"),
    ("post", "9999", {"269"}, "269 after 274"),
    ("post", "9999", {"269", "280", "291", "317"}, "research groups after 274"),
]


def row(which, until, feats, label):
    S = [s for s in json.loads((H / f"sessions-{which}.json").read_text()) if s["start"] < until and (not feats or s["feature"] in feats)]
    G = {r["group"]: r for r in json.loads((H / f"groups-{which}{'-' + '-'.join(sorted(feats)) if feats else ''}.json").read_text())}
    by = collections.defaultdict(list)
    for s in S:
        by[s["group"]].append(s)
    rows = []
    for g, ss in by.items():
        r = G.get(g)
        if not r or not r["complete"]:
            continue
        t = r["things"]
        part = lambda kinds: sum(s["tot"] for s in ss if s["kind"] in kinds) / t  # noqa: E731
        writes = [s for s in ss if s["kind"] == "write"]
        rows.append({"write": part({"write", "continuation"}), "check": part({"check"}), "agents": r["agents"] / t, "total": r["per_thing"],
                     "things": t, "checks": sum(1 for s in ss if s["kind"] == "check"),
                     "write_turns_per_thing": sum(s["turns"] for s in writes) / t})
    med = lambda k: statistics.median(x[k] for x in rows)  # noqa: E731
    print(f"| {label} | {len(rows)} | {med('things'):.0f} | {med('write') / 1e6:.2f} | {med('check') / 1e6:.2f} | {med('agents') / 1e6:.2f} | "
          f"{med('total') / 1e6:.2f} | {med('checks'):.0f} | {med('write_turns_per_thing'):.1f} |")


print("| selection | complete groups | things a group | write M/thing | check M/thing | agents M/thing | total M/thing | check sessions a group | write turns a thing |")
print("|---|---|---|---|---|---|---|---|---|")
for sel in SELECTIONS:
    row(*sel)
