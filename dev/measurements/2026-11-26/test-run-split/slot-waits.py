# 451 T315: every slot-wait Phase line of the clone's event log: its start, its seconds, the make target, the tree, the task it was booked to.
import sys, json, datetime, glob
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
rows = []
for f in glob.glob("/diagram/.clones/diagram-backlog/.git/l7r-events/*.jsonl"):
    for l in open(f, errors="replace"):
        if '"step":"slot-wait"' in l:
            e = json.loads(l); rows.append((e["t0"][11:19], round(ts(e["t1"]) - ts(e["t0"]), 1), e.get("make"), e["clone"].split("/")[-1], ",".join(c.split("/")[-1] for c in e.get("crates", [])), e.get("task")))
for r in sorted(rows): print(*r)
