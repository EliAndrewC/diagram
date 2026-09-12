# Feature 233 - research and measurement

## R1 - what the map actually draws (measured 2026-09-12, from the shipped manifest)

Read from `pool/hamlets/kuwabata/kuwabata.json`; the hamlet tier is 1 px = 1 ft.

| quantity | value |
|---|---|
| pig sties | 7 (`meta.pond_stock.sties`), on 26 dike ponds, 16 houses |
| duck pens | 2 |
| sty footprint | 8 x 6 ft (`STY_FT`) |
| **sty footprint to nearest stub SEGMENT** | **0, 0, 0**, 3.04, 31.07, 64.99, 128.73 ft |
| ... of which, the stub's chord INSIDE the footprint | 3.62, 2.56, 0.06 ft |
| duck pen DRY run to nearest stub segment | 2.32, 10.70 ft |
| duck pen FENCE ARC to nearest stub segment | **0** (crosses at 2404.8, 796.5), 12.91 ft |
| sluice stub length | median 26.5 ft, mean 28.0, min 19.1, max 41.2 (feed-only median 27.7); the pond-5 stub, the motivating case, is 23.9 |
| pond water area | median 28,920 sq ft = 4.03 mu = 0.27 ha |
| pond collar (water edge -> parcel edge) | median 6.7 ft = 2.0 m (min 3.2, max 9.4) |
| shared dike (water edge -> the neighbor's water edge, 68 adjacent pairs) | median 43.6 ft = 13.3 m |
| the strip a sty actually stands in | 8.5-15.3 ft = 2.6-4.7 m |

Kuwabata is the ONLY map in either pool tree carrying pig sties.

**TWO WAYS THIS TABLE WAS WRONG, BOTH UNDERSTATING THE SAME WAY.** Recorded because both traps are
available to anyone measuring a thin feature against a small one.

*First pass* gave the fixture's CENTER to the stub's pond-side ANCHOR - 6, 7, 8, 12 ft - which reads as
a near miss. A stub is a SEGMENT of 19-41 ft (median 26.5), so measuring it by one endpoint overstates every distance to
it. Caught by spec-fidelity round 2.

*Second pass* measured the drawn footprint to the segment, but by SAMPLING the footprint boundary at 8
points per edge and taking the nearest sample, with **no segment-intersection test** - and a measure
built that way cannot return zero. It reported an overlap as a sub-foot gap: 0.13, 0.03, 0.08 for the
three sties and 0.188 for the pen's fence. Caught by spec-fidelity round 3, which reproduced those exact
numbers from the method, which is how the method was identified.

The true figures are in the table above and they are not near misses: on three ponds the feed stub
passes THROUGH the shed, and the duck pen's fence crosses its stub. Any distance function this feature ships MUST return 0 on intersection and MUST be selftested against a
stub driven through a rect - otherwise SC-001's no-overlap clause would score today's crossing shed as
0.13 ft and pass it. That MUST is carried by **spec SC-006**; a rule stated only here would bind
nothing, which spec-fidelity round 4 caught it doing.

**The mechanism, read from the code rather than inferred.** `pondstock._bank_seat` returns the midpoint
of the parcel edge nearest the house cluster, pulled in by `BANK_INSET_FT` = 5.5. `fields/landuse.py`
`_landuse_dikepond_sluices` anchors the FEED sluice at the pond's uphill corner and the DRAIN at its
downhill corner. On a 127 x 143 ft pond those two land on the same short bank whenever the houses lie
uphill of it. `farm_fixtures.pond_fixture_fits` holds the fixture off `pig_sties`, `duck_pens`,
`houses`, `farm_sheds`, `byres`, `wells`, `kosatsuba` and `footbridges` - and off nothing in the water
system.

**Cost of the fix, measured before proposing it.** Ranking every parcel edge of the four affected ponds
by distance to the house cluster and recording each seat's clearance to the nearest sluice anchor: a
seat 30-45 ft clear exists on all four, 10-30 ft further from the houses than the seat now chosen (pond
5: 344 ft / 44 ft clear against the chosen 330 ft / 6 ft). So FR-003's ranked seat costs the household a
few paces and loses no fixture.

**Prior sighting, not recognized as this.** `pool/hamlets/kuwabata/kuwabata.notes.md` records a
settlement-review round measuring the pond sluice's hit box taking 88.4% of a pig sty's own footprint.
It was fixed as a HOVER precedence problem. The two glyphs standing in the same place was the symptom;
nobody asked why.

## R2 - source-reader pass A (FAO/NACA corpus and the ISIS summary)

| claim | verdict |
|---|---|
| C1 the shed is on the dike so excreta enter directly | READ |
| C2 any siting rule relative to inlet / outlet / sluice | **NOT-FOUND** |
| C3 manure loading as a hazard, with limits | READ |
| C4 pond water for domestic use; shed kept clear of it | NOT-FOUND (vegetables only) |
| C5 spacing of sheds along a dike | READ (dike WIDTH) / NOT-FOUND (spacing) |

Quotes, with the page each was read on:

- ch. 7 <https://www.fao.org/4/ac264e/ac264e09.htm>: "There are two types of pigsties in China: the
  simple pig shed constructed on the pond dyke or over the water surface and the centralized hog
  house." / "If the area of a fish pond is less than 8 mu, a pigsty can be set up on the pond dyke and
  pig wastes will flow directly into the pond." / "If more than 30 pigs are raised in the same spot,
  there is too much manure for the direct-flow method." / "Fish surfacing increases (dissolved oxygen
  content decreases) when pig manure sinks to the bottom of the pond or when too much manure flows into
  the pond." / "fresh pig manure mixed with pond water is spread over the whole pond at a daily rate of
  20-40 kg/mu." / "Usually, no manure is applied after mid-October."
- ch. 9 <https://www.fao.org/4/ac264e/AC264E11.htm>: "Pigsties are usually built on the pond dike of an
  integrated fish farm so that the pig excrement can be directly flushed into the pond." / "Besides
  increasing the utilization rate of the feedstuffs, this technique of feeding animal manures to fish
  fertilizes the water, producing plankton which is a good natural fish food."
- ch. 10 <https://www.fao.org/4/ac264e/AC264E13.htm>: "To lead the pig excreta into the fish ponds, the
  pigsties are generally built on pond dikes or on highlands close to the fish pond." / "The width of
  the dikes between fish ponds and inflow and outflow canals should be kept within 5 m; the width of the
  dikes for pigsties, cow sheds piping, or traffic should range from 5 to 10 m." / "Duck and goose pens
  are built separately along the pond dikes."
- FAO IAA primer <https://www.fao.org/4/y1187e/y1187e34.htm>: wastes act by "stimulating phytoplankton
  production; and acting as substrate for bacterial production (detritus) and as feed for zooplankton";
  the pen-siting options are given as a trade-off table headed by LABOR and animal comfort - "On the pond
  dike: Pens close to the pond to reduce labour cost of loading waste" - not by contamination.

**A scope tension inside one report, NOT resolved here.** Ch. 7's household shed flows straight to the
water; ch. 10 describes dike pigsties whose "pig excreta is channeled into septic tanks for fermentation
before it is used". Both are stated as Chinese practice. Two attested forms is the shape of a KNOB, but
ch. 10 reads as modern design guidance and wants `source-applicability` before it drives anything. Spec
233 "Out of scope".

**Do not cite for manure.** ch. 7 pt 1 <https://www.fao.org/4/ac264e/AC264E08.htm> has "The pH of the
water will decline, the biological oxygen demand (BOD) will increase, and nitrites and gases such as
NH3, H2S, CH4 and PH3 will accumulate and harm the fish" - but its subject is EXCESSIVE SILT, not pig
manure. The reader flagged it; it is recorded here so a later session does not reach for it.

## R3 - source-reader pass B (the treatises, Japan, and the where-it-enters question)

| claim | verdict |
|---|---|
| C1 manure is feed and fertilizer, not pollution | READ (premodern half weak - see below) |
| C2 a traditional rule siting pens away from water | **CONTRADICTED** |
| C3 pigs absent from premodern Japan on Buddhist grounds | **CONTRADICTED in part** |
| C4 harm from excessive or concentrated manure | READ |
| C5 Japanese carp culture - what fed the fish, any pen beside it | READ (siting) / SUMMARY-ONLY (feed) |

- **齊民要術 (Qimin Yaoshu, c. 540 AD), 卷第六 養豬第五十八**
  <https://zh.wikisource.org/zh-hant/齊民要術/卷第六>. The only siting instruction the pig chapter gives:
  「圈不厭小。〈圈小則肥疾。〉處不厭穢。〈泥污得避暑。〉亦須小廠，以避雨雪。」 - "The pen is not disliked for being small - a small
  pen makes them fatten fast. The place is not disliked for being filthy - mud and muck let them escape
  the heat. A small shed is also wanted, to keep off rain and snow." (translated from the Chinese by
  this project; the original is the checker's anchor, its 〈〉 interlinear commentary kept.) 處不厭穢 is the
  opposite of the rule the GM's question supposed, and nothing in it concerns water.
- **The Japanese privy is a hut over the water.** kotobank 厠 <https://kotobank.jp/word/厠-468872>,
  aggregating デジタル大辞泉 and 世界大百科事典: 「《川の上に設けた川屋の意とも、家の外側に設けた側屋の意ともいう》」 - "said to mean either kawaya,
  'the hut set over the river', or kawaya, 'the hut set outside the main house'" (translated from the
  Japanese by this project). Dictionary reporting an etymology, not a survey of where privies stood;
  the 世界大百科事典 entry is flagged 旧版 on the page.
