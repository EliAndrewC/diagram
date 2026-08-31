# Feature 174 - the plan, after the spec review and the GM's cheap-tests question

Written 2026-08-31, replacing the first spec's scoping. Two things changed it: `spec-fidelity`
returned CHANGES REQUIRED with seven items (the review is summarized in `spec.md`'s history), and the
GM asked a question that reframes the whole feature.

## The GM's question, and the answer

> I wonder whether we are able to reach one hundred percent code coverage on make done with a less
> expensive version of the tests even if what we would be testing is less valuable than the full
> tests ... understanding that one hundred percent code coverage is different from the kind of end to
> end testing, which is being done in the full tests, which is more valuable and will catch more
> actual bugs.

**Yes, and the distinction they draw is exactly the right one.** Coverage needs each line executed
ONCE; the full tests' expense is VARIETY - many hamlets, many seeds, uncached regeneration - which
buys bug-finding, not coverage. The proof is this feature's own first day: **64 statements closed
with plain-input unit tests, zero map rolls, milliseconds each**, including 24 town/city statements
the first draft had called uncoverable.

## What the review corrected, and what the session had told the GM wrongly

| claim | truth |
|---|---|
| "99.28%, 89 statements to close" | that is the HAMLET PATH alone. The whole measured set is **96.07% - 814 of 20,703** |
| "the hard 100% floor already passes over 88 files" | it FAILS: `Coverage failure: total of 99 is less than fail-under=100`, **54 missing** in the modules it already governs |
| "the scope lock deselects the map-rolling tests from `make done`" | the scope has been **unlocked since 2026-08-27**; both deselections are gated on `scope == reference` and are inert |
| "you cannot cover code no generator produces" | disproved by this feature's own commits - 24 town/city statements closed by unit test |

## The four buckets, measured

| bucket | statements | route |
|---|---|---|
| the hamlet path's remainder | **25** | unit tests; 4 need constructed geometry, the rest are branch guards |
| the existing hard floor's own misses (`ci/`, `switches.py`, `pool_index.py`, `scatter_audit.py`, `pack_audit/__main__.py`) | **54** | unit tests; several are CLI entry points and `__main__` guards |
| the four exempt trees (`settlement/`, `waterfields/`, `interactive/`, `overlap/`) | **760** in 28 files | mostly unit-testable; see the two special cases below |
| **DEAD CODE, not untested code** | **99** | `waterfields/hill.py` - see below |

### `waterfields/hill.py` is dead, and that is a finding rather than a coverage task

Its two engines, `build_terraces` and `build_ribbon`, are called by **nothing**: no generator, no
test, no other module - only a name-census list in `tests/waterfields/test_surface.py`. `hill.py`'s
own docstring says so (*"FIELD_ARCHETYPES deliberately holds neither of these"*), and
`FIELD_ARCHETYPES` confirms it: `("valley_paddy", "polder_grid", "mulberry_dike_fishpond")`.

99 statements at 7% coverage. **Writing tests for it would be paying for code nothing runs**, and
this is the GM's call, not the session's: it is either future work worth keeping (hill-rice terraces
are a real settlement form the migration plan may want) or it is deletable. Put to the GM with the
measurement; not covered and not exempted in the meantime.

## The mechanism: what makes `make done` carry the floor

**One variable, which already exists.** `COV_FLOORS=1` switches off all three of `make done`'s
remaining deselections - `--ignore=tests/full`, the `tooling-fresh` skip, and diff-scoped
`COV_SCOPE` - and is exactly what `test-full` sets. So the literal thing the GM asked for is a flag,
and the whole question is what it costs. **Being measured now** (`make test COV_FLOORS=1`), against
`make done`'s 89 s median and `test-full`'s 272 s pytest phase.

The `tests/full/` tree holds only **25 tests**, so the cost is concentrated: `test_villages.py`
rolls every pool map through `runpy`. If the measurement says most of the 272 s is those rolls, the
cheap version the GM asked about is to keep the FULL tree's SWEEPS out of `make done` while bringing
their COVERAGE in by unit tests - which is the same answer as the 64 already closed.

## Order of work

1. the 25 (in flight, 4 hard ones left)
2. the 54 - the existing floor's own misses, which nobody has looked at
3. the 760, worst-ratio first; `hill.py`'s 99 to the GM as a question
4. only then the floor itself, once the number it would enforce is actually met

**The floor goes on LAST, on purpose.** Setting `fail_under = 100` before the tree meets it leaves
the build permanently red, which is worse than no floor: a red gate that everyone learns to route
around is how the ratchets got there in the first place.
