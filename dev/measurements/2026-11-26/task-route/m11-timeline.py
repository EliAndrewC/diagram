#!/usr/bin/env python3
"""m11-timeline.py: per small task - filed, builder start/end, first code edit, code commit, tick (UTC), and make task-time's own totals."""
import pickle,subprocess,datetime,re,statistics as st,os
S=os.path.dirname(os.path.abspath(__file__))+'/'
R='/diagram/.clones/diagram-backlog-land'
r=pickle.load(open(S+'m11-decomp.pkl','rb'))
def ts(s): return datetime.datetime.fromisoformat(s).timestamp()
f=lambda t:datetime.datetime.fromtimestamp(t,datetime.UTC).strftime('%d %H:%M') if t else '-'
log=subprocess.run(['git','-C',R,'log','origin/main','--since=2026-11-25','--format=%cI|%s'],capture_output=True,text=True).stdout.splitlines()
tt=open(S+'m11-tt72.txt').read()
SMALL=['T252','T263','T267','T268','T269','T270','T271','T272','T248','T249','T262']
print('| task | filed | builder start | first code edit | builder end | code commit | tick (landed) | filed->landed min | builder start->landed | first code edit->code commit | task-time: whole min / blocking |'); print('|---|---|---|---|---|---|---|---|---|---|---|')
A=[];Bq=[];C=[];M=[];BL=[]
for T in SMALL:
    filed=min([ts(l.split('|')[0]) for l in log if re.search(r'\b%s\b'%T,l) and ' filed' in l] or [0])
    tick=max([ts(l.split('|')[0]) for l in log if re.search(r'\b%s\b'%T,l) and 'ticked (make land)' in l and not l.split('|')[1].startswith('Revert')] or [0])
    code=min([ts(l.split('|')[0]) for l in log if re.match(r'451 (T\d+\+)?%s\b|451 T\d+\+%s\b'%(T,T),l.split('|',1)[1]) and 'work in progress' not in l] or [0])
    lg=r[T]['log']; bs=lg[0][0]; be=lg[-1][0]
    fe=min([t for t,s,n,b in lg if s=='b' and (n in('Edit','Write') or re.search(r"<<\s*'?(EOF|PY)|sed -i",b[:110]))] or [0])
    m=re.search(r'## 451-time-retro-and-efficiency %s \(landed.*?\n\nIts whole time[^\n]*?: ([\d.]+) min, ([\d.]+) min blocking'%T,tt)
    whole,blk=(float(m.group(1)),float(m.group(2))) if m else (0,0)
    a=(tick-filed)/60 if filed and tick else None; b2=(tick-bs)/60; c=(code-fe)/60 if fe and code else None
    if T in SMALL[:8]:
        if a: A.append(a)
        Bq.append(b2); 
        if c: C.append(c)
        M.append(whole); BL.append(blk)
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %.0f | %s | %.0f / %.0f |'%(T,f(filed),f(bs),f(fe),f(be),f(code),f(tick),'%.0f'%a if a else '-',b2,'%.0f'%c if c else '-',whole,blk))
print('| median, the 8 small | | | | | | | %.0f (n=%d) | %.0f | %.0f (n=%d) | %.0f / %.0f |'%(st.median(A),len(A),st.median(Bq),st.median(C),len(C),st.median(M),st.median(BL)))
