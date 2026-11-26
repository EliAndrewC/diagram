# m15 - task overlap by file class (pinned 248d6f919f, since 2026-11-19, features 449 and 451)

Units (surviving ticks): 183 (127 of 451, 56 of 449); 72 multi-task ticks; 7 ticks dropped as reverted.
Method error: 9 units have NO commit named for them (delta = bookkeeping only, their code went in under another subject); 18 task-named commits name no landed unit.
Units with no named commit: 449 T156 T214, 449 T157 T215 T217, 451 T1, 451 T2, 449 T237, 451 T26, 451 T25 T27, 451 T4, 451 T5

## 1. Class table (units touching each class)
| class | units | % | files touched (distinct) |
|---|---|---|---|
| BOOK | 183 | 100% | 698 |
| REG | 131 | 72% | 77 |
| RUST | 164 | 90% | 1051 |
| TESTS | 77 | 42% | 71 |
| RESEARCH | 17 | 9% | 475 |
| OTHER | 101 | 55% | 540 |
| only BOOK (no other class) | 11 | 6% | |

Top 15 non-bookkeeping files (units touching):
- 50  Makefile  [REG]
- 50  docs/guards.md  [REG]
- 43  docs/make-targets.html  [REG]
- 41  dev/claims-index.json  [REG]
- 34  rust/gate/CLAUDE.md  [REG]
- 22  rust/guard/CLAUDE.md  [REG]
- 18  dev/claims-pages.json  [REG]
- 17  dev/claims-triage-skips.jsonl  [OTHER]
- 15  specs/451-time-retro-and-efficiency/request.md  [OTHER]
- 14  docs/buildings.md  [OTHER]
- 14  rust/gate/crates/reviews/src/reviews/owed.rs  [RUST]
- 13  tests/hooks/test-make-only-hooks.sh  [TESTS]
- 13  docs/building-programs.md  [OTHER]
- 13  CLAUDE.md  [REG]
- 13  rust/phases/src/driver/polder.rs  [RUST]

Top 10 Rust crates (units touching):
- 66  rust/guard/src
- 50  rust/guard/shared
- 29  rust/gate/crates/measure
- 27  rust/gate/crates/reviews
- 23  rust/gate/crates/land
- 22  rust/mode_a
- 21  rust/gate/crates/plan
- 21  rust/phases
- 18  rust/gate/crates/owed
- 15  rust/gate/crates/claims
Top 10 Rust source files:
- 14  rust/gate/crates/reviews/src/reviews/owed.rs
- 13  rust/phases/src/driver/polder.rs
- 13  rust/guard/shared/src/guards/set_down_hooks.rs
- 11  rust/guard/src/guards/make_only_hooks/tests.rs
- 11  rust/guard/src/guards/make_only_hooks.rs
- 11  rust/guard/src/guards/event_log_hooks.rs
- 11  rust/guard/shared/src/guards/set_down_hooks/tests.rs
- 10  rust/gate/crates/reviews/src/reviews/prereq.rs
- 10  rust/gate/crates/land/src/land/tests.rs
- 10  rust/gate/crates/land/src/land.rs

## 2. Pairwise overlap

### All pairs landed within 24 h of each other (4378 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 609 | 13.9% |
| rust-same-crate-other-file | 934 | 21.3% |
| registry | 357 | 8.2% |
| other-shared(tests/research/other) | 43 | 1.0% |
| bookkeeping-only | 2040 | 46.6% |
| none | 395 | 9.0% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 3929 (89.7%); Makefile 332 (7.6%); OTHER 266 (6.1%); REG 1070 (24.4%); REG hand-edited (generated left out) 865 (19.8%); RESEARCH 35 (0.8%); RUST 609 (13.9%); TESTS 159 (3.6%); same crate (any file) 1543 (35.2%)

### ...of which both units have a non-bookkeeping file (real work on both sides) (3816 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 609 | 16.0% |
| rust-same-crate-other-file | 934 | 24.5% |
| registry | 357 | 9.4% |
| other-shared(tests/research/other) | 43 | 1.1% |
| bookkeeping-only | 1734 | 45.4% |
| none | 139 | 3.6% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 3623 (94.9%); Makefile 332 (8.7%); OTHER 266 (7.0%); REG 1070 (28.0%); REG hand-edited (generated left out) 865 (22.7%); RESEARCH 35 (0.9%); RUST 609 (16.0%); TESTS 159 (4.2%); same crate (any file) 1543 (40.4%)

