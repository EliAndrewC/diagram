import json,glob,os,re,sys
D='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents/'
out=[]
for m in glob.glob(D+'*.meta.json'):
    meta=json.load(open(m))
    if 'spec-fidelity' not in (meta.get('agentType') or ''): continue
    p=m.replace('.meta.json','.jsonl')
    first=None;last=None;prompt=None;reply=None;cmds=[]
    try:
        for line in open(p):
            try:d=json.loads(line)
            except: continue
            ts=d.get('timestamp'); 
            if ts and not first:first=ts
            if ts:last=ts
            msg=d.get('message') or {}; c=msg.get('content')
            if prompt is None and msg.get('role')=='user':
                prompt=c if isinstance(c,str) else ' '.join(b.get('text','') for b in c if b.get('type')=='text')
            if msg.get('role')=='assistant' and isinstance(c,list):
                for b in c:
                    if b.get('type')=='text' and b['text'].strip(): reply=b['text']
                    if b.get('type')=='tool_use' and b.get('name')=='Bash': cmds.append(b['input'].get('command','')[:300])
    except FileNotFoundError: continue
    out.append(dict(id=os.path.basename(p),type=meta.get('agentType'),desc=meta.get('description'),first=first,last=last,prompt=prompt,reply=reply,cmds=[c for c in cmds if 'plan-verdict' in c or 'verdict' in c]))
out.sort(key=lambda r:r['first'] or '')
json.dump(out,open(sys.argv[1],'w'))
print(len(out))
import collections
print(collections.Counter((r['type'],(r['first'] or '')[:10]) for r in out))
