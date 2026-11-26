import pickle,statistics as st,datetime
D=pickle.load(open('parsed.pkl','rb')); H=pickle.load(open('handoffs.pkl','rb'))
def ts(s): return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()
t0=ts('2026-11-19T00:00:00')
def cost(u): return u.get('input_tokens',0)+.1*u.get('cache_read_input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+5*u.get('output_tokens',0)
def q(x,p): x=sorted(x); return x[min(len(x)-1,int(p*len(x)))]
# band rates since 1119
rows=[(t['ctx'],t['out'],t['end']-t['start'],t['u']) for v in D.values() for t in v['turns'] if t['end']>=t0 and t['start'] and t['out']>0 and t['end']-t['start']<900]
bands=[(0,300000),(300000,500000),(500000,800000),(800000,10**9)]
rate={};per={}
for lo,hi in bands:
    x=[r for r in rows if lo<=r[0]<hi]
    rate[lo]=sum(r[2] for r in x)/sum(r[1] for r in x)*1000
    out=st.mean(r[3].get('output_tokens',0) for r in x)
    cw=st.mean(r[3].get('cache_creation_input_tokens',0) for r in x)
    fi=st.mean(r[3].get('input_tokens',0) for r in x)
    per[lo]=(out,cw,fi,len(x))
    print('band',lo,'n',len(x),'s/1kout wtd %.2f'%rate[lo],'med %.2f'%st.median(r[2]/(r[1]/1000) for r in x if r[1]>=50),'mean out/turn %.0f cw/turn %.0f s/turn %.2f'%(out,cw,st.mean(r[2] for r in x)))
# handoffs
cap=[h for h in H if h['old_max_ctx']>=290000 and h['old_start']>=t0]
print('handoffs total (any) since1119',len([h for h in H if h['old_start']>=t0]),'cap-hit (old ctx>=290k)',len(cap))
m=[h for h in cap if h['reread_min'] is not None]
print('with measurable reread',len(m))
rm=[h['reread_min'] for h in m]; rc=[h['reread_cost'] for h in m]
print('reread min median %.1f mean %.1f p90 %.1f total %.0f'%(st.median(rm),st.mean(rm),q(rm,.9),sum(rm)))
print('reread cost(k) median %.0f mean %.0f total(M) %.1f'%(st.median(rc)/1e3,st.mean(rc)/1e3,sum(rc)/1e6))
print('reread turns median',st.median(h['reread_turns'] for h in m))
# fresh own rate after first edit
fs=sum(h['new_sec_after'] for h in m); fo=sum(h['new_out_after'] for h in m)
fresh=fs/fo*1000; print('fresh builders post-edit s/1kout %.2f (turn-latency only), median ctx %.0f'%(fresh,st.median(h['new_rate_ctx'] for h in m)))
R=[h['new_out_after'] for h in m]
print('R remaining out: median %.0f p90 %.0f mean %.0f'%(st.median(R),q(R,.9),st.mean(R)))
# saved estimate per handoff
slow=rate[300000]
sav=[h['new_out_after']*(slow-fresh)/1000/60 for h in m]
print('est minutes old builder would have paid extra (slow-fresh) per handoff: median %.1f total %.0f ; slow=%.2f'%(st.median(sav),sum(sav),slow))
print('net minutes lost(reread) - saved: total %.0f'%(sum(rm)-sum(sav)))
# those since 11-19 regardless: total reread minutes
# break-even
fresh_ctx=st.median(h['new_rate_ctx'] for h in m)
# start ctx of fresh at first edit: approximate from reread turns last ctx
import itertools
sc=[]
for h in m:
    tt=[t for t in D[h['new']]['turns'] if t['end']<=h['new_start']+h['reread_min']*60]
    if tt: sc.append(tt[-1]['ctx'])
C0=st.median(sc); print('fresh ctx at first edit median %.0f'%C0)
def rt(C): 
    for lo,hi in reversed(bands):
        if C>=lo: return rate[lo]
pm=per[0]; 
g=st.mean(r[3].get('output_tokens',0)+r[3].get('cache_creation_input_tokens',0) for r in rows) # growth/turn
out_pt=st.mean(r[3].get('output_tokens',0) for r in rows); cw_pt=st.mean(r[3].get('cache_creation_input_tokens',0) for r in rows)
print('growth/turn %.0f out/turn %.0f cw/turn %.0f'%(g,out_pt,cw_pt))
def run(C,Rr,reread_min=0,reread_cost=0,fast=False):
    n=Rr/out_pt; mins=0; c=reread_cost
    # integrate in 50 chunks
    for i in range(50):
        ctx=C+g*n*(i+.5)/50; k=n/50
        c+=k*(.1*ctx+1.25*cw_pt+5*out_pt)
        mins+=k*out_pt/1000*(fresh if fast else rt(ctx))/60
    return mins+reread_min,c
mm=st.median(rm); mc=st.median(rc)
print('\nbreak-even: C, R | continue min, cost(k) | handoff min, cost(k) | dmin, dcost(k)')
for lbl,Rr in (('median',st.median(R)),('p90',q(R,.9))):
    for C in (300000,400000,500000,600000,800000):
        a=run(C,Rr); b=run(C0,Rr,mm,mc,fast=True)
        print(f'{lbl} R={Rr:.0f} C={C//1000}k | {a[0]:.1f} {a[1]/1e3:.0f} | {b[0]:.1f} {b[1]/1e3:.0f} | {b[0]-a[0]:+.1f} {(b[1]-a[1])/1e3:+.0f}')
