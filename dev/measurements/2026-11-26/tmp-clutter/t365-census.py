# t365: census of /tmp's top level from the snapshot t365-census.tsv (name, type, size, mtime, uid), optional du file (kB \t path).
import re,os,sys,collections,time
snap=float(os.path.getmtime('t365-census.tsv'))
du={}
if os.path.exists('t365-du.tsv'):
    for l in open('t365-du.tsv'):
        k,p=l.rstrip('\n').split('\t',1); du[os.path.basename(p)]=int(k)*1024
def kind(n):
    m=re.match(r'^(l7r-.+)-p(\d+)-(\d+)$',n)
    if m: return ('helper: '+re.sub(r'-\d+$','-N',m.group(1)) ,m.group(2))
    m=re.match(r'^l7r-hooks-suite-(.+)-p(\d+)\..{6}$',n)
    if m: return ('l7r-hooks-suite-*-pPID.XXXXXX',m.group(2))
    m=re.match(r'^(l7r-.+?)-(\d{3,})-(\d+)$',n)
    if m: return ('old form: '+m.group(1)+'-PID-SEQ',m.group(2))
    m=re.match(r'^(l7r-[a-z-]+)',n)
    if m: return (m.group(1).rstrip('-')+'*',None)
    if n.startswith('guardlog-fixtures'): return ('guardlog-fixtures*',None)
    if n.startswith('plan-verdict-'): return ('plan-verdict-*.json',None)
    if n.startswith('tmp.'): return ('tmp.* (mktemp)',None)
    if n.startswith('rollchild'): return ('rollchild*',None)
    if n.startswith('pymp-'): return ('pymp-*',None)
    if re.match(r'^[tT]\d+',n): return ('t<N>* (task scratch)',None)
    m=re.match(r'^([A-Za-z]+)',n)
    return ((m.group(1) if m else n[:3])+'*',None)
g=collections.defaultdict(lambda:{'n':0,'dirs':0,'bytes':0,'old':1e18,'new':0,'live':0,'dead':0,'ages':[0,0,0,0]})
tot=collections.Counter()
for l in open('t365-census.tsv'):
    n,ty,sz,mt,uid=l.rstrip('\n').split('\t'); mt=float(mt)
    k,pid=kind(n); r=g[k]; r['n']+=1; r['dirs']+=ty=='d'; r['bytes']+=du.get(n,int(sz)); r['old']=min(r['old'],mt); r['new']=max(r['new'],mt)
    if pid: r['live' if os.path.exists('/proc/'+pid) else 'dead']+=1
    a=(snap-mt)/3600; r['ages'][0 if a<3 else 1 if a<24 else 2 if a<72 else 3]+=1
    tot['n']+=1; tot['bytes']+=du.get(n,int(sz)); tot['l7r']+=n.startswith('l7r-')
f=lambda t: time.strftime('%m-%d %H:%M',time.localtime(t))
print(f"total entries={tot['n']} l7r-*={tot['l7r']} bytes={tot['bytes']/1e9:.2f} GB (du {'yes' if du else 'NO: top-level inode sizes only'})")
print("count\tdirs\tMB\toldest\tnewest\t<3h\t3-24h\t1-3d\t>3d\tpid-live\tpid-dead\tprefix")
key=(lambda kv:-kv[1]['bytes']) if '--by-bytes' in sys.argv else (lambda kv:-kv[1]['n'])
for k,r in sorted(g.items(),key=key)[:int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 45]:
    print(f"{r['n']}\t{r['dirs']}\t{r['bytes']/1e6:.1f}\t{f(r['old'])}\t{f(r['new'])}\t"+"\t".join(map(str,r['ages']))+f"\t{r['live']}\t{r['dead']}\t{k}")
