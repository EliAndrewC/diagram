import json,pathlib,re,collections
HOME=pathlib.Path.home()
S=json.load(open('sessions.json'))
IDX={}
for idx in pathlib.Path("/diagram/.clones").glob("*/.git/page-sessions/index.txt"):
    for l in idx.read_text().splitlines():
        sp=l.split()
        if len(sp)==2: IDX[sp[0]]=sp[1]
Q={}
for proj in (HOME/".claude/projects").glob("-diagram*"):
    for tp in proj.glob("*.jsonl"):
        sid=tp.stem
        if sid not in S: continue
        qs=set()
        b=IDX.get(sid)
        if b:
            bp=pathlib.Path(b)
            if not bp.is_absolute(): bp=pathlib.Path("/diagram/.clones")/S[sid]['clone']/b
            try:
                for line in bp.read_text().splitlines():
                    if line.startswith("**Your questions"):
                        qs|=set(re.findall(r"PAGE=([\w-]+)\s+SECTION=([\w-]+)",line))
                        qs|={("?",x) for x in re.findall(r"SECTION=([\w-]+)",line)} if not qs else set()
            except OSError: pass
        if not qs:
            txt=tp.read_text(errors="replace")
            qs=set(re.findall(r"PAGE=([\w-]+)\s+SECTION=([\w-]+)",txt))
        Q[sid]=sorted({s for _,s in qs})
json.dump(Q,open('session_questions.json','w'))
print(len(Q), sum(1 for v in Q.values() if v), collections.Counter(min(len(v),6) for v in Q.values()))
