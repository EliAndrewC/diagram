# Feature 233 - research and measurement

## R1 - what the map actually draws (measured 2026-09-12, from the shipped manifest)

Read from `pool/hamlets/kuwabata/kuwabata.json`; the hamlet tier is 1 px = 1 ft.

| quantity | value |
|---|---|
| pig sties | 7 (`meta.pond_stock.sties`), on 26 dike ponds, 16 houses |
| duck pens | 2 |
| sty footprint | 8 x 6 ft (`STY_FT`) |
| sty to nearest sluice ANCHOR | 6, 7, 8, 12, 43, 71, 133 ft |
| duck pen to nearest sluice anchor | 12, 18 ft |
| sluice stub length | ~24 ft (`dikepond_sluices[]` a-to-b) |
| pond water area | median 28,920 sq ft = 4.03 mu = 0.27 ha |
| shared dike width | median 21 ft = 6.5 m (parcel bbox less water bbox, both axes, all 26 ponds) |

Kuwabata is the ONLY map in either pool tree carrying pig sties.

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
(not to its anchor - the stub is 24 ft long and the anchor alone understates the overlap).

| working margin | pens | sties | worst clearance achieved |
|---|---|---|---|
| 0 ft (footprint only, FR-001 alone) | 2/2 | 7/7 | 5.5 ft |
| 4 ft | 2/2 | 7/7 | 13.1 ft |
| 6 ft | 2/2 | 7/7 | 13.1 ft |
| 8 ft | 2/2 | 7/7 | 13.1 ft |
| 12 ft | 2/2 | 7/7 | 17.1 ft |

Every fixture places at every margin tried, so FR-004 costs nothing on this map, and the margin can be
chosen on its own merits rather than against a placement budget. The flat 13.1 ft across 4-8 ft says the
binding seat is the same one throughout - the rule is not scraping against its limit, which is what a
number rising in lockstep with the margin would have shown.

This does NOT prove the rule is free on an unrolled seed; it proves it is free on the one map that has
the feature today, which is the map the GM is looking at. A seed whose ponds are smaller could refuse a
seat, and FR-003's ranked fallback is what keeps that from silently dropping the fixture to another pond.
