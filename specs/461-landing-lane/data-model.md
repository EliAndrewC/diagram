# Feature 461 data model: the lane's entries, batches, states and log line

Load this file when: building or reading the lane's files (`plan.md` D3, D5-D9, D14).

Every file is in the clone's git common directory (`git rev-parse --git-common-dir`), shared by the clone, the pool trees and the
lane's tree. States are COMPUTED from the refs, `origin/main` and the log, never typed into a file (the queue's rule,
`rust/guard/shared/src/builder_queue.rs`), so a runner that dies is restarted with nothing to repair.

## Refs

| ref | written by | holds | deleted by |
|---|---|---|---|
| `refs/l7r/hand-in/<feature>-<task>` | `make builder-done` step 2 | the scratch commit of the builder's work on its old base | `make builder-done` step 6 |
| `refs/l7r/done/<feature>-<task>` | `make builder-done` step 5 (as today) | the hand-in: one commit, parent `origin/main` at hand-in | the lane, after the push that lands it; or superseded by the task's next hand-in |

## A hand-in (one lane entry)

A done ref whose pool-log `done` line carries `"handed_in": true`. Its fields, as the lane reads them:

| field | from |
|---|---|
| `feature`, `tasks` | the ref's name and the `done` line's `detail` |
| `commit` | the ref |
| `base` | the commit's parent: the clone's HEAD in phase 1, `origin/main` from phase 2 (`HAND_IN_BASE`) |
| `at` | the `done` line's `utc` (the queue order) |
| `subject` | the commit's subject (the landing's NOTE is built from these) |
| `repair_of` | the repair entry it answers, where its brief named one |

Its state, the first that holds:

1. `landed` - `origin/main` holds a commit of its author time and subject (`builder_done::uncarried`'s test, asked of
   `origin/main`);
2. `superseded` - a later hand-in of the same task exists;
3. `ejected` - the lane log's last line for it is `eject`; it names its repair entry;
4. `in batch <b>` - an open batch names it;
5. `waiting`.

## A batch

| field | meaning |
|---|---|
| `batch` | `<feature>-<n>`, n counting up per feature |
| `changes` | the hand-ins it holds, oldest first (at most `LANE_MAX`) |
| `runs` | each gate attempt: its `set` (the short shas run), its attempt file, its exit, its minutes |
| `landed`, `ejected` | the changes so far |

A batch takes its changes' shas when it forms (the `batch` line), so a later hand-in that moves a task's done ref changes no open
batch. That later hand-in is `waiting` until the batch ends: carried on top if the batch landed the earlier commit (its earlier half
already on main, the carry's empty hunks skipped), or superseding it if the batch ejected it, the earlier one's repair entry then
read as closed (`superseded`). Phase 2 has no halving: a red the record cannot place ejects every change of the batch into ONE
repair entry (`plan.md` D6, "By phase").

Its states: `forming` -> `carrying` -> `gating <n>` -> (`halving` -> `gating <n+1>` ...) -> `pushing` -> `landed`, or `stopped`
(a US5 case: the arbiter owed, a set red twice, the runner killed, a push failed twice).

## A repair entry (`l7r-lane/repairs.jsonl`, one JSON line)

```json
{"utc": "2026-11-28T03:12:09Z", "repair": "r3", "feature": "461-landing-lane", "tasks": ["T13"], "kind": "fix",
 "ejected": "<done commit sha>", "batch": "461-7", "why": "red", "units": ["rust/gate/crates/land test"],
 "attempt": "<common>/l7r-lane/attempts/461-7-2.log"}
```

`why` is `red` (the gate placed it), `inferred` (the last left after the halving), `unplaced` (phase 2: a whole batch whose red
the gate's record cannot place, ejected as one entry), or `conflict` (the lane's carry stopped; `units` are the conflicting files). The queue reads an entry as READY until a hand-in names it in `repair_of`, then as built; the queue's
own states otherwise (`builder_queue/repairs.rs`).

## The log line (`l7r-lane/lane.jsonl`, one JSON line a transition)

```json
{"utc": "2026-11-28T03:01:44Z", "event": "run", "batch": "461-7", "n": 2, "set": ["a1b2c3d4e5", "f6a7b8c9d0"],
 "code": 1, "minutes": 6.8, "attempt": "<common>/l7r-lane/attempts/461-7-2.log", "red": ["rust/gate/crates/land test"]}
```

| `event` | written when | its own fields |
|---|---|---|
| `start`, `stop` | the runner starts or ends | `pid`, `why` |
| `batch` | a batch is formed | `batch`, `changes` |
| `carry` | the batch's carries end | `code`, `conflict` (files) |
| `run` | a gate attempt ends | `n`, `set`, `code`, `minutes`, `attempt`, `red` (the attributed units) |
| `attribute` | a red is read | `candidates` (the changes it names), `how` (`record`, `none`) |
| `push` | a set is pushed | `set`, `code` (0, 3 merged, other) |
| `eject` | a change leaves the batch | `change`, `repair`, `why` |
| `landed` | the batch is done | `landed`, `ejected`, `runs`, `minutes` |
| `owed` | the coordinator is owed a line | `line` (the status `make lane-wait` prints) |

`make lane-wait` prints the `line` of every `owed` event past `l7r-lane/read-mark` (a byte offset into the log) and moves the
mark. `make task-time` keeps reading the landing's own Phase and `end` lines, which `make land` in the lane's tree still writes
to the feature's event log.

## Recovery

At start the runner reads the log's last batch: one not `landed` or `stopped` is resumed from its last finished event - its tree is
brought to `origin/main` again and its remaining changes run as a new attempt (a set already pushed is on `origin/main` and so
reads `landed`).
