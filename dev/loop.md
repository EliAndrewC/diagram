# The iteration loop: what to run, how much to re-run, and the remote runs

**Load this file when:** You are about to run the gate or a pool sweep, or you are deciding how much to re-run after a change.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md);
the ladder itself (`make quick` -> `make done`) is the root `CLAUDE.md`'s. What a test costs, how to read a timing on
this box, and the levers already withdrawn are in [`test-cost.md`](test-cost.md). Live costs are asked of the record
(`make audit`, `scripts/measure/gatecost.py <target>`), never typed here: prose cannot tell you it went stale.

## Iterate on the motivating map; let the cache skip the rest

Run the red/green loop against the ONE map (or fixture) that shows the defect, where cycles are cheap, and reserve
the whole gate for after that map is green:

    make map GEN=pool/hamlets/sawada/sawada.gen.py       # regenerate ONE gen and gate it; PROFILE=1 for per-stage time
    make cohort N=24                                     # roll N seeds of the hamlet tier, fanned out (JOBS=<workers>)
    make maps                                            # the pool, picking its own scope from how the last run went

`pipeline/regen.py` regenerates a map only if something that map depends on actually changed, and prints `CACHED`,
`REGENERATED` or (a frozen legacy map) `FROZEN`. Multi-map runs fan out across worker processes (`default_jobs` in
`sitegen/jobs.py` is the one definition of the cpus-minus-2 courtesy); parallelism cannot change a verdict (each map
is a pure function of its spec; `gencache.store` publishes atomically), and output is printed in order, so a
parallel run reads like a serial one. A whole-pool regen is an ITERATION convenience, never a pre-gate step: the gate
verifies the pool itself and render-sync regenerates main's renders from main's own tip
([`docs/iteration-loop.md`](../docs/iteration-loop.md) has the evidence).

**Score a perf change by A/B-ing the ONE map against HEAD**, never on the gate's total, which is a BUDGET that grows
with every rule for reasons unrelated to generator speed. Anti-pattern on record: using the full suite as the FIRST
check of an engine change - a failure that would have surfaced in ~6 s on one map surfaced 17 minutes in.

## NEVER re-run what `make done` just ran, and never beside it

