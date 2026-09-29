import json,pathlib,re,collections,importlib.util
spec=importlib.util.spec_from_file_location("x","extract_norm.py");xm=importlib.util.module_from_spec(spec);spec.loader.exec_module(xm)
P=json.load(open('per_url.json')); Q=json.load(open('session_questions.json'))
URLRE=re.compile(r"https?://[^\s\"'<>|\\)]+")
ROOTS=[pathlib.Path("/diagram/.claude/skills/diagram/research")]+sorted(pathlib.Path("/diagram/.clones").glob("*/.claude/skills/diagram/research"))
reg=set(); citq=collections.defaultdict(set)
for RR in ROOTS:
    for f in (RR/"sources").rglob("*.html"):
        for u in URLRE.findall(f.read_text(errors="replace")): reg.add(xm.norm(u.replace("&amp;","&")))
    for f in RR.rglob("*.notes.html"):
        q=f.parent.name+"/"+f.name.replace(".notes.html","")
        for u in URLRE.findall(f.read_text(errors="replace")):
            n=xm.norm(u.replace("&amp;","&")); reg.add(n); citq[n].add(q)
VER={"quote-check","source-applicability","source-reader"}
QUOTED=re.compile(r'(「[^」]{3,}」|"[^"]{6,}"|“[^”]{6,}”)')
def kind(e):
    if e['atype'] in VER: return 'verify'
    w=e.get('why') or ''
    if e['kind']=='fetch' and QUOTED.search(w) and re.search(r'(?i)verbatim|exact|containing|character',w): return 'verify'
    return 'new'
out=collections.Counter(); tok=collections.Counter(); carry=collections.Counter()
nq_hist=collections.Counter(); citeq_hist=collections.Counter()
multi=0; first_full=0; rows=[]
for u,v in P.items():
    if u not in reg: continue
    qs=set()
    for e in v: qs|=set(Q.get(e['session'],[]))
    nq=len(qs); nq_hist[min(nq,6)]+=1; citeq_hist[min(len(citq.get(u,())),6)]+=1
    if nq>=2: multi+=1
    seenq=set()
    for i,e in enumerate(v):
        eq=set(Q.get(e['session'],[]))
        if i==0: seenq|=eq; continue
        k=kind(e)
        # a 'new' read serving a question not seen before for this source = a new-question read
        if k=='new': k='new: other question' if (eq-seenq) else 'new: same question/unknown'
        out[k]+=1; tok[k]+=e['tok']; carry[k]+=e['carry']
        seenq|=eq
    rows.append((u,nq,len(citq.get(u,())),len(v)))
res={"cited_read":sum(1 for u in P if u in reg),"cited_read_in_sessions_of_2plus_questions":multi,"questions_per_cited_source_(session_sections)":dict(sorted(nq_hist.items())),
     "citing_questions_per_cited_source_(footnotes)":dict(sorted(citeq_hist.items())),"split_count":out,"split_tok":tok,"split_carry":carry,
     "first_read_tok_cited":sum(v[0]['tok'] for u,v in P.items() if u in reg),"first_read_carry_cited":sum(v[0]['carry'] for u,v in P.items() if u in reg)}
json.dump(res,open('cited_questions.json','w'),indent=1)
print(json.dumps(res,indent=1))
