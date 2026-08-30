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

## R5 - the final numbers, and one more under-run the tests caught

After the split, comment/docstring stripping, and one more fix, the guard-only blast radius:

| shared file | guards | before the feature |
|---|---|---|
| `_hm_make.py` | **3** (gate, make-only, pair) | 21 |
| `_gatecost.py` | **2** | 21 |
| `test_hooks_cases.py` | **3** | 21 |
| `_hm_shape.py` | 17 | 21 |
| `_hm_escape.py` | 17 | 21 |
| `_guardlog.sh` | 17 | 21 |

This is exactly the outcome predicted to the GM before the work started: the make/rewrite family drops
to three, and the shape family stays wide **because the escape family stands on it and every guard
reaches its escape**. No arrangement of files changes that, which is why the feature also parallelizes.

**The last fix was an under-run my own test caught, and it is the sharpest instance of this feature's
lesson.** `_hm_escape.py` imports `from _hm_shape import _strip_quotes` - and a Python import NEVER
writes the extension, so a filename match could not see it. The deriver reported `_hm_shape.py` as
depended on by 3 guards when the true answer is 17: it would have skipped fourteen suites that a
change to the shape primitives can break. Created by this feature's own split, in the feature built to
prevent exactly that, and caught only because FR-004 demanded an assertion on the transitive case.

## R6 - what parallelism actually bought

Measured on this clone, same content, every suite forced stale:

    serial    194 s   (21 of 21 green)
    parallel   63 s   (21 of 21 green)   HOOKS_JOBS=8 on a 22-core box

3.1x. Not the theoretical 8x, because the suites are uneven - the slowest few dominate the wall clock
once the rest have finished, and two of them (`test-sync-with-main.sh`, `test-clone-sync-hooks.sh`)
build real git trees. Raising `HOOKS_JOBS` past 8 cannot beat the longest single suite.

## R7 - the split dropped two constants, and the equivalence test did not catch it

`hooks-test` went red on five suites after the split: every escape that needed a REASON was refused,
because `_REASON_WORDS, _REASON_CHARS = 2, 8` never made it into `_hm_escape.py`. The splitter
selected top-level nodes by name and its `name_of` handled only single-`Name` targets - a TUPLE
assignment returned None and was silently skipped.

**Two safeguards were in place and neither caught it**, which is the part worth recording:

- the 320-comparison equivalence check compared `escape_used` and `escape_reason` against the
  pre-split module - but not `reason_is_enough`, which is the one function that reads those constants.
  A function-by-function equivalence check is only as complete as its function list.
- the leaves all PARSED, because a name defined nowhere is a runtime `NameError`, not a syntax error.

What did catch it: running the suites. The audit that should have run alongside the split is the one
run afterwards - compare the set of top-level NAMES in the original against the union of the leaves,
which reported exactly `['_REASON_CHARS', '_REASON_WORDS']` and would have taken ten seconds before
the first suite ever ran.

**The rule for the next mechanical split**: assert that the union of the parts defines every name the
whole defined, before trusting any behavioral comparison. Behavior tests check the paths you thought
of; a name census checks the ones you did not.

## R8 - the parallel collector's reporting was verified by an accident

FR-002 requires that a parallel run still report **every** failure together, with the suite that
produced each - the property the serial loop had. That was verified by the run that went red when the
split dropped its two constants: twelve suites failed at once, and the collector listed all twelve in
one line with each suite's own output beneath its own heading.

    hooks-test FAILED: clone-sync-hooks.sh discard-hooks.sh gate-hooks.sh guard-file-hooks.sh
    main-tree-hooks.sh make-only-hooks.sh measure-hooks.sh no-branch-hooks.sh no-poll-hooks.sh
    repo-safety-hooks.sh review-gate.sh source-block-hooks.sh

A deliberate fixture would have planted one failure; the accident planted twelve, concurrently, which
is the stronger test of a fan-out collector - it proves the per-job log and exit-code files do not
collide under load, which is the failure a single planted failure could not have shown.

## R9 - the success criteria understated the cost, and the incremental run said so

SC-002 and SC-003 were written from the derivation alone: `_gatecost.py` reaches two guards, the
make/rewrite family three. A real incremental run - append a comment, run `hooks-test`, revert -
reports **5** and **6** of 21.

The difference is the three whole-tree suites (`sync-with-main.sh`, `review-gate.sh`,
`gate-stamp.py`), which re-run for ANY script change and always will: two are held there deliberately
because they resolve script paths at run time, and one derives there because it reads the whole
directory. That trio is a constant on every targeted change, and criteria that ignored it were
quietly wrong in the flattering direction.

Corrected to the measured figures. The win is undiminished and worth stating in its true form: **5 of
21 instead of 21 of 21**, and the three that always run are three of the slower ones, which is a real
part of what a targeted change still costs.

### R9 addendum - those figures were superseded by round 3, the same day

R9's 5 and 6 were measured while `review-gate.sh` was still held whole-tree. Round 3 measured the
justification false of it - it reaches exactly two scripts, both statically visible - so it derives
now, and the constant on every targeted change is TWO entries rather than three:

    _gatecost.py       4 of 21     (2 consumers + sync-with-main.sh + gate-stamp.py)
    make/rewrite       5 of 21     (3 guards + the same two)
    _guardlog.sh      20 of 21     - and this is the number that must NOT fall

The measurement in R9 is left standing rather than overwritten, because it was true of the tree it was
taken on and the correction is the more useful record: a number in a document is only ever true of a
version of the code, and this one lasted about an hour.
