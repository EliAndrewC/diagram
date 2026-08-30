# Phase 1 data model - feature 161

The "data" here is a directory tree and the facts derived from it. This file states the shape, the
vocabulary, and the invariants the implementation must hold.

---

## The two trees

Both live inside `.claude/skills/diagram/` and share one shape: `<tree>/<tier>/<map>/<map>.<ext>`.

| | `pool/` | `legacy-hand-authored-pool/` |
|---|---|---|
| what it holds | maps that are LIVE | the 18 FROZEN hand-authored Mode B exhibits |
| regenerated? | yes, by `regen.py` / render-sync / the gate | **never** (`regen.py` prints `FROZEN`) |
| re-gated? | yes, every `make done` | never |
| renders in git | ignored (derived) - except a Mode A `.svg`, which is SOURCE | **committed, write-once** |
| classification | `scripted` or `compound` | `legacy` |
| how a map leaves | conversion is not a thing a live map does | by being CONVERTED to scripted generation, at which point it moves to `pool/` |

`pool/regressions/` sits inside `pool/` and is **not** a tier: it holds 107 negative-fixture `.json`
plus one `.notes.md` and one `.svg`, stays flat, and is skipped by the index.

## Membership, exactly

**`pool/`** (10 maps)

| tier | maps |
|---|---|
| `hamlets/` | inashiro, kashikawa, kuwabata, mizuguchi, sawada |
| `magistracies/` | county-magistracy-example, hayakawa-magistracy, ochiba-magistracy, ochiba-roundtrip-test, ubame-magistracy |

**`legacy-hand-authored-pool/`** (18 maps)

| tier | maps |
|---|---|
| `hamlets/` | akagahara, enokida, honda, ikegami, moritono, shimizu, tanada, yatsuda |
| `villages/` | hikari-no-sato, hoshigaoka, kikuta, ueda |
| `towns/` | hirameki, hoshizora, ubame |
| `provincial-cities/` | minami, nagahara, tango |

`pool/villages/`, `pool/towns/` and `pool/provincial-cities/` **cease to exist**. `hamlets/` is the
only tier name present in both trees. `ubame` names a legacy TOWN and a live MAGISTRACY
(`ubame-magistracy`) - different trees, different tiers, different stems, no collision.

## The map bundle

One map's files, all sharing the map's stem as their basename (FR-002).

| file | present for | in git | role |
|---|---|---|---|
| `<stem>.gen.py` | every map | tracked | the source: a generator (Mode B) or a compound program (Mode A) |
| `<stem>.json` | Mode B only | tracked | the manifest - what was drawn; the gate reads THIS, never pixels |
| `<stem>.notes.md` | every map | tracked | the record: why this map is as it is, its review log |
| `<stem>.svg` | every map | live Mode B: ignored. **Mode A: tracked (it IS the source).** Legacy: committed exhibit | the drawing |
| `<stem>.png` | every map, once rendered | ignored, except a legacy exhibit | the raster the GM opens |
| `<stem>.html` | Mode B, once rendered | ignored | the interactive page (feature 134) |

A map is IDENTIFIED by its `.gen.py`; everything else is optional on disk. A clean checkout has no
live `.svg`/`.png`/`.html` at all - which is why the frozen exhibits are the only renders most checks
can see (research R9).

## Invariants the implementation must hold

1. **Every `.gen.py` is in exactly one tree, and its tree agrees with `classify()`.** Under `pool/`:
   `scripted` or `compound`. Under `legacy-hand-authored-pool/`: `legacy`. Nothing anywhere
   classifies `unknown`. (FR-011, and the ratchet FR-013a.)
2. **Every declared name resolves.** Every member of `poolmaps.LEGACY_FROZEN_GENS` is present in the
   legacy tree; every member of `COMPOUND_GENS` is present in `pool/magistracies/`. Both lists are
   basename-keyed and CLOSED, so this is a two-way check: no stale name, no undeclared map.
3. **A map directory holds only its own map's files** (FR-003) - the property that makes the tree
   worth reorganizing at all.
4. **The count is conserved**: 28 maps before, 28 after; 23 Mode B, 5 Mode A. (SC-003.)
5. **Content is conserved**: every moved file's hash is unchanged, except a `.gen.py` whose path
   arithmetic deepens and a document that names a path. (FR-007, SC-004.)
6. **Git sees renames**, not deletes-plus-adds, so the 195 MB of committed exhibits is not
   re-added to history. (FR-008.)
7. **The engine fingerprint is unchanged across the move.** The legacy tree is NOT engine source; if
   its `.gen.py` entered the fingerprint, every live map's cache key would shift. (Research R4 - the
   highest-risk item.)

## Vocabulary

Used consistently in code, tests and docs, because the drift this feature fixes started as
vocabulary drift:

- **tree** - `pool/` or `legacy-hand-authored-pool/`. Never "pool" for both.
- **tier** - `hamlets`, `villages`, `towns`, `provincial-cities`, `capitals`, `magistracies`.
- **map** / **bundle** - one settlement or compound plan and its files.
- **stem** - the map's name as a basename: `inashiro`, `ochiba-magistracy`.
- **live** - in `pool/`; regenerated and gated. **frozen** - in the legacy tree; an exhibit.
- **kind** - `classify()`'s answer: `scripted`, `legacy`, `compound`, `unknown`.

Note "live" is not the complement of "hand-authored": the five magistracies are live AND
hand-authored, by design. That distinction is the whole substance of the GM's second paragraph, and
conflating the two axes is the mistake the vocabulary exists to prevent.
