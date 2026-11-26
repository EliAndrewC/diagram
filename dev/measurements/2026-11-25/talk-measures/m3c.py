import re,pickle,collections,statistics as st,datetime
rows=pickle.load(open('m3rows.pkl','rb'))
R=collections.defaultdict(list)
miss=0
for l in open('/diagram/.clones/diagram-backlog/dev/review-ledger.md'):
    if not (l.startswith('| 2026-11-') and 'MODE 4' in l): continue
    c=l.split('|')
    if c[1].strip()<'2026-11-19': continue
    fm=re.search(r'feature (\d+)',c[3]); 
    if not fm: continue
    m=re.search(r'task (T\d+)',c[3]) or re.search(r'TASK=(T\d+)',l) or re.search(r'(T\d+)',c[5])
    if not m: miss+=1;continue
    R[(fm.group(1),m.group(1))].append(c[4].strip().split()[0].strip('*'))
print('ledger rows unattributed',miss,'rows attributed',sum(len(v) for v in R.values()))
for feat in('449','451'):
    rs={(r['f'],r['task']):r for r in rows if r['f']==feat}
    ns=[len(R.get(k,[])) for k in rs]
    nonclear=sum(1 for k in rs for v in R.get(k,[]) if v!='CLEAR')
    multi=sum(1 for n in ns if n>=2); three=sum(1 for n in ns if n>=3)
    print(feat,'tasks',len(ns),'rounds mean %.2f median %s; 0 rounds %d; >=2 rounds %d; >=3 rounds %d; non-CLEAR round rows %d (%.2f per task)'%(st.mean(ns),st.median(ns),ns.count(0),multi,three,nonclear,nonclear/len(ns)))
# window T226-T259
w=[r for r in rows if r['f']=='451' and 226<=int(r['task'][1:])<=259]
seen=set();ns=[]
for r in w:
    if r['task'] in seen: continue
    seen.add(r['task']);ns.append(len(R.get(('451',r['task']),[])))
print('451 T226-T259 landed tasks',len(ns),'rounds mean %.2f'%st.mean(ns),'0:',ns.count(0),'1:',ns.count(1),'2+:',sum(n>=2 for n in ns))
