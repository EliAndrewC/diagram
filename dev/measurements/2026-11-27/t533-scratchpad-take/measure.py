import json, os, re, sys, subprocess
SP = "/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad"
CLONE = "/diagram/.clones/diagram-backlog"
OUT = "/diagram/.clones/diagram-backlog/.git/worktrees/diagram-backlog-t271/t533/would-take.txt"
done = open("/diagram/specs/451-time-retro-and-efficiency/tasks-done.md").read()
landed = {int(m) for m in re.findall(r"^- \[x\] T(\d+)", done, re.M)}
openl = {int(m) for m in re.findall(r"^- \[ \] T(\d+)", open("/diagram/specs/451-time-retro-and-efficiency/tasks.md").read(), re.M)}
rows = [json.loads(l) if l.strip() else None for l in open(CLONE + "/.git/task-starts.jsonl")]
keep = [True]*len(rows)
for i, r in enumerate(rows):
    u = (r or {}).get("unstart")
    if isinstance(u, dict):
        keep[i] = False
        for j in range(i):
            s = rows[j] or {}
            if isinstance(s.get("task"), str) and s.get("task") == u.get("task") and s.get("feature") == u.get("feature") and (s.get("tree") is None or s.get("tree") == r.get("tree")):
                keep[j] = False
live = [r for r, k in zip(rows, keep) if k and r]
specs = CLONE + "/specs"
def is_open(f, task):
    d = [n for n in os.listdir(specs) if n == f or n.startswith(f + "-")]
    if not d: return True
    try: t = open(f"{specs}/{d[0]}/tasks.md").read()
    except OSError: return True
    return any((l + " ").startswith(f"- [ ] {task} ") for l in t.splitlines())
held = set()
for r in live:
    f, task = r.get("feature") or "", r.get("task") or ""
    m = re.match(r"T(\d+)", task)
    if f and not f.startswith("451") and m and int(m.group(1)) in landed and is_open(f, task):
        held.add(int(m.group(1)))
wt = subprocess.run(["bash","-c","for g in /diagram/.git /diagram/.clones/*/.git; do [ -d $g ] && git --git-dir=$g worktree list --porcelain 2>/dev/null; done | sed -n 's/^worktree //p'"],capture_output=True,text=True).stdout.split()
livep = set()
for pid in os.listdir("/proc"):
    if not pid.isdigit(): continue
    try: fds = os.listdir(f"/proc/{pid}/fd")
    except OSError: fds = []
    for link in ["cwd"] + [f"fd/{x}" for x in fds]:
        try: p = os.readlink(f"/proc/{pid}/{link}")
        except OSError: continue
        if p.startswith(SP + "/"): livep.add(p)
def du(p): return int(subprocess.run(["du","-sb",p],capture_output=True,text=True).stdout.split()[0] or 0)
cats = {}
for name in sorted(os.listdir(SP)):
    m = re.match(r"t(\d+)", name)
    p = SP + "/" + name
    if not m: cat = "no t<N> prefix"
    else:
        n = int(m.group(1))
        if n not in landed: cat = "open in 451" if n in openl else "not a 451 task number"
        elif n in held: cat = "landed, held by another feature's open start"
        elif any(t.startswith(p) for t in wt): cat = "landed, holds a registered worktree"
        elif any(l == p or l.startswith(p + "/") for l in livep): cat = "landed, held by a live process"
        else: cat = "WOULD TAKE"
    cats.setdefault(cat, []).append((name, du(p)))
for c, v in cats.items():
    print(f"{c}: {len(v)} entries, {sum(b for _, b in v)/1e9:.2f} GB")
print("held numbers:", sorted(held))
for c in cats:
    if c not in ("WOULD TAKE", "no t<N> prefix"):
        print(c, [n for n, _ in cats[c]][:40])
take = sorted(cats.get("WOULD TAKE", []), key=lambda x: -x[1])
print("largest would-take:", [(n, round(b/1e9, 2)) for n, b in take[:8]])
open(OUT, "w").write("\n".join(f"{b}\t{n}" for n, b in take) + "\n")
