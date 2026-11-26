import json,subprocess,sys
R='/diagram/.clones/diagram-backlog'
out={}
for f in ['449-rust-codebase','451-time-retro-and-efficiency']:
    p=f'specs/{f}/plan-review.json'
    log=subprocess.run(['git','-C',R,'log','--reverse','--format=%h %cI',"--since=2026-11-19",'--',p],capture_output=True,text=True).stdout.split('\n')
    log=[l for l in log if l]
    # also the commit just before the window
    prev={}
    seq={}  # task -> list of (commit,date,verdict,sha)
    allc=subprocess.run(['git','-C',R,'log','--reverse','--format=%h %cI','--',p],capture_output=True,text=True).stdout.split('\n')
    allc=[l for l in allc if l]
    for l in allc:
        h,d=l.split()
        s=subprocess.run(['git','-C',R,'show',f'{h}:{p}'],capture_output=True,text=True).stdout
        try: j=json.loads(s)
        except Exception: continue
        cur={}
        for t,v in j.get('tasks',{}).items():
            key=(v.get('verdict'),v.get('section_sha256'),v.get('reviewed'))
            cur[t]=key
            if prev.get(t)!=key:
                seq.setdefault(t,[]).append(dict(commit=h,date=d,verdict=v.get('verdict'),sha=v.get('section_sha256')[:8],reviewed=v.get('reviewed'),
                  nonlegit=[ (x.get('id'),x.get('class'),x.get('ruling'),x.get('summary')[:160]) for x in v.get('decisions',[]) if x.get('ruling') and 'NOT' in str(x.get('ruling')).upper() or x.get('class') in('narrowing','widening')]))
        prev=cur
    out[f]=seq
json.dump(out,open('hist.json','w'),indent=1)
for f,seq in out.items():
    n=len(seq); multi={t:v for t,v in seq.items() if any(x['verdict']!='CLEAR' for x in v)}
    print(f,n,'tasks;',len(multi),'with non-CLEAR state ever seen')
    for t,v in multi.items(): print(' ',t,[(x['date'][:10],x['verdict']) for x in v])
