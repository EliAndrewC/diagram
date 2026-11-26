import json,os,statistics as st
S=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(S+'/m16-table.json')); O=d['O']; R=d['rows']
def net(rows,M,key,capF):
    save=0; 
    for r in rows:
        rs=r[key] or 0
        if capF: rs=min(rs,max(r['fix'] or 0,0))
        g=max(0,rs-M)
        if r['cls']=='A': save+=g
        elif r['cls']=='B': save+=0.5*g
    return round(save,1)
def waste(rows):
    # builder-minutes of the second (fix) builder that are thrown away: its reading O plus a fix phase (the median fix of the sample), whole for C/D, half for B
    Fm=st.median([r['fix'] for r in rows if r['fix'] and r['fix']>0] or [0])
    w=sum((O+Fm)*(1 if r['cls'] in 'CD' else 0.5 if r['cls']=='B' else 0) for r in rows)
    extra=sum(O+Fm for r in rows)
    return round(w),round(extra),Fm
for lab,rows in (('ALL 42',R),('PROVED-EARLIER 15',[r for r in R if r['basis']=='proved']),('LEAD-ONLY 12',[r for r in R if r['basis']=='lead']),('SYMPTOM 15',[r for r in R if r['basis']=='symptom'])):
    tot=sum(r['total'] for r in rows)
    lo=net(rows,3,'red_slice',False); mid=net(rows,1,'red_slice',False); hi=net(rows,1,'repro_hi',False)
    w,extra,Fm=waste(rows)
    print('%s: builder-min %d | wall saved low %.1f (red slice, merge 3) mid %.1f (red slice, merge 1) high %.1f (all pre-fix past %.1f min reading, merge 1) = %.1f%%..%.1f%% | second builders cost %d builder-min, of which wasted %d'%(lab,tot,lo,mid,hi,O,100*lo/tot,100*hi/tot,extra,w))
import collections
print(collections.Counter(r['cls'] for r in R))
print('rows where red_slice>=3:',[(r['task'],r['cls'],r['red_slice']) for r in R if r['red_slice']>=3])
print('rows where repro_hi>=4:',[(r['task'],r['cls'],r['repro_hi']) for r in R if (r['repro_hi'] or 0)>=4])
