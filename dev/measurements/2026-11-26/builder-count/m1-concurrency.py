#!/usr/bin/env python3
"""m1: builder concurrency vs throughput on 2026-11-25/26 (read-only measurement).
Sources: the session transcript (streamed; Agent tool_use blocks, launch results, SendMessage, task-notifications)
and the guard's event log (.git/l7r-events/*.jsonl: Phase lines carry t0/t1/clone/make; land end lines carry landed).
usage: m1-concurrency.py [SINCE-ISO] [-v]"""
import json,re,sys,glob,statistics as st,collections
from datetime import datetime,timezone
P='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
EV='/diagram/.clones/diagram-backlog/.git/l7r-events'
SINCE=next((a for a in sys.argv[1:] if a[:2]=='20'),'2026-11-25T12:00')
V='-v' in sys.argv
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def hm(t): return datetime.fromtimestamp(t,timezone.utc).strftime('%m-%dT%H:%M')
calls={};agent2call={};sends=[];notes=[]
for line in open(P):
    if '"name":"Agent"' not in line and '"name":"SendMessage"' not in line and 'agentId' not in line and '<task-notification>' not in line: continue
    try: d=json.loads(line)
    except Exception: continue
    ts=d.get('timestamp','')
    if ts<SINCE: continue
    c=(d.get('message') or {}).get('content')
    if d.get('type')=='assistant' and isinstance(c,list):
        for b in c:
            if b.get('type')!='tool_use': continue
            i=b.get('input') or {}
            if b['name']=='Agent':
                calls[b['id']]=dict(id=b['id'],ts=ts,type=i.get('subagent_type','general-purpose'),desc=i.get('description',''),prompt=i.get('prompt',''))
            elif b['name']=='SendMessage': sends.append((ts,i.get('to')))
    elif d.get('type')=='queue-operation' and '<task-notification>' in str(d.get('content')):
        # some notifications reach the transcript only as a queue line (enqueue, then dequeue): the first sighting is the end
        for blk in re.findall(r'<task-notification>.*?</task-notification>',str(d['content']),re.S):
            g=lambda k:(re.search(r'<%s>(.*?)</%s>'%(k,k),blk,re.S) or [None,None])[1]
            if g('tool-use-id'): notes.append((ts,g('tool-use-id'),g('task-id'),int(g('duration_ms') or 0),int(g('subagent_tokens') or 0)))
    elif d.get('type')=='user':
        r=d.get('toolUseResult')
        if isinstance(r,dict) and r.get('agentId') and isinstance(c,list):
            for b in c:
                if b.get('type')=='tool_result' and b.get('tool_use_id') in calls:
                    agent2call[r['agentId']]=b['tool_use_id']; calls[b['tool_use_id']]['model']=r.get('resolvedModel','?')
                    if r.get('status')!='async_launched':
                        notes.append((ts,b['tool_use_id'],r['agentId'],r.get('totalDurationMs') or 0,r.get('totalTokens') or 0))
        s=c if isinstance(c,str) else json.dumps(c)
        if '<task-notification>' in s and d.get('origin'):
            for blk in re.findall(r'<task-notification>.*?</task-notification>',s,re.S):
                g=lambda k:(re.search(r'<%s>(.*?)</%s>'%(k,k),blk,re.S) or [None,None])[1]
                notes.append((ts,g('tool-use-id'),g('task-id'),int(g('duration_ms') or 0),int(g('subagent_tokens') or 0)))
def why_not(c):
    """None = a builder: a general-purpose agent that WRITES in a clone or worktree. Measurers, claims rounds,
    cascades (check coordinators), triage, audits and brief-writing are not builders."""
    p=c['prompt'];d=c['desc']
    if c['type']!='general-purpose': return 'typed agent'
    if not re.search(r'/diagram/\.clones/diagram-backlog',p): return 'no tree named'
    if re.search(r'^(MEASUREMENT|Measure|Take four read-only|Run the claims round|Coordinate|Triage|Audit)',p): return 'measure/check coordinator (prompt)'
    if re.search(r'[Cc]laims round|cascade|Triage|Audit|briefs|probe:|Guesses-tab|Close .*rows|^Measure|^File feature|Re-run',d) and not re.search(r'^(Finish|Build|T250)',d): return 'measure/check coordinator (desc)'
    return None
