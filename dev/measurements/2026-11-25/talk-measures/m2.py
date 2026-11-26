import pickle,re,datetime,statistics as st
T=pickle.load(open('m2turns.pkl','rb'))
T0=datetime.datetime(2026,11,19).timestamp()
def cost(u): return u.get('input_tokens',0)+.1*u.get('cache_read_input_tokens',0)+1.25*u.get('cache_creation_input_tokens',0)+5*u.get('output_tokens',0)
PATH=re.compile(r'/(rust|scripts|specs|dev|docs|\.claude)/|Makefile|tasks\.md|plan\.md')
BASH=re.compile(r'sed -i|perl -pi|python3? -I? ?<<|python3? - <<|cat > |cat >> |tee |make apply-edits|make append|git (apply|checkout --theirs|merge)|patch ')
def ownedit(t):
    r=[]
    for n,fp,cmd,_ in t['tools']:
        if n in('Edit','Write') and PATH.search(fp) and 'scratchpad' not in fp and '/tmp/' not in fp and '/jobs/' not in fp and 'l7r-handoffs' not in fp: r.append(fp)
        elif n=='Bash' and BASH.search(cmd) and 'scratchpad' not in cmd and '/tmp/' not in cmd[:60]: r.append('bash:'+cmd[:50])
    return r
idx=[i for i,t in enumerate(T) if t['end']>=T0 and ownedit(t)]
print('edit turns since 11-19',len(idx))
# compaction points
comp=[i for i in range(1,len(T)) if T[i]['ctx']<0.5*T[i-1]['ctx'] and T[i-1]['ctx']>150000]
print('compactions',len(comp))
S=[];cur=[idx[0]]
for i in idx[1:]:
    if T[i]['end']-T[cur[-1]]['end']<=600: cur.append(i)
    else: S.append(cur);cur=[i]
S.append(cur)
out=[]
for c in S:
    a,b=c[0],c[-1]
    # extend start back over up to 3 reading turns within 3 min
    while a>0 and T[c[0]]['start']-T[a-1]['end']<180 and c[0]-a<3 and a-1 not in comp: a-=1
    base=T[a-1]['ctx'] if a>0 else T[a]['ctx']
    after=T[b]['ctx']
    if any(x for x in comp if a<=x<=b): continue   # compaction inside: growth unmeasurable
    growth=after-base
    # later turns until next compaction
    nxt=next((x for x in comp if x>b),len(T))
    later=nxt-b-1
    mins=(T[b]['end']-T[a]['start'])/60
    o=sum(T[i]['out'] for i in range(a,b+1)); n=b-a+1
    pc=sum(cost(T[i]['u']) for i in range(a,b+1))
    files={f for i in c for f in ownedit(T[i])}
    kinds=len(c)
    out.append(dict(when=datetime.datetime.fromtimestamp(T[a]['start']).strftime('%m-%d %H:%M'),min=mins,turns=n,edits=kinds,files=len(files),out=o,base=base,growth=growth,later=later,
        reread=max(growth,0)*later*0.1,write=max(growth,0)*1.25,own=pc,sample=sorted(files)[:2],nagent=sum(1 for i in range(a,b+1) for x in T[i]['tools'] if x[0]=='Agent')))
pickle.dump(out,open('m2.pkl','wb'))
print(len(out),'stretches')
for r in out: print(f"{r['when']} {r['min']:5.1f}m turns {r['turns']:3d} edits {r['edits']:2d} files {r['files']:2d} out {r['out']:6d} ctx {r['base']//1000}k->+{r['growth']//1000}k later {r['later']:4d} reread {r['reread']/1000:7.0f}k own {r['own']/1000:7.0f}k  {r['sample'][0][-40:] if r['sample'] else ''}")
