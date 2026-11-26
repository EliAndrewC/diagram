import json,glob,os,re,datetime,pickle
P='/home/agent/.claude/projects/-diagram/'
SELF='a9ce771024d8ecb84'
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def prompt(u):
    i=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
    return i
out={}
for mf in glob.glob(P+'*/subagents/*.meta.json'):
    if json.load(open(mf)).get('agentType')!='general-purpose': continue
    f=mf.replace('.meta.json','.jsonl'); aid=os.path.basename(f)[6:-6]
    if aid==SELF: continue
    rows=[]
    for l in open(f):
        try: rows.append(json.loads(l))
        except: pass
    turns=[];prev_ts=None;prev_id=None;cur=None
    events=[];first_prompt='';refused=False;handoff_w=[]
    for r in rows:
        t=r.get('timestamp'); 
        if not t: continue
        T=ts(t)
        m=r.get('message') if isinstance(r.get('message'),dict) else {}
        if r.get('type')=='assistant' and 'usage' in m:
            mid=m.get('id'); u=m['usage']
            its=[i for i in (u.get('iterations') or []) if i.get('type')=='message']
            ctx=prompt(its[-1]) if its and prompt(its[-1])>0 else prompt(u)
            if cur and cur['id']==mid:
                cur['end']=T; cur['out']=u.get('output_tokens',0); cur['u']=u; cur['ctx']=ctx
            else:
                cur={'id':mid,'start':prev_ts,'end':T,'ctx':ctx,'out':u.get('output_tokens',0),'u':u}
                turns.append(cur)
            for c in m.get('content',[]):
                if c.get('type')=='tool_use':
                    fp=(c.get('input') or {}).get('file_path','')
                    events.append((T,c['name'],fp))
            prev_ts=T if False else prev_ts
            last_assist=T
            continue
        # non-assistant line
        prev_ts=T; cur=None
        if r.get('type')=='user':
            c=m.get('content')
            if not first_prompt:
                first_prompt=c if isinstance(c,str) else json.dumps(c)
            s=json.dumps(c)
            if "BLOCKED: this builder" in s: refused=True
    out[aid]=dict(file=f,turns=turns,events=events,prompt=first_prompt,refused=refused,
        start=ts(rows[0]['timestamp']),end=ts(rows[-1]['timestamp']),
        mentions=re.findall(r'l7r-handoffs/[\w.\-]+\.md',first_prompt))
pickle.dump(out,open('parsed.pkl','wb'))
print(len(out),sum(len(v['turns']) for v in out.values()),sum(v['refused'] for v in out.values()))
