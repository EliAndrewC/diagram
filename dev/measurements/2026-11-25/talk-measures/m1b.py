import pickle,json,statistics as st
rows={r['id']:r for r in pickle.load(open('m1.pkl','rb'))}
for f in('A','B'):
    for l in open(f'briefs/class{f}.jsonl'):
        l=l.strip()
        if l.startswith('{'):
            d=json.loads(l)
            if d['id'] in rows: rows[d['id']].update(cj=d['jobs'],cfirst=d.get('first'),cmeas=bool(d.get('began_with_measure')),cats=d.get('cats'))
R=[r for r in rows.values() if 'cj' in r]
print(len(R),'of',len(rows),'classified; hit',sum(r['hit'] for r in R))
def tab(name,key,order=None):
    G={}
    for r in R: G.setdefault(key(r),[]).append(r)
    print(f'-- by {name}')
    for k in sorted(G,key=lambda k:(order or str)(k)):
        g=G[k];h=sum(x['hit'] for x in g)
        print(f'  {str(k):10s} n={len(g):3d} handoff/cap={h:3d} rate={h/len(g):.2f} | med prompt {st.median(x["plen"] for x in g):.0f} chars, med calls {st.median(x["calls"] for x in g):.0f}, med out {st.median(x["out"] for x in g)/1000:.0f}k, med files {st.median(x["edited"] for x in g):.0f}')
tab('jobs in brief',lambda r:r['cj'])
tab('jobs 1-2 / 3 / 4+',lambda r:'1-2' if r['cj']<=2 else '3' if r['cj']==3 else '4+')
tab('began with measure (brief)',lambda r:r['cmeas'])
tab('began with measure (behavior: measuring cmd in first 6 calls)',lambda r:r['beh'])
tab('either',lambda r:r['cmeas'] or r['beh'])
tab('files edited',lambda r:'1-3' if r['edited']<=3 else '4-8' if r['edited']<=8 else '9+')
tab('files x jobs>=3',lambda r:('1-3' if r['edited']<=3 else '4-8' if r['edited']<=8 else '9+')+('/J3+' if r['cj']>=3 else '/J<3'))
tab('prompt length',lambda r:'<3k' if r['plen']<3000 else '3-4.5k' if r['plen']<4500 else '4.5k+')
tab('calls',lambda r:'<60' if r['calls']<60 else '60-119' if r['calls']<120 else '120+')
print('hit breakdown: refused',sum(r['refused'] for r in R),'handoff written',sum(r['handoff'] for r in R),'ctx>=290k',sum(r['ctxmax']>=290000 for r in R))
print('hit by out tokens: ',[ (lo,round(sum(r['hit'] for r in R if lo<=r['out']<lo+40000)/max(1,sum(1 for r in R if lo<=r['out']<lo+40000)),2),sum(1 for r in R if lo<=r['out']<lo+40000)) for lo in range(0,200000,40000)])
json.dump(R,open('m1-table.json','w'))
