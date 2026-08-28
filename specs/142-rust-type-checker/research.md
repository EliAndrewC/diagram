# Research: feature 142 - Rust-based type checker experiment

All numbers measured 2026-08-28 in this container (Python 3.14.4, mypy 2.3.0 compiled, ty 0.0.75,
pyrefly 1.2.0), on the 163-file set `[tool.mypy] files` names, from
`.claude/skills/diagram/`, with a subprocess wrapper reading `wall` from `time.time()` and peak
RSS from `resource.getrusage(RUSAGE_CHILDREN)` (the wrapper is reproduced in `report.md`).

## R1. Candidates

Two Rust-implemented Python type checkers have vendor backing: **ty** (Astral, the makers of ruff -
which this project already uses) and **pyrefly** (Meta). No third candidate surfaced. Both install
from PyPI as a single binary wheel with no Python dependencies.

## R2. Speed and memory

| tool | run | wall | peak RSS | diagnostics |
|---|---|---|---|---|
| mypy 2.3.0 | cold (no `.mypy_cache`) | 12.66 s | 344 MB | 0 |
| mypy 2.3.0 | warm one-shot (cache present) | 0.20 s | 60 MB | 0 |
| dmypy | first `run` (daemon starts) | 12.56 s | 46 MB client; daemon 415-498 MB resident | 0 |
| dmypy | warm `run` | 0.13 s | 35 MB client + the resident daemon | 0 |
| ty 0.0.75 | cold, no cache, no daemon | 0.46 s | 196 MB (freed at exit) | 16 |
| ty 0.0.75 | second run (no cache exists) | 0.45 s | 202 MB | 16 |
| pyrefly 1.2.0 | cold, no cache, no daemon | 0.64 s | 234 MB (freed at exit) | 18 |
| pyrefly 1.2.0 | second run | 0.61 s | 256 MB | 18 |

**The GM's hypothesis holds**: a Rust checker's full cold check (0.5-0.6 s) is 20x faster than
mypy's cold check and within half a second of the warm daemon, with nothing left resident. Per
quick run the switch costs ~0.5 s against the warm daemon's 0.13 s and returns 400-600 MB of
RAM per clone. On an interface change to a central module (where the daemon fell back to ~2.7 s,
Makefile note) the Rust tool is still ~0.6 s, so the worst case improves too.

## R3. Strictness - what each enforces

The project's discipline is `mypy --strict`, whose load-bearing part is `disallow_untyped_defs`:
an unannotated function is an error. Probe file with an untyped def, a half-typed def, an
implicit-Any return and a bare `dict` annotation (`report.md` reproduces it):

- mypy `--strict`: 8 errors.
- **ty**: 0 by default; with every rule turned on (`--warn all`), 3 warnings, NONE of them "missing
  annotation" - ty has no such rule at all. Astral's typing FAQ says this is by design: an
  unannotated parameter is `Unknown` and checking continues; annotation completeness is left to
  ruff's `ANN` lint rules. So enforcing the project's bar with ty means adding ruff `ANN001/ANN201/
  ANN202/...` - a second tool for the property, and a lint rule rather than a type rule.
- **pyrefly**: 0 by default (preset `legacy`, auto-imported from `[tool.mypy]`); has native rules
  `unannotated-parameter`, `unannotated-return`, `unannotated-attribute`, `implicit-any-parameter`,
  `implicit-any-type-argument`, `no-any-return-implicit`; each can be enabled individually in
  `[tool.pyrefly.errors]`. Its `strict` preset also turns on `implicit-any-lambda` (167 hits on the
  engine) and `implicit-any-empty-container` (163) - noisier than mypy strict, so the project
  enables the mypy-equivalent rules by name rather than taking the preset.

Enabled on the engine, pyrefly's `unannotated-*` rules report **0 hits**: the codebase is already
clean under them (the mypy ratchet did its job).

## R4. Environment and configuration differences

- **ty** did not find the user-site `~/.local/lib/python3.14/site-packages` where `shapely` and
  `PIL` live (5 `unresolved-import`); `--extra-search-path` fixes it, so a `[tool.ty.environment]`
  block would be needed. pyrefly found them unaided.
