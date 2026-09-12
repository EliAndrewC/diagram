# Feature 233 - the pig sty clear of the sluice, and the dike-pond stock recorded

**Created**: 2026-09-12
**Status**: ACCEPTED 2026-09-12 after four rounds of `spec-fidelity`; AMENDED after implementation and re-reviewed (see Review history)
**Input**: the GM's two messages, verbatim, in `request.md`

## Summary

The GM, reading Kuwabata, asked whether a pig sty would stand as close to a pond sluice as the map
draws it, and whether the runoff harms the fish in a pond cultivated for fishing.

The research pass answers the water question and refuses the premise behind it. A pig shed on a
fish-pond dike is the arrangement the dike-pond loop exists to make: the manure is the pond's feed.
What the record does NOT answer, in anything two independent readers could reach, is where on the
dike the shed stands relative to the pond's inlet or outlet - the question the GM actually asked is
met by a silence.

So this feature changes the map for a reason that is constructional rather than sanitary, and it says
so. Four of Kuwabata's seven sties stand 5.6 to 11.7 ft from a feed-sluice anchor on stubs of 23.9, 25.0, 25.2 and 27.9 ft,
so an 8 x 6 ft shed is drawn across the inlet culvert. The cause is a gap in the placer, not a roll:
`pond_fixture_fits` holds a sty off `houses`, `farm_sheds`, `byres`, `wells`, `kosatsuba`,
`footbridges`, `pig_sties` and `duck_pens`, and off nothing in the water system - while the engine's
own dike-top house placer already skips a site within `gap_clear` of a cut, commented "never build
over a sluice notch". The pond-stock placer never got that rule.

Everything else the readers returned is recorded, because the record is the deliverable as much as
the map is: the loading figures, the dike-width rule, the sixth-century treatise, and the silence.

## What the research found

Dispatched as two `source-reader` agents, 2026-09-12. Full verdict tables live in `research.md`.

1. **The sty is on the dike so the manure reaches the water.** FAO/NACA, *Integrated Fish Farming in
   China*, ch. 9: "Pigsties are usually built on the pond dike of an integrated fish farm so that the
   pig excrement can be directly flushed into the pond." Ch. 7 attaches a pond-size condition Kuwabata
   satisfies: "If the area of a fish pond is less than 8 mu, a pigsty can be set up on the pond dyke
   and pig wastes will flow directly into the pond." Kuwabata's ponds measure 4.0 mu (median drawn
   water area, 0.27 ha).
2. **The mechanism is feed, not pollution.** The same report: manure "fertilizes the water, producing
   plankton which is a good natural fish food"; the FAO primer gives the three pathways
   (phytoplankton, detritus/bacteria, zooplankton).
3. **The oldest siting instruction runs the other way.** 齊民要術 (Qimin Yaoshu, c. 540 AD), 養豬第五十八:
   「圈不厭小。〈圈小則肥疾。〉處不厭穢。〈泥污得避暑。〉」 - "The pen is not disliked for being small - a small pen makes
   them fatten fast. The place is not disliked for being filthy - mud and muck let them escape the
   heat." (translated from the Chinese by this project; the original is kept as the checker's anchor.)
   It is the only siting instruction the pig chapter gives, and nothing in it concerns water.
4. **The hazard is a rate and a concentration, never a distance.** FAO ch. 7: "Fish surfacing
   increases (dissolved oxygen content decreases) when pig manure sinks to the bottom of the pond or
   when too much manure flows into the pond." The handles are quantities and dates: more than 30 pigs
   is too much for direct flow; 20-40 kg/mu/day; 100-150 m3 of pond per pig; no manuring after
   mid-October. The one source that speaks to WHERE the manure enters - FAO's consultancy report on
   the Chinese lead centre - keeps the shed on the dike and moves the MANURE: "manure distribution
   techniques generally need to be employed to avoid the development of anaerobic conditions in the
   pond adjacent to the livestock quarters", by bucket, channel or sprinkler.
