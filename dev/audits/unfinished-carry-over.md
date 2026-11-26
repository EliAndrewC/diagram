---
kind: adopted
title: the landing refuses an unfinished carry-over, and make carry carries a builder's commit
for: no task is ticked and pushed without its code because a cherry-pick, merge or revert stood unfinished in the clone, and a builder worktree's commit reaches the clone by one command that resolves the two conflicts every carry-over meets and verifies its end
measured: 2026-11-26
measurement: three landings ran over an unfinished hand cherry-pick (451 T235, T262, T270; T270's pushed its tick without its code, 0526d8b7df, repaired by 83f65718d7). The check through the launcher, three runs on the builder worktree at load: 0.06 s each (three git processes); a carry with one both-sides-added tasks.md conflict on a scratch clone and worktree, 0.08 s. Red first on T270's state built by a real cherry-pick: the unfixed landing answered 0 with land-alone.sh started, the fixed one 2 with nothing run; the unfixed push met a stopped pick with a line naming no command and did not refuse a merge standing on a clean status; the unfixed land-tooling landed from HEAD over a stopped pick
command: make rust-test CRATE=rust/gate/crates/land (land/unfinished/tests.rs, land/carry/tests.rs); bash tests/hooks/test-sync-with-main.sh (case Z3); bash tests/hooks/test-land-tooling.sh (case 8); time scripts/gates/l7r-gate.sh land --unfinished "$PWD"
falsifier: the refusal fires on correct work - a landing held for a staged change or a marker that was no unfinished carry-over - or a landing again ticks a task whose code is not in its delta, or sessions go back to hand cherry-picks because make carry stops on conflicts a hand resolves the same way every time
threshold: more than 1 refusal in 20 that was no unfinished work (the refusal is in the landing's output; a session that meets one says so in its task), or one more landing without its code, or make carry stopping on more than 1 carry-over in 5 for a conflict of one repeated shape (GUESS)
cost: 0.06 s a landing, a land-tooling and a push (0.12 s where make land ends in its own push); make carry 0.1 s in place of a hand cherry-pick and its hand merge
last-audited: 2026-11-26
cadence-days: 30
covers: landing refusal land/unfinished.rs #1
covers: landing refusal land/unfinished.rs #2
covers: landing refusal land/unfinished.rs #3
covers: landing refusal land/unfinished.rs #4
---

451 T292. `rust/gate/crates/land/src/land/unfinished.rs` is the one copy of the check (its header holds T270's landing and why the
refusal comes first and apart: a dirty clone is sent to land alone, which lands HEAD without the uncommitted work, and the first
pass's own commits would conclude a stopped pick); `l7r-gate land --unfinished <tree>` asks it for `scripts/sync-with-main.sh`'s
push and `scripts/land-tooling.sh`. `carry.rs` is `make carry`.

Chosen (this builder, 2026-11-26): no escape - each refusal prints the command that finishes the work, and nothing a landing does
is correct over a stopped pick. Staged changes with nothing in progress are refused too, on the reading that the landing stages and
commits in one step and a builder never stages; that reading is the falsifier's first clause. `make carry` keeps both sides only
where that is provable - a hunk both sides only added to, every added line a list line, or the record's own three-way merge - and
stops on everything else, a file it could have merged by hand included: a wrong keep-both in code is worse than a stop.

A pick or revert of several commits paused between two (`sequencer/todo`, no `*_HEAD`, a clean status) is read too, and a mailbox
apply told from a rebase; the history guard lets `git rebase --abort` through, the command the refusal of a rebase prints (the plan
review's two findings, 2026-11-26). Known limit, accepted: `make carry` carries one commit. The audit register's check reads this file's refusals since this task (`REFUSALS` in
`rust/gate/crates/checks/src/checks/audit_register/detect.rs` counted the first pass's `land/cheap.rs` alone, so the refusal would
have landed asking no entry): the four `covers:` lines above are its two in-progress forms, the unmerged paths and the staged changes.
