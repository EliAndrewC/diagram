import xlrd,sys,math,statistics as st
b=xlrd.open_workbook(sys.argv[1]); s=b.sheet_by_name('main data sheet')
names=[str(c.value) for c in s.row(5)]
print('notes:'); n=b.sheet_by_name('Sources and notes')
for r in range(n.nrows): print('  ',' | '.join(str(c.value) for c in n.row(r) if c.value))
print([ (i,x) for i,x in enumerate(names) if x][:172])
data={}
for r in range(8,s.nrows):
    try: y=int(float(s.cell_value(r,0)))
    except: continue
    data[y]=s.row_values(r)
def ser(col):
    out={}
    for y,row in data.items():
        try: v=float(row[col]); 
        except: continue
        if v>0: out[y]=v
    return out
want=[w for w in sys.argv[2:]]
for w in want:
    cols=[i for i,x in enumerate(names) if x.lower().startswith(w.lower())]
    if not cols: print('no',w); continue
    c=cols[0]; P=ser(c)
    print('==',names[c],'col',c,'years',min(P),max(P),'n',len(P))
    for lo,hi in [(1210,1499),(1500,1650),(1651,1750),(1751,1869),(1210,1869)]:
        xs=[100*math.log(P[y]/P[y-1]) for y in range(lo,hi+1) if y in P and y-1 in P]
        if len(xs)>10: print(f'  {lo}-{hi}: sd annual log chg {st.pstdev(xs):.1f}%, mean|.| {st.mean(map(abs,xs)):.1f}, n={len(xs)}, max {max(xs):.0f} min {min(xs):.0f}')