5. **A dike carrying a pigsty is wider.** FAO ch. 10: "the width of the dikes between fish ponds and
   inflow and outflow canals should be kept within 5 m; the width of the dikes for pigsties, cow sheds
   piping, or traffic should range from 5 to 10 m." Measured against the drawing the map does NOT satisfy
   it - the collar a sty stands on is 2 to 5 m - and the record says so (see the post-acceptance amendment entry in the Review history, and `research.md` R1).
6. **THE SILENCE.** Four FAO manuals, the ISIS dike-pond summary, and the Chinese and Japanese
   material carry nothing relating a shed's or a pen's position on the dike to the pond's inlet,
   outlet, sluice or drainage gate - for it or against it. Two readers searched independently and both
   returned NOT-FOUND.
7. **A penned pig on a pond dike is a CHINESE form.** Hudson and Munoz Fernandez (*Asian Archaeology*,
   2023) name "Buddhism suppressed pig-keeping in Japan" as the assumption they are writing against;
   pork consumption did decline from the mid-first millennium AD, Okinawa is the stated exception, and
   where mainland pigs were kept the reading is pannage - loose in forest - rather than a village pen.
   Nothing read links a Japanese pig to a pond. Kuwabata is the Chinese-derived dike-pond archetype by
   construction, so the sty stands; the record should say that plainly instead of leaving it implicit.

## Functional requirements

**FR-001** No drawn part of a pig sty or a duck pen MUST overlap a drawn pond sluice stub
(`dikepond_sluices[]`). For a duck pen that means the dry run on the bank **and its FENCE ARC** - the open
six-point polyline `duck_pens[].wet`, which is a fence and not a closed region. That exact phrase is
used in FR-002 and SC-001 too: on today's map "the arc" and "the water it encloses" give the same
answer, but on a re-rolled seed a stub ending inside the fenced corner without crossing the fence is an
overlap under one reading and clear under the other. This is a requirement about two glyphs
occupying one piece of ground, and it needs no historical number.

The wet run is named explicitly because it is the worst offender on the shipped map and the easiest to
overlook: duck pen 1 stands 2.3 ft from a feed stub by its dry run, and its fence arc **CROSSES that stub**, at
(2404.8, 796.5) - clearance 0 ft, an overlap rather than a narrow gap. A fence across your own intake is
not a thing anyone builds, and nothing about the dike-pond loop excuses it.

**FR-002** On top of FR-001 the fixture MUST stand clear of the sluice stub by a working margin of
**6 ft**, measured from EVERY drawn part of the fixture - a sty's footprint, a pen's dry run and its
fence arc (the open polyline `duck_pens[].wet`) alike - to the nearest point of the stub (a segment, not its anchor: a stub runs 19 to 41 ft, median 26.5, and the
anchor alone understates the overlap badly, as `research.md` R1 now records). The reason is that
someone has to stand at the gate and lift its boards, the sluice being "a protected opening in the pond
dike that can be easily closed with wooden boards to regulate water level"; 6 ft is about two paces,
room for one person and the board they are drawing.

The 6 ft is a **GUESS**. The record was searched by two readers and is silent on any spacing along a
dike - FAO gives dike WIDTH only (finding 5) - so this is a degree along a continuum with nothing to
measure it against, not a choice between two attested forms, and therefore not a knob. It MUST be
labeled a guess in all three places it appears: the research entry (FR-005), the point of change in
`pondstock.py` / `farm_fixtures.py`, and the `PigSty` and `DuckPen` class entries (FR-008).

The value is chosen on its own merits and not against a placement budget, because there is no budget
pressure: `research.md` R6 simulated the rule at 0, 4, 6, 8 and 12 ft and every fixture places at every
one of them.

**FR-003** A pond whose nearest bank seat is refused MUST NOT lose its fixture to another pond.
`_bank_seat` currently returns the single edge nearest the house cluster and `stage_pond_stock` skips
the whole pond when that seat fails, so adding a clearance would silently move sties between ponds and
could reduce their number. The seat selection MUST instead rank the parcel's edges by distance to the
house cluster and take the nearest one that fits.

