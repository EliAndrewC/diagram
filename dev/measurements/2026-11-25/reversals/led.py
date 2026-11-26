import re,json,collections
rows=[]
for ln,l in enumerate(open('/diagram/.clones/diagram-backlog/dev/review-ledger.md'),1):
    if not re.match(r'\| 2026-11-(19|2\d) \| spec-fidelity \|',l): continue
    if 'PLAN REVIEW' not in l and 'MODE 4' not in l: continue
    c=[x.strip() for x in l.split('|')]
    feat=re.search(r'feature (\d{3})',c[3]); feat=feat.group(1) if feat else None
    tk=re.search(r'task (T\d+(?:[, /]+T?\d+)*)',c[3])
    task=tk.group(1) if tk else None
    if not task:
        m=re.search(r'\b(T\d{2,3})\b',c[5]); task=m.group(1)+'?' if m else None
    v=c[4]
    rows.append(dict(ln=ln,date=c[1],feat=feat,task=task,verdict=v,txt=c[5][:600],c3=c[3]))
print(len(rows),collections.Counter((r['feat'],r['verdict'][:8]) for r in rows))
print(sum(r['task'] is None for r in rows), sum((r['task'] or '').endswith('?') for r in rows))
json.dump(rows,open('ledger_plan.json','w'),indent=0)
