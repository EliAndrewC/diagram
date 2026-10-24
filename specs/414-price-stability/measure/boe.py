import openpyxl,sys,math,statistics as st,csv
wb=openpyxl.load_workbook(sys.argv[1],read_only=True,data_only=True)
ws=wb['A47. Wages and prices']
rows=list(ws.iter_rows(min_row=1,max_row=830,values_only=True))
print('HDR3:',rows[2][3]); print('SRC3:',rows[4][3]); print('UNIT:',rows[5][3])
P={}
for r in rows[6:]:
    try: y=int(r[0]); v=float(r[3])
    except: continue
    P[y]=v
with open(sys.argv[2],'w') as f:
    w=csv.writer(f); [w.writerow([y,P[y]]) for y in sorted(P)]
ys=sorted(P); print('years',ys[0],ys[-1])
L={y:100*math.log(P[y]/P[y-1]) for y in ys if y-1 in P}
for lo,hi in [(1210,1347),(1210,1499),(1500,1650),(1651,1750),(1751,1913),(1821,1913),(1914,1970),(1972,2016),(1984,2016),(1210,1913)]:
    xs=[L[y] for y in range(lo,hi+1) if y in L]
    drift=100*math.log(P[hi]/P[lo-1])/(hi-lo+1)
    absx=st.mean(map(abs,xs))
    big=sum(1 for x in xs if abs(x)>10)
    print(f"{lo}-{hi}: drift {drift:.2f}%/yr; sd annual {st.pstdev(xs):.2f}; mean|.| {absx:.2f}; years |chg|>10%: {big}/{len(xs)}; cum x{P[hi]/P[lo-1]:.2f}")
# decade-to-decade and century: sd of 10y log change of decade means
for lo,hi in [(1210,1499),(1500,1650),(1651,1913),(1972,2016)]:
    d=[100*math.log(P[y+10]/P[y]) for y in range(lo,hi-9) if y in P and y+10 in P]
    print(f" 10y log change {lo}-{hi}: mean {st.mean(d):.1f} sd {st.pstdev(d):.1f} min {min(d):.1f} max {max(d):.1f}")
for a,b in [(1300,1400),(1400,1500),(1500,1600),(1600,1700),(1700,1800),(1800,1900),(1900,2000)]:
    print(f" century {a}-{b}: x{P[b]/P[a]:.2f}  {100*((P[b]/P[a])**0.01-1):.2f}%/yr")
