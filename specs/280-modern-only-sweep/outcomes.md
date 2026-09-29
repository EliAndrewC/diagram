# Outcomes - feature 280, the modern-only sweep

Gathered 2026-09-29 from the 41 groups' handoffs (`briefs/*-handoff.md`, each outcome's full text, search and GM-ruling
note there) and the phase-2 work that followed them. Every item M01-M130 has an outcome line; none is excluded to another
owner (269 and 279 have landed, and every `OWED-TO` text in the handoffs was applied on 2026-09-29, commit fd8dc79cd).

**Outcomes:** 33 PREMODERN-ATTESTED, 82 MIXED, 15 MODERN-ONLY (a MIXED item's
modern-only part is eliminated like a MODERN-ONLY item). `undated-custom` (spec D1) marks a form whose one record is an
undated modern account of custom, counted modern.

**Dispositions:** 43 eliminated or recalibrated in the engine, a sheet or a modal; 58 kept as attested (the
record now cites the premodern source); 6 record-only (nothing drawn rested on it); 19 on the frozen legacy maps
only, owed at their tier's conversion (`future-work/cities.md`, `towns.md`, `farming-communities.md`; `migration-plan.md`);
4 waiting on the GM (a form the GM ruled in knowingly: M50, M52, M53, M64; escalation-check 2026-09-29 settled six more as degrees or legacy-only).

**Found in passing and handled here (not inventory items):** the woodpile's KIZUMA form (homesteads/212; researched
2026-09-29, undated modern pages only - removed, undated-custom); the downstream side of a burial ground (religion-and-death
180 and 270; the 2010 survey of today's villages only - the maps claim no side, the edge seat's fall-line tie-break kept as a
drawing order); religion-and-death 520's entrance stones (the brief's check-inventory line 379: now dated 1695, Ueda,
PREMODERN-ATTESTED); the byre and farmhouse snapshot entries (a phase-1 merge miss, fixed); the practice ground's "swept earth"
on the magistracy sheets (building-review, 2026-09-29: an open candidate for a research pass, recorded in
`future-work/compounds.md`, not eliminated on a guess).

