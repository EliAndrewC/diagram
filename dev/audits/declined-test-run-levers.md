---
kind: declined
title: five levers on a builder's test run
for: the options - the tests' temp files on an in-memory disk, an empty git template, a shared fixture repository copied per test, more test threads, a faster linker
measured: 2026-11-26
measurement: 451 T315, seven crates alone at load 3 to 12: in-memory disk at most 0.3 s a run of the land crate (and /dev/shm is mounted noexec, a tmpfs mount refused in the container); empty template under 0.02 s; shared fixture 0.04 to 0.13 s; 22 threads 1.4 to 1.9 s against 2.0 s at 44; the linker under 0.25 s of a build
command: the scripts in dev/measurements/2026-11-26/test-run-split/ (the tables are in the T315 section of specs/451-time-retro-and-efficiency/plan.md)
falsifier: what would reopen one - a crate whose tests' own run passes about 10 s alone with most of it in repository setup, or a link step over 1 s
threshold: a lever worth under 1 s a run is not built (GUESS)
cost: none: not built
last-audited: 2026-11-26
cadence-days: 30
---

Declined 2026-11-26 (`docs/process-decisions.md`, "Declined so far").
