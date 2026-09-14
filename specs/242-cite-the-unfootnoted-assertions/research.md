# Feature 242 - research notes

## R1 - how big "the rest" actually is, derived rather than restated (2026-09-13)

<!-- The measurement harness is measure/inventory_census.py and measure/note_census.py; every figure
     below is a key in measurements.json, re-derivable with `--record`. -->

Feature 238's closing report put this feature's remainder at "about 600 `CITE` items", taken from its
R6 disposition count of 631. **That number is too large, because it counts items 238 then closed.** R6
classified every one of the 695 inventoried sentences BEFORE the work was done; 238 went on to convert
142 inline markers into absence notes at their own assertions, and R7 states the consequence plainly -
*"A reader-report item whose entry quotes a marker is therefore closed, and that is the largest single
class"* - without ever restating the total.

**The derivation.** R7 declares the four reader reports the authority on identity, so the work list is
a filter over them: every item the readers named, less the items whose prose carried a marker, less
the classes R7 closed by hand. `measure/inventory_census.py` performs it.

The parser's own credibility is the first thing it checks: it reproduces **695** items
(`m:inventory-items`) and every one of the four per-report totals the reports state - 171, 203, 153,
168 - and refuses to report anything if one of them disagrees. The reports use three different item
shapes, and getting all four to their stated totals is what makes the marker split worth reading at
all.

**The answer: 462 to 472 items** (`m:worklist-low`, `m:worklist-high`), against the closing report's
"about 600". The range is honest rather than decorative: the parser classifies 201 items as carrying
a marker where the readers' own stated splits total 211, a disagreement of 10
(`m:marker-classifier-disagreement`), and the wider bound is the one to plan with. Twenty-two
further items are closed in a class other than the marker conversion - the nine roster-hidden claims
on `urban-features`, the five on `buildings`, the six sections that disclosed with no footnote at
all, the one `settlements.html` item that restates footnoted canon, and the caravan inn.

**What the filter does NOT subtract, and why that is right.** R7's fourth class is the twelve defects,
and they are absent from the subtraction on purpose. Those were found in the SECOND reading, of
material that already carried a footnote - a misread workforce figure, a quotation readable on no page
its note pointed at, a damaged text layer - while the four inventory readers named only assertions
carrying NO footnote. The two populations are disjoint by construction, so subtracting the twelve would
understate the list. Where one defect did coincide with a report item, the list is overstated by that
much, at most twelve.

**Checked rather than asserted.** Searching the four reports for each defect's distinctive subject
returns nothing for the Guangdong two-site argument, the Korean grove mean, the insulated hearth, the
hatago fittings and the water-carriers - zero hits apiece. The nearest thing to a collision is item U99
of the religion/vegetation/urban-features report, the 6:1 wood-to-charcoal conversion the reader calls
*"a measured conversion ratio carrying the whole two-site decision"*, marked HIGH with no marker. That
is not one of the twelve: the defect was the Wagner workforce misread and the heading built on it, both
in footnoted material, while U99 is a bare assertion that still owes a citation and correctly stays on
this feature's list. The adjacency is the useful part - correcting an argument did not discharge the
unfootnoted sentence sitting next to it.

Of the 494 parsed bare items - the population BEFORE those twenty-two closures, which is why these do
not sum to the work list - the readers rated **222 HIGH, 24 MEDIUM-HIGH, 207 MEDIUM, 4 LOW-MEDIUM and
37 LOW** (`m:worklist-high-confidence`, `m:worklist-medium-high-confidence`,
`m:worklist-medium-confidence`, `m:worklist-low-medium-confidence`, `m:worklist-low-confidence`).

**The two hedged tiers are reported, not rounded.** The readers hedged 29 of the 695 inventoried
items with a compound label (`m:hedged-items`), 28 of them in this bare population (`m:hedged-bare`)
and at most 27 on the work list (`m:hedged-worklist-max`) - the caravan inn is itself MEDIUM-HIGH and
bare and is one of the twenty-two R7 closes, and it is the only closure the reports name, so the
other twenty-one cannot be checked for hedges. Reading only the first word - as the first version of
this parser did - buckets every one of them a tier low, a MEDIUM-HIGH into MEDIUM and a LOW-MEDIUM
into LOW, which would have the ordering meet all 28 of the bare ones later than the readers meant.

