import json,re,sys,os
from datetime import datetime
S=os.path.dirname(os.path.abspath(__file__))
o=json.load(open(S+'/m16-builders.json'))
def T(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def mins(a,b): return None if not a or not b else round((T(b)-T(a)).total_seconds()/60,1)
def cls(p):
    p=p.replace('/diagram/.clones/','')
    p=re.sub(r'^diagram-backlog[^/]*/','',p)
    if p.startswith(('specs/','.git','.specify')) or '/specs/' in p or '/.git/' in p: return 'plan' if 'plan' in p else 'spec'
    if p.startswith(('/tmp','$S','"$S','$L','t2','t3')) or 'scratchpad' in p: return 'scratch'
    if p.startswith(('/dev','-','$','\\','`','"',"/")) : return None
    if re.search(r'(^|/)tests?(/|\.rs)|test-|_tests?\.rs|fixtures',p): return 'test'
    return 'src'
WAIT=re.compile(r'^\s*(\[bg\] )?(cd \S+ (&&|;) )?(sleep|until|while|wait|timeout \d+ (bash -c )?.?(until|while))')
rows=[]
for tid,v in sorted(o.items(),key=lambda kv:kv[1]['start']):
    ev=[e for e in v['events'] if e.get('ts')]
    if not ev: continue
    W=[]
    for e in ev:
        if e['k'] in('Edit','Write'): W.append((e['ts'],cls(e['s'])))
        elif e['k']=='Bash':
            for w in e.get('w',[]): W.append((e['ts'],cls(w)))
    W=[w for w in W if w[1]]
    first=lambda kinds: next((t for t,k in W if k in kinds),None)
    m=dict(desc=v['desc'],t0=ev[0]['ts'],end=ev[-1]['ts'])
    m['w1']=first(('scratch','test','src')); m['t1']=first(('test',)); m['s1']=first(('src',)); m['plan1']=first(('plan',))
    dec=[e for e in ev if e['k']=='Bash' and re.search(r'make (-s )?decide',e['s'])]
    m['decide']=dec[0]['ts'] if dec else None
    cc=[e for e in ev if e['k']=='Bash' and re.search(r'make[^;|&]*closing-checks',e['s'])]
    m['closing']=cc[0]['ts'] if cc else None
    stop=min([x for x in (m['decide'],m['closing'],m['plan1']) if x] or [m['end']])
    pre=[t for t,k in W if k in('test','src') and t<=stop]
    m['e_pre']=pre[-1] if pre else None
    code=[t for t,k in W if k in('test','src')]
    m['e_last']=code[-1] if code else None
    m['test_after_src']=sum(1 for t,k in W if k=='test' and m['s1'] and t>m['s1'])
    # reviews
    revs=[]
    for e in ev:
        if e['k']=='Agent' and re.search(r'spec-fidelity',e['s']):
            d=e['ts']; name=e['s'].split('| ',1)[1]
            bg='Async agent launched' in (e.get('r') or '') or (e.get('end') and mins(d,e['end'])<0.3)
            if bg:
                vt=next((x['ts'] for x in ev if x['k']=='notif' and x['ts']>d and name[:40] in x['s']),None)
            else: vt=e.get('end')
            if not vt: revs.append(dict(name=name,d=d,v=None)); continue
            inside=[x for x in ev if d<x['ts']<vt and x['k'] not in('say','notif')]
            waits=[x for x in inside if x['k'] in('Monitor','TaskOutput') or (x['k']=='Bash' and WAIT.search(x['s']))]
            work=[x for x in inside if x not in waits]
            lastwork=max([x.get('end') or x['ts'] for x in work] or [d])
            ccdone=[x['ts'] for x in ev if x['k']=='notif' and re.search(r'losing|checks',x['s'])]
            revs.append(dict(name=name,d=d,v=vt,bg=bool(bg),dur=mins(d,vt),nwork=len(work),nwait=len(waits),idle_tail=mins(lastwork,vt) if lastwork<vt else 0.0,cc_done_after=[mins(vt,c) for c in ccdone]))
    m['revs']=revs
    rows.append(m)
json.dump(rows,open(S+'/m16-marks.json','w'))
want=sys.argv[1:]
for m in rows:
    if want and not any(w in m['desc'] for w in want): continue
    t0=m['t0']; g=lambda k: mins(t0,m[k])
    print('%-44s %s tot %5s | w1 %5s t1 %5s s1 %5s e_pre %5s plan %5s decide %5s closing %5s e_last %5s | t>s %d'%(m['desc'][:44],t0[5:16],g('end'),g('w1'),g('t1'),g('s1'),g('e_pre'),g('plan1'),g('decide'),g('closing'),g('e_last'),m['test_after_src']))
    for r in m['revs']:
        if r['v']: print('      REVIEW +%s dur %s %s work %d wait %d idle_tail %s cc_after %s | %s'%(mins(t0,r['d']),r['dur'],'bg' if r['bg'] else 'fg',r['nwork'],r['nwait'],r['idle_tail'],r['cc_done_after'][:3],r['name'][:40]))
        else: print('      REVIEW +%s no verdict seen | %s'%(mins(t0,r['d']),r['name'][:40]))
