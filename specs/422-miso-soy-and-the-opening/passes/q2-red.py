import sys, statistics, xlrd
b = xlrd.open_workbook(sys.argv[1])
eras = {"osaka-1706":(1706,1711,1.875),"osaka-1712":(1712,1718,1.5),"kyoto-1745":(1745,1754,1.725),"kyoto-1790":(1790,1799,1.725),"kyoto-1800":(1800,1817,1.725),
        "edo-1818":(1818,1829,1.35),"edo-1830":(1830,1844,0.975),"edo-1850":(1850,1859,0.975),"edo-1860":(1860,1867,0.4875)}
KG=37.5; L=180.891
for sh in ("Mitsui Bunko Kyoto T6","Mitsui Bunko Edo T7","Mitsui Bunko Osaka T8"):
    s=b.sheet_by_name(sh); rows=[]; y=None
    for r in range(8,s.nrows):
        v=s.row_values(r)
        if isinstance(v[0],float): y=int(v[0])
        if v[2] in ("Spring","Fall"): rows.append((r+1,y,v[2],v[7],v[8]))
    for e,(a,z,g) in eras.items():
        sel=[x for x in rows if a<=x[1]<=z]
        if not sel: continue
        for i,name,unit in ((3,"miso","10 kan"),(4,"soy","1 koku")):
            xs=[x[i] for x in sel if isinstance(x[i],float)]
            if not xs: print(sh,e,name,"no cells"); continue
            m=statistics.mean(xs); d=KG if name=="miso" else L
            print(f"{sh[13:]:10} {e:11} {name:4} n={len(xs):2} yrs {min(x[1] for x in sel)}-{max(x[1] for x in sel)} mean {m:.2f} range {min(xs)}-{max(xs)} monme/{unit} | at era {g} g: {m*g/d:.3f} g/{'kg' if name=='miso' else 'L'} (range {min(xs)*g/d:.3f}-{max(xs)*g/d:.3f}) | at 3.11: {m*3.11/d:.3f}")
