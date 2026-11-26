import json,re
d=json.load(open('m14r-extract.json'))
rows=d['rows']; reps=d['reports']
out=[]
for n,r in enumerate(reps):
    tasks=re.findall(r'T(\d+)',r['name'])
    pat=re.compile(r'T(?:%s)\b'%'|'.join(tasks))
    out.append(f"\n######## R{n+1} line {r['line']} {r['name']}")
    first_turn=True; landed=False; cnt=0
    for (i,ts,k,s) in rows:
        if i<=r['line']: continue
        if k=='REPORT':
            if first_turn: first_turn=False
            continue
        if k=='user':
            first_turn=False
            if pat.search(s): out.append(f"  [{i} USER] {s[:500]}")
            continue
        hit=pat.search(s)
        if not(first_turn or hit): continue
        key=re.search(r'make land|git (-C \S+ )?add|git (-C \S+ )?commit|cherry-pick|make carry|task-add',s) is not None
        isagent=k=='tool' and s.startswith('Agent ')
        lim=6000 if (key or (isagent and hit)) else (900 if k=='text' else 500)
        out.append(f"  [{i} {k}] {s[:lim]}")
        cnt+=1
        if k=='tool' and hit and re.search(r'make land(-batch)? |make land-batch',s) and 'land-tooling' not in s: landed=True
        if isagent and hit and re.match(r'Agent \{"description": "(Finish|Fix)',s): out.append('  == successor dispatched'); break
        if landed and cnt>0:
            # include following 6 rows mentioning task then stop
            extra=[x for x in rows if x[0]>i and x[2] in('text',) and pat.search(x[3])][:2]
            for x in extra: out.append(f"  [{x[0]} post-land text] {x[3][:1200]}")
            break
        if i>r['line']+2500: out.append('  == window cap'); break
open('m14r-windows.txt','w').write('\n'.join(out)); print(len('\n'.join(out)))
for n in range(33):
    pass
