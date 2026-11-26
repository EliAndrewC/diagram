import json,re,collections,datetime,os
rows=json.load(open('plan_rows.json'))
vf=json.load(open('verdict_files.json'))
by=collections.defaultdict(list)
for r in rows:
    if r['task'] and not r['blocks'] and not r['verdict'].startswith('NOT-REV'): by[(r['feat'],r['task'])].append(r)
cl=lambda v:'B' if v.startswith(('BLOCKED','CHANGES')) else 'C'
res={}
for k,v in by.items():
    bl=[r for r in v if cl(r['verdict'])=='B']
    if not bl: continue
    d0=datetime.datetime.strptime(bl[0]['date'],'%Y-%m-%d')
    n=k[1][1:].lstrip('0')
    pat=re.compile(r'(?<![0-9a-z])[tT]-?0*%s(?![0-9])'%n)
    cands=[]
    for m,p,nd,nl,vd in vf:
        if not pat.search(p): continue
        dm=datetime.datetime.fromtimestamp(m)
        if not (d0-datetime.timedelta(hours=6)<=dm<=d0+datetime.timedelta(days=1,hours=8)): continue
        if k[0] not in p and re.search(r'44[0-9]|45[0-9]',p): continue
        cands.append((m,p,nd,nl,vd))
    res[k]=dict(seq=''.join(cl(r['verdict']) for r in v),date=bl[0]['date'],cands=sorted(cands))
json.dump({f'{a}-{b}':v for (a,b),v in res.items()},open('match.json','w'))
print(len(res),sum(1 for v in res.values() if any(c[3]>0 for c in v['cands'])), sum(1 for v in res.values() if v['cands']))
