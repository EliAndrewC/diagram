import subprocess,re,json,glob,collections,statistics as st,datetime,pickle
C='/diagram/.clones/diagram-backlog'
def g(*a): return subprocess.run(['git','-C',C]+list(a),capture_output=True,text=True).stdout
def iso(s): return datetime.datetime.fromisoformat(s).timestamp()
# ticks
ticks=[]
for l in g('log','--since=2026-11-19','--format=%H|%cI|%s').splitlines():
    h,t,s=l.split('|',2)
    m=re.match(r'(449-rust-codebase|451-time-retro-and-efficiency): ((?:T\d+ ?)+)ticked',s)
    if m: ticks.append((iso(t),m.group(1)[:3],re.findall(r'T\d+',m.group(2)),h))
ticks.sort()
# bypass entries
B=[]
for f in glob.glob(C+'/dev/bypass-log/2026-11/*.json'):
    d=json.load(open(f)); u=d.get('utc','')
    if u<'2026-11-19': continue
    if 'T' in u and '-' not in u: u=datetime.datetime.strptime(u,'%Y%m%dT%H%M%SZ').isoformat()+'+00:00'
    else: u=u.replace('Z','+00:00')
    B.append((iso(u),d.get('target') or d.get('guard'),d.get('why') or d.get('reason') or ''))
B.sort()
def cls(t,w):
    if t.startswith('plan-gate'):
        wl=w.lower()
        if 'template' in wl or 'unworked' in wl or 'not started' in wl or 'unfilled' in wl: return 'plan-gate: unworked/unfilled template blocks stale'
        if 'reviewed clear' in wl: return 'plan-gate: reviewed CLEAR earlier, since touched'
        if 'withdrawn' in wl or 'moved' in wl: return 'plan-gate: withdrawn/moved task blocks'
        return 'plan-gate: other'
    return t.split(' ')[0]
# MODE 4 ledger rows
R=collections.Counter();RV=collections.defaultdict(list)
for l in open(C+'/dev/review-ledger.md'):
    if 'MODE 4' in l and l.startswith('| 2026-11-'):
        c=l.split('|')
        if c[1].strip()<'2026-11-19': continue
        desc=c[3]; fm=re.search(r'feature (\d+)',desc)
        if not fm: continue
        for t in re.findall(r'T\d+',desc.split('feature')[-1]):
            R[(fm.group(1),t)]+=1; RV[(fm.group(1),t)].append(c[4].strip()[:12])
rows=[];prev=iso('2026-11-19T00:00:00+00:00')
for t,f,tasks,h in ticks:
    ents=[b for b in B if prev<b[0]<=t]
    prev=t
    for task in tasks:
        fil=g('log','-S','] %s '%task,'--reverse','--format=%cI','--','specs/%s*/tasks.md'%f).splitlines()
        filed=iso(fil[0]) if fil else None
        rows.append(dict(f=f,task=task,t=t,filed=filed,ntask=len(tasks),esc=collections.Counter(cls(b[1],b[2]) for b in ents),escn=len(ents),rounds=R.get((f,task),0),verd=RV.get((f,task),[])))
pickle.dump(rows,open('m3rows.pkl','wb'))
# aggregate by landing (tick commit)
L=collections.defaultdict(list)
for r in rows: L[(r['t'])].append(r)
print('tasks ticked since 11-19',len(rows),'landings',len(L))
tot=collections.Counter()
for t,rs in L.items():
    for k,v in rs[0]['esc'].items(): tot[k]+=v
print('escapes per landing, by class:'); 
for k,v in tot.most_common(): print(f'  {k:55s} {v:4d} {v/len(L):.2f}/landing')
print('all escapes %d -> %.2f/landing'%(sum(tot.values()),sum(tot.values())/len(L)))
for feat in('449','451'):
    rs=[r for r in rows if r['f']==feat]; ls={r['t'] for r in rs}
    e=sum(sum(next(x for x in rows if x['t']==t)['esc'].values()) for t in ls)
    rr=[r['rounds'] for r in rs]
    print(feat,'tasks',len(rs),'landings',len(ls),'esc/landing %.2f'%(e/len(ls)),'mode4 rows/task mean %.2f med %s, tasks with 0 rows %d, BLOCKED/NOT-REV rows %d'%(st.mean(rr),st.median(rr),sum(1 for x in rr if x==0),sum(1 for r in rs for v in r['verd'] if v!='CLEAR')))
# filed->landed for tasks landed since 11-25T03:18Z (window) 
w0=iso('2026-11-25T03:18:19+00:00')
W=[r for r in rows if r['f']=='451' and r['t']>=w0 and r['filed']]
print('window 451 tasks with filing time',len(W))
d=[(r['t']-r['filed'])/60 for r in W]
print('filed->landed min: median %.0f min %.0f max %.0f'%(st.median(d),min(d),max(d)))
for r in sorted(W,key=lambda r:r['t']): print(r['task'],datetime.datetime.fromtimestamp(r['filed']).strftime('%m-%d %H:%M'),'->',datetime.datetime.fromtimestamp(r['t']).strftime('%m-%d %H:%M'),'%.0f min'%((r['t']-r['filed'])/60),'rounds',r['rounds'],r['verd'],'tasks-in-landing',r['ntask'])
