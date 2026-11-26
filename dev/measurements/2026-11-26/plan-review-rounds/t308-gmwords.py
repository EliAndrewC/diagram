# Candidate rule R1, replayed: the task's line of tasks.md quotes the GM, and request.md (as committed before the round) lacks the words.
import json,re,collections,glob,subprocess,os
S=os.path.dirname(os.path.abspath(__file__))
W='/diagram/.clones/diagram-backlog-t271'; F='specs/451-time-retro-and-efficiency/'
rows=[x for x in json.load(open(S+'/t308-rounds.json')) if x['first']<'2026-11-26T19:42']
by=collections.defaultdict(list)
for x in rows: by[x['task']].append(x)
tasks=open(W+'/'+F+'tasks.md').read()+''.join(open(f).read() for f in glob.glob(W+'/'+F+'tasks-done*.md'))
def fold(t): return ' '.join(re.findall(r'[a-z0-9]+',t.lower()))
def quotes(line):
    out=[]
    for m in re.finditer(r"\bthe GM\b[^'\"]{0,60}?[:,]?\s*'",line):
        i=m.end(); j=i
        while True:
            j=line.find("'",j)
            if j<0: break
            if not (j+1<len(line) and line[j+1].isalnum() and line[j-1].isalnum()): break   # an apostrophe inside a word
            j+=1
        if j>0: out.append(line[i:j])
    return out
def req_at(ts):
    c=subprocess.run(['git','-C',W,'log','-1','--format=%H','--before='+ts,'--',F+'request.md'],capture_output=True,text=True).stdout.strip()
    return subprocess.run(['git','-C',W,'show',c+':'+F+'request.md'],capture_output=True,text=True).stdout
fires=[]
for t,v in by.items():
    if t.startswith('blocks'): continue
    m=re.search(r'^- \[.\] '+t+r'\b.*$',tasks,re.M)
    if not m: print('no line',t); continue
    qs=[q for q in quotes(m.group(0)) if len(fold(q).split())>=4]
    req=fold(req_at(v[0]['first']))
    miss=[q for q in qs if not all(fold(p) in req for p in re.split(r'\.\.\.|…',q) if fold(p))]
    if miss: fires.append((t,v[0]['verdict'],len(v),len(qs),len(miss),miss[0][:60]))
    by[t][0]['r1']=dict(q=len(qs),miss=len(miss))
print('tasks',len([t for t in by if not t.startswith('blocks')]),'with a GM quote on the line',sum(1 for t in by if by[t][0].get('r1',{}).get('q')),'fires',len(fires))
for f in fires: print(f)