**FR-012** (added after acceptance) A candidate seat MUST be refused if it is further from the house
cluster than its pond's own center. Ranking alone (FR-003) leaves the accept set the WHOLE pond
perimeter: on the nine ponds that carry a fixture, the far bank runs 155.6 to 320.0 ft further from the houses than the first choice, a shed there would read as belonging to no household, and neither the placer nor the gate would say so. The bound is GEOMETRIC rather than a tuned distance - no number to
justify and none to drift - and it keeps a fixture on the side of the water its households are on.

It may refuse seats, so FR-004 and SC-002 bound it in turn. Measured on the reference map: the accepted seats cost +0 to +21.2 ft over the first choice, the bound's own allowance runs 60.5 to 157.2 ft per pond, and the TIGHTEST accepted seat sits 57.3 ft inside it - so it refuses nothing drawn today and the manifest is byte-identical with it in place.

**FR-004** The sty and pen counts on a given seed MUST NOT fall as a result of FR-001, FR-002, FR-003 or FR-012. (FR-012 was added after acceptance and this range was hand-enumerated before it existed; a refusal the counts requirement does not cover is exactly the failure FR-003 was written to prevent.)
Simulated on Kuwabata with the wet run included in the clearance (`research.md` R6): 7/7 sties and 2/2
pens place at every margin from 0 to 12 ft, the worst achieved clearance at 6 ft being 8.5 ft. The
fixtures move a short distance rather than disappearing, and the wet run costs nothing.

**FR-005** The research record MUST carry findings 1 to 7 above, each as an assertion with a footnote
quoting the passage it rests on, linked to a public page where the quote can be read, the notes living
on `research/citations/archetypes.html` beside the page. The foreign-language passages (finding 3's
齊民要術, and any Japanese passage) are quoted in English translation, marked as translations, with the
original following as the checker's anchor. Where finding 1's pond figure (4.0 mu / 0.27 ha) is written
on a reader-facing page it MUST carry its honest limit - the same ponds sit below the ISIS 0.4-0.6 ha
band - the obligation being repeated here from "Out of scope" because this is the requirement whose
implementer actually writes that number down.

They land on **`research/archetypes.html`**, the one page in the record covering this archetype and the
page `PigSty.Entry:` already names. Findings 1, 2, 5 and 7 extend the EXISTING section 'What stands on a
dike-pond hamlet that a paddy hamlet lacks?' (see FR-011, which that section needs anyway). Findings 3,
4 and 6 - the treatise, the hazard, and the silence - open a NEW section, because they answer a question
that section does not ask. Its heading MUST be phrased as the question a reader would ask standing at
the map, which the GM's own wording nearly supplies:

> Does a pig sty have to stand back from the water, or from the pond's sluice?

Its anchor is derived from that text by `interactive/sources.py` `github_anchor` and is STABLE from the
moment it lands - a later rename owes its inbound links, which after FR-008 include the `Entry:` tags of
`PigSty` and `DuckPen`.

**FR-006** The inlet/outlet silence (finding 6) MUST be recorded as a labeled ABSENCE note - what was
searched, by whom, and when - carrying no key and no link, and MUST NOT be written as a finding.

**FR-007** The archetype entry MUST state that a penned pig on a pond dike is a Chinese form and that
the Japanese record does not carry it (finding 7).

**FR-008** The `PigSty` and `DuckPen` class entries in `interactive/classes/dikepond.py` MUST be
rewritten against the record as it stands after FR-005 to FR-007, since those docstrings ARE the
modal text every map with the feature shows. Their `Sources:` and `Entry:` tags MUST name the sections
and keys the new text was written from. This is what the GM asked for by "make sure that you update the
relevant HTML pages ... for any map with a pigsty feature".

Neither entry MAY offer a water-quality reason for the fixture's position (D2). The clearance is
constructional; saying otherwise would assert a finding the record does not carry, and finding 6 is a
silence. This clause is repeated from D2 deliberately, because FR-008 is the requirement whose
implementer actually writes that prose.

