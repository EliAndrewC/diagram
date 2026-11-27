# 451 T505 and T506 - a wave row's wait bounded; the partial read's cheaper scan priced

Method: `dev/measurements/2026-11-27/t490-part-read/t490-time.py <before> <after> 20`, unchanged, run from a scratch copy with
`T490_SRC` set to a copy of the clone's `checks-open.json` (2,618,222 bytes, copied from the clone's common git dir 2026-11-27
08:2x (before 08:33)). Per case 2 warm-up and 20 counted rounds, the two binaries INTERLEAVED; CPU from `RUSAGE_CHILDREN`; "writes" counts the
calls whose state file's inode moved.

Binaries: `before` is the clone's guard at 495a852db9 (its checks code differs from this tree's base f0197563d3 only by T490's
coverage repair of `Part::whole`, no answer moved); `T505` is this tree with the wave wait; `T506` is that plus `IgnoredAny` for the
skipped rows and fields (built, timed, reverted).

## T505 - `before` against `T505` (`t505-time-run1.txt`, `t505-time-run2.txt`)

| case | run 1 CPU ms | run 2 CPU ms | writes |
|---|---|---|---|
| agent-stop (checks-hooks SubagentStop, an agent no row names) | 89.6 -> 14.1 | 94.3 -> 14.3 | 22/22 -> 0/22 |

Load 4.4 to 4.6 (run 1), 2.5 to 2.6 (run 2). The other four cases did not move (within 2 ms, writes unchanged). The 14 rows were
`returned` with no reply, 860.7 to 863.6 hours past their dispatch (counted with Python's `json` on the copy); every one is now
past `WAVE_WAIT_S` (6 h, a GUESS knob in `rounds.rs`).

## T506 - `T505` against `T506` (`t506-time-run1.txt`, `t506-time-run2.txt`)

| case | run 1 CPU ms | run 2 CPU ms |
|---|---|---|
| bash-pre | 17.7 -> 17.0 | 18.6 -> 17.4 |
| bash-post | 14.9 -> 13.7 | 15.7 -> 15.3 |
| agent-post | 27.2 -> 29.3 | 30.7 -> 31.0 |
| agent-pre | 9.8 -> 8.7 | 9.2 -> 9.5 |
| agent-stop | 12.3 -> 11.5 | 11.3 -> 10.5 |

Load 2.7 to 2.8 and 2.5. -2.1 to 1.2 ms a hook (agent-post 2.1 and 0.3 the other way), against the 5 to 8 ms the task line
priced. It agrees with T490's own in-process bench (`t490-part-read/t490-bench.txt`): the exact scan 2.38 ms, `IgnoredAny` 1.67.
The 5 to 8 ms between the partial read and the `dispatches`-dropped arm is not the scan's exactness; not built.
