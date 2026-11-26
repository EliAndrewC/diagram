import json,os
S=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(S+'/m16-table.json')); R={r['task']:r for r in d['rows']}
EV={
'T207':'"the lock-wait lead was wrong, and the real cause was a child run of the test binary emptying the shared guard log mid-run"',
'T209+T212':'cause as the cascade table named it (change.rs echo never reads a new sentence; the three ABSENCE phrases); threshold SUBJECT_WORDS=3 set from the replay',
'T210+T211+T213':'"each with a test that fails on the old code and passes now"; fixes at the named functions (gather_section, gather_code, relabeled_only)',
'T214':'brief named scoped.rs lines 80/112; found three reasons elsewhere (unit name misread, a stale review-tree snapshot, no kept copy) - fix asks `reviews owed` first',
'T215':'design change T210\'s builder had named; no reproduction needed',
'T217':'cause probed before the brief (Explore does not inherit); built as briefed',
'T223':'arbiter ruling + measurement file before the brief; built as ruled',
'T224':'arbiter ruling + cargo-tree result before the brief; built as ruled',
'T225':'built as ruled, plus a fourth case: "This goes beyond the ruling\'s words"',
'T226':'"The cause. There were two": the one T241 measured, and "P15\'s tag was invisible" (unbriefed)',
'T227':'"There were two causes, one per case, and a third problem"; "this fix alone would still not have held the 0097 rounds" (filed on)',
'T228':'"The parser itself needed no change on HEAD" (926e10e593 had fixed it); only pin tests added',
'T230+T239':'brief: "probably the error lines\' paths are not parsed"; report: "The error paths were being parsed correctly ... The fault was in theirs() ... awk\'s NR == FNR" on an empty list',
'T231':'"The task line\'s premise was wrong" - the rows had been written; four readers used three ownership rules',
'T232':'no variance found: "both runs judged the same fingerprint ... but the scope differed" (the morning run judged one bullet)',
'T234':'no hidden cause (a missing clause); thresholds measured over 52 pairs',
'T235':'rule tuned on a 112-message corpus the builder built; the fix is the measurement\'s output',
'T238':'two measures found where expected (raw bytes vs prose); one prose() serves both',
'T240':'brief asked "why ... not counted (keyed by feature+task section? digest? not at all?)"; cause: a BLOCKED section verdict "left no row"; counted from verdicts, not dispatches',
'T241':'"I didn\'t change the owing logic, because make record-owed did owe hamlet/marsh" - the listing was cut with tail -6',
'T242':'brief: refuse when another writer is in the clone; report: "The real fault was that the landing\'s own git commit of the tick made nothing, and its exit code was never read"',
'T247':'"The workaround in the task\'s text (env -u RUSTFLAGS ...) would not have fixed it" - the flag travels in RUSTC_WORKSPACE_WRAPPER',
'T248':'built as briefed (restart only where another session moved the subject)',
'T249':'T232\'s builder\'s leftovers, built as briefed',
'T252':'"a pipe race in the suite itself, not shared state on disk ... That rules out the brief\'s four candidates"',
'T253':'cause proved by T252; recount 158 lines in 32 files against the task line\'s 98 sites in 17 suites (the recount was the brief\'s job)',
'T254+T255':'shared mark / shared numbering as the parallel trials saw them; built as briefed (review needed 2 rounds for the bundle\'s sources)',
'T256+T257':'as briefed; route chosen a merge driver, not per-task files (a design choice the task line allowed)',
'T261':'"stopped before building. The fix as briefed would be a no-op" - withdrawn',
'T262':'T261\'s builder had measured it (7 of 12 replays owed nothing); built as briefed',
'T263':'"Cause: the fixture, not T258\'s state restore" (the brief\'s likeliest cause)',
'T267':'"Cause confirmed" - commands.rs:384 joins onto a .git that is a file',
'T268':'cause from T263\'s report (ask drops the spawn error); fix also covers the auto sync-in notice and, by the plan review, a silent failure',
'T269':'detector built as briefed; red on T258\'s fixture',
'T270':'"make audit never classified anything itself before"; "Not the brief\'s ticked vs asked split: ... not derivable"',
'T271':'"Per-task bundle (make decide): no collision between two builders ... Left as is"; only the changed-blocks bundle collides',
'T272':'case 1 "is not a status cell" (a listed content; no status-cell exemption built); case 2 "true positive, left firing"',
'T281':'task line: "cause not proven"; both effects reproduced; "Fix: more than a store keyed by tree, because the suite stamps stay shared"',
'T292':'refusals as briefed; "Why T270 got through: a dirty clone is sent to land-alone.sh before any first-pass refusal" - "Deviation from the brief: the refusal comes first and apart"',
'T295':'"Job 1, the spelling - reproduced, and wider than briefed" (make detector, eight guards through one reader)',
'T303':'"Cause, as proved: the builder\'s diagnosis was right" (feature read from another feature\'s start row)',
'T305':'cause found by replay: "Every rung of left/whose.rs failed"; fix a new pool rung plus the write side - neither in the brief',
}
BAS={'proved':'cause PROVED before the brief (an earlier builder\'s report, an arbiter\'s measurement, a probe)','lead':'brief held a LEAD or a guess ("probably", "likeliest", "find why")','symptom':'brief held the symptom and the wanted behavior, no hidden cause claimed'}
B=json.load(open(S+'/m16-basis.json')); HB={t:('yes: '+', '.join(v['h'][:2]) if (v['h'] and t!='T261') else 'no') for t,v in B.items()}
L=['# M16: could the fix have been built beside its reproduction? (feature 451, defect fixes built 2026-11-24..26)','',
'Measured 2026-11-26 from the builders\' transcripts (m16-timeline.py, m16-marks.py, m16-table.py, m16-net.py, m16-review.py, m16-carry.py, m16-digest.py).','',
'Classes: A confirmed, B narrowed or widened, C wrong cause, D no defect. Basis, judged from the brief alone: '+'; '.join('%s = %s'%(k,v) for k,v in BAS.items())+'.','',
'Minutes, mechanical from tool-call timestamps (one row a builder chain; a multi-task builder is one row): **pre-fix** = first tool call to first source edit (reading AND reproduction, interleaved); **red slice** = first test-file write to first source edit (the part only a reproduction costs, lower bound); **repro high** = pre-fix less the 4.6 min median a builder spends before any write (upper bound); **fix** = first source edit to the last code edit before the plan section; **rest** = after that to the report (plan section, decide, plan review rounds, closing checks, review-driven rework, Finish builders).','',
'| task | class | basis (hand) | hedge in brief | total | pre-fix | red slice | repro high | fix (to plan section .. to last code edit) | rest | evidence |','|---|---|---|---|---|---|---|---|---|---|---|']
for t,r in R.items():
    L.append('| %s | %s | %s | %s | %.1f | %s | %s | %s | %s .. %s | %s | %s |'%(t,r['cls'],r['basis'],HB[t],r['total'],r['prefix'],r['red_slice'],r['repro_hi'],r['fix'],r['fix_hi'],r['rest'],EV[t]))
L+=['','Not in the sample: T309 (built 17:38Z, not landed at measurement; class C on a lead - "the red ... comes from the clock, not the live transcripts"), T104/T304/T159 (still running), the mechanisms and records (T216, T218-T222, T229, T233, T236, T237, T243-T246, T250, T251, T258, T259, T265, T284, T285, T289).','',
'Known noise: edits are mostly made through shell heredocs and python patches; the write detector reads their target paths by pattern, so a phase boundary can be off by a minute or two and "fix" reads 0.0 where the detector missed the later edits. Phases interleave (tests written after the first source edit in 33 of 42 rows).']
open(S+'/m16-results.md','w').write('\n'.join(L)+'\n')
print(len(R), sum(1 for r in R.values() if r['interleaved']>0))
