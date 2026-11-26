# T308 job 1: each non-first plan review round of feature 451 since 2026-11-24, classed by what it was owed for.
# Input: t308-rounds.json (t308-index.py then t308-rounds.py over the session's spec-fidelity subagent transcripts).
# The class of each round was read by hand from the prior round's verdict JSON / reply and the section's diff (t308-show2.py, t308-show3.py).
import json,collections,statistics as st
C={ # (task, round): (class, subclass, note)
('T202',2):('d','','D8 replace_all left as not a defect'),
('T207',2):('c','touch-up','a figure gained its label (observed, method)'),
('T213',2):('c','real','the Approach line restated the mechanism'),
('T215',2):('c','real','item 9 filled; Performance work yes -> no'),
('T217',2):('d','','(c) an unprobed route passed'),
('T219',2):('d','','D3 closed reader set'),
('T220',2):('d','','no backfill of one row'),
('blocks:T173-T178',2):('d','','blocks review: T223 deferral to T224 judged not legitimate (it had a filed id)'),
('T236',2):('d','','D11 what STAGE= covers'),
('T230',2):('c','real','two decisions gained'),
('T240',2):('d','',''),
('T237',2):('d','',''),
('T243',2):('b','GM words','request.md held none of the GM\'s words for the task (they were on the task line)'),
('T243',3):('d','',''),('T243',4):('d','',''),('T243',5):('d','',''),('T243',6):('d','',''),
('T243',7):('c','touch-up','restatement after CLEAR, no new decision'),
('T228',2):('c','touch-up','an evidence sentence added'),
('T235',2):('b','figure + GM words','"about 70k tokens" unlabeled; the GM\'s pre-filter request not in request.md'),
('T235',3):('e','edited during review','round 2\'s record refused: the section changed while it was being reviewed'),
('T245',2):('b','GM words','"the GM\'s three sentences in tasks.md T245" not in request.md'),
('T229',2):('c','real','item 9 filled from its placeholder; one decision added'),
('T232',2):('d','',''),
('T233',2):('b','GM words','cited docs/gm-rulings.md and 449\'s request.md; not in this request.md'),
('T248',2):('c','real','a file split recorded as a new bullet'),
('T253',2):('d','','a class fix\'s census unmeasured (FR-009)'),
('T253',3):('c','real','D3 gained a consequence; a garbled figure corrected'),
('T257',2):('c','real','found-and-left gained an item fixed here'),
('T254',2):('b','GM words','"quoted in T254\'s line of tasks.md" not in request.md; the wrong D4 cited'),
('T259',2):('b','figure','"the gate\'s 20-odd minutes", "the 634-transcript pass"'),
('T259',3):('d','',''),
('T251',2):('d','','fringe: a DEVIATION left (the remedy offered a deferral line)'),
('T251',3):('c','filed id','"Filed as T<n> by the coordinating session" became the ids'),
('T263',2):('d','','a class fix\'s census method (FR-009)'),
('T250',2):('a','','visible-text defects left with no filed id or order'),
('T265',2):('e','edited during review','round 1\'s record refused: plan.md edited 3 minutes after the bundle'),
('T265',3):('c','filed id','"Not filed by this builder" became "Filed as T277/T276"'),
('T268',2):('d','',''),
('T272',2):('c','results','item 9\'s counts and a table row restated after a test moved'),
('T292',2):('d','',''),('T292',3):('d','',''),
('T285',2):('d','','D4b land-batch releases nothing; D9c the cache budget may empty pool trees'),
('T285',3):('b','figure + GM words','"21 of 22 code builders ran cold", "six more profiles"; the 2026-11-26 words in no request.md'),
('T285',4):('d','','D6a a hold that names no feature'),
('T285',5):('a','','D9a a path-spelled git passes the guard, left with no filed id (the cure offered and taken: filed as T295)'),
('T284',2):('b','figure','"589 s", "load median 42"'),
('T284',3):('c','review-asked','a caveat the CLEAR review raised, written in; tests\' description'),
('T295',2):('d','also (a)','census bypasses left unfiled AND make -C unread'),
('T281',2):('d','',''),
('T305',2):('a','','D10 event-log booking left, no filed task'),
('T309',2):('a','','D7 test-written log entries left, no deferral'),
('T289',2):('d','','Performance work? no'),
('T104',2):('c','real','two more cases found and fixed'),
('T159',2):('c','real','scope widened to three crates'),
('T316',2):('d','also (a)','D7 pre-warm during rollout AND D11 a failure left unfiled'),
}
rows=[x for x in json.load(open('t308-rounds.json')) if x['first']<'2026-11-26T19:42']  # the corpus is frozen here: T298's round 2 was in flight
by=collections.defaultdict(list)
for x in rows: by[x['task']].append(x)
out=[];seen=set()
for t,v in by.items():
    for i in range(1,len(v)):
        k=(t,i+1)
        if k not in C: print('UNCLASSED',k,v[i]['first'],v[i-1]['verdict'],v[i]['verdict']); continue
        c=C[k]; seen.add(k)
        out.append(dict(task=t,round=i+1,start=v[i]['first'],mins=v[i]['mins'],prev=v[i-1]['verdict'],now=v[i]['verdict'],cls=c[0],sub=c[1],note=c[2]))
