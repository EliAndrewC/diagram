# t373: from the timing tables, a line a (table, state, session, event): the hook, the binary, process start, and the three guards with the largest medians.
import csv,sys,collections
for f in sys.argv[1:]:
    g=collections.OrderedDict()
    for r in csv.reader(open(f),delimiter='\t'):
        state,sess,arm,n,med,p90,mn,mx,cpu,rc,_,load=r[:12]; case,_,what=arm.partition(' ')
        g.setdefault((state,sess,case,load),[]).append((what,float(med),float(p90),float(cpu),rc))
    for (state,sess,case,load),rows in g.items():
        d={w:(m,p,c,rc) for w,m,p,c,rc in rows}
        def s(k): return f'{d[k][0]:.1f}/{d[k][1]:.1f}' if k in d else '-'
        only=sorted(((w.replace('--only ','').replace('-hooks',''),m,p) for w,m,p,c,rc in rows if w.startswith('--only')),key=lambda x:-x[1])
        summed=sum(m for _,m,_ in only); base=d.get('binary --version (process start)',(0,))[0]
        print(f'{f.replace("t373-","").replace(".tsv",""):9s} {state:5s} {sess:5s} {case:22s} hook {s("hook(launcher+binary)"):14s} binary {s("binary, every guard"):14s} start {s("binary --version (process start)"):8s} | '+'; '.join(f'{w} {m:.1f}/{p:.1f}' for w,m,p in only[:3])+(f' | guards-alone sum less {len(only)-1} starts {summed-base*(len(only)-1):.0f}' if only else '')+f' | load {load}')
