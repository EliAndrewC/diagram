import re,subprocess,sys
F='specs/451-time-retro-and-efficiency/tasks.md'
def show(ref):
    return subprocess.run(['git','show',f'{ref}:{F}'],capture_output=True,text=True).stdout.split('\n')
def cont(L):
    d={}
    for i,l in enumerate(L):
        m=re.match(r'- \[ \] (T\d+) ',l)
        if m: d[m.group(1)]= i+1<len(L) and L[i+1].startswith('      ')
    return d
def lost(a,b,res):
    A,B,R=cont(show(a)),cont(show(b)),cont(show(res))
    return sorted(k for k in R if (A.get(k) or B.get(k)) and not R[k])
if __name__=='__main__':
    for line in open(sys.argv[1]):
        if 'CONFLICT' not in line: continue
        h,o=line.split()[:2]
        print(h, 'session lost', lost(h+'~1',o,h))