BY=collections.defaultdict(list)  # agent id -> its tool-call times
MK=collections.defaultdict(collections.Counter)  # agent id -> make target -> foreground minutes
for f in glob.glob(EV+'/*.jsonl'):
    for l in open(f):
        if '"by"' not in l: continue
        try: d=json.loads(l)
        except Exception: continue
        if d.get('t','')>=SINCE and isinstance(d.get('by'),str):
            BY[d['by']].append(T(d['t']))
            if d.get('ev')=='PostToolUse' and d.get('ms'): MK[d['by']][d.get('make') or ('(agent wait)' if d.get('tool') in ('Agent','Task') else '(other tool)')]+=d['ms']/60000
OUTTOK=collections.Counter()  # agent id -> max cumulative output tokens at a SubagentStop (work done; subagent_tokens is context size)
BLT=set()
for f in glob.glob(EV+'/*.jsonl'):
    for l in open(f):
        if '"SubagentStop"' not in l: continue
        try: d=json.loads(l)
        except Exception: continue
        if isinstance(d.get('tok'),dict): OUTTOK[d.get('aid')]=max(OUTTOK[d.get('aid')],d['tok'].get('out',0))
B={}
for k,v in calls.items():
    w=why_not(v)
    if w is None: B[k]=v
    elif V and v['type']=='general-purpose': print('NOT-BUILDER',v['ts'][5:16],w,'|',v['desc'][:60],file=sys.stderr)
for k,v in list(B.items()):
    v['tree']=(re.search(r'/diagram/\.clones/([a-z0-9-]+)',v['prompt']) or ['','?'])[1]
    v['task']=(re.search(r'\bT\d{2,3}\b',v['desc']+' '+v['prompt'][:300]) or ['-'])[0]
    aid=next((a for a,t in agent2call.items() if t==k),None); v['aid']=aid
    ns=sorted(n for n in notes if n[1]==k or (aid and n[2]==aid))
    ss=sorted(s[0] for s in sends if aid and s[1]==aid)
    v['tok']=max((n[4] for n in ns),default=0); v['durms']=sum({n[3] for n in ns})
    # ONE stretch: launch -> the agent's LAST TOOL CALL in the guard's event log (its lines carry `by`), never before its first
    # notification. A builder notifies each time it stops with no live child and is woken again by its own background commands
    # (closing checks), so the first notification is early; the last can be a wake that did nothing (T240: tools to 28 min, a
    # last notification at 41), so it is late. duration_ms counts from launch.
    last=max(BY.get(aid,[0]))
    v['stretch']=[(T(v['ts']),max(T(ns[0][0]),min(last,T(ns[-1][0])+60)))] if ns else []; run=None
    v['first']=(T(ns[0][0])-T(v['ts']))/60 if ns else 0; v['stops']=len({n[3] for n in ns})
    v['open']=run is not None
    if V: print('NOTES',v['ts'][5:16],v['desc'][:40],[(round((T(n[0])-T(v['ts']))/60),round(n[3]/60000)) for n in ns],'sends',[round((T(x)-T(v['ts']))/60) for x in ss],file=sys.stderr)
    if not v['stretch']:
        if V: print('NO-END',v['ts'][5:16],v['desc'][:60],file=sys.stderr)
        del B[k]
allst=[(a,b,k) for k,v in B.items() for a,b in v['stretch']]
def nb(t,skip=None): return sum(1 for a,b,j in allst if j!=skip and a<=t<b)
def avg_conc(v,k):
    tot=w=0
    for a,b in v['stretch']:
        pts=sorted({a,b}|{x for s,e,j in allst if j!=k for x in (s,e) if a<x<b})
        for x,y in zip(pts,pts[1:]): tot+=(y-x)*(1+nb((x+y)/2,k)); w+=y-x
    return tot/w
rows=sorted(B.values(),key=lambda v:v['ts'])
for v in rows:
    v['mins']=sum(b-a for a,b in v['stretch'])/60; v['ac']=avg_conc(v,v['id']); v['at_start']=1+nb(v['stretch'][0][0]+1,v['id']); v['grp']=min(4,max(1,round(v['ac'])))
    v['kind']='comment/doc' if re.search(r'T250|talk measurements|agenda items|Narrow decision|T439|T251',v['desc']) else 'code'
