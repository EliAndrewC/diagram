import json,re,os,sys
S=os.path.dirname(os.path.abspath(__file__))
idx=json.load(open(S+'/m16-index.json'))
res={}
for n in idx['notif']:
    for blk in re.findall(r'<task-notification>.*?</task-notification>',n['text'],re.S):
        m=re.search(r'<summary>Agent "(.*?)" (finished|completed|.*?)</summary>',blk,re.S); r=re.search(r'<result>(.*?)</result>',blk,re.S)
        if m and r: res.setdefault(m.group(1),[]).append((n['ts'],r.group(1)))
json.dump(res,open(S+'/m16-results.json','w'))
disp=[x for x in idx['dispatch'] if x.get('desc') and x.get('ts') and x['ts']>='2026-11-24']
pat=sys.argv[1]; bl=int(sys.argv[2]); rl=int(sys.argv[3])
for d in disp:
    if not re.search(pat,d['desc']): continue
    p=d['prompt']; i=p.find('SESSION_MODEL'); body=p[i:] if i>=0 else p
    j=body.find('The fault'); j=body.find('The defect') if j<0 else j; j=body.find('Read the T') if j<0 else j; body=body[j:] if j>0 else body
    print('#####',d['ts'][5:16],d['desc']); print('BRIEF:',body[:bl].replace('\n',' '))
    for ts,r in sorted(res.get(d['desc'],[]),key=lambda x:-len(x[1]))[:1]:
        print('RESULT',(ts or '')[5:16],':',r[:rl].replace('\n',' '))
    print()
