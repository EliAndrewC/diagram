# Feature 420: the goods-dollar koku on a sound index basis - what was bought, its modern match, the eras beyond rice, and which mean (diagram#17)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files here to be worked (his words, quoted above); a money research request gm-assistant
opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic
approval, and therefore you should not ask in the future"). The six questions are the GM's, asked through gm-assistant's
feature 223 (`request.md`, with his dictated words).

**Input**: `request.md` (the issue body, verbatim).

## Why

gm-assistant's goods-dollar koku prices the standard basket (Bassino and Ma's Japan basket A plus salt, fuel and a
back-tenement room, Kyoto 1745-54, diagram 0249) against a dated US retail snapshot. Its eleven single-good koku run from $36
(cloth) to $4,384 (housing). Part of that spread is real, and part may come from pricing unlike goods (organic soybeans and wheat
berries now against mass-market rice; cod fillets against whatever fish a Kyoto laborer ate) or unlike market levels (wholesale
then, retail now). The GM also asks what these baskets are used to compute in academic papers, and which mean to take.

## User Scenarios & Testing

1. **What was bought (Q1).** gm-assistant reads, for each basket good in Kyoto or Osaka about 1745 (and where it differs, in
   the other eras the record prices), its form and quality (fish: fresh, salted or dried, which species; soybeans: whole beans,
   or miso or tofu; barley and wheat: grain or flour; buckwheat and millets: grain or noodles; oil: rapeseed, sesame or fish;
   cloth: weave and width), and whether the price the record cites is wholesale or retail, with any attested retail markup per
   good.
2. **The modern match (Q2).** It reads, for each good, the modern US product that best matches Q1's form, with its price per
   the good's unit (kg, liter, meter, million BTU, m² a year) and a link: at retail (the cheapest plain household pack from a
   national retailer, about 2-25 lb, as gm-assistant's snapshot rule says) and, where the historical price is wholesale, at
   wholesale (USDA or a commodity price).
3. **Housing (Q3).** It reads any Kyoto or Osaka rent for about 1745 (or the nearest) with its room size, and the modern
   candidates for a laborer's tenement share per m² a year with links and what each measures: the average US asking rent, a
   low-income or rooming-house rent, a cost to build per m² (materials and labor, no land), and a world poverty line's housing
   allowance.
4. **The eras beyond rice (Q4).** It reads, for each of the 23 eras gm-assistant holds (Japan first, 1620-1882; China beside
   it), which of soybeans, fish, cloth, salt, fuel and housing can be priced from an observed price rather than a
   reconstruction, with new silver prices in 0286's format (grams of pure silver a unit, its label, its source); and per era,
   which goods are observed and which reconstructed or borrowed.
5. **Which mean, and rice as numeraire (Q5).** It reads what economic historians do when a historical sum is put into modern
   money with a basket and relative prices have moved by two orders of magnitude (Laspeyres, Paasche, Fisher, a geometric mean
   such as Jevons or Tornqvist, or a range); how named works put a basket into modern money (Allen 2017, "Absolute poverty: when
   necessity displaces desire"; Moatsos's basic-needs lines; MeasuringWorth's real price against labor value), each with its
   method cited; whether a range or one figure is the norm; what such baskets are used to compute in those papers (the GM's
   question); and whether expressing each era's prices in rice is an accepted way to compare across debasements, or whether
   rice's own harvest swing makes it unsound over a multi-year era.
6. **Modern quantities (Q6).** It reads, for each basket good, what a US adult consumes in a year (rice, soybeans as food,
   wheat, other grains, dry beans, fish, cooking oil, cloth or textiles in m², salt, home heating and cooking fuel in million
   BTU, housing m² a person), each with its source (USDA ERS food availability, EIA RECS, Census AHS, or what the search finds).

**Acceptance**:
1. Every figure each question names gets a verdict - ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT -
   SILENT with its search; a reconstruction is never written as an observation, and each era's observed-or-reconstructed list
   says which source each observed price comes from.
2. Q1's market level is stated per good from the source of the price the record cites (Mitsui's purchase books, a market floor,
   a shop); a markup is given only where a source states one.
3. Q2 and Q3's modern prices are each a dated observation with its link, archived, labeled with the date seen; a retail price
   follows the snapshot rule as the request states it; where no matching product is found, the nearest is given with what
   differs.
4. Q4's new prices are in 0286's format; a price already in the record is pointed to, not copied.
5. Q5 states each work's method in its own words (quoted), says which works give a range and which one figure, and answers the
   rice-as-numeraire question from what the sources say about it, or SILENT; any rule this project draws from them is labeled
   its own derivation.
6. Each answer says how it stands against the canon the request names: gm-assistant's 2026-10 snapshot (never edited here; a
   finding that would change a modern price is reported for a new snapshot) and the reading's eleven-good table.

## Requirements

- **FR-001**: The historical findings (Q1, Q3's historical rent, Q4) are written in the "Money and prices" section under the
  citation rules: Q1 in 0249 (the Kyoto laborer's year of goods, the basket's page) and its sibling pages where a good has one
  (0261 cloth, 0273 salt, 0279 charcoal); Q3's rent in 0265 (rents); Q4 in a new question per country beside 0286 and 0288 (both
  near the size cap), each with its per-era observed-or-reconstructed table.
- **FR-002**: The modern findings (Q2, Q3's modern candidates, Q6) and the method (Q5) are written in the "Comparative money:
  other societies" section, their sources of the kind `comparative` (research/CLAUDE.md, "Comparative money sources": the GM
  asks for them here), each page saying it never sets a Rokugani price; a scholarly source on index-number method that is not a
  source on another society's money is tagged by what it is, and the section's rules decide where it is cited.
- **FR-003**: The work runs in page sessions of at most four questions and ten new registry keys a write, each followed by a
  check session (`make page-session`); search passes (`research-pass`) run first, one per question or group.
- **FR-004**: The reply on #17 gives, per question, each figure with its fragment file and verdict, what is still open (sources
  for `research/to-download.md`, passes not run, figures no source gives), and how to verify the landing; findings that bear on
  the GM's canon go through `escalation-check` first.
- **FR-005**: The feature closes with `make impl-check F=420` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001-FR-003, FR-005): `make record CHECK=1` passes, `make record-owed` shows no unanswered unit for the touched
  questions and sources at landing, and `make impl-check F=420` reports nothing missing.
- **SC-002** (FR-004, Acceptance 1-6): a reply on #17 answers each of Q1-Q6 with every figure it names, or that figure's SILENT.

## Out of scope

- Computing the koku's dollar value, a headline or a range: that is gm-assistant's toolkit's (`/money/koku`); this feature
  supplies the research it reads.
- Editing gm-assistant's snapshot or canon.

## Assumptions

- Q4's "23 eras" are the eras in `research/assets/money-conversions.json` (15 Japanese, 8 Chinese); a good already priced in
  the record for an era (0261, 0265, 0273, 0279, 0286, 0288) counts as observed if its record entry is.
- Five or six write sessions: Q1 with Q3's rent; Q4 Japan; Q4 China; Q2 with Q3's modern candidates and Q6; Q5.