**FR-011** The existing section 'What stands on a dike-pond hamlet that a paddy hamlet lacks?' MUST be
brought into agreement with what the map draws. Its "Pigs and ducks ON the pond dikes" item currently
ends *"A pig sty on a pond dike and a duck pen at a pond corner are both attested forms, then, though
how common they were before the modern period is unquantified; neither is drawn."* followed by an HTML
comment marking both as a CANDIDATE awaiting "the GM's call". Both ARE drawn - the GM called it in
feature 150 - and `PigSty.Entry:` sends the reader of every sty modal to that sentence. The stale clause
and the resolved CANDIDATE comment MUST go, and the section MUST say what the map now does. The
unquantified-prevalence half stays true and stays.

This is inside the GM's *"make sure that you update the relevant HTML pages"*, and it is the defect this
feature found while doing something else (Principle XIV).

**FR-009** Every new registry key MUST be judged by `source-applicability` before its numbers, claims
or details reach a map or a rule, and the changed entries MUST pass `quote-check` and `record-format`
before the feature lands.

**FR-010** Kuwabata MUST be regenerated and, its layout having moved, reviewed by `settlement-review`
paired with the gate.

## Success criteria

**SC-001** On Kuwabata, no drawn part of any `pig_sties[]` or `duck_pens[]` record - a sty's footprint,
a pen's dry run, a pen's fence arc (the open polyline `duck_pens[].wet`) - overlaps a
`dikepond_sluices[]` stub, and every one of those parts stands at least the FR-002 margin clear of the
nearest stub SEGMENT.

Measured as shipped with an intersection-aware distance, the criterion is not vacuous and the true state
is worse than a gap: on ponds 5, 12 and 24 a feed stub passes THROUGH the sty's footprint (clearance
0 ft; the chord lying inside the shed is 3.62, 2.56 and 0.06 ft), and duck pen 1's fence arc crosses its
feed stub. Three sheds have a culvert running through them and one fence is drawn across an inlet.

**SC-002** Kuwabata still carries 7 sties and 2 duck pens.

**SC-006** The distance used to verify SC-001, and ANY clearance predicate shipped in the placer,
returns 0 when a stub intersects a drawn part or lies wholly inside one - proven by a case with a stub
driven through a footprint, a case with a stub wholly inside one, and an open polyline that is not
silently closed into a region. This criterion exists because this feature's own acceptance numbers were
twice produced by a measure that could NOT return zero (`research.md` R1); without it, SC-001 could be
verified by that same measure a third time, in the test meant to prove it.

**SC-003** A test proves FR-001 fires: with the clearance removed, it goes red.

**SC-004** `quote-check` reports every changed assertion carrying a footnote that is verbatim on its
page, readable there, and supporting; `record-format` reports no session note, no history and no
undefined vocabulary in the changed entries; `source-applicability` returns a verdict for every new key.

**SC-005** `make done` green, `settlement-review` returned on the regenerated map.

## Decisions recorded

**D1 - the sty stays at the water's edge.** ACCURATE. The manure reaching the pond is the design
(finding 1, 2). The GM's opening premise - that the sty should be held away from the water to stop
contamination - is declined on the record, not on preference.

**D2 - the clearance is constructional, not sanitary.** MAP DRAWING CONVENTION for the no-overlap half
(FR-001: two glyphs, one piece of ground), GUESS for the working margin (FR-002). The modal must not
tell a reader the shed was moved for water quality - nothing read supports that, and finding 6 is a
silence.

**D3 - the anaerobic patch is not drawn.** ACCEPTED LIMITATION. The one real place-dependent hazard in
the record is a dead patch in the water below the shed, managed by spreading the manure with buckets,
channels or sprinklers (finding 4). Alternatives priced and DECLINED: (a) a tinted patch in the pond
under each sty - rejected, it would assert a condition no source ties to a premodern pond and would
read as a drawn feature; (b) a distribution channel glyph on the dike - rejected, the report describes
it as remediation on 1980s farms, not as a thing a premodern dike carried. The map draws neither and
the record says why.

