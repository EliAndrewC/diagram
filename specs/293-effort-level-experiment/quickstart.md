# Quickstart: running the pilot (the implementing session)

Prerequisite: the tooling tasks are done and gated green (`tasks.md` Phase 1), the rubrics and prompts committed. The tooling
cannot land on main while the feature's tasks are open (the push's open-task refusal), so the runs clone from the session's own clone
at the recorded start commit (`effort-run`'s default origin), and everything lands together at the end.

1. **Pre-flight (P0).** Record `START=<sha>` (main at that moment). Confirm both future-work entries are still open at `START` and that main
   draws no burial-ground way. Run the three R1 measurements and the R6 claims-file check. Snapshot the sources ledger and cache. Draw
   `SEED`; the first task's arm order follows from it and the second task's is the other order (spec US2 AS6). Record all of it in
   `interventions.md` as the first lines.
2. **Freeze.** Commit each task's rubric and prompts before that task's first run starts - a replaced task's before the
   replacement's first run (FR-008, SC-002; `make effort-refreeze`). Push nothing of this feature until the last run has ended:
   a pushed `interventions.md` would reach later run clones through `origin/main`.
3. **Run, strictly one at a time** (the GM, 2026-09-29, for memory), when the host is otherwise quiet; a launch the headroom check refuses is
   logged and retried later, never forced; while a run is live, do nothing memory-heavy (no gate, tests, measurement or grading): `make effort-run TASK=... RUN=e1 ARM=... COMMIT=$START`; wait for its
   completion notification (never poll); `make effort-measure RUN=e1`. A question from a run: answer it, log it, give the other run of that
   task the identical answer at the same point. A void run is re-launched as the next id.
4. **Blind and grade**, one grading at a time, after the last run has ended. `make effort-blind TASK=R SEED=...`; dispatch `effort-grader` on the bundle; the GM grades the same bundle (A/B only).
   Record both grades, then open the key. Same for I.
5. **Report.** Fill `report.md` from the measurements and grades; apply FR-011; send the outcome through `escalation-check` before it
   reaches the GM.
6. **Land the winners** (spec US4): R's entry through its checks (already passed in the run) onto main; I's diff merged onto current main,
   `make done` and the moved-map reviews run there, defects found recorded in the report. Delete the losing clones; close the future-work
   entries the winners close; append the winning R run's ledger lines to the real ledger.
