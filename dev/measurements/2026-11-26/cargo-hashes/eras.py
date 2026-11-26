import json,sys,os,glob,re,collections
def load(root):
    rows=[]
    deps=collections.defaultdict(int)
    for d in os.scandir(root+"/deps"):
        m=re.search(r'-([0-9a-f]{16})(\.|$)',d.name)
        if m: deps[m.group(1)]+=d.stat().st_blocks*512
    for d in os.listdir(root+"/.fingerprint"):
        m=re.match(r'(l7r[_a-z0-9]*)-([0-9a-f]{16})$',d)
        if not m: continue
        for j in glob.glob(f"{root}/.fingerprint/{d}/*.json"):
            u=os.path.basename(j)[:-5]
            if 'build-script' in u: continue
            f=json.load(open(j)); rows.append(dict(c=m.group(1),h=m.group(2),u=u,feat=f['features'],prof=f['profile'],rustc=f['rustc'],size=deps[m.group(2)],mt=os.path.getmtime(j)))
    return rows
old=load(sys.argv[1]); new=load(sys.argv[2])
live=set((r['c'],r['u'],r['prof']) for r in new)
dead=[r for r in old if (r['c'],r['u'],r['prof']) not in live]
cur=[r for r in old if (r['c'],r['u'],r['prof']) in live]
G=2**30
print(f"{sys.argv[1]}: {len(old)} workspace fingerprint dirs, deps files {sum(r['size'] for r in old)/G:.1f} GB")
print(f"  profile hash no build at HEAD produces (config history): {len(dead)} dirs, deps files {sum(r['size'] for r in dead)/G:.1f} GB")
print(f"  profile hash a build at HEAD produces: {len(cur)} dirs, {sum(r['size'] for r in cur)/G:.1f} GB")
k=set((r['c'],r['u'],r['prof'],r['feat']) for r in cur)
print(f"    distinct (unit, mode+profile, own features): {len(k)}; further dirs differing only in a dependency's hash: {len(cur)-len(k)}")
kn=set((r['c'],r['u'],r['prof'],r['feat']) for r in new)
print(f"  the day-old tree {sys.argv[2]}: {len(new)} dirs, distinct (unit, mode+profile, own features) {len(kn)}, dependency-only siblings {len(new)-len(kn)}")
