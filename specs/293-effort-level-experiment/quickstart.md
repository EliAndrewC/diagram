# Quickstart: running the pilot (the implementing session)

Prerequisite: the tooling tasks are done and landed (`tasks.md` Phases 1-2), the rubrics and prompts committed.

1. **Pre-flight (P0).** Record `START=<sha>` (main at that moment). Confirm both future-work entries are still open at `START` and that main
   draws no burial-ground way. Run the three R1 measurements and the R6 claims-file check. Snapshot the sources ledger and cache. Draw
   `SEED`; the first task's arm order follows from it and the second task's is the other order (spec US2 AS6). Record all of it in
   `interventions.md` as the first lines.
2. **Freeze.** Commit the rubrics and prompts; the commit time is before the first run's start.
3. **Run, one at a time**, when the host is otherwise quiet: `make effort-run TASK=... RUN=e1 ARM=... COMMIT=$START`; wait for its
   completion notification (never poll); `make effort-measure RUN=e1`. A question from a run: answer it, log it, give the other run of that
   task the identical answer at the same point. A void run is re-launched as the next id.
4. **Blind and grade.** `make effort-blind TASK=R SEED=...`; dispatch `effort-grader` on the bundle; the GM grades the same bundle (A/B only).
   Record both grades, then open the key. Same for I.
5. **Report.** Fill `report.md` from the measurements and grades; apply FR-011; send the outcome through `escalation-check` before it
   reaches the GM.
6. **Land the winners** (spec US4): R's entry through its checks (already passed in the run) onto main; I's diff merged onto current main,
   `make done` and the moved-map reviews run there, defects found recorded in the report. Delete the losing clones; close the future-work
   entries the winners close; append the winning R run's ledger lines to the real ledger.
