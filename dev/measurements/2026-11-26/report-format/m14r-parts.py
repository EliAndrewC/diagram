#!/usr/bin/env python3
"""m14r stage 2: classify each report's text into parts (keyword rules on paragraph/bullet labels), sizes, cache shares."""
import json,re,statistics as st
d=json.load(open('m14r-extract.json')); reps=d['reports']
RULES=[('paths',r'paths? (to commit|changed)|^paths'),
 ('candidates',r'candidate|proposed task titles|titles, not filed|title to file|found and filed|notes for you|not built / left'),
 ('verify',r'to verify|how to test|to check it yourself'),
 ('red-first',r'red[- ]first|^test\b|fires-proof'),
 ('claims',r'^claims|claims-owed'),
 ('plan-review',r'plan review|^verdict|review rounds|^round \d|^ruling|arbiter|message-check|round 2 and'),
 ('checks',r'^checks|closing[- ]checks|^gates|check results|^stop point|^coverage|builder-checks|status and frictions|^tests:|other checks|wall time'),
 ('handoff-next',r'next builder|not yet done|after the fix|where it stands|current state|^status|what failed|likely spots|left for'),
 ('caveats',r'worth knowing|for the coordinating|things for you|friction|^load|caveat|known slip|escapes i took|one call to confirm|open mismatch|not mine|leave out|before t254|not searched|not edited|two notes|disk-usage|also done|environment')]
def label(u):
    m=re.match(r'\s*(?:[-*]|\d+\.)?\s*(?:#+\s*)?\*{0,2}([^*\n:.]{2,80})',u); return (m.group(1) if m else u[:60]).strip().lower()
def cls(lab,full=''):
    for k,p in RULES:
        if re.search(p,lab): return k
    return None
def units(text):
    for p in [x for x in re.split(r'\n\s*\n',text) if x.strip()]:
        head=cls(label(p))
        lines=p.split('\n'); bl=[i for i,l in enumerate(lines) if re.match(r'- \*\*',l)]
        if len(bl)>=3 and bl[0]<=1 and head is None:   # a paragraph of labeled top-level bullets
            for a,b in zip(bl,bl[1:]+[len(lines)]):
                u='\n'.join(lines[a:b]); yield (cls(label(u)) or 'built', u)
            if bl[0]==1: yield ('built',lines[0])
        else: yield (head,p)
def parts(r):
    out={}; first=True; last=None
    for k,u in units(r['result']):
        if first: k='status'; first=False
        elif k is None:
            # an unlabeled tail note about untracked files / behind main
            k='caveats' if re.search(r'untracked|commits behind|not mine|already there|handoff note',u) else ('built' if last in(None,'status') or len(u)>250 else last)
        out[k]=out.get(k,0)+len(u); last=k
    return out
if __name__=='__main__':
    allp=[parts(r) for r in reps]; keys=['status','built','red-first','checks','plan-review','claims','paths','candidates','caveats','handoff-next','verify']
    ch=[r['chars'] for r in reps]
    print('n',len(reps),'chars median',st.median(ch),'min',min(ch),'max',max(ch),'sum',sum(ch),'tokens(chars/4) median',st.median(ch)/4,'sum',sum(ch)/4)
    tot=sum(sum(p.values()) for p in allp)
    for k in keys:
        v=[p.get(k,0) for p in allp]; n=sum(1 for x in v if x)
        print(f"{k:13s} in {n:2d}/{len(reps)}  share {100*sum(v)/tot:5.1f}%  median(when present) {st.median([x for x in v if x]) if n else 0:6.0f}  median(all) {st.median(v):6.0f}")
    json.dump(allp,open('m14r-parts.json','w'))
    # turns + real cache shares
    us=d['usages']
    for n,r in enumerate(reps): pass
    for lo,hi,name in [(102239,115673,'first report -> compaction'),(115673,10**9,'compaction -> end')]:
        u=[x[1] for x in us if lo<x[0]<hi]; cr=sum(x.get('cache_read_input_tokens',0) for x in u); cc=sum(x.get('cache_creation_input_tokens',0) for x in u); i=sum(x.get('input_tokens',0) for x in u)
        print(name,'api calls',len(u),'cache_read',cr,'cache_creation',cc,'uncached',i,'read share %.4f'%(cr/(cr+cc+i)))
    # usage probes
    rows=d['rows']
    def after(line,pat,kinds=('text','tool'),n=3):
        return [(i,k,s[max(0,re.search(pat,s).start()-80):re.search(pat,s).start()+160].replace('\n',' ')) for i,ts,k,s in rows if i>line and k in kinds and re.search(pat,s)][:n]
    for name,line,pat,kinds in [('R3 table relayed?',104108,r'research and page sessions.{0,40}(4171|41\.6|949|40\.6)|2,?340|10,?026',('text',)),
      ('R1 verify',102239,r'test-context-cap-hooks\.sh',('text','tool')),('R9 verify',110797,r'check pipe-race',('text','tool')),('R16 verify',114027,r'test-state-sync\.sh',('text','tool')),
      ('R20 verify',117211,r'CRATE=rust/gate/crates/claims',('text','tool')),('R8 verify',110358,r'bash tests/hooks/test-closing-checks',('text','tool')),
      ('R6 leave-out',105643,r'b743b6',('tool',)),('R28 disk note',121455,r'disk-report-from-host|disk-usage note|disk trimming',('text','tool')),
      ('R6 research-deferred',105643,r'make research-deferred',('tool',)),('R27 verbatim',120361,r'verbatim',('tool','text')),('R31 ledger',121949,r'ledger',('tool',)),
      ('R25 cands',119984,r'builder-tree-hold|/usr/bin/git|Seed a new pool|seed a new pool',('tool',)),('R12 mismatch',111796,r'looser|only about the task being landed',('tool','text')),
      ('R10 before-T254',111427,r'gitattributes|merge driver',('text','tool')),('R13 T260',112494,r'T260',('tool',)),('R4 -land clone',105096,r'never in diagram-backlog-land',('tool',))]:
        print(name, after(line,pat,kinds,2))
