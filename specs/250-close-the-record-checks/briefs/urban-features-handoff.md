# Handoff - feature 250, page `urban-features`, session 1 (locate, read, write)

Sources read by one `source-reader` over `/tmp/l7r-check/urban-features-pages/` (17 saved pages) and the GM's
Mukoyama PDF: 5 READ, 2 CONTRADICTED (the text was rewritten to what the page says), 4 NOT-FOUND (absence notes).
Canon checked in one folded `make canon` call (horses, stable, warhorse, deputy, visits): no domain horse count, no
visiting frequency. `make record`, `make citations` and the four record test files are green; no question is over
the size cap (010 and 070 came within 100 bytes of it and were brought back under by trimming this session's own
glosses and roster notes, not split).

## Changed questions

- SECTION=010 (the notice board)
- SECTION=026 (the punishment ground in town)
- SECTION=060 (tanning yards) - notes only
- SECTION=068 (which way out of town a tanning yard stands)
- SECTION=070 (the bell-and-drum tower)
- SECTION=080 (stable yards)
- SECTION=170 (drawing a clan border)

## New or changed registry keys

- KEY=five-punishments-enwiki (new, 9710)
- KEY=beijing-fortifications-enwiki (new, 9720)
- KEY=daikan-jawiki (new, 9730)
- KEY=unl-beefwatch-cattle-water (new, 9740) - modern US feedlot cattle; source-applicability should judge
- KEY=blm-oregon-trail-wagons (new, 9750) - 1840s-60s American emigrant trail; source-applicability should judge
- KEY=shuanmazhuang-zhwiki (new, 9760)
- KEY=mukoyama-linear-borders (existing entry unchanged; newly quoted at a second note, `mukoyama-linear-borders-2`, p. 270, from the GM's downloaded copy)

## FR-002 items

| item | form | note |
|---|---|---|
| kosatsuba - "ban edicts" | citation | `kosatsu-jawiki-10`: Shōtoku 1711 board article 「一、博徒之類一切に禁制之事」; the old "(ban edicts are this page's addition)" gloss removed from `kosatsu-jawiki-2` |
| kosatsuba - deputy "twice a year" | citation | `daikan-jawiki` (replaces absence `...-decision-2`): intendants near the Kanto came out only for surveys, harvest inspections, tours, serious incidents; gloss says the page is Kanto-scoped, distant intendants lived locally, and twice a year is this page's estimate |
| kosatsuba - "Every site ... ON the way" | citation | `kosatsu-jawiki-11` (往来などに掲示) + `adachi-kosatsu` (bridge ends, officials' gate fronts); gloss says "never open ground" is this page's reading |
| justice works - bamboo a COURT act | citation (partial) | `five-punishments-enwiki` (笞, 杖 defined) + `yamen-enwiki` (zao stood around the court at trial and applied minor punishment); gloss: no page read says WHERE, so the courtyard is this page's reading. The old reading-gloss on `cangue-enwiki` removed |
| trade works - "several hundred horses per domain" | absence | `tanning-yards-...-gate-2` rewritten, searched 2026-09-27: 厩舎 read, Equine Museum PDF unreadable here (scanned, and about the shogun's stables), canon gives no number |
| drum tower - City God "from 1369" | already cited | `chenghuangmiao-zhwiki` carries the 1369 edict and the four ranks down to county; no change |
| drum tower - Beijing ~6.5 x 5.3 km | citation (partial) | `beijing-fortifications-enwiki` (replaces absence `the-bell-and-drum-tower---one-per-walled-seat`): the 24 km perimeter; gloss: the sides are this page's map reading. The zh page (北京内城, not registered) says wider east-west, the en page says east and west walls longer - the two disagree on orientation; the prose states no orientation |
| stable yards - 拴马桩 WELL-ATTESTED | citation | `shuanmazhuang-zhwiki` placed at 拴马桩; absence note `stable-yards-...` trimmed to the yard's ground and edge only |
| stable yards - cattle "~1-2 gal/min" | citation, TEXT CHANGED | CONTRADICTED by the page (1.1-3.7 gal/min); prose now "~1-4 gal/min ... over in two to seven minutes"; `unl-beefwatch-cattle-water` replaces absence `...-relay-2` |
| stable yards - "rested for HOURS" | citation, TEXT CHANGED | CONTRADICTED (most rested "only an hour or so"; several hours depending on weather); prose now "unhitched to rest - most for an hour or so, several hours in hot weather"; `blm-oregon-trail-wagons` replaces absence `...-relay-3`, which had been sitting on the "9.5 ft trough" |
| (found in passing) stable yards - "one 9.5 ft trough" | absence | new `stable-yards-...-relay-4`: the MDFCTA page gives the 1,800 horses and no trough length |
| tanning - first "designated carcass routes" | absence | the existing absence note `tanning-yards-...-gate-7` now also marks the first statement (both are in 068); its search refreshed to 2026-09-27 (穢多 re-read: carcass handling "strictly controlled", no route) |
| clan border - "fifty years", "smaller and more closely spaced" | citation | `mukoyama-linear-borders-2` (replaces absence `drawing-a-clan-border`): Mukoyama p. 270 says both in so many words, plus the Nanbu-Date page's 1688 "smaller mounds" sentence; `mukoyama-linear-borders` added to 170's Sources roster |

## FR-006 items

- 36 (caravanserai one courtyard well): CONFIRMED - 080, the BUFFER sentence, carries `caravanserai-enwiki-2` (the fountain or well in the courtyard), with the INSTEAD-of-basins reading labeled inline.
- 58 (salted hides keep for months): CONFIRMED as rewritten - 064, "raw hides were salt-cured to keep ... a wet-salted pack stands a month", carries `tanning-leather-enwiki-3` (whose gloss says months of keeping is on no page).
- 59 ("the"): NOT LOCATABLE - the item's text is one word; no action possible.
- 60 (samurai estates outside the walls): CONFIRMED as rewritten - 130, "Great houses kept roomier walled estates in the outskirts ...", carries `edo-hantei-jawiki`.
- 86 (Potters are not hinin): CONFIRMED - 050 carries `hinin-jawiki`, whose gloss says the sentence follows from the status definition rather than being stated.
- 87 (kawaramono self-name): CONFIRMED as rewritten - 060, "The name the caste went by was kawaramono", carries `kawaramono-jawiki` (gloss: "were called", not their own name); 130's related sentence carries `abele-2018-kawata`.

## Left open

- Entry drift: 080's body changed in substance (the cattle rate and the rest interval), so `_entry_owed.py` may name a stable-yard class at push.
- source-applicability is owed on the two non-Asian sources (UNL feedlot cattle, BLM Oregon Trail) before their numbers stand.
- The Equine Museum paper (https://www.bajibunka.or.jp/uma/pdf/20230113_03.pdf) could not be read here (scanned PDF, no pdftoppm); it is about the shogun's stables and was not added to TO-DOWNLOAD.md, since it would not give a domain's count.
