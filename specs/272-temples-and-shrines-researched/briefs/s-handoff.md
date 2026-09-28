# Feature 272, group S - handoff from the write session (2026-09-27)

Written in `/diagram/.clones/diagram-shrines-1`. Every new citation was read by one `source-reader` over 17 claims
(17 READ, 0 NOT-FOUND, 0 CONTRADICTED), from `/tmp/l7r-check/272-s-pages/` (its `MANIFEST.txt`; the two PDFs and the
two fan-wiki pages were fetched with curl and saved as text there). Three of its caveats were applied: the
kotobank one-bay sentence is about Kamakura survivals only and is NOT used; the Kanazawa statement is the "received
view" (通説) and is written so; the Niiza lanterns now flank the Inari hall on the site. `make record`, `make
citations`, the four record tests (257 passed) and `check-question-size.py` (clean) were run. The record checks
(quote-check, record-format, source-applicability, entry-drift) were NOT run.

## Size splits (made because 090 and 124 were already over 20,000 bytes and 110, 120, 126 would have gone over)

Each split moved text and notes unchanged except for joining pointers; no class `Entry:` names any of these anchors
(grepped), so no modal pair is expected from the moves.

- 090 -> 092: the first-arch paragraph, the approach-length sentence and its note, and the two GM rulings of
  2026-07-27 (the threshold, the caption).
- 110 -> 112 (where the registers are kept) and 114 (China's village temples).
- 120 -> 121 (the dwelling, the one roof, Kaie-ji, China's Xietang hall).
- 124 -> 125 (why the registers may not give an Edo precinct).
- 126 -> 127 (the wealth-knob gifts: guardian dogs, lanterns, strength stones, sanctuary fence).

## Sections

- SECTION=religion-and-death/090
- SECTION=religion-and-death/092
- SECTION=religion-and-death/100
- SECTION=religion-and-death/110
- SECTION=religion-and-death/112
- SECTION=religion-and-death/114
- SECTION=religion-and-death/120
- SECTION=religion-and-death/121
- SECTION=religion-and-death/122
- SECTION=religion-and-death/124
- SECTION=religion-and-death/125
- SECTION=religion-and-death/126
- SECTION=religion-and-death/127
- SECTION=religion-and-death/128

## Registry keys (new)

- KEY=kotobank-chinju-no-mori
- KEY=sun-2014-zhejiang-village-entrances
- KEY=hie-jinja-kurihara-jawiki
- KEY=yuya-2007-kanazawa-shaso
- KEY=kotobank-bettoji
- KEY=l5r-fandom-seido
- KEY=l5r-fandom-shinden-tcg
- KEY=kotobank-nagarezukuri
- KEY=kotobank-shinboku
- KEY=shinboku-jawiki
- KEY=ubusuna-jinja-ameblo
- KEY=kawasaki-nagao-chozubachi
- KEY=niiza-ishigami-lantern
- KEY=jinjahoncho-sessha-massha
- KEY=kudamatsu-stone-torii
- KEY=hasegawa-2021-nagoya-precincts

`kuri-jawiki` (existing) gains a second note, `kuri-jawiki-2`, in 121.

## Items

- 090-1 SILENT - the two-regimes note gains the second search (the AIJ approach studies: part 1 read, parts 2 and 8 and the Kamo study listed for the GM) - no change to what a map draws.
- 090-2 SILENT - no page gives a first-to-second arch distance; Kasuga's own walks and Kashihara's 300 m whole approach recorded as searched - nothing changes.
- 090-3 SILENT - Manzo Inari's row still has no measured length; the note records that pages count the row from over 100 to about 200, so 114 is one visitor's count - the 12 ft pitch stays the GM's ruled guess; whoever owns its arithmetic may want to know the divisor is soft.
- 090-4 ACCURATE (corroboration) - a city inventory (Kudamatsu) lists its dated stone arches from 1679, the earliest built by the parish, every one a single gate; still no dated village row before 1868 - nothing changes (the absence of a pre-1868 village row is better supported).
- 090-5 SILENT (moved to 092 with its sentence) - no village approach length or innermost-arch distance found - nothing changes.
- 090 GUESS - unchanged: 12 ft inside the GM's band, bounded by Manzo's estimated row.
- 100-1 ACCURATE in part - a Japanese village's tutelary shrine ordinarily stands within the village or at its edge (Heibonsha, via kotobank); Zhejiang villages' temples stand at water mouths and entrances, read by a survey as "auspicious sites"; still unattested that the earth god's shrine took the water mouth as a rule or that it is the most strategic site, which stays this project's reading - nothing changes on the maps.
- 100-2 SILENT (on a ceiling) - a village shrine's own Edo halls are small (Hie Shrine, village shrine 1874: worship hall 3 by 2 bays, sanctuary 2 by 1, about 18 by 12 ft and 12 by 6 ft at 6-shaku bays); no source gives a village hall a ceiling, so 490 and 600 m2 stay calibration - nothing changes; the drawn 275 m2 one-roof building is larger than a shrine's own halls because it holds the dwelling, as the section already says.
- 110-1 ACCURATE in part - "many" provincial shrines had a bettō-ji (Heibonsha), and for Kanazawa the received view is that shrines served by lay priests were rare before 1868; no national or village count - the resident-monk form is better supported; nothing changes.
- 110-2 ACCURATE - the fan wiki's three sentences are now read (curl through the site's public API) and cited; the old absence note is gone - nothing changes on the maps.
- 120-1 SILENT (size) / ACCURATE (form) - ja.wikipedia now cited that an ordinary temple's kuri is often like an ordinary house; still no small kuri measured - the dwelling stays farmhouse form, size a guess.
- D50 SILENT - a small kuri's size: the one blocked source, the Miyashiro survey report, opened with curl; it is image-only drawings of a small subsidiary Hachiman sanctuary (about 0.8 by 0.7 m body), no kuri - the absence note (now in 121) says so.
- 120-2 SILENT - no second hall-and-kuri under one roof (more separate-building temples read) - nothing changes.
- 120-5 ACCURATE in part - nagare-zukuri is more than half (over 55%) of designated sanctuaries (Mypedia; older Heibonsha); no Edo village hall three bays square found (Himemiya's 1715 sanctuary is three bays wide, depth not given) - nothing changes.
- 120 GUESS - unchanged: a small kuri's size.
- D51 SILENT - a village shrine-temple's bell: new absence note in 120 recording both searches; the curl retries (the shrine-monk page, now opened; all five volumes of the Gunma prefectural shrine survey, opened and searched) name bell towers at a few surveyed shrines and count none; the heritage database needs its interactive search - the bell stays a knob.
- 122 SILENT - no general statement that a village shrine's whole precinct was unfenced; the Kōchi dissertation summary says nothing of fences, the gazetteers are images - no fence stays accurate as this page's reading; nothing changes.
- 124-3 SILENT - Baidu 村庙 still 403 under curl; the Fujian paper behind a login (TO-DOWNLOAD 247, 248 already list both) - nothing changes.
- 124-2 SILENT (the split) / ACCURATE (a comparison) - Nagoya's shrine precincts today (92 surveyed: 21 under 1,000 m2, 37 more under 2,500 m2) and Ishigami village's tutelary shrine at over 2,000 tsubo with its grove at the end of Meiji are cited in 124; no buildings/grove/open-ground split found - Hoshigaoka's 860 tsubo is inside what villages had; nothing changes.
- 124 GUESS x3 - unchanged (the wood's share; the place in the band).
- 126-1 ACCURATE (kind) - the roped sacred tree in a precinct is cited (Nipponica), and the shrine built where one stood (ja.wikipedia, disclosed as unsourced); how common, still a guess.
- 126-2 SILENT (pre-1868) - a parish's dated basin of 1828 (Kawasaki) and a shrine blog on many shrines today with no pavilion are cited; the unroofed form before 1868 stays a guess, now with modern support.
- 126-3 ACCURATE - the 1799 lanterns given by Ishigami village's parishioners are cited (now in 127); the absence note is gone.
- 126-5 SILENT (village facilities) / CONTRADICTION-RESOLVED - the Association of Shinto Shrines' page, now read, does NOT say subsidiary shrines are seen especially at high-ranking shrines (the old absence note's search-summary claim); it ties only the formal classing to them; 126's row is rewritten from the page - nothing changes (not drawn).
- 126-6 SILENT - village Bishamon precinct furniture (note now in 127) - tigers stay a guess at village scale.
- 126 GUESS x3 - unchanged in label (the tree's prevalence, the unroofed basin, the tigers' reach).
- 128 SILENT (China) - the Ming or Qing exemption still unreadable (Baidu 里社 403 under curl, no zh.wikipedia article, ctext refuses scripts); the Japanese exempt precinct was already cited (`jochi-jawiki`) and matches the canon (the country monk on tax-free land) - nothing changes.
- A133 A135 D49 D52 D53 D54 D55 D56 - confirmed: 100-128 still answer each row (the moved parts now in 092, 112, 114, 121, 125 and 127, pointed to from the sections the audit names); nothing the second search left as it was was changed.

## FR-007 - the drawn country shrine (the Hoshigaoka sheet and its village map)

FR-007: none. Checked against each finding:

- The 1679 single parish-built arch and the rest of 090 - no contradiction; the seven arches 12 ft apart stay the GM's ruling and particular.
- Hie's small halls - no contradiction; the 66 by 32 ft one-roof building holds the dwelling, and it sits in the attested one-roof band.
- The kuri like an ordinary house - no contradiction; this supports the dwelling ends.
- Nagoya's precincts and Ishigami's 2,000 tsubo - no contradiction; the open grove's 860 tsubo is within what village shrines had.
- The roped sacred tree - no contradiction. The definition says the tree is roped with a shimenawa. If the sheet's tree carries no rope mark, drawing one would follow the source; that is a drawing detail, not a contradiction.
- The unroofed basin - no contradiction; still a guess.
- No fence - no contradiction; the finding is unchanged.
- No temple of its own on the village - no contradiction; no finding bears on it.

## Corrections owed to other owners

None found.

## TO-DOWNLOAD entries appended

- 259 - AIJ, 参道空間の研究(その2) (1978): torii spacing, 090.
- 260 - AIJ, 参道空間の研究(その8) (1986): the same question.
- 261 - AIJ, 参道空間の構成に関する研究 (the Kamo shrines, 1989): approach length and innermost arch, 092.
- 262 - Hikino 2006, 鎮守のご本尊: who served a village shrine, 110.

Entry 1819, the L5R fan-wiki item, is now satisfied: both pages are read and cited through the site's API. The GM
need not fetch it.

## Left open, and why

- The Kōchi depopulated-shrines survey (Jinja Honcho 1977) is not online anywhere, and Fuyutsuki's book is a
  commercial book. Neither was listed, because neither is a page the GM can fetch; the 122 note records both.
- Gan Mantang's Fujian paper sits behind an institutional login (TO-DOWNLOAD 248 already holds it).
- A national survey of giant trees might count shrine sacred trees. It was not reached.
- The national heritage database's search for bell towers needs its interactive page. It is a search, not a work,
  so it was not listed.
- One edit on this page was made by a script rather than the Edit tool: the truncation that moved 090's last two
  paragraphs to 092. The result was checked by hand.
- `/tmp/272s-curl/` holds the curl copies: the five Gunma volumes, the Miyashiro report and the three repository
  PDFs. They are there if a check session wants them.
