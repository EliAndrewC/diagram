"""m:full-plan-reasons (feature 430): each 2026-10-26 `make done` run planned full, by its reason's file."""

import collections
import glob
import json
import re

REASON = re.compile(r"(a non-module file under tests/ changed: [^\"\\]+|an engine file that is not Python changed: [^\"\\]+)")
counts: collections.Counter[str] = collections.Counter()
for f in sorted(glob.glob("dev/run-log/2026-10/20261026*.json")):
    run = json.load(open(f, encoding="utf-8"))
    if run.get("target") == "done" and (m := REASON.search(json.dumps(run))):
        counts[m.group(1)] += 1
for reason, n in counts.most_common():
    print(n, reason)
