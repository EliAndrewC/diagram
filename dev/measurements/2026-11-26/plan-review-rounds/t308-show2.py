import json,re,difflib,collections,sys
rows=json.load(open('t308-rounds.json'))
by=collections.defaultdict(list)
for x in rows: by[x['task']].append(x)
DL=re.compile(r'^\*\*D\d+[a-z]?\s+-\s')
def decs(x):
    s=x.get('vjson') or ''
    m=re.search(r'\{\s*\\?"section_sha256.*\}',s,re.S)
    if not m: return None
    txt=m.group(0)
    for cand in (txt, txt.encode().decode('unicode_escape',errors='ignore')):
        # trim to balanced
        for end in range(len(cand),0,-1):
            if cand[end-1]=='}':
                try: return json.loads(cand[:end])['decisions']
                except Exception: continue
            if len(cand)-end>400: break
    return None
n=0
lo,hi=int(sys.argv[1]),int(sys.argv[2])
for t,v in by.items():
    for i in range(1,len(v)):
        n+=1
        if not lo<=n<=hi: continue
        p,c=v[i-1],v[i]
        print(f'##### {n} {t} r{i+1} {c["first"][5:16]} {c["mins"]}min prev={p["verdict"]} now={c["verdict"]} same_sha={p["sha"]==c["sha"]} gap={c["first"][5:16]} prev_end={p["last"][5:16]} ref={len(c["refusals"])}')
        if c['extra']: print(' PROMPT+:',c['extra'][:350].replace('\n',' '))
        if p['verdict']!='CLEAR':
            ds=decs(p)
            if ds is None: print(' PREV REPLY:',(p['reply'] or '')[:600].replace('\n',' '))
            else:
                for d in ds:
                    if (d.get('ruling') or '').upper().startswith('NOT'):
                        print('  BLOCK:',d.get('id'),'|',d.get('class'),'|',d.get('ruling'),'|',(d.get('why') or '')[:330].replace('\n',' '))
        if p['sec'] and c['sec'] and p['sha']!=c['sha']:
            a=p['sec'].split('\n'); b=c['sec'].split('\n')
            d=[l for l in difflib.unified_diff(a,b,lineterm='',n=0) if not l.startswith(('---','+++','@@'))]
            dl=sum(1 for l in d if DL.match(l[1:]))
            print(f' DIFF lines {len(d)} (decision lines {dl}) of {len(b)}')
            if p['verdict']=='CLEAR':
                minus=[l[1:] for l in d if l[0]=='-']; plus=[l[1:] for l in d if l[0]=='+']
                for k in range(max(len(minus),len(plus))):
                    A=minus[k] if k<len(minus) else ''; B=plus[k] if k<len(plus) else ''
                    sm=difflib.SequenceMatcher(None,A,B,autojunk=False)
                    for tag,i1,i2,j1,j2 in sm.get_opcodes():
                        if tag!='equal': print(f'   {A[:14]!r} {tag}: [{A[i1:i2][:110]}] -> [{B[j1:j2][:170]}]')
                    if k>3: break
        print()
