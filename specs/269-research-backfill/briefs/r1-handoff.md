# 269 R1 handoff - religion-and-death: burial (B36)

- SECTION=religion-and-death/160
- SECTION=religion-and-death/170
- SECTION=religion-and-death/180
- SECTION=religion-and-death/206
- SECTION=religion-and-death/270
- SECTION=religion-and-death/280
- KEY=meiji-1884-bochi-saimoku
- KEY=isesaki-bochi-kijun
- KEY=kawazoe-2010-ryobosei
- KEY=kimura-1934-bochi-menseki
- KEY=kaf2-kinsei-bo
- KEY=takeuchi-2017-bochi-hosei
- KEY=buck-1930-farm-economy (existing entry; limits and "Used for" extended to the grave figures)

B36 CONTRADICTION-RESOLVED (size) + ACCURATE (distance and side) + KNOB (temple yard or a ground apart) - The record now cites the readable 1930 Buck survey in place of the unread 1937 one: graves on 2.6% of the farm land of five level-land localities, up to 9.1% on the most fertile, standing anywhere in a field (160). The 0.15-0.30 acre village band is checked against a 1934 Japanese cemetery-planning rule for cremating cities, which gives one 1-tsubo family plot per household times 1.5-2 for paths. For ~160 households that is about 0.20-0.26 acre, inside the band. The ladder stays this project's own arithmetic (206). A 22-village survey measures visiting graves at ~130 m (82% within 200 m) from the houses and burial grounds at ~370 m (up to ~900 m), always on the downstream side, never above the houses (270). The 1884 siting rule says away from great rivers, on high, dry ground, clear of drinking water, and at least ~60 ken from houses. The Song paupers' grounds were on high, open, barren ground. The only numeric set-back from water is modern: 20 m from a river or lake (Isesaki). So 180's distances are now explicitly labeled a guess, well beyond that floor (180). Temple graveyards, settlement common grounds and individual or lineage graves all stood side by side at the end of Edo, and how common each was is unknown (280). - What the generator should draw differently:
  1. **The knob (280, and 170's village clause, rewritten to match):** each village's seed chooses whether its one burial ground lies in the shrine's yard (today's churchyard rule, within ~500 ft of the hall) or as a ground of its own apart from the shrine, at even odds (the odds are a guess). A hilltop shrine always takes the second. Today the engine only has the churchyard form plus the hill exception.
  2. **The side (270):** a ground that stands apart from the shrine goes downstream of the houses, beyond the last of them, and NEVER upstream on the village's stream. No generator encodes this today.
  3. **The reach (270):** a village's burial ground lies within ~650 ft (325 px at 2 ft/px) of the middle of its houses. That is the surveyed reach of the visiting graves, carried to an urn ground by reasoning. Check the pool villages against it.
  4. **Water set-back (180):** no change to the ladder. It is still a guess, now labeled as one. The measured modern floor is 20 m (~65 ft), and the ladder's village floor is ~150 ft, so it stays conservative.
  5. **Size (160/206):** no change. The 0.12-0.38 acre drawn band holds under the 1934 household reckoning.

## Left open, and why
- How common each Japanese form was (temple yard against a ground of the village's own), village by village: no page read counts it. 280 carries an absence note, and the even odds are a guess.
- The distance from the houses for a village that buried in ONE ground (not two-grave): only two-grave villages were measured. 270 carries an absence note.
- No premodern Japanese burial ground's area against the population it served was found. 206's absence note stands, with a fresh date.
- The cremation ground's own siting relative to water and the houses (religion-and-death/190) is outside R1's sections and was not edited. Suggestion for its owner: in a cremating village the sanmai/cremation place takes the two-grave burial ground's position, at the settlement's edge, downstream, ~370 m on average (kawazoe-2010-ryobosei). 190 is unclaimed in RESEARCH-CLAIMS.md as far as I can see (272 claims 010-128 plus 204 and 210).
- Owed to feature 272: nothing in 204 changed. 272's R3 ("village temple ... A144 only what 269 R1 leaves open") should read 280's knob before writing the village-temple graveyard.
- Owed to no one else: none of the other sessions' sections were touched.
- Not mine: `make test-file` still fails two tests on water.html (notes 44 and 46). They come from the uncommitted water work that was already in this clone's tree when R1 started. All religion-and-death tests pass.
- The source pages and the PDFs converted to text are in /tmp/l7r-check/269-r1-pages. Kimura 1934 (22-kimura-1934.txt) and Kawazoe 2010 (20-jsce-kawazoe.txt) were converted by hand with pdftotext, because `make source-pages` reports those PDFs as having no text layer. The quote-verbatim pass may need the same text. Buck 1930 is the Internet Archive djvu text (24-buck-cfe-1930.txt).
