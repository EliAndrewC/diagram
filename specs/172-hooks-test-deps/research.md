# Feature 172 - what the refinement is actually worth, measured BEFORE specifying

## R1 - the skip already exists, and costs nothing

Measured with nothing changed since the last green run:

    hooks-test: 0 guard suites green, 21 unchanged since they last went green
    elapsed: 0s

So the mechanism the GM expected is present and working. The 94 s figure that prompted this came from
a run where 29 guard scripts had genuinely changed in half a day - four consecutive days of guard work
(162, 164, 168, 169, 170, 171). Nothing was stale; there was simply nothing stable to hit.

## R2 - THE REFINEMENT IS WORTH MUCH LESS THAN IT LOOKS, because the dependency is TRANSITIVE

Every suite is declared to depend on all four shared helpers. The obvious refinement is to derive each
suite's real dependencies. Measured over the actual reference graph - and the graph is TRANSITIVE,
because `_guardlog.sh` itself calls `_hookmatch.py` (`escape_or_refuse`, feature 170), so every guard
that sources `_guardlog.sh` depends on `_hookmatch.py` whether it names it or not:

| shared helper | suites that must re-run, DERIVED | today | saved |
|---|---|---|---|
| `_hookmatch.py` | **20** of 21 | 21 | **1** |
| `_guardlog.sh` | **19** of 21 | 21 | 2 |
| `_gatecost.py` | **2** of 21 | 21 | **19** |
| `test_hooks_cases.py` | **3** of 21 | 21 | **18** |

**The two helpers this session edits constantly are the two the refinement barely helps.** Nearly all
of the last days' guard work touched `_hookmatch.py` or `_guardlog.sh`; on those the refinement saves
one or two suites out of 21. The GM's expectation that this "would have paid off a lot over the last
couple of days" is not supported by the measurement, and that is recorded here rather than discovered
after the work.

The refinement IS worth having for the other two: a `_gatecost.py` edit (which this session made
today, one line) drops from 21 suites to 2.

## R3 - where the time actually is, and the lever the measurement points at

`hooks-test` runs its 21 suites SERIALLY. The `diagram-testing` session measured the phase at 94 s
against 17 s for the entire 2,286-test Python suite, which pytest runs in parallel. When a shared
helper changes - which is most of the time during guard work - the derived set is still 19-20 suites,
so the only thing that reduces THAT cost is running them concurrently.

Each suite builds its fixtures in its own `mktemp -d`, and since feature 170 each isolates its own
`GUARD_LOG_DIR`. That is the argument that parallelizing is safe; it is not proof, and two suites
(`test-sync-with-main.sh`, `test-clone-sync-hooks.sh`) manipulate git trees and a host-wide lock.
Verify before relying on it.