out=[]
out.append('## Every builder dispatch since '+SINCE+' (UTC)\n\n| start | tree | task | kind | min to first stop | min to last tool call | tokens k | builders at start | avg builders | stops |\n|---|---|---|---|---|---|---|---|---|---|')
for v in rows: out.append(f"| {v['ts'][5:16]} | {v['tree'].replace('diagram-backlog','db')} | {v['task']} | {v['kind']} | {v['first']:.0f} | {v['mins']:.0f} | {v['tok']/1000:.0f} | {v['at_start']} | {v['ac']:.2f} | {v['stops']} |")
out.append('\n## Code builders only: minutes per 10k OUTPUT tokens (a size-normalized pace: cumulative tok.out from the SubagentStop lines; subagent_tokens is the final context size and saturates at the cap)\n\n| n | code builders with tok.out | median output tokens k | median min per 10k output tokens, to last tool call | to first stop | vs n=1 | worktree builders among them |\n|---|---|---|---|---|---|---|')
b1=None
for g in (1,2,3,4):
    r=[v for v in rows if v['grp']==g and v['kind']=='code' and v['tok']]
    if not r: continue
    r=[v for v in r if OUTTOK[v['aid']]]; m=st.median(v['mins']/(OUTTOK[v['aid']]/1e4) for v in r); f1=st.median(v['first']/(OUTTOK[v['aid']]/1e4) for v in r); b1=b1 or m; o=st.median(OUTTOK[v['aid']]/1e3 for v in r)
    out.append(f"| {g} | {len(r)} | {o:.0f} | {m:.1f} | {f1:.1f} | {m/b1:.2f}x | {sum(v['tree']!='diagram-backlog' for v in r)} |")
out.append('\n## Code builders: foreground minutes inside make targets, per builder (the event log\'s PostToolUse ms by agent; a backgrounded run is not in it)\n\n| n | builders | models | rust-test | closing-checks | quick | crate-checks + rust-lint | decide + plan-verdict | all make targets | all tool time | builder min |\n|---|---|---|---|---|---|---|---|---|---|---|')
for g in (1,2,3,4):
    r=[v for v in rows if v['grp']==g and v['kind']=='code']
    if not r: continue
    f=lambda *ks: sum(MK[v['aid']][k] for v in r for k in ks)/len(r)
    allmk=sum(x for v in r for k,x in MK[v['aid']].items() if not k.startswith('('))/len(r); alltool=sum(sum(MK[v['aid']].values()) for v in r)/len(r)
    mods=collections.Counter(v.get('model','?').replace('claude-','') for v in r)
    out.append(f"| {g} | {len(r)} | {', '.join(f'{k} {n}' for k,n in mods.items())} | {f('rust-test'):.1f} | {f('closing-checks'):.1f} | {f('quick'):.1f} | {f('crate-checks','rust-lint'):.1f} | {f('decide','plan-verdict'):.1f} | {allmk:.1f} | {alltool:.1f} | {st.mean(v['mins'] for v in r):.0f} |")
ev=sorted({x for a,b,_ in allst for x in (a,b)}); wall=collections.Counter()
for x,y in zip(ev,ev[1:]): wall[nb((x+y)/2)]+=(y-x)/60
out.append('\n## Builders by concurrency (avg builders over its life, rounded)\n\n| n | builders | of them code | median min to first stop | median min | mean min | mean tokens k | tokens k per builder-min | wall min with exactly n running |\n|---|---|---|---|---|---|---|---|---|')
for g in (1,2,3,4):
    r=[v for v in rows if v['grp']==g]
    if not r: continue
    m=[v['mins'] for v in r]; t=[v['tok']/1000 for v in r]
    out.append(f"| {g} | {len(r)} | {sum(v['kind']=='code' for v in r)} | {st.median(v['first'] for v in r):.0f} | {st.median(m):.0f} | {st.mean(m):.0f} | {st.mean(t):.0f} | {sum(t)/sum(m):.1f} | {wall[g]+(wall[5]+wall[6] if g==4 else 0):.0f} |")
# ---- the event log: Phase lines (like-for-like spans) and landings
ph=[];lands=[]
for f in glob.glob(EV+'/*.jsonl'):
    for l in open(f):
        if '"Phase"' not in l: continue
        try:d=json.loads(l)
        except Exception: continue
        if d.get('t0','')<SINCE or d.get('code')!=0: continue
        if d['src']=='land':
            if d.get('step')=='end' and d.get('landed') and d.get('sid','').startswith('c6fd72d1'): lands.append((T(d['t1']),d.get('tasks') or [d.get('task')]))
            continue
        if d.get('step')=='cached': continue
        a,b=T(d['t0']),T(d['t1'])
        if b-a<1: continue
        ph.append((d['src'],d['step'],d.get('name') or ','.join(d.get('crates') or []),a,b,d.get('clone',''),d.get('make','')))
