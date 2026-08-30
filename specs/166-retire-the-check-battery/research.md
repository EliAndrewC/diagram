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

## R2 - the accept-criterion change did not move a map (T05)

`make maps` after T03, with every hamlet genuinely REGENERATED rather than served from cache
(inashiro 30.5 s, kashikawa 45.3 s, kuwabata 40.2 s, mizuguchi 20.6 s, sawada 50.6 s; exit 0), then
`git status` over `pool/`:

    (empty)

**All five live hamlets are byte-identical after the ladder's accept criterion changed from the gate's
whole failure list to the reach count.**

**What this does and does not prove**, stated precisely because the temptation is to read it as more than
it is. It proves the change moved none of the five maps we ship. It does NOT prove the two criteria are
equivalent in general - they are not, and the difference is exactly the case the old one was built for: a
re-roll that fixes reach while breaking something else. On these five seeds that case never arose, either
because no re-roll was rejected or because the two measures agreed. A wider seed set (the tripwire seeds,
a cohort) would exercise it harder.

That is acceptable and was the requirement: FR-002 asks for the difference to be DIAGNOSED, not prevented,
because the GM's standing ruling is that maps may move. Here there is no difference to diagnose. If a
future seed does move, the cause is already written down at the point of change in `driver.py`.

**Sources:** none - a measurement of this repository.