**All three counts are DERIVED and recorded, and that is the lesson rather than a detail.** They were
stated in prose twice and were wrong about their population both times, because the harness printed
the tier shares and nothing else - so `make figures` had nothing to check, and two review rounds
re-ran every other number without touching these. The harness computes them now, and its
unrecognized-tier refusal covers every item rather than only the bare ones, since the 29 is taken
over all 695. Collapsing a
deliberate hedge into either neighbor invents a judgment the reader declined to make, so the compounds
keep their own tiers. This moves no item on or off the work list; it only corrects what the split says.

That ordering is the one this feature works in, and it replaces the ordering feature 238's draft
proposed - "a claim the record states WRONGLY costs a reader more than one it states without
support" - which cannot
be applied, because nothing in the reports marks an item as wrong rather than unsupported. That class
was found by READING, and this feature is told not to re-read.

## R2 - the second class: an absence note that records no search (2026-09-13)

`measure/note_census.py` counts what the record's footnotes are actually made of, over the nineteen
citations pages: **994 citation notes, 259 absence notes and 2 grounds notes** (`m:citation-notes`,
`m:absence-notes`, `m:grounds-notes`).

Of those 259 absence notes, **119 say in so many words that no query of its own was run**
(`m:absence-notes-never-searched`), leaving 140 that record a real search. The 119 are 238's marker
conversions where the marker recorded no reason: the label moved to the assertion honestly, but no
hunt was ever made for it.

**This matters because it decides the feature's size**, and the two readings differ by a quarter. On
the narrow reading the work list is R1's 462 to 472 bare items and those 119 are done, because they
carry a footnote and the population the GM named was assertions that *"do not carry a footnote"*. On
the wider reading they are backlog: `research/CLAUDE.md` says an absence note *"re-opens on anything
that changes what can be read"*, and a note that was never searched has nothing to re-open FROM. The
spec takes the wider reading and records why, with the narrow one priced, as decision D1.