- **Concentration at the point of entry is the one place-dependent hazard in the record.** FAO
  consultancy report <https://www.fao.org/4/ac257e/AC257E05.htm>: "Pig sties and cow sheds should be
  constructed on the dikes to minimize construction costs ... In the latter case, manure distribution
  techniques generally need to be employed to avoid the development of anaerobic conditions in the pond
  adjacent to the livestock quarters." Observed: "It was observed that the fish lost their apetite,
  presumably due to lack of dissolved oxygen because of anaerobic conditions at the manuring - feeding
  sites". Remedies: buckets, brick or concrete distribution channels, sprinklers. It keeps the shed on
  the dike in the same sentence, and says nothing about the inlet.
- **Japan, pigs.** Hudson and Munoz Fernandez, "Henceforth fishermen and hunters are to be restrained",
  *Asian Archaeology* (2023), open access
  <https://pure.mpg.de/rest/items/item_3527987_3/component/file_3528006/content>. The Buddhism
  explanation is named as an assumption under review: "two broad assumptions continue to shape writings
  on this topic: first, that while pigs and chickens were introduced into the archipelago in the Bronze
  Age Yayoi 弥生 period (1000 BC - AD 250), they never really 'took off' in the Japanese context; and
  second, that while horses and cattle were added from the fifth century AD, religious and other
  cultural proscriptions limited the consumption of meat until Westernisation in the nineteenth
  century." Their own reading: "With the exception of Okinawa, Japan seems to have followed the pannage
  system". So a PENNED pig in a Japanese village is doubly unsupported, and nothing links a Japanese pig
  to a pond.

