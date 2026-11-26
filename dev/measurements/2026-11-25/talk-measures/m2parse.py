import json,datetime,pickle
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
f='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
T=[];cur=None;prev=None
for l in open(f):
    try: r=json.loads(l)
    except: continue
    t=r.get('timestamp')
    if not t: continue
    T_=ts(t); m=r.get('message') if isinstance(r.get('message'),dict) else {}
    if r.get('type')=='assistant' and 'usage' in m:
        u=m['usage']; mid=m.get('id')
        its=[i for i in (u.get('iterations') or []) if i.get('type')=='message']
        uu=its[-1] if its and sum(its[-1].get(k,0) for k in('input_tokens','cache_read_input_tokens','cache_creation_input_tokens'))>0 else u
        ctx=sum(uu.get(k,0) for k in('input_tokens','cache_read_input_tokens','cache_creation_input_tokens'))
        tools=[]
        for c in m.get('content',[]):
            if c.get('type')=='tool_use':
                i=c.get('input') or {}
                tools.append((c['name'],i.get('file_path',''),(i.get('command') or '')[:300],(i.get('subagent_type') or i.get('description') or '') if c['name']=='Agent' else ''))
        if cur and cur['id']==mid:
            cur['end']=T_;cur['out']=u.get('output_tokens',0);cur['tools']+=tools;cur['ctx']=ctx
        else:
            cur={'id':mid,'start':prev if prev else T_,'end':T_,'ctx':ctx,'out':u.get('output_tokens',0),'tools':tools,'u':u};T.append(cur)
        continue
    prev=T_;cur=None
pickle.dump(T,open('m2turns.pkl','wb'))
print(len(T),datetime.datetime.fromtimestamp(T[0]['end']),datetime.datetime.fromtimestamp(T[-1]['end']))
