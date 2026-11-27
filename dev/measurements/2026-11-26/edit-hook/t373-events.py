# t373: the day's hook invocations from a COPY of the clone's event log (the copy made into the sandbox at 18:26 local; the real log is not opened).
# The day is 2026-11-26 local (UTC-5): t from 2026-11-26T05:00Z. Counts PreToolUse lines by tool; Edit and Write by file kind, by who (session or a sub-agent), and by clone.
import json,sys,collections,os,glob
S=os.path.dirname(os.path.abspath(__file__)); D=S+'/w/diagram/.clones/diagram-backlog/.git/l7r-events'
lo,hi='2026-11-26T05:00','2026-11-27T05:00'
tools=collections.Counter(); kinds=collections.Counter(); who=collections.Counter(); trees=collections.Counter(); posts=collections.Counter(); files=collections.Counter(); sids=collections.Counter(); probes=collections.Counter(); where=collections.Counter()
CLONES={'diagram-backlog','diagram-backlog-pages'}  # checked 2026-11-26: test -d <tree>/.git
def kind(p):
    if '/.clones/' not in p: return 'outside any clone (scratch, /tmp, ~)'
    r=p.split('/.clones/',1)[1].split('/',1)[1] if '/' in p.split('/.clones/',1)[1] else ''
    if r.startswith('rust/'): return 'Rust source (rust/**)'
    if r.startswith('specs/') and r.endswith('plan.md'): return "a spec's plan.md"
    if r.startswith('specs/') and r.endswith('tasks.md'): return "a spec's tasks.md"
    if r.startswith('specs/'): return 'other spec file'
    if r.startswith('dev/measurements/'): return 'dev/measurements record'
    if r.startswith(('docs/','dev/')) or r.endswith('.md'): return 'doc (docs/, dev/, *.md)'
    if r.startswith(('scripts/','tests/')) or r=='Makefile' or r.startswith('.claude/'): return 'tooling (scripts/, tests/, Makefile, .claude/)'
    return 'other in a clone'
for f in sorted(glob.glob(D+'/*.jsonl')):
    if os.path.basename(f)=='_unassigned.jsonl': continue  # the sandbox's own runs
    files[os.path.basename(f)]+=0
    for l in open(f,errors='replace'):
        if '"t":"2026-11-2' not in l[:20]: continue
        try: r=json.loads(l)
        except Exception: continue
        if not (lo<=r.get('t','')<hi): continue
        if r.get('sid','').startswith(('t365-','t304-','t373-')): probes[r.get('sid')]+=1; continue  # PROBES: measurement sessions, not work
        ev,tool=r.get('ev'),r.get('tool','')
        if ev=='PostToolUse': posts[tool]+=1
        if ev!='PreToolUse': continue
        tools[tool]+=1; files[os.path.basename(f)]+=1
        if tool in ('Edit','Write','MultiEdit','NotebookEdit'):
            p=r.get('path','') or ''
            kinds[(tool,kind(p))]+=1; who['sub-agent' if r.get('by') else 'the session itself']+=1; sids[r.get('sid','')[:12]]+=1
            tr=p.split('/.clones/',1)[1].split('/')[0] if '/.clones/' in p else None
            where[(tool,'outside any clone' if tr is None else ('the clone itself (.git a directory: clone-sync judges it)' if tr in CLONES else 'a pool worktree (.git a file: clone-sync has no opinion)'))]+=1
            trees[p.split('/.clones/',1)[1].split('/')[0] if '/.clones/' in p else '(outside)']+=1
print('files with lines of the day:',{k:v for k,v in files.items() if v})
print('PreToolUse lines by tool:'); [print(f'  {n:6d} {t}') for t,n in tools.most_common()]
print('PostToolUse lines by tool:',dict(posts.most_common(8)))
print('Edit/Write PreToolUse by file kind:'); [print(f'  {n:6d} {t:6s} {k}') for (t,k),n in sorted(kinds.items(),key=lambda x:-x[1])]
print('Edit/Write PreToolUse by where the file is:'); [print(f'  {n:6d} {t:6s} {k}') for (t,k),n in sorted(where.items(),key=lambda x:-x[1])]
print('left out, lines of measurement sessions:',dict(probes)); print('by who:',dict(who)); print('by session id:',dict(sids)); print('by tree:',dict(trees.most_common(12)))
