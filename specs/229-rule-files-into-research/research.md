# Research - 229 the rule files retire into the research pages

The inventory the spec's success criteria are checked against. R2, R3, R4, R6 and R7 are filled from the
writers' reports and the source-reader verdicts as the work lands.

## R1 - the contradictions (FR-001), and what each resolves to

| # | Where it disagrees | Truth it resolves to | Owner |
|---|---|---|---|
| 1 | head-race width: `research/water.html` and `water.md` say 5.0 ft; `waterfields/frame.py` has `HEAD_RACE_FT = 6.0` with the 2026-08-17 review's reason (`sqrt(4.5² + 4.0²)` so the top three tiers do not sit within 1 ft) | the page states 6.0 ft and the reason | session (T03) |
| 2 | bell-and-drum tower: `research/urban-features.html` states the 36 ft / 30 ft finding and then "70 ft at city tier, ~60 ft at town tier" as the decision; the engine draws `px(36)`; `urban_fixtures.py:74` docstring says "county tier ~60-80 ft square" | the page's decision reads 36 / 30 ft; the docstring is corrected | session (T03, T29) |
| 3 | mulberry bush density: `archetypes.md` "attested ~1 bush per 10-20 sq ft"; the page labels it a GUESS | the page's GUESS label; nothing on the page says attested | writer (T06) |
| 4 | the Shunde township figure ("townships past 50% the same year") is struck on `research/archetypes.html` as traced to an uncited blog; `archetypes.md:42` still cites it as the evidence for `fraction` being a share of eligible ground | the `fraction` design is re-based on what the page supports (the county-wide ~4.6%); the struck claim is not revived | writer (T06) |
| 5 | `defenses.md` states as fact three things `research/cities/defenses.html` marks GUESS or unsourced (guard and inspection stations facing each other; the 52x30 gate-tower footprint; Shen Kuo 矢石相及 and the Pingyao 50-60 m spacing); the throat setback ~110-135 ft vs the page's ~20-100 ft unsourced; mamian 62x40 vs ~65x40 | the page's labels; the specification paragraphs carry the labels, not the rule file's confidence | writer (T14) |
| 6 | `fabric.md` grounds row-packing in "street frontage was taxed"; `research/cities/fabric.html` records that ja.wikipedia 京町家 disputes it | the row-packing specification moves without the tax rationale | writer (T15) |
| 7 | houses per household: `settlements.md` says the gate wants ~0.7 occupied houses per household; `hamletgen/homesteads/stages.py:32` wants 0.85-1.05x; 16 of 17 pool manifests sit at 1.00, Hikari no Sato at 0.94; `interactive/place.py:198` mis-describes Hikari | `settlements.html` states the engine's rule; the "~70 households, at least 50 houses" GM quote is a floor, not a ratio | writer (T18); `place.py` comment (T29) |
| 8 | the capital's extramural share: `capitals.md` "the wall encloses all 12,360 inhabitants"; the 2026-08-10 ruling on `research/cities/capitals.html` and `citybudget.py` put ~2.8% outside | nothing of the wrong statement moves | writer (T17) |
| 9 | `capitals.md` lists `SAMURAI_INWALL_FRAC` as open and `C_YASHIKI`/`C_TERRACE` as proposed; the engine ships 0.85, 4150, 660, plus `C_PACKED_CAPITAL = 950` and `CIRC_FRAC_CAPITAL = 0.15` | the page speaks of settled figures | writer (T17) |
| 10 | bamboo legibility floor: `vegetation.md` and `research/vegetation.html` say 20 ft; `hamletgen/hinterland/bamboo.py:24` has `BAMBOO_LEGIBLE_FT = 14.0` (the short axis) | the page states 14 ft on the short axis | writer (T07) |
| 11 | the marsh wedge below the collector: `water.md` keeps "is nevertheless correct"; `research/water.html` marks that argument superseded | the superseded reasoning does not move | writer (T08) |
| 12 | `research/cities/river-cities.html` says it is "the research behind the river, moat-junction and wharf rules" and contains no junction-angle content | the junction hydrology from `river-cities.md` lands there | writer (T16) |
| 13 | `homesteads.md:50` lists "the yard is smaller than its farmhouse" as live; `homesteads.md:56`, the page and `yards.py` say the opposite (Kodaira's 231 sq m yard against a ~120 sq m minka) | nothing of the retired rule moves | writer (T04) |
| 14 | `homesteads.md:107` derives the grove's N/W side as THE rule; the page says the record gives south-to-west (Tonami) and the side is a per-map default | the page's reading; the default is a map convention | writer (T04) |
| 15 | byre share: `homesteads.md` fraction ~0.2; the shipped hamlet stage calls 0.22 with gap 60 | preserved by the engine; nothing on the page states 0.2 | writer (T04) |
| 16 | `towns.md:62` `bscale ~0.82` (retired) and Hirameki's canvas `(2600, 1820)` (it is `(2600, 2000)`) | dropped as stale | writer (T12) |
| 17 | `_TOUCH_GAP`: `ways.md` says 1 ft; `hamletgen/ways/geom.py:143` has 4.0 with the reason | preserved by the engine | writer (T09) |
| 18 | `ways.md` widths given at "1px=2ft" beside the 1 ft/px re-read | the hamlet figures at 1 ft/px | writer (T09) |
| 19 | `vegetation.md` "~1,800 sq ft per household" belt anchor vs the page's ~1-2 ha upper half of the HK band | the page's figure | writer (T07) |
| 20 | `sizing.md` cites Chang in Skinner for the civic 5-15% share; `fabric.html` has the civic share unsourced | pending T26; until then the share is labeled as the page labels it | writer (T17) + T26 |
| 21 | plot size stated three ways: `fields.md:62` ~0.19 acre at plot=46 "within the real parcel range"; `research/fields.html` "the maps draw ~0.1-0.15 acre"; `fields.md:15` the 0.05-acre leveled cell | the page reconciles them: the v1 `paddy_field` grain vs the water-first cell target, each named for what it is | writer (T05) |
| 22 | `fields.md`'s two and `archetypes.md`'s seven deep links into the pages use single-hyphen anchors where the page ids carry `---` | moot on deletion; every NEW link a writer writes uses the page's real id (the gate's link test holds it) | writers |
| 23 | `archetypes.md:52` gives the 0.4-0.6 ha pond and 6-10 m dike figures flatly; the page attaches them to a summary-only monograph and `hamletgen/consts.py:299-301` carries the caveat | the page's caveat stands; the specification paragraph carries it | writer (T06) |
| 24 | kura share: `homesteads.md` ~30% (measured pool 28.4%); the page's only figure is Sugiura's 0.24 per household | the page says the 30% is a choice calibrated near Sugiura's 0.24, not a finding | writer (T04) |
| 25 | `homesteads.md:103` puts a bamboo clump in each N/W grove arm as standard; the page labels the N/W bamboo strip a GUESS and notes Tonami's bamboo stands south | the page's GUESS label | writer (T04) |
| 26 | `BURAKUMIN_SEAM_FT` is named as a constant in `urban-features.md:101` and exists in no `.py`; `tanning_yard_on_water` vs the roster's `tanning_yards_on_water` | the seam's 60 ft moves as a specification with no identifier; the check name does not move | writer (T13) |
| 27 | `settlements.md:186-187` describes `_MATRIX_OUTSTANDING` as populated; `overlap/taxonomy.py:629-640` is empty ("ALL ELEVEN are now fixed") | nothing moves; stale | writer (T18) |
| 28 | "gated off all fifteen keep-clear hazards at once" (`settlements.md:161`) has no mechanism since feature 166; `dev/placement.md:317-408` repeats the same claim in a surviving document | nothing moves; `dev/placement.md`'s passage is corrected under XIV (T28) | session (T28) |
| 29 | `religion-and-death.md:46` describes `check_village.py` and its registry as live; the registry lives in `l7r/diagram/overlap/` | nothing of the location sentence moves | writer (T11) |
| 30 | `water.md`'s KNOWN GAP proposes the per-field slope record as "the real fix" while the block above it says it was implemented; `capitals.md`'s STATUS lists capital checks as shipped and gated (none exists) | the gap entry moves as the accepted limitation only; the STATUS block does not move | writers (T08, T17) |
| 31 | coppice cycle: `research/vegetation.html` says 15-20 years (satoyama) against 20-40 "by one review"; the `WoodlandCommons` explanation in `interactive/classes/greenery.py` says "a 10-30 year cycle" - a page-versus-map contradiction that outlives the deletion | the page's finding; the class explanation is corrected to it (a docstring, `make page-check`) | session (T29) |
| 32 | the machiya eave gap: `research/cities/fabric.html` records an 18 ft median gap as a disclosed departure; `fabric.md`'s row doctrine states 3-6 ft with no mention of it | the row-packing specification carries the page's departure | writer (T15) |

Owners of rows 1 and 2 moved from the session to the page's writer (T08, T13) so no page has two editors at once.

Found during the sweep (added as the writers report): -

## R2 - the decision map (FR-002, SC-002)

Filled per page from the writers' reports: audit D item -> anchor.

## R3 - the specification map (FR-003, SC-003)

Filled per page: rule -> anchor, or dropped with the reason.

## R4 - physical claims that moved (FR-005)

| Claim | Named source | source-reader verdict | Landed as |
|---|---|---|---|

## R5 - new registry keys and their applicability verdicts

## R6 - engine pointers re-pointed (D10)

## R7 - stale content dropped, by rule file
