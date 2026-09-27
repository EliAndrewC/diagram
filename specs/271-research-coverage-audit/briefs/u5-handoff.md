# 271 U5 handoff - urban-features: town trades (session 1, research and write)

Written 2026-09-27 in clone diagram-research-5. Record checks NOT run (the check sessions own them).

- SECTION=urban-features/500
- SECTION=urban-features/510
- SECTION=urban-features/520
- SECTION=urban-features/530
- SECTION=urban-features/540
- SECTION=urban-features/550
- SECTION=urban-features/560
- SECTION=cities/fabric/050
- KEY=token-edo-shokunin
- KEY=kotobank-okeya
- KEY=kotobank-tatamiya
- KEY=kotobank-tofuya
- KEY=kotobank-sobaya
- KEY=kotobank-yakushuya
- KEY=kusuriya-jawiki
- KEY=kotobank-sakaya
- KEY=bunka-yachiya-sakagura
- KEY=momisuriki-jawiki
- KEY=seimai-jawiki
- KEY=kotobank-konya
- KEY=konya-jawiki
- KEY=konyacho-jawiki
- KEY=kotobank-zaimokuya
- KEY=zaimokuuri-jawiki
- KEY=kotobank-debata
- KEY=kotobank-nishijin
- KEY=toyota-museum-washi
- KEY=kotobank-washi
- KEY=kotobank-niuriya
- KEY=kotobank-mizujaya
- KEY=kotobank-chaya
- KEY=kotobank-izakaya
- KEY=izakaya-jawiki
- KEY=kotobank-ryorijaya
- KEY=taishu-shokudo-jawiki

Existing keys newly quoted (their registry "Used for" lines were not touched): l7r-castes, l7r-budgets,
tsukurizakaya-jawiki, kotobank-tsukigomeya, nippon-com-kanda-konyacho, yk-kankou-konya, dongjing-menghualu-juan2,
dongjing-menghualu-wikisource. One source-reader pass read all 35 claims READ from the saved pages
(/tmp/l7r-check/271-u5-pages).

## Items

- B45 ACCURATE - urban-features/500: the cooper, tatami maker, tofu maker, noodle shop and apothecary each work and sell in the keeper's house (Japanese reference entries), the carpenter works out on site, and in castle towns coopers (and Edo's drug sellers) stood together in one street - the rice dealer is 520 - no workshop size read. - Nothing changes: they stay in the generic shop rows; a city may group one trade's shops in a street.
- B46 ACCURATE (count SILENT) - urban-features/510: a county town keeps a brewer (canon: the county's sake brewer; Edo law first confined brewing to castle towns, post towns and ports and licensed every brewer, and let villages brew only after the early 18th century); brewers were lenders and often pawnbrokers; one Edo-period castle-town store (Yachiya, Kanazawa, 1751-1829) measures 132 m2, about 19 m long (~60 x 23 ft). The 1-2 per ~3,000 stays an estimate (absence note). - The town tier should draw one brewery (a shopfront at the center, a store of at least ~60 x 23 ft behind it on a deep plot); no village brewery.
- B47 ACCURATE (drying-yard area SILENT) - urban-features/530: dyers lived in a ward in the towns and a few to a village, all working at home to order, their indigo jars sunk four together indoors; rinsing in a channel off the castle moat (Yamatokoriyama) and bolts drying in rows in the sun (Kanda) now cited; canon has the county's dye-house owner. - The town tier should draw one (or two) dyer's houses with a drying ground and rinsing water within reach, like the city dye works; count and yard placement are a labeled guess.
- B52 KNOB - urban-features/520: hulling was done on the farm (the town receives brown rice); polishing was the specialist rice polisher's (Edo 1744: ~2,100 polishers, ~5,500 mortars), by treadle mortar in the shop, or by a waterwheel driving pestles on a stream (Hokusai's Onden wheel). - Every town's rice polisher stays a generic shop; add a seeded knob for a waterwheel mill, only where a stream with fall passes the town's edge: a small shed on the bank with its wheel in the water, outside the built-up blocks (siting and size a labeled guess).
- B53 KNOB (and CONTRADICTION-RESOLVED in part) - urban-features/540: the timber trade grew where consumers met water transport and its merchants' quarters were the kiba (a 12 m city stream served Kyoto as a log pond), but retail timber dealers, who kept sawyers, were found scattered in every region. - Two forms, seeded: a yard on the bank with logs in the water (a river or channel town), or a retail dealer's shop with a small yard of stacked sawn timber behind it in ANY town, river or not (yard a labeled guess). This corrects 030's rule sentence "a landlocked city has none" (see below).
- B60 B61 C133 ACCURATE (null result) - urban-features/550: cloth was woven at home or put out to farm households in the slack season, with a city weaving quarter (Nishijin) as the ceiling; canon lists weavers and a county's clothier; papermaking was a village's off-season side job, sheets dried on boards in the sun (clean-water need unread, labeled). - No weaving works and no paper mill in a town; a city weavers' quarter draws as houses; a village map that declares papermaking may draw drying boards propped beside the farmhouses.
- B63 C116 D150 ACCURATE (count SILENT) - urban-features/560, cities/fabric/050: the kinds (tea stall, cooked-food shop, drinking house, restaurant; the Song wine shop and teahouse) and where they gathered (temple gates and precincts - the first tea sellers at Toji's gate, 1403; the road through a post town and its ends; busy quarters; bridges and water - Osaka's drinking houses even on the bridges; every lane of the Song capital) are cited; one generic shop glyph is a map drawing convention; villages got drinking houses only in the later 18th century. cities/fabric/050 now adds that the travelers' teahouses moved to the post town's ends. - The generator should place eating/tea houses among the generic shops at a temple's gate, at the town's road entrances and along the road, and at a bridge foot; a village draws none unless a road through it carries travelers.

