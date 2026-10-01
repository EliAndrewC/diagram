# Feature 294 - engineering scout: FR-003 / FR-004 rules (read-only, 2026-10-01)

Clone `/diagram/.clones/diagram-review`; paths below are relative to `.claude/skills/diagram/`. Pool manifests read from the
clone (byte-identical to the mirror's for all five hamlets); rendered SVG/HTML read from the mirror
`/diagram/.claude/skills/diagram/pool/...` (gitignored, so a gate test must read them through `tests/gate/_pool.obtain(gen)`,
as `tests/gate/test_covers_298.py` does). Measurement scripts are in this scratchpad (`rec.py`, `ruled2.py`, `wood.py`,
`twin.py`, `tread.py`, `law.py`, `hitshare.py`).

**Template for every pool-manifest/SVG gate test**: `tests/gate/test_covers_298.py` (parametrized over
`pool/hamlets/*/*.gen.py`, `_pool.obtain(gen)` -> manifest path, `.svg` beside it). Pure-manifest checks can live in
`tests/gate/` the same way (`tests/gate/test_farm_groves.py`).

**Data facts verified**
- The settlement SVG carries NO per-element class or id (`grep class=` finds only `class="scale"`). The class link lives in
  the HTML page: 2,423 `<g class=".." data-k="<class key>">` wrappers on Inashiro, from the side-list `ClsTag`
  (`interactive/tags.py`) that `settlement/finish.py:880-911` keeps in step with the SVG body. There is NO per-RECORD link
  (no manifest index on an ink element) - only per-CLASS.
- `M["ink_classes"]` (finish.py:904) is a per-class element COUNT (`ink_census`), no geometry.
- Topology records vs drawn records exist side by side for water: `channels` (topology, hairline 2.5) vs `drawn_channels`
  (`pts`, `w0`, `w1`, `bedz`), `streams.poly`, `pond` = `[cx, cy, rx, ry]` (`hamletgen/sink.py:99-103` says so in words).
- `meta.view` = `[x, y, w, h]`; canvas `meta.W/H` is much larger (padding).

---

## 1. Record against ink

**Link available**: per class only (HTML `data-k`), plus the manifest's own topology-vs-drawn pairs for water. No ids.

**Narrowest general test (two layers)**
- (a) MANIFEST layer, cheap, `tests/gate/test_record_against_ink.py`: for every key with a drawn twin, the record lies on its
  drawn ink. Water: each `channels[i].poly`, clipped to the canvas, minus the union of `drawn_channels` buffered by
  `max(w0,w1)/2 + 1`, `streams` buffered `w/2 + 1`, and the `pond` ellipse, must have length <= 3 ft. Point records
  (`sluice_gates`, `weirs`, `bridges`) within 2 ft of water ink. Houses/byres/sheds vs `marshes[*].poly`: zero intersection.
- (b) PIXEL layer for kinds with no drawn twin in the manifest (marsh hit polygon, toe polygon): render each class flat
  (fork's `hitshare.py` approach, `raster.id_map` via resvg, no browser) and require a record's footprint to be >= 0.9 its
  own class's ink. Effort M; share the renderer with item 7.

**Measured (a)**: Inashiro and Mizuguchi drain `channels[1]` run ~71 ft past the drawn stroke - INTO the pond centre, which
the pond ellipse covers, so they pass once the pond is counted. **Kuwabata `channels[1]` (pond -> polder supply) has 101 ft
off all water ink** (vertices 3293,2003 -> 3275,2022 -> 3293,2095: a jog the drawn stroke does not take). Unless the dike
culvert or sluice ink stands there (not in `drawn_channels`), Kuwabata FAILS today. Sluice gates: 0.0 ft from ink (the
7 ft snap case is closed). Houses touching any marsh record: 0 on all five maps.
**Seed**: shift one `drawn_channels` vertex 10 ft, or append a 20 ft tail to a `channels` record.
**Norm**: map drawing convention (the record IS the drawing); tolerance 3 ft = GUESS (one drawn ditch width).
**Effort**: (a) S, (b) M.

## 2. Ruled or plumb edges on non-brook shapes

**Home**: gate test reusing `hamletgen/water/brook_rules.py` (`straightest_run`, `RULED_TOL_FT` 3.1, `RULED_SHARE` 0.4,
`RULED_MIN_LEN_FT` 300; `axis_segments` idea with `AXIS_EPS_DEG` 1.6) over `marshes`, `commons` (woodland), `village_groves`,
`groves`, `bamboo_stands`, clipped to the view, with edges lying on the view edge removed. Nearest test:
`tests/hamletgen/test_brook.py::test_the_ruled_share_is_judged_inside_the_view`. For the shrine grove and the precinct
clearing, those are on the Mode A sheet (`pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg`,
`data-kind="shrine grove"` / `"precinct clearing"`, `<path d="M.. L..">`), so that half is a pack_audit registry check.
**Measured on the RECORDS (in view)**: toe marshes have straight runs of 739-1,147 ft (18-39% of their in-view edge;
Kashikawa 39%, just under 0.4); axis-aligned record edges of 450-590 ft on Inashiro and Mizuguchi toe and Kuwabata waterside
marshes; 252 x 168 ft axis rectangles notched into the toe (a keep-out box). Grazing `commons` and the `copse` records have
1-6k ft axis edges - but those are cover regions under other ink.
**Not decidable from the record**: what matters is the VISIBLE edge, and most of these record edges lie under the field,
lanes or scrub ink. A sound test must read the boundary between the marsh class and the ground/scrub class in a per-class
raster (item 7's renderer), then apply the brook's straightness predicate to that traced boundary. Pool status: unknown
(record says it would fail the axis rule on 3 maps).
**Seed**: replace a marsh poly's free edge with a two-vertex 400 ft segment. **Norm**: the brook's W03/W04 constants
(GM's August ruling on Sawada; map drawing convention). **Effort**: M (raster) / S on records (wrong answer).

## 3. Woodpile seating

Since feature 280 M21 the woodpile is a **wood shed of its own** (`hamletgen/homesteads/fixtures.py:70-74`): the eaves stack
and the kizuma are MODERN-ONLY and not drawn. So "end-on to the wall" and "off the wall" (ledger 2026-08-27) are retired
with the glyph. What survives: the shed stands on its own household's ground, raked with its house.
**Home**: placer guarantee in `hamletgen/homesteads/fixtures.py` (the seat is a fixed local-frame offset), with a gate
assertion over `farm_fixtures` (`kind == "woodpile"`, `of` = own house centre). Nearest test:
`tests/hamletgen/test_fixtures_287.py::test_a_bath_room_is_drawn_at_its_laid_size_with_its_wall_and_a_flank_seat_along_its_flank`.
**Predicate**: distance to own house < distance to any other house/retirement house/shed/byre; |rot - house rot| mod 90 <= 2 deg.
**Measured**: 32 sheds across five maps, gap to own wall 9.4-16.8 ft, never nearer a neighbour, skew 0.0 deg. PASSES.
**Seed**: move one shed's `of` to a neighbor, or rotate it 90. **Norm**: research/questions/0043-firewood-stacks-and-sheds-kigoya.html and 720 (the shed); the
"nearer its own house" rule is a GUESS. **Effort**: S.

## 4. Parallel twin watercourses 12-32 ft apart

**Home**: gate test over `drawn_channels` + `streams` (the drawn ink). Predicate: for each pair, the longest run with
centreline distance 12-32 ft, bearings within 15 deg, inside the view and > 60 ft from where they touch, must be < 60 ft.
**Measured**: FAILS 4 of 5: Inashiro dc6/dc9 190 ft, Kashikawa dc7/dc10 310 ft, Mizuguchi dc7/dc10 205 ft, Sawada dc6/dc9
270 ft - every pair is two `field_ditches` role `branch` (w0 2.4 and 1.8). The ledger's 2026-08-28 "twin branch canals ~25 ft
apart (pre-existing)" is still on every comb map.
**Norm**: none found; the band is the reviewer's observation; thresholds GUESS. Two branches leaving the main near each other
may be legitimate - this is the item most likely to be a judgment (it goes back through the audit if research says so).
**Seed**: copy a branch 20 ft sideways. **Effort**: S to write, M+ to make the pool pass (a comb-branch spacing rule in
`waterfields`).

## 5. Draw order and translucency ghosting

**Already covered in part**: `tests/settlement/test_finish_287.py::test_no_bed_is_painted_above_a_sheen_and_the_pond_fill_over_every_mouth`
(the sheen-cap case: `water_sheen_zmin > water_bed_zmax`, recorded in every manifest); feature 298's
`tests/gate/test_covers_298.py` pins the cover tiles at the bottom of the stack.
**New rule (translucency registry)**: gate test over the HTML page: every primitive with an effective opacity < 1
(`opacity`, `fill-opacity`, `stroke-opacity`, including an ancestor `<g opacity>`) belongs to a class on an allowlist with
its reason. Today's census: lane wear (0.4/0.9 tread pair), well curb 0.55, bund beans 0.85, holdings stroke 0.8, Kuwabata's
dike plantings 0.35-0.95, the grass pattern 0.85. No 0.94 placard and no 0.9 mound exist now (both were fixed).
**Seed**: set the field-grave mound back to `opacity="0.9"` (the recorded case) - a class not on the list fails.
**Broadleaf over conifer**: `tree_crowns` is `[x, y, r]` only (no species), so not decidable from the manifest; needs the
crowns' z-order with their fill colours from the SVG - GUESS-level, defer.
**Norm**: map drawing convention. **Pool passes**: yes once the allowlist is seeded from today's census. **Effort**: S-M.

## 6. Reed-fringe gaps

**Obsolete after feature 298** (`specs/298-tiled-ground-cover/spec.md` FR-002: each marsh is ONE shape filled with a
repeating reed tile; tasks all ticked). Density, empty sectors and thin waterlines cannot occur in a uniform tile. The only
residue is a hole or notch in the marsh shape, which is item 1 (record against ink) and item 2 (its edges).
`tests/gate/test_covers_298.py` already asserts no reed is drawn one by one. Verdict: CUT, covered.

## 7. Page hit regions - see the fork's section (appended below)

## 8. Lane tread to house-wall clearance

**Existing**: `settlement/houses.py:263` (`_house_on_a_tread`) refuses a drawn corner within `half + 2.0` ft of a tread
centreline - a 2 ft hair from the tread's edge; `hamletgen/ways/clearance.py:_clear_touch` uses the same figure. So the gate
allows 2 ft; the reviewer flagged 3.85 ft.
**Home**: raise the hair at the one predicate (`houses.py` tread test and `law`), plus a gate test over `lanes` (`pts`, `w`)
against `houses`, `retirement_houses`, `farm_sheds`, `byres` rectangles. Nearest test: `tests/hamletgen/ways/test_sweeps.py`
(houses_clear_of_lanes).
**Measured** (tread edge to wall): minima Inashiro 7.3, Kashikawa 27.5, Kuwabata 11.9, Mizuguchi 26.9, **Sawada 4.94 ft**.
At a 6 ft threshold Sawada fails once; at 4 ft all pass.
**Norm**: research has a three-shaku (~3 ft) eaves strip (inubashiri) "required before townhouses facing a public" way -
found by grep in research/buildings; it is a TOWN figure and an eaves overhang must be added, so a hamlet threshold is a
GUESS anchored on it (e.g. eaves 3 ft + 3 ft). **Effort**: S (test) + engine change if > 4.9 ft.

## 9. Privy seat and wind

**Not a defect class**: research/homesteads/220 ("The outhouse faces the SUN, not away from the wind - and 72.7% of them
do") searched for a wind rule and found none ("No source, in English or Japanese, was found stating any general wind rule
for koedame or benjo siting"). The seat is a researched roll with no wind term:
`tests/hamletgen/test_homesteads.py::test_the_privy_seat_weights_are_rolled_per_hamlet_over_the_four_attested_seats`,
`tests/settlement/test_fixture_seats.py::test_the_privy_faces_the_sun_on_its_share_and_takes_an_attested_seat_otherwise`,
`PRIVY_SUNNY_SHARE = 0.727` (`settlement/homestead_parts/fixture_seats.py:54`). The manure heap goes with the privy
(fixtures.py:76-80). Verdict: back to the audit as researched; STRUCK from FR-003.

## 10. Acute lane merges

**Already covered**: `hamletgen/ways/law.py` `NEEDLE_DEG = 20.0`, `NEEDLE_FT = 20.0` (`needle_ends`), plus `needle_loops`
(`NEEDLE_LOOP_FT`) for sliver faces; applied by the placer in `ways/settle.py` and `ways/last_resort.py`; tests
`tests/hamletgen/ways/test_settle.py::test_mizuguchis_needle_join_is_relaid_square`,
`::test_a_needle_of_grass_is_opened_on_its_shorter_lane`, `::test_lawful_refuses_a_needle_or_a_hairpin_at_the_connectors_start`,
`tests/hamletgen/ways/test_tree.py`. The 140 deg rule is `hamletgen/ways/clearance.py:327 _HAIRPIN_DEG = 140.0`
(`kink_spans`, aliased `law.DOUBLE_BACK_DEG`). Measured: `needle_ends`, `needle_loops`, `lanes_that_kink` all 0 on the five
maps. Gap: no gate test runs the law over the SHIPPED manifests (a 5-line parametrized test would). Effort S.

## 11. Side-by-side footbridges

**Home**: gate test over `bridges` (`x`, `y`, `rot`, `span`, `foot`, `form`); placer side is `channel_footbridges(spacing=300|320)`
(`hamletgen/frame.py:51-54`) and the web's `bridges()`.
**Predicate**: no two decks within 60 ft of each other (or within 60 ft along the same watercourse).
**Measured**: nearest pairs 124 ft (Kuwabata) to 236 ft (Mizuguchi); none within 60 ft. PASSES (the 269 E-round case was
fixed). **Norm**: GUESS (60 ft); the placer's own spacing 300 ft is a softer anchor. **Seed**: duplicate a bridge 15 ft along.
**Effort**: S.

## 12. Drawn area against rolled area

The recorded case (hamlet burial ground at 57-60% of its box) no longer exists: `hamletgen/burial.py` (feature 280 M68)
draws no hamlet ground (`meta.hamlet_burial = "village_ground"` on all five). The class survives in
`meta.homestead_wood_ft2 = {rolled, drawn}` (`hamletgen/hinterland/stages.py:469`): Inashiro 12,136 -> 14,023 (116%),
Kuwabata 13,210 -> 11,575 (88%), **Sawada 17,692 -> 10,672 (60%)**. The only rule there is a FLOOR (`HOMESTEAD_WOOD_FT2[0]`
6,000, research/vegetation/210), which all pass.
**Home**: a generic gate test over every `meta.*` pair `{rolled, drawn}` (and `*_target` vs drawn counts, item 16): drawn/rolled
within [0.85, 1.25]. **Pool**: FAILS on Sawada's wood at 0.85. **Norm**: GUESS band; the register band is 6,100-27,800 sq ft
per homestead so 60% is inside the RECORD - which may make this a deliberate shortfall the placer accepts; decide whether the
wood roll is a target or a ceiling before writing the test. **Effort**: S test, M engine.

## 13. House bearings bunching

**Research norm exists**: research/homesteads/240 (Sakamoto & Tsubaki 1985: 87% of houses within the commonest compass
point and the two either side, ~67 deg, i.e. about +-33 deg; 11% turned right, 1% each left/back) and 780 (no pre-1868
count; the map should turn each house by its lane's curve and stop drawing the quarter-turned tenth). The ledger finding
(sawada, 269 E round 1) was "9 of 16 house bearings piled at +-30 deg" - a PILE-UP AT A CLAMP, not a spread problem.
**Predicate**: no more than 2 houses within 1 deg of the largest |rot - house_bearing_deg| (no pile at a limit), and all
within +-33.75 deg of `meta.house_bearing_deg` (`meta.house_quarter_turns == 0` since 780).
**Measured**: deviations Inashiro -27..+6, Kashikawa -12..+4, Kuwabata -12..+14, Mizuguchi 0..16, Sawada -11..+13; no pile.
PASSES. **Home**: placer assertion where `houses.py` rakes (`_house_rot`), or a gate test over `houses[*].rot`; nearest test
`tests/settlement/test_bearing.py`. **Effort**: S.

## 14. Brook share off the frame

**Measured**: the brook's share of its on-canvas length outside the view is 0.37-0.67 on all four brook maps - this is the
canvas padding (a brook runs off-map to off-map by construction, `brook_rules.ends_off_canvas`), not a defect. The recorded
defect was the brook leaving and RE-ENTERING the view ("67% of Sawada's brook off-frame in three pieces", 230 pass 3).
**Predicate**: the brook's intersection with `meta.view` is ONE piece (at most 2 if a declared form needs it), and its in-view
length >= one view side's length. **Measured**: 1 piece on every map, 2,170-3,368 ft in view. PASSES.
**Home**: gate test over `streams[*].poly` + `meta.view`; nearest `tests/hamletgen/test_brook.py::test_the_ruled_share_is_judged_inside_the_view`.
**Norm**: map drawing convention / GUESS. A share-off-frame threshold as such is NOT meaningful. **Effort**: S.

---

# Items 7, 15, 16, 17 (sub-scout)

# Feature 294 scout - Mode B items 7, 15, 16, 17

Paths relative to `.claude/skills/diagram/`. Measurements: Python one-offs over the mirror's rendered pages
(`/diagram/.claude/skills/diagram/pool/hamlets/*/*.html`, 2026-10-01 10:08); the scratch script is
`scratchpad/hitshare.py`.

## 7. Page hit regions (a class winning only part of its own ink)

**Computable without a browser: yes.** `interactive/raster.py:id_map(svg, class_keys(svg))` renders the page's
class id map with the resvg CLI (`/usr/bin/resvg`): one flat palette color per class group, hit geometry included,
opacity stripped, anti-aliasing off, at 1 px per map px. It returns `(png, {red value: key})`. The module docstring
says it agrees with the DOM's own hit-testing on 98.2% of a grid of points. It takes 0.1-0.2 s a map.

**Own ink, measured.** Render the same SVG with only class K painted (`_recolor_group` on its group with the
`class="hit"` elements and `<g class="hit">` stripped, every other group `_unpaint`ed). The mask is alpha > 0.
`share(K) = |mask AND idmap==K| / |mask|`. This is one resvg render per class (33-37 a map), about 1 min a map.

**Measured on the 5 hamlets.** Classes under 0.9:

| class | share | top thief |
|---|---|---|
| paddy | 0.34-0.41 | bund (by design: Split + widened bund) |
| wet paddy | 0.29-0.46 | bund (by design) |
| bund | 0.67-0.75 | bund beans (by design: HIT_PRIORITY) |
| storage shed | 0.70-0.82 | farmhouse, on every map: a real candidate |
| byre | 0.82-0.83 | retirement house or privy (Mizuguchi, Kashikawa) |
| notice board | 0.71-0.75 | mostly unpainted (its text and frame) |
| Sawada fallow | 0.39 | bund |

On **Kuwabata**, the mulberry dike takes 78% of the bund, 44% of the wet paddy and 31% of the paddy. Paddy keeps
only 0.10 and bund 0.00. This is very likely a real defect: a lifted or late region over the fields, of the same
shape as the GM's "lifted layer 88% of a sty". No sluice box is on today's pool (M57 retired the pond sluice).

**Home.** A gate test over the shipped pages, marked `renders`, one parametrized case per map. Copy the
pattern of `tests/interactive/test_raster.py::test_the_id_map_paints_every_class_and_its_hit_geometry_flat_and_nothing_else`,
which already runs `id_map` on synthetic SVG. The pool walk would follow `tests/gate/test_pool.py`. The pages are
gitignored, so the test needs the rendered `.html`, or must call `render_page` from the manifest and SVG. Use the
mirror's artifacts the way the existing pool gates do.

**Predicate.** `share(K) >= 0.80` for every class, except a thief/victim pair declared intentional. The
intentional pairs are derivable from `Split` pairs plus `HIT_WIDEN`/`HIT_PRIORITY` in `interactive/page.py:312-358`:
paddy/bund, bund/bund beans, wet paddy/bund, fallow/bund. Also exempt a class whose missing share is UNPAINTED
rather than stolen (notice-board text).

**Norm.** GUESS. The 0.8 sits under the worst undeclared share measured today: storage shed 0.70 fails, byre
0.82 passes. The reviewer's 42% and 88% cases sit far beyond it. Alternatively, use "a non-declared thief takes
at most 0.25": the shed's farmhouse is at 0.18-0.20.

**Seeded fault.** Append a `<g class="f f-x" data-k="mulberry dike">` region polygon over a paddy in a synthetic
page. Alternatively, move the hit layer above the ink.

**Pool passes?** NO. Kuwabata fails (mulberry dike). Storage shed (0.70 on Kashikawa) fails at 0.8 and passes at
"thief at most 0.25".

**Effort.** M.

## 15. FR-004 - typed counts in notes prose

The existing coverage is `tests/test_notes_census.py`:
- It checks the generated `<!-- census -->` block (from `tools/notes_census.py:census` - windbreak and copse
  clumps, farmhouses, family form, fixtures, board) against the manifest.
- It requires the block on the 5 hamlets.
- Prose outside the block is unchecked.

**Measured.** The notes are long design journals: Inashiro 1,878 lines, the 5 hamlets 5,688. A pattern
`<digit|one..twenty> <kind>` for the kinds farmhouses, houses, households, farmsteads, gardens, privies, wells,
footbridges, byres and persimmons, run outside the census block:

| map | agree | disagree |
|---|---|---|
| Inashiro | 25 | 15 |
| Kashikawa | 16 | 9 |
| Kuwabata | 9 | 8 |
| Mizuguchi | 17 | 11 |
| Sawada | 18 | 12 |

A sample of the "disagreements" shows they are mostly NOT totals: "6 gardens re-seated", "eight of fifteen
footbridges", "two households across an unbridged...", and dated history of earlier rolls. A free-prose regex is
**not decidable**: it cannot tell a current total from a subset, a delta or history.

**Narrowest decidable rule.**
- Every current-state count in prose is written as a derived inline token, e.g. `**15** farmhouses<!-- c:houses -->`.
  Alternatively, it goes in the census block, whose `census()` gains rows: gardens, wells, footbridges, byres, ponds.
- A test checks every token against a `COUNTERS` map from token name to a manifest lambda. The `census()` key
  logic is the source; the farm_fixtures kinds are already counted there.
- A second test refuses a bare `<number> <counted-kind>` inside a section headed current or as-shipped, while
  dated or journal sections are exempt.

**Home.** `tests/test_notes_census.py` (extend) and `tools/notes_census.py`.

**Seeded fault.** Edit a token's number in a tmp copy.

**Pool passes?** The token rule is vacuous until tokens are written. The bare-count refusal would fail every
hamlet until the prose is converted.

**Effort.** M. The prose conversion is the cost.

## 16. Declared knobs / rolled forms drawn as declared

**287.** H33 is a recorded decision: no woodpile-form knob (280 M21). H34 (the bath a room joined to the house,
the rolled wall tried FIRST) and H35 (an eaves woodpile within the wall gap) are "recorded decisions". See
`specs/287-placer-guarantees/research.md:828-830` and `plan-rules.md:131-133`.

**Existing coverage.**
- `hamletgen/homesteads/fixtures.py:record_drawn_forms` writes `meta.bath_seats_drawn`, and
  `tests/hamletgen/test_homesteads.py::test_the_drawn_forms_are_recorded_beside_the_rolled_knob` tests it.
  Nothing compares drawn against rolled.
- `settlement_form` against `settlement_form_asked`, and `row_water_drawn`/`farm_water_drawn`, are recorded.
- `tests/settlement/test_grove_sides.py` has predicates for the grove sides (`test_the_predicates_catch_a_missing_side...`).
- `tests/hamletgen/test_plan.py::test_every_declared_knob_is_honored_over_its_roll` tests the knob value, not the drawing.

**Measured against the pool manifests.**
- byre_target equals the byres drawn on all 5 maps.
- retirement_target equals the retirement houses drawn.
- settlement_form equals settlement_form_asked on all 5.
- Fixtures target against drawn: equal on 4 maps. **Kuwabata is short:**

  | fixture | target | drawn |
  |---|---|---|
  | privy | 14 | 11 |
  | woodpile | 7 | 6 |
  | manure | 7 | 5 |
  | bath | 5 | 2 |
  | coop | 13 | 11 |
  | shrine | 1 | 0 (below `farm_fixtures_min.shrine` 1) |
  | persimmon | 15 | 12 |

- bath_seat against drawn: Kuwabata rolled `main_door` and drew `stable_end` x2; Sawada rolled `main_door` and
  drew `stable_end` x4 plus `floored_rooms` x1. Both are legal under H34 ("rolled wall tried first", fallback
  allowed), so a strict equality test is wrong.

**Predicate.** A gate test over the pool manifests:
- (a) for every `X_target`, `len(drawn X) == target`, and every `farm_fixtures_min` is met;
- (b) `settlement_form == settlement_form_asked`;
- (c) a bath seat drawn other than the rolled one is recorded with its refusal reason (a `bath_seat_fallbacks`
  count), or its share is capped;
- (d) `grove_sides` matches the faces planted (reuse `test_grove_sides` predicates on the manifest).

**Norm.** The roll itself (GM 2026-08-24: "a rolled knob is honored by what is drawn").

**Seeded fault.** Drop one record from a manifest copy.

**Home.** A new `tests/gate/test_declared_forms.py`, copying `tests/gate/test_farm_groves.py` (a pool-manifest
walk).

**Pool passes?** NO. Kuwabata fails (a). Kuwabata and Sawada fail (c) as strict equality.

**Effort.** S for the test. The Kuwabata shortfall is the engine's to fix or record (287's "stragglers dropped"?).

## 17. Every pool map has a notes file

All 11 pool folders (5 hamlets, 1 country shrine, 5 magistracies including `ochiba-roundtrip-test`) carry
`<name>.notes.md`, and all 18 legacy folders do too. No test asserts it generally:
`test_the_pool_hamlets_all_carry_a_census_block` covers the 5 hamlets indirectly.

**Predicate.** For every `pool/*/*/` directory with a `<name>.gen.py`, `<name>.notes.md` exists and is non-empty.

**Home.** `tests/gate/test_pool.py`, or beside the census test.

**Seeded fault.** A tmp pool dir without notes.

**Pool passes?** YES.

**Effort.** S.

---

# Mode A items 18-26 and sheet production (sub-scout)

# Feature 294 recon - Mode A items 18-26 (read-only)

Paths below are relative to `.claude/skills/diagram/` in the clone `diagram-review`.
Measurement scripts: `scratchpad/modeA/measure{,2,3,4,5}.py` (they import the engine read-only; nothing in the repo was written).
The two generated sheets were emitted into `scratchpad/modeA/` by calling `compound.place` + `emit_svg` directly, not by running their gen.py.

## How Mode A sheets are produced, and what a new failing check costs

- **Hand-authored and tracked (4):** `pool/magistracies/{hayakawa,ochiba,ubame}-magistracy/*.svg` and `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg`. Their gen.py never writes the svg. It places the declared captions (`labels.hand_sheet.placed`), renders the png, and writes the page (`interactive.sheet.write_sheet_page`).
- **Generated exceptions (2):** `county-magistracy-example` (`compound.county_magistracy_program()`) and `ochiba-roundtrip-test` (`ochiba_program()` in its gen.py). Both go through `compound.place` + `compound.emit_svg`, and both are listed under `generated_exceptions` in `buildings/types.json`. Their svg is gitignored, and `tests/_sheets.fresh` regenerates it whenever it is stale.
- **Where the gate runs:** `tests/test_mode_a_sheets.py::test_every_mode_a_sheet_passes_its_checks` runs every check in `tools/pack_audit/registry.py` (a `Check(name, run, shared, fixture, fix)`) against every live sheet. `tests/tools/test_registry.py` adds two tests: `test_every_check_fires_on_its_red_fixture`, which needs the fixture at `tests/fixtures/<sheet>-<defect>-red.svg`, and `test_every_check_passes_the_pool_sheets_of_its_tiers`. A per-type check must also be named in the tier's `checks` list in `types.json`, or `test_names_are_unique_and_declarations_name_registered_checks` fails.
- **If a new check fails a hand sheet:** someone edits the tracked SVG by hand and adds a dated entry to its `.notes.md` journal. Under the standing rule ("no hand-map edits in generator work; ask"), the GM may need to approve that edit.
- **If a new check fails a generated sheet:** the fix goes in `compound.py`, `compound_model.py` or `compound_parts.py`, or in the program in the gen.py. That is engine code, so it lands on the GATED route.
- **The data a check can read:** `parse.ParsedPlan` gives classified rects, `label_kinds` (byte offset to kind), `kinds`, `ids`, `tubs`, `wall_bands`, `gate_posts` and `door_rects`. `interactive.sheet.parse` gives the Node tree with `data-kind` and `data-part-of`. Ancestor kinds and part-of are needed to group rooms, doors and latrines with their building; `ParsedPlan` does not carry them today, so the parser needs a small extension (`structure -> owning kind`).

## 18. Every lodging block has a door on its wall
- **Home:** a new shared-or-magistracy check `lodging_entrances`. Nearest existing check to copy: `floating_doors` (checks.py:364).
- **Data:** `data-kind="door"` and `data-kind="genkan"` rects, plus `plan.door_rects`. Structures are grouped into touching components (gap no more than 1 px).
- **Predicate:** every component that contains a lodging kind (residence, family/lord's/guest/servants'/retainers' quarters, barracks, karo's house, hall and dwelling, the monk's rooms) has at least 1 door or genkan within 1.5 px of its outer boundary. The door must not lie wholly inside the component.
  - It has to be per component, not per block. Lord's and family quarters are rooms of the residence and have no door of their own.
- **Norm:** the `buildings.md` checklist (line 177): "every lodging block ... has a drawn entrance". This is a composition rule from the building-review sweep. It has no research entry and needs no number.
- **Seeded fault:** delete karo's house door rects in a copy of Ochiba, saved as `ochiba-lodging-no-door-red.svg`.
- **Pool:** PASSES on all 6. Every lodging component has 1-5 entrances.
- **Effort:** S-M (the component grouping is new).

## 19. Residence privy attached; privy count per functional zone
- **Home:** a new magistracy check `privies_by_zone`, modeled on `notice_board_adrift`.
- **Data:** `data-kind="latrine"` groups with `fill="#7E726A"`, and `data-part-of`. The zones are the precinct rects tagged `data-kind="inner court"` and `"outer court"`.
- **Predicate:**
  - (a) at least one latrine is part-of the residence or within 0.5 ft of the residence component;
  - (b) at least 1 latrine per court;
  - (c) the total is at least 3.
- **Norm:**
  - Research `0101` (privy built into the house) and `buildings/310`.
  - "~one per functional zone, ~3-4 for 40-60 persons" is the `buildings.md` vocabulary (lines 100-104 and 177). Its class is unstated, so treat the count as a GUESS until it is checked against the research.
- **Seeded fault:** move Ochiba's `latrine data-part-of="residence"` group 30 ft into the inner court.
- **Pool:** FAILS on 1 of 6. `ochiba-roundtrip-test` has only 2 latrines, beside the stables and the servants' quarters, and none on the residence, so it fails (a) and (c). The other 5 pass:
  - Hayakawa 5 (2 on the residence)
  - Ochiba 4
  - Ubame 5
  - county 5 (2 abut the residence)
  - Hoshigaoka 1, attached to the hall
- **Fix for the failure:** in `ochiba_program()` or in the emitter's seating of point features.
- **Effort:** M.

## 20. Tub count per wooden building (kitchen at least 2)
- **Home:** a new per-type check `fire_water_distribution`, next to `fire_water_adrift`.
- **Data:** `plan.tubs`, structures by kind, and `KURA_FILLS`.
- **Predicate:**
  - every major wooden building kind (office hall, residence component, barracks, gatehouse, compound shrine, stables, servants' quarters; for a shrine, the hall) has at least 1 tub within 3.5 ft (the adrift constant already used);
  - the kitchen has at least 2;
  - a kura has 0. `tubs_in_buildings` does not cover this: a kura with a tub at its wall passes it today.
- **Norm:** research `buildings/170` plus the `buildings.md` Fire-water section (lines 85-94). The "~8-12" total is not usable: Ubame has 19 and roundtrip 17, and the vocabulary says the count scales with the number of buildings, so check per building, not the total.
- **Seeded fault:** delete one of Ubame's two kitchen tubs.
- **Pool:** PASSES on all 6.
  - Kitchen tubs: Hayakawa 3, Ochiba 3, Ubame 2, county 2, roundtrip 3, Hoshigaoka kitchen 2.
  - If guest quarters, karo's house and retainers' quarters are added to the list, Ochiba (karo's house 0, retainers' 0) and Ubame (guest 0) fail. That list choice is the decision to record.
- **Effort:** S.

## 21. Proportion pairs on data-kind areas
- **Home:** a new shared check `size_hierarchy`, next to `size_bands` (labels.py `check_bands`; `footprint()` already gives the largest tagged structure).
- **Predicate:** area(a) < area(b) for each pair:
  - kitchen < residence (the largest living block)
  - stables < barracks
  - tax archive and storehouse < residence
  - compound shrine < residence
  - cell < barracks
  - Hoshigaoka: sanctuary < hall
  - A pair is skipped when either kind is absent.
- **Norm:** research `0116` ("the compound has a size HIERARCHY"). This is the page's own reading and is labeled as such. The pair list itself is from `buildings.md` line 172.
- **Seeded fault:** widen Ochiba's stables to 40x30 ft (1,200 sq ft against barracks 1,022).
- **Pool:** PASSES on all 6.
  - Closest pair: county tax archive 1,156 against residence 1,344.
  - Hayakawa kitchen 1,333 against its largest residence block 2,432.
- **Already partly covered:** `size_bands` holds each item's absolute band. Nothing holds pairs.
- **Effort:** S.

## 22. No compass rose, no key box, title block present
- **Home:** a new shared check `sheet_furniture`, copying `scale_bar_present` (shared.py:85).
- **Data:** `plan.labels`, `<text>` attributes, ids and data-kind.
- **Predicate:**
  - Title: there is a positioned (non-caption) bold text that is the largest on the sheet and sits above the precinct's top edge.
  - No compass: no text that is only `N` or `North`, and no element whose id or kind contains compass, rose or legend.
  - No key box: no text "Key" or "Legend".
- **Norm:** `SKILL.md` lines 165-178 (no compass rose, GM 2026-07; title 30 bold) and the `buildings.md` checklist (lines 168 and 180). These are map drawing conventions.
- **Seeded fault:** delete the title texts in a copy of Ochiba, or add `<text>N</text>` with an arrow.
- **Pool:**
  - No compass and no key box on any sheet. The two compass hits are comments saying "No compass rose".
  - The title is present on all 6, but its size varies: 30 on the three hand magistracies, 18 on Hoshigaoka, 20 on the two generated sheets.
  - "Font-size 30" as the predicate would fail 3 of 6, so use presence only, or record the shrine's size as a deviation.
- **Effort:** S. The compass test is heuristic, and nothing has ever fired.

## 23. A road stub runs to the viewBox edge
- **Home:** a new shared check `roads_leave_the_frame`.
- **Data:** `data-kind="road"` groups and paths (stroke-width), the viewBox, `wall_openings`, `_main_gate_passage`, and door rects.
- **Predicate:** each road end is one of:
  - at or past the viewBox edge (inside by no more than half its stroke);
  - within half its stroke of a wall opening, the main-gate passage or a door;
  - on another road's stroke.
  - Optional: the main gate has a road at all.
- **Norm:** `buildings.md` lines 123 and 169 ("running OFF the viewBox edge ... not a stub stopping short"). A map drawing convention.
- **Seeded fault:** shorten Ochiba's road from y 900 to y 820 (the viewBox bottom is 836).
- **Pool:**
  - Hand magistracies PASS: every end lands at an edge (-64 to 0 px), a gate (0-9 px), a door, or another road (14 px = half of 28).
  - The generated sheets draw no road at all. Under "the main gate has a road" both fail; the fix is in `emit_svg`.
  - Hoshigaoka has no road kind. Its `footpath` ends 73 px (24 ft) short of the top edge. Whether a footpath counts is unknown.
- **Effort:** S-M.

## 24. Palette role (fill) matches data-kind
- **Home:** a new shared check `palette_roles`.
- **Data:** the largest non-room rect per kind and its `fill`.
- **Norm:** the `SKILL.md` Palette table (lines 129-152). Its machine form already exists as `compound_model.KINDS` (role to fill), but nothing maps a kind to its role. That table must be written, and every kind the palette does not name (karo's house, retainers', bath, ...) is a GUESS.
- **Predicate:** the kind's main fill is in its allowed set.
  - The set is per knob form: the granary has two attested forms, `#F2EFE4` earthen kura or `url(#granary-slats)` (buildings.md line 58; Ochiba notes R18).
  - Room rects folded inside a building are excluded, using the existing `rooms_folded` logic.
- **Seeded fault:** paint Ochiba's stables `#DDB87A`.
- **Pool:**
  - A naive version flags clerks' room on all 5 magistracies (`#DDB87A` where the palette says `#E8D2A8`). These are false positives: it is a room inside the office hall.
  - It also flags the granary `#F2EFE4` on Ochiba, county and roundtrip. That is the legitimate kura form.
  - With the room fold and the granary form set, all 6 pass.
  - The check has never fired on a real defect. Low yield.
- **Effort:** M.

## 25. Gate opening width agrees with the route it feeds
- **Home:** a new shared check `gate_feeds_its_road`, next to `gate_widths` (shared.py:227), which only bounds an opening to 5-16 ft.
- **Data:** road ends as in item 23, matched to the nearest `wall_openings` entry or `main_gate_passage_ft`.
- **Predicate:** road width is no more than the opening width plus 1 ft (the tolerance is a GUESS: a 3 px authoring grain). It is one-sided: a 2 ft footpath to an 8 ft river door is fine.
- **Norm:**
  - research `0093` ("How wide was the main gate of a magistrate's post?");
  - the feature 267 pass 2 rulings recorded in the Hayakawa and Ubame svg comments ("12 ft, matching the passage through the gate range it meets", "9 ft, matching the narrowed cart gate").
- **Pool:** FAILS on Ochiba. Its approach road is 13.3 ft (40 px) and its main-gate passage 8.0 ft. Feature 267 narrowed the roads on Hayakawa and Ubame and missed Ochiba's. This is the recorded case and needs no seeding: a fixture is the current Ochiba svg.
  - Hayakawa: main 12/12, east postern 10.0 against lane 10.7.
  - Ubame: main 12/12, cart gate 9/9.
  - The generated sheets have no roads; Hoshigaoka has no wall openings.
- **Effort:** S once item 23's end-pairing exists.

## 26. mapmatch: gate direction / addressing face; require `**On map**` where the subject stands on a pool map
- **Which sheets stand on a map today:**
  - **Hoshigaoka shrine:** declared (`legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json - religious at (392, 1074) = hall`).
  - **Ubame magistracy:** stands on `legacy-hand-authored-pool/towns/ubame/ubame.json` as `manors[0]` "Magistrate's Manor" at (1980, 240), 290 x 200 ft, `gate` (1980, 340), `gate_dir` south, `gate_w` 12. That matches the sheet exactly (precinct 870 x 600 px = 290 x 200 ft; south main gate passage 12 ft). It has **NO** `**On map**` line.
  - **Ochiba and Hayakawa:** no map in the pool or the legacy pool records them.
  - Other "Magistrate's Manor" records exist in moritono, hoshizora and hirameki, but they are generic and match no sheet.
- **Trial declaration of Ubame:** run with the current `matches_map` code (`sheet_id=precinct`), it returns 11 findings:
  - 10 "tree at svg(...) has no tree on the map": the sheet's garden trees, which the town map lacks;
  - 1 footprint mismatch ("290 x 100 ft on the sheet; the map draws it 290 x 200 ft"). `by_id('precinct')` returns only the inner-court rect, so the sheet needs one id'd outline of the whole compound, or `OnMap` must take the union.
  - Clearing it means moving the sheet's trees or editing the legacy map: a GM call.
  - Note: mapmatch's `lane` class reads the key `lanes`, while the town map records `lane`, `road` and `roads`. Road agreement is therefore never checked.
- **Gate rule:**
  - **Home:** a fourth direction (e):
    - when the subject's record carries `gate` or `gate_dir`, the sheet's `_main_gate_passage` center, mapped through `Transform`, lies within `MAP_GRAIN_PX` (15) of `record["gate"]`;
    - the passage side matches `gate_dir`;
    - |passage_ft - gate_w*ftpx| is no more than `SIZE_GRAIN_PX*ftpx`.
  - **Trial on Ubame:** the gate maps to (1979, 341) against (1980, 340) and is 12 ft against 12 ft, so it PASSES.
  - **For a shrine:** the addressing face is the approach and torii line, which the existing `arch` class already matches by position.
  - **For a hamlet house:** not decidable. The house records carry `rot` but no door or front field; only `meta.house_bearing_deg` exists.
- **Required-declaration rule:** a new test in `tests/tools/test_mapmatch.py` or `test_mode_a_sheets.py`. For a sheet `<place>-<type>`, if a manifest `*/<place>/<place>.json` in `pool/` or `legacy-hand-authored-pool/` records a subject under the tier's key (`manors` for magistracies, `religious`/`shrines` for country shrines), the notes must parse a `**On map**` line.
  - The name-convention match is a GUESS. An explicit `**On map**: none` opt-out is the alternative.
  - Today it FAILS on Ubame, which is the red case.
- **Seeded fault for the gate rule:** a tmp manifest whose `gate_dir` is east (the `tests/tools/test_mapmatch.py` tmp_path pattern).
- **Effort:** gate rule S-M; required line S; the Ubame fix M plus a GM decision.

## Already covered / not decidable
- Covered in part:
  - 21: `size_bands` covers absolute sizes only.
  - 18: `floating_doors` covers a door adrift inside a building, not a missing one.
  - 20: `fire_water_adrift`, `tubs_in_buildings` and `tubs_on_wells` cover tub position, not distribution.
  - 25: `gate_widths` covers only the 5-16 ft band.
  - 26: `matches_map` covers position, class and footprint.
- Not decidable from geometry:
  - 26: a house's addressing face, because the manifest records no front.
  - 22: "no compass" is only heuristically decidable, and no sheet has ever had one.
  - 24: decidable, but every flag it raises on the current pool is a false positive until a kind-to-role table and form sets exist. Low value.
