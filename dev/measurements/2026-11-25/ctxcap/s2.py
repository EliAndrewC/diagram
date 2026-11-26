import pickle,statistics as st,datetime,re,json
D=pickle.load(open('parsed.pkl','rb'))
def ts(s): return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()
def cost(u): return u.get('input_tokens',0)+.1*u.get('cache_read_input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+5*u.get('output_tokens',0)
HW=lambda v:[e for e in v['events'] if e[1] in('Write','Edit') and 'l7r-handoffs' in e[2]]
old={a:v for a,v in D.items() if v['refused'] or HW(v)}
print('refused',sum(v['refused'] for v in D.values()),'handoff-writers',sum(1 for v in D.values() if HW(v)),'union',len(old))
# successors
succ={}
for a,v in D.items():
    for m in v['mentions']:
        for o in old:
            if o in m and o!=a: succ.setdefault(o,[]).append(a)
print('old with successor',len(succ))
res=[]
for o,ss in succ.items():
    ov=D[o]
    if not ov['turns']: continue
    s=min(ss,key=lambda x:D[x]['start']); sv=D[s]
    t0=sv['start']
    # first non-handoff Edit/Write
    fe=[e for e in sv['events'] if e[1] in('Write','Edit') and 'l7r-handoffs' not in e[2] and '/scratchpad' not in e[2]]
    tfe=fe[0][0] if fe else None
    pre=[t for t in sv['turns'] if tfe and t['end']<=tfe]
    res.append(dict(old=o,new=s,old_max_ctx=max(t['ctx'] for t in ov['turns']),old_start=ov['start'],old_end=ov['end'],
      new_start=t0,new_end=sv['end'],wall_new=(sv['end']-t0)/60,reread_min=(tfe-t0)/60 if tfe else None,
      reread_cost=sum(cost(t['u']) for t in pre) if tfe else None,reread_turns=len(pre),
      new_out_total=sum(t['out'] for t in sv['turns']),new_out_after=sum(t['out'] for t in sv['turns'] if tfe and t['end']>tfe),
      new_cost_total=sum(cost(t['u']) for t in sv['turns']),
      new_sec_after=sum(t['end']-t['start'] for t in sv['turns'] if tfe and t['end']>tfe and t['start']),
      new_rate_ctx=st.median(t['ctx'] for t in sv['turns']),
      n_succ=len(ss)))
pickle.dump(res,open('handoffs.pkl','wb'))
for r in sorted(res,key=lambda r:r['old_start']):
    print(datetime.datetime.utcfromtimestamp(r['old_start']).strftime('%m-%d %H:%M'),r['old'][:6],'->',r['new'][:6],'oldctx',r['old_max_ctx']//1000,'k reread_min',None if r['reread_min'] is None else round(r['reread_min'],1),'cost',None if r['reread_cost'] is None else round(r['reread_cost']/1000),'k newout',r['new_out_total'],'after',r['new_out_after'],'wall',round(r['wall_new']))
