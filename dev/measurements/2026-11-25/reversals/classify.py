import json,collections,csv
m=json.load(open('match.json'))
# class, confidence (H/M/L), one-line basis
C={
'449-T202':('b','M','order of old-code read vs new placer'),
'449-T204':('c','M','guard passed lister-fed forms; refuse them'),
'449-T152':('c','M','fix gate/defect instead of DEVIATION; order a found defect'),
'449-T209':('c','H','county leaders crossing a building: fix'),
'449-T223':('b','H','two found-and-left defects need task id + order'),
'449-T220':('b','H','found defect T227 needs an order'),
'449-T229':('c','M','hold two more guard files'),
'449-T236':('b','M','owed glyph-check found-and-left needs a home'),
'449-T238':('c','M','undeclared-element case left unrefused'),
'449-T244':('b','M','link failure must be filed'),
'449-T158':('c','M','plan had undone 7 callers + codeid.py edits; review made it do the deletion (reverses a back-out, not implemented work)'),
'449-T243':('c','M','arbiter-accept route must not pass over budget'),
'449-T235':('a','M','re-acceptance not impossible: counts 1.70x measured'),
'449-T247':('b','M','found-and-left ground false vs census wording'),
'449-T258':('c','M','unplaced check passes: refuse; quote must match a record'),
'449-T254':('b','M','"before T158" bound / sequencing'),
'449-T289':('b','M','finding points at a Found-and-left entry that does not exist'),
'449-T292':('c','M','check refused a store beyond divider on a GUESS: loosen'),
'449-T351':('a','M','"48 discharged" read across a later county redraw: re-measure'),
'449-T377':('a','M','discharge list of nine re-compared; six kept'),
'449-T415':('c','M','live seat stage keeps belt room for every form: a defect, not a difference'),
'449-T418':('c','H','pinned bare winter carved out; refuse it too (R1->R2 diff)'),
'449-T432':('c','H','R1 bands 10.7% on toe fixed with rim (c); R2 polders unmeasured (a)'),
'451-T03':('c','M','task field lacks feature'),
'451-T25':('c','M','item-4 lint only first match'),
'451-T06':('c','M','landing stopped after push'),
'451-T15':('c','L','shared reader gaps left; fix or record'),
'451-T31':('b','M','three heredoc reads left with no home'),
'451-T44':('c','H','rg --hostname-bin unscreened; screen widened to 49 shapes, diff dropped'),
'451-T46':('d','L','index-line cut: heuristic (sentence rule) replaced by a cut-by-construction rule after rounds 1-2; round 3 added clause ids'),
'451-T09':('c','H','idle booked as waits wrongly'),
'451-T55':('a','L','foreground-run refusal unmeasured'),
'451-T11':('c','M','re-rounds windowed like the table'),
'451-T67':('c','H','copies outside the mirror, one-line string, then work-tree README rule narrowed'),
'451-T79':('d','M','catch-all (unknown word is not the mirror) replaced by resolve-then-D6; its probes passed mirror writes'),
'451-T88':('b','M','red under load left unrecorded'),
'451-T102':('d','L','date-typed (waits:) hold form unused by any line: withdrawn'),
'451-T51':('c','M','script route read added (make-only)'),
'451-T87':('c','H','CDPATH regression: HEAD refused, fix let through'),
'451-T83':('c','H','unpaired-quote bodies and nested substitutions still blanked'),
'451-T118':('c','H','unread writers counted (plan-done: "the plan review named the gap: fixed here")'),
'451-T91':('c','M','first plan review asked about D=<mirror>/x forms; added'),
'451-T153':('b','H','performance-work label wrong against GM words'),
'451-T158':('c','M','scratch worktree rule over-reaches'),
'451-T160':('a','M','search for executable-writing tests cannot see three forms'),
'451-T170':('c','M','269 wordings baselined unreviewed; list-growing messages'),
'451-T177':('c','M','R1 D6b: bundle lacked tooling_fix (added to bundle); R2 D6c judged-second by guard and kind'),
'451-T183':('b','L','D6/D10 narrowing cured by wording; round 2 new wording problem'),
'451-T186':('d','M','CJK/quotation exclusion from claim words removed (plan-done: "NOT taken out ... removed")'),
'451-T185':('c','M','split links re-owe: fix 0009/0059'),
'451-T187':('c','M','class-flip normalization limited to anchored claims; stale check'),
'451-T188':('c','H','cascade per finding, not per reply'),
'451-T193':('c','H','reread after wait, capped-builder line, builder-status probe added (MODE 4 D8-D12)'),
'451-T196':('c','M','pure split costs a dispatch: remove'),
'451-T197':('d','L','re-triage verb contradicts ruling "none built"; withdraw 81 marks'),
'451-T195':('b','H','performance-work label'),
'451-T198':('c','M','claims carved out of "a split is a move"'),
'451-T192':('c','H','tag the rest: CONVENTION with GUESS in block'),
'451-T202':('c','H','replace_all edit put back (D8 fixed here)'),
'451-T217':('c','M','agent() without agentType passes'),
'451-T219':('c','H','form widened'),
'451-T220':('c','M','existing rows lack digest: re-judge'),
'451-T236':('c','M','STAGE= misses driver.rs'),
'451-T243':('c','H','read-back, gatherer search, wait scope, L4b one owner per task; partly GM amendment (l) replacing round-4 reading'),
'451-T240':('c','M','block review falls back to active task'),
'451-T237':('c','M','guard keyed on brief marker only'),
'451-T235':('c','H','negation/measure-name exemptions too wide'),
'451-T232':('c','H','hold must key on factual finding / the reply\'s own check'),
'451-T253':('a','H','sed q readers never counted'),
}
rows=[]
for k,v in m.items():
    cl=C.get(k,('?','-','item text not recoverable (stub ledger row only)'))
    rows.append((k,v['seq'],v['date'])+cl)
rows.sort()
with open('table.tsv','w') as f:
    f.write('task\trounds(C=CLEAR,B=BLOCKED)\tfirst_B_date\tclass\tconf\tbasis\n')
    for r in rows: f.write('\t'.join(r)+'\n')
cnt=collections.Counter(r[3] for r in rows); print(cnt)
print(collections.Counter((r[3],r[4]) for r in rows))
print([r[0] for r in rows if r[3]=='d'])
fb=collections.Counter(r[1][0] for r in rows); print('first round among ever-blocked',fb)
