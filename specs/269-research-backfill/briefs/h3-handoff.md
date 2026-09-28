# 269 H3 handoff - homesteads: thin sections (B19, B20)

Written 2026-09-27 by the H3 write session. The record checks are owed (not run here).

## Sections

- SECTION=homesteads/050
- SECTION=homesteads/110
- SECTION=homesteads/145
- SECTION=homesteads/160
- SECTION=homesteads/170
- SECTION=homesteads/190

## New registry keys

- KEY=gogura-kotobank
- KEY=jikata-monjo-kotobank
- KEY=oamishirasato-kaoku
- KEY=kawai-jutaku-bunka
- KEY=nta-nengu
- KEY=chimei-jawiki
- KEY=yaji-tani-sawa
- KEY=okamoto-1956-sonraku
- KEY=santome-shinden-jawiki
- KEY=shuson-jawiki

`shuson-jawiki` (12350) is a byte-identical copy of the entry committed in `/diagram/.clones/diagram-research-3`
(feature 271 W1, 46f3e64f). The reserve tool refused a second home for the key, and the identical file merges
cleanly. Its `Used for:` line names only (ways). Once both have landed, append (homesteads): the nucleated village
packed closer than a dispersed one, with no density threshold; the forms it takes.

Existing keys that are newly cited here: `dosojin-jawiki` (145), `sonraku-jawiki`, `jori-jawiki` and
`caoshi-zhwiki` (160), `shakkanho-jawiki` (110), and the canon `l7r-budgets` (110).

## Items

B19 KNOB - The village-form sections now cite what they assert:
- 170: a nucleated village packs closer than a dispersed one, but no definition of how dense it must be exists. A
  1956 survey counts houses within 200 m as one settlement. The built-share floor stays a labeled calibration, with
  an absence note: no built share, density or plot size was found.
- 160: the lump, levee-line and road-line forms are attested, as are the 1-cho jori grid (often tilted) and the
  long-strip allotment of a planned colony.
- 190: terrain naming is common but often uncertain; tani is western, ya and sawa eastern, and sawa means a valley
  in the east and a marsh in the west.
- 110: the headman's house was large because it lodged the lord's officials. The tax rice waited either in a
  village gogura or in the headman's own kura (two attested forms). The drawn size is a guess on the large side.

What this means for the kinds and maps:
- Village tier, NEW KNOB: roll where the tax rice waits. Either the headman's kura (as now), or a separate village
  gogura: one storehouse standing on its own among the houses, on dry-field ground or an empty house plot, never
  in the paddy. The headman keeps their own kura either way.
- Village tier, NEW RULE (170 spec): no house of a clustered village stands more than about 650 ft (200 m) from the
  next. A wider gap reads as two settlements.
- The headman's house, drawn at 92 by 56 ft, is four times a plain farmhouse's area. The attested ratio is 2 to 2.5
  times: 18 tsubo usual against 40-45 for the leading households, from an 1885 table. One measured shoya house of
  1805 is 12.5 by 6.5 ken (about 75 by 39 ft). The GM's canon says "a slightly larger headman's household". A
  headman's house of about 65-75 by 40 ft would be closer to the record. The size is left as a labeled guess;
  whether to change it is the orchestrator's (or the GM's) call.
- 160 corrections of wording only, nothing the generator draws:
  - The caoshi was a market quarter outside Chinese city walls that grew from the periodic rural market. It is not
    itself the "informal country market".
  - "Strip tenancy" is now "a planned new-field colony's strip allotment".
- 190: a sawa name is read as a valley or a marsh by region. No generator reads names.

B20 ACCURATE - 145: the village-entrance stone is attested: a dosojin, a stone monument or image, stands chiefly at
a village's entrances and exits (also passes, crossroads and bridge-feet). 050's dooryard-garden area stays SILENT:
the absence note is updated with the 2026-09-27 searches, and the 10-140 sq m band stays a labeled guess.
- For the maps: the village-entrance stone is drawn as a dosojin by the road where it enters the village. It is no
  longer a guess, and it is not on a farmstead. The garden band is unchanged.

## Left open, and why

- **homesteads/180 was NOT done.** `RESEARCH-CLAIMS.md` shows 271 V7 (clone diagram-research-1) claiming "edit 180".
  It stays thin (no source cited) until V7's work lands or V7 hands it back.
- **The plain farmhouse's size.** The same 1885 table (`oamishirasato-kaoku`) gives about 18 tsubo (about 60 sq m) as
  the usual main house. The drawn plain farmhouse is 46 by 28 ft, about 120 sq m, twice that. Its home is
  homesteads/130, which 271 V1 checked. For that owner: the drawn house is about double the one usual size read.
  This is one Kazusa district in 1885, so it is weak evidence.
- **The gogura knob is not encoded.** If a village storehouse program exists under buildings 240-640 (feature 267),
  its owner may want the siting quote in `gogura-kotobank` (the 地方凡例録 of 1794).
- **A second dosojin source.** `matsumoto-dosojin` is being defined, uncommitted, in `/diagram/.clones/diagram-shrines-2`
  (feature 272). It says "most dosojin are enshrined at a settlement's entrance". 145 could cite it once it lands. I
  did not copy it because it is uncommitted there.
- **A source only the GM can fetch.** The Kiyose museum's 「幕藩体制下の農民の居宅」 (house sizes by status, house plots
  and kitchen gardens) is entry 270 at the end of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`. It could settle
  050's area and 170's plot size.
- **Over the question-size cap (not touched here, all 269's).** After the sync-in merge, `scripts/check-question-size.py`
  reports homesteads/210 (20,107 bytes), vegetation/120 (20,095), water/070 (20,442) and water/270 (21,396). Each
  needs a split by the session that owns it.
- **The sync-in merge (110004e5).** It resolved conflicts in `_check_bundle.py` and its test, archetypes/170 (269 A1's
  checked line kept), and the glossary. Aizu, Fuyu and Diospyros kaki were renumbered to 12080-12100 under the lock.
  The Kanto and hydrosere duplicates were merged into main's files. 269's GM duplicate was dropped in favor of main's.
