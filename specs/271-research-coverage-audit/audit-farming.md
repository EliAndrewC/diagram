# Audit A - farming settlements (hamlets and villages)

Feature 271 FR-001, domain A. Built 2026-09-27 from `measure/kinds.json` (the hamlet and village tiers: 5 scripted
hamlets, 8 hand-drawn hamlets, 4 hand-drawn villages), `measure/modals.json` (the CLASSES registry's farming modals),
`measure/questions.json`, the record's fragments, `future-work/farming-communities.md` (`fc:`), and the claims of
269 (`B..`, its inventory and the new questions its clone holds unpushed), 267 (`R..`) and 268.

How to read the columns:
- **status** is against the record in this clone (main as of a864e29e). A 269 or 267 question written in their clone
  but not yet on main counts as not there; the owner column says who is writing it.
- **COVERED**: a question answers it with quoted, footnoted evidence. **THIN**: a question touches it, but with no or
  almost no quoted evidence, or only partly (the part missing is named). **NONE**: nothing answers it.
- **owner**: `269 Bnn`, `267 Rnn`, `268` where that feature claims it; `271` otherwise (a COVERED row with no claim
  is `271` only as the audit's owner - nothing is owed on it).
- **priority**: 1 = the kind is drawn on a map already (pool, hand-drawn pool); 2 = village tier, not drawn yet; 3 = town
  tier; 4 = city or capital tier.
- **tiers**: H hamlet, V village, T town (its farming ring), C city (its farming ring).

The canon frame, from `settlements/010` (canon, not evidence): a hamlet has no headman, no shrine, no tax-free plot; a
village has a headman's house (the largest on the sheet), a shrine and two or three tax-free plots; neither has a
temple (towns have monasteries). Several rows below ask what history says a village of 40-100 households also had -
a temple, a smith, a mill, a meeting place - because the GM's goal names them; where history and canon part, that row
is research FOR the GM's ruling, not a change.

## Fields

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A01 | paddy plot | What shape and size is a paddy plot, and why is the fabric an irregular patchwork rather than a grid? | H V T | COVERED | fields/020, fields/050, fields/110 | 271 | 1 |
| A02 | paddy plot | How much paddy does a household, and so a hamlet or village, farm (acreage from population, the grain share)? | H V | COVERED (the grain share is a guess) | fields/110, fields/120 | 269 B09 | 1 |
| A03 | paddy basin | What is the smallest basin, and how does a fan-toe basin end? | H V | COVERED | fields/023, fields/024 | 271 | 1 |
| A04 | bund | How wide is a bund, and how wide is the walking bund (azemichi)? | H V T | THIN (widths are guesses) | fields/021, fields/026 | 269 B02 | 1 |
| A05 | bund | Does a bund run on or turn - never stepping sideways and carrying on? | H V | THIN (no footnotes) | fields/022 | 271 | 1 |
| A06 | bund | Why is a hand-piled bund never straight or square at the corners? | H V | THIN (no footnotes) | archetypes/070 | 269 B35 | 1 |
| A07 | bund | Is the lowest bund of a paddy laid with the drain or across it? | H V | THIN (no footnotes) | fields/100 | 271 | 1 |
| A08 | bund beans | What grew on the bund (azemame), how thickly, and what it looks like from above? | H V | COVERED | fields/200 | 271 | 1 |
| A09 | paddy water | How deep does the water stand, and was a paddy drained in midsummer (nakaboshi) before modern times? | H V | COVERED (depth) / THIN (midseason drainage is a guess) | fields/030 | 269 B03 | 1 |
| A10 | wet paddy | Which plots are waterlogged year-round (shitsuden), and where do they lie? | H V | COVERED | fields/190 | 271 | 1 |
| A11 | fallow patch | Was paddy left fallow within a hamlet, how much, and where does a resting plot lie? | H V | NONE (the modal says "no dedicated entry") | - | 269 B01 | 1 |
| A12 | terraced paddy | What does rice land look like with no valley floor - terraces (tanada), their riser height, bund width and plot size on a slope? | H V | THIN (1 note; riser and terrace plot size unanswered) | archetypes/040, fields/024 | 269 B35 (040); riser/plot size 271 | 1 |
| A13 | dry field | Where do dry (hatake) crops go on the catena, and which crops? | H V | THIN (269: no source places them) | fields/160 | 269 B07 | 1 |
| A14 | dry field | Why do dry plots square to a canal, and which way do neighbors' furrows run (the angle between them)? | H V | COVERED (170, 180) / THIN (the angle leans on European open-field sources) | fields/170, fields/180 | 269 B06 | 1 |
| A15 | dry crops | What do millet, buckwheat, barley and soy look like from above in season (rows, color, height)? | H V | THIN (the crops are placed, their look is not researched) | fields/050, fields/160 | 271 | 1 |
| A16 | winter crop, straw rick | Did a paddy carry a second winter crop, and where did the straw rick stand and for how long? | H V | THIN (the rick's duration is a guess) | homesteads/210 | 269 B05 | 1 |
| A17 | drying racks (hasa) | Where were rice-drying racks put up - along bunds, by the lane, in the yard - how long, and how many per household? | H V | THIN (145 names hasa; siting and size unanswered; seasonal maps deferred, fc:2048) | homesteads/145 | 271 | 2 |
| A18 | field pond, field rock | Which obstacles a flooded paddy keeps (in-field pond, rock), and how often? | H V | COVERED (2 notes, thin on rates) | fields/010 | 271 | 1 |
| A19 | grave island | Were graves left among the working paddy, and how often? | H V | THIN (the rate was a session's choice) | fields/010 | 267 R52 | 1 |
| A20 | tax-free plot | Which of a village's plots were tax-free (shrine and temple glebe, the headman's allowance), how many, how big, where? | V | THIN (no footnotes) | fields/150 | 269 B08 | 1 |
| A21 | overlay crops | Which cash-crop overlays may a village carry (mulberry fishpond, lotus, tea fringe), and how much of it? | V | COVERED (030) / THIN (overlay extent, no footnotes) | archetypes/030, archetypes/020 | 271 (020) | 1 |
| A22 | rape flower | Why is there no rape (canola) beside the rice? | H V | COVERED | archetypes/010 | 271 | 1 |
| A23 | field path | Where does a path to the fields end - at a bund head, a gap in the outer bund, the worked ground? | H V | NONE | - | 269 B04 | 1 |
| A24 | plot tenure | How were a village's plots held and allotted (scattered strips per household, warichi redistribution, tenant plots), and does it show in the plot pattern? | H V | THIN (only the polder's private patchwork) | archetypes/050 | 271 | 2 |
| A25 | fodder and green-manure meadow | Did a village keep a cut meadow or common for fodder and green manure (kusakariba, magusaba), how large against its paddy, and where? | H V | NONE | - | 271 | 1 |
| A26 | hayfield, pasture | Where does a hayfield or grazing ground stand, and how is it bounded (hand-drawn towns label "hayfields & grazing")? | H V T | NONE (the commons tiling is open, fc:1421) | - | 271 | 1 |
| A27 | flower field | Did a town's ring grow flowers (chrysanthemum) for the market or the shrine, and in plots of what size? | T | NONE | - | 271 | 3 |
| A28 | town farmland | What is the farmland around a town or city made of, and how big is a town's paddy plot? | T C | COVERED (130) / THIN (towns/150, no footnotes) | fields/130, towns/150 | 269 B43 (150) | 3 |
| A29 | samurai estate in the paddy ring | Where do the samurai estates sit when the paddy has the near ring? | T C | THIN (no footnotes) | fields/140 | 269 B08 | 4 |
| A30 | farmland inside a city | Does a city farm inside its walls, and why is it ringed by farmland? | C | COVERED | cities/hinterland/020, cities/hinterland/050 | 271 | 4 |

## Water and irrigation

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A31 | stream | How wide is a brook, a stream, a river at each rank (the width ladder)? | H V T C | COVERED | water/010, water/230 | 271 | 1 |
| A32 | intake | Where does the brook become the ditch - the intake on its bank, and the brook runs on? | H V | COVERED | water/250 | 271 | 1 |
| A33 | weir | What was a village weir built of, how thick, and when is one built rather than a bank intake (the 50/50 roll)? | H V | THIN (thickness a guess; the roll unsourced) | water/250 | 269 B22 | 1 |
| A34 | intake mouth | What does an intake mouth look like from above? | H V | THIN | water/250, water/040 | 269 B22 | 1 |
| A35 | irrigation ditch | How wide is a ditch, how does it taper, and where does the drawn net stop? | H V | COVERED | water/020, water/030, water/050, water/070 | 271 | 1 |
| A36 | irrigation layout | Comb, fan or grid - when does each canal pattern apply, and does the head race fork? | H V | COVERED | fields/070, fields/075, water/240, water/220 | 271 | 1 |
| A37 | division works | How was a ditch split between users (a division weir or notched board, bunsuiban) and what shows of it? | H V | THIN (the fork is covered, the structure is not) | water/240, fields/070 | 271 | 1 |
| A38 | drainage ditch | Where does a field drain go - across the slope, back to the river, via the next field? | H V | COVERED (260, 080) / THIN (090 has one note over 500 words) | water/260, fields/080, fields/090, water/090 | 269 B25 (090) | 1 |
| A39 | reservoir (tameike) | How big is a village's irrigation pond against the paddy it serves, and where is it dammed? | H V | COVERED | fields/110, fields/070 | 271 | 1 |
| A40 | reservoir shore | Is the pond shore reeded and its embankment mown, and were the reeds a crop? | H V | COVERED (280) / THIN (the reed economy searched, not found) | water/280, vegetation/120 | 269 B24 | 1 |
| A41 | footbridge | What crosses a farm ditch - a plank, a log, earth over logs? | H V | THIN (the Footbridge kind is a guess) | water/070 | 269 B21 | 1 |
| A42 | bridge | What is a plank bridge, how far past the bank does a bridge land, and is it where the road actually crosses? | H V T | COVERED (010, 030) / THIN (050) | ways/010, ways/030, ways/050 | 269 B46 (050) | 1 |
| A43 | stream and settlement | Does a hamlet stand on one bank of its stream or around it, and may it be split by its water? | H V | COVERED (270) / THIN (the split is a guess) | water/270 | 269 B23 | 1 |
| A44 | marsh | Where is the wet toe, how wide, and what ground is too wet to build on? | H V | COVERED (140, 150) / THIN (160, two notes) | water/140, water/150, water/160 | 269 B25 (160) | 1 |
| A45 | channel junction | At what angle does an offtake leave, and how is a junction drawn? | H V | COVERED (190) / THIN (200, convention) | water/190, water/200 | 271 | 1 |
| A46 | water-lifting device | Did a village lift water onto its fields by treadle wheel (fumiguruma), swing bucket (hanetsurube) or the Chinese chain pump (longgu che), how many, and what shows on a map? | H V | NONE | - | 271 | 2 |
| A47 | water mill | Did a village have a water mill (suisha) for polishing rice or grinding, how many per village, where on the stream, how big, and whose? | V | NONE | - | 271 | 2 |
| A48 | washing place | Where did a village wash vegetables and clothes (araiba, kawabata - steps down to a stream or ditch), and how many? | H V | NONE | - | 271 | 2 |
| A49 | flood works | What did a river-plain village build against floods - a village ring levee (wajū), a flood-refuge storehouse on a mound (mizuka), a raised house base - and where? | V | NONE | - | 271 | 2 |
| A50 | well | How many communal wells a rural village ran, and the wellhead as drawn | H V | COVERED | urban-features/090 | 271 | 1 |
| A51 | well | Where does a village's communal well stand - a dooryard, a lane side, the commons (the Inashiro south well, fc:2063) - and was there a well house? | H V | THIN (count covered, rural siting not) | urban-features/090, urban-features/120, homesteads/145 | 271 | 1 |
| A52 | well | Does a dispersed hamlet's outlying farm have its own well, and may a byre stand by a wellhead? | H | COVERED | homesteads/200, homesteads/060 | 271 | 1 |
| A53 | crescent pond | Why is there a half-moon pond in front of some villages, how big, and when is it dug? | V | THIN (no footnotes) | homesteads/180 | 269 B19 | 1 |

## The dike-pond and polder archetypes

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A54 | fish pond | The 6:4 water-to-dike ratio and pond size | H V | COVERED | archetypes/140 | 271 | 1 |
| A55 | pond layout | Grid or mosaic - how dike-ponds are arranged | H V | COVERED | archetypes/130 | 271 | 1 |
| A56 | pond sluice, pond canal | How is a dike-pond fed and drained? | H V | COVERED | archetypes/150 | 271 | 1 |
| A57 | mulberry dike | How dense is dike mulberry, and how wide its crowns (drawn 10-20x sparser than the one figure) | H V | THIN (one modern figure; a GM decision is open, fc:22) | archetypes/140 | 269 B33 | 1 |
| A58 | cane, banana, fruit, vegetable dike | Is any of these premodern? (drawn as accurate; the gazetteer dates them modern) | H V | THIN (the record says modern; a GM decision is open, fc:37) | archetypes/173 | 269 B34 | 1 |
| A59 | pig sty, duck pen | Does a dike-pond hamlet keep pigs and ducks, what share of households, and how far back from the water? | H | COVERED (the practice) / THIN (the shares are guesses) | archetypes/171, archetypes/180 | 269 B32 | 1 |
| A60 | fry pond | Were fry a trade, and which ponds were the nursery ponds, how many? | H | THIN (the share is a guess) | archetypes/172 | 269 B32 | 1 |
| A61 | manure pit, silkworm rearing | What stands on a dike-pond hamlet that a paddy hamlet lacks? | H V | COVERED | archetypes/170 | 271 | 1 |
| A62 | perimeter dike | Where does a polder's dike run, how high and wide is it, and what grows on it? | H V | COVERED (course, planting) / THIN (no dimension found in 080) | archetypes/080, archetypes/090, archetypes/100 | 271 (dimensions) | 1 |
| A63 | ring canal | Where does a polder's canal run? | H V | COVERED | archetypes/110, archetypes/120 | 271 | 1 |
| A64 | polder parcels | How were polder parcels held, and what lies between two of them, how wide? | H V | COVERED (050) / THIN (060, no footnotes) | archetypes/050, archetypes/060 | 269 B35 | 1 |
| A65 | polder siting | Where does a polder stand and where does its village sit? | H V | COVERED | archetypes/160 | 271 | 1 |
| A66 | polder drainage | How did a polder get rid of its water - a sluice at low tide, a lifting pump - and what shows of it? | H V | THIN (sluices named; lifting absent) | archetypes/150, archetypes/160 | 271 | 1 |
| A67 | settlement card | What a settlement IS and what its card may say; does a branch hamlet keep its own tutelary shrine? | H V | COVERED (190) / THIN (branch-hamlet chinju) | archetypes/190 | 269 B35 | 1 |

## Homesteads

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A68 | farmhouse | How big is an ordinary farmhouse (the drawn 46 x 28 ft), and how does it vary with the household's standing? | H V T | THIN (the band rests on "general reading"; no size source) | homesteads/130 | 271 | 1 |
| A69 | farmhouse | Why is a farmhouse longer than deep, and within what proportions? | H V | THIN (1 note; the band is unsourced) | homesteads/130 | 271 | 1 |
| A70 | farmhouse roof | What does a farmhouse roof look like from above - thatched hip, half-hip, gable, tile - and how does it differ Japan to south China? | H V T | NONE | - | 271 | 1 |
| A71 | farmhouse form | Which plan forms a farmhouse took by region (a straight minka, the L-shaped magariya, the south-China three-sided courtyard house) and which the maps should draw | H V | THIN (145 names magariya; no regional survey) | homesteads/145, homesteads/130 | 271 | 1 |
| A72 | farmhouse bearing | Why is each house a little off due south, and how widely do bearings spread in one hamlet? | H V | THIN (no footnotes; the 5 degrees is a guess) | homesteads/240 | 269 B18 | 1 |
| A73 | headman's house | How much larger is the headman's house than an ordinary farmhouse (drawn 92 x 56 against 46 x 28)? | V | THIN (no footnotes; GM rulings only) | homesteads/110 | 269 B19 | 1 |
| A74 | headman's house | What did a headman's (shoya, nanushi) homestead carry that others did not - a gate (nagaya-mon), a wall or hedge, several kura, an office room - and how big was its plot? | V | THIN (the kura is asserted with "no source cited"; gate, wall and plot not asked) | homesteads/110, homesteads/145 | 269 B19 (110); the gate, wall and plot 271 | 1 |
| A75 | headman's house | Where in a village did the headman's house stand - the center, the oldest spot, by the shrine, on the road? | V | NONE | - | 271 | 1 |
| A76 | poorer households | Were landless and tenant households (mizunomi) housed in smaller huts, and where in the village? | V | NONE | - | 271 | 2 |
| A77 | storehouse (kura) | Which farmhouses have a storehouse, and what share? | H V | COVERED | homesteads/120 | 271 | 1 |
| A78 | storehouse (kura) | How big is a farm kura, what is it built of, and where on the plot does it stand? | H V | THIN (the share is covered; size and siting not) | homesteads/120, homesteads/140 | 271 | 1 |
| A79 | farm shed (naya) | How big is a farm shed and where on the plot? | H V | THIN (the count is covered; size not) | homesteads/140 | 271 | 1 |
| A80 | byre | How big is a draft-animal byre and what stands in it? | H V | COVERED | homesteads/070 | 271 | 1 |
| A81 | byre | Where does a village's draft ox stand - a shared shed on the commons or the village edge (a knob)? | H V | THIN | homesteads/070 | 269 B16 | 1 |
| A82 | draft animals | Ox or horse, by region, and how many households kept one? | H V | THIN (145 on the magariya's horse country only) | homesteads/070, homesteads/145 | 271 | 1 |
| A83 | pigs in a paddy hamlet | Did an ordinary south-China paddy hamlet keep pigs, poultry and ducks, and where (the sty is drawn only on dike-pond hamlets)? | H V | NONE (only for the dike-pond) | archetypes/171 | 271 | 1 |
| A84 | threshing yard | How big was the work yard, and how far does the house shade it? | H V | COVERED | homesteads/020, homesteads/030 | 271 | 1 |
| A85 | kitchen garden | How big was the dooryard garden, and how much sun does it keep? | H V | THIN (the size is a guess) / COVERED (sun) | homesteads/050, homesteads/040, homesteads/043 | 269 B20 | 1 |
| A86 | privy | Where did the privy stand, which way does it face, and where was night soil kept? | H V | COVERED (facing, the fixture) / THIN (placement) | homesteads/210, homesteads/220 | 269 B10 | 1 |
| A87 | manure heap | Where in the dooryard was the manure heap? | H V | THIN (1 note) | homesteads/230, homesteads/210 | 269 B11 | 1 |
| A88 | bath shed | Detached or not, and where? | H V | COVERED (2 notes; the modal is guess) | homesteads/214 | 269 B12 | 1 |
| A89 | hen coop | What share of farmsteads kept chickens, and in what coop? | H V | COVERED (the share is a guess) | homesteads/215 | 269 B13 | 1 |
| A90 | household shrine | Which farmsteads had a yashikigami shrine, and in which corner? | H V | COVERED | homesteads/216 | 271 | 1 |
| A91 | persimmon | Which side of the house, and how wide the crown? | H V | COVERED (the tree) / THIN (side and crown) | homesteads/218 | 269 B14 | 1 |
| A92 | woodpile | Against which wall, and how big? | H V | COVERED | homesteads/212 | 269 B15 | 1 |
| A93 | other farmstead trees | Which other trees stood on a farmstead - plum, chestnut, loquat, a mulberry or tea hedge - and how many? | H V | NONE | - | 271 | 1 |
| A94 | farmstead inventory | What stood on a farmstead, with counts (the Miyagi survey) | H V | COVERED | homesteads/140 | 271 | 1 |
| A95 | farmstead boundary | How was a farmstead bounded - a hedge (ikegaki), a stone wall, an earth bank, nothing - and how does it show? | H V | NONE (the gate is covered as a warrior feature; the boundary is not asked) | homesteads/145 | 271 | 1 |
| A96 | farmstead gate | Did a commoner farmstead have a gate? | H V | COVERED (no, a warrior house's) | homesteads/145 | 271 | 1 |
| A97 | homestead grove | How big a yashikirin, how common, which side? | H V | COVERED | homesteads/010, homesteads/046 | 271 | 1 |
| A98 | homestead bamboo | Did a farmstead grove carry bamboo, on which side, what share? | H V | COVERED | vegetation/150, vegetation/154 | 269 B29 | 1 |
| A99 | farmhouse and paddy | How close does a farmhouse stand to the paddy? | H V | COVERED | homesteads/100 | 269 B02 (the setback) | 1 |
| A100 | settlement form | Must a hamlet be nucleated? Why does one village look nothing like the next? | H V | COVERED (150) / THIN (160) | homesteads/150, homesteads/160 | 269 B19 (160) | 1 |
| A101 | village packing | How tightly does a nucleated village pack - the spacing between farmsteads, a village's footprint per household? | V | THIN (512 words, no footnotes) | homesteads/170 | 269 B19 | 1 |
| A102 | village name | Does the village's name say where it stands? | H V | THIN (no footnotes) | homesteads/190 | 269 B19 | 1 |
| A103 | household count | Is every household drawn, and how many inhabitants a house stands for | H V | COVERED (020) / THIN (030) | settlements/020, settlements/030 | 269 B42 (030) | 1 |
| A104 | tier ladder | What a hamlet and a village are, and what each keeps | H V | COVERED (canon) | settlements/010, settlements/050 | 271 | 1 |

## Vegetation and groves

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A105 | the village's groves | What are a village's three groves (windbreak, water-mouth, dooryard copse)? | H V | COVERED | vegetation/020 | 271 | 1 |
| A106 | windbreak | Which side does the belt stand on, and was it one kind of tree in a row? | H V | COVERED (030) / THIN (the species mix) | vegetation/030 | 269 B30 | 1 |
| A107 | windbreak | How wide is a gap in the belt, and why does it run off the sheet? | H V | THIN (040 no footnotes; the gap width is a guess) | vegetation/030, vegetation/040 | 269 B31 (030) | 1 |
| A108 | copse | How big was a village's dooryard copse, and in how many clumps? | H V | THIN (the role is covered; its size is not) | vegetation/020 | 269 B26 | 1 |
| A109 | water-mouth grove | How big is a water-mouth grove, and a fengshui forest? | V | COVERED (010) / THIN (the water-mouth size is a guess) | vegetation/010 | 269 B31 | 1 |
| A110 | woodland commons | How is a coppice lot bounded, and does it stand upslope? | H V | COVERED (provenance of "ridge, stream and path" unknown) | vegetation/140 | 269 B27 | 1 |
| A111 | woodland commons | How thickly was a coppice stocked, how wide its crowns? | H V | THIN (the figures come from unread papers) | vegetation/060, vegetation/070 | 269 B28 | 1 |
| A112 | woodland floor | Does scrub stand under a village wood? | H V | COVERED | vegetation/130 | 271 | 1 |
| A113 | scrub and rough grazing | How far does scrub stand off a field, a channel, open water? | H V | COVERED (090, 110) / THIN (100, convention) | vegetation/090, vegetation/100, vegetation/110 | 269 B31 | 1 |
| A114 | hillside | Why is the hillside past the grove open scrub, and how far was it stripped? | H V | COVERED | vegetation/050 | 269 B31 | 1 |
| A115 | marsh margin | Reed, sedge, then dry ground - and were reed beds cut? | H V | COVERED | vegetation/120 | 269 B31 | 1 |
| A116 | bamboo | How common, where, and how drawn? | H V | COVERED | vegetation/150, vegetation/152 | 271 | 1 |
| A117 | landmark tree | Did a village keep a great old tree at a crossroads, the entrance or a well as a landmark (enoki, zelkova; China's village-mouth tree), and where? | V | NONE (the shrine's sacred tree is 268's) | - | 271 | 2 |
| A118 | forest density | Forest density and crown size, and no canopy tree under another's crown | H V | COVERED | vegetation/060, vegetation/080 | 271 | 1 |
| A119 | slope | How does a flat map show that ground slopes? | H V | COVERED (1 note) | vegetation/160 | 271 | 1 |
| A120 | fuel wood | Where did a village cut its fuel wood and burn charcoal (sumigama) - the hill ground beyond the fields - and did a kiln show? | H V | NONE (fuel-wood siting is in 269's unpushed vegetation 220; the charcoal kiln is not) | - | 269 (fuel wood); 271 (village charcoal kiln) | 2 |

## Lanes and ways at village scale

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A121 | village lane | What vehicle used a village lane, how wide, and where may it run? | H V | COVERED | ways/020, ways/025 | 271 | 1 |
| A122 | village lane | Is every farmhouse reached by a lane, and in what form; how does a lane bend? | H V | COVERED | homesteads/080, homesteads/090 | 271 | 1 |
| A123 | village lane | How far does a lane run past its last farmhouse? | H V | NONE | - | 269 B17 | 1 |
| A124 | lane surface | What was a village lane surfaced with - bare earth, gravel, stone steps on a slope - and does it show? | H V | NONE | - | 271 | 1 |
| A125 | freight | Where does a village's freight go? | H V | COVERED | ways/040 | 271 | 1 |
| A126 | road through a village | How does a village lay itself along a highway it straddles (a street village, kaidō-zoi), and what fronts the road - teahouses, a rest stop (tatebazaki), a milestone mound (ichirizuka)? | V | NONE | - | 271 | 2 |
| A127 | ferry | Where a village road met a river with no bridge, how was a ferry landing (watashiba) laid out, and how many villages kept one? | V | NONE (river crossings are named only) | water/130 | 271 | 2 |
| A128 | village entrance | How is a village's entrance marked - a boundary stone, a wayside deity (dōsojin), a rope across the road (kanjō-nawa) - and how many? | V | THIN (the entrance stone is a guess; 210 gives the dōsojin siting, 1 note) | homesteads/145, religion-and-death/210 | 269 B20 (the stone); the rest 271 | 1 |
| A129 | village boundary | How was the line between two villages marked (mura-zakai stones, a ridge or stream), and does a village map show it? | V | NONE | - | 271 | 2 |

## The village's public things

| id | thing | question | tiers | status | existing (page/NNN) | owner | priority |
|---|---|---|---|---|---|---|---|
| A130 | notice board | Where does the notice board stand, why even a hamlet keeps one, and who read it aloud? | H V T | COVERED | urban-features/010, urban-features/012 | 271 | 1 |
| A131 | notice board | How does the map choose the board's seat, and may it stand under a tree? | H V | THIN (no footnotes) | urban-features/015 | 271 | 1 |
| A132 | notice board | How big was a village board and what did it look like from above (roofed, fenced, on a stone base)? | H V | THIN (the siting is covered; the form is not asked) | urban-features/010 | 271 | 1 |
| A133 | village shrine | Where does a village put its shrine and how big is it? | V | COVERED | religion-and-death/100, religion-and-death/120 | 268 | 1 |
| A134 | village shrine | Does the country monk live at the shrine, and who owns and pays for it? | V | COVERED | religion-and-death/110, religion-and-death/128 | 268 | 1 |
| A135 | shrine precinct | How big is the precinct, is it walled, and what else stands in it (the grove, sacred tree, basin, farmers' stage)? | V | COVERED | religion-and-death/122, religion-and-death/124, religion-and-death/126 | 268 | 1 |
| A136 | torii | How many arches and at what spacing? | V T C | COVERED | religion-and-death/080, religion-and-death/090 | 268 | 1 |
| A137 | swept ground | Is the ground around a shrine or grave swept clear, and why the ragged edge? | V T | COVERED (130) / THIN (140, no footnotes) | religion-and-death/130, religion-and-death/140 | 271 (140) | 1 |
| A138 | village temple | Did a village of 40-100 households have a Buddhist temple of its own (the Edo parish-temple system put one in or near most villages; the canon gives a village only a shrine), and how many villages shared one? | V | THIN (210 states the canon tier rule; no historical evidence on village temples) | religion-and-death/210 | 271 | 2 |
| A139 | village temple | If a village temple is drawn: how big is its precinct, what stands in it (hall, priest's quarters, bell), and where does it sit against the houses and the graves? | V | NONE | - | 271 | 2 |
| A140 | wayside shrines | How many small wayside shrines (jizō, dōsojin, a stone kami) a village carries, and at which thresholds | H V | THIN (1 note, siting only) | religion-and-death/210 | 271 | 2 |
| A141 | village burial ground | How much ground does a village burial ground need, whose dead lie in it, and what shape is it? | V | COVERED (the Buck 2% figure is unread) | religion-and-death/160, religion-and-death/150, religion-and-death/206 | 269 B36 | 1 |
| A142 | village burial ground | Does it stand beside the shrine or a temple, and how far from water? | V | THIN (269: no source found) | religion-and-death/170, religion-and-death/180 | 269 B36 | 1 |
| A143 | household graves | Where does a HAMLET bury its dead - household plots beside the farmstead (yashiki-baka), a shared hillside, the district's ground? | H | THIN (the canon has none; field graves are 267's R52) | religion-and-death/210, fields/010 | 271 | 1 |
| A144 | cremation, ossuary | Does a village cremate or bury, and where do its crematory and bone mound go? | V | THIN (the answers are for towns and cities) | religion-and-death/190, religion-and-death/202, religion-and-death/204 | 271 | 2 |
| A145 | village granary | Did a village keep a communal granary (the tax-rice gokura; the relief granaries - gisō, shasō, China's charity granary), how many, how big, and where? | V | THIN (cities/fabric/143 and buildings/080 mention the gokura in passing) | cities/fabric/143, buildings/080 | 271 | 2 |
| A146 | meeting place | Where did a village meet (yoriai) - the headman's house, the shrine, a hall of its own; and in south China the lineage ancestral hall - and how big and where was it? | V | NONE | - | 271 | 2 |
| A147 | ancestral hall | Did a south-China village's lineage hall (citang) front the crescent pond, and how big was it? | V | THIN (180 names the lineage, no hall, no footnotes) | homesteads/180 | 271 | 2 |
| A148 | communal threshing floor | Did a south-China village thresh and dry on a shared floor (a stone roller, the drying ground before the hall) rather than each dooryard, and how big? | H V | NONE (the private work yard only) | homesteads/020 | 271 | 1 |
| A149 | smithy | Did a village have its own smith for tools (a village smith or an itinerant one), how often, and how big and where was the forge? | V | NONE | - | 271 | 2 |
| A150 | village trades | Which trades did a village of 350 hold - a general shop, a sake brewer (often the headman), an oil presser, a carpenter, a cooper - and how many? | V | NONE | - | 271 | 2 |
| A151 | village school | Where were village children taught to read (a temple school, terakoya; the headman's house), and does it show? | V | NONE | - | 271 | 2 |
| A152 | fire watch | Did a village keep a fire bell on a ladder (hanshō), a watch hut, a fire-water pond, and where? | V | NONE (the town tower is covered, not the village) | towns/070 | 271 | 2 |
| A153 | village watch | Did a village keep a watch hut (bansho) or a night watch, and where did it stand? | V | NONE | - | 271 | 2 |
| A154 | inn and teahouse | Did a village on a road keep a teahouse or an inn, and where? | V | NONE | - | 271 | 2 |
| A155 | village festival ground | Where did a village hold its festivals, sumo and dances - the shrine precinct (covered by 268), or a separate open ground? | V | COVERED (the precinct) | religion-and-death/126 | 268 | 2 |
