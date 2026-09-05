# Feature 187 - the render cache sees the page's assets

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5) - cleared for implementation (constitution XVI).
Round 1 found FR-002 (widening `gencache.engine_files()`) beyond the question and resting on a backwards
account of the generation cache; round 2 verified the corrected account against the code and returned
none.
**Request**: [`request.md`](request.md) - the GM's question verbatim, and what the investigation found
**Predecessors**: feature 181 FR-010 (the GATE key and the ROUTE learned to count `page.js`/`page.css` as
engine content after the gate short-circuited on an asset-only delta); feature 186 (the asset-only
landing whose pages did not regenerate)

## The defect

`pipeline/render_cache.engine_fingerprint()` decides whether render-sync re-runs a map's generator in
the mirror by hashing the engine, and it walks `.py` files only. The interactive page's stylesheet and
script are inlined into every `<map>.html` at write time, so a landing that changes only
`interactive/assets/page.css` changes every page's content and not this fingerprint - render-sync says
"cached (fresh)" and the GM opens a page rendered before the change. Feature 186 was exactly that
landing, and the GM saw the dotted underlines it had removed.

**The generation cache is NOT part of the defect** (measured, round-1 review): `page.py`'s `_asset()`
reads the two files through `open()`, `gencache.record()` traces every non-output read into the entry's
data files, and `key_for()` hashes each data file by its bytes - so a clone's `make map` keyed on the
assets' content all along, which is why the clone regenerated Inashiro correctly while the mirror's
render-sync did not. `render_cache` has exactly one consumer, render-sync in the mirror, and that is the
whole blast radius. An earlier draft of this spec named `gencache.engine_files()` as half the defect and
proposed widening it too; that account was backwards and the requirement is withdrawn (D3).

## Functional requirements

- **FR-001** `render_cache.engine_fingerprint()` MUST include the interactive page's assets - every `.js`
  and `.css` under the engine tree it already walks - in the fingerprint, hashed by their bytes, under the
  same DIRECTORY prunes as the `.py` files (the `test_` name filter and the self-exclusion have no
  analogue among assets and are not applied to them; stated at the point of change).
- **FR-003** A test MUST prove `engine_fingerprint()` moves when an asset's bytes change and does not move
  when a `.py` under `tests/` or a pool file does (the existing prunes hold).
- **FR-004** The consequence is stated and accepted: the first render-sync after this lands regenerates
  every live pool map once (the fingerprint's file set changed), which is the regeneration feature 186
  owed and did not get. About one to two minutes in the mirror, once.
- **FR-005** Nothing else changes: no glyph, no page content, no cache layout.

## Decisions Recorded

- **D1 - suffix, not path**, as in feature 181 D4: `.js`/`.css` anywhere the walk already reaches, so a
  future asset is engine content the day it lands. Today the two assets are the only such files under
  the engine tree (feature 181's test pins that census).
- **D3 - `gencache.engine_files()` is left alone.** The read trace already keys every entry on the assets'
  bytes (measured: `record()` -> data files -> `key_for()` hashes them). Widening the census would have
  bought consistency with the gate key at the price of a cold miss on EVERY generation-cache entry at the
  next gate, and would have rested on a false account of the defect. If a code path ever inlines an asset
  without an `open()` the trace sees, that is the named case that reopens this. **The account being
  retracted is also the one in [`request.md`](request.md)'s "What the investigation found"** - written by
  the session before the review, and left as written because that file is kept verbatim; this decision
  is its correction.
- **D2 - fixed under a spec-kit feature rather than as a hotfix**, because pipeline code is engine code
  and the GM's rule admits no exception; the question that found it is the request.
