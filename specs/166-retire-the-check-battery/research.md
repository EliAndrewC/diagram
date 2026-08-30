# Research: the baseline, and what the migration is measured against

## R1 - the constitution XIII baseline and the opening perf bookend (T01)

Taken 2026-08-30 on UNMODIFIED code in a detached worktree (`git worktree add --detach /tmp/base166 HEAD`
at `11692b03`), never a stash:

    /tmp/base166/.claude/skills/diagram $ make done
    2786 passed, 2 skipped in 160.07s   -> green

    $ make perf LABEL=166-start
    total 121.3s  median 26.8s  worst 46.8s   (seeds 4, 25, 39, 47)

Zero pre-existing failures, so there is no ledger to carry and every failure after this point is this
feature's.

**Both numbers are higher than feature 163's baseline the same day** (2753 tests, 95.5 s total perf), and
the reason is that main moved: peer sessions landed features 164 and 165 in between. The bookend pair is
still valid because both halves are taken against THIS base, which is what `perf_snapshot` compares on -
but it is worth recording, because a reader comparing 163's numbers to 166's across the session would
otherwise read a 27% perf increase that this feature did not cause and that nothing regressed.

**Sources:** none - a measurement of this repository.
