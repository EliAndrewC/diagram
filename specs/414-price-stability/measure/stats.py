import json,math,statistics as st,sys
D=sys.argv[1]
def load(f):
    s=json.load(open(D+'/'+f))['series']['docs'][0]
    return {p:v for p,v in zip(s['period'],s['value']) if isinstance(v,(int,float))}
cpi=load('db_cpi.json')
def ann_avg(ser,y):
    v=[ser.get(f'{y}-{m:02d}') for m in range(1,13)]
    v=[x for x in v if x is not None]
    return sum(v)/len(v) if len(v)==12 else None
def sd(x): return st.pstdev(x) if len(x)>1 else float('nan')
print("== US CPI-U NSA, annual-average inflation")
years=range(1914,2025)
infl={}
for y in years:
    a,b=ann_avg(cpi,y-1),ann_avg(cpi,y)
    if a and b: infl[y]=100*math.log(b/a)
for lo,hi in [(1972,2024),(1914,1970),(1950,1970),(1972,1982),(1983,2019),(1992,2019),(2020,2024)]:
    xs=[infl[y] for y in range(lo,hi+1) if y in infl]
    print(f"{lo}-{hi}: mean {st.mean(xs):.2f}%/yr (log), sd {sd(xs):.2f}, min {min(xs):.2f}, max {max(xs):.2f}, n={len(xs)}")
print("decade cumulative (Dec-to-Dec):")
for d0 in range(1970,2030,10):
    a=cpi.get(f'{d0}-12'); b=cpi.get(f'{min(d0+10,2024)}-12')
    if a and b: print(f" Dec{d0}-Dec{min(d0+10,2024)}: x{b/a:.3f} ({100*((b/a)**(1/(min(d0+10,2024)-d0))-1):.2f}%/yr)")
a=cpi['1971-08']; b=cpi['2024-12']; print(f"Aug1971-Dec2024: x{b/a:.2f}, {100*((b/a)**(1/53.33)-1):.2f}%/yr")
a=cpi['1913-01']; b=cpi['1970-12']; print(f"Jan1913-Dec1970: x{b/a:.2f}")
def monthly(ser,lo,hi):
    ks=sorted(k for k in ser if lo<=k<=hi)
    out=[]
    for i in range(1,len(ks)):
        y,m=map(int,ks[i-1].split('-')); nm=f'{y+(m==12)}-{(m%12)+1:02d}'
        if ks[i]==nm: out.append(100*math.log(ser[ks[i]]/ser[ks[i-1]]))
    return out
def yoy(ser,lo,hi):
    out=[]
    for k in sorted(ser):
        if lo<=k<=hi:
            y,m=k.split('-'); p=f'{int(y)-1}-{m}'
            if p in ser: out.append(100*math.log(ser[k]/ser[p]))
    return out
print("== monthly log changes")
for lo,hi in [('1972-01','2024-12'),('1984-01','2019-12'),('1913-02','1970-12')]:
    m=monthly(cpi,lo,hi); y=yoy(cpi,lo,hi)
    print(f"CPI {lo}..{hi}: monthly sd {sd(m):.3f}% mean {st.mean(m):.3f}; mean |monthly| {st.mean(map(abs,m)):.3f}; 12-mo sd {sd(y):.2f}% mean {st.mean(y):.2f}")
for f,name in [('db_rice.json','rice'),('db_APU0000708111.json','eggs'),('db_APU0000701111.json','flour')]:
    s=load(f)
    for lo,hi in [('1980-01','2024-12'),('1984-01','2019-12')]:
        m=monthly(s,lo,hi); y=yoy(s,lo,hi)
        # real
        r={k:v/cpi[k] for k,v in s.items() if k in cpi}
        mr=monthly(r,lo,hi); yr=yoy(r,lo,hi)
        print(f"{name} {lo}..{hi}: n={len(m)} monthly sd {sd(m):.2f}% mean|.| {st.mean(map(abs,m)):.2f}; 12-mo sd {sd(y):.2f}% (range {min(y):.1f}..{max(y):.1f}); real 12-mo sd {sd(yr):.2f}")
    ks=sorted(s); print(f"  {name} first {ks[0]} {s[ks[0]]} last {ks[-1]} {s[ks[-1]]}")
