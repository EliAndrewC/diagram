# Research - 224 clip the throw, the glossary scan, and the drop's last pass

## R1 - the before (from specs/223 research R2 and this feature's own measurements, 2026-09-11)

After feature 223, seconds per pool hamlet (inashiro / kashikawa / kuwabata / mizuguchi / sawada): regen 9.7 /
12.1 / 10.3 / 8.4 / 14.3; `stage_hinterland` 1.3 / 1.8 / 1.4 / 1.1 / 1.8; `flush_blade_groups` 0.17 / 0.21 /
0.16 / 0.14 / 0.23; `drop_offmap` 0.22 / 0.21 / 0.15 / 0.20 / 0.20; the explanations step 0.35 / 0.32 / 0.38 /
0.32 / 0.30. The commons scatter under cProfile (2026-09-10, Kuwabata): `commons` 3.15 s profiled, `_sparse`
143,604 calls at 1.7 s profiled, `random.uniform` 1.0 million calls; Inashiro's SVG held 259,978 blade subpaths
before 223's cull and 49,465 after it - the ~80% culled were thrown, keep-out-tested and drawn for nothing.

The explanations step, profiled on Inashiro's manifest: `explanations` 0.005 s, `place_card` 0.001 s,
`json.dumps` 0.000 s, `glossary_for` 0.333 s - 729 `re.search` calls (0.276 s in the pattern searches, 0.053 s
compiling them) over the joined explanations text, for 44 glossary terms present of the vocabulary's.

The frame against the content: on the five pool maps the view reaches 19-194 px past the bounding box of the
houses, the fields and the pond (`title_band` None, no outside title pocket on any) - the dry hem, the
farm-yard rects and the crop's 48 px margin account for it; the prediction of FR-001 reads the crop's own
boxes, so its overhang is what R2 measures.

## R2 - the after (2026-09-11)

The same measurement as 223's R2 (the phase marks in a detached worktree of the feature's first commit, each pool
gen alone; a settlement-review's own renders ran on the box for part of it):

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| `stage_hinterland` (was 1.3 / 1.8 / 1.4 / 1.1 / 1.8) | 0.61 | 0.62 | 0.60 | 0.63 | 0.63 |
| `flush_blade_groups` (was 0.17 / 0.21 / 0.16 / 0.14 / 0.23) | 0.07 | 0.05 | 0.05 | 0.07 | 0.05 |
| `drop_offmap` (was 0.22 / 0.21 / 0.15 / 0.20 / 0.20; see the note) | 0.17 | 0.12 | 0.10 | 0.17 | 0.12 |
| explanations + json blob (was 0.35 / 0.32 / 0.38 / 0.32 / 0.30) | 0.06 | 0.06 | 0.06 | 0.06 | 0.05 |
| the picture's four tiles | 0.97 | 0.83 | 1.26 | 1.00 | 0.69 |
| regen total (was 9.7 / 12.1 / 10.3 / 8.4 / 14.3) | 8.7 | 10.3 | 9.1 | 7.7 | 12.7 |

