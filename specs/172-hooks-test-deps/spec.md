# Feature 172 - `hooks-test` Costs What It Should

**Status**: **APPROVED** 2026-08-30 - `spec-fidelity` round 4 returned FAITHFUL, having verified every
stated number against the tree with the deriver itself rather than accepting them. Specified 2026-08-30. [`request.md`](request.md) is the authority;
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
short-circuit (a different mechanism, already working); the perf ratchets of feature 171; and **the
Python test suite** - the other of the GM's *"those two of the slowest tests"*, which this feature
deliberately does not serve and which belongs to the efficiency work.

## Requirements

### FR-001 - the dependency set is DERIVED, and transitively

Each suite's dependency set is computed from what its guard and its own test file actually reference,
followed transitively through the shared helpers - shell references (`. _guardlog.sh`,
`"$X/_hookmatch.py" mode`) and Python imports alike. A suite re-runs when anything in ITS set changed
and not otherwise.

**The set of shared helpers is itself DERIVED** - every `_*.py` / `_*.sh` in `scripts/` plus the shared
test runner - not a list. Round 2 caught the first implementation propagating a hardcoded five-name
roster, which the split's own three new leaves were invisible to: a guard calling a leaf directly
would have re-run ZERO suites when that leaf changed. A hardcoded list of shared files, in the feature
whose subject is deriving instead of listing.

**And a MENTION is not a dependency.** The graph is read from CODE, not raw text: `#` comments go, and
in Python so do docstrings (via `ast`, docstrings only - other string literals stay, because
`spec_from_file_location(..., "_ratchet.py")` is a real reference expressed as a string). Without
this the split delivered nothing at all, because this repository comments heavily and nearly every
guard NAMES `_hookmatch.py` in its prose. Measured at each stage in `research.md` R4.

**Transitive is not optional and is the whole subtlety.** `_guardlog.sh`'s `escape_or_refuse` calls
`_hookmatch.py` (feature 170), so a guard that names only `_guardlog.sh` depends on `_hookmatch.py`
whether it says so or not. A direct-reference-only derivation would under-run and pass a suite that a
change had broken - which is worse than today's over-running, because today's is merely slow.

**Whole-tree is an OUTPUT of the rule where it can be, and a STATED LIMIT where it cannot.** Round 1
caught the first draft preserving three rows by hand - a carve-out asserted rather than derived, which
would keep for those three exactly the over-running the GM asked to end. Measured:

- **`gate-stamp.py` DERIVES to the whole tree**, by a text match on the path glob AS THE CODE WRITES
  IT - `("scripts", ("*.sh", "*.py"))` - and is pinned by a test. Round 2 caught the first version
  matching only the literal `scripts/*.sh`, which in that file appears solely in its DOCSTRING: the
  row was true by accident of wording, and a reword would have dropped the suite from 56 files to 4.
- **`sync-with-main.sh` ALONE is held there deliberately**, and the reason is a LIMIT OF
  REFERENCE-GRAPH DERIVATION rather than a preference: its suite exercises the push path end to end,
  and that path resolves script paths at RUN TIME from `$ROOT` and `$MAIN` against trees the fixture
  builds. It names 11 siblings and reaches more. Over-running one suite is the safe side of an edge
  the derivation cannot see.
- **`review-gate.sh` WAS held under that same sentence, and round 3 measured the sentence false of
  it**: it reaches exactly two scripts, both statically visible, and its suite drives only itself -
  everything else it touches is DATA, which a hold over `scripts/` does not cover anyway. One
  justification stretched over two unlike things, keeping for that suite exactly the over-running this
  feature exists to end. It derives now, to five files.

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
family, the make/rewrite family. Guards invoke the module they use directly - all of them, including the two
`classify` call sites that round 3 found still going through the umbrella - because a split behind an
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
guard reaches a helper only THROUGH another helper still depends on it; that every shared helper ON
DISK is reachable by the deriver (so a new leaf cannot be invisible to it); and that `gate-stamp.py`
still derives to the whole tree. A derivation that silently
under-runs is the one failure mode that matters here.

