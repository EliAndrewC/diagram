# The audit: what Kuwabata, a dike-pond hamlet, is still missing (feature 139, T31)

For the GM. Nothing here is drawn; every item is a decision the GM makes (FR-007, FR-008). The
research behind each row is in `research/archetypes.md` "What stands on a dike-pond hamlet that a
paddy hamlet lacks" with its sources; the verdict column says how well the record supports it.

## A. Candidates - features a silk-and-fish hamlet would carry that a paddy hamlet does not

| # | Feature | Record | Prevalence | Drawable at 1 ft/px | New category? |
|---|---|---|---|---|---|
| A1 | **DECLINED by the GM (2026-08-28)** - *"would it necessarily be the case that any settlement of this sort would have one. I wouldn't think so"*; the connector lane is the market link (to the market or to the water that carries it) and the docs no longer imply a creek. Was: a navigable creek along the landward flank, household boats moored at it, a landing | Fei 1939 (READ): "nearly every household possesses one or more boats"; "the houses must be near the water and consequently determines the plan of the village"; the Sangyuanwei proverb 一船蚕丝出，一船白银归 | ~1 boat per household (Lake Tai, 1936); the cash-crop economy depends on it, and Kuwabata's own notes say a market water link is implied | yes - a sampan ~15-20 x 4 ft; a creek is a watercourse the map already knows how to draw; a boat is furniture, not fauna | YES (water + boats + landing) |
| A2 | **Manure PITS, half-buried earthenware, behind the house and along the road** | Fei 1939 (READ) | every household (Lake Tai) - the same fixture we draw as a heap | yes - a ~3 ft round pit glyph | a new GLYPH for an existing fixture; by the knob rule `heap \| pit` |
| A3 | **A pig sty ON a pond dike (or over the water)** | Ruddle & Zhong via i-sis (SUMMARY-ONLY): "pigs, chickens and ducks are reared on the dykes"; FAO/NACA (READ) for the form | attested, premodern share unquantified; the bagasse-to-pigs loop is traditional | yes - a shed-sized footprint on a dike | YES (a new kind and a new position; we draw byres and coops, not sties) |
| A4 | **A duck pen at a pond corner** (a fenced dry run on the dike, a wet run in the water) | FAO/NACA (READ, modern); Ruddle via i-sis (SUMMARY-ONLY) | attested in the loop; premodern share unquantified; the weakest-evidenced row | yes, but a fence line at true scale is a hairline | YES |
| A5 | **Fry (鱼花) nursery ponds** - a few of the smallest parcels designated as fry ponds | Miles 2003 (SUMMARY-ONLY): the Ming fry trade of Jiujiang; the proverb 男贩鱼花 (READ) | a district trade, not every hamlet | no new ink - a manifest record on parcels that already exist (for the interactive map's reader) | no |
| A6 | **Other dike crops - sugar cane, banana, fruit** (蔗基 / 蕉基 / 果基) as a rolled `dike_crop` form | i-sis (READ) carrying the 1980s survey: cane 18%, mulberry 12%; 中国国家地理 2005 (READ): 蕉林蔗海 | attested forms of the SAME landscape; Kuwabata is the mulberry case by name | yes | YES (each a plant not on any map) |

| A7 | **A sluice-gate glyph at the two perimeter dike cuts** (and, at most, at each pond's cut) | the record (FAO, READ): a gate is boards in a protected opening; the Sangyuanwei 窦 | every polder crossing was gated | a 6 x 3 ft bar across the gap - legible; the boards themselves are inches wide | YES (a new glyph; raised by the settlement-review) |

## B. Should-be-absent - rice features Kuwabata carries because the homestead bundle does

| # | Feature | Why it is in question | Options |
|---|---|---|---|
| B1 | **The threshing yard on every farmstead** | Fei: rice is threshed "in the open space in front of the house, or in the front room" - a rice use; Kuwabata grows no rice | keep as a work yard (cocoons, leaves, nets) and say so in the record; or omit on this archetype; or shrink it - the GM's call |

| B2 | **The three unconverted cells draw as dry stubble** (the leftover repaint) | at wholesale conversion the leftovers were vegetables under mulberry or more pond, not paddy (Fei; the gazetteers' "no rice") - two attested forms | keep as standing rice; or a `leftover` knob rolling paddy \| vegetable ground (a new crop glyph); or convert them too - the GM's call (raised by the settlement-review) |

## C. Not owed / not supported - so the question is not reopened

| Item | Why |
|---|---|
| A silkworm-rearing house or reeling shed | Fei (READ): worms on tray stands in the house's own rooms, "all the rooms except the kitchen"; reeling on a home machine. Communal 蚕房 are 1950s collective buildings |
| Pond-side huts (塘头屋 / a watchman's hut) | searched twice in Chinese and English; nothing attested |
| A silk-goddess shrine (蚕花娘娘) | a village/town festival institution (Huzhou-Jiaxing); a hamlet has no shrine by the tier's definition - a note for the village tier |
| Sheep huts | a 1920s-30s Lake Tai innovation (Fei: "in the past ten years") |
| Mulberry on the raised margin, houses on it, vegetables under it | already drawn (the planted perimeter dike, the village on the dry flank) |
| The pond sluices | already drawn and gated (`dikepond_sluices`) |

## D. Reference-hamlet families absent from Kuwabata (FR-002, for the GM to confirm)

| Family | Reason | Pointer |
|---|---|---|
| `dry_plots` (the comb's dry hem) | a polder is a solid diked wet block; no hem | `research/fields.md`; `make family-census` |
| `field_ditches:branch` (comb deliveries) | a polder is watered by a ring canal and laterals | `waterfields/polder.py` |
| `field_ponds` (the in-field pocket pond) | open water IS this fabric - no obstacle tiles (research D4) | `settlement/fields/features.py` |

Everything else Inashiro records - the fixtures (privy, woodpile, manure heap, bath shed, coop,
hokora, persimmon), the new sheds, the bamboo, the lane web, the wells, the byres, the windbreak,
the notice board, the crossings - is on Kuwabata (`make family-census`: 37 families/kinds in both).

## E. Open number

`GROSS_ACRES_PER_HOUSEHOLD` is the paddy 1.3 ac. Fei's rice-and-silk village averaged 8.5 mu
(~1.4 ac) per household (READ) - the same order, so the figure is not wrong for a mixed village;
nothing read gives a WHOLLY converted pond hamlet's holding. Stays a labeled guess.
