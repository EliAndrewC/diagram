# Does the calibration loop's slowdown track quick's? (FR-007's one-shot measurement)

Measured 2026-10-27 on this 22-CPU host shared with other sessions: a fixed suite (`make test-file FILE=tests/hamletgen/`, 6
xdist workers as quick uses) timed beside `ratchet.slowdown` (the calibration loop on 6 processes, best of 3 rounds' slowest,
over the pinned 0.12 s), quiet and then with 16 busy processes (`python3 -c 'while 1: pass'`) adding load. The script is the
session's (`os.times` for the children's CPU).

| run | suite wall | children CPU | loop slowdown | load (1 min) | wall / slowdown |
|---|---|---|---|---|---|
| quiet 1 | 14.0 s | 73.0 s | 1.25x | 4.0 | 11.2 s |
| quiet 2 | 16.6 s | 84.1 s | 1.31x | 4.5 | 12.7 s |
| loaded 1 | 35.0 s | 139.8 s | 2.74x | 11.8 | 12.8 s |
| loaded 2 | 30.2 s | 143.8 s | 3.00x | 15.7 | 10.1 s |

- The suite slowed 2.13 times under the load (15.3 s -> 32.6 s, the means), the loop 2.24 times (1.28x -> 2.87x): it tracks
  within about 5%, and the suite's time net of the slowdown stays at 10-13 s quiet or loaded.
- The children's CPU time doubled under load as well (shared physical cores), so CPU time is no load-free measure here; the
  loop is.
- A first attempt, whose "quiet" run was taken while load from the session's own failed start was still at 8.7, read the
  loop 2.35 times against the suite's 1.38 - its baseline was not quiet. It is reported, not used.

## The ceiling it is read against

The 15 s is the GM's: "if it takes even as much as fifteen seconds ... a failure" (`specs/171-runtime-ratchets/request.md`,
2026-08-30), pinned as `hard_ceiling=15` on quick's ratchet in `scripts/measure/ratchet.py`; this feature leaves it, and the
11 s baseline, as they are.
