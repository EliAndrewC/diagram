# Feature 461 contract: the lane's commands

Load this file when: building or calling the lane's or the hand-in's commands (`plan.md` D2, D3, D9).

Each is a Makefile target over `scripts/gates/l7r-gate.sh`. Exits: 0 done, 2 refused (every reason printed together, each with the
command that fixes it), 1 an error the command could not handle (its cause printed).

| target | runs | where | prints | exit |
|---|---|---|---|---|
| `make builder-done T= F= MSG= [GUARD=]` | `l7r-gate land --hand-in` | the builder's pool tree (the registry finds it) | the hand-in's ref, the next dispatch, `handed in to the lane (make lane for its place)`; on a refusal, every reason and its fix | 0; 2 refused (a stopped apply leaves its conflict in the tree and names the files) |
| `make lane-start` | `l7r-gate lane start` | anywhere in the clone | the runner's pid, new or already running | 0 |
| `make lane` | `l7r-gate lane status` | anywhere | each waiting hand-in, the open batch and its state, the last landed batch's line, repairs open | 0 |
| `make lane-wait` | `l7r-gate lane wait` | the coordinator, `run_in_background: true` | every owed line past the read mark, each naming the fresh agent to dispatch where its work is integration (D7's table) (no ceiling of its own; the pool-idle Stop rule refuses the session's stop while the lane has work and none runs, D9) | 0 |
| `make lane-stop` | `l7r-gate lane stop` | anywhere | the batch in flight finished first, then the runner ends; `NOW=1` stops it at once, as `make land-stop` stops a landing | 0 |

Internal: `l7r-gate lane --work` is the runner's own argv (the stall watchdog's match); nobody types it.

Environment the lane hands `make land` in its tree: `SPECIFY_FEATURE` (the batch's feature), `LAND_NOTE` (the changes' subjects,
`landed by the lane, batch <b>`), `L7R_LANE_BATCH` (the batch's id: the red-gate tripwire leaves a run to the lane's own rule,
keyed by task, only when the run is in the lane's tree and the id names a batch open in `lane.jsonl`, or the runner holding
`lane.lock` started it; anywhere else the variable changes nothing, D6 step 4).

Refusals added (each with its test, constitution XVIII):

- `make builder-done`: the first pass's hand-in form (D4), and a stopped apply onto `origin/main` (D3);
- `make builder-tree`: the clone's HEAD holds commits `origin/main` lacks - `scripts/sync-with-main.sh done` first (D13);
- `make land` outside the lane's tree, from phase 4: `make lane-start`, escape `LAND_HERE_OK="<reason>"` (D11).
