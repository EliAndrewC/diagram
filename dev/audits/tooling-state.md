---
kind: adopted
title: the per-clone tooling state pushed to the private tooling-state repository
for: a lost container loses no check answer and no measurement - a clone's .git/record-checks and .git/l7r-events are pushed after every landing and merged back into a fresh clone or a replacement container
measured: 2026-11-25
measurement: on diagram-backlog's state (2,837 answers, 71 MB; 31 logs, 122 MB), the machine at load 24 to 28: the git mirror's first push to GitHub 29.3 MB in 8.7 s, a landing's push after it 0.13 MB in 7.0 s (to a local bare remote 0.13 and 0.72 MB in 2.6 and 9.7 s; the first there 126 s, packed three times before the fix that packs it once); the landing itself waits 0.03 s (the push is detached); the mirror on disk 29 MB, steady across three pushes (repacked each run); a restore over the full state 15.9 s. The alternative, a tar.gz snapshot of both, 33.8 MB and 4.7 s every landing. Whole logs committed unsegmented grew the mirror 9 MB a commit
command: make state-push (its line gives the seconds and the bytes sent); the record of every run is <common .git>/tooling-state.log, one JSON line each (action, outcome, s, bytes, answers, lines)
falsifier: no restore has ever brought anything back (no `"action": "restore"` line of any clone's tooling-state.log with answers or lines above 0) and the pushes cost more than they save - a push grown slow or large, or failing
threshold: a landing's push past 60 s or 5 MB sent as the median of the log's last 20 pushes, or more than 1 failed push in 20, or 90 days with no restore that brought anything back (GUESS; a restore saves the answers' re-checking, 2,837 answers of agent checks on this clone, against detached seconds no session waits on)
cost: no session time (detached; 0.03 s at the landing); 3 to 10 s of one core a landing and 0.1 to 0.7 MB sent; 29 MB of disk a clone for the mirror; one fetch at a fresh clone's first sync-in
last-audited: 2026-11-25
cadence-days: 30
---

451 T258, the GM 2026-11-25: "I created https://github.com/EliAndrewC/diagram-tooling-state for the tooling state". The repository is
PRIVATE: what it holds is never linked or copied anywhere public. `scripts/state-sync.sh` (its header holds the mechanism and why
each part is as it is): `make land` and `make land-tooling` run `push --detach` after their own push and exit with their own code;
`make state-restore [FROM=<clone>]` merges a branch back, and `sync-with-main.sh sync-in` does so once for a clone with no mirror
yet. A branch a clone, named for the clone the common .git belongs to.

Chosen by measuring (above): a bare git mirror under the common .git, committed into, over tar snapshots - a landing sends what
changed, not everything. The logs go in as 8 MB segments (`SEGMENT`, a GUESS knob) so an append re-sends one segment and no file
nears GitHub's 100 MB limit, which 449's 38.6 MB log was on its way to.

Known limits, accepted (this builder, 2026-11-25): a detached push's failure is said at the NEXT landing, not the one that started it
(the alternative, a foreground push, delays every landing 3 to 10 s); a landing's push sends the grown logs' last segments whole
(0.1 to 0.7 MB) where a delta would be a few KB - git's thin pack found no base for them, not pursued at this size; the audit
register's check does not see this step (a script called from a recipe is none of its five detectors), so this entry carries no
`covers:` line.
