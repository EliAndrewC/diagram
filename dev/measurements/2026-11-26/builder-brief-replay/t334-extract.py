import json,sys,re
src='/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl'
out=[]
for line in open(src):
    try: r=json.loads(line)
    except Exception: continue
    m=r.get('message') or {}
    c=m.get('content')
    if not isinstance(c,list): continue
    for b in c:
        if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('name') in('Agent','Task'):
            i=b.get('input') or {}
            out.append({'ts':r.get('timestamp'),'type':i.get('subagent_type',''),'model':i.get('model',''),'desc':i.get('description',''),'prompt':i.get('prompt','')})
json.dump(out,open('t334-dispatches.json','w'))
print(len(out))
pool=re.compile(r'/diagram/\.clones/[A-Za-z0-9_.-]+')
n=0
for d in out:
    if not (d['ts'] or '').startswith('2026-11-2'): continue
    trees=sorted(set(pool.findall(d['prompt'])))
    if d['type'] in('','general-purpose') and any(re.search(r'-(t\d+|b\d+)$',t) for t in trees):
        n+=1
        print(d['ts'],d['type'] or '-',len(d['prompt']),d['desc'][:60],'|',[t.split('/')[-1] for t in trees], '| STOP' if 'STOP POINT' in d['prompt'] else '')
print(n)
