import re,json,collections
raw=open('/diagram/.clones/diagram-backlog/dev/review-ledger.md').read().split('\n')
rows=[]
for ln,l in enumerate(raw,1):
    if not re.match(r'\| 2026-11-(19|2\d) \| spec-fidelity \|',l): continue
    if 'MODE 4' not in l: continue
    c=[x.strip() for x in l.split('|')]
    fm=re.search(r'feature (\d{3})',c[3]); 
    if not fm or fm.group(1) not in('449','451'): continue
    feat=fm.group(1)
    t=c[5]; full=l
    task=None;src=''
    for pat,s in [(r'TASK=(T\d+)','TASK='),(r'task (T\d+)\b','c3'),(r'\b(?:451|449) (T\d+)\b','fT'),(r"\b(T\d+)['’]s (?:plan|section|review)",'poss'),(r'(?:for|on) (T\d+)\b','for')]:
        m=re.search(pat,c[3]+' '+t) if s!='TASK=' else re.search(pat,l)
        if m: task=m.group(1);src=s;break
    if not task:
        m=re.search(r'\b(T\d+)\b',t)
        if m: task=m.group(1);src='first'
    blocks='BLOCKS=1' in l or 'blocks of feature' in c[3] or "plan (plan-delta" in c[3] or re.search(r'blocks? of feature',c[3])
    rows.append(dict(ln=ln,date=c[1],feat=feat,task=task,src=src,blocks=bool(blocks),verdict=c[4],txt=t,line=l))
json.dump(rows,open('plan_rows.json','w'))
print(len(rows))
by=collections.defaultdict(list)
for r in rows:
    if r['task'] and not r['blocks'] and not r['verdict'].startswith('NOT-REV'): by[(r['feat'],r['task'])].append(r)
def cl(v): return 'B' if v.startswith(('BLOCKED','CHANGES')) else ('C' if v.startswith('CLEAR') else '?')
print('tasks',len(by))
first=collections.Counter(cl(v[0]['verdict']) for v in by.values())
print(first, 'ever blocked',sum(any(cl(r['verdict'])=='B' for r in v) for v in by.values()))
print(collections.Counter(r['src'] for v in by.values() for r in v))
json.dump({f'{k[0]}-{k[1]}':[(r['ln'],r['date'],cl(r['verdict']),r['src']) for r in v] for k,v in by.items()},open('by_task.json','w'))
