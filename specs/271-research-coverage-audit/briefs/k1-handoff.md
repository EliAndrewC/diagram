# K1 handoff - cities/fabric: blocks, wards and merchant estates (session 1: research and write)

Written 2026-09-27 in clone diagram-research-3. No item of K1 had been claimed by another session.

## Sections

- SECTION=cities/fabric/200
- SECTION=cities/fabric/210
- SECTION=cities/fabric/220
- SECTION=cities/fabric/230
- SECTION=cities/fabric/240
- SECTION=cities/fabric/090
- SECTION=cities/fabric/100
- SECTION=cities/fabric/130
- SECTION=cities/hinterland/050
- SECTION=settlements/090

## New registry keys

- KEY=crd-heiankyo-block
- KEY=machiwari-jawiki
- KEY=kotobank-jobosei
- KEY=ginza-machiwari
- KEY=kotobank-edo-machinanushi
- KEY=kotobank-machiyakunin
- KEY=kotobank-machikido
- KEY=bunka-sugimoto-omoya
- KEY=kyototuu-sugimoto
- KEY=jtb-sugimoto
- KEY=bunka-hasegawa-omoya
- KEY=matsusaka-hasegawa-bunka
- KEY=matsusaka-hasegawa-kanko
- KEY=iwasaki-kitakata
- KEY=jtb-kitakata
- KEY=kotobank-jokamachi
- KEY=thepaper-city-fields

Existing keys newly cited on these pages: `lijia-zhwiki` (its Used for updated), `machiya-shoka-jawiki`,
`sekkei-sya-sayama-kura`. The saved pages are in `/tmp/l7r-check/271-k1-pages` (MANIFEST.txt); the
source-reader's verdicts were 19 READ and one split, the Nanjing "three-fifths" figure, which is 1921 and not
used.

## Items

- C91 ACCURATE - a city block is about 120 m (about 400 ft) square in both Japanese plans that give a figure (Heian-kyo's 40 jo, Edo's 60 ken); Heian cut it into 32 lots of about 50 by 100 ft, Edo into lots 20 ken (about 130 ft) deep round an open middle, about fifty ordinary street-front lots a block by the record's arithmetic; the Chinese provincial block is an absence note - the generator should lay a city's commoner blocks at about 400 ft a side with lots about 130 ft deep and 25-30 ft wide (a few 60 ft+), tenement rows behind; check the drawn cities' blocks against 400 ft.
- C102 ACCURATE - a ward (machi) is the houses along one block-length of street, closed at night by its own gate, run month by month by its house-owners and paying for its own bell, dredging and fire standard; one hereditary headman governs two or three to a dozen and more wards and lives in one; the Ming unit is 110 households; the number of wards in a provincial city is SILENT (absence note, the spec's "a dozen or two" is labeled a guess) - the generator should draw a ward gate at each end of a ward's street and no ward wall, and one headman's house (a larger ordinary house) per few wards.
- B28 D117 D118 ACCURATE, with one CONTRADICTION-RESOLVED and one SILENT - two surviving great-merchant houses (Sugimoto, Kyoto: about 70-100 ft frontage, 1,200-1,560 m2 site, three kura in a hook behind the house, a high wall round the estate; Hasegawa, Matsusaka castle town: grew by buying neighbors to 34 ken, about 200 ft, main house 100 by 52 ft, one kura at the front and four at the back, lot bounded behind by the block's drain which is the ward line) show a shop-house at the street edge with kura behind and a wall round the rest, no gatehouse and no set-back court; how many per town of 1,200 is SILENT - the merchant-estate kind should front a commercial street with its main house at the street edge, roll frontage 70-200 ft, carry 3-5 kura at the back (a knob for one more at the front), and drop the in-block-core placement: fabric/090's rule now says that placement is a DEVIATION from the record, and the modal written from 090 owes the change.
- B31 C50 D152 KNOB - a merchant's kura stand at the back of the lot in a row or hook (Kyoto custom, both houses), and in some estates one more at the street beside the entrance (Hasegawa; Edo's kura-built shop fronts); each about 19-38 m2, 14-20 ft square; one great house holds three to five, and one to every four households (Kitakata, a famous kura town) is a ceiling; spacing between kura is SILENT (absence note) - the generator's city floor of five storehouses (fabric/130) is well under the record (two great houses alone hold eight): count about four per walled estate plus one or two per large merchant house, capped at one per four households, placed at the lot's back away from the street.
- C172 CONTRADICTION-RESOLVED - canon has no farmer household inside a city's wall; the record now has the in-wall ground worked by the city's own households beside their other work (Chinese city dwellers growing rice and vegetables inside the wall; townsmen of small castle towns farming beside their trade), and villagers coming in through the gates is an absence note - hinterland/050's rule ringing an in-wall field with about sixteen farmhouses per 3,000 ft (not counted in the population) contradicts the canon and the record, and the section now labels that ring a DEVIATION; the generator should edge an in-wall field with the city's own houses and draw no farmhouse inside the wall. This moves a pool map's layout, so it is the GM's call before anyone changes the engine.

## Left open, and owed to other owners

- Coordination with 269: its cities/fabric 070 (B40, the street grid) and cities/government 085 (B39, the ward
  gates) and cities/hinterland 030 / cities/sizing 010 (B41) were not yet written in this clone. fabric/200 links
  070 by anchor; fabric/210 links cities/capitals/060 for the gates, and owes a link to 269's government ward-gate
  question once it lands; fabric/240 cites neither hinterland 030 nor sizing 010 (the 030 in this clone is the moat
  question, not about who farms).
- 267's urban-features/210 (merchant storehouses) is not in this clone; if it states a storehouse's size or siting,
  fabric/230 owes it: at the back of the lot, 14-20 ft square, 3-5 per great merchant house, and the knob for one at
  the street.
- The Sugimoto site's area disagrees between two pages (1,200 m2 against 30 by 52 m); both are noted, not resolved.
- Scripted edit: one `python3` heredoc edited fabric/210's notes (translation glosses and a key rename) against the
  brief's rule; the result was checked by the record tests, and every later edit was done with Edit.