**D4 - no setback from the inlet.** The obvious inference - that incoming water at a feed sluice would
disperse the manure, making the inlet the BEST seat - is the session's reasoning and not the record's.
It is NOT recorded as a finding and NOT used to justify a placement.

**D5 - the sties are not removed from the map.** The Japanese record does not carry a penned pig
(finding 7), but Kuwabata is the Chinese dike-pond archetype by its own construction. Alternative
priced and DECLINED: dropping pond stock from the archetype - rejected, it would throw away an
attested feature of the system the map is modeled on. The record states the provenance instead
(FR-007).

**D6 - the drawn collar does NOT meet the modern floor, and that is ACCEPTED.** The dike-width rule
(finding 5) asks 5 to 10 m of a dike carrying a pigsty. Measured on the map, the collar a sty stands on
is 2.0 m median and 2.6-4.7 m under the sheds; the ground between one pond's water and the next is
13.3 m, but a canal runs down the middle of it, so it is not one bank. The drawn collar is therefore
SNUG by that standard, and the map is not changed to meet it.

*Why it is accepted.* That figure is a design requirement for farms built in the 1980s, not a
measurement of any premodern dike, and nothing read gives the width of an old one - so there is no
historical number the map is failing, only a modern one it was never built to. *Alternative priced and
DECLINED*: widening the collars, which means moving pond geometry on a shipped map to satisfy a
requirement whose own source we have already discounted as modern. *What it costs*: a reader who
measures the collar against the FAO band finds it short, so the record says so before they do.

*How this became a decision*: the spec previously claimed the opposite - that the map "already satisfies
a rule it had never cited" - on arithmetic that measured nothing. `settlement-review` caught it.

**D7 - the seat bound is a LEGIBILITY judgment, not a research finding.** FR-012 refuses a seat past the
pond's center because a shed on the far bank reads as belonging to no household. Nothing in the record
says where on a pond's perimeter a shed stood; this is a judgment about what the map communicates, and
it is labeled as one rather than dressed as history. No research pass is owed for it.

## Out of scope

- The share of households keeping a sty stays a labeled GUESS; nothing read gives a premodern figure.
- The FAO ch. 7 direct-flow shed against the ch. 10 septic-tank shed is a candidate KNOB (two attested
  forms) and is NOT built here: ch. 10 reads as modern design guidance, and the question of whether it
  describes a premodern form wants `source-applicability` on its own. Noted in `research.md`.
- Pond area is untouched as a DRAWN quantity; it is the hamlet tier's business and predates this
  feature. But finding 1 rests on the drawn ponds measuring 4.0 mu to satisfy FAO's "less than 8 mu"
  condition, and the same ponds sit below the ISIS 0.4-0.6 ha band at 0.27 ha. Where that figure reaches
  a reader-facing page it MUST carry that limit; a number may be out of scope to CHANGE and still be in
  scope to state honestly.
- The guardrail that would have made FR-008 happen without the GM asking is feature 234.

## Review history

**AMENDED AFTER ACCEPTANCE, 2026-09-12** (the counter resets to zero for a post-acceptance amendment,
GM 2026-09-12). The feature was implemented, and `settlement-review` returned **PASS** on the
regenerated map - 7 sties and 2 pens held, minimum clearance over every drawn part 0.0 -> 8.47 ft, and
the five fixtures that moved ended up NEARER the water rather than further from it. It found both of its
errors in the record rather than the drawing, and both are taken:
(1) Finding 5 was wrong. "Kuwabata's shared dikes measure 6.5 m, so the map already satisfies a rule it
had never cited" rested on arithmetic that measured nothing - one pond's two opposite collars summed, a
strip that exists nowhere on the map. Re-derived independently: the collar is 2.0 m median, the sheds sit
in 2.6-4.7 m, and the water-to-water ground is 13.3 m with a canal in it. The map does NOT meet the
modern 5 m floor; finding 5, the research page and the new D6 all say so now. The error flattered, which
is why it is recorded rather than quietly corrected.
(2) `kuwabata.notes.md` carried no entry for a change that moved five of nine fixtures, while five
features that changed nothing on the map each had one. It has one now.
Its questionable finding is taken as FR-012 and D7: ranking the seats had left the accept set the whole
perimeter, so the accept is bounded to the near half of the pond.