### Pairs landed within 2 h of each other (435 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 80 | 18.4% |
| rust-same-crate-other-file | 81 | 18.6% |
| registry | 24 | 5.5% |
| other-shared(tests/research/other) | 6 | 1.4% |
| bookkeeping-only | 217 | 49.9% |
| none | 27 | 6.2% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 406 (93.3%); Makefile 36 (8.3%); OTHER 40 (9.2%); REG 105 (24.1%); REG hand-edited (generated left out) 84 (19.3%); RESEARCH 3 (0.7%); RUST 80 (18.4%); TESTS 31 (7.1%); same crate (any file) 161 (37.0%)

### Pairs of SINGLE-task units within 24 h (a batch tick of several tasks inflates every overlap) (1748 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 207 | 11.8% |
| rust-same-crate-other-file | 257 | 14.7% |
| registry | 167 | 9.6% |
| other-shared(tests/research/other) | 23 | 1.3% |
| bookkeeping-only | 891 | 51.0% |
| none | 203 | 11.6% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 1536 (87.9%); Makefile 144 (8.2%); OTHER 131 (7.5%); REG 409 (23.4%); REG hand-edited (generated left out) 325 (18.6%); RESEARCH 1 (0.1%); RUST 207 (11.8%); TESTS 79 (4.5%); same crate (any file) 464 (26.5%)

Units with a start mark before landing: 166 of 183; distinct trees among them: {'': 154, 'diagram-backlog': 1, 'diagram-backlog-t417': 1, 'diagram-backlog-t261': 1, 'diagram-backlog-t262': 1, 'diagram-backlog-t263': 1, 'diagram-backlog-t251': 1, 'diagram-backlog-t267': 1, 'diagram-backlog-t265': 1, 'diagram-backlog-t272': 1, 'diagram-backlog-t268': 1, 'diagram-backlog-t271': 1, 'diagram-backlog-t269': 1}
Units with a commit carried over from a worktree (author time != commit time): 12

### Pairs IN FLIGHT TOGETHER (each: last start mark before its first named commit, to its landing; the intervals overlap). An upper bound on side-by-side work: a started task may sit idle (86 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 4 | 4.7% |
| rust-same-crate-other-file | 27 | 31.4% |
| registry | 1 | 1.2% |
| other-shared(tests/research/other) | 0 | 0.0% |
| bookkeeping-only | 42 | 48.8% |
| none | 12 | 14.0% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 58 (67.4%); Makefile 4 (4.7%); OTHER 2 (2.3%); REG 9 (10.5%); REG hand-edited (generated left out) 8 (9.3%); RESEARCH 1 (1.2%); RUST 4 (4.7%); TESTS 1 (1.2%); same crate (any file) 31 (36.0%)

### ...of which landed in different ticks AND at least one was carried over from a worktree (4 pairs)
| exclusive tier (highest that applies) | pairs | % |
|---|---|---|
| rust-same-file | 0 | 0.0% |
| rust-same-crate-other-file | 0 | 0.0% |
| registry | 0 | 0.0% |
| other-shared(tests/research/other) | 0 | 0.0% |
| bookkeeping-only | 3 | 75.0% |
| none | 1 | 25.0% |
Non-exclusive (pairs sharing >=1 file of the class): BOOK 3 (75.0%)
- both carried: 451 T263 || 451 T251: bookkeeping-only; shared non-bookkeeping: none

