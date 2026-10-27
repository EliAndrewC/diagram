# Process clock - feature 437 (FR-006)

Wall-clock UTC. The log opened at 20:57:54 (commit `9e4d79b85`); rows before it are RECONSTRUCTED, each with its source:
commit times (`git log --format=%cI`), the raw profiles' file names (their UTC start), the shell's first timestamp of the
trial (20:54:02) and each review agent's reported duration. WAIT marks time spent waiting on a review, a measurement or a
gate; "overlapped" marks a wait the session worked beside. A time no source holds is "not recorded".

| # | step | start | end | took | kind | source |
|---|---|---|---|---|---|---|
| 0 | the GM's request (after feature 436's amendment landed) | after 20:44:32 | 20:54:02 | not recorded (the session's reply on 436 and the GM's message lie in this window) | - | RECONSTRUCTED: commit `1119c34cf` (436 landed), the shell's first timestamp |
| 1 | read T57 item 10, claim 437, request.md, spec.md | 20:54:02 | 20:54:49 | 47 s | work | RECONSTRUCTED: shell, commit `15464a083` |
| 2 | profile the four largest stages | 20:54:23 | 20:54:52 | 29 s | WAIT (overlapped with 1 and 4) | RECONSTRUCTED: the first profile's file name; the run's own clock |
| 3 | spec review, round 1 | not recorded (after 20:54:49) | not recorded (before 20:58:39) | 189 s | WAIT (overlapped with 4-6) | RECONSTRUCTED: the agent's reported duration |
| 4 | read the profiles: the share and the callers, two scripts | not recorded (after 20:54:52) | 20:57:54 | at most 3 min 2 s | work | RECONSTRUCTED: commit `9e4d79b85` |
| 5 | advisor consulted on the approach | not recorded | not recorded | not recorded | WAIT | RECONSTRUCTED: its place in the session (between rows 4 and 6, so inside 20:54:52-20:57:54); no timestamp holds it |
| 6 | spec push refused (no verdict yet); round 1's four items applied | 20:57:54 | 20:58:39 | 45 s | work | commits `9e4d79b85`, the round 1 fix |
| 7 | spec review, round 2 | not recorded (after 20:58:39) | not recorded | 218 s | WAIT (overlapped with 8-10) | the agent's reported duration |
| 8 | spike written, its equality test, the tests run | 20:58:39 | 20:59:14 | 35 s | work | commits |
| 9 | spike measured - perf-ab quick 38 s, phase-calls 60 s, homesteads profile 29 s - set down, reverted, evidence written | 20:59:14 | 21:01:38 | 2 min 24 s | WAIT 2 min 7 s, work about 17 s | commits; the runs' own clocks |
| 10 | the clock log rewritten from its sources | 21:01:38 | 21:02:01 | 23 s | work | commit `cefa1d3c9` |
| 11 | round 2's items applied (callers re-run over FR-001's space, wording, this log) | not recorded (at or after 21:02:17, round 2's return) | 21:03:15 | not recorded (under 58 s) | work | commit `0919c4423`; round 2's dispatch and duration |
| 12 | spec review, round 3 | not recorded (after 21:03:15) | not recorded | 221 s | WAIT (overlapped with 13) | the agent's reported duration |
| 13 | the round cap put to the round arbiter; spike 2 written, tested, measured (perf-ab 38 s, profile 29 s), reverted; round 3's items applied | 21:03:15 | 21:09:10 | see the commits | work, WAIT for the runs | commits |
