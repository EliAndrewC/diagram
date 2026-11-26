import subprocess,re,sys,difflib
R='/diagram/.clones/diagram-backlog'
def sh(*a): return subprocess.run(['git','-C',R,*a],capture_output=True,text=True).stdout
def section(txt,t):
    lines=txt.split('\n'); out=[];on=False
    for l in lines:
        m=re.match(r'### (T\d+)\b',l)
        if m:
            on = (m.group(1)==t)
        elif re.match(r'## ',l): on=False
        if on: out.append(l)
    return '\n'.join(out)
def revs(f,t,since,until):
    res=[]
    for fn in ['plan.md','plan-done.md']:
        p=f'specs/{f}/{fn}'
        for l in sh('log','--reverse','--format=%h %cI','--since='+since,'--until='+until,'--',p).split('\n'):
            if not l: continue
            h,d=l.split(); s=section(sh('show',f'{h}:{p}'),t)
            if s: res.append((d,h,fn,s))
    res.sort(); return res
if __name__=='__main__':
    f,t,since,until=sys.argv[1:5]
    prev=None
    for d,h,fn,s in revs(f,t,since,until):
        if prev is not None and s!=prev:
            df=[x for x in difflib.unified_diff(prev.split('\n'),s.split('\n'),lineterm='',n=0) if x[:1] in '+-' and x[:3] not in('+++','---')]
            print(f'--- {d[5:16]} {h} {fn} +{sum(x[0]=="+" for x in df)} -{sum(x[0]=="-" for x in df)}')
            for x in df[:int(sys.argv[5]) if len(sys.argv)>5 else 12]: print('   ',x[:260])
        elif prev is None: print('first',d[5:16],h,fn,len(s))
        prev=s
