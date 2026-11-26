import json,glob,os,re,datetime,pickle,statistics as st
P='/home/agent/.claude/projects/-diagram/'
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
T0=datetime.datetime(2026,11,24,tzinfo=datetime.timezone.utc).timestamp()
def pr(u): return u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
J={'measure':r'\b(measure|measurement|sweep|baseline|re-measure|probe|time the|profile)\b',
 'build':r'\b(build|implement|port|write the code|add a (test|guard|check|rule)|code half|rewrite)\b',
 'fix':r'\b(fix|defect|bug|repair|wrong outcome)\b',
 'content':r'\b(entries|registry|research record|write the (entry|entries|section|page|brief|docs?)|rewrite the (doc|page)|prose|modal)\b',
 'claims':r'claims round|claims-owed|impl-drift|claims-triage|claims-bundle',
 'plan':r'plan section|make decide|plan review|spec-fidelity|plan-delta|plan\.md'}
rows=[]
for mf in glob.glob(P+'*/subagents/*.meta.json'):
    if json.load(open(mf)).get('agentType')!='general-purpose': continue
    f=mf.replace('.meta.json','.jsonl'); aid=os.path.basename(f)[6:-6]
    R=[]
    for l in open(f):
        try: R.append(json.loads(l))
        except: pass
    if not R or 'timestamp' not in R[0] or ts(R[0]['timestamp'])<T0: continue
    prompt='';calls=[];outs={};ctxmax=0;refused=False;handoff=False;edits=set()
    for r in R:
        m=r.get('message') if isinstance(r.get('message'),dict) else {}
        if r.get('type')=='user':
            c=m.get('content')
            if not prompt: prompt=c if isinstance(c,str) else json.dumps(c)
            if 'BLOCKED: this builder' in json.dumps(c): refused=True
        if r.get('type')=='assistant' and 'usage' in m:
            u=m['usage'];outs[m.get('id')]=u.get('output_tokens',0)
            its=[i for i in (u.get('iterations') or []) if i.get('type')=='message']
            ctxmax=max(ctxmax,pr(its[-1]) if its and pr(its[-1])>0 else pr(u))
            for c in m.get('content',[]):
                if c.get('type')=='tool_use':
                    i=c.get('input') or {}; fp=i.get('file_path','')
                    calls.append((c['name'],fp,i.get('command','')))
                    if c['name'] in('Edit','Write','NotebookEdit'):
                        if 'l7r-handoffs' in fp: handoff=True
                        elif '/.clones/' in fp or fp.startswith('/diagram/'): edits.add(fp)
    if not re.search(r'300k|l7r-handoffs',prompt): continue   # builder = told to write a handoff at the cap
    lp=prompt.lower()
    pos={k:(re.search(v,lp).start() if re.search(v,lp) else None) for k,v in J.items()}
    jobs=[k for k,v in pos.items() if v is not None]
    first=min(jobs,key=lambda k:pos[k]) if jobs else None
    # behavioral: any of first 6 calls before first edit is a measuring command
    beh=False
    for n,fp,cmd in calls[:6]:
        if n in('Edit','Write'): break
        if re.search(r'measure|sweep|baseline|run\.sh|work-budget|cohort|probe|make (hamlet|map|compound|seeds)|bench',cmd): beh=True
    numbered=len(re.findall(r'(?m)^\s*(?:\d+[.)]|\([a-z]\)|[-*]) ',prompt))
    rows.append(dict(id=aid,start=ts(R[0]['timestamp']),plen=len(prompt),jobs=jobs,nj=len(jobs),first=first,beh=beh,numbered=numbered,
      hit=refused or handoff or ctxmax>=290000,refused=refused,handoff=handoff,ctxmax=ctxmax,edited=len(edits),calls=len(calls),out=sum(outs.values()),
      head=prompt[:90].replace('\n',' ')))
pickle.dump(rows,open('m1.pkl','wb'))
print(len(rows),sum(r['hit'] for r in rows))
def tab(name,key):
    G={}
    for r in rows: G.setdefault(key(r),[]).append(r)
    print(f'-- by {name}: group n hit rate | med prompt chars, med calls, med out')
    for k in sorted(G,key=str):
        g=G[k];print(f'{str(k):10s} n={len(g):3d} hit={sum(x["hit"] for x in g):3d} rate={sum(x["hit"] for x in g)/len(g):.2f} | {st.median(x["plen"] for x in g):.0f} {st.median(x["calls"] for x in g):.0f} {st.median(x["out"] for x in g):.0f}')
tab('jobs(types)',lambda r:min(r['nj'],5))
tab('jobs>=4 vs <4',lambda r:'4+' if r['nj']>=4 else '<4')
tab('began brief-measure',lambda r:r['first']=='measure')
tab('began behavior-measure',lambda r:r['beh'])
tab('files edited',lambda r:'1-3' if r['edited']<=3 else '4-8' if r['edited']<=8 else '9+')
tab('prompt length',lambda r:'<3k' if r['plen']<3000 else '3-4.5k' if r['plen']<4500 else '4.5k+')
tab('numbered items',lambda r:'<=6' if r['numbered']<=6 else '7-12' if r['numbered']<=12 else '13+')
tab('edited 0',lambda r:r['edited']==0)
