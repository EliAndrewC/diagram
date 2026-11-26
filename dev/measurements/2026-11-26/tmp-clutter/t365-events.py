import json,collections,sys
c=collections.Counter(); mk=collections.Counter(); first=None;last=None
keys=collections.Counter(); steps=collections.Counter(); sids=set()
for l in open('t365-events-day.jsonl'):
    try: v=json.loads(l)
    except Exception: c['bad']+=1; continue
    ev=v.get('ev'); c[(ev,v.get('tool') if ev in('PreToolUse','PostToolUse') else v.get('src') or '')]+=1
    t=v['t']; first=min(first or t,t); last=max(last or t,t); sids.add(v.get('sid'))
    if ev not in ('PreToolUse','PostToolUse','Phase'): keys[(ev,tuple(sorted(v.keys())))]+=1
    if ev=='Phase': steps[(v.get('make'),v.get('step'))]+=1
    if 'make' in v and ev!='Phase': mk[(ev,v['make'])]+=1
print(first,last,'sids',len(sids))
for k,n in sorted(c.items(),key=lambda x:-x[1])[:40]: print(n,k)
print('--- other ev shapes')
for k,n in keys.most_common(15): print(n,k)
print('--- make on non-Phase'); print(mk.most_common(40))
print('--- Phase make/step'); 
for k,n in steps.most_common(40): print(n,k)
