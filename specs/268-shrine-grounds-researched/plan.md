# Implementation Plan: 268 - a village shrine's grounds, researched

**Branch**: none (`export SPECIFY_FEATURE=268-shrine-grounds-researched`) | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md) (FAITHFUL at round 2), [request.md](request.md), [research.md](research.md)

## Summary

Record the research pass (enclosure, precinct size and built share, torii spacing, precinct features) on
the religion-and-death page; bring the country-shrine program to it (no precinct enclosure, the grove and
sacred tree and basin as items, the donated stonework and the stage and ring as knobs); set the torii
pitch to 12 ft on every map with a plan-view arch glyph that stands at that pitch; edit the frozen
Hoshigaoka village map by hand (grove, sacred tree, basin, the seven arches at 12 ft); redraw the
Hoshigaoka shrine sheet to it; and run the crop check on sheets drawn to a map.

## Technical context

- **Language**: Python 3 (the engine, the pack audit, tests); hand-authored SVG (the sheet); HTML
  fragments (the record); JSON (the type declaration, the map manifest).
- **Engine surface touched**: `settlement/_geom/walls.py` (the pitch constant and `torii_halfbox`),
  `settlement/shrines_wells/torii.py` (the glyph, `_avenue_pitch`, the wall-shortening floor),
  `settlement/shrines_wells/shrines.py` (the single-point extension stride), `settlement/rolling/roll.py`
  (the village avenue), `tools/pack_audit/{shared,registry,mapmatch}.py` (the enclosure check, the crop
  check's reach), `buildings/types.json`.
- **Testing**: pytest through `make test-file` / `make quick` / `make done`; the pack-audit red fixtures.
- **Scale**: no live pool map draws torii today (every `pool/hamlets/*/*.json` has `"torii": []`; the
  magistracy sheets carry no arch) - observed 2026-09-27; method: a scan of every pool and legacy
  manifest's `torii` list. The ten maps with avenues are frozen exhibits and are not regenerated.
- **Single-artifact target**: the Hoshigaoka shrine sheet
  (`pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.gen.py`, a rasterize, seconds). The
  generator change is proven on unit tests of the avenue placer at 1, 2 and 3 ft/px; there is no pool
  map for it to move.
- **Every step is two steps**: the sheet (the reference artifact) then the pool (`make done`, which rolls
  the live pool and sweeps every Mode A sheet through the pack audit).

## Performance bookends

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `268-start` | 28.3 s | 7.0 s | 7.9 s | taken on unmodified code, 2026-09-27 (`dev/perf-log/20260927T053237Z-268-start-diagram-shrines.json`) |
| after | `268-end` | | | | taken before the push |

The reference hamlet draws no torii, so no change is expected; any band the report names is diagnosed.

## Baseline (constitution XIII)

The engine surface is covered by the whole gate. Baseline: main's last green `make done` (the
verification record the push stamps against, 2026-09-27) - no pre-existing failure is ledgered. The
live pool rolls no torii, so a changed roll is a regression to diagnose, not an expected effect.

## Constitution check

- **I, II**: N/A - no UI in this repository.
- **III**: N/A - no pool content of the markdown kind.
- **IV, V**: PASS - no SOURCE block is added, moved or edited; `request.md` quotes the GM and is not edited
  after this plan.
- **VI**: PASS - each task names its verification: the pack audit on the sheet, `building-review` and
  `size-audit` on it, `settlement-review` on the village map's edited region, `make done` once at the end;
  the record's four checks on every new or changed entry.
- **VII**: PASS - the program stays generic; Hoshigaoka's particulars (the seven, Bishamon) stay in its
  notes.
- **VIII**: N/A - no in-world prose.
- **IX**: PASS - `make canon TERMS="shrine|torii|country monk"` is read before the program text changes;
  the GM's notes say the country monk serves "in village shrines" and nothing about fences or groves.
- **X**: PASS - ruff, format, pyrefly, red-green tests for the pitch, the glyph extents, the floor, the
  enclosure check and the crop reach; 100% coverage. No overlap check is added (the enclosure check reads
  one sheet's declared groups; the grove is hand-drawn). No file nears 1,000 lines (`torii.py` and
  `shared.py` are measured at T-engine).
