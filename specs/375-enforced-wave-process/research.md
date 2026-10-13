# Feature 375 - research

Load this file when: checking where amendment 3's figures came from.

## R1 - the record tooling's cost on a real delta (amendment 3, FR-020)

`m:375-a3-record-tooling-before`. On 374's pushed HEAD 61a52f3c8 (a detached worktree, its answer store copied), each of
`record-owed`, `check-bundle`, `modal-bundle` and `claims-owed` took 6.0 to 6.9 s of wall time. The first three spend most of
it in `record_owed.units`: the whole record parsed at the merge base and at the working tree (0.92 s and 0.8 s), the pop-ups
read at the base by one `git show` each (299 processes, 1.25 s for the stage), the entry-drift classes likewise (177, 0.76 s).
`claims-owed` re-parses every engine module for its claims: its `all_units` stage took 7.29 s timed in-process, in a separate run
while the guard suites were being timed beside it, which is why it exceeds the command's whole 6.9 s run earlier. `check-bundle`'s quote pass (`quote-verbatim`) took 0.3 s with
the page cache warm; its 20.7 s first run was the cache filling. In 374's transcript the record and claims tooling took
59 min over 209 calls.

## R2 - why pop-ups reach the round cap (amendment 3, FR-019)

`m:375-a3-popup-rounds-before`. From the kept dispatch records and replies of the diagram-backlog clone (374) and the
diagram-research clone: 2.09 and 2.06 dispatches per checked (pop-up, check) unit, 29 of 34 and 70 of 82 units with a second
round. Every second and later round's recorded reason was the pop-up's own words having changed - the last round's applied
edits. A check's OWN applied edits already settle its units (feature 335, `apply_edits.settle_round`); the others' do not.
`modal-form` proposed edits in 12 of 12 kept second-round replies in the research clone (2 of 5 in 374's), each re-owing the
substance checks. One case argues against running form last: 374's residence-corridor round 2, where `modal-research` caught a
comparison that modal-form's rewording had introduced.

The context put to the GM said "about 20 of 374's units" reached the round cap: that was 374's 20 `accept` rulings over all
its tripwires (building reviews, claims checks and pop-ups together). The pop-up units alone: 4 with a third dispatch in
374's kept records, and 5 ruled in wave 120's one batch; 352's 21 triggers are pop-up units.

## R3 - what `hooks-test` spends (amendment 3, FR-021)

`m:375-a3-hooks-test-before`. Each guard suite run alone: 894 s in all, of which `test-sync-with-main.sh` 230 s, the next
82 s (`test-pair-hooks.sh`) and 72 s (`test-batching-hooks.sh`). `hooks-test` runs the stale suites in parallel (8 jobs),
so its time is its longest stale suite's, and then the Python test files that test `scripts/` (74 s, all of them on any
script change). `test-sync-with-main.sh` is held to the whole `scripts/` tree (feature 172: its push path reaches scripts
at run time), so it is stale after every merge that touches a script: a post-merge `hooks-test` waited on it and then on
the Python files - 374's 19 runs took 39 min. Its 26 headed cases (25 numbered, 11 and 12 each used twice, and `W`)
each build their own fixture; case 7d (a feature in progress lands nothing) takes 66 s, the rest 1 to 12 s each.

## R4 - wall time against CPU time on this laptop (amendment 5, FR-023 to FR-025)

`m:375-a5-wall-vs-cpu`. The reference hamlet's four seeds, each stage timed in wall and CPU time, on unchanged code: five
rounds quiet, three with six busy-loop processes beside it, three with one on every logical CPU. Quiet, CPU and wall agree
to a hundredth of a second, except the first roll in a process (6.26 s of CPU in 4.47 s of wall: another thread's start-up
work counted). Under load CPU time rose with wall time - about 2.2 times with six cores busy, four to six times with all -
because this processor (Intel Core Ultra 7 155H: performance and efficiency cores, a clock that drops under load) does less
work per CPU second when it is contended. So CPU time does not separate a slower change from a busier machine here, which is
why the GM's answer was to record and flag rather than gate. Quiet, a 3.7 s roll varied by 7.4% across rounds (seed 39) and
the four-seed total by about 2%; rolls are short now (about 4 s each), so a seed's percentage is noisy on its own.

## R5 - what is left after amendment 5 (amendment 7, FR-029 to FR-034)

`m:375-a7-turn-time`, `m:375-a7-perf-and-census`. Model time: 374's session had 1,385 turns (a reply after a tool result),
1.91 hours in all, a median of 3.7 s; a fit gives about 1.6 s a turn, 0.25 s for every 100,000 tokens of context read and
3.3 s for every 1,000 tokens written, so context size explains about 0.5 hours of the 1.91 (a turn at 800,000 tokens about
2 s slower than at none). The "6.5 hours of model time" first put to the GM summed every gap between tool calls, the waits
on background gates, agents and the GM among them; this is the model's own time. `make perf` took 181 s with the old code
(16 rolls) and 97 s with the new (4), and the overlap census it runs after every snapshot took 74 s of those 97 alone. The
cohort: 109 minutes of 374's tool time (`m:375-a7-cohort-cost`), each wave rolling a "before" leg of unchanged code and an
"after" leg, six seeds at a time on one worker under the memory cap; no structured record says which seed found which
failure, so whether fewer seeds would have found the same cannot be counted after the fact.

