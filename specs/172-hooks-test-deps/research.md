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

## R4 - the split delivered nothing three times before it delivered anything

Each failure was found by MEASURING the blast radius after the change rather than by assuming the
split had worked, and each was the same mistake wearing a different coat.

| attempt | measured | cause |
|---|---|---|
| after splitting into three leaves | `_hm_make.py` **17 of 18** guards | the deriver's `_SHARED` roster was a HARDCODED list of the four helpers that existed when it was written. The three new leaves were invisible to the closure, so it reported that no guard depends on the escape family - through which every guard reaches its escape. A hardcoded list, in the feature whose subject is deriving instead of listing |
| after deriving the roster | still **17 of 18** | the closure scanned RAW TEXT, and this repository comments heavily: nearly every guard says *"detection lives in `_hookmatch.py`"* in prose. A mention counted as a dependency - the same mention-versus-invocation mistake the guards have made six times, now in the thing that decides what they depend on |
| after stripping `#` comments | still **17 of 18** | each leaf's own DOCSTRING opens *"Split out of `_hookmatch.py`"*, and a docstring is not a `#` comment. Stripped via `ast`, and only docstrings: other string literals stay, because `spec_from_file_location(..., "_ratchet.py")` is a real reference expressed as a string and dropping those would UNDER-run |
| after stripping docstrings | **3 of 18** | the split finally pays |

Final, guards only, against 21 of 21 for every shared file before the feature:

    _hm_make.py     3   (gate, make-only, pair)          _gatecost.py         2
    _hm_shape.py    3   (main-tree, measure, no-poll)    test_hooks_cases.py  3
    _hm_escape.py  17   - correct: every guard reaches its escape through `_guardlog.sh`
    _guardlog.sh   17   - correct, same reason

**The lesson, which is this repository's oldest one in a new place**: a dependency deriver has exactly
the same failure mode as a guard, and it is not "is the answer plausible" but "is the thing I am
matching an INVOCATION or a MENTION". Three of the four attempts above were plausible and wrong, and
only measuring the resulting blast radius told them apart.