## Success Criteria

- **SC-001**: with nothing changed, `hooks-test` still reports every suite unchanged and costs ~0 s.
- **SC-002**: **stated over the whole 21-entry roster, which is the unit the tooling reports in.** Touching `_gatecost.py` re-runs **4 of 21** - its 2 real consumers plus the 2 whole-tree entries (`sync-with-main.sh`, `gate-stamp.py`) that re-run for ANY script change and always will. `test_hooks_cases.py`: **5 of 21**. Round 3 caught the first version stating a guards-only figure that the tooling never reports, so a reader checking it would have concluded the feature missed its own criterion.
- **SC-003**: touching the make/rewrite module re-runs **5 of 21** - the 3 guards that use it (`gate`, `make-only`, `pair`) plus the same 2 whole-tree entries.
- **SC-004**: touching `_guardlog.sh` still re-runs **20 of 21**, and `_hm_escape.py` likewise - the derivation must NOT get these "right" by under-running. This is the number that must NOT fall.
- **SC-005**: a full `hooks-test` (every suite stale) is measurably faster than the same set run serially, measured on the SAME content in this clone rather than against a figure from another session's run - and reports every failure together as it does today. Measured: **194 s serial, 63 s parallel**, all 21 green both ways.
- **SC-006**: every suite that runs concurrently has been checked for shared state; any that cannot is serialized with its reason recorded.
- **SC-007**: `make hooks-test` and `make done` green, and no suite's assertions changed.
- **SC-008**: the command-shape module, which after the split both other families depend on, is named as having the widest blast radius of the three - the first draft noted this for the escape family only.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| the GM's stated rationale is not supported, and the feature leads with parallelism instead | measured before building; put to the GM, who accepted | Why / research R2 |
| the derivation is TRANSITIVE | a direct-only derivation under-runs, which is worse than over-running | FR-001 |
| split by cohesion into three, not per function | the closure through shared primitives dominates past that | FR-003 |
| a flaky parallel suite is SERIALIZED, never retried | a retry hides a race behind a green result | FR-002 |

## Review history

Constitution XVI: reviewed against [`request.md`](request.md) by an independent `spec-fidelity`
subagent, up to five rounds. **Four rounds; FAITHFUL at round 4.**

| round | verdict | what it found |
|---|---|---|
| 1 | CHANGES REQUIRED | `request.md` carried only two of the four GM messages, so FR-002 and FR-003 had NO authorizing GM words in the file the spec calls its authority - the gap was covered by the session's paraphrase. It went to the transcript to find them and noted the acceptance existed in exactly one place, which is not a durable record. Also: FR-003 split one of the GM's "those two files" without saying why the other was left, and three whole-tree rows were preserved by hand |
| 2 | CHANGES REQUIRED | the deriver propagated a HARDCODED five-name roster - in the feature about deriving - so the split's own three leaves were invisible and a guard calling a leaf would have re-run ZERO suites. And `_globs_tree` matched only the literal `scripts/*.sh`, which in `gate-stamp.py` appears solely in its DOCSTRING, making that row true by accident of wording |
| 3 | CHANGES REQUIRED | `review-gate.sh` was held whole-tree under the sentence written for `sync-with-main.sh` - measured, it reaches exactly two scripts, both statically visible, so one justification had been stretched over two unlike things, keeping for that suite the over-running this feature exists to end. And the success criteria were stated in a guards-only unit the tooling never reports |
| 4 | **FAITHFUL** | verified all five stated numbers against the tree with the deriver, and confirmed the two `classify` call sites really do reach the leaf. Four RECORD defects, all fixed before the push: `--all` had silently lost a suite when round 3 changed the held set; `CLAUDE.md`, a test docstring and research R9 all carried the superseded 5-and-6 figures |

**One item was DECLINED after verification**: round 2 asked for the review cap to be changed from five
back to three. The GM raised it to five on 2026-08-30 and both the constitution and `CLAUDE.md` say
five, in this clone and on main - the reviewer was reading the rule as it stood before the change.
