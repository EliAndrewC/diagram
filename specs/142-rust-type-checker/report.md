# Feature 142 - findings: a Rust type checker instead of mypy and its daemon

**For the GM's acceptance (spec FR-010). Nothing has been pushed.** Measured 2026-08-28 in this
container; method and every number in [`research.md`](research.md).

## The answer

**Your hypothesis holds: no daemon is needed.** A Rust checker checks the whole engine (163 files,
~79k lines) cold, from nothing, in about half a second - mypy needs 12.7 s cold, which is why it
ran through a daemon holding 400-600 MB per clone. Per quick run the switch costs **~0.5 s more
than the warm daemon** (0.6 s one-shot against 0.13 s warm) and returns the RAM of every daemon;
on an interface change to a central module it is faster than the daemon was (0.6 s against ~2.7 s).

| tool | cold, no cache, no daemon | resident afterwards |
|---|---|---|
| mypy 2.3.0 | 12.66 s, 344 MB peak | nothing (0.20 s warm with `.mypy_cache`) |
| dmypy | 12.56 s first run, then 0.13 s | **415-498 MB per clone, for good** |
| ty 0.0.75 (Astral) | 0.46 s, 196 MB peak | nothing |
| pyrefly 1.2.0 (Meta) | 0.64 s, 234 MB peak | nothing |

The ~200 MB peak of a one-shot run is freed at exit; it is not the daemon's resident cost.

## The pick: pyrefly

Both candidates clear your two criteria - fast enough to need no daemon, and no crash or hang in
~20 runs each. They part on the one thing the project's discipline rests on: **an unannotated
function is an error.** pyrefly has that rule natively (`unannotated-parameter`,
`unannotated-return`, `unannotated-attribute`, each a one-line switch); **ty has no rule for a missing
annotation at all** - Astral's docs say that is by design, an unannotated name is `Unknown` and
checking carries on, and annotation completeness is ruff's `ANN` lint family. So ty would mean two
tools for the property mypy gave us in one. Secondary: pyrefly read our `[tool.mypy]` block and
found the user-site packages unaided (ty needed an extra search path for `shapely`/`PIL`), and
pyrefly honored every existing `# type: ignore[mypy-code]` comment (ty flagged three of those
lines). ty is at 0.0.75 and self-described pre-release; pyrefly at 1.2.0. Speed is a wash.

## What the check enforces now, against mypy --strict (FR-005)

| mypy --strict flag | pyrefly rule, enabled in `[tool.pyrefly.errors]` | hits on today's engine |
|---|---|---|
| `disallow_untyped_defs` / `disallow_incomplete_defs` | `unannotated-parameter`, `unannotated-return` | 0 |
| (mypy infers class attributes) | `unannotated-attribute` - stricter than mypy | 0 |
| `disallow_any_generics` | `implicit-any-type-argument` | 0 |
| `warn_return_any` | `no-any-return-implicit` | 2, fixed |
| `warn_unused_ignores` | `unused-ignore` | 0 |
| `no_implicit_reexport` | `implicit-reexport` exists, NOT enabled - it fires on the star-import `__init__` files that feature 027 made the canonical re-export form; mypy's flag never did | - |
| `strict_equality`, `warn_redundant_casts` | pyrefly's defaults cover comparisons and casts (`incompatible-comparison`, `redundant-cast`) | 0 |

Deliberately NOT taken: pyrefly's `strict` preset, which adds `implicit-any-lambda` (167 hits) and
`implicit-any-empty-container` (163 hits) that mypy strict never demanded.

**Gained**: pyrefly reports "may be uninitialized" (`unbound-name`) for a variable assigned under one
condition and read under another - 6 sites, each initialized ahead of its branch. mypy does not
do flow-sensitive unbound analysis. **Lost**: nothing measured. mypy remains installed and
`python3 -m mypy` still passes on the switched tree, so the two can be compared at any time.

## The residual diagnostics on today's engine (FR-006): 24, all resolved

