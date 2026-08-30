# Research: what the check battery actually costs, and what already fires

Measured 2026-08-30 in `.clones/diagram-testing` at `c33315db`, before any change. These are the
BASELINE numbers FR-011 and SC-005 are measured against, and the floor the User Story 1 census has to
beat.

## R1 - the per-map cost is small; the SURFACE is the cost

The GM's framing is that running the checks *"every time a map is generated instead of having it happen
when a thing is placed"* is the waste. Measured, the per-generation half of that is minor:

| what | measured |
|---|---|
| `make gate-manifest M=pool/hamlets/inashiro/inashiro.json` (full battery, one finished map) | **1.3 s** |

So retiring the battery buys ~1.3 s per map roll, against hamlet rolls that run tens of seconds. That is
real but it is not the argument. The argument is the surface the battery carries:

| surface | lines / count |
|---|---|
| `check_village/` source | **14,483 lines** (385 registry segments, 152 live check names) |
| its tests (`tests/check_village/`, `tests/gate/`) | **7,464 lines** - 23% of the whole 32,813-line test tree |
| frozen negative fixtures (`pool/regressions/`) | **105 manifests, 11 MB** |
| the placement engine the battery audits (`settlement/`, `hamletgen/`, `waterfields/`) | 38,153 lines |

**~22,000 lines of audit code plus 11 MB of frozen maps, against a 38,000-line generator.** That ratio
is the honest statement of the GM's point, and it is the number to carry into the User Story 2
discussion - not the 1.3 s.

**Sources:** none - this is a measurement of this repository, not a research finding. `wc -l` over the
trees named above; the gate timing is a single `make gate-manifest` run on an otherwise idle container.

## R2 - the floor for the never-fires census

A cheap static pre-count, to give User Story 1 a number to beat and to prove the census is not returning
an empty set (FR-005). This is NOT the census: it greps rather than executes, which FR-002 forbids as the
method, and it therefore both over- and under-counts. It is a sanity floor only.

| firing source | live checks with evidence |
|---|---|
| a frozen negative fixture in `pool/regressions/` naming it in `_regression.fires` | 76 of 152 |
| a name appearing in any file under `tests/` | 140 of 152 |
| a waiver declared on a live pool map | **0 of 152** |
| union of frozen + scripted negative fixtures | ~95 of 152 |

- **9 checks have no frozen fixture, no test naming them, and no waiver at all**:
  `capital_has_kosatsuba`, `capital_has_no_headman`, `city_has_no_headman`, `farmhouse_aspect_in_range`,
  `stream_end_anchored`, `stream_source_anchored`, `town_has_no_headman`, `village_has_no_headman`,
  `ways_clear_of_castle_moat`. Six of the nine are legacy-tier checks with no scripted executor at all
  (feature 158 deleted the frozen town/city exhibits that were their only possible subjects).
- **~57 checks have no NEGATIVE fixture of any kind** - nothing in the tree is known to make them fail.
  The gap between 9 and 57 is the difference between "no test names it" and "no test makes it FAIL",
  and closing that gap by execution rather than by grep is precisely FR-002.

So the census's candidate set is expected to land between **9 and 57**, and a census returning zero or
returning all 152 is a broken census, not a finding.

**Sources:** none - a measurement of this repository.

## R3 - no live map is exempting itself

Zero waivers are declared on the five live scripted hamlets. Every waiver in the repository belongs to a
frozen hand-authored exhibit. So on the live pool the battery is fully green with nothing suppressed,
which is what makes the GM's *"our automated checks are not catching anything in this exact moment"*
literally true today - and what makes "never fires" so weak a test on its own, since a battery that
catches nothing is what both a correct generator and a neutered battery produce.

**Sources:** none - a measurement of this repository.