def load2(p):  # other trees with a Phase span overlapping this one's midpoint (landings, gates and measurers count here)
    m=(p[3]+p[4])/2; return 1+len({q[5] for q in ph if q[5]!=p[5] and q[3]<=m<q[4]})
def ratios(sel,loadf):
    by=collections.defaultdict(lambda:collections.defaultdict(list))
    for p in ph:
        if sel(p): by[p[:3]][min(4,max(1,loadf(p)))].append(p[4]-p[3])
    res=collections.defaultdict(list);secs=collections.Counter();cnt=collections.Counter()
    for k,d in by.items():
        if len(d.get(1,[]))<3: continue
        base=st.median(d[1])
        for n,xs in d.items():
            if n==1 or len(xs)>=2: res[n].append((st.median(xs)/base,len(xs)*base)); secs[n]+=sum(xs); cnt[n]+=len(xs)
    line=[]
    for n in (1,2,3,4):
        if not res[n]: line.append('-'); continue
        w=sum(x[1] for x in res[n]); line.append(f"{sum(r*x for r,x in res[n])/w:.2f}x (median key {st.median(r for r,_ in res[n]):.2f}x; {cnt[n]} spans, {len(res[n])} keys, {secs[n]/60:.0f} min)")
    return line
out.append('\n## The same span at each load: duration / that span\'s own median at load 1 (time-weighted mean over keys)\n\nA key is (source, step, suite name or crate). Spans under 1 s, cached and failed ones are dropped; a key needs 3 spans at load 1.\n\n| spans | load measured as | 1 | 2 | 3 | 4+ |\n|---|---|---|---|---|---|')
for name,sel in (('hook suites (no build cache)',lambda p:p[0]=='hooks'),('rust build + cover-build (cold in a new worktree)',lambda p:p[0]=='rust' and 'build' in p[1]),('rust lint',lambda p:p[0]=='rust' and p[1]=='lint'),('rust test + cover-run',lambda p:p[0]=='rust' and p[1] in('test','cover-run')),('make quick, whole',lambda p:p[0]=='quick')):
    out.append(f"| {name} | builders running at t0 | "+' | '.join(ratios(sel,lambda p:max(1,nb(p[3]))))+' |')
    out.append(f"| {name} | trees with an overlapping span | "+' | '.join(ratios(sel,load2))+' |')
# ---- whole closing-checks runs: one tree's hook-suite spans under make closing-checks, clustered (a 60 s gap splits runs);
# a FULL run has 40+ suites, so a one-suite re-run is not compared with a whole one
cc=collections.defaultdict(list)
for p in ph:
    if p[0]=='hooks' and p[6]=='closing-checks': cc[p[5]].append(p)
runs=[]
for clone,ps in cc.items():
    ps.sort(key=lambda p:p[3]); cur=[ps[0]]
    for p in ps[1:]:
        if p[3]>max(q[4] for q in cur)+60: runs.append(cur); cur=[p]
        else: cur.append(p)
    runs.append(cur)
full=[(min(p[3] for p in r),max(p[4] for p in r),r[0][5],sum(p[4]-p[3] for p in r),len(r)) for r in runs if len(r)>=40]
out.append('\n## A whole closing-checks run (40+ hook suites in one tree), by what ran beside it\n\n| beside it | runs | median wall s | mean wall s | vs alone | median suite-seconds (sum of its suites) | vs alone |\n|---|---|---|---|---|---|---|')
def beside(r): return sum(1 for q in full if q[2]!=r[2] and q[0]<r[1] and q[1]>r[0])
def bld(r): return max(1,nb((r[0]+r[1])/2))
wt=lambda r:r[2].rstrip('/').endswith('diagram-backlog')
firsts={min(q for q in full if q[2]==t) for t in {r[2] for r in full}}
out.append('\n### The same runs in builder worktrees, a tree\'s FIRST whole run apart from its later ones\n\n| run | builders at midpoint | runs | trees | median wall s | min - max |\n|---|---|---|---|---|---|')
for lab,sel in (('first in its tree',lambda r:r in firsts),('later',lambda r:r not in firsts)):
    for n in range(1,6):
        xs=[r for r in full if not wt(r) and sel(r) and bld(r)==n]
        if xs: out.append(f"| {lab} | {n} | {len(xs)} | {len({r[2] for r in xs})} | {st.median(r[1]-r[0] for r in xs):.0f} | {min(r[1]-r[0] for r in xs):.0f} - {max(r[1]-r[0] for r in xs):.0f} |")
