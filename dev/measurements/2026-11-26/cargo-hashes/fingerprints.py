import json,sys,os,glob,collections,time,re
root=sys.argv[1]; want=sys.argv[2:]
deps=os.listdir(root+"/deps")
def mode(crate,h,unit):
    if unit.startswith('test-') or unit.startswith('bin-'):
        b=unit.split('-',2)[-1] if unit.startswith('test-') else unit.split('-',1)[1]
        exe=[d for d in deps if d.endswith('-'+h) and '.' not in d]
        return 'exe' if exe else 'check'
    fs=[d for d in deps if ('-'+h+'.') in d]
    if any(d.endswith('.rlib') for d in fs): return 'rlib'
    if any(d.endswith('.rmeta') for d in fs): return 'check'
    return 'gone'
tot=collections.Counter()
allrows=collections.defaultdict(list)
for d in sorted(os.listdir(root+"/.fingerprint")):
    m=re.match(r'(l7r[_a-z0-9]*)-([0-9a-f]{16})$',d)
    if not m: continue
    c,h=m.groups()
    for j in glob.glob(f"{root}/.fingerprint/{d}/*.json"):
        f=json.load(open(j)); u=os.path.basename(j)[:-5]
        if u.startswith('run-build') or u.startswith('build-script'): continue
        f.update(_h=h,_u=u,_mt=os.path.getmtime(j),_mode=mode(c,h,u)); allrows[c].append(f)
print("crate | fp dirs | units | distinct(profile) | distinct(features) | modes | distinct (unit,features,profile) | extra = dirs - that")
S=collections.Counter()
for c,rs in sorted(allrows.items(), key=lambda kv:-len(kv[1])):
    combos=set((r['_u'],r['features'],r['profile']) for r in rs)
    S['dirs']+=len(rs); S['combos']+=len(combos); S['crates']+=1
    S['ufm']+=len(set((r['_u'],r['features'],r['_mode']) for r in rs))
    if not want or c in want:
        print(f"{c} | {len(rs)} | {len(set(r['_u'] for r in rs))} | {len(set(r['profile'] for r in rs))} | {len(set(r['features'] for r in rs))} | {sorted(set(r['_mode'] for r in rs))} | {len(combos)} | {len(rs)-len(combos)}")
print(dict(S))
for c in want:
    rs=allrows[c]
    names=sorted(set(d[1] for r in rs for d in r['deps']))
    for u in sorted(set(r['_u'] for r in rs)):
        print(f"--- {c} {u}")
        ur=sorted([r for r in rs if r['_u']==u], key=lambda r:r['_mt'])
        depids={}
        for r in ur:
            dm={d[1]:d[3] for d in r['deps']}
            # letters for local workspace deps' variants
            sig=[]
            for n in names:
                if n.startswith('l7r') and n in dm:
                    k=depids.setdefault(n,{}); sig.append(f"{n[4:] if n.startswith('l7r_') else n}:{k.setdefault(dm[n],len(k))}")
            print(f"  {r['_h']} {time.strftime('%m-%d %H:%M',time.localtime(r['_mt']))} {r['_mode']:5} prof={str(r['profile'])[-5:]} feat={r['features']:16} rustc={str(r['rustc'])[-4:]} deps[{' '.join(sig)}]")
