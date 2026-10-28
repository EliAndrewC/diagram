# The 427-end bookend against 427-start (T11)

Measured 2026-10-28, `make perf LABEL=427-end SCALING=1` on the clone at 58f928668 (the host shared with other sessions),
read against `dev/perf-log/20261026T184511Z-427-start-diagram-backlog.json` with `make perf-report AGAINST=427-start
ENV=local`. Calls are the snapshot's counting pass (Python calls, `sys.monitoring` PY_START), summed over each roll's stages.

## Python calls per roll

| households | seed 4 | seed 25 | seed 39 | seed 47 | total, start -> end |
|---|---|---|---|---|---|
| 10 | 3,865,298 -> 3,554,860 | 3,597,149 -> 1,917,530 | 2,624,537 -> 1,667,233 | 2,455,903 -> 1,653,109 | 12.5M -> 8.8M (-30%) |
| 20 | 7,281,027 -> 4,491,507 | 8,042,563 -> 4,955,586 | 6,867,861 -> 3,349,002 | 5,978,094 -> 3,640,404 | 28.2M -> 16.4M (-42%) |
| 40 | 54,120,535 -> 22,471,353 (refused at the end: WebRefused) | 29,460,860 -> 7,613,894 | 18,739,973 -> 6,735,669 | 15,549,984 -> 8,239,850 | 117.9M -> 45.1M (-62%) |

The reference rolls (15 households) total 18,696,644 -> 11,187,978 calls (-40%); CPU time -48.0% (band 0).

## The slowest stage at 40 households (the worst seed's seconds)

Start: web 13.72 s, lane_wells 6.67, homesteads 4.38, field 4.01, hinterland 1.15. End: web 5.31 s, homesteads 2.90, field
2.57, hinterland 1.12, windbreak 0.75.

## Against the success criteria

- **SC-002** (an order of magnitude fewer calls; under 2.5M at 20 households): NOT MET. 20 households fell 42%, to 16.4M over
  four seeds (about 4.1M a roll).
- **SC-003** (every stage under a second at 40 households): NOT MET. Four stages are over a second; the web is at 5.3 s.

Both goals pass to feature 444, whose whole-roll budget is set from first principles and closes only when the roll meets it
(444 FR-009). T10 (the web's pairwise chains) is withdrawn: 444 rebuilds the web against its budget.
