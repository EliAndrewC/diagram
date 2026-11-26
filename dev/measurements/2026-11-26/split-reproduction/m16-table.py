import json,os,statistics as st
from datetime import datetime
S=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(S+'/m16-marks.json'))
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def mins(a,b): return None if not a or not b else round((T(b)-T(a)).total_seconds()/60,1)
# task-row -> (class, basis, builder desc keys [primary, finishes...])
SAMPLE=[
('T207','C','lead','T207:'),('T209+T212','A','proved','T209 and T212'),('T210+T211+T213','A','proved','T210 T211 T213'),
('T214','B','symptom','T214'),('T215','A','proved','T215'),('T217','A','proved','T217'),('T223','A','proved','T223'),('T224','A','proved','T224'),
('T225','B','proved','T225'),('T226','B','proved','T226'),('T227','B','symptom','T227'),('T228','D','lead','build 451 T228'),
('T230+T239','C','lead','T230/T239'),('T231','C','lead','T231'),('T232','C','lead','T232 check|Finish 451 T232'),('T234','A','symptom','T234'),
('T235','B','symptom','T235'),('T238','A','symptom','T238'),('T240','B','lead','T240'),('T241','D','lead','T241'),('T242','C','lead','T242'),
('T247','C','lead','T247'),('T248','A','symptom','T248'),('T249','A','proved','T249'),('T252','C','lead','T252'),('T253','A','proved','T253'),
('T254+T255','A','symptom','T254+T255|Finish 451 T254'),('T256+T257','A','symptom','T256+T257'),('T261','D','lead','T261'),('T262','A','proved','T262'),
('T263','C','lead','T263'),('T267','A','proved','Build 451 T267'),('T268','A','proved','Build 451 T268'),('T269','A','symptom','Build 451 T269'),
('T270','B','proved','Build 451 T270'),('T271','B','symptom','Build 451 T271'),('T272','B','symptom','Build 451 T272'),('T281','B','symptom','T281'),
('T292','B','symptom','T292'),('T295','B','symptom','Build 451 T295|Finish 451 T295'),('T303','A','proved','T303'),('T305','B','symptom','T305'),
]
allw1=[mins(m['t0'],m['w1']) for m in rows if m['w1'] and ('Build' in m['desc'] or 'build' in m['desc'] or 'Fix' in m['desc']) and 'Finish' not in m['desc']]
alls1=[mins(m['t0'],m['s1']) for m in rows if m['s1'] and ('Build' in m['desc'] or 'build' in m['desc'] or 'Fix' in m['desc']) and 'Finish' not in m['desc']]
O=st.median(allw1); print('median min to first write (any), all primary builders n=%d: %.1f ; to first source edit: %.1f'%(len(allw1),O,st.median(alls1)))
out=[]
for name,c,basis,keys in SAMPLE:
    ks=keys.split('|'); ms=[next(m for m in rows if k in m['desc']) for k in ks]
    m=ms[0]; t0=m['t0']
    P=mins(t0,m['s1']); t1=mins(t0,m['t1']); ep=mins(t0,m['e_pre']); tot=sum(mins(x['t0'],x['end']) for x in ms)
    if P is None: P=t1; 
    if ep is None or (P is not None and ep<P): ep=mins(t0,m['plan1']) or P
    Rlow=round(P-t1,1) if (t1 is not None and P is not None and t1<P) else 0.0
    Rhigh=round(max(0,P-O),1) if P is not None else None
    F=round(ep-P,1) if P is not None else None
    rest=round(tot-ep,1)
    el=mins(t0,m['e_last']); fix_hi=round(el-P,1) if (el is not None and P is not None and el>=P) else F
    out.append(dict(task=name,cls=c,basis=basis,total=tot,prefix=P,red_slice=Rlow,repro_hi=Rhigh,fix=F,fix_hi=fix_hi,rest=rest,interleaved=m['test_after_src'],date=t0[5:16]))
json.dump(dict(O=O,rows=out),open(S+'/m16-table.json','w'),indent=0)
print('%-15s %-2s %-8s %6s %6s %6s %6s %6s %6s %s'%('task','cl','basis','total','prefix','redSl','reproH','fix','rest','t>s'))
for r in out: print('%-15s %-2s %-8s %6s %6s %6s %6s %6s %6s %s'%(r['task'],r['cls'],r['basis'],r['total'],r['prefix'],r['red_slice'],r['repro_hi'],r['fix'],r['rest'],r['interleaved']))
med=lambda k,f=lambda r:True: round(st.median([r[k] for r in out if r[k] is not None and f(r)]),1)
for k in('total','prefix','red_slice','repro_hi','fix','fix_hi','rest'): print(k,'median all',med(k),'| A',med(k,lambda r:r['cls']=='A'),'| proved',med(k,lambda r:r['basis']=='proved'))
print('sum total',round(sum(r['total'] for r in out)),'rest share',round(sum(r['rest'] for r in out)/sum(r['total'] for r in out),2))
import collections
print(collections.Counter((r['basis'],r['cls']) for r in out))