| item | group | outcome | section(s) | form | disposition | what was done |
|---|---|---|---|---|---|---|
| M01 | F1 | PREMODERN-ATTESTED | fields/600, fields/070, fields/210 | Comb at right angles | kept (attested) | right angles attested (Zhouli commentary, Lake Tai tangpu, jori); nothing to stop |
| M02 | F1 | PREMODERN-ATTESTED | fields/080 | Drain head width | kept (attested) | the drain head's 1.5 ft rests on the Kaogongji and Hattori; nothing to stop |
| M03 | F2 | PREMODERN-ATTESTED | fields/170 | Dry plots square to the canal | kept (attested) | dry strips squared to a canal are Edo work (Musashino); sizes inside the 1591/1678 registers |
| M04 | F2 | PREMODERN-ATTESTED | fields/620, fields/400, fields/180 | Dry-crop furrows and colors | kept (attested) | rows and furrows premodern (Hanshu, Qimin yaoshu, Nogyo zensho); the rice-barley-soy rotation not drawn |
| M05 | F2 | PREMODERN-ATTESTED | fields/410 | Chrysanthemum field | kept (attested) | Edo flower-growing dated (1824, 1827); Hirameki's field a legacy map, unchanged |
| M06 | F3 | MODERN-ONLY | fields/050 | Rice-hill spacing | record only | the 20-30 cm hill spacing is today's advice; the mottle never drew a spacing - prose only |
| M07 | F3 | MIXED | fields/610 | The "grid" plot knob | kept (attested) | `plot_regularity=grid` rolls on no pool map and already reads as equal strips; the 610 rule holds it off a checkerboard |
| M08 | F3 | PREMODERN-ATTESTED | fields/610 | The "large_block" plot size | kept (attested) | `large_block` sits inside the 1678/1684 register range |
| M09 | F4 | MIXED | fields/260, fields/630 | Bund cross-section | eliminated / recalibrated | the Bund modal: a few inches high, today's standard a foot; Sources kotobank-azebiki, hattori-site-yayoiken |
| M10 | F4 | MIXED | fields/640, fields/270 | Water depth | eliminated / recalibrated | the Paddy modal: the drained stages are premodern (Qimin yaoshu, Chen Fu), the depths modern |
| M11 | F4 | PREMODERN-ATTESTED | water/610 | Collector across the slope | kept (attested) | the collector on the low line is the Minuma layout of 1728 (fields/090 now says so) |
| M12 | F4 | MIXED | fields/650 | Pond sized by command area | eliminated / recalibrated | the m3/ha rule gone from fields/110; the scripted tameike is sized from Ikegami by households, noted as held below Chen Fu's measure (a guess) |
| M13 | H1 | MIXED | homesteads/710 | Grove size | legacy map - owed at conversion | no pool hamlet draws a homestead grove; `_find_grove_arms` (the arms-only L) serves the legacy maps only - owed at conversion (future-work) |
| M14 | H1 | MODERN-ONLY | homesteads/040 | Sun lane from belt height | kept (attested) | the belt's 10 m is kept as a labeled working height - no grove height before 1868 exists to replace it (the GM's 2026-08-26 ruling was made not knowing the figures were modern; escalation-check: a degree, not a form) |
| M15 | H1 | MODERN-ONLY (undated-custom) | homesteads/046 | The Tonami model homestead | record only | persimmon and bamboo sides are rolled guesses already (269 B14, B29); the N/W bamboo side's 'attested' wording dropped (undated-custom) |
| M16 | H2 | MODERN-ONLY (undated-custom) | homesteads/020 | Work-yard median | eliminated / recalibrated | YARD_MEDIAN_TSUBO 18 -> 25 (the IRRI spreading depth retired; undated-custom calibration, so a GUESS) |
| M17 | H2 | PREMODERN-ATTESTED | homesteads/070 | Byre size | kept (attested) | the byre's 16 x 11 ft is the Maizuru stable of 1751-1829 |
| M18 | H2 | MIXED | homesteads/440 | Farm-shed size | eliminated / recalibrated | the storehouse annex at 1.67:1 (0.46 w x 0.45 h), inside the Edo sheds' 18-27 ft; the Meiji-Taisho barns not drawn |
| M19 | H2 | MIXED | homesteads/470 | Pig-sty share | kept (attested) | the sty on a rice farm is premodern (the Shen manual); STY_SHARE stays a calibration |
| M20 | H3 | MIXED | homesteads/720 | Outbuildings, the storehouse share and the heap rate | eliminated / recalibrated | the storehouse annex on ~1 farm in 8 (KURA_SHARE 0.125, headman always); the heap's 40-70% stays a guess |
| M21 | H3 | MIXED | homesteads/212 | The firewood stack | eliminated / recalibrated | the woodpile is a wood shed only, 35-45% of farmsteads, larger houses first, 24 x 12 ft; the eaves stack and (found in passing, undated-custom) the kizuma removed |
| M22 | H4 | MIXED | homesteads/740, 214 | The bath shed | eliminated / recalibrated | the bath is a room joined to the house, 20-30%, main door / stable end / a headman's floored rooms, 6 x 6-12 ft; the shed and corridor removed |
| M23 | H4 | PREMODERN-ATTESTED | homesteads/220 | The detached privy | eliminated / recalibrated | the privy rolled from the Kakimochi table's sixteen sizes (it was a 6 x 6 ft guess) |
| M24 | H5 | PREMODERN-ATTESTED | homesteads/760 | Chickens | kept (attested) | chickens in the Qing village yard (Smith 1899, King 1909); the coop band stands |
| M25 | H5 | MIXED | homesteads/770 | Persimmon crown | record only | the 23 ft crown labeled a GUESS in 218 and the Persimmon modal |
| M26 | H5 | MIXED | homesteads/780 | House bearings | eliminated / recalibrated | the quarter-turned tenth removed (QUARTER_TURN_SHARE); houses turn with their lane |
| M27 | H5 | MODERN-ONLY | homesteads/170 | Village packing | record only | the 200 m gap dropped from 170's village rule; no code carried it |
| M28 | W1 | MIXED | water/010, water/620 | The width ladder | kept (attested) | every built rung of the ladder has a premodern width |
| M29 | W1 | MIXED | water/030, water/610 | Where the drawn net stops | kept (attested) | the finite ladder and plot-to-plot hand-off are classical; the modern justifications removed from 030 |
| M30 | W1 | MIXED | water/050 | True-size comb strokes | kept (attested) | the drain outfall's 5.5 ft is a hydraulic figure, not a modern-only form; the GM's true-size ruling (2026-08-17) stands |
| M31 | W1 | MIXED | water/040 | The bund along the channel | kept (attested) | the continuous bund along a channel and its 1.5 ft attested; 040's spec now carries it |
| M32 | W2 | MIXED | water/610, fields/070 | The separated net | eliminated / recalibrated | the DrainageDitch modal: the separated net is the Minuma layout, not modern consolidation |
| M33 | W2 | MIXED | water/190, cities/river-cities/020 | Junction angles | kept (attested) | the downstream lean attested (Edo slanting weirs); the 30-45 degree figure not cited |
| M34 | W2 | MODERN-ONLY | water/150, water/600 | The wet toe along the collector | eliminated / recalibrated | the modern MAFF grounding of the reed edge removed (water/600, the Marsh modal); the engine reads the fan's toe, never the drain - no geometry change; reported to the GM (ruled in 2026-08-26 unknowingly) |
| M35 | W3 | PREMODERN-ATTESTED | water/630 | The dry-hem berm | kept (attested) | the 5.0 ft berm inside the Yayoi bank-bund range; 070 re-grounded |
| M36 | W3 | PREMODERN-ATTESTED | water/640 | The stake-and-reed weir | eliminated / recalibrated | the weir fence woven with brushwood, not reed (the Weir modal, brook.py) |
| M37 | W4 | PREMODERN-ATTESTED | water/650, water/280 | The reeded pond fringe | kept (attested) | the reeded pond fringe is premodern (Book of Songs commentary) |
| M38 | W4 | MIXED | water/650, water/285 | The bare embankment | kept (attested) | the reed-free bank is premodern (turfed or trodden); a sparse-mulberry bank is a second attested form, recorded for a knob (future-work) |
| M39 | W4 | MIXED | water/660, water/160 | Too wet to build on | eliminated / recalibrated | the well keep-out re-grounded as this project's decision (water/160, 660); the two modern well manuals marked Not cited |
| M40 | V1 | MIXED | vegetation/600, vegetation/010 | Fengshui-forest scale | kept (attested) | the groves are old forms; their sizes are today's measurements of centuries-old survivors, kept as labeled guesses |
| M41 | V1 | PREMODERN-ATTESTED | vegetation/610 | The afternoon-sun lane | kept (attested) | the 50 ft sun lane is a sun-angle figure valid in any century; the Qimin yaoshu's ~33 ft is one tree height on the same modern belt - a degree, the GM's 50 ft stands |
| M42 | V1 | MIXED | vegetation/620 | A lane through the belt | kept (attested) | the angled crossing and end offset reach no engine code; the gap fill stays a convention |
| M43 | V1 | MIXED | vegetation/600 | The water-mouth grove | kept (attested) | the water-mouth grove old; no premodern area - the count may rise (future-work) |
| M44 | V2 | MIXED | vegetation/060, vegetation/650 | Forest density | kept (attested) | the 500-800/ha band sits at the sparsest Edo planting; crowns a guess - GM may choose the denser planting |
| M45 | V2 | MODERN-ONLY | vegetation/070 | Belt crowns | kept (attested) | no premodern crown width; one crown size stays (the GM ruled the sameness) |
| M46 | V2 | MODERN-ONLY | vegetation/230 | Coppice stocking | kept (attested) | the coppice's 1,700/ha a modern calibration with no older figure; kept labeled |
| M47 | V3 | MIXED | vegetation/630 | The crop margin | kept (attested) | the kept-cut margin attested (karishiki); its 6 ft a guess inside the attested ground |
| M48 | V3 | MIXED | vegetation/110, water/040, vegetation/630 | The cut bank | kept (attested) | the bank margin stands where the channel runs along a paddy bund; 6 ft the margin's choice |
| M49 | V3 | PREMODERN-ATTESTED | vegetation/640 | The take-yabu | eliminated / recalibrated | the take-yabu thicket seated at the settlement's edge behind its back row, not the field margin |
| M50 | V3 | MODERN-ONLY | vegetation/152 | The bamboo glyph | waiting on the GM | the stand-level bamboo glyph follows a modern (GSI) legend; the GM ruled it in knowingly (2026-08-27) - waiting on the ruling |
| M51 | A1 | PREMODERN-ATTESTED | archetypes/600 | The lotus field | kept (attested) | the lotus field is premodern in both countries |
| M52 | A1 | MIXED | archetypes/020 | Overlay extent | waiting on the GM | lotus has no premodern share; the upper band fits a lotus-district village - a knob narrowing the GM's knowing liberty of 2026-07-19, raised |
| M53 | A1 | MIXED | archetypes/310 | The cash-crop share | waiting on the GM | as M52, for legacy shimizu (frozen) |
| M54 | A2 | MIXED | archetypes/050 | The polder parcel | eliminated / recalibrated | the rice polder's cell 110 -> 190 ft (three mu, the 1897 fish-scale register); no pool map rolls it |
| M55 | A2 | PREMODERN-ATTESTED | archetypes/090 | Dike planting rows | eliminated / recalibrated | the dikes.py comment re-pointed at Pan Jixun; no geometry |
| M56 | A2 | MIXED | archetypes/130 | The pond grid | eliminated / recalibrated | POND_LAYOUTS mosaic only; reversal of the GM's knob of 2026-08-18 reported |
| M57 | A2 | MIXED | archetypes/150 | Dike-pond sluices | eliminated / recalibrated | the per-pond sluice removed (PondSluice retired, the sty keep-clear and its gate test with it); reversal of the GM's 2026-07-22 request reported |
| M58 | A3 | MIXED | archetypes/610 | The 6:4 ratio | eliminated / recalibrated | the water inset 11 -> 23 ft: 0.62 water per parcel on Kuwabata (was 0.80) |
| M59 | A3 | MIXED | archetypes/172 | Fry ponds on the smallest parcels | eliminated / recalibrated | the fry pond no longer a 1-3 mu parcel form by share (see M60) |
| M60 | A3 | MIXED | archetypes/200 | One parcel in ten a fry pond | eliminated / recalibrated | FRY_FORMS knob: none, or a fry village (the smallest ponds up to 7/10 of the water); the one-in-ten removed |
| M61 | A4 | MIXED | archetypes/180, archetypes/210 | The sty at the water | eliminated / recalibrated | the PigSty modal: on the pond bank as the 1639 pen; no flush-into-the-pond claim |
| M62 | A4 | MIXED | archetypes/171, archetypes/210 | The pig shed on the dike | eliminated / recalibrated | the 5-10 m shed-dike width not a rule the maps follow (PigSty modal) |
| M63 | A4 | PREMODERN-ATTESTED | archetypes/620, homesteads/260, homesteads/211 | Manure pits | kept (attested) | the manure jar by the road attested (Staunton 1797) |
| M64 | R1 | MIXED | religion-and-death/710, 090 | The torii avenue | waiting on the GM | the avenue of arches at ordinary shrines: the GM ruled the pitch for all maps knowing no village row was found (2026-09-27) - waiting on the ruling; Hoshigaoka's seven are the GM's |
| M65 | R1 | MIXED | religion-and-death/730, 122 | The sanctuary fence | eliminated / recalibrated | the sanctuary fence dropped from the wealth knob (programs.md); no kind drew it |
| M66 | R1 | MIXED (undated-custom (shrine half)) | religion-and-death/720, 130 | The swept collar | eliminated / recalibrated | no swept collar at arches or graves (the clearings' collars 30 -> 0); the precinct's ground kept, not called swept (key precinct clearing); undated-custom (shrine half) |
| M67 | R1 | MIXED | religion-and-death/240 | Salt wards | kept (attested) | nothing live draws salt; the record allows only a small heap at a trade's door |
| M68 | R2 | MIXED (undated-custom (the hamlet's own ground)) | religion-and-death/155 | One ground per village | eliminated / recalibrated | no hamlet burial ground of its own (hamlet_burial village_ground only); undated-custom |
| M69 | R2 | MIXED | religion-and-death/190 | The crematory's set-back | eliminated / recalibrated | the 390 ft crematory set-back relabeled a guess (190); no scripted map draws it |
| M70 | R2 | MIXED | religion-and-death/202 | Cremation-ground size and fire bed | eliminated / recalibrated | the cremation ground open-air on most seats (ROOFED_SHARE 0.25), no pyre platform or hut |
| M71 | R2 | MIXED | religion-and-death/700, 530 | Six stone jizo | eliminated / recalibrated | the six jizo only at a burial ground's entrance; the village cremation ground on its own draws none |
| M72 | R3 | MIXED | religion-and-death/740, 460 | The town monastery | kept (attested) | the town monastery's defaults calibrated to the Edo holdings; bands' ends a guess |
| M73 | R3 | PREMODERN-ATTESTED | religion-and-death/040 | Clergy families' homes | kept (attested) | clergy homes attested; the count the GM's |
| M74 | R4 | MIXED | religion-and-death/160 | Ground per population | kept (attested) | the death rate rests on Edo registers; no drawing change |
| M75 | R4 | MIXED | religion-and-death/180 | Set-back from water | eliminated / recalibrated | the scaled water set-backs gone: the village cremation ground keeps a bank margin only; the hamlet's own ground (which carried them) retired by M68 |
| M76 | R4 | MIXED | religion-and-death/750, 206 | Burial-ground ladder and path factor | kept (attested) | no code applies the 1934 path factor; the ladder stands on the Qing charity grounds (750) |
| M77 | R4 | MIXED (undated-custom) | religion-and-death/270 | Burial distance | eliminated / recalibrated | no set distance drawn; the village cremation's 650 ft is a search reach, relabeled; downstream kept as a drawing tie-break only (attested today only) |
| M78 | R5 | PREMODERN-ATTESTED | religion-and-death/760 | Precinct area | kept (attested) | the precinct band is Edo-attested (760) |
| M79 | R5 | PREMODERN-ATTESTED | religion-and-death/760 | The register disclosure | kept (attested) | the disclosure reworded (124, 125) |
| M80 | R5 | MIXED | religion-and-death/770 | The unroofed basin | kept (attested) | the basin is drawn plain with its roof labeled a guess (religion-and-death 770); neither form is modern-only |
| M81 | R5 | MODERN-ONLY | religion-and-death/730 | The fence as a gift | eliminated / recalibrated | as M65 |
| M82 | Y1 | MIXED | ways/010 | Bridge landing | kept (attested) | the bridge carried into its banks is premodern; the 10 ft landing a guess |
| M83 | Y1 | MIXED | ways/030 | The plank bridge | kept (attested) | the plank bridge premodern; its bund placement a guess (ways/030) |
| M84 | T1 | MIXED | towns/050 | The wagon inn | legacy map - owed at conversion | the inn's grooms' lean-to, well and the hatago's stable and cart yard - legacy towns and cities, owed at conversion; the wagon inn's single story a GM question |
| M85 | T1 | MIXED (undated-custom) | towns/350 | Stall size | legacy map - owed at conversion | the stall 8-9 ft, not 10 - legacy, owed at conversion |
| M86 | T1 | MIXED | towns/040 | The flophouse | legacy map - owed at conversion | the flophouse as a plain thatched house - legacy, owed at conversion |
| M87 | T2 | MIXED | towns/210 | Core length | legacy map - owed at conversion | the road town's length from the Edo counts - legacy, owed at conversion |
| M88 | T2 | MIXED | towns/220 | Core density | legacy map - owed at conversion | the street front ~32 ft per house - legacy, owed at conversion |
| M89 | T2 | PREMODERN-ATTESTED | towns/440 | Market catchment | kept (attested) | the market's reach dated to the mid-Qing |
| M90 | T3 | MIXED | towns/410 | Hayfield barns | legacy map - owed at conversion | no hay barns; haystacks or stores - legacy (Hoshizora), owed at conversion |
| M91 | T3 | PREMODERN-ATTESTED | towns/420 | The young coppice at the edge | kept (attested) | the young coppice dated before Meiji |
| M92 | T3 | MIXED | towns/600, vegetation/320, towns/410 | The hay-bale pasture | legacy map - owed at conversion | no bales or fence round the hayfield - legacy (Ubame, Hoshizora), owed at conversion |
| M93 | T4 | PREMODERN-ATTESTED | towns/130 | The communal windbreak | kept (attested) | the communal windbreak premodern; ring vs one-side a knob candidate (future-work) |
| M94 | T4 | MIXED | towns/140 | The shelter band | kept (attested) | the hugging band premodern; no bearing rule drawn |
| M95 | T4 | MIXED | towns/150 | The town paddy plot | kept (attested) | the plot inside the 1602 register span as one diked paddy |
| M96 | U1 | MIXED | urban-features/082 | Stable troughs | legacy map - owed at conversion | the stable trough described as a plain one-sided trough - legacy, owed at conversion |
| M97 | U1 | MIXED | urban-features/090 | Well capacity | eliminated / recalibrated | the Well modal: the Beijing figure, not the Sphere standard |
| M98 | U1 | MIXED | urban-features/270 | What a well looks like | kept (attested) | sweep, pulley frame and roof premodern |
| M99 | U2 | MIXED | urban-features/710 | The brewery's vat hall | legacy map - owed at conversion | the brewery's vat hall 50-62 ft - legacy, owed at conversion |
| M100 | U2 | PREMODERN-ATTESTED | urban-features/340 | The Chinese pawnshop | kept (attested) | the pawnshop attested |
| M101 | U2 | MODERN-ONLY (undated-custom) | urban-features/430 | The village smithy | record only | no map draws the village smithy; the 21 x 18 plan is held back (undated-custom) |
| M102 | U2 | MIXED | urban-features/440 | The town smithy | record only | the town smithy unscripted; its frontage 21 ft |
| M103 | U3 | MIXED | urban-features/720, 040 | The log-boom pen | legacy map - owed at conversion | the log boom's chain fence and pens - legacy (Minami), owed at conversion: moored rafts or a pond |
| M104 | U3 | MODERN-ONLY | urban-features/150, 152 | The charcoal cooling ground | eliminated / recalibrated | the charcoal yard's cooling apron removed from the engine; the CharcoalStore and cart-yard modals drop the cooling and 30 ft gap |
| M105 | U3 | MIXED | urban-features/190 | Bale sizes | eliminated / recalibrated | the bale notes (TaxBarge, CharcoalBales modals) |
| M106 | U3 | PREMODERN-ATTESTED | urban-features/520 | Hulling on the farm | kept (attested) | hulled rice attested |
| M107 | U4 | PREMODERN-ATTESTED | urban-features/130, towns/040 | Flophouse siting | kept (attested) | the city's flophouse quarter is Edo |
| M108 | U4 | MIXED | urban-features/032 | The farrier | legacy map - owed at conversion | the farrier stands; the sling frame is a question of region (Western), not modernity - on frozen maps only; the Qing two-post tie frame is the attested alternative (future-work) |
| M109 | B1 | MIXED | buildings/220 | The family privy | kept (attested) | two privies attested; the family privy's seat a guess (modal wording) |
| M110 | B1 | MIXED | buildings/360 | The kamado on the board floor | kept (attested) | the board-floor kamado attested in an Edo tenement; its samurai use a guess |
| M111 | B1 | MIXED | buildings/370 | The kitchen door | eliminated / recalibrated | the Door modal says nothing of who used the kitchen door |
| M112 | B1 | MIXED | buildings/380 | The 67-tsubo house | eliminated / recalibrated | the Residence and Kitchen modals measure against the 49-tsubo house of 1794, not the 67-tsubo Meiji plan (the sheets were already at 49) |
| M113 | B2 | PREMODERN-ATTESTED | buildings/290 | The shared garden | kept (attested) | Takayama's shared garden dated to the 1830 plan |
| M114 | B2 | PREMODERN-ATTESTED | buildings/470 | The notice board at the gate | eliminated / recalibrated | the notice board: notices at the office gate accurate (Chinese county office), the freestanding board a guess |
| M115 | B2 | MODERN-ONLY (undated-custom) | buildings/560 | The striking bundle | eliminated / recalibrated | Ubame's striking bundle replaced by upright posts; the knob's bundle value gone; undated-custom |
| M116 | B2 | MIXED | buildings/620 | The storehouse door leaf | kept (attested) | paired storehouse leaves attested; the width a convention |
| M117 | B3 | MIXED | buildings/780 | The drill hall | legacy map - owed at conversion | the drill hall three bays - legacy city tier, owed at conversion |
| M118 | B3 | PREMODERN-ATTESTED | buildings/800 | The Chinese carters' inn | kept (attested) | the carters' yard inn attested |
| M119 | B3 | MIXED | buildings/900, buildings/750 | Bunk rooms | eliminated / recalibrated | no bunk rooms (Barracks modal, buildings.md, Hayakawa's sheet comment); the size band's recalibration to the staff rowhouse recorded (future-work/compounds) |
| M120 | C1 | MIXED | cities/capitals/600, 340 | Funerary-ground clearance | legacy map - owed at conversion | the funerary pyre clearance and the 'triple the bonfire' reasoning - legacy cities, owed at conversion (citybudget comment) |
| M121 | C1 | PREMODERN-ATTESTED | cities/capitals/310 | The castle's area | kept (attested) | the castle's ~50 ha is the Edo castle's |
| M122 | C1 | PREMODERN-ATTESTED | cities/capitals/040 | The sluice's calendar | kept (attested) | the field-gate calendar premodern; any April/September naming dropped where found |
| M123 | C2 | MIXED | cities/river-cities/600, 020 | Moat offtake angles | legacy map - owed at conversion | the moat's junction tilts, a guess on modern hydraulics ruled in 2026-07-24 - on frozen maps only, owed at conversion |
| M124 | C2 | MODERN-ONLY | cities/river-cities/070 | Private landings | eliminated / recalibrated | the Dock modal: a private back-gate landing is modern only; Hayakawa's steps across the street stand; legacy maps' back-gate landings owed at conversion |
| M125 | C2 | MODERN-ONLY (undated-custom) | cities/river-cities/060 | The boatmen's water-god shrine | eliminated / recalibrated | the boatmen's altar is the boats' guardian's shrine (Hayakawa sheet, modal); undated-custom |
| M126 | C3 | MIXED | cities/government/600 | The generous lot | legacy map - owed at conversion | the generous lot capped at about double the Fukui ladder - legacy cities, owed at conversion |
| M127 | C3 | MIXED | cities/fabric/230 | The storehouse cap | legacy map - owed at conversion | the storehouse cap ~1 to 10 houses - legacy cities, owed at conversion |
| M128 | C5 | MIXED | cities/fabric/030 | The open reserve | legacy map - owed at conversion | the 25-30% reserve norm dropped from citybudget's text; the 20% cap stands |
| M129 | C5 | PREMODERN-ATTESTED | cities/hinterland/600, 050 | Farmland inside the wall | kept (attested) | farmland inside a Chinese wall dated from the Sui-Tang |
| M130 | C5 | MIXED | cities/defenses/100 | Moat width | legacy map - owed at conversion | the moat ~36 ft (provincial) / ~10 ft (county), not 66 - legacy cities, owed at conversion |
