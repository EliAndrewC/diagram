# 271 T2 handoff - towns: houses on the street (session 1: research and write)

Written 2026-09-27 in clone diagram-research-4. Canon (`make canon`) was silent on every item except the budget's
"laborers, master (rich)" rows, which B34 uses. No item was claimed by another session.

## Sections to check

- SECTION=towns/260
- SECTION=towns/270
- SECTION=towns/280
- SECTION=towns/290
- SECTION=towns/300
- SECTION=towns/310
- SECTION=urban-features/100
- SECTION=cities/fabric/010
- SECTION=cities/fabric/020
- SECTION=cities/fabric/110

(cities/fabric 010, 020 and 110 changed by one pointer paragraph or sentence each, no new footnotes. urban-features/100
was rewritten for the wealth bands: its absence note became a citation plus a narrower absence note, and it gained two
footnotes.)

## New registry keys

- KEY=kotobank-machiya
- KEY=kotobank-tanagari
- KEY=tehaishi-jawiki
- KEY=ouchijuku-jawiki
- KEY=sekijuku-jawiki
- KEY=unnojuku-jawiki
- KEY=matouqiang-zhwiki
- KEY=dianwu-zhwiki
- KEY=qixian-cnr
- KEY=hirairi-tsumairi-jawiki
- KEY=homes-nagaya

Existing write-ups changed only in their `Used for:` line (plus "two-storey" corrected to "two-story" in
kotobank-shukubamachi): machiya-shoka-jawiki, kotobank-uradana, kotobank-shukubamachi, kotobank-hitoyado,
naraijuku-jawiki.

## Items

- B27 D109 KNOB - Frontage is set by wealth. Kyoto had three bands: 10+ ken (about 65 ft) for the rich, 4-5 ken (26-33 ft) for the ordinary shopkeeper, 1.5-2 ken (10-13 ft) for small traders or renters. Edo's lots were 5-6 ken by 20 ken, the front shop kept to about 5 ken (33 ft) deep, and the great stores merged lots up to 36 ken. A post town's lots shared one depth and varied in frontage. One Chinese county seat (Qixian) had shops of about 5 bays of 2.5-3 m (41-49 ft), deep, with a courtyard behind. The share of shops in each band, and the spread of Chinese shop sizes, is SILENT - For the kinds: the 48 x 32 ft `shop` has an Edo front shop's depth, but its width is 1.5-2x an ordinary Japanese shop's; it matches only a Chinese five-bay shop or Kyoto's rich band. The generator should roll the Japanese or Chinese model per town, and on the Japanese model draw the ordinary shop about 26-33 ft wide (small 10-13, rich 65+), all about 33 ft deep. `merchant` (54 x 36) and `merchant_large` (86 x 60) sit in the rich band. The band weights are a labeled guess.
- B29 KNOB - A Japanese town's street front took one of two forms, decided by traffic. On a busy highway, each house was built across the full width of its lot and inns stood eave to eave, with fire walls on the roofs (Unno). On a side road or in the hills, farmhouse-like inns stood behind a front yard with gaps between them (Ouchi, thatched). Chinese town houses stood close, with fire gables between house and house (the Hui-style horse-head wall), and Qixian's shops were close-set. How many towns took each Japanese form is SILENT - For the kinds: town frontage placement becomes a per-town knob. Busy towns get touching rows along the street, with the drawn joint of cities/fabric/020. Quiet towns get a front-yard setback and gaps. The weight between the two is a guess.
- B30 D113 D114 KNOB - Stories: the machiya's first second story was a low half-story used for storage, and it was low because domains banned more. The full second story came later, and Kyoto kept the half-story except for large merchants. Busy post towns had two-story inns by late Edo; Seki mixes 2-story, half-story and 1-story houses. Roofs: tile and plaster in the west; stone-weighted board in the east and the Kiso valley, and on the busy highway's inns; thatch in a half-farming station (Ouchi); early Edo was mostly shingle and board. Fire law: after 1657 Edo tried earth-covered thatch, and in 1720 it recommended tile (which it had once forbidden to townsmen) and plastered walls. Late Edo's plastered storehouse style reached the main house, but Kyoto kept its storehouse at the back of the lot. No fire law for a small town's roofs was found (SILENT). China: Qixian's street buildings were 2 stories with small gray tile, and the southern shophouse was 2-3 stories - For the kinds: add a per-town roof-material knob (tile / board / thatch) for the street front. Stories change nothing in plan. A storehouse (kura) stands at the back of its lot, not on the street, except in a great city. Giving a rich merchant tile in a board-roofed town is a labeled guess.
- B33 C85 KNOB - A city's laborer rented a one-story back tenement. The unit was 9 shaku by 2 ken (about 9 x 12 ft, 108 sq ft), with a range up to 2 x 2.5 ken. Several rows stood on a lane about 1 ken wide, with a shared well, privy and trash heap in one corner. The residents were peddlers, craftsmen and day laborers. There was one row behind a 3-ken shop and two behind a 5-ken one, and about 70% of Edo and Osaka residents rented. In towns, 20-30% rented (Ou, Hokuriku) to 50-60% (Setouchi). Post-town households that supplied porters and horses held roughly even plots of their own. SILENT: where a Chinese county town's laborers lived, and a whole block's ground per household - For the kinds: the 34 x 24 ft `laborer` (816 sq ft) is the size of a row building of 7-8 back-tenement units, not one household. The orchestrator must decide whether the glyph stays a household or becomes a row. City laborers belong on back lanes behind the shops. In towns, a per-town tenant-share knob decides between laborers on their own small plots (low share) and back tenements (high share); the laborer-specific split is a calibration, labeled. Cities/capitals/100 (the capital's per-household ground cost) was not edited; its "laborer row house at 891" could point at towns/290.
- B34 SILENT - The large laborer's house is the setting's master (rich) laborer's: about 1 laborer in 12 in a town, 1 in 8 in a city (budgets canon). The attested historical analogues are three: the Edo placement broker, who lodged the men placed until they had a place (kotobank; tehaishi-jawiki calls it a bunkhouse-like boarding house, but that article is flagged unsourced); the house manager living on the tenement lot; and the post town's porters' office among the inns. No page gives the size of any of them - For the kinds: `laborer_large` stays 50 x 34 ft as a labeled GUESS. Its modal should say it is a labor boss's house that finds work for laborers and houses some of them, and that it stands among the laborers' housing, not on the shop street.
- B38 ACCURATE - A town house faces the street it stands on. A post town's lots were strips of one depth with the house on the road and, since households also farmed, a vegetable garden behind. The ridge usually runs along the street, with some gables turned to it, and either way the entrance is on the street face. Rows are one deep; a second rank appears only on a back lane, following the city rule of cities/fabric/110 - For the kinds: town houses should not stack behind one another off a street. The space behind a street-front town house is its garden plot. A second rank belongs only on a drawn back lane.

## Left open

- The Osaka Semba/Tanimachi frontage figures on machiya-shoka-jawiki were read and not used. They describe three-story machiya of the Taisho era and later (source-reader's scope finding). The same page misdates the pantile (延宝2 given as 1647; it is 1674), so no date was taken from that line.
- A business-encyclopedia page (wiki.mbalib.com 商业建筑) said to give Chinese street shops as 1-5 bays, most often 3, could not be fetched (TLS timeout). If a later session can read it, it would give the Chinese band spread that towns/260 records as silent.
- No correction is owed to another feature's sections. towns/050 (T3's) was not touched; towns/280 covers the street front around the inn.
