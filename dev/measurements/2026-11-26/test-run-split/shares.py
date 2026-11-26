#!/usr/bin/env python3
"""451 T315: how much of a crate's test time is tests that start `git`, or any program found on PATH, against tests that start none.
A test is counted as starting git where it FAILS with a `git` first on PATH that exits 127, and as starting a program where it fails
with PATH=/nonexistent; its seconds are those of the good run (libtest's own per-test time, the suite running whole). A LOWER BOUND:
a test that does not check what it started, or starts a program by its full path, passes both.
usage: shares.py <dir of <name>-report.jsonl, <name>-nogit.jsonl, <name>-nopath.jsonl> <name> ..."""
import json, sys
d = sys.argv[1]
def ev(p): return [json.loads(l) for l in open(p) if l.startswith("{")]
print("crate | tests | sum of the tests' seconds | start git: tests, seconds | start any program: tests, seconds | start none: tests, seconds | longest test s")
for n in sys.argv[2:]:
    good = {e["name"]: e["exec_time"] for e in ev(f"{d}/{n}-report.jsonl") if e["type"] == "test" and "exec_time" in e}
    bad = lambda f: {e["name"] for e in ev(f"{d}/{n}-{f}.jsonl") if e["type"] == "test" and e.get("event") == "failed"}
    git, anyp = bad("nogit"), bad("nopath") | bad("nogit")
    s = lambda names: sum(good.get(x, 0) for x in names)
    tot = sum(good.values()); rest = set(good) - anyp
    print(f"{n} | {len(good)} | {tot:.1f} | {len(git)}, {s(git):.1f} ({100*s(git)/tot:.0f}%) | {len(anyp)}, {s(anyp):.1f} ({100*s(anyp)/tot:.0f}%) | {len(rest)}, {s(rest):.1f} ({100*s(rest)/tot:.0f}%) | {max(good.values()):.2f}")