xs=[r for r in full if wt(r)]
out.append(f"| the session clone, any | 1 | {len(xs)} | 1 | {st.median(r[1]-r[0] for r in xs):.0f} | {min(r[1]-r[0] for r in xs):.0f} - {max(r[1]-r[0] for r in xs):.0f} |")
out.append('\nSpans at 3 or more builders, by tree: '+'; '.join(f"{k[0]} {k[1].split('/')[-1]} {n} spans" for k,n in sorted(collections.Counter((('hooks' if p[0]=='hooks' else p[0]+' '+p[1]),p[5]) for p in ph if nb(p[3])>=3 and p[0] in('hooks','rust','quick')).items())))
for title,f,keep in (('other full runs overlapping',beside,lambda r:True),('builders at its midpoint, all trees',bld,lambda r:True),('builders at its midpoint, the session clone only',bld,wt),('builders at its midpoint, builder worktrees only',bld,lambda r:not wt(r))):
    base=None
    for n in range(0,6):
        xs=[r for r in full if f(r)==n and keep(r)]
        if not xs: continue
        w=st.median(r[1]-r[0] for r in xs); ss=st.median(r[3] for r in xs)
        if base is None: base=(w,ss)
        out.append(f"| {title}: {n} | {len(xs)} | {w:.0f} | {st.mean(r[1]-r[0] for r in xs):.0f} | {w/base[0]:.2f}x | {ss:.0f} | {ss/base[1]:.2f}x |")
if V:
    for r in sorted(full): print('CCRUN',hm(r[0]),r[2].split('/')[-1].replace('diagram-backlog','db'),'wall',round(r[1]-r[0]),'suite-s',round(r[3]),'builders',bld(r),'beside',beside(r),file=sys.stderr)
# ---- throughput by era. RULE: an era opens at the first dispatch that raises the count of builders at once to a level not
# seen before (2, then 3+) and runs to the next era's opening; landing and merging gaps stay inside. Tasks landed are the
# event log's land end lines with landed true, inside the era.
t2=min((v['stretch'][0][0] for v in rows if v['at_start']>=2),default=None); t3=min((v['stretch'][0][0] for v in rows if v['at_start']>=3),default=None)
t2=min(t2,min(a for a,b,k in allst if any(a2<=a<b2 and k2!=k for a2,b2,k2 in allst)))-1
t3s=[a for a,b,k in allst if nb(a+1)>=3]; t3=min(t3s)-1 if t3s else None
# the 3+ era opens at the start of the earliest builder still running when the count first reached 3
if t3: t3=min(a for a,b,k in allst if a<=t3+2<b)
first=min(a for a,b,_ in allst); last=max(b for a,b,_ in allst)
eras=[('one at a time',first,t2),('two at a time',t2,t3 or last),('three and four at a time',t3,last)] if t3 else [('one',first,t2),('two',t2,last)]
out.append('\n## Throughput by era (an era opens when the builder count first reaches a new level; landing and merge gaps stay inside)\n\n| era | window (UTC) | wall min | builders | builder-min | builder-min per wall hour | % wall at 0 / 1 / 2 / 3+ builders | tokens M | builder-built tasks landed (distinct) of all this session landed | landed per wall hour | builder-min per landed task |\n|---|---|---|---|---|---|---|---|---|---|---|')
for name,a,b in eras:
    bm=sum(max(0,min(y,b)-max(x,a)) for x,y,_ in allst)/60; W=(b-a)/60
    pts=sorted({a,b}|{x for s,e,_ in allst for x in (s,e) if a<x<b}); share=collections.Counter()
    for x,y in zip(pts,pts[1:]): share[min(3,nb((x+y)/2))]+=(y-x)/60
    who=[v for v in rows if a<=v['stretch'][0][0]<b]; tok=sum(v['tok'] for v in who)/1e6
    built={x for v in rows for x in re.findall(r'T\d{2,3}',v['desc'])}; ld=len({x for tt,t in lands if a<tt<=b for x in t if x in built}); allld=sum(len(t) for tt,t in lands if a<tt<=b)
    out.append(f"| {name} | {hm(a)} - {hm(b)} | {W:.0f} | {len(who)} | {bm:.0f} | {60*bm/W:.0f} | {' / '.join(f'{100*share[i]/W:.0f}' for i in range(4))} | {tok:.1f} | {ld} of {allld} | {60*ld/W:.2f} | {bm/ld if ld else 0:.0f} |")
out.append('\nwall minutes by exact builder count: '+', '.join(f'{n}: {w:.0f}' for n,w in sorted(wall.items()) if n))
print('\n'.join(out))
