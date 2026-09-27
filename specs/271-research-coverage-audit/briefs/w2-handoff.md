# 271 W2 handoff - ways: streets, bridges and approach roads by tier (session 1: research and write)

Written 2026-09-27 in clone diagram-research-5. All 32 claims went through ONE source-reader pass (32 READ, 0
CONTRADICTED); the pages are saved in `/tmp/l7r-check/271-w2-pages` (MANIFEST.txt; note its 27-ja row is listed twice -
the file on disk is 町割, the 石橋 page was overwritten by the tooling defect fixed below and is cited nowhere).
`make record`, `make citations`, `make glossary`, the four record tests (257 passed) and `check-question-size.py` are green.
No record checks were run (quote-check, record-format, source-applicability are owed by the check sessions).

## Sections

- SECTION=ways/160
- SECTION=ways/170
- SECTION=ways/180
- SECTION=ways/190
- SECTION=ways/200
- SECTION=ways/210
- SECTION=urban-features/110

## Keys

- KEY=shukubamachi-kotobank
- KEY=nakatsugawa-masugata
- KEY=oiso-shukuba-mlit
- KEY=ginza-machiwari-column
- KEY=mizu-edo-gesui
- KEY=yichang-drains-hubei
- KEY=netease-city-street-widths
- KEY=hlj-traditional-bridges
- KEY=nihonbashi-bridge-jawiki
- KEY=zhouzhuang-zhwiki
- KEY=nikko-suginamiki-jawiki
- KEY=thepaper-road-trees
- KEY=yidao-zhwiki
- KEY=mlit-gokaido-seibi

Existing keys newly cited on these pages: shukuba-jawiki, jokamachi-jawiki, roji-jawiki, dobashi-jawiki, l7r-budgets (canon).
Glossary: new term `dobu` (13340); `masugata` (3980) widened to cover the post town's crank as well as the castle gate court.

## Items

