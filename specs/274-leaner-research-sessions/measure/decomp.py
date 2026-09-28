import json,pathlib,collections,bisect,sys
sys.path.insert(0,'.')
H=pathlib.Path.home()
S=json.loads(open('sessions.json').read())
inc={'271:diagram-research-2:k5','271:diagram-research-5:t5','271:diagram-research-4:k7','271:diagram-research-1:u3','271:diagram-research-3:k3','269:diagram-supplemental:a2'}
def recs(p):
    for l in open(p,errors='replace'):
        try: yield json.loads(l)
        except ValueError: pass
res=collections.defaultdict(lambda:collections.Counter())
for s in S:
    if s['group'] in inc: continue
    kind=s['kind'] if s['kind'] in ('write','check') else 'other'
    p=H/f".claude/projects/-diagram--clones-{s['clone']}/{s['sid']}.jsonl"
    rs=[r for r in recs(p) if not r.get('isSidechain')]
    # message rows
    per={}
    for r in rs:
        if r.get('type')=='assistant':
            m=r['message']; u=m.get('usage') or {}
            if not m.get('id'): continue
            row=per.setdefault(m['id'],{'ts':r.get('timestamp'),'ctx':0,'out':0})
            row['ctx']=max(row['ctx'],(u.get('input_tokens') or 0)+(u.get('cache_creation_input_tokens') or 0)+(u.get('cache_read_input_tokens') or 0))
            row['out']=max(row['out'],u.get('output_tokens') or 0)
    rows=sorted(per.values(),key=lambda x:x['ts']); tss=[x['ts'] for x in rows]; n=len(rows)
    C=res[kind]
    C['sessions']+=1; C['cost']+=sum(x['ctx'] for x in rows)
    C['floor']+=rows[0]['ctx']*n
    for i,x in enumerate(rows): C['output_carry']+=x['out']*(n-1-i)
    for r in rs:
        t=r.get('timestamp') or ''
        later=n-bisect.bisect_right(tss,t)
        if r.get('type')=='attachment':
            a=r.get('attachment') or {}
            if a.get('type') in ('prompt_snapshot','queued_command'): continue
            C['att:'+str(a.get('type'))]+=len(json.dumps(a))//4*later
        c=(r.get('message') or {}).get('content')
        if r.get('type')=='user':
            for b in c if isinstance(c,list) else []:
                if b.get('type')=='tool_result':
                    body=b.get('content'); text=body if isinstance(body,str) else ''.join(str(q.get('text','')) for q in body or [] if isinstance(q,dict))
                    C['tool_results']+=len(text)//4*later
                elif b.get('type')=='text':
                    C['user_text']+=len(b.get('text',''))//4*later
            if isinstance(c,str): C['user_text']+=len(c)//4*later
for k,C in res.items():
    cost=C['cost']; print(f"== {k} sessions {C['sessions']} input cost {cost/1e6:.0f}M")
    for kk,v in C.most_common():
        if kk in('cost','sessions'): continue
        if v/cost>0.005: print(f"  {kk:<34}{v/1e6:8.1f}M {v/cost:6.1%}")