## 2b. Registry edits: consecutive touches of one registry file by two different units landed within 24 h
(no other commit touched the file between; SAME = hunks overlap or abut, git would conflict; NEAR = within 3 lines, merges but inside each other's context; DISTINCT = clean merge)
| file | consecutive pairs | SAME | NEAR | DISTINCT | SAME at end of file |
|---|---|---|---|---|---|
| docs/guards.md | 48 | 10 | 2 | 36 | 0 |
| Makefile | 44 | 9 | 1 | 34 | 0 |
| docs/make-targets.html | 38 | 11 | 1 | 26 | 0 |
| rust/gate/CLAUDE.md | 30 | 11 | 1 | 18 | 0 |
| dev/claims-index.json | 28 | 19 | 0 | 9 | 0 |
| rust/guard/CLAUDE.md | 20 | 18 | 2 | 0 | 0 |
| dev/claims-pages.json | 13 | 1 | 0 | 12 | 0 |
| CLAUDE.md | 9 | 3 | 0 | 6 | 0 |
| dev/guard-messages.tsv | 9 | 4 | 2 | 3 | 0 |
| l7r/diagram/CLAUDE.md | 5 | 2 | 2 | 1 | 0 |
| l7r/diagram/pipeline/CLAUDE.md | 5 | 1 | 1 | 3 | 0 |
| rust/guard/src/lib.rs | 5 | 2 | 0 | 3 | 0 |
| l7r/diagram/tools/CLAUDE.md | 4 | 1 | 2 | 1 | 0 |
| rust/guard/src/guards.rs | 4 | 2 | 0 | 2 | 0 |
| dev/audits/* | 3 | 3 | 0 | 0 | 2 |
| ALL registry files | 283 | 107 | 15 | 161 | 5 |
Hand-edited only (generated make-targets.html, claims-index.json, claims-pages.json left out): 204 pairs - SAME 76, NEAR 14, DISTINCT 114
Of the 76 SAME: 54 the later unit REWROTE lines the earlier one had just written (the same PHYSICAL line - see 2c: mostly 400-900 character table rows and help lines, so two separate clauses meet on one line; and this is serial history, the later task saw the earlier one's text, so some are follow-ups that would not exist side by side); 22 only inserted beside them (adjacent rows, mechanical).

Sample of 15 (seed 15, hand-edited files, at most 3 a file):
- CLAUDE.md: 451 T84 T85 T86 then 451 T82 T95 T97 T101 - DISTINCT (nearest hunks 36 lines apart; 1 and 1 hunks)
- rust/gate/CLAUDE.md: 449 T238 then 449 T242 - DISTINCT (nearest hunks 6 lines apart; 1 and 1 hunks)
- dev/audits/tooling-state.md: 451 T258 T261 then 451 T269 - SAME (nearest hunks 0 lines apart; 1 and 2 hunks) [rewrote the same lines] [both at end of file]
- dev/guard-messages.tsv: 451 T244 then 451 T235 - DISTINCT (nearest hunks 14 lines apart; 4 and 2 hunks)
- l7r/diagram/CLAUDE.md: 449 T221 then 449 T222 - SAME (nearest hunks 0 lines apart; 3 and 5 hunks) [rewrote the same lines]
- rust/gate/CLAUDE.md: 451 T187 T191 then 451 T195 T197 T198 T199 T200 T204 - SAME (nearest hunks 1 lines apart; 1 and 5 hunks)
- l7r/diagram/pipeline/CLAUDE.md: 449 T223 then 449 T220 - DISTINCT (nearest hunks 8 lines apart; 1 and 2 hunks)
- Makefile: 451 T154 T155 T160 T161 T164 then 451 T168 T169 - DISTINCT (nearest hunks 328 lines apart; 3 and 1 hunks)
- dev/audits/plan-gate-escape.md: 451 T262 then 451 T270 - SAME (nearest hunks 0 lines apart; 1 and 1 hunks) [rewrote the same lines] [both at end of file]
- CLAUDE.md: 451 T58 then 451 T84 T85 T86 - DISTINCT (nearest hunks 104 lines apart; 1 and 1 hunks)
- docs/guards.md: 451 T15 T18 T24 T28 T29 T30 then 451 T14 T16 - SAME (nearest hunks 0 lines apart; 1 and 1 hunks) [rewrote the same lines]
- Makefile: 451 T168 T169 then 449 T377 - DISTINCT (nearest hunks 481 lines apart; 1 and 1 hunks)
- Makefile: 451 T15 T18 T24 T28 T29 T30 then 451 T12 T17 - SAME (nearest hunks 0 lines apart; 3 and 3 hunks) [rewrote the same lines]
- rust/gate/crates/pool/Cargo.toml: 449 T220 then 449 T221 - SAME (nearest hunks 0 lines apart; 1 and 3 hunks) [rewrote the same lines]
- rust/gate/CLAUDE.md: 449 T230 then 449 T231 - SAME (nearest hunks 0 lines apart; 2 and 1 hunks) [rewrote the same lines]

## 4. Same crate, different file: shared module-list lines
Units that added a `mod` line: 84; files receiving mod lines from >=2 units: 36
Same-24h pairs both adding a `mod` line to the SAME file: 62 (of 4378 pairs in the window)
- 6  rust/gate/crates/checks/src/checks/documents.rs
- 6  rust/guard/shared/src/tree/tests.rs
- 6  rust/guard/shared/src/tree.rs
- 3  rust/gate/crates/checks/src/checks.rs
- 3  rust/guard/shared/src/lib.rs
- 3  rust/phases/src/driver/polder.rs
- 3  rust/gate/crates/reviews/src/reviews/prereq/scoped.rs
- 3  rust/gate/crates/land/src/land/alone/tests.rs
Of the 934 same-crate-different-file pairs: 376 also share a hand-edited registry file, 37 share a tests/ file.

Note on section 4: a pair where both added a `mod` line to one file is by construction a same-FILE pair (it sits in the
rust-same-file tier). 62 of 4378 pairs (1.4%); 609 pairs share a Rust file in all.

## 2c. Line shape of the registry files (why textually separate edits collide)
docs/guards.md 255 lines, mean 662 chars a line; rust/gate/CLAUDE.md 45 lines, mean 885; rust/guard/CLAUDE.md 19 lines, mean 724;
docs/session-clones.md 96 lines, mean 430; Makefile 1209 lines, mean 123 (34 lines over 400). Lines a commit removed that the
previous commit to the file had just added (all commits since 2026-11-19): guards.md 12 (11 table rows), rust/guard/CLAUDE.md 15
(all one table row, the guards list), rust/gate/CLAUDE.md 14 (all table rows), Makefile 29 (12 help lines, 4 .PHONY/list lines, 13 short).

## 3a. Commits carried over from a worktree onto main (m15-carry.py; author time != commit time; 24 commits, about 12 tasks, 2026-11-25/26)
Files main changed between the task's start mark and the carry-over (other tasks' commits only), by class:
carried commits: 24
  10 BOOK changed underneath, hunks MEET
  14 BOOK changed underneath, hunks apart
  15 BOOK untouched underneath
   1 OTHER changed underneath, hunks MEET
   7 OTHER changed underneath, hunks apart
  15 OTHER untouched underneath
   3 REG changed underneath, hunks apart
  20 REG untouched underneath
 205 RESEARCH untouched underneath
  77 RUST untouched underneath
   1 TESTS changed underneath, hunks apart
   1 TESTS untouched underneath
(hunks MEET/apart is judged against the LAST other commit to the file only - a lower bound on conflicts.)
The 3 registry files changed underneath: Makefile twice (T246, T233), docs/make-targets.html once (T246); hunks apart each time.
Per-commit rows: m15-carry.txt. The builder's base commit survives for 2 of 24, so the start mark stands in for it.

## 3b. What an overlap cost, as recorded
"held by" refusals (land logs under ~/.claude/jobs/c6fd72d1/tmp and the session transcript; the event logs hold exit codes only, no text):
| when (UTC) | landing | held by | cause | minutes |
|---|---|---|---|---|
| 11-19 19:14 | 449 T156,T214 | T156 | task list typed with a comma - not an overlap | <1 |
| 11-21 18:32 | 451 T81 T88 T93 | T97 | the one started-task mark (before T101) - not files | <1 to relaunch (mark moved by hand) |
| 11-22 02:01 | 451 T83 T87 | T89 | after T101; with a plan finding; files not named in the record | 1 |
| 11-22 07:13 | 449 T244 | T240 | the MAKEFILE in both deltas - a real shared-registry hold; T150 filed | <1 (Makefile taken out of the delta) |
| 11-22 ~14:00 | 449 batch (T274) | T275 | another session moved the mark mid-landing; 40 files held T158's edits | not recorded (handoff file) |
| 11-24 16:50 | 449 T424 | T418 | several builders in ONE clone: the delta held T418's uncommitted files | 19 (landed together 17:09) |
| 11-26 15:12 | 451 T292 | T285 | six shared files (Makefile, guards.md, make-targets.html, session-clones.md, gate CLAUDE.md, builder-brief.md) | open when measured (16+) |
7 refusals; 2 are two tasks needing the same registry file (T244/T240, T292/T285); none names a Rust source file.
Reverted ticks on main: 7 (make land undoes its tick when the push fails). Three read from the transcript:
- T227 (11-25): the push refused because another builder's start mark named T232 - a mark, not a file.
- T218-T225 (11-24 19:22Z): the push met a MERGE CONFLICT with main in l7r/diagram/interactive/assets/glossary.json, an assembled
  file another SESSION (the research clone) had also rebuilt; resolved by rebuilding it, about 1 minute, then a second landing.
- T272 (11-26 13:19Z): the push refused for a ledger row another builder's (T268's) review pass owed; 64 s to the re-tick.
The four of 2026-11-20 not read; builders first ran side by side on 11-21 (T88), so they predate parallel work.
"minutes" in the table = refusal to the relaunch of the landing, not the length of the hold.
Conflicts recorded in commit messages: c20118a7f2 (tasks.md lines the carry-over doubled, one repair commit); 83f65718d7 (T270's
code left out of its landing; 79 s on main between tick and code; T292 filed); built in answer: T105 (take-back merges spec files
piece by piece), T256+T257 (plan-review.json merge driver), T292 (make carry). Conflicts printed in the transcript since 11-25
(55 cherry-pick commands): plan-review.json 2, tasks.md 2, glossary.json 1 - the transcript mostly did not print them.

## 2d. CO-ACTIVE pairs, from the event log (m15-check.py) - the nearest record of what really ran side by side
A unit's builder activity = ten-minute buckets in which a subagent (`by`) ran a tool under its task; 152 of 183 units have some.
Checked against the transcript's named co-running builders: 451 T118/T129 share 7 buckets, T118/T89 11, 449 T158/T240 4.
| tier | pairs sharing >=3 buckets (85) | single-task units only (36) | pairs sharing >=1 bucket (196) |
|---|---|---|---|
| rust-same-file | 10 (11.8%) | 1 (3%) | 36 (18.4%) |
| rust-same-crate-other-file | 21 (24.7%) | 7 (19%) | 52 (26.5%) |
| registry, hand-edited | 2 (2.4%) | 2 (6%) | 7 (3.6%) |
| registry, generated only | 2 (2.4%) | 0 | 5 (2.6%) |
| other shared | 1 (1.2%) | 1 (3%) | 3 (1.5%) |
| bookkeeping-only | 40 (47.1%) | 23 (64%) | 79 (40.3%) |
| none | 9 (10.6%) | 2 (6%) | 14 (7.1%) |
The Makefile is shared by 5 of the 85 (5.9%). Rust same-file cases include 451 T129 || T89 (tree.rs) and T58 (the crate split, which
moved files under everyone). The start-mark version of this row in section 2 (86 pairs, 4 rust-same-file) is the weaker proxy.

## 3c. Rust exposure under the carried commits
10 carried commits held Rust (77 files). 21 Rust-editing commits of other tasks landed on main inside their windows; the same crate
twice (T254+T255: plan, guard/shared); the same file never. Exposure existed but is small: no conflict in 10, not "no conflict".

## Method notes
A unit is a tick; 72 of 183 are multi-task ticks, which inflates every overlap - read the single-task table beside the full one.
REG is wider than the brief's list: every CLAUDE.md, dev/claims-index.json and claims-pages.json (generated), Cargo.toml/lock.
451 T292 and T285 (the prompting case) are not on the pinned commit. One `git fetch origin` was run in the clone at the start
(it moved origin/main's remote ref only); nothing else was written there.
