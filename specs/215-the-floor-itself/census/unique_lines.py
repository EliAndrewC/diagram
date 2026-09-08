"""Per coverage CONTEXT of the gate baseline: engine lines it executed and the lines NO other context executed."""
import sqlite3, sys, collections
from coverage.numbits import numbits_to_nums
db = sys.argv[1]
con = sqlite3.connect(db)
rows = con.execute("select c.context, f.path, l.numbits from line_bits l join file f on f.id=l.file_id join context c on c.id=l.context_id").fetchall()
by_ctx = collections.defaultdict(set)
for ctx, path, nb in rows:
    if "/l7r/" not in path or "/tests/" in path: continue
    short = path.split("/l7r/diagram/")[-1]
    for ln in numbits_to_nums(nb): by_ctx[ctx].add((short, ln))
count = collections.Counter()
for ctx, lines in by_ctx.items():
    for x in lines: count[x] += 1
want = [c for c in by_ctx if c.startswith("fixture:") or "rolls" in c or any(k in c for k in sys.argv[2:])]
out = []
for ctx in sorted(by_ctx):
    lines = by_ctx[ctx]
    if len(lines) < 200: continue  # not a roll
    uniq = sorted(x for x in lines if count[x] == 1)
    out.append((len(uniq), ctx, len(lines), uniq))
for n, ctx, tot, uniq in sorted(out, reverse=True):
    files = collections.Counter(f for f, _ in uniq)
    print(f"{n:5d} unique of {tot:6d} lines  {ctx[:95]}")
    if n: print("        " + ", ".join(f"{f}:{c}" for f, c in files.most_common(6)))
