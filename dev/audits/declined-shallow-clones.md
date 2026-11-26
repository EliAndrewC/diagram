---
kind: declined
title: shallow clones for session copies
for: the option - session clones and worktrees made with a shallow history to save disk and clone time
measured: 2026-11-25
measurement: a clone's git history is 404 MB; the disk's pressure was the Rust build caches (190 GB against a 100 GB budget the same day, disk-budget.md), not the object store
command: git -C <clone> count-objects -vH (size-pack)
falsifier: what would reopen it - the object store grows past about a gigabyte
threshold: size-pack past 1 GB in a clone (GUESS, from "a gigabyte or so")
cost: none: not built
last-audited: 2026-11-25
cadence-days: 30
---

Not adopted on 2026-11-25 (`docs/process-decisions.md`, "Decisions NOT to do something"): the history is small beside the build
caches, which 451 T245 and T246 hold to budget, and a shallow clone costs the history that `git log` and the replays read.
