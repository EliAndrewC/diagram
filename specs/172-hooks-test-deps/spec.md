# Feature 172 - `hooks-test` Costs What It Should

**Status**: specified 2026-08-30. [`request.md`](request.md) is the authority;
[`research.md`](research.md) holds the measurements taken BEFORE specifying, which reshaped it.

## The feature, in one sentence

`hooks-test` re-runs only the suites a change can actually affect, and runs those in parallel.

## Why this exists (the GM's words)

*"could we not do something similar where if the hooks have not changed, then we do not run the hooks
tests? that feels like the obvious thing to do"* - and, on being shown that this exists and costs 0 s
while the per-suite dependency set is too coarse: *"Go ahead and do the dependency refinement as its
own feature. That seems worth doing as it would have paid off a lot over the last couple of days."*

Then, on whether the shared files could be split so the dependency graph is finer: *"am I correct in
thinking that we would also be able to potentially break up those two files? ... I'm not saying that we
should go so far as to put every single function or bit of functionality which we define into its own
separate file... Though that would presumably make this kind of efficiency gain much easier. Right?
What do you think about that?"* The session answered with the measurement below and a
three-part proposal; the GM accepted it in those words: *"Yes. I think that doing both sounds
helpful"*, and then *"I accept your proposal, so please proceed with that for feature 172."* Both are
now in `request.md`, which round 1 found carried neither - so two of the three parts had no
authorizing GM words in the authority document and rested on this paraphrase instead.

## What was measured before specifying (details in `research.md`)

| finding | result |
|---|---|
| does the skip exist? | YES, and costs **0 s** with nothing changed: *"0 guard suites green, 21 unchanged"* |
| would the refinement have paid off over the last days? | **NO** - the dependency is TRANSITIVE (`_guardlog.sh` calls `_hookmatch.py` since feature 170), so the two helpers this session edits constantly derive to **20** and **19** of 21. One and two suites saved |
| where it DOES pay | `_gatecost.py` 21 -> **2**; `test_hooks_cases.py` 21 -> **3** |
| where the 94 s actually is | 21 suites run SERIALLY, against 17 s for the entire 2,286-test Python suite, which runs in parallel |
| how `_hookmatch.py` usage partitions | three families: escape (~all 19 guards, via `_guardlog.sh`), command-shape (3 guards), make/rewrite (3 guards) |

**The GM's stated reason for the feature is not supported by the measurement, and that is recorded
rather than quietly inherited.** It was put to them before any code was written; they accepted a
proposal that leads with the part the measurement points at.

## Scope, stated exactly

**IN**: the three parts below. **OUT**: changing what any suite ASSERTS; the `make done` engine-key
short-circuit (a different mechanism, already working); the perf ratchets of feature 171.

## Requirements

### FR-001 - the dependency set is DERIVED, and transitively

Each suite's dependency set is computed from what its guard and its own test file actually reference,
followed transitively through the shared helpers - shell references (`. _guardlog.sh`,
`"$X/_hookmatch.py" mode`) and Python imports alike. A suite re-runs when anything in ITS set changed
and not otherwise.

**Transitive is not optional and is the whole subtlety.** `_guardlog.sh`'s `escape_or_refuse` calls
`_hookmatch.py` (feature 170), so a guard that names only `_guardlog.sh` depends on `_hookmatch.py`
whether it says so or not. A direct-reference-only derivation would under-run and pass a suite that a
change had broken - which is worse than today's over-running, because today's is merely slow.

**Whole-tree is an OUTPUT of the rule where it can be, and a STATED LIMIT where it cannot.** Round 1
caught the first draft preserving three rows by hand - a carve-out asserted rather than derived, which
would keep for those three exactly the over-running the GM asked to end. Measured:

- **`gate-stamp.py` DERIVES to the whole tree.** It reads `scripts/*.sh scripts/*.py`, so the rule
  "a file that reads the whole directory depends on the whole of it" picks it up with no special case.
- **`sync-with-main.sh` and `review-gate.sh` are held there deliberately**, and the reason is a LIMIT
  OF REFERENCE-GRAPH DERIVATION rather than a preference: their suites exercise the push path end to
  end, and that path resolves script paths at RUN TIME from `$ROOT` and `$MAIN` against trees the
  fixture builds. A static reader cannot see which scripts a run will reach - `sync-with-main.sh`
  names 11 siblings and reaches more. Over-running two suites is the safe side of an edge the
  derivation cannot see, and they are among the slowest, which is exactly why it is said out loud
  rather than quietly narrowed.

