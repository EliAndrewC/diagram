# `tests/` - the diagram project's test bed

<!-- the engine's dev loop applies to test work too -->
@../l7r/diagram/CLAUDE.md

**No Python test is left here, and pytest is gone** (feature 449 FR-001b, the GM 2026-11-10: "Yes delete everything except that
group, please."; T211 deleted the last test, the pool sweep, now `rust/mode_a/src/pool_sweep.rs`; T213 retired pytest, its
configuration in `pyproject.toml`, its plugins in `requirements-dev.txt`, and the targets that ran it - `test`, `test-full`,
`test-file`, `durations`, `soak`). The tests are Rust: each crate's own, run by `make rust-test` (one crate: `CRATE=<dir>`) and by
`make static`'s coverage, 100% of a crate's lines owed by its own tests. The pytest trees this file once indexed (`tests/gate/`,
`tests/full/`, `tests/tooling/`, `tests/tier_*/`) and their rules are in git history (the tag `python-tests-before-removal`).

| path | what it holds | run by |
|---|---|---|
| `hooks/` | each guard's suite, `test-<guard>.sh`, replayed through its link to `l7r-guard`; the frozen command corpora in `hooks/fixtures/` | `make hooks-test` |
| `fixtures/` | the red sheets each Mode A check must fail (`*-red.svg`), the Rust fixture crate (`fixtures/rust/fixture`), the work-budget fixtures and the recorded inputs the Rust tests read | the crates' tests |
| `tooling/` | fixtures the gate crates' tests read (`fixtures/archive`, `fixtures/brief_load`, `_deps_site`); no test of its own since T133 | the crates' tests |
| `soak/` | the tier ABOVE the gate, declared and empty: [`soak/CLAUDE.md`](soak/CLAUDE.md) | nothing - its runner left with pytest |

## Running it

    make quick                                         # while iterating: ruff's outright errors, the fast tree checks
    make rust-test CRATE=rust/gate/crates/tree         # one crate's tests
    make hooks-test                                    # the guard suites
    make done                                          # the real gate: the static checks, the crates, the guard suites

A bare `cargo` is refused and named its make target (`rust/guard/src/guards/make_only_hooks.rs`).

## `tests/` is invisible to the generation cache, on purpose

The Rust generation cache (feature 449 T221, [`dev/cache.md`](../dev/cache.md)) keys a map on its engine's binary and the files the
engine reports reading, so a file here affects a map's key only if an engine reads it - and no engine should. (`render_cache`'s
fingerprint prunes this directory too, until T222.)
