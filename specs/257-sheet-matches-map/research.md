# Feature 257 - the research pass

*What was measured and read, and what it decides. Nothing here is a rule: the rules are in `spec.md`
and the plan's decisions, each pointing back here. This feature asks no historical question - it is
about the correspondence between two of this project's own drawings - so every item is
`research: rendering`; the one physical question it touches (what stands around a country shrine)
was answered by feature 254 and is not reopened: the map, not the record, decides what stands around
THIS shrine (the GM, 2026-09-20).*

## R1. The map's drawing grain - how close is "the corresponding place"?

**Question.** The map check (spec FR-004) must decide whether a feature on the sheet and a feature on
the map are the same feature. Held too tight, a well placed by the map's own ring search fails a
sheet that drew it exactly where the map did; held too loose, a grove forty feet off passes.

**Measured, from the village map's own placement code and manifest (a one-shot observation,
2026-09-20, by reading `settlement/shrines_wells/wells.py` and `shrines.py` and the Hoshigaoka
manifest):**

- The set-apart shrine's own well is placed on rings of 54, 66, 80, 96 and 112 map px around the
  hall's center at 30 degree steps - the ring steps are 12, 14, 16 and 16 px, median 15 px; on the
  Hoshigaoka map it landed on the first ring due north, at map (392, 1020). (observed 2026-09-20; method: the map's placement code and its recorded manifest, read by hand)
- The torii avenue's points march 15 px apart; the one torii the map records stands 22 px from the
  hall's center, 10 px in front of the hall's face.
- A tree crown in the manifest is a circle of radius 3.7 to 7.8 px in the crowns read; a grove clump
  is a point with the grove's radius, 14 px.
- The map's scale is 2 ft per px (`meta.ftpx`), so 15 map px is 30 ft; a sheet at 3 px per ft draws
  that as 90 sheet px.

**Decision.** The grain is 15 map px - the median ring step, which is also the avenue pitch - and it
is stated in MAP px, so the same check serves a hamlet map (1 ft per px) or a city map (3 ft per
px) without a second number. `m:map-grain`. A sheet feature whose mapped center lies within the
grain of a map feature of a corresponding class is that feature; a map feature inside the sheet's
frame with no sheet feature within the grain is missing; the subject's footprint matches when each
side is within ONE map px of the map's - the map records a footprint to the pixel and the sheet can
draw it exactly, so the placement grain, which is for a position the map found by search, is not
the size's tolerance. The number lives in the check beside its reason and is not
repeated in the record (the record's page is not touched by this feature).

## R2. What the map records, by class, and how each is shaped

**Question.** The check reads the map's recorded manifest, never the generator. Which manifest keys
correspond to what a sheet draws, and where is each feature's position?

**Read from `legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json` (2026-09-20).** Every
position is the feature's CENTER in map px unless said otherwise:

| sheet class (how the sheet marks it) | manifest key(s) | shape |
|---|---|---|
| tree (a canopy circle, by its fill or a `trees` group) | `tree_crowns` | a flat list of `x, y, r` triplets |
| | `village_groves[*].clumps` | points, each a clump of the grove's radius `r` |
| | `forest_patches` | none on this map; read as `x, y, w, h` when present |
| burial ground (`id="burial_ground"`) | `cemeteries` | `x, y, w, h, rot` |
| well (`id="well"`) | `wells` | `x, y, r` (`shrine: true` marks the shrine's own) |
| arch (`id="arch"`) | `torii` | `[x, y, id]` triples |
| water (`id="water"`) | `streams`, `channels` | `poly` point lists with a width `w` |
| | `pond` | a pond polygon (a point list); `crescent_ponds` `cx, cy, r` |
| lane (`id="lane"`) | `lanes` | `pts` point lists with a width `w` |
| another building (`id="building"`) | `houses`, `byres`, `farm_sheds`, `storehouses`, `buildings` | `x, y, w, h, rot` |
| the subject | the declared key, e.g. `religious` | `x, y, w, h` (`kind`) |

The subject's position is its center: the Hoshigaoka shrine is `religious[0]` at (392, 1074), 30 by
24 px - 60 by 48 ft - and its torii at (392, 1096) stands 10 px beyond the hall's south face, which is
only possible if (x, y) is the center. The map's `meta.ftpx` gives its scale. (observed 2026-09-20; method: the map's placement code and its recorded manifest, read by hand)

**Decision.** The class table is data in the check (plan D2), one row per sheet class; a class the
sheet marks that the table lacks is a finding ("the sheet marks `id="pond"` and the check knows no
such class"), so a new class is added deliberately.

## R3. What the Hoshigaoka map shows at the shrine - the inventory the sheet must match

**Read from the manifest, every feature within 160 map px (320 ft) of the shrine's center, and the
map's own render (2026-09-20):** (observed 2026-09-20; method: the map's placement code and its recorded manifest, read by hand)

- the shrine hall, 60 by 48 ft, its long side east-west, facing south; (observed 2026-09-20; method: the map's placement code and its recorded manifest, read by hand)
- ONE torii, 20 ft south of the hall's face, on its axis - the generator's comment promises a
  seven-arch avenue but the manifest records `torii_count: 1` and the render draws one (reported to
  the GM under spec FR-009; the sheet matches what is drawn);
- the shrine's own well, 108 ft due north of the hall's center, on its axis, behind the hall;
- swept ground: the manifest's `clearings` around the shrine cover about 292 by 272 ft - the whole
  of a sheet frame two hundred feet on a side;
- no tree crown, grove clump or forest patch inside the frame, and none near it: the nearest
  recorded tree crown is 238 ft from the hall's center, the water-mouth grove's nearest clump center
  258 ft, and the grove's drawn outline comes no nearer than 163 ft - the outline's nearest edge
  clears the frame's north edge by 19 ft (9.6 px, at x = 427), under the grain, but the outline is
  the grove's boundary, not a feature the check reads: the check reads crowns and clumps, and the
  nearest crown stands 74.6 ft (37.3 px) beyond the frame's edge, the nearest clump 96.7 ft (48.4 px),
  both well over the 15 px grain;
- NO cemetery within 320 ft: the village graveyard is about 430 ft west;
- the connector lane passes about 112 to 172 ft east of the hall's axis and comes no nearer the
  arch than 148 ft, outside a frame of 100 ft half-width; the nearest byre is 224 ft north, the
  crescent pond 340 ft north-west - both outside.

**Decision.** The redrawn sheet (spec FR-006) shows the hall at 60 by 48 ft (observed 2026-09-20; method: the map's placement code and its recorded manifest, read by hand), the arch 20 ft in front
of it, the well 108 ft behind it on the axis, swept ground to the frame's edge, and nothing else the
program lists as surroundings; its frame is held to 100 ft either side of the axis and from 60 ft in
front of the arch to 20 ft behind the well, so the lane, the grove, the pond and the byre stay outside
it and the check's second direction (map features inside the frame) has exactly the three features
to find. The fence, the sanctuary, the kitchen garden, the privy and the fire-water are below the
map's resolution and are the program's; the basin beside the approach is dropped, because the map
draws the shrine's one well behind the hall and a second water point on the sheet would be a thing
the map does not show (the well item's label admits `basin`, so the program stays complete).
