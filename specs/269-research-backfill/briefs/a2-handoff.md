# 269 A2 handoff - archetypes: thin sections (B35)

Written 2026-09-27 by the A2 write session. Claims file checked first: nothing of B35 was claimed by another
session. (271 V5 owns archetypes 300-350 and edits 020, 080, 150, 160, 340; none of those were touched.)

## Questions new or changed

- SECTION=archetypes/040
- SECTION=archetypes/060
- SECTION=archetypes/070
- SECTION=archetypes/190
- SECTION=archetypes/250
- SECTION=archetypes/260

## New registry keys

- KEY=suido-ishizue-tanada
- KEY=suido-ishizue-yachida
- KEY=yachida-jawiki
- KEY=kotobank-yatoda
- KEY=titian-zhwiki
- KEY=shokukaku-suiden-jawiki
- KEY=kotobank-shuson
- KEY=kotobank-sanson
- KEY=kotobank-sonraku
- KEY=kotobank-ujigami
- KEY=tanba-2019-higashi-ashida

These existing entries got a longer "Used for" line only: `kato-1999-ittanbu-kukaku`, `aze-jawiki`, `tanada-jawiki`,
`kotobank-aze-sekai-daihyakka`.

## Outcomes

- B35 (040) ACCURATE - the hill terrace (a paddy on sloping ground, built up steep slopes in western Japan once the
  Edo plains were taken, small irregular hand-dug cells; in China mainly Guangxi and Yunnan) and the narrow valley
  paddy (long and narrow, found all over Japan, the typical medieval farm landscape) are both cited now, replacing
  "general reading". Where the brook runs in the chain stays an absence note. - Nothing changes in what is drawn;
  the two spec rules stand as written.
- B35 (060) ACCURATE for the ridge, SILENT for the walking bund - the dividing ridge is cited (two shaku in the 1869
  Inazato replanning; half a meter or less in Yayoi-Kofun small-plot paddies); a bund's extra width where it carries
  the path is still unread, so the walking bund's three feet stays a labeled GUESS, pointed at fields 260. The Song
  Taiping memorial on polder ridges (three to four chi high, four to five chi at the base) was found only in a search
  summary; its page timed out twice. - Nothing changes on the map.
- B35 (070) ACCURATE for the result, SILENT for the mechanics; CONTRADICTION-RESOLVED on one word - the record now
  cites that old bunds had no set shape or size, that most domain-era paddies were irregular plots of every size,
  that fields were shaped to the slope until postwar consolidation, and that bunds were re-plastered every year and
  set on the owners' boundary. Why a mud corner rounds and a run wanders (slump, walking, re-cutting) and the junction
  as the most worked point stay open absence notes. 070 called the 1.5 ft bund "an ordinary walking bund", which
  clashed with 060's three-foot walking bund; it is the DIVIDING bund (fields 260 draws `AZE_FT = 1.5` as that), and
  070 now says so. - Nothing changes in the geometry; only the wording.
- B35 (190 -> new 250) ACCURATE, share SILENT - the clustered village was the general form in Japan (dense in the
  Kinai and Setouchi, loose with wide lots and groves in the Kanto and Tohoku); the block village is the most general
  clustered form (a general ranking, not one made for Japan alone); the dispersed village is regional (Tonami, lower
  Oi, Sanuki, Izumo); medieval valleys held one or a few houses per valley paddy. No page gives a national count or
  share. 190 now points to 250. - The hamlet generator's single cluster is the general form, so no change. The place
  card may now call the clustered village the usual form (still no figure); that wording is the card owner's call.
- B35 (190 -> new 260) KNOB - there was a tutelary shrine in every village, with the village as its unit since Edo.
  Below the village, the Tanba 2019 article shows sections with a shrine of their own beside the whole community's
  (Higashi-Ashida: 14 shrines for about 180 households), and communities with none. No page speaks of the branch
  hamlet (edago) itself, and none gives a share, so the knob is unweighted. - The hamlet maps draw no shrine, on the
  GM's rule for what a hamlet has; 260 records that the history supports a per-hamlet roll between "own small
  shrine" and "none, shares the village's", and that the rule stands until the GM rules. **For the GM, via
  escalation-check:** should a hamlet roll a small shrine of its own? Canon was searched (`make canon
  TERMS="hamlet shrine|chinju|bund|terrace"`) and has nothing on it.

## Left open, and why

- **Sync-in conflicts.** A `scripts/sync-with-main.sh sync-in` was run mid-session to pick up `jinja-goshi-jawiki`
  (feature 272's key, on main, reserved from `diagram-shrines-2`). It conflicted: assembled pages, citations, the
  glossary assets, and a real add/add on `research/sources/010-works-cited/10080-buck-1930-farm-economy.html`. The
  merge was ABORTED (`git merge --abort`), leaving the clone exactly as it was. The orchestrator owns that merge.
- **`jinja-goshi-jawiki` not cited.** The source-reader read ja.wikipedia 神社合祀. Mito in 1830 destroyed 村々の小祠堂
  to leave one shrine a village; Choshu in 1842 did the same to 淫祠. Lived settlements and administrative villages
  did not always coincide, and the Meiji merger moved some ujigami far from their parishioners. This would
  strengthen 260's Edo-period reading. It is recorded as an HTML comment in 260's absence note; cite it once main
  is merged.
- **Kato p. 845 quote** (070 note `kato-1999-ittanbu-kukaku-2`) was transcribed by the source-reader from the scan
  image, because the text layer spaces every character. quote-check should read it against the scan.
- **economy.guoxue.com/?p=1951** (Sui-Yuan polder building, carrying the Song Taiping memorial's ridge figures)
  timed out on `make source-pages` and on WebFetch. It is a candidate for a later pass. It is a public page, so it
  was not put on TO-DOWNLOAD.
- `scripts/check-question-size.py` reports four questions over the cap that this group did not touch: homesteads
  210, vegetation 120, water 070 and water 270.
- No corrections are owed to sections owned by 265, 267 or 268.
