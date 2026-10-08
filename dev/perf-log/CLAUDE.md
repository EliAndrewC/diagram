# `perf-log/` - how long the generator took, over time

One JSON file per snapshot. **Never edit these; never delete one to make a trend look better.**

    make perf LABEL=<NNN>-start          # record a snapshot (and <NNN>-end before shipping)
    make perf-report                     # print the trend, latest vs the one before
    make perf-report AGAINST=<NNN>-start # the newest snapshot against a bookend

## Why a directory and not one log file

This is the one home of the rule for every log under `dev/` (`run-log/`, `bypass-log/`, `idle-log/` point here).
Several session clones change this engine at the same time, and an append-only shared log conflicts on every
concurrent push - two sessions add lines at the same offset, the merge is textual, the content is not, and resolving
it by hand is exactly the kind of chore that ends with someone deleting rows. A file per entry never conflicts,
because git merges disjoint new files without being asked.

The rule had to be learned twice. It was written here (as a README) and then broken on 2026-08-24 by a session that
had read it the same day, which created a single-file `run-log.jsonl`. The GM caught it: *"I thought that the general
way to deal with this would be to have a directory rather than a file... I'm not sure if you implemented a single file
because you figured out that this will not be a problem or if my instructions simply got dropped."* Neither - the
pattern was in the repo and went unapplied. Hence a `CLAUDE.md` and not a README: a README is never loaded into a
session's context, and anything a session must KNOW belongs in a `CLAUDE.md` or a doc one points at.

The filename carries `<utc>-<label>-<clone>`, so the trend reconstructs WHO changed WHAT and WHEN
without opening anything: a run of slow snapshots all from one clone is a feature that regressed,
while a step across every clone at once is the machine or a dependency.

## What a snapshot measures

The REFERENCE HAMLET - Inashiro's spec, held fixed - rolled across a fixed set of seeds, timed per
stage. Seeds rather than maps, because one map proves nothing about performance: a seed can be
pathologically good as easily as bad. The seed set deliberately includes the slowest seeds known
when it was chosen, so a comfortable average cannot hide a stalled outlier.

This does NOT replace `GEN_TIME_BUDGETS` in `tests/test_villages.py`. That is a per-gen CEILING that
fires when one pool map goes pathological. This is a TREND, and it answers the other question: is
the generator getting slower, and since when.

## The bookends

Constitution VI requires a diagram spec-kit feature to record `<NNN>-start` before it changes
anything and `<NNN>-end` before it ships, and to diagnose any seed more than 5% slower. The 5% is
the project's own threshold for a whole-process speedup mattering, applied in the other direction.
