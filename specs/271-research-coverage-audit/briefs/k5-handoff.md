# K5 handoff - cities/capitals: granaries, brokers, the castle and the lineages (session 1: research and write)

Written 2026-09-27 in clone diagram-research-2. No K5 item had been claimed by another session.

## Sections

- SECTION=cities/capitals/110
- SECTION=cities/capitals/120
- SECTION=cities/capitals/350
- SECTION=cities/capitals/360
- SECTION=cities/capitals/370
- SECTION=cities/capitals/400
- SECTION=cities/capitals/410

## New registry keys

- KEY=fudasashi-jawiki
- KEY=kotobank-asakusa-okura
- KEY=kotobank-jomai
- KEY=homemate-sannomaru
- KEY=fukuokajyo-sannomaru
- KEY=kanazawa-honda-kamiyashiki
- KEY=kanazawa-kaga-hakka
- KEY=kazusa-bugyosho
- KEY=edo-ashigaru-bugyo-yakutaku
- KEY=orange-hatchobori-yoriki
- KEY=tabiiro-takayama-jinya
- KEY=jtb-takayama-jinya
- KEY=shoho-shiroezu-jawiki

Existing keys newly quoted here (the check sessions should re-check their notes): honmaru-jawiki,
edo-hantei-jawiki, fukui-bushi-jutaku, machi-bugyo-jawiki, takayama-jinya-jawiki, bukeyashiki-wiki,
jokamachi-jawiki, japanese-castle-enwiki (a second note, for the sloped stone bases).

## Outcomes

- C49 ACCURATE - 120 now says why the Emperor's granaries stand apart: Edo kept the overlord's RESERVE rice inside castles (it went with the castle like its arms) and its WORKING stipend rice at the Asakusa granary on the river, and the setting's budget notes make the Imperial granaries a working store that pays Imperial stipends, so history and the GM's threat model agree; both knob values are now cited (beside the magistrate: Takayama's intendant's office held its rice storehouse inside its grounds; on the water: Asakusa, the Osaka warehouses). - Nothing new to draw; the existing `imperial_granary_seat` knob stands, and its code comment can point at the 120 anchor.
- C52 ACCURATE (the row's length a GUESS, with an absence note) - 110 now says who kept the Edo row (fudasashi and rice wholesalers, a 109-house licensed guild in three street groups, bound to live at Kuramae and to post the day's rice price in front of their shops) and what it looked like (big merchant houses eaves to eaves on the granary's town side, facing it, with a firebreak kept open in the same block). - The brokers' row should be drawn as ONE continuous street of large merchant frontages on the landward side of the domain granary, facing it across the street, with an open firebreak kept clear before the storehouses; 6 to 12 frontages (guess). A new spec line in 110 states it.
- C56 D129 ACCURATE (350: a period CONVENTION plus a labeled DEVIATION; 360: attested, with four items left a GUESS) - 350 now cites the 1644 Shoho castle plans as the precedent for a castle drawn as works without rooms (their standards name walls, moats, keep, turrets and streets, and no residence or storehouse), and labels our omission of the keep, turrets and inner baileys a deviation argued by the experiment; the sloped stone rampart is cited. 360 now cites the keep, the goten (residence and seat of government), the stables, the storehouses, the reserve rice and the castle's arms as inside; the treasury, guard barracks, wells and gardens have an absence note and stay a guess. - No change to what the map draws (the castle stays blank). Two findings owed elsewhere, below.
- C59 KNOB (siting) and ACCURATE (the size anchors; the Chancellery-line mapping a GUESS with an absence note) - 410: history graded a great house's estate by its holding (Edo scale: 2,500 tsubo for 10,000-20,000 koku up to 7,000 for 100,000-150,000; Fukui: 1,000 koku ~ 1,000 tsubo; Kanazawa's Honda elder house over 10,000 tsubo), and because the estate housed the house's own people the GM's households rule is the history's own logic; siting is attested two ways - the samurai ground nearest the castle, OR inside the castle's outer bailey (Fukuoka). - Lineage compounds (no generator yet): walled, row-house gate, sized by households from ~36,000 sq ft (~4,000 px^2) to ~90,000 sq ft (~10,000 px^2) or somewhat more, never near 356,000 sq ft; sited on the samurai ground nearest the castle, the chancellors' nearest. The inside-the-bailey knob value is HELD pending the GM (see open items).
- C70 ACCURATE (size, calibrated) and KNOB (staff housing) - 400: the compound is court, office and residence in one wall, like the Edo town magistracy (office one side, residence the other, a wing for the magistrate's own retainers); anchors 2,500-2,600 tsubo (Edo magistracies, ~90,000 sq ft) and over 3,000 tsubo (Takayama intendant's office, with its granary); staff housing attested two ways - inside in perimeter row housing (a domain's Edo estate) or outside on plots of their own in a group quarter (the Edo magistracy's officers and constables). - Raise the capital program's "Imperial Magistrate's compound" line from 8,000 to 10,000 px^2 (72,000 -> 90,000 sq ft; the current figure is a fifth under the smaller anchor), and add a per-map knob `staff inside | staff beside`; under `beside` the dozen staff households take a walled group quarter against the compound wall, drawn in the compound's ink (a convention), and the compound line no longer houses them.

## Open, and owed to others

- **For the GM (via escalation-check):** the lineage compounds' siting is a two-form knob, and one form (inside the castle's outer bailey, attested at Fukuoka and in the general account of the third bailey) puts them behind the blank castle's wall, where nothing is drawn - which would erase the labeled compounds 370 calls the tier's best flavor feature. May the knob take that value? Until answered, 410 and 360 keep them outside.
- **cities/capitals/140 (not K5's; no feature claims it):** `honmaru-jawiki` says that as a castle's government grew, its offices moved from the innermost bailey to the second or third bailey - INSIDE the castle. 140's claim (and the `citybudget.py` comment) that "a jokamachi's offices spilled out of the ninomaru as they grew" should be re-checked against its own sources; 360 now says the source read here shows offices moving within the castle and points at 140 rather than restating it.
- **Engine inconsistency found in passing (not a research item):** `CAPITAL_CIVIC_PROGRAM` in `citybudget.py` still prices a "House Chancellery" line of 2,000 px^2, while 360's and 370's rules say a capital draws no chancellery compound (the council meets in the goten). Whoever next touches the capital program should reconcile the two.
- Not searched: the Chinese side (a prefectural seat's state granary against its yamen) for C49; Japan leads at the capital tier (010), and the finding did not need it.
- A 2,617-tsubo figure for the South magistracy, attributed by a search summary to a plan of Ooka's official residence, was not found on a readable page (wheatbaku.exblog.jp returned 403); the kazusa page's hedged 2,500-2,600 is what is cited.
- **Merge overlap:** K3 (clone diagram-research-3, in progress) also edits cities/capitals 360. K5's 360 edit
  rewrites the Sources roster and adds two paragraphs before "The one that matters most", and replaces the notes
  file; the orchestrator should expect a conflict there and keep both groups' additions.
- `religion-and-death.html` was re-assembled by `make record` from another session's committed fragment (a one-line drift); it is left unstaged for its owner.
