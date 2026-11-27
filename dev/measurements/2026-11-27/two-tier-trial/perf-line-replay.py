"""451 T308/T410: the decide rule's replay - each `**Performance work?**` line of a plan that answers no and holds `measurement`."""
import re, sys
for path in sys.argv[1:]:
    task = "?"; hits = []; total = 0
    for n, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        m = re.match(r"#{2,6} (T[0-9]+[a-z]?)", line)
        if m: task = m.group(1)
        low = line.lower().lstrip()
        if low.startswith("- "): low = low[2:]
        if not low.startswith("**performance work?**"): continue
        total += 1
        ans = low[len("**performance work?**"):].lstrip()
        if ans.startswith("no") and not ans[2:3].isalnum() and "measurement" in low:
            hits.append((task, n, line[:150]))
    print(f"{path}: {total} Performance lines, {len(hits)} refused")
    for h in hits: print("  ", *h)