- B14 C89 ACCURATE - a post town's street was 2 to 4 ken (about 12 to 24 ft), the Edo highway standard about 9 m (4-7 m in mountains), a Chinese Ming-Qing main street 4-8 m and lane under 3 m (a self-published popular account), the back alley (roji) 3 to 6 shaku; no side-lane width was found (absence) (ways/160) - the town street's 24 ft default stands at the top of the band; a lesser street may be drawn narrower down to ~12 ft (width a guess); the 10 ft alley is now labeled a map drawing convention for a 3-6 ft passage; nothing need change, but the generator MAY roll lesser streets narrower.
- B15 C101 KNOB - town streets were earth (Edo mud, c. 1630); a Chinese official road through a post station could be stone slab; three drain forms are attested: an open channel down the street's middle or along its edge (post town), the eaves ditch ~9 in wide at the house fronts feeding the front-street drain (Edo), and covered drains under stone lids (Yichang); a Chinese town's own street paving and a post-town channel's width are absences (ways/170) - draw town streets earth; roll the Imperial road's stretch through a town as earth or stone slab; roll one drain form per town (middle channel / edge ditches / none visible). Today no town draws any drain.
- B16 KNOB + ACCURATE - a post town is one street with strip lots on both sides (Oiso 1803: 269 of 605 houses on the highway); a Chinese market town (Zhouzhuang) had two main streets in a T; the road entered a post town through a masugata crank (bent twice at right angles) at both ends, with a mitsuke bank and gates; castle towns bent roads and made dead ends; the count of side lanes is an absence (ways/180) - roll the town plan (single street / T); bend the road twice at right angles at each end of the built street. NOTE: this is the opposite of the city's straight gate-to-gate Imperial road, which cities/fabric/040 records as a deliberate deviation; whether a TOWN follows history (the crank) or the city's deviation is the one decision here I would put to the GM before the generator draws it.
- B18 C86 CONTRADICTION-RESOLVED - urban-features/110 said a quarter's paths were packed-earth footpaths because paving was beyond a quarter's means, on no source; the roji was a 3-6 shaku private passage entered between the street's shops, with boards over a 6-7 sun ditch down its middle, a gate shut at dusk, used almost only by its residents (Chinese lanes under 3 m), and the path is "not a street" because it serves only the houses on it (urban-features/110) - keep drawing it as a narrow single-file way never captioned as a street; the generator may draw the board line down its middle; the "cannot afford to pave" reason is gone from the spec. The section's body changed, so an entry-drift check is owed on the class(es) whose Entry names it.
- B19 ACCURATE - a post town's highway was built up in order from the middle out (transport office, honjin and waki-honjin in the middle; inns, teahouses, cookshops around them; merchants and craftsmen farther out), with a notice-board place; on busy highways each lot's main house filled its whole frontage, on byways inns often kept front gardens and gaps; the label is this project's decision, beyond the town's built edge, read from the canon's county-kept minor roads (ways/190) - where the Imperial road runs through a town: continuous two-sided frontage, officials' lodgings and big inns central, trades at the ends; place the "Imperial Road" label beyond the built edge, as a city's is.
- B20 C167 KNOB - Japanese river bridges were overwhelmingly earth-decked timber (dobashi), plank decks for an important few, stone very rare; castle towns built timber post-and-girder, Kyushu stone arches the exception; Chinese water towns kept stone arch bridges; Nihonbashi (~69 m by ~8 m) is the upper bound; a town's bridge count and a town bridge's own size are absences (ways/200) - roll one bridge form per town (earth-decked timber / stone arch); one bridge per street or road meeting the water, deck as wide as its way, capped at ~26 ft wide and ~225 ft long; count a guess.
- C175 ACCURATE + KNOB - the 1605 highway standard (~9 m) came with a mound every ri (~2.4 mi) and roadside trees; the shogunate kept pine and cedar avenues on the main highways; China lined official roads with trees from the Zhou, replaced its per-li earth mounds with pagoda trees (Western Wei), and the Yuan ordered elm, willow and pagoda trees; where an avenue stops short of a town is an absence (ways/210) - line the Imperial road approaching a town with a row of trees on each side, species rolled per settlement (pine, cedar, elm, willow, pagoda tree), running to the gate market or first houses; a low tree-planted distance mound only where its interval falls on the sheet. Today no town draws an avenue.

## Open, and owed to others

- **Held keys and terms in other clones (not on main when written):** `jarimichi-jawiki` and `ichirizuka-jawiki` (and glossary `ichirizuka`) are reserved in diagram-research-3 (W1); glossary `mitsuke` in diagram-research-4; glossary `honjin` and a different MLIT page `mlit-kinsei-michi` in diagram-buildings. I did not cite the held keys, to keep this clone's record green; `honjin` and `mitsuke` are used in the prose and will take their tooltips when those land. Once W1 lands: ways/170's surface paragraph should point at W1's ways/100 (lane surface; `jarimichi-jawiki` says roads were trodden earth and gravel was for main roads), and ways/210 may cite `ichirizuka-jawiki` for the mound's size and tree (note its 1 jo = "about 1.7 m" is wrong; 1 jo is about 3 m, as the zh page says).
- **To 269 (cities/fabric 080, B40):** its "unpaved gravel or plank rests on general reading" for the city alleys can now cite `roji-jawiki` (boards over a 6-7 sun ditch down a 3-6 shaku alley) - the same notes as urban-features/110. Nothing else owed: fabric 030/070/080 and hinterland 040 are linked, not edited.
- **Source cautions for source-applicability:** `netease-city-street-widths` is self-published and unsourced (hedged in prose); `dobashi-jawiki` and `yidao-zhwiki` carry unsourced-article tags; the MLIT page dates the milestone order 1605 where the ichirizuka article says 1604.
- **Tooling:** `scripts/_source_pages.py` numbered a third save past the manifest's row count, which falls behind the files on disk after a retried failure, and overwrote two saved pages; fixed to number past the highest file on disk, with a test (committed separately, `271 W2: make source-pages ...`).
- ways 010, 020 and 030 needed no edit: the new questions point at them.