**ABSENCE NOTE - the question the GM asked.** Whether a pig sty stands near or away from a dike pond's
INLET or OUTLET sluice: searched 2026-09-12 across the FAO/NACA integrated-farming corpus (chs. 7-10 of
ac264e, the ac233e training manual, the y1187e primer, the ac257e consultancy report, the x6709e
training series), the ISIS dike-pond summary, and Chinese and Japanese material including 齊民要術 and
農業全書, by two readers independently. NOT-FOUND, for it and against it. No key and no link: there is
nothing to cite. The clearance this feature adds rests on FR-001's geometry and FR-002's labeled guess,
NOT on this question.

**NOT recorded as a finding.** That incoming water at a feed sluice would disperse the manure, making
the inlet the best seat, is this session's inference from R3's anaerobic-patch material. No source says
it. Spec D4.

## R4 - the Saku carp page, re-read with a shell (2026-09-12)

Reader B returned this page as SUMMARY-ONLY and explicitly refused to quote it: one returned sentence
was internally incoherent, the signature of a paraphrase presented as a quotation, and the agent had no
shell. Re-fetched here with `curl` and decoded Shift_JIS (0 replacement characters), per the project's
own note that these pages garble under the fetch tool:

<https://www.sakucci.or.jp/sakukoi/rekishi/> 「長野県は群馬と並んで、国の主力産業であった製糸業を支える、養蚕の盛んな地域であり、佐久は養鯉飼料として最も
優れているサナギが容易に手に入る立地にも恵まれ、鯉の大量生産が可能となった。」 - "Nagano, alongside Gunma, was a region of flourishing
sericulture supporting the silk-reeling industry that was one of the nation's main industries, and Saku
was blessed with a location where pupae - the finest of carp feeds - were easily obtained, which made
mass production of carp possible." (translated from the Japanese by this project.)

