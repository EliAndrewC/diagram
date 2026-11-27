# 451 T353: a week (2026-11-20..27 UTC) of the coordinating sessions' Agent dispatches (t353-extract.py) - the ad-hoc ones naming
# no pool tree and no marker: which wrote source (the Edit/Write tools only, a floor: a Bash write is not counted), in which tree,
# and which carried a STOP POINT line. A tree is named as builder_brief_hooks::names reads it: the path ended at no name character.
import json,re,glob,os,collections
P=os.path.expanduser('~/.claude/projects/-diagram/')
d=json.load(open('t353-dispatches.json'))
idx={os.path.basename(f)[6:-6]:f for f in glob.glob(P+'*/subagents/agent-*.jsonl')}
POOL=re.compile(r'/diagram/\.clones/diagram-backlog-(?:t\d+|b\d+)(?![A-Za-z0-9_-])')
CLONE=re.compile(r'/diagram/\.clones/diagram-backlog(?![A-Za-z0-9_-])')
TREE=re.compile(r'/diagram/\.clones/([A-Za-z0-9_.-]+)')
STOP=re.compile(r'(?m)^[ \t]*STOP POINT')
POOLAT,GUARDAT='2026-11-26T15:28','2026-11-26T22:02'   # T285 landed 10:28 -05:00, T334 17:02 -05:00
def written(aid):
    f=idx.get(aid or '')
    if not f: return None
    trees=collections.Counter()
    for line in open(f,errors='replace'):
        if '"tool_use"' not in line: continue
        try: r=json.loads(line)
        except Exception: continue
        for b in (r.get('message') or {}).get('content') or []:
            if isinstance(b,dict) and b.get('type')=='tool_use' and b['name'] in ('Edit','Write','NotebookEdit','MultiEdit'):
                m=TREE.match((b.get('input') or {}).get('file_path',''))
                if m: trees[m.group(1)]+=1
    return trees
first_stop=min(x['ts'] for x in d if STOP.search(x['prompt']))
by=collections.Counter();rows=[]
for x in d:
    t=x['type'] or ''
    if t not in ('','general-purpose','claude'): continue
    p=x['prompt']
    if p.lstrip().startswith('Run the claims round') or POOL.search(p) or re.search(r'(?m)^BUILDER-BRIEF ',p): continue
    era='1-before-pool' if x['ts']<POOLAT else ('2-pool-no-guard' if x['ts']<GUARDAT else '3-guard')
    s=written(x['agent'])
    k='no-transcript' if s is None else ('reader' if not s else ('wrote-clone' if 'diagram-backlog' in s else 'wrote-other-tree'))
    stop='STOP' if STOP.search(p) else '-'
    named='names-clone' if CLONE.search(p) else '-'
    by[(era,k,stop,named,'after-first-STOP' if x['ts']>=first_stop else 'before')]+=1
    rows.append((x['ts'][:16],era,k,stop,named,x['desc'][:60],','.join(sorted(s or []))))
print('first STOP POINT line:',first_stop)
for k in sorted(by): print(by[k],*k,sep='\t')
with open('t353-week.tsv','w') as f:
    f.write('ts\tera\tverdict\tstop\tnames the clone\tdesc\ttrees written (Edit/Write)\n')
    for r in sorted(rows): f.write('\t'.join(r)+'\n')
