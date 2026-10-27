# Process clock - feature 437 (FR-006)

Wall-clock UTC. The log opened at 20:57:54 (the share measurement's commit); the steps before it are RECONSTRUCTED from the
shell's first timestamp (20:54:02, the session's first command after the GM's request), commit times (`git log --format=%cI`)
and each review agent's own reported duration. WAIT marks time the session spent waiting on a review, a measurement or a gate;
it did other work beside a wait where it could (marked "overlapped").

| # | step | start | end | took | kind | source |
|---|---|---|---|---|---|---|
| 1 | read T57 item 10, claim 437, request.md, spec.md | 20:54:02 | 20:54:49 | 47 s | work | reconstructed: shell, commit |
| 2 | profile the four largest stages | 20:54:2x | | 29 s | WAIT (overlapped with 1) | the run's own clock |
| 3 | spec review, round 1 | ~20:55 | ~20:58 | 189 s | WAIT (overlapped with 4) | the agent's reported duration |
| 4 | read the profiles: share and callers, scripts written | ~20:55 | 20:57:54 | ~3 min | work | reconstructed: commit |
| 5 | advisor consulted on the approach | ~20:57 | ~20:58 | ~1 min | WAIT | reconstructed |
| 6 | spec push refused (no fidelity verdict yet) and round 1's four items applied | 20:57:54 | 20:58:39 | 45 s | work | commits |
| 7 | spec review, round 2 | 20:58:4x | | (pending) | WAIT (overlapped with 8-9) | |
| 8 | spike written, equality test, tests run | 20:58:39 | 20:59:14 | 35 s | work | commits |
| 9 | spike measured: perf-ab quick 38 s, phase-calls 60 s, profile 29 s; set down, reverted, evidence | 20:59:14 | 21:01:38 | 2 min 24 s | WAIT 2 min 7 s, work ~20 s | commits, the runs' clocks |