So the verified claim is narrower than the paraphrase: silkworm pupae are **carp feed**, not pond
fertilizer, and the reader was right to distrust what it got. **The limit that governs its use**: the
passage sits under 「明治の時代を迎え」 and cites a 1871 survey, so it is MEIJI - post-1868 - and is not
premodern evidence. A silk-and-fish hamlet feeding its fish on pupae is suggestive and undrawn; it is
NOT used by this feature. Recorded so the search need not be repeated.

## R5 - hosts that refused (one attempt each, not retried)

link.springer.com (303 to a login IDP), sciencedirect.com (403), artic.edu (403 - the Han pigsty-privy
material, which would bear on R3's C2 and remains uncited), jfa.maff.go.jp (403),
repository.seafdec.org.ph (timeout), tourism.repo.nii.ac.jp (302 to a signed object-storage URL).
農業全書 (Nogyo Zensho, 1697) surfaced no digitized full text - only works ABOUT it - so it says nothing
either way here.

## R6 - the ranked-seat rule simulated before implementing it (2026-09-12)

FR-004 promises no fixture is lost. Rather than discover that at the gate, the rule was simulated
against the shipped manifest: the placer's own pond order (grow-out ponds, nearest the house cluster
first, pens before sties), each pond's parcel edges ranked by distance to the house cluster, each
candidate seat tested against the true point-to-SEGMENT distance to every `dikepond_sluices[]` stub
(not to its anchor - a stub runs 19-41 ft, median 26.5, and the anchor alone understates the overlap).

**SUPERSEDED - kept only as the record of what was measured when.** This run tested the dry footprint
alone and used the sampled distance R1 describes, so its clearance column is wrong throughout; the live
figures are in the corrected run below.

| working margin | pens | sties | worst clearance achieved |
|---|---|---|---|
| 0 ft (footprint only, FR-001 alone) | 2/2 | 7/7 | ~~5.5 ft~~ |
| 4 ft | 2/2 | 7/7 | ~~13.1 ft~~ |
| 6 ft | 2/2 | 7/7 | ~~13.1 ft~~ |
| 8 ft | 2/2 | 7/7 | ~~13.1 ft~~ |
| 12 ft | 2/2 | 7/7 | ~~17.1 ft~~ |

Every fixture PLACED at every margin tried, which is the one conclusion that survived the correction:
FR-004 costs nothing on this map, and the margin can be chosen on its own merits rather than against a
placement budget. (An earlier reading of the flat 13.1 ft column - that the binding seat is the same one
throughout - rested on the superseded figures and is dropped; the corrected run's flat 8.5 ft supports
the same point and is where it is now made.)

**Re-run with the duck pen's FENCE ARC included, on a corrected distance** (spec-fidelity rounds 2 and
3 - the first run tested the dry footprint only, and the second used the sampled measure described in
R1). The distance now returns 0 on intersection. It is `measure_geom.py`, committed beside this file, and it
CARRIES its selftest (`python3 measure_geom.py`) rather than claiming one: a stub driven through a rect,
a stub wholly inside one, a clear gap, and an open polyline that must not be silently closed into a
region. Verified independently by spec-fidelity round 4 against shapely - 300,000 random trials, max
absolute error 1.1e-14, zero disagreements on the zero/nonzero verdict:

