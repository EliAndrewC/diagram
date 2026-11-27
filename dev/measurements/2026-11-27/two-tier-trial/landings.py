"""451 T308: the landings of the two-tier trial, read from the 451 event log (read-only).
A landing is a `Phase` line of src `land`, step `end`; it went out where `landed` is true. The trial's first line is the first
`make builder-checks` the log holds."""
import json, sys
log = sys.argv[1]; until = sys.argv[2]
start = None; ends = []; gates = []
for line in open(log, encoding="utf-8"):
    if '"builder-checks"' not in line and '"src":"land"' not in line: continue
    try: l = json.loads(line)
    except ValueError: continue
    t = l.get("t", "")
    if start is None and (l.get("make") == "builder-checks" or "builder-checks" in (l.get("makes") or [])): start = t
    if start is None or t > until: continue
    if l.get("ev") == "Phase" and l.get("src") == "land":
        if l.get("step") == "end": ends.append(l)
        if l.get("step") == "gate": gates.append(l)
out = [e for e in ends if e.get("landed") is True]
tasks = sorted({t for e in out for t in e.get("tasks", [])}, key=lambda s: int(''.join(c for c in s if c.isdigit())))
mins = lambda l: (__import__("datetime").datetime.fromisoformat(l["t1"][:-1]) - __import__("datetime").datetime.fromisoformat(l["t0"][:-1])).total_seconds() / 60
print("trial's first builder-checks:", start, "until", until)
print("landing attempts (end lines):", len(ends), "went out:", len(out), "refused or red:", len(ends) - len(out))
print("tasks landed:", len(tasks), " ".join(tasks))
print("gate steps:", len(gates), "red:", sum(1 for g in gates if g.get("code")), "green:", sum(1 for g in gates if not g.get("code")))
print("gate minutes: red %.1f green %.1f" % (sum(mins(g) for g in gates if g.get("code")), sum(mins(g) for g in gates if not g.get("code"))))
print("attempts refused before a gate ran:", len(ends) - len(out) - sum(1 for g in gates if g.get("code")))
for e in ends: print(" ", e["t0"][:16], "->", e["t1"][11:16], "landed" if e.get("landed") else "NOT", e.get("code"), " ".join(e.get("tasks", [])))