**Amendment round 2** (`spec-fidelity`, 2026-09-12): CHANGES REQUIRED, three items, all taken.
(1) FR-012's justifying figures were per-case numbers stated as bounds and one was simply wrong - "up
to 288 ft" is pond 20's own spread where the true maximum is 320.0 ft on pond 24, and "a limit of about
+70" described three of nine ponds. Re-derived from the manifest before rewriting: far bank 155.6 to
320.0 ft over the first choice, the bound's allowance 60.5 to 157.2 ft per pond, accepted seats +0 to
+21.2 ft, tightest slack 57.3 ft. All four places that carried the wrong figures now carry these and
point at the new `research.md` R7 - which also records that this was the THIRD time a figure was written
where its method did not travel with it.
(2) FR-004 read "as a result of FR-001 to FR-003", a range hand-enumerated before FR-012 existed, while
FR-012 claimed FR-004 bounded it - so on a re-rolled seed the new refusal could drop a fixture with no
requirement forbidding it. FR-004 names FR-012 now.
(3) Two British spellings in the map's notes prose, which the house-style rule covers.

**Confirming round** (`spec-fidelity`, 2026-09-12) on the amended text: CHANGES REQUIRED, four items,
all taken - the shipped bound was specified nowhere and FR-003 read as contradicted by the code (now
FR-012, with its class in D7); this amendment entry did not exist and finding 5 pointed a reader at a
round that said nothing about dike width; the 5 m non-compliance was asserted with no
accepted-limitation entry (now D6); and the Summary still gave one pond's 23.9 ft stub as if it
described all four - the same per-case-as-statistic fault an earlier round had corrected one file over.
Also taken: a `centre` identifier in the new gate test, which the house-style rule covers.

**Round 4** (`spec-fidelity`, 2026-09-12): every corrected number verified INDEPENDENTLY - the reviewer
built its own geometry rather than reusing `measure_geom.py` and reproduced all four zeros, the three
chords, the crossing point and the seven larger clearances exactly. Four items, all taken, and all of
them one fault in new places: a measured figure written into the record without the method that produced
it travelling alongside.
(1) `research.md` stated a MUST on this feature's shipped code - that any distance must return 0 on
intersection and be selftested - and NO requirement or criterion carried it, so it bound nothing. That
is now SC-006, which exists precisely because this feature's acceptance numbers were twice produced by a
measure that could not return zero; without it SC-001 could be verified by that measure a third time, in
the test meant to prove it.
(2) `measure_geom.py` was committed as the record of how this was measured and contained no selftest -
three places asserted one. It carries the asserts now and runs them as `__main__`. (The reviewer
confirmed the function itself is sound: 300,000 random trials against shapely, max error 1.1e-14, zero
disagreements on the zero/nonzero verdict, containment and the open-polyline case both correct.)
(3) R6's first table and its analysis read as live while standing above the block that corrects them,
and the round-2 history entry still called the superseded figures "the true clearances". Both marked.
(4) "~24 ft" was never a statistic of the artifact: over 52 stubs the median is 26.5 and the mean 28.0;
23.9 is the pond-5 stub, the motivating case. Stated as measured wherever it is quoted.
**Status: accepted.** No persistent misunderstanding; the reviewer explicitly would not escalate.