| working margin | pens | sties | worst clearance achieved |
|---|---|---|---|
| 0 ft | 2/2 | 7/7 | 0.0 ft |
| 4 ft | 2/2 | 7/7 | 8.5 ft |
| 6 ft | 2/2 | 7/7 | 8.5 ft |
| 8 ft | 2/2 | 7/7 | 8.5 ft |
| 12 ft | 2/2 | 7/7 | 12.6 ft |

So covering the fence arc costs nothing either, and the choice to include it (spec FR-001) is free
rather than a trade. **The corrected measure did not move this result** - the same 7/7, 2/2 and 8.5 ft
as the sampled run produced - because the sampled measure erred toward ACCEPTING by at most its ~1 ft
sample spacing, and the seats these margins choose are clear by far more than that. It moved the
as-shipped figures in R1, not the placement conclusion.

**Implementation note for FR-003** (spec-fidelity round 3, needing no requirement because SC-001
backstops it on the manifest): the fence arc is a function of the SEAT and the pond's water outline, so
a ranked-seat test must build the arc each candidate seat WOULD produce rather than reusing the shipped
one. Reimplementing `duck_pen`'s loop (`PEN_WET_FT` 12.0, half-width 5, five steps of `pi*t`,
`sin(ang)*0.9`) reproduces both shipped `wet` polylines to within manifest rounding, so this is
straightforward - but a seat test that forgets it would check the old arc against a new seat.

This does NOT prove the rule is free on an unrolled seed; it proves it is free on the one map that has
the feature today, which is the map the GM is looking at. A seed whose ponds are smaller could refuse a
seat, and FR-003's ranked fallback is what keeps that from silently dropping the fixture to another pond.

## R7 - the seat bound, measured (2026-09-12, after settlement-review asked for one)

Over the nine ponds that carry a sty or a pen, with seats rebuilt by the engine's own rule (parcel edge
midpoints pulled 5.5 ft toward the parcel centroid) and ranked by distance to the house cluster:

| quantity | measured |
|---|---|
| far bank, over the first choice | **155.6 to 320.0 ft** |
| the bound's own allowance (pond PARCEL center less nearest seat) | **60.5 to 157.2 ft** per pond |
| cost of the ACCEPTED seat over the first choice | **+0 to +21.2 ft** |
| slack on the accepted seat, inside the bound | **57.3 ft** at its tightest |

**THE SAME FAULT, A THIRD TIME.** R1 records two earlier versions of it - a distance measured to a
stub's endpoint, then a distance from a measure that could not return zero. This round's was a third:
FR-012, the placer comment, the gate test docstring and the map's notes all carried "up to 288 ft" and
"a limit of about +70", and neither was a statistic of anything. 288.1 ft is pond 20's own spread and
the true maximum is 320.0 on pond 24; the "+70" described three of the nine ponds. The argument was
unaffected - the bound is still free on this map - but the numbers a reader would try to reproduce were
not the numbers. Every figure above was re-derived from the manifest before it was written here, and the
four places that quote them now quote these.

The pattern worth carrying forward: **a number written in four places is a number whose method is in none of them.** R1 and R6 exist so the derivation travels, and FR-012, the placer comment, the gate test docstring and the map's notes all point here.

**A postscript, because it is the same fault wearing a third face.** The first draft of this paragraph
said the gate test did not point here "because no test in this tree cites a `specs/` path". That is
false - 34 test files cite one, and `tests/test_rolls.py` is a gate test that REQUIRES a
`specs/NNN-slug/research.md#R<k>` pointer and asserts the file exists. Rather than add a one-line
pointer, the session invented a property of the tree to excuse its absence, and the tree contradicts it
thirty-four times. An unwritten pointer is cheap to add and expensive to justify; reach for the pointer.
