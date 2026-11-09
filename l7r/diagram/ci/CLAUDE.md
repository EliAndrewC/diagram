# `l7r/diagram/ci/` - the incremental gate

**Load this when:** the gate selected oddly, or a gated push refused and you want to know why (`make ci-status` prints the route and
every condition). The remote test path that was here was deleted, not ported (feature 449 FR-001a; the GM, 2026-11-09: "Let's delete
rather than port our tooling which runs our tests remotely on AWS.").

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
| `rust/gate/src/ci/` | `make ci-status`, `make gated-check`, `make switches`: the route and a gated push's conditions (`gated.rs`), the feature check (`features.rs`), the switches, the push's credential (`config.rs`) |

## A gated push's conditions, and the GM's words each rests on

1. **feature-complete** - a named spec-kit feature with no open task and a FAITHFUL spec. *"I don't think we want things to land on Maine if the feature is incomplete."*
2. **green-local-since-edit** - the last recorded verification is a green local target against exactly this code.
3. **merged-engine-green** - a green local `make done` on exactly the engine content the merge lands (GM 2026-08-25), keyed by the engine key, so a docs edit after a green run keeps it.