- **pyrefly** reads `[tool.mypy]` (`files`, `mypy_path`, the `boto3` ignore) with no `[tool.pyrefly]`
  present - it printed "using settings imported from [tool.mypy] (preset: legacy)". A native block is
  still written (FR-004) so the intent is explicit rather than inherited.
- **namespace portion**: both tools gave every file one identity with no `__init__.py` added.
- **`# type: ignore[mypy-code]`**: pyrefly honored every existing one (none of its 18 residuals
  is on an ignored line); ty flagged three lines that carry a mypy ignore (`timings.py:268`,
  `why_placed.py:208`, `driver.py:142` / `perf_profile.py:71`) - it does not treat a mypy-coded
  ignore as covering its own rules.
- **crashes/hangs**: none, on either tool, across ~20 runs.

## R5. pyrefly's residual diagnostics on today's engine (18, default preset)

Sixteen share ONE root: pyrefly types `d.get(k, default)` on a `dict[str, Any]` as `Any | None`
when the default expression is itself `Any` (`o.get("vw", o["w"])`); with a `float` default it
gives `Any`, and mypy gives `Any` in both cases. Verified with `reveal_type` in-tree. Under the
typing spec's overload-evaluation rule an `Any` argument that matches several overloads with
different return types should evaluate to `Any`, so this is a pyrefly limitation, not a defect in
the engine - the value at runtime is never `None` (the default is always supplied). Sites:
`civic.py:224` (3), `homestead_parts.py:1018` (2), `servants.py:77/78/196`, `banks.py:537/538`,
`carve.py:67/735/904(2)/914`, `segments_01a:283` (ty only). Resolution: a
`# pyrefly: ignore[<rule>]` at each site with the reason - the code is right and mypy agrees.

The other two:
- `segments_02c:104`, `segments_10f:355` `no-any-return-implicit`: `rr_ is not None and min(...) < x`
  returns `bool | Any`; wrap in `bool(...)` - a real tightening, no behavior change.
- `castle_civic.py:266` `bad-assignment`: `rec["karamete_dir"] = karamete_dir` where `karamete_dir`
  is `str | None` and the record's value type has no `None`. Inspect at implementation: if `None`
  can reach it, that is a defect the manifest schema does not admit (fix by guarding); if it cannot,
  narrow the local.

With the `unannotated-*`, `implicit-any-type-argument`, `no-any-return-implicit` and `unused-ignore`
rules enabled, 6 more `unbound-name` ("may be uninitialized") at `moat.py:121`, `dikes.py:144`,
`packing.py:248` (2), plus `finish.py:468` `implicit-any-attribute` (`self._road_label = None`
with no annotation). The unbound-name cases are variables assigned under one condition and read
under a different but equivalent one (`if river is not None` twice); pyrefly cannot correlate them.
Initializing them to `None` beside their declaration is a cheap robustness fix, not a suppression.

## R6. The pick

**pyrefly.** Both clear the GM's two criteria (fast enough to need no daemon; not crashing). They
differ on the thing the project relies on: pyrefly enforces "an unannotated function is an error"
natively; ty cannot, and would need ruff's ANN rules bolted on. pyrefly also honored the existing
mypy ignore comments and found the environment unaided, so the switch touches less. ty is at
0.0.75 and its own docs call it pre-release; pyrefly is at 1.2.0. Speed is a wash (0.46 vs 0.64 s).

Sources (read): Astral, "Typing FAQ - ty" <https://docs.astral.sh/ty/reference/typing-faq/>
(unannotated symbols inferred as Unknown; annotation enforcement is ruff's ANN); Astral, "Rules - ty"
<https://docs.astral.sh/ty/reference/rules/>; pyrefly, "Error kinds" <https://pyrefly.org/en/docs/error-kinds/>;
facebook/pyrefly issue #1505 (a `dict.get` default false positive of the same family) <https://github.com/facebook/pyrefly/issues/1505>.
The `Any | None` behavior above was measured here, not taken from any page.