<!-- The census counts research/citations/*.html only. citations/<name>.js is DERIVED from the page by
     `make citations`, so a grep over both doubles every figure, which it did on the first attempt. -->

## R5 - what the capitals pass found WRONG, and corrected (2026-09-14, FR-006)

Eleven readers - ten over the 92 bare items and one over the page's 13 never-searched absence notes -
returned, and the page was footnoted from their quotes in eight batches. Where a reading showed the
record stated something wrong rather than merely unsupported, the sentence was rewritten to the finding
(nothing in the entry says what it used to say; this is where that is recorded). The corrections, by
the reader's item number (`measure/worklist.py cities/capitals.html` order at the time of reading):

- **8** - "`~67 km` of buried conduit in Edo, feeding over 3,600 draw-wells" was the KANDA system's conduit
  total alone; the Tamagawa adds `84.7 km`, and the one city-wide well count read runs to 8,000. The
  sentence now gives both lengths and "thousands of draw-wells".
- **14** - the Kaogongji's square capital was said to rest on "round heaven, square earth"; the one page
  read on exactly that question (the record's own `thepaper-city-walls`) says the attribution has no
  direct evidence and prefers constructional convenience. The heading and sentence now say so.
- **18** - "Europe cured the corner by CURVING"; the keep article calls the corner's weakness theoretical
  before the trebuchet and the crossbow and credits round plans to symbolism and earthworks. Restated.
- **27** - Pingyao "stands NEAR the Fen, not on it" - both encyclopedias put it on the Fen's east bank, and
  its south wall follows a river. The sentence and the paragraph's closing generalization were rewritten.
- **35** - the field gates ran "under the village's rotation of water rights": the JSIDRE paper says
  rotation is the DROUGHT regime and continuous supply the normal one. Restated, with the modern-practice
  limit disclosed in the registry.
- **48** - Hirosaki's tenshu "occupies `~0.6 ha`, about `1.2%` of the works": the park's own page gives a 5 by
  `6 ken` plan, about `0.01 ha` - a fraction of a percent. The `50 ha` was also identified as the park's figure
  (the original castle was `38.5 ha`).
- **77** - "Song cities ran mass cremation through a small number of Buddhist crematoria": the Song record
  as quoted by Wu Gou gives Southern Song Lin'an SEVERAL DOZEN, sixteen once demolished and fourteen
  restored by edict. The sublinear reading now rests on the Japanese case alone, and the sentence says the
  capital follows the Japanese form. **This is a two-forms question** (constitution XII): where the record
  supports both concentration and dispersal, the map owes a knob rather than a choice - engine work, and
  not this feature's (FR-014); it is named in the closing report for a successor beside the caravan inn.
- **N8** - "Pingyao's county yamen runs 300+ rooms": every source reached says over two hundred.
- **4, 5, 6, 7, 13** - five sentences carried quotation marks around words on no readable page ("larger
  compounds separated by walls and gates", "excavated without timbering", "six rooms and three shifts",
  the Marco Polo horses on the Shaoxing towpath, the drum-and-bell hours and the "40 lashes" framing of
  the Qing curfew). Each was restated without the quotation, from what the pages do say (the Great Qing
  Code's night-prohibition article, the estate walls of Edo's High City, the Tamagawa's open earth cut).
- **Unsupported clauses dropped or scoped**, each the reader found on no page: the Marco Polo horses and
  the towpath's "over `40 km`" (13; now the record's "close to a hundred li"); "the palace at the center"
  in the Kaogongji (14); "strictly rectangular" for every government compound (15); the bailey layouts
  "all polygonal-irregular" when the same article lists a circular type (16); the Grand Secretariat as a
  "council-of-state" when the article says it was never a first-rank organ (20); "rivers most commonly"
  and "wetlands" among moat sources, and Imabari's springs (21, 22); "small daimyo" for the whole residence
  table (23); "largest real main halls" for a ceiling the eighth-century Daibutsuden breaches (24); the
  towpath's `6.5 ft`, which was the pier span (25); "every example" of a boat-canal town (32); the "public"
  quay and a timber kashi (33); Kawagoe "never dug a canal into town" (34); the Song and Ming registered
  kiln households, "immediately beyond a gate" and "never scattered" (36); "a handful of muenbotoke sites"
  and "no great mound" (37); Yamatokoriyama's late-16th-century founding and the toponym "across Japan"
  (38); the weaving offices' "~7,000" (39); the Zuihoden "outside the town" (40); Liulichang as one of
  "five official kilns", "`~3 km`", "and temples" (41); Okawachiyama "`~6 km` up a valley" (42); Injō-ji "ON
  Hideyoshi's Odoi" and "explicitly described as the boundary" (43); Rendaino doing "all three jobs" (44);
  "in every attested case" (45); the flank-siting rule as a rule (47); the kumi-yashiki housing "the lowest
  samurai" when ashigaru stood below samurai status (52); Osaka and Nijo read as rectangles (57); the
  tulou as "emergency forms from the empire's margins" (58); "every side drain" bridged (60); "sluiced leats
  for supply and flushing" (66); a basin that "silts its mouth shut" (71); Varanasi's "`~100` pyres a day",
  which the weak pages put anywhere from 90 to 300 (81); the "gigawatt plume" and the fire FRONT framing
  (82); the louzeyuan "walled" when the page says fenced (83); "no jokamachi ever built" a continental
  avenue (86); the Kitsuki hills' "temples" (N4); Beijing's moats "fed by the Tonghui", which is the
  outfall (N10); Song wards surviving "only as name plaques" (N5).
- **Two figures left standing but labeled UNVERIFIED in the prose**, because the only numbers in
  circulation contradict them and no page could be read: the josui cut's `1-3 ken` (26) and the Shaoxing
  towpath deck's half-meter (55). Both are on the GM's download list.

**The three checks over the page** (quote-check, record-format, and source-applicability over the 112
new registry keys in four batches) were dispatched together after the eighth batch landed; their verdicts
and what they changed are R6.

## R6 - the checks' verdicts over the capitals page (2026-09-14)

- **quote-check** over the 72 new citation notes and 23 absence notes: 71 readable and one host unreachable
  (`qiaokou.gov.cn`, whose half of one note was dropped, the other source carrying the sentence); 61 quotations
  verbatim and ten differing from the page in small ways, every one brought to the page's wording (a dropped
  「（中略）」, a variant character quoted as the base text, a particle, a full-width comma, an omitted gloss); 0
  DOES-NOT-SUPPORT and 18 PARTIAL, of which ten were over-readings in the prose and were brought down to what the
  quotes carry (R5 lists them), the rest already disclosed in their notes' glosses; all 23 absence notes correctly
  formed. Five assertions it found carrying no footnote at all went to a twelfth reader; four now carry a citation
  and one an absence note, and one figure the reader found wrong ("four of them seating thousands" where the
  memoir says the largest one does) was corrected.
- **record-format** over the page, its notes and the 112 new registry entries: sixteen vocabulary terms added to the
  glossary; thirteen session tails (download-list pointers and "until X can be read") moved into HTML comments;
  HISTORY clauses ("which is why this page no longer says") removed from two notes and thirteen write-ups; three
  visible defects repaired (a literal backslash-n, a broken sentence tail, a duplicated anchor); the two rosters'
  session notes trimmed.
- **source-applicability** over the 112 keys in four batches: 0 NOT-APPLICABLE; `What it is:` inaccurate on three
  (the firebrand paper's authors and kind, the Kaifeng feature's section, the bansui article's authors and standing),
  all corrected; limits MISSING on 44 write-ups and now stated - the imperial- and shogunal-capital ceiling on the
  Beijing, Edo, Kaifeng and Hankou keys, the present-day regime behind the Yanagawa, Imabari, Pingyao and Hirosaki
  measurements, the same-datum and same-town pairs that do not corroborate one another, the encyclopedia's own
  sourcing notices, the self-media authorship of the Sina reposts.

## R7 - the urban-features pass (2026-09-14, FR-005 to FR-007)

- **Counts** (observed 2026-09-14; method: the worklist over the page, then the notes json applied): 87 bare items
  and 10 never-searched notes went to ten readers; 60 items now carry a citation from a page read, 21 an absence
  note, one a grounds note; the ten never-searched notes and nine older absence notes for which a citation was found
  were replaced in place. 73 registry entries were added. The session's web-search allowance ran out early in this
  pass, so the readers worked by fetching likely pages by address; every absence note says so, and 34 works that
  would settle the absences went on the GM's download list (entries 34 to 67).
- **Corrected in the prose** because a page contradicted it: rice's salt threshold (FAO 29: `3.0 dS/m` soil, `2.0`
  water, moderately sensitive - not the most sensitive cereal at `0.9`); the charcoal ratio (three to five to one by
  weight, not six); the ōkajiba's feed (pig iron decarburized to hōchō-tetsu, not low-carbon fractions to wari-tetsu);
  the fire tower's hansho carrying a time signal outside Edo; a well being diggable on high ground; Xingcheng's
  tower `21 m` square; the Kokuchō bell fee per ken of frontage rather than per house; kawaramono as a name given,
  not taken; the Danzaemon compound's four hundred as officials' families; Edo's outlying estates as daimyo villas;
  the kido as the town block's own gate; the horseshoe common in Yuan China.
- **Labeled as this page's reading** because no page read carries it: the kimon alignment of Edo's northern
  institutions, kilns pushed out by fire law, the siege-labor reason for an in-wall quarter, the kegare siting of
  the ground downwind and downstream, the courier hoof-wear rate, the one-flame-height rule, the ox's water and
  the trough dimensions, the caravanserai's single well as a choice, the brewer's rate per seat, the well counts
  per village and per block, the kabu-ido case as a peculiarity, the assembly place and shrine precinct for a
  village board, the hamlet's senior farmer as reader.

## R8 - the homesteads and water passes (2026-09-14, FR-005 to FR-007)

- **Counts** (observed 2026-09-14; method: the worklists and the notes json applied): homesteads 45 items and 8
  never-searched notes to six readers, 30 citations and 15 absence notes placed, 26 registry entries; water 42 items,
  13 never-searched notes and five table rows to six readers, 28 citations, 21 absence notes and one grounds note,
  24 registry entries. Both passes fetch-only; 25 further works on the download list (entries 68 to 92).
- **Corrected in the prose**: the hulling yield `80%`; 散村 as sanson; Osaki's igune heights; the Kaga tenure
  arrangement; the magariya's hearth-warmed stable; the privy from the floor-plan page itself; Himeji's moats by
  circuit and Osaka's `90 m`; the Isawa fan's `20,000 ha`; the Yodo's renaming at a border; the marsh belt's year;
  Beijing's moat inlet and outfall from the Chinese article.

## R9 - the fields, religion-and-death and archetypes passes (2026-09-14)

Eleven readers (fetch by address only; the search allowance stayed exhausted). Notes placed: fields 41 (26 citations, 15 absence; fn-92/93/96 replaced), religion-and-death 40 (fn-101 to fn-106 replaced), archetypes 28 (17 citations, 11 absence). New registry entries: 9 + 18 + 11.

Corrections the reading forced, page by page:

- fields: the alluvial-fan sentence had the landform backwards (a fan widens from its apex) and now speaks of the DRAWN fan; the terrace-bench economics contradicted the FAO page it cites (beds are made as wide as the slope allows to save labor); 1.3 koku/tan is the middle-grade kokumori, a tax rate; the 614 m2 mu is the 1915 law's Qing definition, not "Ming-Qing", and one mu is 0.15 acre at it (0.16 at the metric mu defined in 1930), not 0.17; the azemichi 2-5 ft against the one readable 300-600 mm crest; weeding "by hand and foot" reduced to hand and hand claw; the "shared water schedule" left as this page's reading against Obata's attribution to the preceding crop (and free valley water lengthening the window past twenty days); the "each family has some paddy and some hatake" quotation marks removed - the words are this page's.
- religion-and-death: Kyoto ~80 temples replaced by kotobank's Sakai (~60 + ~50) and Akita (43, 1663); the wenmiao decree is Tang (630) and the Ming act Taizu's enfeoffment of city gods; Sanuki's kokubunji precinct 240 x 220 m is the small end (Shimotsuke 457 x 413); Osaka's seven graveyards attest CONSOLIDATION onto the rim, not fragmentation, and nothing on pits; the clan mausoleum rewritten from Zuihoden's page (outside the castle, facing the keep) with the inside-the-walls placement labeled this project's; the temple-fair renting rests on a 1991 compilation, the gazetteers are Qing and Republican; "100 generations" to "scores"; "rice grows submerged" to "stands in water".
- archetypes: deep-water lotus is the page's "more than 40 cm" class (species to 2.5 m), the paddy's 5-9 cm optimum unread; hojo seibi's 30 a plot is 24 x 125 m, the 1963 and 30 x 100 m dropped; willow-fascine antiquity unread; the bare dike is the MODERN tell (concrete dropped); the "mosaic-like constructed ponds" quotation reduced to paraphrase; "coppice barely fruits" unread, the bush height from Morus (1.5-1.8 m); fry ponds corrected to the fry-fingerling-grow-out chain at 15-30 percent of pond area; the dike-width ceiling attributed to the FAO page's own pigsties, piping and traffic.

Tooling defects found by the homesteads/water record-format pass and fixed in `apply_notes.py`: a wrapped roster's first line was rewritten as a closed paragraph (five homesteads rosters restored from the pre-pass commit); a footnote mark landed inside a decimal figure (the terminator regex now refuses a period between digits); the registry key's address is the entry's first link, as the tests read it. The absence notes' `searched` field must not carry its own `searched YYYY-MM-DD:` prefix (41 doubled dates removed).

Download list: entries 93 to 140 appended for these three pages.

## R10 - the remaining nine pages (2026-09-14)

Two more waves of fetch-by-address readers (13 and 11 agents) closed the worklist: buildings 32 notes, vegetation 28, river-cities 24, defenses 22, towns 18, fabric 25, government 26, hinterland 11, ways 5. Every never-searched note on those pages was replaced in place. Registry entries added this stretch: about 120 (a census of `<h3 id=` additions since the homesteads/water commit gave 117 before towns and government).

What the reading contradicted, and what the pages now say:

- vegetation: neighboring canopies do NOT interlace (crown shyness), so the edge overlap is a drawing allowance; the Tonami homestead's bamboo stood on the SOUTH side with the storehouses; the pictorial hill is the oldest cartographic convention, not an estate-map one.
- river-cities: the takasebune runs 30 to 89 ft (a one-shot reading of the kotobank takasebune page, 2026-09-14) in the records read, not 50-60 ft.
- towns: the fire watch was the neighborhood's as much as the state's; the kichin-yado sold roof and fire, bedding rented extra; important cities walled in far more ground than they had built; farmland stood inside Chinese city walls.
- fabric: machiya touched at the gable, the shared wall proper being the nagaya's; the flood function belongs to the walls, not the intramural fields; the chapter's open consumers are cultivation, ponds and parks.
- government: the servants' changeover was the 5th of the 3rd month from the 1668 decree; the Chinese military examinations ran at provincial, metropolitan and palace level; the runners' banfang was a duty station, the shed and the town houses this page's reading.
- defenses: Hakone's stations are the menbansho and mukaibansho within a fence; the flat-face argument credits the spur's length and projection.

Tooling learned on these pages: a fragment of two words is tried (a parenthetical gloss closing a sentence); a registry address with balanced parentheses is read whole; a rewrite that spans a footnote mark keeps the mark (the matcher moves it to the end of the replacement); the tests want a Japanese or Chinese Wikipedia key's link in the unencoded kanji form when the registry has it so (toribeno, xian-wall, and the parenthesized 町屋 (商家)), which the apply tool cannot derive and the test reports.

Download list: entries 141 to 224 appended for these pages. Checks dispatched: quote-check over the twelve newly noted pages in four agents, record-format in four, source-applicability over the 117 new keys in five batches.

## R11 - handoff (2026-09-14)

The feature paused on the GM's instruction with the checks filed and unapplied; the state, the reports and the remaining work are in [`HANDOFF.md`](HANDOFF.md), with the thirteen check reports copied verbatim to `handoff/reports/`.
