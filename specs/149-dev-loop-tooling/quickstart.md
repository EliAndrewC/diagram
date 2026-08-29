# Quickstart: the three diagnostics and the paired gate (feature 149)

## Measure a polder geometry change without drawing a map

```
make polder-probe SEED=21                      # the reference dike-pond block
make polder-probe SEEDS=21,22,23               # three blocks, one table
make polder-probe SEED=21 ARCHETYPE=polder_grid
```

Prints, per block: parcels overlapping a channel (with coordinates), the minimum and median berm, acreage
against target, per-parcel vertex counts and the square-corner mean, ring point counts, and its own wall
time. Exits non-zero when a metric would fail the gate - so it can guard an expensive run.

Use it while iterating on `waterfields/polder.py` or `hamletgen/water.py`: it is the same code the map
rolls, so it cannot pass while the map fails.

## Ask whether two things overlap

```
make overlap-audit M=pool/hamlets/kuwabata.json
make overlap-audit M=pool/hamlets/kuwabata.json FAMILIES=ink-mounds,parcels-channels
```

Families: `footprints-water`, `footprints-marsh`, `parcels-channels`, `ink-mounds`, `ink-water`. The `ink-`
families read the rendered SVG, not the manifest, because a mark drawn over a mound is invisible to the
record. Each offender prints its family, coordinates and count; the tool exits non-zero if any family has
one, and prints `unmeasured` for a family whose inputs this map does not carry.

## Find the slow stage in one roll

```
make map GEN=pool/hamlets/kuwabata.gen.py PROFILE=1
```

Prints each stage's elapsed time, the total, and the slowest stage. Without `PROFILE=1` the roll is exactly
what it is today - a test asserts the manifest is identical either way.

## Verify: the gate and the review, together

```
make verify
```

Starts the integration gate detached and prints the review dispatch line for the maps whose manifests
changed. Neither half runs alone: invoking the gate by itself, or dispatching a `settlement-review` by
itself, is refused with a message naming this command. To take a one-sided case deliberately:

```
PAIR_OK="docs-only change, no map ink" make done
```

The reason lands in `dev/bypass-log/` where the audit reads it.

## SC-002, demonstrated (2026-08-29)

Every overlap question features 150's T50-T55 answered by a hand-written script, re-asked with one command
and no script written - `make overlap-audit M=pool/hamlets/<map>.json` over all five pool hamlets. All five
families report `ok` on each. The audit found one defect on its first run (reed ink across the inlet
hairline, because the source pond's fringe was scattered before the field's channels existed), recorded in
`pool/hamlets/kuwabata.notes.md` and fixed.
