#!/usr/bin/env python3
"""m11-decomp.py: the spec-kit task route decomposed for small tasks, from the builders' and reviewers' transcripts
and the event log. Read-only. Convention: on an actor's transcript each gap between consecutive lines is booked to the
step of the line that ENDS it - an assistant line's gap (the model's turn) to the step of the tool it calls, a tool
result's gap (the tool's run) to that tool's step, a notification's gap (the builder stopped, waiting) to the step of
the background work last launched. Tokens: each API message's usage once, booked to the step of the tool it calls;
weighted = fresh in + 0.1 cache read + 1.25 cache write + 5 out (the 2026-11-25 context-cap measure's weights)."""
import json,re,collections,sys,datetime,statistics as st,pickle,os
SID='c6fd72d1-ab6c-4736-b723-0697a1f5ca51'
PR='/home/agent/.claude/projects/-diagram/'
SUB=PR+SID+'/subagents/agent-%s.jsonl'
EV='/diagram/.clones/diagram-backlog/.git/l7r-events/451-time-retro-and-efficiency.jsonl'
OUT=os.path.dirname(os.path.abspath(__file__))
B={'T252':'a4e71d9c9340532eb','T263':'ae16eb1531e2d7f1a','T267':'a28e4ae596c3ea67d','T268':'a2618c8b8cf48fbbd','T269':'a64c970141ee45e77','T270':'a0dac9729ccdc3074','T271':'abd213a4ab68a3b72','T272':'ac6e4b30328810149','T248':'a0d2f2fb977d1a6d3','T249':'ac88c008c893db684','T262':'ac0165a2ade526e95'}
SMALL=['T252','T263','T267','T268','T269','T270','T271','T272']
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def w(u): return u.get('input_tokens',0)+0.1*u.get('cache_read_input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+5*u.get('output_tokens',0)
def raw(u): return u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('output_tokens',0)
STEPS=['a filing/bookkeeping','b code+tests (read, write, run)','c plan section','d decide + plan review','e claims','f closing checks','g landing+commit','r builder report/handoff','i idle after its report (woken, nothing in flight)','x other/unmapped']
def bash_step(cmd):
    mk=re.findall(r'\bmake\s+(?:-\S+\s+)*(?:[A-Z_]+=\S+\s+)*([a-z][a-z0-9-]+)',cmd)
    head=cmd[:320]
    if re.search(r"<<\s*'?(EOF|PY)|\bsed -i\b",head):
        if 'plan.md' in head: return 'c'
        if 'tasks.md' in head: return 'a'
        if 'plan-review' in head: return 'd'
        if 'l7r-handoffs' in head: return 'r'
        return 'b'
    s=set(mk)
    if s&{'land','done','land-tooling','cohort-landing','land-batch'} or re.search(r'(^|&&|;|\|\||\n)\s*(scripts/sync-with-main\.sh\s+done|git\s+(-C\s+\S+\s+)?(commit|push|cherry-pick)\b)',cmd): return 'g'
    if s&{'task-add','task-start','tick','set-down'}: return 'a'
    if s&{'closing-checks'}: return 'f'
    if s&{'decide','plan-delta','arbiter-ask','arbiter-bundle','plan-bundle','record-answer','ledger-owed'} or 'plan-review.json' in cmd or '/tmp/l7r-check/plan-' in cmd: return 'd'
    if any(x.startswith('claims') for x in s): return 'e'
    if re.search(r'-closing\.log',cmd): return 'f'
    if re.search(r"<<\s*'?EOF",cmd) and re.search(r'specs/\S*plan\.md',cmd): return 'c'
    if re.search(r"<<\s*'?EOF",cmd) and re.search(r'specs/\S*tasks\.md',cmd): return 'a'
    if re.search(r'l7r-handoffs',cmd): return 'r'
    return 'b'
def tool_step(name,i):
    if name=='Bash': return bash_step(i.get('command',''))
    if name in('Edit','Write','Read','NotebookEdit'):
        p=i.get('file_path','')
        if '/specs/' in p and p.endswith(('plan.md','plan-done.md')): return 'c'
        if p.endswith('tasks.md'): return 'a' if name!='Read' else 'b'
        if 'plan-review.json' in p or '/tmp/l7r-check/plan' in p or 'plan-template' in p: return 'd'
        if 'l7r-handoffs' in p: return 'r'
        return 'b'
    if name=='Agent':
        t=i.get('subagent_type','')
        if t in('spec-fidelity','spec-fidelity-verify','round-arbiter'): return 'd'
        if t in('impl-drift','claims-triage'): return 'e'
        return 'x'
    if name in('Grep','Glob','ToolSearch'): return 'b'
    return None  # Monitor/TaskStop/SendMessage: a wait - booked by what is in flight
def walk(path):
    """-> (min by step, weighted tokens by step, raw tokens by step, elapsed, n tool calls by step, list of (t, step, name, brief))"""
    mins=collections.Counter(); tokw=collections.Counter(); tokr=collections.Counter(); calls=collections.Counter(); log=[]
    prev=None; seen=set(); use={}; last_bg='b'; pending=[]; inflight={}; runs=[]; waker=collections.Counter()  # pending: assistant gaps whose message has no tool (text) - booked to next tool's step
    first=last=None; last_step='b'
    for l in open(path):
        try: r=json.loads(l)
        except: continue
        if r.get('type') not in('assistant','user'): continue
        t=r.get('timestamp')
        if not t: continue
        T=ts(t); first=first or T; last=T
        gap=(T-prev) if prev is not None else 0.0; prev=T
        m=r.get('message') if isinstance(r.get('message'),dict) else {}
        if r['type']=='assistant':
            u=m.get('usage') or {}; mid=m.get('id')
            step=None
            for c in m.get('content',[]) if isinstance(m.get('content'),list) else []:
                if c.get('type')=='tool_use':
                    i=c.get('input') or {}
                    s=tool_step(c['name'],i)
                    if s is None: s=last_bg
                    use[c['id']]=s; step=step or s; calls[s]+=1
                    if (i.get('run_in_background') and c['name']=='Bash') or c['name']=='Agent': last_bg=s; inflight[c['id']]=(s,T,c['name'])
                    log.append((T,s,c['name'],(i.get('command') or i.get('file_path') or i.get('subagent_type') or '')[:110]))
            new=mid not in seen; seen.add(mid)
            if step is None:
                pending.append((gap,w(u) if new else 0,raw(u) if new else 0))
            else:
                for g,a,b in pending: mins[step]+=g; tokw[step]+=a; tokr[step]+=b
                pending=[]; mins[step]+=gap; last_step=step
                if new: tokw[step]+=w(u); tokr[step]+=raw(u)
        else:
            c=m.get('content')
            res=[x for x in c if isinstance(x,dict) and x.get('type')=='tool_result'] if isinstance(c,list) else []
            if res:
                s=use.get(res[0].get('tool_use_id'),last_step); mins[s]+=gap
            else:
                # a notification or a message from the coordinator: the builder was stopped
                txt=c if isinstance(c,str) else json.dumps(c)[:300]
                for g,a,b in pending: mins['r']+=g; tokw['r']+=a; tokr['r']+=b
                pending=[]
                if gap>0:
                    m2=re.search(r'<tool-use-id>(toolu_\w+)</tool-use-id>',txt); wk=None
                    if m2 and m2.group(1) in inflight: wk=m2.group(1)
                    elif '<task-id>' in txt:
                        ags=[k for k,v in inflight.items() if v[2]=='Agent']
                        wk=ags[0] if ags else None
                    crit='f' if any(v[0]=='f' for v in inflight.values()) else (inflight[wk][0] if wk else ('i' if not inflight else last_bg))
                    wstep=inflight[wk][0] if wk else '?'
                    mins['w:'+crit]+=gap; waker[(wstep,crit)]+=gap
                    if wk:
                        runs.append((inflight[wk][0],inflight[wk][2],inflight[wk][1],T)); del inflight[wk]
                    log.append((T,'w:'+crit+'<-'+wstep,'<resumed>',txt[:110].replace('\n',' ')))
    for g,a,b in pending: mins['r']+=g; tokw['r']+=a; tokr['r']+=b
    return mins,tokw,tokr,(last-first) if first else 0,calls,log,runs,waker
# ---- the event log: agents per task, landing runs, main-session rows
ag={}; land=collections.defaultdict(list); mainrows=collections.defaultdict(list); verd=collections.defaultdict(list); tid2task={}
for l in open(EV):
    if l[6:16]<'2026-11-25' and '"t":"2026-11-2' not in l[:40]: pass
    try: v=json.loads(l)
    except: continue
    t=v.get('t','')
    if t<'2026-11-25T17': continue
    T=v.get('task')
    if v.get('id') and T: tid2task[v['id']]=(T,v.get('fallback',False))
    if v['ev'] in('SubagentStart','SubagentStop'):
        a=ag.setdefault(v['aid'],{'agent':v['agent'],'task':T,'fb':v.get('fallback',False),'starts':[],'stops':[]})
        (a['starts'] if v['ev']=='SubagentStart' else a['stops']).append(ts(t))
        if v['ev']=='SubagentStop':
            a['tok']=v.get('tok'); a['verdict']=v.get('verdict')
    if v['ev']=='BgEnd' and v.get('make') in('land','done','closing-checks') and T:
        land[T].append((v['make'],v['t0'],t,(ts(t)-ts(v['t0']))/60,v.get('exit'),v.get('sid')))
    if v['ev']=='PostToolUse' and v.get('tool')=='Bash' and v.get('make') in('land','done','closing-checks') and T and not v.get('bg'):
        land[T].append((v['make']+' (fg)',t,t,v.get('ms',0)/60000,None,v.get('by','main')))
res={}
for T,aid in B.items():
    mins,tokw,tokr,el,calls,log,runs,waker=walk(SUB%aid)
    rev=[]
    for a2,a in ag.items():
        if a['task']==T and a['agent'] in('spec-fidelity','spec-fidelity-verify','round-arbiter','impl-drift','claims-triage') and a['starts'] and a['stops']:
            m2,tw2,tr2,el2=walk(SUB%a2)[:4] if os.path.exists(SUB%a2) else ({},{},{},0)
            rev.append({'aid':a2,'agent':a['agent'],'start':min(a['starts']),'min':(max(a['stops'])-min(a['starts']))/60,'verdict':a.get('verdict'),'tokw':sum(tw2.values()),'tokr':sum(tr2.values()),'fb':a['fb']})
    rev.sort(key=lambda x:x['start'])
    res[T]={'mins':{k:v/60 for k,v in mins.items()},'tokw':dict(tokw),'tokr':dict(tokr),'elapsed':el/60,'calls':dict(calls),'rev':rev,'land':land.get(T,[]),'log':log,'runs':runs,'waker':dict(waker)}
pickle.dump(res,open(OUT+'/m11-decomp.pkl','wb'))
def fold(d):
    o=collections.Counter()
    for k,v in d.items(): o[k[2:] if k.startswith('w:') else k]+=v
    return o
L=[]
def P(*a): L.append(' '.join(str(x) for x in a))
P('# m11: the builder\'s clock by step, per task (minutes; waits folded into the step waited on)\n')
keys=['a','b','c','d','e','f','g','r','i','x']
P('| task | builder elapsed | '+' | '.join(keys)+' | of it waits (b/d/e/f/g) | reviewers: n, machine min, verdicts |'); P('|---|---|'+'---|'*len(keys)+'---|---|')
for T in B:
    r=res[T]; f=fold(r['mins']); wt={k[2:]:v for k,v in r['mins'].items() if k.startswith('w:')}
    P('| %s%s | %.1f | '%(T,'' if T in SMALL else ' (wider)',r['elapsed'])+' | '.join('%.1f'%f.get(k,0) for k in keys)+' | '+' '.join('%s %.1f'%(k,v) for k,v in sorted(wt.items()))+' | %d, %.1f, %s |'%(len(r['rev']),sum(x['min'] for x in r['rev']),'/'.join(str(x['verdict']) for x in r['rev'])))
P('\n# weighted tokens (thousands) by step, builder; reviewers apart\n')
P('| task | builder total | '+' | '.join(keys)+' | reviewers | builder raw total (k) |'); P('|---|---|'+'---|'*len(keys)+'---|---|')
for T in B:
    r=res[T]; f=fold(r['tokw'])
    P('| %s | %.0f | '%(T,sum(f.values())/1e3)+' | '.join('%.0f'%(f.get(k,0)/1e3) for k in keys)+' | %.0f | %.0f |'%(sum(x['tokw'] for x in r['rev'])/1e3,sum(r['tokr'].values())/1e3))
P('\n# medians over the %d small tasks (%s)\n'%(len(SMALL),' '.join(SMALL)))
P('| step | median min | range | share of summed builder minutes | median weighted tok (k) | share of summed tokens |'); P('|---|---|---|---|---|---|')
totm=sum(sum(fold(res[T]['mins']).values()) for T in SMALL); tott=sum(sum(fold(res[T]['tokw']).values())+sum(x['tokw'] for x in res[T]['rev']) for T in SMALL)
names=dict(zip(keys,STEPS))
for k in keys:
    ms=[fold(res[T]['mins']).get(k,0) for T in SMALL]; tk=[fold(res[T]['tokw']).get(k,0)+(sum(x['tokw'] for x in res[T]['rev']) if k=='d' else 0) for T in SMALL]
    P('| %s | %.1f | %.1f-%.1f | %.0f%% | %.0f | %.0f%% |'%(names[k],st.median(ms),min(ms),max(ms),100*sum(ms)/totm,st.median(tk)/1e3,100*sum(tk)/tott))
el=[res[T]['elapsed'] for T in SMALL]; P('| builder elapsed | %.1f | %.1f-%.1f | | %.0f | |'%(st.median(el),min(el),max(el),st.median([sum(fold(res[T]['tokw']).values())+sum(x['tokw'] for x in res[T]['rev']) for T in SMALL])/1e3))
P('\n# background runs the builder waited on (step, kind, minutes) and waits by (what woke it, what the wait is booked to)\n')
for T in B:
    P(T,'; '.join('%s %s %.1f'%(a,b,(e-s0)/60) for a,b,s0,e in res[T]['runs']),'| waits:',', '.join('%s->%s %.1f'%(k[0],k[1],v/60) for k,v in res[T]['waker'].items()))
P('\n# landing, done and closing-check runs booked to each task in the event log (make, t0, minutes, exit, who)\n')
for T in B:
    for x in res[T]['land']: P(T,x[0],x[1][5:19],'%.1f min'%x[3],'exit',x[4],str(x[5])[:17])
# ---- the coordinating session's own turns naming the task
rows=pickle.load(open(OUT+'/m11-main.pkl','rb'))
def mstep(n,inp,st):
    if n=='Agent': return 'h brief+dispatch' if inp.startswith('Build feature') else 'h other dispatch'
    if n=='SendMessage': return 'h message to builder'
    if re.search(r'make task-add',inp): return 'a filing'
    if re.search(r'make land\b',inp): return 'g landing'
    if re.search(r'cherry-pick|git add -u|git commit|worktree (add|remove)',inp): return 'h commit, carry-over, worktree'
    return 'h other'
MT=collections.defaultdict(lambda:collections.defaultdict(lambda:[0.0,0.0,0])); prev=None; seen=set(); bgl={}; landruns=collections.defaultdict(list); filed={}; mlog=collections.defaultdict(list)
ALLT=re.compile(r'\bT(2[4-9]\d)\b|\bt(2[4-9]\d)\b')
msgs=[]; cur=None; pendwake=None
for r in rows:
    T0=ts(r['t']); gap=min((T0-prev) if prev else 0,300); prev=T0
    if r['type']=='assistant':
        if cur is None or cur['mid']!=r['mid']:
            cur={'mid':r['mid'],'gap':0.0,'u':None,'tools':[],'t':r['t'],'T0':T0,'wake':pendwake}; msgs.append(cur); pendwake=None
        cur['gap']+=gap; cur['u']=r['u'] or cur['u']; cur['tools']+=r['tools']
    elif r['res']:
        pass
    else:
        cur=None
        m3=re.search(r'<task-id>(\w+)</task-id>',r['text'])
        woke=[t for t,a in B.items() if m3 and a==m3.group(1)]
        if woke: pendwake=woke[0]
        m2=re.search(r'<tool-use-id>(toolu_\w+)</tool-use-id>',r['text'])
        if m2: bgl.setdefault('done',{})[m2.group(1)]=T0
done=bgl.pop('done',{})
for m in msgs:
    per=[]
    for id,n,inp,sty,bg in m['tools']:
        allnamed={'T'+(x or y) for x,y in ALLT.findall(inp)}
        named=[t for t in sorted(allnamed) if t in B]
        if not named or len(allnamed)>3: continue
        stp=mstep(n,inp,sty)
        for t in named: per.append((t,stp,len(allnamed),inp))
        if bg and re.search(r'make land\b',inp) and id in done:
            for t in named: landruns[t].append((done[id]-m['T0'])/60)
        if stp=='a filing':
            for t in named: filed.setdefault(t,m['T0'])
    if not per:
        if m['wake']:
            c=MT[m['wake']]['h woken by its builder']; c[0]+=m['gap']; c[2]+=1; c[1]+=w(m['u']) if m['u'] else 0
        continue
    share=1.0/len(per)
    for t,stp,k,inp in per:
        c=MT[t][stp]; c[0]+=m['gap']*share; c[2]+=1; c[1]+=(w(m['u']) if m['u'] else 0)*share
        mlog[t].append((m['t'][5:19],stp,inp[:100].replace('\n',' ')))
P('\n# the coordinating session\'s own turns whose tool call names the task (minutes of the model turn / weighted tokens k / calls) - a call naming more than three tasks is left out, one naming two or three is split; the tool\'s own run is not in the minutes\n')
hk=['a filing','h brief+dispatch','h woken by its builder','h commit, carry-over, worktree','g landing','h other']
P('| task | '+' | '.join(hk)+' | sum min | sum tok k | make land background run(s), min |'); P('|---|'+'---|'*len(hk)+'---|---|---|')
for T in B:
    P('| %s | '%T+' | '.join('%.1f / %.0f / %d'%(MT[T][k][0]/60,MT[T][k][1]/1e3,MT[T][k][2]) for k in hk)+' | %.1f | %.0f | %s |'%(sum(v[0] for v in MT[T].values())/60,sum(v[1] for v in MT[T].values())/1e3,' '.join('%.1f'%x for x in landruns.get(T,[]))))
P('| median of the small | '+' | '.join('%.1f / %.0f'%(st.median([MT[T][k][0]/60 for T in SMALL]),st.median([MT[T][k][1]/1e3 for T in SMALL])) for k in hk)+' | %.1f | %.0f | |'%(st.median([sum(v[0] for v in MT[T].values())/60 for T in SMALL]),st.median([sum(v[1] for v in MT[T].values())/1e3 for T in SMALL])))
pickle.dump({'MT':{t:{k:v for k,v in d.items()} for t,d in MT.items()},'landruns':dict(landruns),'filed':filed,'mlog':dict(mlog)},open(OUT+'/m11-mainsteps.pkl','wb'))
open(OUT+'/m11-decomp.txt','w').write('\n'.join(L)+'\n'); print('\n'.join(L))
