import json,sys,re,os
P='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
out={'dispatch':[], 'notif':[]}
with open(P) as f:
    for line in f:
        if '"Agent"' not in line and 'task-notification' not in line: continue
        try: d=json.loads(line)
        except: continue
        ts=d.get('timestamp'); m=d.get('message') or {}
        c=m.get('content')
        if isinstance(c,list):
            for b in c:
                if b.get('type')=='tool_use' and b.get('name')=='Agent':
                    i=b['input']
                    out['dispatch'].append(dict(ts=ts,id=b['id'],desc=i.get('description'),st=i.get('subagent_type'),prompt=i.get('prompt')))
                if b.get('type')=='tool_result':
                    t=b.get('content'); t=json.dumps(t) if not isinstance(t,str) else t
                    if 'agentId' in t[:3000] or 'agent_id' in t[:3000]:
                        out['dispatch'].append(dict(ts=ts,result_for=b.get('tool_use_id'),text=t[:600]))
                if b.get('type')=='text' and 'task-notification' in b.get('text',''):
                    out['notif'].append(dict(ts=ts,text=b['text']))
        elif isinstance(c,str) and 'task-notification' in c:
            out['notif'].append(dict(ts=ts,text=c))
json.dump(out,open(sys.argv[1],'w'))
print(len(out['dispatch']),len(out['notif']))