## Left open, and owed to others

- **urban-features/030 was NOT edited**, deliberately. Group U2 (clone diagram-research-1, commits c704a564c and
  7940e332b, unlanded when this was written) rewrote 030 and cited brewery halls (bunka-sugita-shikomigura,
  bunka-hatsuzakura-shikomigura); editing the same long lines here would conflict at merge. Once U2 lands, 030 owes:
  (1) the null-results bullet should point at "Which small trades fit an ordinary town shop, and which go out to
  work?" (500) and "Where was a town's rice hulled and polished, and by whom?" (520), and say "polishing", not
  "hulling", for the rice dealer; (2) the brewery sentence should point at 510 for the county town (Yachiya store,
  132 m2); (3) the dyer sentence should point at 530; (4) the lumber-dealer sentence and the rule sentence "since
  stacked timber stands on dry ground and a landlocked city has none" should be corrected per 540: a city or town
  without a river may still keep a retail timber dealer's yard; only the log pond needs water.
- **religion-and-death/050 has no pointer to 560.** It stands at 19,961 bytes with its notes; even a one-sentence
  pointer took it over the 20,000 cap, so it was reverted. Its owner (272, done) or the orchestrator can add the
  pointer with a split, or 560 is joined from the modal side. 560 carries the gate-teahouse finding (Toji, 1403).
- **Key collisions handled:** `bunka-sugita-shikomigura` is reserved in diagram-research-1 (U2) and is not cited
  here; my reservation `bunka-hatsusakura-shikomigura` (prefix 16670) duplicated U2's `bunka-hatsuzakura-shikomigura`
  (same URL) and was deleted before use - prefix 16670 is unused. Note keys shared with other questions of the
  urban-features page were given suffixes -50 to -53 (l7r-castes-50/-51, l7r-budgets-51/-52/-53,
  tsukurizakaya-jawiki-51, kotobank-tsukigomeya-51) so they do not collide with U2's or U4's notes at merge.
- **U2 overlap:** U2's 310 ("How many shops does a county seat keep, and of which trades?") counts Hachijo's sake
  brewer and two dyers; 510 and 530 could point at it once both are on main (not linked here: the anchor does not
  exist in this clone).
- No item of mine was claimed by another session. No section owned by 267, 268, 269 or 270 was touched. Nothing
  was added to TO-DOWNLOAD.md.