### FR-002 - the suites run in PARALLEL

`hooks-test` runs its suites concurrently and reports exactly as it does now: every failure, together,
with the suite that produced it. This is the requirement that addresses the 94 s.

**Safety is to be VERIFIED, not assumed.** The argument that it is safe is that each suite builds its
fixtures in its own `mktemp -d` and, since feature 170, isolates its own `GUARD_LOG_DIR`. That is an
argument, not a proof: `test-sync-with-main.sh` and `test-clone-sync-hooks.sh` drive real git trees,
`test-idle-tests-hooks.sh` takes a host-wide lock, and any suite writing to a fixed path outside its
own temp directory will collide. Each suite is checked for shared state before it is allowed to run
concurrently, and one that cannot be is run serially with the reason recorded at the point of change.

**A parallel run must not become a flaky run.** If concurrency makes any suite intermittent, that
suite is serialized rather than retried - a retry hides a real race behind a green result.

### FR-003 - `_hookmatch.py` is split by COHESION, and guards call the LEAF

Into three modules along the families the measurement found: the escape family, the command-shape
family, the make/rewrite family. Guards invoke the module they use directly, because a split behind an
umbrella that imports everything changes no dependency set at all - the closure is what matters, not
the file count.

**Not one function per file**, which the GM raised and the measurement argues against: the closure
through shared primitives dominates, so past cohesion you add files without shrinking any blast
radius. The project's own file-size doctrine agrees - it asks the package question at ~1,000 lines and
`_hookmatch.py` is 574 - so this split is justified by the dependency argument alone, and that
argument runs out at about three modules.

**`_guardlog.sh` - the second of the GM's "those two files" - is deliberately NOT split**, and the
spec says so rather than leaving a reader to wonder whether it was forgotten. It is **98 lines**
against `_hookmatch.py`'s 574, and it is one cohesive thing (record what a guard did; decide an
escape). Splitting it would add a file and shrink no blast radius: every guard that sources it uses
`guard_log`, and `escape_or_refuse` is what pulls in `_hookmatch.py` for all of them. The dependency
argument that justifies splitting the larger file does not reach the smaller one.

**What this cannot fix, stated so nobody expects it to**: the escape family is used by ~all 19 guards
and depends on the shape primitives, so escape-family churn keeps a ~20-suite blast radius however the
file is cut. FR-002 is the only thing that helps there.

### FR-004 - the derivation is checked, not trusted

A test asserts the derived set against the real reference graph, and specifically that a suite whose
guard reaches a helper only THROUGH another helper still depends on it. A derivation that silently
under-runs is the one failure mode that matters here.

## Success Criteria

- **SC-001**: with nothing changed, `hooks-test` still reports every suite unchanged and costs ~0 s.
- **SC-002**: touching `_gatecost.py` re-runs 2 suites, not 21; touching `test_hooks_cases.py` re-runs 3.
- **SC-003**: touching `_hookmatch.py`'s make/rewrite module re-runs the 3 guards that use it, not 21.
- **SC-004**: touching `_guardlog.sh` still re-runs ~19 - the derivation must NOT get this "right" by under-running.
- **SC-005**: a full `hooks-test` (every suite stale) is measurably faster than the same set run serially, measured on the SAME content in this clone rather than against a figure from another session's run - and reports every failure together as it does today. Measured: **194 s serial, 63 s parallel**, all 21 green both ways.
- **SC-008**: the command-shape module, which after the split both other families depend on, is named as having the widest blast radius of the three - the first draft noted this for the escape family only.
- **SC-006**: every suite that runs concurrently has been checked for shared state; any that cannot is serialized with its reason recorded.
- **SC-007**: `make hooks-test` and `make done` green, and no suite's assertions changed.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| the GM's stated rationale is not supported, and the feature leads with parallelism instead | measured before building; put to the GM, who accepted | Why / research R2 |
| the derivation is TRANSITIVE | a direct-only derivation under-runs, which is worse than over-running | FR-001 |
| split by cohesion into three, not per function | the closure through shared primitives dominates past that | FR-003 |
| a flaky parallel suite is SERIALIZED, never retried | a retry hides a race behind a green result | FR-002 |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent, up to five rounds.
