# Contract: the pool discovery surface

**Module**: `l7r.diagram.pipeline.poolmaps`

The one place that answers *"which maps exist, in which tree, of which kind"*. Every consumer that
walks the pool calls this instead of building a path or a glob. Rationale and the rejected
alternative are in `research.md` R1; the tree it describes is in `data-model.md`.

---

## Why this is a contract and not just a helper

Ten consumers currently restate the pool's shape independently, and they disagree in ways that are
green: `mapcheck._live_gens` carries a comment recording that Kuwabata was converted and left in
`LEGACY_FROZEN_GENS`, so `regen.py` regenerated it while `make maps` never rolled it - *"settlement-review
round 3, 2026-08-29"*. That is the drift this module already exists to prevent for classification,
extended to the walk.

The contract's real content is therefore **the tree selection**, not the file listing: a consumer
must be forced to SAY which tree its job concerns, because the wrong answer is silent (a sweep over
too few maps is green - see research R9 for the one that would have failed loudly, and note that it
failing loudly was luck).

---

## Surface

```python
TREES: tuple[str, ...]              # ("pool", "legacy-hand-authored-pool"), live first

@dataclass(frozen=True)
class MapBundle:
    gen: str                        # absolute path to <stem>.gen.py
    stem: str                       # "inashiro"
    tier: str                       # "hamlets"
    tree: str                       # "pool" | "legacy-hand-authored-pool"
    directory: str                  # absolute path to the map's own folder

    def path(self, ext: str) -> str # the bundle's <stem><ext>, whether or not it exists
    @property
    def kind(self) -> str           # classify(self.gen)

def bundles(*, trees=..., kinds=None, skill_dir=...) -> list[MapBundle]
def classify(gen: str) -> str       # UNCHANGED
```

### `bundles(...)`

Returns every map bundle in the named trees, **sorted deterministically** by `(tree, tier, stem)`
with `pool` before the legacy tree - so any listing built from it is stable and any two consumers
agree on order.

- `trees` - which trees to walk. **The caller states this explicitly**; the default is both, because
  the safe default is the one that sees everything (a consumer that over-collects is caught by its
  own assertions, one that under-collects is green).
- `kinds` - optional filter on `classify()`. `kinds={"scripted"}` is the regeneration sweep's
  request; `None` means every kind.
- `skill_dir` - injectable for tests, defaulting to the real skill root.

A tree that does not exist on disk contributes nothing rather than raising: `pool/capitals/` does not
exist yet, and neither tree exists in a `tmp_path` fixture that only builds one.

`pool/regressions/` and `__pycache__` are never map directories and are excluded by the walk. This
is the SAME exclusion the index applies (`SKIP_DIRS`), and it lives here now so the two cannot
disagree.

---

## Who calls it with what

The table IS the contract - FR-013's "which tree" answered once per consumer, in one place a reviewer
can read.

| consumer | trees | kinds | why |
|---|---|---|---|
| `render_cache.regen_pool` | both | all | regenerates the live pool AND warns about a frozen exhibit whose render is missing - that warning follows the exhibits into the legacy tree |
| `pool_index.build_index` | both | all | ONE page over both trees (FR-016) |
| `tools/notes_census` | both | all | every map's notes carry a derived census block |
| `tests/test_villages` GENERATORS | `pool` | `{"scripted"}` | the gate rolls and gates live scripted maps only |
| `tests/test_villages` ratchet | both | all | every map accounted for, in the right tree (FR-013a) |
| `tests/test_villages` stale-render sweep | both | all | in a clean checkout the frozen exhibits are the ONLY renders it can check (FR-013b, research R9) |
| `tools/cache_audit.gens` | `pool` | `{"scripted"}` | a frozen map is never regenerated, so it has no cache to audit |
| `tools/mapcheck._live_gens` | `pool` | not `legacy` | "live gens in this tier" is its whole job |
| `tools/timings` map count | both | all | a census of what the repository holds |

**A consumer NOT in this table has not been considered.** Adding one means adding a row.

---

## Invariants (each is a test)

1. **Round trip**: for every bundle, `os.path.dirname(gen) == directory`, `basename(directory) == stem`,
   and `path(".gen.py") == gen`.
2. **Tree agrees with kind**: every bundle in `pool` is `scripted` or `compound`; every bundle in the
   legacy tree is `legacy`; none is `unknown`.
3. **Filtering is exact**: `bundles(kinds={"scripted"})` equals the members of `bundles()` whose
   `kind` is `scripted`. The filter is not allowed to be a second, subtly different rule.
4. **Determinism**: two calls return equal lists; order is `(tree, tier, stem)` with `pool` first.
5. **Depth**: `classify()` returns the same answer for a gen one level deeper than before -
   it is basename-keyed, so this holds by construction, and the test pins it so a future change to
   `classify` cannot break it silently. (FR-011.)
6. **Absent tree is empty, not an error.**
7. **Non-maps excluded**: a `regressions/` fixture and a `__pycache__` directory never appear.

## Compatibility

`classify()` keeps its signature, its behavior and its two closed lists. Everything here is
additive - which is what lets Phase 2 convert consumers one at a time against a green suite
(research R2).
