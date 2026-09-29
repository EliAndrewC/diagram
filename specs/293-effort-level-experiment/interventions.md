# Interventions - feature 293

One line per event (UTC, run id, kind, text). Written by the implementing session; an answer given to one run of a task is
given, identically, to the other.

- 2026-09-29T21:44:01Z | - | preflight | START (superseded by the re-freeze below) 1044b0372c701fc6a27831f569777b67d47b4f64 (this clone's HEAD with the final rubrics and prompts); SEED 853050; order R: xhigh then medium, I: medium then xhigh - runs e1 R/xhigh, e2 R/medium, e3 I/medium, e4 I/xhigh
- 2026-09-29T21:44:01Z | - | preflight | sources snapshot /diagram/.clones/.runs-293/sources-snapshot, ledger sha256 8b2c60bbc18d59d2...; fallback offset 1.9 GB (the larger measured, R5 D7)
- 2026-09-29T21:44:01Z | - | preflight | memory: the shared cgroup's working set read 5.87 GB with other sessions active (a fully quiet host was not available; the gate opens at 4.5 GB, so it CAN open - it read 4.2-4.7 GB through the afternoon)
- 2026-09-29T21:44:01Z | - | preflight | R8: both future-work entries open at START; main draws no burial-ground way (feature 287's tasks T03/T46 still open)
- 2026-09-29T21:44:10Z | e1 | wait | launch refused: shared working set 6.09 GB over 4.5 GB; waiting (R5 D7)
- 2026-09-29T21:53:15Z | e1 | refreeze | the page runner refused R-write.md (no '## Your items' for its write cap to count) before anything ran; the brief gained that section, the launcher now removes the clone on a refusal, and the experiment was re-frozen at a new START with the same SEED (no run had started)
- 2026-09-29T21:53:16Z | - | preflight | re-freeze: START ec99356cf081c1ac44ae227723edfdcf5675e6f7, SEED 853050 (the same order), snapshot re-taken
- 2026-09-29T22:03:31Z | e1 | memwatch | warning at 22:03 UTC during the run (8.1 GB raw: diagram 4.7, gm-assistant 3.4); the run continues (R5 D7)
- 2026-09-29T22:16:18Z | e1 | memwatch | warning at 22:15 UTC during the run (8.5 GB raw: diagram 4.7, gm-assistant 3.8); the run continues
- 2026-09-29T22:36:45Z | e1 | memwatch | warning at 22:35 UTC during the run (8.8 GB raw: diagram 5.0, gm-assistant 3.8); the run continues
- 2026-09-29T22:49:49Z | e1 | memwatch | warning at 22:49 UTC during the run (8.1 GB raw: diagram 5.4, gm-assistant 2.3); the run continues
- 2026-09-29T23:10:15Z | e1 | memwatch | warning at 23:09 UTC during the run (8.0 GB raw: diagram 7.2, gm-assistant 0.8); the run continues
- 2026-09-29T23:17:44Z | e1 | memwatch | warning at 23:17 UTC during the run (8.0 GB raw: diagram 6.8, gm-assistant 1.2); the run continues
