# Feature 233 - the pig sty clear of the sluice, and the dike-pond stock recorded

**Created**: 2026-09-12
**Status**: Draft
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
so. Four of Kuwabata's seven sties stand 6-12 ft from a feed-sluice anchor on a stub only ~24 ft long,
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
   piping, or traffic should range from 5 to 10 m." Kuwabata's shared dikes measure 6.5 m, so the map
   already satisfies a rule it had never cited.
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

**FR-001** A pig sty's drawn footprint MUST NOT overlap a drawn pond sluice stub
(`dikepond_sluices[]`), and neither MUST a duck pen's dry run. This is a requirement about two glyphs
occupying one piece of ground, and it needs no historical number.

**FR-002** On top of FR-001 the fixture MUST stand clear of the sluice by a working margin - room for
a person to reach the gate and lift its boards, the sluice being "a protected opening in the pond dike
that can be easily closed with wooden boards". The margin is a GUESS (the record is silent on any
spacing along a dike; FAO gives dike WIDTH only) and is labeled one wherever it is stated.

**FR-003** A pond whose nearest bank seat is refused MUST NOT lose its fixture to another pond.
`_bank_seat` currently returns the single edge nearest the house cluster and `stage_pond_stock` skips
the whole pond when that seat fails, so adding a clearance would silently move sties between ponds and
could reduce their number. The seat selection MUST instead rank the parcel's edges by distance to the
house cluster and take the nearest one that fits.

**FR-004** The sty and pen counts on a given seed MUST NOT fall as a result of FR-001 to FR-003.
Measured on Kuwabata, a seat 30-45 ft clear of any sluice exists on all four affected ponds only 10-30
ft further from the houses than the seat now chosen, so the fixtures move a short distance rather than
disappearing.

**FR-005** The research record MUST carry findings 1 to 7 above, each as an assertion with a footnote
quoting the passage it rests on, linked to a public page where the quote can be read, on the citations
page beside the research page. The foreign-language passages are quoted in English translation, marked
as translations, with the original following as the anchor.

**FR-006** The inlet/outlet silence (finding 6) MUST be recorded as a labeled ABSENCE note - what was
searched, by whom, and when - carrying no key and no link, and MUST NOT be written as a finding.

**FR-007** The archetype entry MUST state that a penned pig on a pond dike is a Chinese form and that
the Japanese record does not carry it (finding 7).

**FR-008** The `PigSty` and `DuckPen` class entries in `interactive/classes/dikepond.py` MUST be
rewritten against the record as it stands after FR-005 to FR-007, since those docstrings ARE the
modal text every map with the feature shows. Their `Sources:` and `Entry:` tags MUST name the sections
and keys the new text was written from. This is what the GM asked for by "make sure that you update the
relevant HTML pages ... for any map with a pigsty feature".

**FR-009** Every new registry key MUST be judged by `source-applicability` before its numbers, claims
or details reach a map or a rule, and the changed entries MUST pass `quote-check` and `record-format`
before the feature lands.

**FR-010** Kuwabata MUST be regenerated and, its layout having moved, reviewed by `settlement-review`
paired with the gate.

## Success criteria

**SC-001** On Kuwabata, no `pig_sties[]` or `duck_pens[]` footprint overlaps a `dikepond_sluices[]`
stub, and every one stands at least the FR-002 margin clear of it.

**SC-002** Kuwabata still carries 7 sties and 2 duck pens.

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

## Out of scope

- The share of households keeping a sty stays a labeled GUESS; nothing read gives a premodern figure.
- The FAO ch. 7 direct-flow shed against the ch. 10 septic-tank shed is a candidate KNOB (two attested
  forms) and is NOT built here: ch. 10 reads as modern design guidance, and the question of whether it
  describes a premodern form wants `source-applicability` on its own. Noted in `research.md`.
- Pond area (0.27 ha drawn against the ISIS 0.4-0.6 ha band) is untouched; it is the hamlet tier's
  business and predates this feature.
- The guardrail that would have made FR-008 happen without the GM asking is feature 234.

## Review history

(to be filled by the `spec-fidelity` rounds)
