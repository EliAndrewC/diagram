import json,re,os,statistics as st
from datetime import datetime
S=os.path.dirname(os.path.abspath(__file__))
o=json.load(open(S+'/m16-builders.json'))
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def mins(a,b): return round((T(b)-T(a)).total_seconds()/60,2)
WAIT=re.compile(r'^\s*(\[bg\] )?(cd \S+ (&&|;) )?(sleep|until|while|wait|timeout \d+)')
recs=[]
for v in o.values():
    if not re.search(r'451 T\d|T25[01]',v['desc']) or re.search(r'Plan review|Arbiter|impl-drift',v['desc']): continue
    ev=[e for e in v['events'] if e.get('ts')]
    end=ev[-1]['ts']
    for i,e in enumerate(ev):
        if e['k']=='Agent' and 'spec-fidelity' in e['s']:
            d=e['ts']; name=e['s'].split('| ',1)[1]
            fg=e.get('end') and mins(d,e['end'])>0.5 and 'Async' not in (e.get('r') or '')
            if fg: vt=e['end']
            else:
                c=[x for x in ev if x['k']=='notif' and x['ts']>d and x['s'].startswith('Agent')]
                exact=[x for x in c if name[:30] in x['s']]
                vt=(exact or c or [None])[0]; vt=vt['ts'] if vt else None
            if not vt: recs.append(dict(b=v['desc'],d=d,verdict=None)); continue
            inside=[x for x in ev if d<x['ts']<vt and x['k'] not in('say','notif','Agent')]
            waits=[x for x in inside if x['k'] in('Monitor','TaskOutput') or (x['k']=='Bash' and WAIT.search(x['s']))]
            work=[x for x in inside if x not in waits]
            # idle = time in [d,vt] not covered by a work tool call or the 20 s after one (thinking allowance)
            cover=0.0; cur=T(d)
            segs=sorted((T(x['ts']),T(x.get('end') or x['ts'])) for x in work)
            busy=0.0; last=T(d)
            for a,b in segs:
                a=max(a,last); b=min(max(b,a),T(vt))
                if b>a: busy+=(b-a).total_seconds(); last=b
            lastwork=max([x.get('end') or x['ts'] for x in work] or [d]); lastwork=min(lastwork,vt)
            ccpend=any(x['k']=='notif' and x['ts']>vt and re.search(r'losing|check',x['s'],re.I) for x in ev)
            ccbg=[x for x in ev if x['k']=='Bash' and x['s'].startswith('[bg]') and re.search(r'closing-checks|builder-checks|hooks-test|make (quick|static)',x['s']) and x['ts']<vt]
            recs.append(dict(b=v['desc'],d=d,verdict=vt,dur=mins(d,vt),nwork=len(work),nwait=len(waits),tail_idle=mins(lastwork,vt),checks_pending_at_verdict=ccpend,after=d>='2026-11-26T17:00'))
json.dump(recs,open(S+'/m16-review.json','w'),indent=0)
for lab,f in (('before 17:00Z 11-26',lambda r:not r['after']),('after',lambda r:r['after'])):
    R=[r for r in recs if r.get('verdict') and f(r)]
    if not R: continue
    nb=len(set(r['b'] for r in R))
    print(lab,': rounds',len(R),'builders',nb,'| median dur',st.median(r['dur'] for r in R),'| sum dur',round(sum(r['dur'] for r in R)),'| rounds with 0 work calls inside',sum(1 for r in R if r['nwork']==0),'| median tail idle',st.median(r['tail_idle'] for r in R),'sum tail idle',round(sum(r['tail_idle'] for r in R)),'| checks still pending at verdict',sum(1 for r in R if r['checks_pending_at_verdict']),'| tail idle where checks NOT pending',round(sum(r['tail_idle'] for r in R if not r['checks_pending_at_verdict'])), 'in', sum(1 for r in R if not r['checks_pending_at_verdict']),'rounds')
    per=[sum(r['tail_idle'] for r in R if r['b']==b) for b in set(r['b'] for r in R)]
    print('   per builder tail idle median',round(st.median(per),1),'max',max(per),' rounds per builder median',st.median([sum(1 for r in R if r['b']==b) for b in set(r['b'] for r in R)]))
print('no verdict matched:',sum(1 for r in recs if not r.get('verdict')))
for r in recs:
    if r.get('after') or r['d']>='2026-11-26T17:00': print(r)

# --- corrected: a check counts as pending at the verdict only if a background check run started before the verdict has not yet notified
import collections
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
pend_n=0; tot=0; idle_np=0.0; rounds_np=0; early=[]
CK=re.compile(r'closing-checks|builder-checks|hooks-test|make (-s )?(quick|static)|crate-checks|rust-test|rust-cover')
for v in o.values():
    if not re.search(r'451 T\d|T25[01]',v['desc']) or re.search(r'Plan review|Arbiter|impl-drift',v['desc']): continue
    ev=[e for e in v['events'] if e.get('ts')]
    mine=[r for r in recs if r['b']==v['desc'] and r.get('verdict')]
    for r in mine:
        if r['after']: continue
        tot+=1
        starts=[e for e in ev if e['k']=='Bash' and e['s'].startswith('[bg]') and CK.search(e['s']) and e['ts']<r['verdict']]
        done=[e for e in ev if e['k']=='notif' and e['s'].startswith('Background command') and e['ts']<r['verdict']]
        p=len(starts)>len(done)
        r['pending2']=p
        if p: pend_n+=1
        else: idle_np+=r['tail_idle']; rounds_np+=1
    # code edits after the first review dispatch, and rounds
    if mine:
        first=min(r['d'] for r in mine)
        W=[]
        for e in ev:
            ws=[e['s']] if e['k'] in('Edit','Write') else e.get('w',[])
            for w in ws:
                if e['ts']>first and re.match(r'(/diagram/.clones/)?(diagram-backlog[^/]*/)?(rust|scripts|tests|Makefile)',w) : W.append(e['ts'])
        early.append((v['desc'],len(mine),len(W)))
print('CORRECTED before 17:00Z: rounds',tot,'| a background check run still out at the verdict in',pend_n,'| the rest:',rounds_np,'rounds, tail idle',round(idle_np),'min')
a=[x for x in early if x[2]>0]; b=[x for x in early if x[2]==0]
print('builders with code edits after their first review dispatch:',len(a),'of',len(early),'| mean rounds',round(sum(x[1] for x in a)/max(1,len(a)),2),'vs',round(sum(x[1] for x in b)/max(1,len(b)),2),'for those with none')
print('builders with 2+ rounds:',sum(1 for x in early if x[1]>=2),'of',len(early),'; 3+:',sum(1 for x in early if x[1]>=3))
