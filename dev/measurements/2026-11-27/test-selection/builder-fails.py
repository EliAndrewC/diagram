# Failing Rust tests in builders' transcripts, IN or OUT of the modules each builder wrote (event log `writes`, keyed by `by`).
# Run from ~/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents:
#   python3 builder-fails.py $(find . -name '*.jsonl' -newermt '2026-11-26 12:00' | xargs grep -lE -- '---- [a-z_:]+ stdout ----') > builder-fails.txt
# (12:00 local, EST, is 17:00Z). A test is IN when its path's first two segments, `tests` dropped, match an edited file's module
# path, or the edited file is a crate root of one segment that the test path names - a heuristic.
import sys,re,json,glob,collections
EV="/diagram/.clones/diagram-backlog/.git/l7r-events/"
W=collections.defaultdict(set); T={}
for p in glob.glob(EV+"*.jsonl"):
    for l in open(p):
        if '"by"' not in l: continue
        try: e=json.loads(l)
        except Exception: continue
        b=e.get("by")
        if not b: continue
        for w in e.get("writes",[]):
            if "/rust/" in w and w.endswith(".rs"): W[b].add(w)
        if e.get("task"): T.setdefault(b,e["task"])
def mod(path):
    m=re.search(r"/rust/(?:gate/crates/|guard/|)([^/]+)/src/(.+)\.rs$",path) or re.search(r"/rust/([^/]+)/src/(.+)\.rs$",path)
    if not m: return None
    return m.group(1),[x for x in m.group(2).split("/") if x!="tests"]
for p in sys.argv[1:]:
    aid=re.search(r"agent-([0-9a-f]+)",p).group(1)
    first=None; fails=collections.Counter()
    for l in open(p,errors="replace"):
        if first is None:
            try: first=json.loads(l).get("timestamp")
            except Exception: pass
        for m in re.finditer(r"---- ([a-z_][a-z0-9_:]+) stdout ----",l): fails[m.group(1)]+=1
    ed=[x for x in (mod(w) for w in W.get(aid,())) if x]
    print(f"== {T.get(aid)} {aid} start={first} edited={sorted({c+':'+'/'.join(m) for c,m in ed})[:10]}")
    for t in fails:
        key=[x for x in t.split("::") if x!="tests"]
        hit=any(m[:2]==key[:2] or (len(m)==1 and m[0] in key[:2]) for c,m in ed)
        print(f"   {'IN ' if hit else 'OUT'} {t}")