SC-1: the hinterland stage 0.60-0.63 s on every map (under 1.0 / 1.4). SC-2: the explanations step 0.05-0.06 s
(under 0.1). SC-3: `drop_offmap` under 0.1 s on none - 0.10-0.17 (the row above is the re-measurement after the gate's
coverage floor found the direct parse had never fired: the element regex leaves a leading space on the attribute
string and the anchored per-tag regexes did not allow it; the first measurement, 0.10-0.21, was the general parse
alone). The direct parse takes a fifth off; what is left is the per-string regex scan itself (`_PATH.sub` and
`_SHAPE.sub` over every classed string, the reviewer's aside) and the elements the pad band still carries -
reported, not chased. SC-4: 1.0 / 1.8 / 1.2 / 0.7 / 1.6 s saved - Mizuguchi 0.3 s under
the 1 s bar. The SVG: 2.52 / 1.98 / 2.03 / 2.43 / 1.86 MB (3.4-4.5 after 223).

The prediction against the frame. On the five pool maps the view's tightest side is exactly the 120 px pad inside
the predicted frame (`meta.scatter_frame_overhang` -119.6 to -120.2 on at least one side of every map), which says
the crop's boxes at hinterland time ARE the final ones there - the pad is all slack. The first 48-map cohort found
the case the pool did not: four elongated seeds (13, 24, 46 and one more) whose sheet had no room for its name
grew the TITLE BAND above the map after the crop (138 px) and reached 5.6-6.4 px past the pad on the north side.
Two things followed: the prediction's top edge now carries the band's full height (`TITLE_BAND_ALLOWANCE` 140),
and the breach is judged per scatter on the ground its parcel covers inside the view - the first form compared the
view against the tightest frame regardless of where the parcel lay, and would have flagged the marsh's early frame
against a band the marsh never neared. The second cohort's verdict is below.

The second cohort, with the band allowance and the per-scatter judgment: **48 of 48 passed the whole gate**, no
`scatter_frame_breach` on any seed. The pool's five: no breach, the tightest side still the 120 px pad, the north
side now 260-564 px inside the frame.

The perf bookends: 224-end vs 224-start on the reference hamlet's four seeds -10.9% total (31.1 -> 27.7 s), every
seed faster, band 0.

## R3 - the settlement-review's measurements, and the pad's argument (2026-09-11)

The review (over the shipped SVGs at 832a506d, its own raster of each, against main's renders) adjudicated every
scatter base against the recorded keep-out geometry at zero pad: **0 bases on crop plots, structures, lane treads or
water on all five maps, before and after; 0 brush dots and 0 pines on bog-tinted pixels; 0 reeds on water; 0
scatter bases inside the cluster's hull.** In-view density per 1,000 sq ft, main -> shipped: blades 10.55 -> 10.47 /
5.43 -> 5.48 / 3.55 -> 3.50 / 10.21 -> 10.27 / 4.53 -> 4.61 (inashiro / kashikawa / kuwabata / mizuguchi / sawada),
reeds 4.75 -> 4.69 / 3.71 -> 3.65 / 3.26 -> 3.26 / 5.20 -> 5.34 / 3.92 -> 3.78, dots and pines within a hundredth,
crowns identical; the wet-tint discs 1513 -> 1494 / 1096 -> 1114 / 727 -> 727 / 1690 -> 1620 / 1083 -> 1100 at an
unchanged mean radius. The edge-band density (the outer 40 px of every side) holds within 10% on every side of every
map; no bare strip. The same place, five for five.

**Why 120 px suffices laterally - the enumeration the review asked for.** The prediction is the crop's own boxes at
hinterland time plus every polygon the crop can later take in. What is placed AFTER the hinterland: `stage_bamboo`
draws the stands on `plan.bamboo_polys` (in the prediction; not in `_CROP_HARD` anyway); `stage_woodland` draws the
coppice patches on `plan.woodland_polys` (in the prediction; they ARE hard, as `forest_patches`); `stage_windbreak`
draws the belt on `plan.belt` (in the prediction; the crop reads its inner face plus the margin); `stage_crossings`
seats footbridges on water inside the frame (not hard); `stage_notice` seats the board on a lane's verge among the
houses (not hard); `stage_labels` runs after the crop. So no hard feature unknown at hinterland time grows the crop
laterally at all - which is what the pool shows: the tightest side is the pad exactly on every map, the prediction's
non-pad part coinciding with the view. The one late grower is the title band, on the north only, covered by
`TITLE_BAND_ALLOWANCE`. The widest scatter mark is the wet tint's 28 px radius against the 120 px pad, so no skipped
throw could have painted into the view. The pad is slack, kept as slack, and the breach record is what would say so
if a later placer changed this.

**A pre-existing thing the review noticed, not this feature's.** A few brush dots and pines stand inside a recorded
`marshes[].poly` on every map (Kuwabata 3 dots and 1 pine after; 4 dots before) while 0 stand on drawn bog: the
recorded polygon is the parcel's outline and `_in_soft` tests the feathered interior, so the two describe different
ground. The doctrine (woody never in the bog) is about the drawn bog and holds; whether the record and the test
should ever disagree is a code question, left here for whoever next touches the marsh.

**And a convention to state:** since this feature the SVG's scatter is a function of the PREDICTED frame, not of the
parcel: a map re-cropped wider than its recorded view would find bare ground from 120 px out. Recorded at
`scatter_frame`.
