#!/usr/bin/env python3
"""Feature 347: every tool call that names a coordination file (the cross-session claims file, a group's handoff, a
checks report), by file and verb, with the tokens its result carries over the session's later turns.

Usage: coord.py r1|post [UNTIL|-] [FEATURES]   (the same selection as analyze.py)

This is how 274's R1 counted "about 60 M" - every call naming the file, Bash `cat` the bulk of it, not only Read calls:
on R1's window (r1 2026-09-27T22:30) it gives ~59 M over ~1,250 calls.
"""

import bisect
import collections
import importlib.util
import json
import pathlib
import re
import sys

H = pathlib.Path(__file__).parent
sp = importlib.util.spec_from_file_location("c274", H.parent.parent / "274-leaner-research-sessions/measure/collect.py")
c = importlib.util.module_from_spec(sp)
sp.loader.exec_module(c)
which = sys.argv[1] if len(sys.argv) > 1 else "post"
until = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else "9999"
feats = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
S = [s for s in json.loads((H / f"sessions-{which}.json").read_text()) if s["start"] < until and (not feats or s["feature"] in feats)]
FILES = [("claims", r"RESEARCH-CLAIMS"), ("handoff", r"handoff"), ("checks", r"-checks\.md|checks-report|CHECKS")]
n = collections.Counter()
carry = collections.Counter()
ses = collections.defaultdict(set)
for s in S:
    tp = pathlib.Path.home() / f".claude/projects/-diagram--clones-{s['clone']}/{s['sid']}.jsonl"
    rs = [r for r in c.recs(tp) if not r.get("isSidechain")]
    tss = [x["ts"] for x in c.msgs(rs)]
    tr, _ = c.tools(rs)
    for t in tr:
        txt = str(t["inp"].get("file_path", "")) if t["name"] == "Read" else str(t["inp"].get("command", "")) if t["name"] == "Bash" else ""
        for f, pat in FILES:
            if not re.search(pat, txt):
                continue
            if t["name"] == "Read":
                verb = "Read"
            else:
                m = re.search(r"make (lines|append)|\b(cat|sed|head|tail|grep|awk|echo|printf|tee|cp)\b|>>", txt)
                verb = (m.group(1) or m.group(2) or ">>") if m else "other"
            k = (f, verb)
            n[k] += 1
            carry[k] += t["chars"] // 4 * (len(tss) - bisect.bisect_right(tss, t["ts"]))
            ses[k].add(s["sid"])
for k, v in sorted(carry.items(), key=lambda kv: -kv[1]):
    print(f"{v / 1e6:7.1f}M {n[k]:5} calls {len(ses[k]):4} sessions  {k[0]} {k[1]}")
whole = sum(v for (f, verb), v in carry.items() if verb in ("cat", "Read"))
print(f"{len(S)} sessions; all calls {sum(n.values())} carrying {sum(carry.values()) / 1e6:.1f} M; whole reads (cat, Read) "
      f"{sum(v for (f, verb), v in n.items() if verb in ('cat', 'Read'))} carrying {whole / 1e6:.1f} M; "
      f"make lines {sum(v for (f, verb), v in n.items() if verb == 'lines')}, make append {sum(v for (f, verb), v in n.items() if verb == 'append')}")