**Round 3** (`spec-fidelity`, 2026-09-12): verdict CHANGES REQUIRED, two items, both taken; round 2's
fix confirmed carried into all three places with no fourth place disagreeing, and the scope re-walked
clause by clause against the request with no accretion found.
(1) **The clearances the spec quoted were wrong, and wrong in the direction that made the map look
better than it is.** The session's measure sampled each footprint's boundary at 8 points per edge and
took the nearest sample, with NO segment-intersection test - so an actual overlap was reported as a
sub-foot gap. The reviewer reproduced those exact figures from that method, which is how the method was
identified. True state: ponds 5, 12 and 24 have a feed stub passing through the sty footprint and duck
pen 1's fence arc crosses its stub - four clearances of 0, not 0.13 / 0.03 / 0.08 / 0.19. FR-001 had
been asserting a positive clearance and a crossing in the same sentence. All figures replaced from a
run whose distance returns 0 on intersection and which is selftested against a stub driven through a
rect; `research.md` R6 re-run on the corrected measure, and its placement result is UNCHANGED (7/7
sties, 2/2 pens at every margin, 8.5 ft worst at 6 ft), which is what the reviewer predicted, the old
approximation having erred toward accepting.
(2) FR-001 called the wet run "the fenced arc" while SC-001 called it "a pen's `wet` polygon", and
`duck_pens[].wet` is an OPEN polyline - two readings that agree on today's map and diverge on a
re-rolled seed where a stub ends inside the fenced corner without crossing the fence. One phrase now,
used in all three places.
The reviewer independently re-verified the pond area (4.03 mu / 0.269 ha), the dike width (6.52 m), the
`fao-x6708e` sluice quotation behind FR-002's reason, FR-005's anchor, FR-011's stale sentence, and that
the wet arc is reproducible from a candidate seat - confirming FR-003 is implementable.

**Round 2** (`spec-fidelity`, 2026-09-12): verdict CHANGES REQUIRED, one item, taken. FR-001 covered a
duck pen's DRY RUN only, while FR-002 and SC-001 said "the fixture" and "footprint" without qualifying
which part - and `duck_pens[]` carries two drawn parts. The reviewer measured what that ambiguity hides:
duck pen 1's wet fence stands 0.19 ft from a feed stub against its dry run's 2.3 ft, so the map's worst
duck-pen offender was the part FR-001 excluded, and the two readings of the spec produce different maps
on this seed. Resolved by INCLUDING the wet run rather than documenting its exclusion: a fence across
one's own intake is indefensible, and R6 re-simulated with the wet run shows it costs nothing (7/7 and
2/2 at every margin, 8.5 ft worst at 6 ft). The reviewer's aside on the pond-area figure is also taken -
the obligation now sits inside FR-005 as well as under "Out of scope", where an implementer would not
have looked for it. Its second aside corrected `research.md` R1: the 6/7/8/12 ft figures there were
ANCHOR distances and read as more comfortable than the map is; R1 now leads with the true
footprint-to-segment clearances (0.13, 0.03, 0.08, 3.04 ft) - figures ROUND 3 then showed to be wrong
in their turn: three of those four are 0. See the round-3 entry below.
The reviewer independently re-verified round 1's three fixes, the 6 ft against R6, and FR-011's quoted
passage against `archetypes.html:141`.

**Round 1** (`spec-fidelity`, 2026-09-12): verdict CHANGES REQUIRED, three of them, all taken.
(1) FR-002 required a margin the spec never stated, making SC-001 unverifiable - the value is now 6 ft
with its reason, its GUESS label and the three places it is stated. (2) FR-005 said only "the citations
page beside the research page" - it now names `research/archetypes.html`, which findings extend the
existing section, which open a new one, and the new heading's text. (3) The reviewer found, outside
anything the session had looked at, that the section `PigSty.Entry:` points at ENDS with "neither is
drawn" and an unresolved CANDIDATE comment, while the map has drawn both since feature 150 - the record
contradicts the map on the very sentence the modal cites. That is now FR-011.
Both asides also taken: D2's prohibition is repeated into FR-008 where the prose is written, and the
pond-area figure must carry its honest limit wherever it reaches a reader.
The reviewer independently verified the spec's measurements against the manifest and the engine
(sty-to-sluice 5.6 / 6.8 / 8.0 / 11.7 ft, the eight registries `pond_fixture_fits` iterates,
`dikes.py:304-305`'s sluice-notch skip, Kuwabata as the only map with sties).
