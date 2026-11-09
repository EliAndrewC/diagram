# `l7r/diagram/ci/` - the CodeBuild dispatcher (feature 130)

**Load this when:** a remote run refused and you want to know why, you are changing when a paid
run may start, or you are touching the buildspecs. The usage-level answer is one command:
`make ci-status` prints every condition and its reason, free, with no AWS call on a DIRECT route.

**A remote run runs `make soak`, not `make done` (GM 2026-09-05).** `sync-in` merges main into every clone on every
message, so the remote's old job - re-running the gate against your work merged with the latest main - almost never
saw a tree the laptop had not, and condition 4 declines to pay when the trees match. So the remote does the tier the
laptop SKIPS: [`tests/soak/`](../../../tests/soak/CLAUDE.md), the same code over many seeds and larger, more realistic
maps. **Accepted in exchange: the remote is no longer a MERGE QUEUE** - a conflict that is textually clean but
semantically broken is not caught by a machine before it lands (it never once fired). `make soak` REFUSES on an empty
suite rather than reporting a vacuously green build. **Remote is OFF** - `make switches`.

Every remote run costs money (`RATE_PER_MIN` = **$0.02 per build-minute** on `BUILD_GENERAL1_LARGE`,
in `rust/gate/src/ci/config.rs` - mirrored in exactly one other place, the `gm-assistant-ci-monthly-alert`
Lambda's `RATE_PER_MIN` environment variable; change both together). So the GM's rule for this
package is stricter than for any other: *"all of the situations in which we absolutely, positively
do not want to run anything on AWS"* come first, and the speedup second.

## The modules

| module | what it is for |
|---|---|
| [`delta.py`](delta.py) | the Python callers' door to the delta in the Rust gate (feature 449 T063): `rust/gate/src/delta.rs` holds the Delta (what OUR commits changed since the merge base with `origin/main`, R1), `is_engine` - **the one list** of engine paths (FR-008): `l7r/**/*.py`, `pool/*.gen.py`, `pool/*.json`, the Rust sources - the code the tests exercise and nothing that merely shapes how the gate runs (GM 2026-08-25); **not `tests/`** since feature 132 FR-024 and **not this `ci/` package** since FR-025 - and `engine_key`, the verification key; `tests/tooling/ci/test_delta.py` pins every path kind |
| [`state.py`](state.py) | the Python callers' door to the VerificationState in `rust/gate/src/state.rs` (`.git/verification-state.json`: the last local check, its target, and the content hash at that moment, the stamp's own) |
| [`incremental.py`](incremental.py) | THE INCREMENTAL GATE (feature 207): the baseline (the last full run's coverage with per-test and per-fixture contexts + a raw-bytes manifest, under `<git dir>/gate-baseline/`), the plan (which tests a change can reach; the six fallbacks to a full run), the merge (the pruned baseline unioned with this run), `carry` (a full run's reused tooling tests' coverage, from the baseline - feature 383 amendment 5), `save-baseline`. The soundness argument is its docstring |
| [`selection.py`](selection.py) | the pytest plugin the gate loads (`-p l7r.diagram.ci.gate_plugin`, an excluded two-hook shim, because a `-p` module loads before coverage starts): switches the coverage context to `fixture:<name>` around every fixture setup, deselects what the plan says (identically on every xdist worker), writes the run's result and the fixture dependency graph from worker `gw0` |
| [`gate_plugin.py`](gate_plugin.py) | the incremental gate's `-p` entry: a tiny shim, because a `-p` module is imported before pytest-cov starts measuring; its hooks delegate to `selection.py` |
| `rust/gate/src/exempt.rs` | the engine code the Rust port replaces, exempt from the coverage floor (feature 448, the GM 2026-11-02): the one reader of `dev/coverage-exempt.json` every floor asks (`l7r-gate coverage-exempt omit`, `report`, `cover_changed.py`, `make land`); a stale entry refuses with `make coverage-exempt PRUNE=1` |
| [`__main__.py`](__main__.py) | `incremental`, with `assert_via_make` at the top, until T071 |
| `rust/gate/src/ci/` | `make ci-status`, `ci-check`, `ci-merge`, `ci-measure`, `ci-image`, `make switches`: the conditions (`decision.rs`), the sequence (`dispatch.rs`), the AWS boundary (`aws.rs`, the `aws` CLI; **unproven until the first paid run after remote is turned on**), the constants and secrets (`config.rs`), the run log (`runlog.rs`), the build-side door (`door.rs`), the feature check (`features.rs`), the image check (`imagecheck.rs`), the bucket's lifecycle document (`cachepolicy.rs`, `l7r-gate lifecycle`) |

## The conditions, and the GM's words each rests on

0. **remote-enabled** (feature 132, printed first) - `dev/switches.json` says remote is on. *"if it
   is disabled, then we do not use it as a gate. and we do not dispatch to it while we are doing
   iteration."* With remote OFF nothing dispatches: `check` and `image` refuse before a client is
   built, and `merge` becomes LOCAL-GATED - the other conditions are still judged, and the verdict
   is SKIP-VERIFIED only when a green local `make done` vouches for the merged engine content
   (condition 4's local rule); otherwise `REFUSE(remote-enabled)` and the work stays in the clone.
   Thrown and released by `make ci-off` / `make ci-on`, which commit; no variable overrides it.
   The doctrine: [`../../../docs/switches.md`](../../../docs/switches.md).
1. **route-is-gated** - our delta touches engine code. *"if we make any updates that are only outside
   of the diagram skill, then we do not want to run anything on AWS ... even if the diagram
   documentation was touched, but not the code itself, then we should not rerun the tests."* The
   delta is what THIS clone's commits changed, *"paying careful attention to make sure it is
   actually our work and not the result of what we have merged from main into our branch."*
2. **feature-complete** (merge only) - a named spec-kit feature with no open task and a FAITHFUL
   spec. *"I don't think we want things to land on Maine if the feature is incomplete ... Anything
   involving the diagram skill is sufficiently complicated to require a spec kid feature."*
3. **green-local-since-edit** - the last recorded verification is a green local target against
   exactly this code. *"make done could check whether the last thing that was run was an
   unsuccessful make done, in which case it should just short circuit immediately and refuse to
   run without even dispatching to AWS."* A source edit after the green run also refuses (the
   Assumptions reading in the spec: the green run vouched for different code).
4. **tree-not-already-verified** - a green build already verified the ENGINE CONTENT the merge
   would produce, so no second build. *"we can keep track of whether the commit hash that will land
   on main has already had a successful remote run ... This saves both time and money."* Keyed by
   the engine key (`delta.engine_key`: a hash over the engine paths' blobs in the merge tree),
   not by the commit and - since 2026-08-25 - not by the whole tree either: a docs edit after a
   green build keeps the verification (the first day's tree key threw one away, $0.64).
   And a green LOCAL `make done` on exactly this engine content counts too, when main adds no
   engine content to the merge (GM 2026-08-25): the remote reference gate is the same `make done`
   plus the merge, so with nothing new from main it would only re-prove a verdict in hand. A build
   runs when main moved on engine paths since your merge base, or for FULL / an operation.
5. **breaker-not-tripped** - the monthly hard stop's deny policy; discovered at `start_build`,
   reported with the detach command (FR-021).

## The measurement route, the threat model and the `verified/` write path

`make ci-measure` bypasses `route-is-gated` alone and cannot mint a push credential; the threat model every condition
answers; and the bucket policy that lets only a build write `verified/`: [`dev/ci.md`](../../../dev/ci.md).

## The sequence (every remote target)

    conditions -> lint/format/types locally -> push mailbox, start_build (build PARKS at wait-go)
      -> make _reference locally -> red: stop_build(OUR id) | green: put go/<id> -> stream -> record

The build parks for at most `PARK_TIMEOUT_S` (120 s, ~$0.04) if the dispatcher dies (FR-036). A
started build that is stopped costs its partial minute; a queued one costs nothing. Only the id
this dispatcher got back is ever stopped - nothing on the AWS side is shared between sessions;
the merge project's single slot serializes merges, and the local sync lock is the only shared
local state.

## What travels to the build, and how

The projects hold a placeholder buildspec. The dispatcher passes the repository's own
[`buildspec/<mode>.yml`](../../../buildspec) as `buildspecOverride`, so the build runs
whatever the tree under test says - reviewable in a diff. Both YAMLs call
[`buildspec/run.sh`](../../../buildspec/run.sh); `MODE` (check | merge) is the only
difference: merge fast-forward-pushes the verified result to GitHub `main` and deletes the mailbox.
The custom image (`Dockerfile.ci`, `make ci-image`) is used once its marker `image/latest.txt`
exists in the bucket; until then the build bootstraps Python 3.14 + resvg on the stock image
(measured in `dev/timings.md`).
