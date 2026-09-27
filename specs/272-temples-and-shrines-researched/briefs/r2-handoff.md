# Handoff - feature 272, group R2 (town monasteries, town and city shrines), session 1: research and write

Written 2026-09-27. Nothing here has been through `quote-check`, `record-format` or `source-applicability` yet; one
`source-reader` pass returned all 21 claims READ against `/tmp/l7r-check/272-r2-pages` (its MANIFEST.txt; the Shinoda
PDF's text was added there by hand from `pdftotext`, two columns interleaved).

## Sections

- SECTION=religion-and-death/450
- SECTION=religion-and-death/460
- SECTION=religion-and-death/470
- SECTION=religion-and-death/040
- SECTION=religion-and-death/210

## New registry keys

- KEY=ranzan-temple-register
- KEY=ranzan-kinsenji
- KEY=ranzan-koshoji
- KEY=ranzan-soshinji
- KEY=ranzan-anyoji
- KEY=ranzan-kamagata-hachiman
- KEY=jinja-goshi-jawiki
- KEY=amagasaki-teramachi
- KEY=miyazu-teramachi
- KEY=eijuji-shinshiro
- KEY=licheng-chenghuangmiao-zhwiki
- KEY=sanyuan-chenghuangmiao-zhwiki
- KEY=zhangde-chenghuangmiao-zhwiki
- KEY=pingyao-gucheng-zhwiki
- KEY=bicchu-sojagu-jawiki
- KEY=shinoda-2004-edo-shrines
- KEY=kamigamo-shake-plan

Existing keys cited anew (new note keys on the page): hongwu-emperor-enwiki-2, lin-2001-miaohui-4,
pingyao-chenghuangmiao-2, sano-shrine-gazetteer-5. New glossary terms: gōsha, sōchinju.

## Items

- B96 D66 ACCURATE - 450: canon gives a county town a monastery per patron Fortune (a preceptor per Order); history kept more (19 temples in 14 old villages of one Saitama district; castle towns 12-20) and the Ming law fewer (one monastery a county), and a temple's head priest and family lived in its kuri inside the precinct, monks in training in a dormitory; the head count is SILENT (absence note) - maps: the town's two monasteries stay (recorded as a canon deviation); the household is implied inside the precinct.
- B97 B98 D65 KNOB - 460: precinct 285-1,944 tsubo (median 462, about 16,400 sq ft), main hall 4-10.5 ken across (median 7, about 42 ft), with kuri, bell tower about 1 ken square, storehouse, gates on the axis; the boundary (wall, fence or hedge) is SILENT; where it stands is a knob between EDGE (Japanese temple quarter at the town's rim) and AXIAL (Chinese county seat, inside, either side of the main street) - maps: a town generator rolls size within the bands and the seat per seed; the boundary is drawn as a guess; `The rule the map follows` in 460 is the spec.
- B101 C152 ACCURATE - 470: a real county town kept a district shrine (gōsha: one per ~20 villages / ~1,000 households by the 1871 rule; 1897 precinct floor 500 tsubo against a village's 300; halls village-sized, with a gate and lesser shrines; one example 3,373 tsubo), and a city a principal shrine (Edo's Sannō sōchinju on raised ground, moved outward; a province's sōja at its capital; a Chinese City God temple at every seat of government, 1,892-13,390 m² at county seats) - maps: nothing drawn, since the setting's tier ladder names no town shrine and no city principal shrine and the canon has no City God (recorded as a deviation). **For the GM:** whether a town or a city should carry a shrine of its own is the one open question here; the canon is silent on it rather than against it.
- C147 D70 CONTRADICTION-RESOLVED - 040: its "the eye could not pick the temple families out, because in reality it could not" was wrong: a Japanese temple's married head priest lived inside the precinct in the kuri, and where priest families lived outside (Kamigamo's shake-machi) their houses were a distinct walled, gated style - maps: none; the identical-house rule stands and is now labeled a deviation. The 040 absence note (in `readers/272-temple-absences.md`) is replaced by the two citations, its old search kept in an HTML comment; the T reader's part C was not on disk, so this session ran the second search itself (the Kamigamo preservation plan was the find).

## FR-007 (the drawn country shrine)

- FR-007: the Hiki temple register's nearly-one-temple-per-village (450) - contradicts the Hoshigaoka village carrying no temple of its own, as HISTORY only; the setting's canon gives the village a shrine whose monk does the temple's work, so nothing drawn should change.
- FR-007: none for everything else (the temple precinct, the kuri inside it, the town and city shrine findings do not touch a country shrine; the kuri finding agrees with the sheet's monk's dwelling at the hall).

## Owed to other owners

- religion-and-death/170 (feature 269, `/diagram/.clones/diagram-supplemental`): the Hiki register enters Kinsenji's graveyard (4 se 10 bu, about 130 tsubo) among the land held OUTSIDE its precinct, at another named place (立山) of its village from the temple (大堂); 170's rule puts a town monastery's graveyard in its precinct. Cite `ranzan-kinsenji` (see 460's note `ranzan-kinsenji-3`) and consider a knob (in the precinct / held apart) or a disclosed deviation.
- religion-and-death/210 is edited here (pointers to 450-470 in its town sentence, and the sentence that neither tier has a shrine of its own); group R3 edits it next.
- Group R3 (the village temple): the Hiki temple register (`ranzan-temple-register` and the per-temple keys) is a village-temple source; cite it rather than re-reading.

## TO-DOWNLOAD

- 258. Goossaert 2000, "Counting the Monks" (HAL-SHS bot check; academia.edu and ResearchGate 403) - the Chinese clergy head count in 450.

The other blocked sources in the reader's list opened with curl and `pdftotext` (NILIM ks072307, the Maruoka register, the Lanzhou paper, the Edo religious-space paper, Shinoda 2004); only Shinoda was used - the others gave nothing quotable on these items (the Maruoka register's text layer is jumbled; its Edo temple-site areas would be worth a later reading).

## An engine fix made here (constitution XIV)

`make reserve` hands out glossary prefixes past 9990 (the host ledger is at 11,440), and `glossary_source.py`
refused any prefix not exactly four digits and read files in TEXT order ("11310" before "1410"). Fixed: at least
four digits, read in NUMERIC order (`_order`), with a test in `tests/interactive/test_glossary_source.py`. This makes
the landing GATED (engine code); `make quick` is green. Every clone reserving a glossary term hits the same refusal
until this lands.
