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
2. `in batch <b>` - an open batch's `batch` line names it and its last line is not an `eject` (before `superseded`, 461 T53: the
   change a batch is landing stays its, a later hand-in of its task waiting until the batch ends);
3. `superseded` - a later hand-in of the same task exists;
4. `ejected` - the lane log's last line for it is `eject`; it names its repair entry;
5. `waiting on its closing half` - a build half's (its tree's last `brief` line since the tree was held says `"kind":
   "build-half"`): formed into no batch, its closing half's hand-in superseding it (461 T90);
6. `waiting`.

## A batch

| field | meaning |
|---|---|
| `batch` | `<feature>-<n>`, n counting up per feature |
| `changes` | the oldest waiting hand-in and the waiting hand-ins of its feature that come straight after it in hand-in order, cut at the first of another feature, at one held behind an open batch, or at `LANE_MAX` (`plan.md` D5) |
| `runs` | each gate attempt: its `set` (the short shas run), its attempt file, its exit, its minutes |
| `landed`, `ejected` | the changes so far |

A batch takes its changes' shas when it forms (the `batch` line), so a later hand-in that moves a task's done ref changes no open
batch. That later hand-in is `waiting` until the batch ends: carried on top if the batch landed the earlier commit (its earlier half
already on main, the carry's empty hunks skipped), or superseding it if the batch ejected it, the earlier one's repair entry then
read as closed (`superseded`). Phase 2 had no halving: a red the record cannot place ejected every change of the batch into ONE
repair entry (`plan.md` D6, "By phase"); since 461 T24 it is halved (D6 step 3), each set its own `run` line, a green one its `push`
line, and a change ejected `red` after its own one-change red run or `inferred` when left last.

Its states: `forming` -> `carrying` -> `gating <n>` -> (`halving` -> `gating <n+1>` ...) -> `pushing` -> `landed`, or `stopped`
(a US5 case: the arbiter owed - a task's second pinned red, `plan.md` D6 step 4 - or the runner killed). A green batch whose push
failed twice is not `stopped`: it files one `integrate` repair entry (`why` `push`) and ends.

A task's PINS are its `eject` lines with `why` `red`, `inferred` or `unplaced`, any batch (a change ejected after its own one-change red run is `red`, so pinned); a red half of two changes or more pins nothing, a `conflict`
ejection pins nothing. At a task's second pin the lane files no repair: the batch stops and the round arbiter is owed.

## A repair entry (`l7r-lane/repairs.jsonl`, one JSON line)

```json
{"utc": "2026-11-28T03:12:09Z", "repair": "r3", "feature": "461-landing-lane", "tasks": ["T13"], "kind": "fix",
 "ejected": ["<done commit sha>"], "batch": "461-7", "why": "red", "units": ["rust/gate/crates/land test"],
 "attempt": "<common>/l7r-lane/attempts/461-7-2.log"}
```

`ejected` is always a list of full shas (461 T15): the one change the gate placed, or every change of an `unplaced` batch (or of an
`integrate` set), so a reader takes one shape. `feature` is the spec directory's name. `why` is `red` (the gate placed it), `inferred` (the last left after the halving), `unplaced` (phase 2: a whole batch whose red
the gate's record cannot place, ejected as one entry), `conflict` (kind `integrate`: the lane's carry of the change stopped in conflict, 461 T25; `units` are the conflicting files, `attempt` the carry's output; the batch's other changes go on), `carry` (kind `integrate`: the change's carry stopped with no conflicting path but not on the lane's own tree, 461 T25 Decision 4; `units` the carry's own stop lines),
`push` (kind `integrate`: a green batch whose push failed twice; `tasks` every change of the set, `attempt` the push's output), or
`arbiter` (filed once the round arbiter's ruling on a task's second pin is recorded; `attempt` names the ruling). Every entry is
taken by a fresh builder the coordinator dispatches (`plan.md` D7's table). The queue reads an entry as READY until a hand-in names it in `repair_of`, then as built; the queue's
own states otherwise (`builder_queue/repairs.rs`).
AN ENTRY IS A CHANGE'S REPAIR ONLY WHERE AN `eject` LINE NAMES IT (461 T15): the runner files the entry before its `eject`
lines, and a runner killed between them resumes what the log has not ejected as a new attempt, which may land a change the entry
lists - so the queue hands out an entry only once a lane `eject` line carries its id (`log::repairs_open`), and the repair's changes
are those `eject` lines' `change`s, never the entry's `ejected` alone. A unit of `units` is `<crate dir> <step>`, or for a Phase line
naming several crates (a `cover-build` of a family) one unit over all of them, `<dir> <dir> <dir> (+<k> more) <step>`. A file the cover step lists with lines no test reaches
is `<file> cover-run` (461 T86).

## The log line (`l7r-lane/lane.jsonl`, one JSON line a transition)

```json
{"utc": "2026-11-28T03:01:44Z", "event": "run", "batch": "461-7", "n": 2, "set": ["a1b2c3d4e5", "f6a7b8c9d0"],
 "code": 1, "minutes": 6.8, "attempt": "<common>/l7r-lane/attempts/461-7-2.log", "red": ["rust/gate/crates/land test"]}
```

| `event` | written when | its own fields |
|---|---|---|
| `start`, `stop` | the runner starts or ends | `pid`, `why` |
| `stop` (of a batch) | the tripwire by task fires (461 T18) | `batch`, `why` `arbiter`, `trigger` (`ask:lane-<task>`, `-<n>` from a third pin), `spec`, `tasks`, `held` (the changes it holds), `attempts` |
| `batch` | a batch is formed | `batch`, `changes` |
| `carry` | the batch's carries end | `code`, `conflict` (files): code 0 with files where a change's carry conflicted and it was ejected (461 T25, its `eject` line before), not 0 where a carry stopped on the lane's own tree (a `make` that could not start, or the carry's refusal of a tree holding unfinished work) and the batch stays open; a change's carry that failed otherwise is ejected `why` `carry` as a conflict is |
| `run` | a gate attempt ends | `n`, `set`, `code`, `minutes`, `attempt`, `red` (the attributed units) |
| `attribute` | a red is read | `candidates` (the changes it names), `how` (`record`, `none`) |
| `push` | a set is pushed, or its push failed after a green gate | `set`, `code` (0, 3 merged, other); `failed: true` where the push failed (461 T19: the batch's first runs the set again on the new `origin/main`, its second files the `integrate` entry) |
| `eject` | a change leaves the batch | `change`, `repair`, `why`; at a second pin (461 T18) `repair` null, `arbiter` (the trigger it waits on) and `attempt`; the ruling's repair's line `of_batch` in place of `batch` (the batch ended at its `stop`), `why` `arbiter` |
| `landed` | the batch is done | `landed`, `ejected`, `runs`, `minutes` |
| `owed` | the coordinator is owed a line | `line` (the status `make lane-wait` prints); `stopped: true` on the runner's own line that it stopped with the batch open (461 T15), which no death line follows |

`make lane-wait` prints the `line` of every `owed` event past `l7r-lane/read-mark` (a byte offset into the log) and moves the
mark. `make task-time` keeps reading the landing's own Phase and `end` lines, which `make land` in the lane's tree still writes
to the feature's event log.

## Recovery

At start the runner reads the log's last batch: one not `landed` or `stopped` is resumed from its last finished event - its tree is
brought to `origin/main` again and its remaining changes run as a new attempt (a set already pushed is on `origin/main` and so
reads `landed`).