- **XII**: PASS - opening bookend in `research.md` (R1-R4, each with what determined it and whether the
  design matches); closing bookend is task T-close (read the rendered PNGs of the sheet and the village
  map's edited region against R1-R4). Decisions are classified in the spec's Decisions Recorded (added at
  T-record).
- **XIII**: PASS - baseline above; the frozen maps are not regenerated.
- **XIV**: the spec-lint scope defect found by review round 1 was fixed in the same work (commit
  691fc9ca).

## Decisions this plan makes that the spec left open

D1-D7 are in [`research.md`](research.md), "Design decisions": the pitch 12 ft (a guess inside the
GM's band, two ken); every avenue at the pitch; the arch drawn in plan, true size, with the stroke floor
as convention; the wall-shortening floor at the glyph's drawn depth plus one px; the sheet's arch in
plan; the grove's outline on the map (about 667 tsubo, measured at T-map); the enclosure check. Two
more:

- **D8 - the hand edit's artifacts.** The frozen map's manifest is tracked; its svg and png are
  gitignored and exist only in the mirror (`/diagram`), where the 2026-09-26 edit was also made. The svg
  is backed up to the scratchpad, edited in place (a `<g>` for the grove's canopy, the sacred tree, the
  basin; the six moved arches and the innermost re-seated), and the png re-rasterized with the same
  `resvg` call the gen uses. The manifest and the notes carry the edit in git; the gen's
  `SHRINE_TORII` stride is brought to the pitch so conversion lays the same avenue.
- **D9 - the crop check's reach.** `registry.py`'s `viewbox_cropped` row stops excusing `ctx.on_map`;
  `mapmatch.frame_is_the_maps` is removed with its report line; `buildings.md` says an on-map sheet's
  frame is cropped to its ink like any other, and `matches_map` still holds every map feature inside it.

## Phases

1. **T-record** (research: physical): write the new questions on `religion-and-death` (was a village
   shrine enclosed; how large was its precinct and how much was built; what else stood in it), rewrite
   the torii-spacing question, and bring entry 120's fence and precinct-size sentences and every other
   stale mention to the finding; register every new source with what it is and its limits. Checks, in
   the background, from bundles: `source-reader`, `quote-check` (after `make quote-verbatim`),
   `record-format` (after `make record-prepass`), `source-applicability`; then `entry-drift` on the
   modals that name the changed entries (`household.py` torii and country-shrine kinds, `grounds.py`
   grove). Glossary terms for new words (`make glossary`).
2. **T-program** (research: physical): `buildings/programs.md` and `types.json` - no enclosure; the
   grove, sacred tree and basin as items (grove and tree as site items); the precinct band from R2; the
   knobs (donated stonework on wealth; stage and ring); `buildings.md`'s arch and grove vocabulary.
   `no_precinct_enclosure` replaces `fence_not_wall` with its red fixture (the old walled fixture and a
   precinct-fence fixture both fire; a sanctuary-only fence passes).
3. **T-engine** (research: rendering): the pitch constant, `_avenue_pitch` for every avenue, the village
   roll's stride and threshold, the plan-view glyph and `torii_halfbox`, the floor. Tests first. Then the
   crop check's reach (D9) with its test.
4. **T-map** (research: physical): the hand edit of the Hoshigaoka village map (D6, D8); measure the
   grove's area on the drawn outline; notes and migration plan.
5. **T-sheet** (research: physical): redraw the shrine sheet; `make seat-label SHEET=... WRITE=1`; the pack
   audit (program, map-match, crop) green; notes rewritten.
6. **T-review**: `building-review` and `size-audit` on the sheet (`make size-table` first),
   `settlement-review` on the village map's edited region, all in the background, one map per agent;
   ledger rows; findings applied; anything for the GM through `escalation-check`.
7. **T-close**: `make perf LABEL=268-end` + `make perf-report AGAINST=268-start`; `make done` (background);
   the closing XII bookend on the rendered PNGs; `sync-with-main.sh done`.

## Project structure

```text
specs/268-shrine-grounds-researched/   spec, plan, research, request, reader-reports/, tasks
.claude/skills/diagram/
  research/religion-and-death/         new NNN-*.html + .notes.html; 090 and 120 revised
  research/sources/010-works-cited/    new NNNN-<key>.html per source
  buildings/programs.md, buildings.md  the program and the vocabulary
  l7r/diagram/buildings/types.json     the declaration
  l7r/diagram/settlement/_geom/walls.py, shrines_wells/{torii,shrines}.py, rolling/roll.py
  l7r/diagram/tools/pack_audit/{shared,registry,mapmatch}.py
  legacy-hand-authored-pool/villages/hoshigaoka/{hoshigaoka.json,.notes.md,.gen.py}  (+ the mirror's svg/png)
  pool/country-shrines/hoshigaoka-shrine/{.svg,.notes.md}
  tests/ (settlement torii, pack audit, fixtures)
```

## Complexity tracking

None.
