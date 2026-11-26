import json,re,os
S=os.path.dirname(os.path.abspath(__file__))
idx=json.load(open(S+'/m16-index.json')); tab=json.load(open(S+'/m16-table.json'))
tasks=open(S+'/m16-tasks-done.md').read()+open(S+'/m16-tasks.md').read()
HEDGE=re.compile(r"probabl|likel(y|iest)|inferred|\bthe lead\b|find why|find the race|find its shared|measure why|measure first|measured first|cause not (proven|isolated)|not proven|not isolated|perhaps|hypothes|if it does not reproduce|\(keyed by[^)]*\?|why the three tools disagreed|premise",re.I)
CITE=re.compile(r"ask:[\w-]+|arbiter|cascade-test|cascade test|T\d+'s (builder|handoff|plan section|report)|handoff|probed|measured 20|\(measured|replay|found by 451 T\d+|451 T\d+'s|restatement-audit|parallel trials",re.I)
KEY={'T207':'T207:','T209+T212':'T209 and T212','T210+T211+T213':'T210 T211 T213','T230+T239':'T230/T239','T232':'T232 check','T254+T255':'T254+T255','T256+T257':'T256+T257','T295':'Build 451 T295','T228':'build 451 T228'}
out={}
for r in tab['rows']:
    t=r['task']; k=KEY.get(t,t)
    d=next(x for x in idx['dispatch'] if x.get('desc') and x.get('ts') and x['ts']>='2026-11-23T23' and k in x['desc'] and 'Finish' not in x['desc'] and 'Plan review' not in x['desc'] and 'plan review' not in x['desc'])
    p=d['prompt']; i=p.find('STOP POINT'); p=p[:i] if i>0 else p
    lines=' '.join(m.group(0) for n in t.split('+') for m in re.finditer(r'^- \[.\] \*?\*?%s\b.*$'%n,tasks,re.M))
    text=p+' '+lines
    h=sorted(set(m.group(0).lower()[:28] for m in HEDGE.finditer(text))); c=sorted(set(m.group(0).lower()[:24] for m in CITE.finditer(text)))
    basis='hedged' if h else ('cited' if c else 'asserted')
    out[t]=dict(basis=basis,h=h,c=c[:4],cls=r['cls'],old=r['basis'])
    print('%-15s %s %-8s (was %-7s) H=%s C=%s'%(t,r['cls'],basis,r['basis'],h[:4],c[:4]))
json.dump(out,open(S+'/m16-basis.json','w'))
import collections
print(sorted(collections.Counter((v['basis'],v['cls']) for v in out.values()).items()))
