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
