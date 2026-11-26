# M16: could the fix have been built beside its reproduction? (feature 451, defect fixes built 2026-11-24..26)

Measured 2026-11-26 from the builders' transcripts (m16-timeline.py, m16-marks.py, m16-table.py, m16-net.py, m16-review.py, m16-carry.py, m16-digest.py).

Classes: A confirmed, B narrowed or widened, C wrong cause, D no defect. Basis, judged from the brief alone: proved = cause PROVED before the brief (an earlier builder's report, an arbiter's measurement, a probe); lead = brief held a LEAD or a guess ("probably", "likeliest", "find why"); symptom = brief held the symptom and the wanted behavior, no hidden cause claimed.

Minutes, mechanical from tool-call timestamps (one row a builder chain; a multi-task builder is one row): **pre-fix** = first tool call to first source edit (reading AND reproduction, interleaved); **red slice** = first test-file write to first source edit (the part only a reproduction costs, lower bound); **repro high** = pre-fix less the 4.6 min median a builder spends before any write (upper bound); **fix** = first source edit to the last code edit before the plan section; **rest** = after that to the report (plan section, decide, plan review rounds, closing checks, review-driven rework, Finish builders).

| task | class | basis (hand) | hedge in brief | total | pre-fix | red slice | repro high | fix (to plan section .. to last code edit) | rest | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| T207 | C | lead | yes: find its shared, inferred | 54.7 | 6.2 | 0.0 | 1.6 | 15.1 .. 21.2 | 33.4 | "the lock-wait lead was wrong, and the real cause was a child run of the test binary emptying the shared guard log mid-run" |
| T209+T212 | A | proved | no | 28.6 | 8.7 | 1.7 | 4.1 | 11.5 .. 14.8 | 8.4 | cause as the cascade table named it (change.rs echo never reads a new sentence; the three ABSENCE phrases); threshold SUBJECT_WORDS=3 set from the replay |
| T210+T211+T213 | A | proved | no | 36.2 | 11.3 | 1.7 | 6.7 | 18.5 .. 21.9 | 6.4 | "each with a test that fails on the old code and passes now"; fixes at the named functions (gather_section, gather_code, relabeled_only) |
| T214 | B | symptom | yes: find why | 23.1 | 7.5 | 0.5 | 2.9 | 6.1 .. 6.1 | 9.5 | brief named scoped.rs lines 80/112; found three reasons elsewhere (unit name misread, a stale review-tree snapshot, no kept copy) - fix asks `reviews owed` first |
| T215 | A | proved | no | 18.9 | 4.1 | 0.7 | 0 | 5.8 .. 5.8 | 9.0 | design change T210's builder had named; no reproduction needed |
| T217 | A | proved | no | 15.4 | 3.0 | 0.6 | 0 | 0.6 .. 0.6 | 11.8 | cause probed before the brief (Explore does not inherit); built as briefed |
| T223 | A | proved | no | 27.4 | 4.5 | 0.0 | 0 | 0.0 .. 21.0 | 22.9 | arbiter ruling + measurement file before the brief; built as ruled |
| T224 | A | proved | no | 11.3 | 4.2 | 0.0 | 0 | 1.5 .. 5.1 | 5.6 | arbiter ruling + cargo-tree result before the brief; built as ruled |
| T225 | B | proved | no | 23.0 | 4.3 | 0.0 | 0 | 14.6 .. 14.6 | 4.1 | built as ruled, plus a fourth case: "This goes beyond the ruling's words" |
| T226 | B | proved | no | 22.8 | 5.7 | 0.0 | 1.1 | 8.2 .. 14.1 | 8.9 | "The cause. There were two": the one T241 measured, and "P15's tag was invisible" (unbriefed) |
| T227 | B | symptom | no | 64.3 | 14.4 | 0.0 | 9.8 | 7.5 .. 30.4 | 42.4 | "There were two causes, one per case, and a third problem"; "this fix alone would still not have held the 0097 rounds" (filed on) |
| T228 | D | lead | no | 43.7 | 7.0 | 0.0 | 2.4 | 3.5 .. 24.7 | 33.2 | "The parser itself needed no change on HEAD" (926e10e593 had fixed it); only pin tests added |
| T230+T239 | C | lead | yes: find why, probabl | 10.5 | 1.8 | 0.8 | 0 | 0.0 .. 4.5 | 8.7 | brief: "probably the error lines' paths are not parsed"; report: "The error paths were being parsed correctly ... The fault was in theirs() ... awk's NR == FNR" on an empty list |
| T231 | C | lead | no | 48.7 | 2.5 | 0.0 | 0 | 0.0 .. 40.6 | 46.2 | "The task line's premise was wrong" - the rows had been written; four readers used three ownership rules |
| T232 | C | lead | yes: measure first, measured first | 67.0 | 19.2 | 0.0 | 14.6 | 7.8 .. 41.7 | 40.0 | no variance found: "both runs judged the same fingerprint ... but the scope differed" (the morning run judged one bullet) |
| T234 | A | symptom | no | 44.0 | 7.1 | 0.0 | 2.5 | 9.5 .. 19.2 | 27.4 | no hidden cause (a missing clause); thresholds measured over 52 pairs |
| T235 | B | symptom | no | 53.6 | 3.7 | 0.0 | 0 | 8.7 .. 47.6 | 41.2 | rule tuned on a 112-message corpus the builder built; the fix is the measurement's output |
| T238 | A | symptom | no | 4.6 | 0.7 | 0.0 | 0 | 1.2 .. 1.2 | 2.7 | two measures found where expected (raw bytes vs prose); one prose() serves both |
| T240 | B | lead | yes: (keyed by feature+task secti | 40.7 | 5.7 | 1.5 | 1.1 | 0.2 .. 20.2 | 34.8 | brief asked "why ... not counted (keyed by feature+task section? digest? not at all?)"; cause: a BLOCKED section verdict "left no row"; counted from verdicts, not dispatches |
| T241 | D | lead | yes: measure why | 12.2 | 0.9 | 0.0 | 0 | 7.4 .. 9.0 | 3.9 | "I didn't change the owing logic, because make record-owed did owe hamlet/marsh" - the listing was cut with tail -6 |
| T242 | C | lead | no | 41.5 | 9.2 | 0.0 | 4.6 | 4.5 .. 13.3 | 27.8 | brief: refuse when another writer is in the clone; report: "The real fault was that the landing's own git commit of the tick made nothing, and its exit code was never read" |
| T247 | C | lead | no | 27.0 | 7.6 | 2.9 | 3.0 | 0.0 .. 0.0 | 19.4 | "The workaround in the task's text (env -u RUSTFLAGS ...) would not have fixed it" - the flag travels in RUSTC_WORKSPACE_WRAPPER |
| T248 | A | symptom | no | 40.6 | 13.3 | 4.0 | 8.7 | 3.4 .. 12.3 | 23.9 | built as briefed (restart only where another session moved the subject) |
| T249 | A | proved | no | 31.5 | 7.5 | 2.6 | 2.9 | 2.1 .. 2.1 | 21.9 | T232's builder's leftovers, built as briefed |
| T252 | C | lead | yes: find the race, likely | 10.0 | 4.5 | 0.0 | 0 | 0.0 .. 0.0 | 5.5 | "a pipe race in the suite itself, not shared state on disk ... That rules out the brief's four candidates" |
| T253 | A | proved | no | 30.8 | 7.2 | 0.0 | 2.6 | 0.0 .. 5.9 | 23.6 | cause proved by T252; recount 158 lines in 32 files against the task line's 98 sites in 17 suites (the recount was the brief's job) |
| T254+T255 | A | symptom | no | 74.1 | 7.2 | 0.0 | 2.6 | 25.0 .. 25.5 | 41.9 | shared mark / shared numbering as the parallel trials saw them; built as briefed (review needed 2 rounds for the bundle's sources) |
| T256+T257 | A | symptom | no | 32.6 | 5.9 | 0.0 | 1.3 | -0.7 .. 6.8 | 27.4 | as briefed; route chosen a merge driver, not per-task files (a design choice the task line allowed) |
| T261 | D | lead | no | 13.3 | 5.0 | 0.0 | 0.4 | 8.1 .. 8.1 | 0.2 | "stopped before building. The fix as briefed would be a no-op" - withdrawn |
| T262 | A | proved | no | 28.6 | 10.2 | 4.8 | 5.6 | 0.0 .. 0.0 | 18.4 | T261's builder had measured it (7 of 12 replays owed nothing); built as briefed |
| T263 | C | lead | yes: find the race, likeliest | 42.9 | 5.8 | 0.0 | 1.2 | 8.7 .. 8.7 | 28.4 | "Cause: the fixture, not T258's state restore" (the brief's likeliest cause) |
| T267 | A | proved | no | 43.8 | 2.3 | 0.1 | 0 | 6.1 .. 37.4 | 35.4 | "Cause confirmed" - commands.rs:384 joins onto a .git that is a file |
| T268 | A | proved | no | 39.7 | 4.0 | 2.7 | 0 | 1.7 .. 27.9 | 34.0 | cause from T263's report (ask drops the spawn error); fix also covers the auto sync-in notice and, by the plan review, a silent failure |
| T269 | A | symptom | no | 49.8 | 3.4 | 0.0 | 0 | 12.8 .. 41.9 | 33.6 | detector built as briefed; red on T258's fixture |
| T270 | B | proved | no | 43.9 | 5.5 | 3.6 | 0.9 | 0.0 .. 0.0 | 38.4 | "make audit never classified anything itself before"; "Not the brief's ticked vs asked split: ... not derivable" |
| T271 | B | symptom | yes: measure first | 42.7 | 5.8 | 1.0 | 1.2 | 0.1 .. 14.5 | 36.8 | "Per-task bundle (make decide): no collision between two builders ... Left as is"; only the changed-blocks bundle collides |
| T272 | B | symptom | no | 41.8 | 9.7 | 5.3 | 5.1 | 0.4 .. 22.8 | 31.7 | case 1 "is not a status cell" (a listed content; no status-cell exemption built); case 2 "true positive, left firing" |
| T281 | B | symptom | yes: cause not proven | 31.2 | 9.5 | 0.0 | 4.9 | 13.5 .. 17.3 | 8.2 | task line: "cause not proven"; both effects reproduced; "Fix: more than a store keyed by tree, because the suite stamps stay shared" |
| T292 | B | symptom | no | 35.4 | 5.1 | 0.0 | 0.5 | 6.9 .. 25.8 | 23.4 | refusals as briefed; "Why T270 got through: a dirty clone is sent to land-alone.sh before any first-pass refusal" - "Deviation from the brief: the refusal comes first and apart" |
| T295 | B | symptom | yes: if it does not reproduce, measured first | 60.3 | 3.7 | 0.3 | 0 | 10.4 .. 42.7 | 46.2 | "Job 1, the spelling - reproduced, and wider than briefed" (make detector, eight guards through one reader) |
| T303 | A | proved | yes: cause not isolated | 9.5 | 4.9 | 0.0 | 0.3 | 0.8 .. 1.1 | 3.8 | "Cause, as proved: the builder's diagnosis was right" (feature read from another feature's start row) |
| T305 | B | symptom | no | 17.8 | 5.7 | 0.2 | 1.1 | 3.1 .. 10.7 | 9.0 | cause found by replay: "Every rung of left/whose.rs failed"; fix a new pool rung plus the write side - neither in the brief |

Not in the sample: T309 (built 17:38Z, not landed at measurement; class C on a lead - "the red ... comes from the clock, not the live transcripts"), T104/T304/T159 (still running), the mechanisms and records (T216, T218-T222, T229, T233, T236, T237, T243-T246, T250, T251, T258, T259, T265, T284, T285, T289).

Known noise: edits are mostly made through shell heredocs and python patches; the write detector reads their target paths by pattern, so a phase boundary can be off by a minute or two and "fix" reads 0.0 where the detector missed the later edits. Phases interleave (tests written after the first source edit in 33 of 42 rows).

## Basis, re-derived by a fixed rule from the brief and task line alone (m16-basis.py)

The hand "basis" column was filled after the reports were read, so it carries hindsight. The mechanical rule: a HEDGE word in the brief or task line ("probably", "likeliest", "inferred", "the lead", "find why", "find the race", "measure why/first", "cause not proven/isolated", "if it does not reproduce"); T261's "premise" is the withdrawn line's later wording and is not counted.

- hedged, 12 rows: A 1 (T303), B 5, C 5, D 1.
- stated as fact, 30 rows: A 17, B 8, C 3 (T231, T242, T247), D 2 (T228, T261).

## Hand check of four rows against their write and test events

- T262 (A): test written +5.4 min, red run 03:49:54-03:51:16 (1.4 min), fix and hook suite done +9.5, plan section +10.9, report +28.6. Reproduction about 2 min, fix about 2, rest about 19. The mechanical row put the fix at 0.0 (it missed the later source writes).
- T248 (A): test written +9.3 min, red run 22:53:39-22:55:37 (2.0 min), then the fix.
- T267 (A): test written +2.2 min and the fix 11 s later, BEFORE the red run (07:09:00-07:12:04, 3.1 min): the builder already wrote the fix beside its reproduction, in one tree.
- T223 (A): no reproduction at all (source first at +4.5 min, tests at +11); the arbiter's measurement was the proof.
- So on confirmed rows the reproduction is one compile-and-test run of 1.4 to 3.1 min plus the minute or two of writing the test.

## Net of a split (m16-net.py)

- ALL 42: builder-min 1439 | wall saved low 4.2 (red slice, merge 3) mid 15.2 (red slice, merge 1) high 37.6 (all pre-fix past 4.6 min reading, merge 1) = 0.3%..2.6% | second builders cost 483 builder-min, of which wasted 201
- PROVED-EARLIER 15: builder-min 411 | wall saved low 2.1 (red slice, merge 3) mid 9.8 (red slice, merge 1) high 17.0 (all pre-fix past 4.6 min reading, merge 1) = 0.5%..4.1% | second builders cost 156 builder-min, of which wasted 16
- LEAD-ONLY 12: builder-min 412 | wall saved low 0.0 (red slice, merge 3) mid 0.2 (red slice, merge 1) high 0.1 (all pre-fix past 4.6 min reading, merge 1) = 0.0%..0.0% | second builders cost 146 builder-min, of which wasted 140
- SYMPTOM 15: builder-min 615 | wall saved low 2.1 (red slice, merge 3) mid 5.2 (red slice, merge 1) high 20.6 (all pre-fix past 4.6 min reading, merge 1) = 0.3%..3.3% | second builders cost 177 builder-min, of which wasted 53
- Counter({'A': 18, 'B': 13, 'C': 8, 'D': 3})
- rows where red_slice>=3: [('T248', 'A', 4.0), ('T262', 'A', 4.8), ('T270', 'B', 3.6), ('T272', 'B', 5.3)]
- rows where repro_hi>=4: [('T209+T212', 'A', 4.1), ('T210+T211+T213', 'A', 6.7), ('T227', 'B', 9.8), ('T232', 'C', 14.6), ('T242', 'C', 4.6), ('T248', 'A', 8.7), ('T262', 'A', 5.6), ('T272', 'B', 5.1), ('T281', 'B', 4.9)]

Model: serial wall = pre-fix + fix + rest; split wall = max(pre-fix, reading + fix) + merge + rest, so the saving is at most the reproduction-only minutes less the merge. A rows count whole, B rows half. Second builder = 4.6 min of reading (the median to a first write over 62 primary builders) plus the sample's median fix; it is thrown away whole on C and D, half on B. Merge: 1 to 3 min (an assumption; a carry command is 2.5 s at the median over 76 carry and cherry-pick commands of 11-25/26, and the word "conflict" appears in the output of 16 of them - one tree into the clone, never two builders' edits to one file).

## Plan review waits (m16-review.py)

- before 17:00Z 11-26 : rounds 117 builders 69 | median dur 2.74 | sum dur 318 | rounds with 0 work calls inside 16 | median tail idle 0.48 sum tail idle 146 | checks still pending at verdict 86 | tail idle where checks NOT pending 31 in 31 rounds
- per builder tail idle median 0.9 max 9.7  rounds per builder median 2
- after : rounds 5 builders 4 | median dur 3.08 | sum dur 15 | rounds with 0 work calls inside 1 | median tail idle 1.69 sum tail idle 8 | checks still pending at verdict 0 | tail idle where checks NOT pending 8 in 5 rounds
- per builder tail idle median 1.8 max 4.93  rounds per builder median 1.0
- CORRECTED before 17:00Z: rounds 117 | a background check run still out at the verdict in 35 | the rest: 82 rounds, tail idle 95 min
- builders with code edits after their first review dispatch: 44 of 73 | mean rounds 1.7 vs 1.62 for those with none
- builders with 2+ rounds: 36 of 73 ; 3+: 9
- "tail idle" = minutes from the builder's last tool call (advisor calls counted as work) to the verdict's notification; it includes the model's own thinking.
- `make decide` (rust/gate/crates/plan/src/plan.rs `decide`) needs: one specs directory; a plan.md section whose heading names the task (every member of a bundle sharing it); the lint clean (GM quotes, labeled figures and counts, a differential's verify report, the red exit, the deferral form, a class fix's method line); the Approach block with every part A item answered. It needs no code, no diff and no check run (the closing-checks order is a notice, static_runs_hooks/order.rs). The verdict is recorded against the section's digest (record.rs line 175), so any later edit of the section owes another round.
