# t297: every SendMessage the coordinating session made to a subagent, matched to its arrival in the subagent's transcript
# usage: python3 -I t297-delivery.py <session.jsonl> <subagents dir> <since ISO> > out.tsv
import json,sys,os,datetime as dt
sess,sub,since=sys.argv[1],sys.argv[2],sys.argv[3]
P=lambda s: dt.datetime.fromisoformat(s.replace('Z','+00:00'))
calls={};res={}
with open(sess) as f:
    for line in f:
        if 'SendMessage' not in line and 'tool_result' not in line: continue
        d=json.loads(line); c=(d.get('message') or {}).get('content')
        if not isinstance(c,list) or not d.get('timestamp'): continue
        for b in c:
            if not isinstance(b,dict): continue
            if b.get('type')=='tool_use' and b.get('name')=='SendMessage': calls[b['id']]=(d['timestamp'],b['input'])
            elif b.get('type')=='tool_result' and b.get('tool_use_id') in calls and b['tool_use_id'] not in res:
                rc=b.get('content'); rc=' '.join(x.get('text','') for x in rc if isinstance(x,dict)) if isinstance(rc,list) else rc
                res[b['tool_use_id']]=rc or ''
def safe(l):
    try: return json.loads(l)
    except ValueError: return None
norm=lambda s:' '.join(s.split())
def doing(L,t):
    # the builder's last assistant block before t
    last=None
    for d in L:
        if d['timestamp']>t: break
        if d.get('type')=='assistant':
            for b in d['message']['content']:
                if b.get('type') in('tool_use','server_tool_use'): last=(d['timestamp'],b.get('name'))
                elif b.get('type')=='text' and b['text'].strip(): last=(d['timestamp'],'text')
    return last
print('\t'.join(['send','to','kind','result_words','arrive','delay_s','form','at_send','desc','summary']))
for i,(t,inp) in sorted(calls.items(),key=lambda x:x[1][0]):
    if t<since: continue
    r=res.get(i,'')
    kind='queued' if 'queued for delivery' in r else 'resumed' if 'Resuming agent' in r else 'other'
    words=('moved-to-bg' if 'Moved ' in r and 'running tool call' in r else 'moved-nothing' if 'moved nothing' in r else '') if kind=='queued' else ''
    a=inp.get('to',''); f=os.path.join(sub,'agent-'+a+'.jsonl'); meta=os.path.join(sub,'agent-'+a+'.meta.json')
    desc=json.load(open(meta)).get('description','') if os.path.exists(meta) else ''
    arrive=form='';delay='';at=''
    if kind in('queued','resumed') and os.path.exists(f):
        L=[d for d in (safe(l) for l in open(f)) if d and d.get('timestamp')]
        key=norm(inp.get('message',''))
        for d in L:
            if d['timestamp']<t[:19]: continue
            if d.get('type')=='attachment' and norm(str((d.get('attachment') or {}).get('prompt',''))).__contains__(key[:80]):
                arrive=d['timestamp'];form='attachment:'+d['attachment'].get('type','');break
            c=(d.get('message') or {}).get('content') if d.get('type')=='user' else None
            if isinstance(c,str) and norm(c).__contains__(key[:80]): arrive=d['timestamp'];form='user-turn';break
        if arrive: delay='%.1f'%(P(arrive)-P(t)).total_seconds()
        dg=doing(L,t); at='%s %s'%dg if dg else ''
    print('\t'.join([t,a,kind,words,arrive or 'NOT FOUND',delay,form,at,desc,inp.get('summary','')]))
