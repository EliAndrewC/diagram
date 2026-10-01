# C2 handoff - cities/government (session 1: research and write)

Written 2026-09-28 by the C2 write session (clone diagram-supplemental). The record checks are owed.

## Sections

- SECTION=0161
- SECTION=cities/government/050
- SECTION=cities/government/070
- SECTION=0115
- SECTION=cities/government/085
- SECTION=cities/government/100 (new: split from 070 - the Chinese evidence - because 070 went over the 20,000-byte cap)
- SECTION=cities/government/110 (new: split from 080 - the third plan position, servants with no gate range - because 080 went over the cap)

## Registry keys

- KEY=kotobank-kidoban
- KEY=wuju-zhwiki
- KEY=kotobank-nagayamon
- KEY=bunka-inshu-ikeda-gate
- KEY=tatebayashi-nagayamon
- KEY=aizu-bukeyashiki-guide
- KEY=kotobank-bukeyashiki (existing; the citation line, What it is, limits and Used for now cover the Nipponica entry and the rank, servant and foot-soldier passages)
- KEY=kotobank-kido (existing; the Daijisen and Nihon Kokugo Daijiten definitions added, Used for extended)
- KEY=dojo-jawiki (existing; Used for extended)
- KEY=l7r-budgets (existing, canon; the "Per-waystation staffing breakdown" section and the ashigaru note added)
- KEY=l7r-median-domain (existing, canon; the "Samurai Population of the Largest Cities" section added)
- KEY=kotobank-jokamachi - NOT this session's: `reserve-prefix.py` refused it as already defined in clone diagram-research-3 (feature 271 K3, prefix 15420, checked there). I copied that file byte for byte into this clone so 030 can cite it (the two adds are identical, so the merge will not conflict). Its `Used for:` line should gain "how much of a castle town was samurai ground and population, and where each rank lived (government)", but that edit belongs in its home clone, not here.

## Items

- B39 MIXED (ACCURATE / CONTRADICTION-RESOLVED / DEVIATION recorded / SILENT on the rest). What the record now says, part by part:
  - the samurai count (030, which had no footnotes): the canon count is cited (`l7r-median-domain`). The historical castle town is now cited as mostly samurai ground (often over half) with samurai the majority of its population, so the setting's tenth is labeled a DEVIATION. Plots were granted by status and stipend, and a samurai moved house on promotion. Every historical plot was enclosed, so the unwalled in-city samurai house is labeled a DEVIATION. The drawn proportions (two-thirds floor, three large houses, a third within 270 ft of a lane) are labeled calibration. Maps and kinds: no change; the rule stands and is now honestly labeled. Plot size by rank is K3's government 280 (see Left open).
  - ward gates (050): ACCURATE. The kido stood on the street at the block boundary, in castle towns as in Edo. Its central gate was 2.5 ken (about 15 ft) wide in the great cities, open by day, shut at 10 pm and in emergencies to cut off traffic, with wickets to left and right. That it stood square to the street is on no page (absence note); it stays the GM's 2026-07-26 ruling. Maps and kinds: the orientation rule is unchanged. A drawn ward gate could span about 15 ft with a wicket either side. That is a great city's gate, and no provincial gate was measured.
  - martial training (070 + new 100): CONTRADICTION-RESOLVED. 070 said private machi-dojo were "a late phenomenon and a metropolitan one". The Heibonsha entry says they flourished above all in the Bakumatsu, in every part of the country, with townsmen and farmers training. They were late, but not only metropolitan: the large enrolled halls grew in Edo. The thin private tail is now labeled this project's calibration. Many domains attached a practice hall to their school (`dojo-jawiki`). The Chinese examination levels are now cited (`wuju-zhwiki`), in new question 100. Still guessed, with absence notes: private academies and garrison drill at a Chinese county seat, an Edo-period pupil's fee, the boom's end, and a changing room or armory in a hall. Maps and kinds: no generator change; a provincial city keeping 1-2 private halls is consistent with the nationwide spread.
  - servant nagaya (080 + new 110): four of the six guesses are now ACCURATE, two stay GUESS.
    - Now cited: the range stood at the FRONT of the residence with its roof continuous with the gate's; a surviving range is single-story; the range served as storeroom and servants' quarters; a samurai gate had a guard room projecting at each side, its form fixed by rank; one domain gate ran to a 120 m frontage. A smaller house with few live-in servants had a wall instead of a range, and a provincial castle town needed few ranges. The Aizu karo house (Saigo Tanomo's) had a group of maids' and servants' rooms and a one-sided range beside its gate for retainers.
    - Still GUESS, with absence notes: barred lookout windows, the range on the inside of the boundary line, the 15 x 70-80 ft measured examples, the stipend threshold below which a house had no range, and where a small house's servants slept.
    - Maps and kinds: no change to the drawn form. A generator could add a small projecting guard room at each side of a gate range for senior houses (attested, rank-fixed); that is optional.
  - ashigaru plots (085): CONTRADICTION-RESOLVED plus a DEVIATION. 085 said ashigaru, kachi and doshin "got individual plots". The encyclopedia says kachi and ashigaru as a rule had no plot of their own: they lived in shared row-houses (two to a building or a row of several), each dwelling a narrow earth floor and about two rooms. Individual plots were Kaga's and Hikone's exception. Kachi are now named on a page read; doshin are not. The canon's "in Rokugan, ashigaru are peasants, not samurai" is now recorded as the setting's DEVIATION. "Forbidden walls" stays an absence. Maps and kinds: no change. The section already keeps ashigaru blocks off the city tier, and the deviation strengthens that: the setting's foot soldiers are peasant levies with no samurai foot-soldier quarter.

## Left open

- **Pointers owed once 271's and 267's work reaches this clone.** A link to a section this tree does not have fails `test_record.py`, so these are plain text for now, each with an HTML comment at the point:
  - 030 -> 0118 ("how big is a samurai's house lot, by rank", 271 K3, clone diagram-research-3).
  - 070 -> buildings 780 ("how big was a dojo", 271 G2, on main).
  - 080 -> buildings 750 (the magistrate staff's row-house, 271 G1) and 340 (where the chief retainer lives, 267 G1B), both on main.
  - 100 -> buildings 780's Chongming drill ground for the garrison-drill clause, which that section attests.
- The sync-in at the start of this session hit merge conflicts, in homesteads, religion-and-death, vegetation, water and two registry files. I aborted it with `git merge --abort`, so the clone is 372 commits behind main. The orchestrator owes that merge.
- `meirinkan-jawiki` (defined in clone diagram-research-2) would have supported "the state hall stands in the school compound near the castle": the old Hagi Meirinkan's martial halls formed its perimeter, in the third enclosure. It was not cited, to avoid pulling in a second foreign key.
- Two public PDFs from hist-geo.jp would likely give castle-town population shares by rank: `005_185.pdf`, on the zoning's area shares, and `111_001.pdf`, on domain and castle-town population. The fetch tool can read no text layer in either. They are public, so they are not added to TO-DOWNLOAD; a later pass with a PDF text tool could read them.
- The saved pages include the Hirosaki Nakacho page. It shows servants' rooms added only in the Meiji period, so it was not used.
- Nothing here owes a correction to a do-not-edit section. I grepped 0165 and the listed towns, urban-features and capitals sections for the machi-dojo and the "metropolitan" claim, and none states it.
