# Feature 271 group G2 (buildings: houses and halls as buildings) - handoff from session 1 (research and write)

- SECTION=buildings/760
- SECTION=buildings/770
- SECTION=buildings/780
- SECTION=buildings/790
- SECTION=buildings/800
- SECTION=buildings/210 (the domain schools' siting now cited for Hagi and Mito, the absence note narrowed; a pointer to 780)
- SECTION=buildings/010 (a pointer: the Japan-first rule is for compound interiors; houses outside are the knob in 760)
- SECTION=towns/030 (a pointer to 790)
- SECTION=cities/capitals/100 (the ~1 acre country manor set against the measured residences; a pointer to 770)
- KEY=kotobank-omoteyazukuri
- KEY=okeihan-kyomachiya
- KEY=toyama-bushi-yakata
- KEY=fukui-kenshi-bushi-yakata
- KEY=ranhaku-bushi-yakata
- KEY=kotobank-shimoyashiki
- KEY=hagi-meirinkan-guide
- KEY=kodokan-mito-jawiki
- KEY=chongming-yanwuchang
- KEY=toyokawa-akasaka-juku
- KEY=jiemian-ancient-inns
- KEY=netease-dachedian
- KEY=siheyuan-zhwiki, KEY=kotobank-machiya, KEY=edo-hantei-jawiki, KEY=dojo-jawiki, KEY=machiya-shoka-jawiki, KEY=qixian-cnr (existing entries; only their "Used for" line grew)

## Items

- D115 B32 KNOB - a house follows the Japanese forms (a townhouse's rooms in a row along an earth-floored passage) or the Chinese courtyard house (ranges closing a court, one court up to three or four by household and ground, never deeper than about 77 m / 250 ft), a settlement-level choice rather than one by tier or class; the courtyard house IS the Chinese town merchant's house, its street range the two-story shop (Qixian) - roll the house form per settlement with the same roll as towns/260's shop-frontage knob; on the Chinese roll draw one court for an ordinary household and two or three in a row for a rich one; compound interiors stay Japan-first (buildings/010). Which households get more than one court, and a one-court house's frontage and depth, are SILENT (absence note).
- D133 CONTRADICTION-RESOLVED (size) + KNOB (form) - measured moated country residences run about 1.2 acres (Toyama, 62 x 80 m) to about 3 (the usual one cho square, 109 m), a great one 5-10 acres; a moated residence held a gate with a lookout, the master's house at the center, a stable, a storehouse for rent rice, servants' row houses, a riding ground, and its own paddy before the gate; the Edo-period garden form (a lord's suburban estate) held gardens, vegetable plots and bamboo groves; canon puts the estate by farmland and never in the village - the drawn ~1 acre manor (C_ constant beside cities/capitals/100's "~4,900 px^2") is under every measured moated residence: the moated form should draw 1.2-3 acres (about 230-360 ft a side) with moat, bank, one gate, house, stable, storehouse, servants' row and paddy at the gate; the garden form (no moat; garden, vegetable plots, bamboo) keeps ~1 acre as a labeled guess. The house, stable, vegetable garden and bath inside are pointed at 267's R15/R16/R17/R09 in plain text (their sections are not on main yet).
- C141 D143 ACCURATE (state hall) / CONTRADICTION-RESOLVED (the hall's head) / SILENT (private dojo size) - the surviving Yubikan at Hagi is a single-story tiled hip-and-gable hall 37.8 x 10.8 m (124 x 35 ft), split into a board-floored 39-mat fencing hall and an earth-floored 54-mat spear hall, each with the lord's viewing place on its west side; Mito's Kodokan had three halls by art and an open bout ground; an Edo-period hall's head was the master's raised seat hung with Kashima and Katori scrolls, and the shrine shelf (kamidana) was NOT in Edo dojo (required in school dojo from 1936); a Chinese county kept a walled drill ground (Chongming: 37.5 mu, about 6 acres, outside the east gate, a south-facing drill hall at the north, platform, south gate; the last hall 29 x 11.5 m, 95 x 38 ft) - the state martial hall should be drawn about 124 x 35 ft split into two floors, or three halls with a bout ground for a large city; the Chinese-model city draws a walled drill ground outside a gate instead; the engine's `_dojo_hall` docstring (castle_civic.py, "the KAMIZA ... where the shrine alcove sits") should say the master's seat with scrolls, no shrine; the private dojo's drawn 44 x 24 ft hall (about 60 mats, the size of the Yubikan's spear hall) stays a guess.
- D110 KNOB - a Japanese merchant's house is one of three plans in the provincial towns (Kyoto's through passage with shop room, kitchen and formal room in a row; Edo's front earth floor; their fusion - the through passage near Kyoto), a light garden of about one tsubo inside, the storehouse at the back of the lot and never on the street, one story with a low loft (a full second story only for large merchants); a rich house splits into shop and dwelling with an inner garden and a narrow link between; the Chinese town shop is the two-story street range of a courtyard house - a town-house glyph should draw the passage or front earth floor and a back-of-lot kura; the rich-merchant estate can draw the shop/garden/dwelling split.
- D136 KNOB - the Japanese inn (hatago) was a townhouse with rooms to let: earth floor to the back, board rooms, guest rooms upstairs and behind, kitchen, bath and privy, two stories on the road, a large one about 9 x 23 ken (54 x 138 ft), no yard or stable; the Chinese carters' inn was a fenced yard on the road with lodging houses, a large stable and hay in the corners, rooms of long heated sleeping platforms (the one readable account is a weak, self-published Northeast source, used for parts only); a Chinese inn's size is SILENT - the town inn (civic_grounds/lodging.py inn()) should on the Japanese roll be a street-front house with no yard, on the Chinese roll a walled yard with a stable; the size of the Chinese yard stays a guess.

## Left open, and owed to others

- `sanheyuan-zhwiki` is reserved by diagram-research-1 (271 V1, homesteads) and not on main; 760 quotes the three-sided form from the siheyuan page instead. Once V1 lands, 760 may cite it.
- Feature 267's sections (buildings 320 bath, 380 house size, 390 stable, 400 vegetable garden, 560 striking posts and weapon rack) are named in plain text in 770 and 780, with an HTML comment; turn them into links once 267 lands.
- cities/government/070 ("Martial training is an urban institution") draws the state martial hall; nothing in it was edited here. If it states the hall's head as a shrine, it owes the correction in 780 (the master's seat with scrolls, no kamidana before 1936).
- The Pingyao museum page on house types by household (sanyamuseum.com) and the Mu family manor's page (gujianchina.cn) could not be fetched; both are named in absence notes.
- No source needed the GM to fetch it; nothing was added to TO-DOWNLOAD.md.
