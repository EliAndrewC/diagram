import json,re,sys,datetime as D,bisect
from collections import defaultdict
def ts(s): return D.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def hm(t): return D.datetime.fromtimestamp(t,D.timezone.utc).strftime('%H:%M')
W0=ts('2026-11-26T17:00:00Z'); W1=ts(sys.argv[1])
T='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
use={}; aid_tree={}
for l in open(T,errors='replace'):
    if '"Agent"' not in l and 'agentId' not in l: continue
    try: r=json.loads(l)
    except Exception: continue
    m=r.get('message') or {}
    c=m.get('content')
    if not isinstance(c,list): continue
    for b in c:
        if not isinstance(b,dict): continue
        if b.get('type')=='tool_use' and b.get('name')=='Agent':
            p=(b.get('input') or {}).get('prompt','')
            tr=re.search(r'/diagram/\.clones/(diagram-backlog-(?:t\d+|b\d+))',p)
            if tr: use[b['id']]=tr.group(1)
        if b.get('type')=='tool_result' and b.get('tool_use_id') in use:
            txt=json.dumps(b.get('content'))
            a=re.search(r'agentId: (a[0-9a-f]{12,})',txt)
            if a: aid_tree[a.group(1)]=use[b['tool_use_id']]
print('builders mapped to a tree:',len(aid_tree))
ev=[]
for l in open('.git/l7r-events/451-time-retro-and-efficiency.jsonl'):
    if '2026-11-26T1' not in l and '2026-11-26T2' not in l and '2026-11-27T' not in l: continue
    try: ev.append(json.loads(l))
    except Exception: pass
busy=defaultdict(list); st=defaultdict(list); sp=defaultdict(list)
for e in ev:
    a=e.get('aid')
    if a in aid_tree:
        if e.get('ev')=='SubagentStart': st[a].append(ts(e['t']))
        if e.get('ev')=='SubagentStop': sp[a].append(ts(e['t']))
for a in st:
    s=min(st[a]); e=max(sp[a]) if sp.get(a) else W1
    if e<s: e=W1
    busy[aid_tree[a]].append((s,e))
ph=sorted((ts(e['t0']),ts(e['t1'])) for e in ev if e.get('ev')=='Phase' and e.get('make')=='land' and e.get('t0') and ts(e['t1'])>W0)
runs=[]
for a,b in ph:
    if runs and a-runs[-1][1]<90: runs[-1][1]=max(runs[-1][1],b)
    else: runs.append([a,b])
allm=sorted([(ts(e['t']),'p') for e in ev if e.get('ev')=='UserPromptSubmit' and str(e.get('sid','')).startswith('c6fd72d1')]+[(ts(e['t']),'s') for e in ev if e.get('ev')=='Stop' and str(e.get('sid','')).startswith('c6fd72d1')])
tm=[x for x,_ in allm]
def stopped(t):
    i=bisect.bisect_right(tm,t)-1
    return i>=0 and allm[i][1]=='s'
gmp=sorted(ts(e['t']) for e in ev if e.get('ev')=='UserPromptSubmit' and e.get('gm') and str(e.get('sid','')).startswith('c6fd72d1'))
tot=defaultdict(float); rows=[]
first={'diagram-backlog-b1':ts('2026-11-26T20:38:58Z')}
for tr,L in sorted(busy.items()):
    L.sort(); merged=[]
    for s,e in L:
        if merged and s<=merged[-1][1]: merged[-1][1]=max(merged[-1][1],e)
        else: merged.append([s,e])
    t0=max(W0,first.get(tr,W0)); cur=t0; gaps=[]
    for s,e in merged:
        if e<t0: continue
        if s>cur: gaps.append((cur,s))
        cur=max(cur,e)
    if cur<W1: gaps.append((cur,W1))
    for a,b in gaps:
        t=a; d=defaultdict(float)
        while t<b:
            k='a landing running' if any(x<=t<y for x,y in runs) else ('session stopped, its turn ended' if stopped(t) else 'session in its own turn')
            d[k]+=min(10,b-t)/60; t+=10
        for k,v in d.items(): tot[k]+=v
        rows.append((hm(a),tr[-4:],(b-a)/60,dict((k,round(v,1)) for k,v in d.items())))
    print(tr,'busy %.0f min of %.0f'%(sum(min(e,W1)-max(s,t0) for s,e in merged if e>t0)/60,(W1-t0)/60))
for r in sorted(rows):
    if r[2]>=3: print('  %s %s idle %5.1f  %s'%r)
print('tree-idle minutes by what the session was doing:',{k:round(v) for k,v in tot.items()},'total',round(sum(tot.values())))
print('landing runs total min %.0f, count %d'%(sum(b-a for a,b in runs)/60,len(runs)))
