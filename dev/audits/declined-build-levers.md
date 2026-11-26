---
kind: declined
title: build levers - line-table debug info, incremental off, a shared compiler cache, an eager drop of coverage builds
for: the options - each would trade build or test time for disk in the Rust target directories (13-14 GB a fresh worktree, 94 GB the session clone's, 55 GB of that coverage builds)
measured: 2026-11-26
measurement: against main (debug = 0, incremental on; gate cold 327 s, warm 55 s, 2.86 GB; guard cold 91 s, warm 24 s, 0.68 GB) - line tables cold +12-14%, warm +1-25%, disk +76-114%; incremental off disk -81% but warm 363 s (gate) and 100 s (guard); sccache 0 hits of 18 in a fresh target directory, cold +23%; a dropped coverage build costs up to 512 s cold against 123 s warm to free about 41 GB and 24 GB
command: dev/measurements/2026-11-26/build-levers/m9-run.sh <label> <gate|guard> <test|cover> <cold|warm|keep> [ENV=VAL ...]
falsifier: what would reopen each - a tool that needs DWARF; a tree that builds once and is thrown away (incremental off); sccache showing hits across worktrees; the disk pressing again, when the GM may take about 6 minutes a landing for about 65 GB
threshold: a lever is adopted only where no build or test time is lost beyond the measured noise (the GM's pre-approval, 2026-11-25); warm-rebuild noise was about 1-2 s
cost: none: not built
last-audited: 2026-11-26
cadence-days: 30
---

Declined under the GM's pre-approval of 2026-11-25 for the talk's item 9 (`docs/process-decisions.md`, "Declined so far"). The
measurement's caveats: a shared machine (load 5 to 86), one quiet cold baseline for the gate family, sccache tried on the guard
family only. Its finding acted on: stale incremental variants under the coverage builds, 451 T278.