- **1 real narrowing gap** - `castle_civic.py`: `rec["karamete_dir"] = karamete_dir` (`str | None`)
  under `if karamete is not None`, where `karamete` exists only when `karamete_dir` was truthy two
  branches earlier; the condition now says so (`and karamete_dir`). Behavior unchanged.
- **2 tightenings** - two gate segments returned `x is not None and <Any comparison>` from a
  `-> bool` function; wrapped in `bool(...)`.
- **6 defensive initializations** - `moat.py` (inlet/outlet), `dikes.py` (runs), `packing.py`
  (fr/fd), each read under a condition equivalent to the one that assigned it; initialized to a
  typed `None`/empty ahead of the branch. Behavior unchanged. Plus `finish.py`: a conditional
  attribute re-declared with its `Any` annotation.
- **15 suppressions of ONE pyrefly limitation** - `d.get(key, default)` on a `dict[str, Any]` types
  as `Any | None` when the default is itself `Any` (e.g. `o.get("vw", o["w"])`); mypy says `Any`,
  and the typing spec's overload rule agrees with mypy. Each site carries
  `# pyrefly: ignore[rule]  # ... research 142 R5`. If a later pyrefly fixes it, `unused-ignore`
  is enabled, so those comments will turn red and can be deleted.

`pyrefly check`: 0 errors. `python3 -m mypy`: 0 errors. Every one of these is an engine `.py` token
change, so this lands by the GATED route on a green gate.

## What changed in the tooling

- `pyproject.toml`: `[tool.pyrefly]` beside `[tool.mypy]` - same file list (asserted equal by
  `tests/tooling/test_typecheck.py`), same search root, the same boto3/botocore exemption.
- `Makefile`: `TYPECHECK = pyrefly check` (one form, CodeBuild included); `DMYPY_SWEEP` and the
  daemon comment block removed, the history kept in a short note.
- `requirements-dev.in/.txt`: `pyrefly==1.2.0` added; `mypy==2.3.0` kept. `Dockerfile.ci` probes
  `pyrefly --version`.
- Removed: `scripts/dmypy-hooks.sh`, `scripts/test-dmypy-hooks.sh`, the `SessionEnd` hook entry,
  the `CLAUDE.md` guard-table row (replaced by the pyrefly row); `docs/iteration-loop.md` rewritten.
- New test: `tests/tooling/test_typecheck.py` - a planted wrong-argument-type fixture fails
  `pyrefly check` under the project's own rules; the two file lists are equal.
- The gate: `make done` green on the merged engine content - 3901 passed across its phases, wall 1m25.347s (exit 0, 2026-08-28)

## Two decisions reserved to you (FR-007b)

1. **Does mypy leave the lockfiles?** It costs no RAM uninvoked; it is the cross-check this report
   used; it is also the fallback if pyrefly disappoints. Keeping it means a future session can run
   both; removing it is one line in `requirements-dev.in` and a re-lock. My recommendation: keep it
   for now, drop it once pyrefly has held through a few features.
2. **The constitution names `mypy --strict`** (Principle X, and the plan template's Constitution
   Check). Only you amend it. If you accept the switch, the wording I would propose:
   *"strict static typing on production modules (pyrefly with the mypy-strict rule set, feature 142;
   `mypy --strict` before it)"* - so the principle names the property, and the tool is a footnote.

## Also found on the way (not this feature's defect; recorded so nobody re-diagnoses it)

`tests/tools/test_scatter_audit.py::test_crown_fills_covers_every_recorded_crown` fails in a clone
after a merge that brought regenerated pool MANIFESTS (tracked in git) beside the clone's older
gitignored SVGs - feature 140's commit did exactly that for Kashikawa, Mizuguchi and Sawada. The
test compares the tracked `.json` against the untracked `.svg` and reads two different rolls. It is
not an engine defect (a fresh roll agrees 510/510 on Inashiro; the gate regenerates the pool, so
the gate never sees it), but it cost this session ~40 minutes to prove that. Worth a follow-up:
the test could skip a pair whose SVG predates its manifest, or the sync-in could evict a stale
render when the merge touches its manifest.