## R6 - About-only edits to pop-ups (feature 375 amendment 6, FR-028)

Every edit to an existing pop-up from 2026-10-05 to the commit that reopened 375 for amendment 6, replayed through the depiction
re-owe rule (`scripts/measure/depiction_replay.py`, `m:375-a6-about-only-replay`): 221 edits, of which amendment 1's rule owed
`modal-depiction` on 213 and amendment 6's on 170. The 43 between are edits whose About changed and nothing else
`modal-depiction` reads - each an Opus depiction round under amendment 1, none now. (The reopening session's hand count put
44 of 222; the one edit between the two counts was not traced.) Every About edit owes `modal-form`, whose contract holds M13,
so the drawing statement the depiction check used to look for in About is still looked for there.

## R7 - What is left of the record and claims tooling (feature 375 amendment 8)

The claims (`m:375-a8-claims-cold`): `make claims-owed` takes 1.0 s while its cache holds, and 11.9 s after a one-line comment
in one engine module, because the cache is keyed by every engine source together. Profiled cold, the per-module unit work is
17.5 of 24.9 s; parsing and the cross-module constants are the rest. So a cache kept per module - by its source and the
constants it reads - recomputes one module's units after an edit to it.

The check bundle (`m:375-a8-check-bundle`): `make check-bundle Q=0021` took 15.2 s the first time (the page cache filling) and
6.1 s the second. By phase: `record_prepass` 3.2 s, `quote_verbatim` 0.46 s (the two helpers this question ran), the other
git reads 1.1 s, and the bundle's own owed check 1.3 s in-process; four helper interpreters start, imports and all, in 0.35 s
(the imports alone 0.22 s), so the time is in what they compute. `record_prepass`
spends 2.96 of its 3.6 s in `corpus_frequency`, counting every word of the whole record to judge which terms are rare, and
does it again for every bundle; the owed check's translation pairs (`translation_owed.record_pairs`) take 0.92 s. Both read
only the record's content, so both can be kept while it is unchanged - about 3.7 s - where folding the helpers into one process
would save their start, about 0.2 s.

Measured after (`m:375-a8-claims-after`, `m:375-a8-check-bundle-after`): `make claims-owed` after a one-line engine edit took
6.3-7.0 s on today's code and 0.7 s on the new, alternating, three runs each; warm, 0.5-0.7 s. The check bundle - question 0022
right after 0021, the two helpers swapped in place - took 3.7-3.8 s on today's code and 2.8-2.9 s on the new, at load about 2:
about 1 s saved, not the 3.7 s the profile predicted. cProfile slows pure-Python loops more than the rest, so it overstated
`corpus_frequency`'s share; and the first 6.1 s was timed at load 6. The new bundle's time by phase: `record_prepass` 0.68 s,
`quote_verbatim` 0.20, the other git reads 0.32, the owed check in-process 0.81.

## R8 - What a glyph check costs and finds (feature 375 amendment 9)

`make review-yield` over the ledger since 2026-09-26 (`m:375-a8-review-yield`): `glyph-check` is the costliest review check,
9.29 hours, with 120 of its passes reporting a finding and 46 of those acted on - 5.0 acted on an hour, against 12 to 97 for the
others. Counted from the same rows (`m:375-a9-glyph-passes`): 158 glyph-check passes, 124 of them PASS, 46 a second round or
later. A glyph check is owed today on each occasion (feature 294) and dispatched once the gate is green, so a long feature
checks its new elements after each wave and again after each fix; on the hour, an element changed several times in an hour
is checked once, on what it is by then.

## R11 - amendment 11 measured on 374's plan (SC-036 to SC-039)

Observed 2026-10-13; method: `plan_gate.py` run read-only against the backlog clone's `specs/374-match-the-research-continued/`
(the archive on a committed copy of it), `ls -la` for sizes.

- **SC-036**: after batch 18's edits the plan owes 1 of its 69 blocks (`## Batch 18: where a clustered hamlet's wells stand`,
  1,062 characters) where the rule before owed a review of the whole 93,744-character plan.
- **SC-037**: `make plan-archive` moves 38 finished tasks' sections; `plan.md` 93,762 -> 30,706 bytes, `plan-done.md` 64,727; what
  the plan owes is unchanged (the same one block).
- **SC-038**: 374's record converted in memory: 376 KB -> 232 KB (the plan's copy and 43 section copies gone; what is left is the
  decisions). The 105 other records converted in this clone judge exactly as before (105 same, 0 different).
- **SC-039**: 374's T46 section bundle is 12,648 bytes against 117,065 for its spec, plan and request; 374's sections cite their
  own wave items, not the spec's FRs, so its cited file is empty and the reviewer has the index's first lines.
- On 375 itself, after this amendment's plan was written, `make plan-delta F=375` owed 2 blocks (amendment 10's corrected
  counts and amendment 11's section) of its 72 KB plan.