assert seen==set(C), set(C)-seen
json.dump(out,open('t308-class.json','w'),indent=0)
allm=[x['mins'] for x in rows]
print(f"rounds {len(rows)} over {len(by)} tasks; first rounds {len(by)}, non-first {len(out)}; all rounds median {st.median(allm):.2f} min, sum {sum(allm):.0f} min; non-first sum {sum(x['mins'] for x in out):.0f} min")
print('tasks by rounds',sorted(collections.Counter(len(v) for v in by.values()).items()))
print('| class | rounds | minutes | median min | mean min |');print('|---|---|---|---|---|')
for c in 'abcde':
    m=[x['mins'] for x in out if x['cls']==c]
    print(f"| ({c}) | {len(m)} | {sum(m):.1f} | {st.median(m):.2f} | {sum(m)/len(m):.2f} |")
print('sub-classes:')
for (c,s),n in sorted(collections.Counter((x['cls'],x['sub']) for x in out if x['sub']).items()):
    m=[x['mins'] for x in out if (x['cls'],x['sub'])==(c,s)]
    print(f"  ({c}) {s}: {n} rounds, {sum(m):.1f} min: {', '.join(x['task']+' r'+str(x['round']) for x in out if (x['cls'],x['sub'])==(c,s))}")
# the wasted first halves: the NOT-REVIEWABLE round itself
nr=[(t,i) for t,v in by.items() for i in range(len(v)-1) if C[(t,i+2)][0]=='b']
print('the NOT-REVIEWABLE rounds themselves:',len(nr),'rounds',round(sum(by[t][i]['mins'] for t,i in nr),1),'min')
ref=[x for x in rows if x['refusals']]
rc=[x for x in out if x['cls']=='a' or x['sub'] in('filed id','also (a)')]
print('root cause an id nobody had filed, every view: (a)',sum(1 for x in rc if x['cls']=='a'),'+ (c) filed id',sum(1 for x in rc if x['sub']=='filed id'),'+ (d) also (a)',sum(1 for x in rc if x['sub']=='also (a)'),'=',len(rc),'rounds',round(sum(x['mins'] for x in rc),1),'min')
print('rounds whose record was refused (section changed while reviewed):',len(ref),[x['task'] for x in ref])
with open('t308-class.md','w') as f:
    f.write('| task | round | start (UTC) | min | prior | class | what it was owed for |\n|---|---|---|---|---|---|---|\n')
    for x in out: f.write(f"| {x['task']} | {x['round']} | {x['start'][5:16]} | {x['mins']} | {x['prev']} | ({x['cls']}){' '+x['sub'] if x['sub'] else ''} | {x['note']} |\n")