- **A green `make done` already covers every test.** Re-running any of them "to be sure" buys nothing - the gate is
  the proof (one such re-run once cost 19% of a feature's wall clock). Re-run only what changed since it went green.
- **Do not run a test BESIDE the running gate** - not merely wasteful, but a source of false RED. Both runs
  regenerate the same live maps in the same tree, and a test that snapshots a manifest and reads it back read `b''`
  from a second writer mid-write (2026-08-16, feature 116). Determinism makes concurrent writers safe for the BYTES;
  it does not make them safe for a test that reads a file someone else is rewriting.

## NEVER poll a backgrounded command

A backgrounded Bash command NOTIFIES you when it exits: background the gate, spend the turn on the docs or the
commit message, and act on the notification. `no-poll-hooks.sh` enforces it (`docs/guards.md` has the rule and the
self-matching `pgrep` story). Keep the backgrounded command simple enough that its EXIT CODE is real -
`make done > <log> 2>&1` and nothing more: a wrapper ending in `; echo EXIT=$?` exits 0 whatever make did, and once
reported a red gate green. The log's tail is the authority; the notification is a summary of the wrapper.

## Before the gate, run the WHOLE affected test file - not a `-k` subset

A `-k torii` pre-gate check once missed the existing test the change broke and paid a whole extra gate round trip.
The whole files for the modules you touched reach every test the change can (`gate-hooks.sh` refuses a `-k` subset
as the only run before the gate):

    make quick                                        # lint, types, every test that rolls no map, change-selected
    make test-file FILE="tests/settlement/ tests/gate/"   # the files you touched, WHOLE
    make done                                         # once, backgrounded, not watched; reports every failure together

### Probe vs survey: when `-x` pays (GM 2026-08-15)

Every test run is one of two things, and fail-fast is right for exactly one of them:

- **A PROBE** - "did anything break?", and you will fix whatever surfaces one at a time. Fail fast (`make quick`
  stops at the first failure): the first failure arrives in seconds and you were going straight back to the code.
- **A SURVEY** - you need the failure SET to scope a problem: how far did this ripple, is this one bug or five?
  Run everything. The pattern of failures is the diagnostic.

The decision follows from RERUN COST: when a rerun is cheap, fail-fast costs nothing; when a rerun costs minutes, one
complete run beats N fail-fast runs. That is why `make done` stays report-everything (the GM's 2026-07-25 decision -
every phase runs, all failures report together, fix them all, re-run once). A fail-fast run that fails says nothing
about the tests it never reached, so it never substitutes for the whole-file pass before the gate.

## Update the predictably-affected tests in the SAME edit

Touching a `settlement/` method breaks its unit tests deterministically - you know which ones before you run
anything. Changing `channel_footbridges`' placement semantics (e.g. "a plank now needs cultivation on both banks")
means its `tests/settlement/` setups need cultivated ground added. Update them in the same turn as the engine change;
grep for the method name in `test_*.py` before editing.

## Converge on a new rule with ONE pool-wide dry run, not one variant per turn

When adding a placement rule, the pool IS the test bed: the right predicate flags exactly the defective features and
spares every good one across all maps. Write ONE script that loads every pool manifest and, for each candidate
predicate, prints what each would drop or keep per map - then read it once and pick the winner. This is how the
footbridge rule's edge cases (polder toe-planks crossing onto the DIKE, village-edge planks, dry-to-wet crossings)
surfaced in one pass instead of five. And ask every overlap question in both directions, with one shared
implementation: a VERTEX-only test misses what passes BETWEEN the vertices (a stream between a farmhouse's corners).

## The paired gate

`make verify` starts the gate and the settlement-review together, and `pair-hooks.sh` refuses either alone
(`PAIR_OK="<reason>"` takes a one-sided case and logs it) - the review dispatched from memory, LAST, once cost a
17-minute wait at the end of a fix (feature 151).

## The remote runs (CodeBuild): when they are used

**The remote can be OFF** (`make ci-off REASON=...`, released by `make ci-on`; [`docs/switches.md`](../docs/switches.md)):
then nothing here dispatches, `make ci-status` shows `remote-enabled` failing first, and the gated push lands on a
green local `make done` instead (LOCAL-GATED).

**A session does not decide whether to go remote - the conditions do.** `make ci-status` prints them, free, every
one even after the first fails: the delta has engine code; on a merge, the named spec-kit feature is complete; the
last recorded verification is a GREEN local target against EXACTLY this code (a red gate or a source edit since
resets it - run `make quick`); the tree the merge would produce is not already verified by a build; the monthly hard
stop has not tripped.

**Every remote target runs the same ladder**: lint/format/types locally (fail -> nothing touches AWS) -> the build
starts and PARKS -> the local reference roll -> red: the parked build is stopped (`run-log` records
`aborted-local-reference`) | green: the build is released, merges the LATEST GitHub main into the work, runs its
target, and on green writes `verified/<tree>.json`. The log streams into the command's output and the command exits
with the build's status - background it and act on the notification.

| target | what it runs remotely | prompts? |
|---|---|---|
| `make ci-check` | the soak suite (`TARGET=<op>` for another expensive operation, e.g. `cohort`; its report comes back under `dev/ci-artifacts/<build>/`) | no; `FULL=1` yes |
| `sync-with-main.sh done` on a GATED delta | `make ci-merge`: the soak suite, then the build fast-forward-pushes the merge to GitHub main | no; `FULL=1` yes |
| `make ci-measure` | what the remote gate costs, optionally on another `COMPUTE` size | yes |
| `make ci-image` | docker-builds `Dockerfile.ci` on CodeBuild and pushes it to ECR | **yes** - the GM's |

**A green local `make done` followed by `sync-with-main.sh done` is free** when main has added no engine content
since your merge base (the local verdict IS the remote one then - GM 2026-08-25); likewise a green `make ci-check` on
the same engine content (SKIP-VERIFIED). **What stays local, always**: `quick`, `test-file`, `durations`, `maps`, a
plain `make done`, every read-only diagnostic.

**Cost is visible before and after**: the pre-dispatch printout carries the estimate and the month-to-date; `make
audit` sums a "Remote spend" block from `dev/run-log/` entries with `where: codebuild` (never from Cost Explorer,
which costs money to ask). The account-side budgets and the hard stop are described in
`specs/130-codebuild-merge-gate/spec.md` and are not repo code.
