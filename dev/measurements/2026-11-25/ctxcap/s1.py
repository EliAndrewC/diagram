import pickle,statistics as st,datetime
D=pickle.load(open('parsed.pkl','rb'))
def ts(s): return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()
W={'7d':ts('2026-11-18T14:47:00'),'since1119':ts('2026-11-19T00:00:00')}
def cost(u): return u.get('input_tokens',0)+.1*u.get('cache_read_input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+5*u.get('output_tokens',0)
def q(x,p): x=sorted(x); return x[min(len(x)-1,int(p*len(x)))]
for name,t0 in W.items():
    rows=[]
    for a,v in D.items():
        for t in v['turns']:
            if t['end']>=t0 and t['start'] and t['out']>0:
                rows.append((t['ctx'],t['out'],t['end']-t['start'],cost(t['u'])))
    print(f'== {name}: {len(rows)} turns, max ctx {max(r[0] for r in rows)}')
    print('bucket(k) turns  med_s/1kout mean_s/1kout(wtd=sum s/sum out) med_s/turn p90_s  med_out  cost_per_turn(mean) cost/1kout')
    B={}
    for r in rows: B.setdefault(min(r[0]//50000,16),[]).append(r)
    for b in sorted(B):
        x=B[b]; 
        r1=[s/(o/1000) for c,o,s,_ in x if o>=50 and s<900]
        print(f'{b*50:>4}-{b*50+50:<4} {len(x):6d} {st.median(r1):7.1f} {sum(s for c,o,s,_ in x if s<900)/max(1,sum(o for c,o,s,_ in x if s<900))*1000:7.1f} {st.median(s for _,_,s,_ in x):6.1f} {q([s for _,_,s,_ in x],.9):6.1f} {st.median(o for _,o,_,_ in x):6.0f} {st.mean(c for *_,c in x):9.0f} {sum(c for *_,c in x)/sum(o for _,o,_,_ in x)*1000:8.0f}')
