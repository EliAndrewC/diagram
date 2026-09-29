# 269 C3 handoff - cities/fabric (B40)

- SECTION=cities/fabric/030
- SECTION=cities/fabric/070
- SECTION=cities/fabric/080
- SECTION=cities/fabric/120
- SECTION=cities/fabric/160
- KEY=kotobank-machiwari
- KEY=ginza-machidukuri-machiwari
- KEY=kyoto-city-jobosei
- KEY=kotobank-shukuson-taigaicho
- KEY=tokaido-qa-mlit-hatago
- KEY=qianggen-beijing-inns
- KEY=pingyao-mct-streets

Reused keys whose "Used for" line grew (their write-ups are otherwise unchanged): `jokamachi-jawiki`,
`kichinyado-jawiki`, `kichinyado-kotobank`, `roji-jawiki`.

## Items

B40 KNOB - 070 now says planned Japanese towns were real grids with a known block size (Heian-kyo's 40 jo, about 120 m / 390 ft square between lanes about 12 m wide; Edo's 60 ken, about 120 m, with lots 20 ken, about 130 ft, deep and an open core), and that the block's shape takes two attested forms: the square with an open core (Edo, Sunpu, Nagoya and a few others) and the rectangle with no open core (the great majority of castle towns); castle-town trunk roads were lined without gaps and bent into dog-legs; only the main streets carried the bustle - the calibrated tolerances stand as calibrations, "gravel" is dropped from the lining rule's alley exemption - a city generator's quarter grid should roll its block shape per settlement between the two forms, weighted toward the rectangle, keeping blocks near 390 ft on the fronting side and lots about 130 ft deep (the lining rule's 175 ft building setback is looser than that lot depth); the square form's core is open ground or threaded by a lane.

B40 ACCURATE (alley surfaces; new 160, 080 points at it) - an Edo back alley began between two shops on the main street, was closed by an alley gate shut at dusk, and had a line of drain boards down its middle over a ditch 6-7 sun (7-8 in) wide; the privy and well were shared; the ground either side of the boards is an ABSENCE (GUESS, best drawn as plain earth); 080's "one lane per block" is now labeled a map convention, since the historical alley ran in from the street between two shops rather than as a block spine - the alley renderer (`town_ways.py` `alley()`, "a pale gravel path with a plank/speckle dash") should drop the gravel reading: draw an earth footway with a board line down its center; its docstring's "gravel / wood planks" claim should point at `#what-was-a-back-alley-like-underfoot`.

B40 SILENT (the lodging-house count, 120) - no page read counts cheap lodging in any town or city before modern times; the shogunate's post-station survey counted households and hatago and names no count of kichin-yado; old Beijing's chicken-feather inns are placed and priced but not counted; the unsourced "the ruling class did not count / gazetteers foreground post-stations" sentence is replaced by what was read. WHERE is now ACCURATE: Japan's firewood-fee inn stood at the edge of the post town (a hatago cost over five times as much by the 1830s; its lodgers the poor, entertainers, pilgrims, beggars, levied porters), and Beijing's cheapest inns clustered in one small poor district - the map's one cheap house in a humble quarter plus one outside each gate is consistent with both forms; the count stays the GM's 2026-07-24 GUESS; no generator change.

B40 SILENT, partly re-sourced (street-share anchors, 030) - Pingyao's four main streets, eight lesser streets and 72 lanes serving some 4,000 compounds is now cited (a Ministry of Culture and Tourism page); no page read gives any city's street share as a figure; Quanzhou 1945 and Suzhou stay unread (absence note, the one page naming them could not be fetched); a GROUNDS arithmetic check on Heian-kyo's grid (120 m blocks, 12 m lanes) gives about 17%, inside the 10-20% band - no generator change; the ~7% the maps draw stays a map calibration.

## Left open, and why

- **Key collisions.** `kotobank-jobosei` (reserved 15290 in diagram-research-3) and `pingyao-gucheng-zhwiki`
  (11980, diagram-shrines-2) are on main but not in this clone, so I cited `kyoto-city-jobosei` and
  `pingyao-mct-streets` instead. The zh.wikipedia article gives the old city's area as both 225 ha (the body)
  and 245.62 ha (the infobox); a later pass could add it to 030 under the existing key.
- **Glossary.** `kaishochi` (13440, on main) and `sun` (13430, reserved in diagram-research-5) are used in 070
  and 160 and are not in this clone; they resolve once main is merged. No new glossary file was written.
- **Sync-in not done.** `scripts/sync-with-main.sh sync-in` conflicted in 38 files, among them other groups'
  source entries and assembled pages. I aborted the merge (`git merge --abort`), leaving the clone as it was.
  The merge is the orchestrator's to make.
- **Shared tool.** `/diagram/.clones/.tools/reserve-prefix.py` now imports `_escape_log`, which is not beside it;
  it runs only with `PYTHONPATH=/diagram/scripts`. That tool belongs to 274.
- **For the GM to fetch.** TO-DOWNLOAD #278, Abe and Shinohara on the design of Osaka's and Edo's commoner
  quarters (J-STAGE PDF, no text layer here), for street widths and any road-area ratio.
- **Not owed to another owner.** No finding here corrects a section that 265, 267 or 268 owns.
- **Pre-existing.** `check-question-size.py` reports five questions over 20,000 bytes: homesteads 210,
  religion-and-death 160, vegetation 120, water 070 and water 270. None is on cities/fabric or was touched here.
