# `run-log/` - how the gate has actually been used

One JSON file per gate run: target, scope, ELAPSED SECONDS, result, commit. Read it with
`make audit`; never edit or delete an entry to make the history look better.

A `make done` entry that RAN (not an `already-verified` reuse) also carries, since 2026-10-03 (GM: whether
streaming failures would let a session start fixing early needs these numbers, and an outlier run needs telling
from a slowdown):

- `first_failure_s`, `last_failure_s` - seconds after the gate's start; a failed test marks its own moment, a
  failed non-test phase the moment it ended. `failed_tests` - how many tests failed.
- `host` - `load` and `mem_avail_mb` (MB) as `[start, end]`; `stall_s` - seconds over the run that some task
  waited for `cpu`, for the disk (`io`, `io_full`: every task waiting) or for `memory` (the kernel's pressure
  stall totals); `cpu_temp_c` as `[start, end]`; `throttle_ms` - thermal-throttle time over the run (`core`
  summed over CPUs, `package`). A figure the host does not expose is left out.

Written by `scripts/_runstats.py` (what each figure reads and why only one read each), pinned by
`tests/tooling/test_runstats.py`.

**A CLAUDE.md rather than a README, deliberately**: this is a rule a session has to KNOW, and a
README is never loaded. See [`../perf-log/CLAUDE.md`](../perf-log/CLAUDE.md) for what that cost.

## Why a folder per month

Each entry goes in `<YYYY-MM>/`, named from its own UTC stamp (2026-10-02). Both logs gain an entry per gate run
or escape, about a thousand files a week between them, with no end; no tracked directory may pass 5,000 files
(`scripts/check-file-scale.py`), and a shell glob over one flat folder would reach the argument limit within a
year. Every reader searches recursively, so an entry a clone wrote flat before syncing past the move still counts.

## Why a directory and not one log file

**The same reason as [`../perf-log/`](../perf-log/README.md), and this file exists because that
lesson had to be learned twice.** Several session clones work on this engine at once, and an
append-only shared log conflicts on EVERY concurrent push: two sessions add lines at the same offset
and git has no way to know which goes first. The merge is textual; the content is not. A file per
entry never conflicts, because git merges disjoint new files without being asked.

The first version of this log was a single `run-log.jsonl`, written on 2026-08-24 by a session that
had read `perf-log/README.md` earlier the same day and quoted it. The GM caught it: *"I thought that
the general way to deal with this would be to have a directory rather than a file... I'm not sure if
you implemented a single file because you figured out that this will not be a problem or if my
instructions simply got dropped."* Neither - the pattern was in the repo and went unapplied.

## Why it exists at all

GM 2026-08-24: *"if there exists a make done that can be run in order to run the full tests, do we
still have the ability to audit that it is only being run when we have fully completed a feature?
... not just confirming that in the moment, but also being able to audit after the fact."*

Before this, only BYPASSES were recorded, so plain `make done` usage was invisible and that question
had no answer. Elapsed seconds are recorded too: a target that quietly gets slower shows up in the
history rather than in someone's memory, which is how `make quick` reached 254 s unnoticed.
