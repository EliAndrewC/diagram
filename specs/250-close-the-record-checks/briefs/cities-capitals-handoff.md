# Handoff - feature 250, page `cities/capitals` (T06), session 1 -> session 2

Source pages saved: `/tmp/l7r-check/cities-capitals-pages` (MANIFEST.txt). One `source-reader` ran over every item
(2026-09-27). No new registry keys; no canon terms were needed (no item is a setting claim).

## Changed questions (check each: quote-check + record-format)

- SECTION=040 - Hirosaki table cell rewritten: the stale "keep itself ~0.6 ha ... GUESS" (which contradicted the
  paragraph's 0.01 ha) replaced with the park's ~49 ha, the as-built 38.5 ha and the tenshu's 0.01 ha, cited to
  `hirosakipark-tenshu`; "every bailey plus all three moats" dropped (no page says the park area includes the moats);
  the note's gloss says so and that 0.01 ha is this page's arithmetic.
- SECTION=090 - "more than 110 of them at the early-1800s peak (... a GUESS ...)" removed: source-reader found it on
  neither `kurayashiki-jawiki` nor the JPX page; the cited 80 (1670s) / 125 (1840s) sentence already carries it.
- SECTION=150 - split (size cap); keeps the question, the China and Japan shape roster and the three Decisions; a
  pointer paragraph links to 155. The `chen-2016-song-yamen` note's gloss now says the Beijing Daily yamen is one Qing
  county yamen at Neixiang and "rectangular" is this page's reading of siheyuan.
- SECTION=155 - NEW (split from 150): why East Asian walls kept their corners (flanking, not rounding) and the two
  round forms (Shanghai 1553, the tulou). Notes moved: keep-enwiki, chinese-city-wall-enwiki, the absence note (key
  renamed to `why-do-east-asian-walls-keep-their-corners-and-where-were-the-round-ones`), shanghai-xiancheng-zhwiki,
  fujian-tulou-enwiki, fujian-tulou-zhwiki. Relies on 150 for the finding that big walls are rectangles or terrain
  loops; 150 relies on it for why ("A round keep would be reading European castle grammar").
- SECTION=210 - uncited Honcho-dori 13.8 m / Nihonbashi-dori 18.2 m / hirokoji-firebreak sentence removed
  (source-reader: NOT-FOUND on the ginza page; the entry itself said no page carries 13.8 m); the band now rests on
  `ginza-machidukuri-width` (7-8 ken, Ginza-dori the Tokaido) and 45 ft (~13.7 m) sits inside it; the "No page read
  carries the 13.8 m" sentence dropped with the figure.
- SECTION=330 - split (size cap) three ways; keeps the intro (pointers to 333 and 336), classes 1-2 (linear,
  sublinear), the oil-press and kiln-count guesses and the graveyard reconciliation. Item 86 sentence: "Buddhist"
  removed (source-reader: the page does not call the crematoria temple ones - the two it names are temples and were
  BARRED); `wugou-song-cremation-rujia` moved to sit on the Lin'an clause; the note's gloss corrected.
- SECTION=333 - NEW (split from 330): classes 3-4 (superlinear theaters and hanko; fixed pauper ground). Notes moved:
  dongjing-menghualu-juan2, edo-sanza-jawiki, japanknowledge-jishibai, hanko-jawiki-3, louzeyuan-zhwiki,
  kozukappara-jawiki. `hanko-jawiki` and `louzeyuan-zhwiki` were quoted but missing from 330's roster - now on 333's.
  Relies on 330 for the four-class frame.
- SECTION=336 - NEW (split from 330): dye works as a street, the mausoleum's lineage tier, the two official-kiln
  forms. Notes moved: nippon-com-kanda-konyacho, jiangning-zhizao-zhwiki, zuihoden-jawiki, liulichang-zhwiki,
  imari-okawachiyama. Relies on 330 only for the question it answers (how a capital's trades scale).

## FR-006 verdicts

- 43 (Ikeda ~520,000 koku, 040) - CONFIRMED: carries `himeji-han-jawiki` (source-reader READ; the 520,000 held
  1600-1613, which the gloss's "later far smaller" covers).
- 44 (wharf / western daimyo, 090) - CONFIRMED as rewritten: "By the 1670s eighty domains ... by the 1840s 125"
  carries `kurayashiki-jawiki` (READ).
- 45 (yamen rectangular and axial, 150) - CONFIRMED: carries `chen-2016-song-yamen` (with bjd-qing-yamen). OPEN:
  source-reader saw Chen 2016 only as SUMMARY-ONLY (swu.edu.cn 502 / timeout today); quote-check should retry it.
- 46 (Edo kami-yashiki, 220) - CONFIRMED: carries `wako226-hairyo-yashiki`. OPEN: the blog refused the fetch today
  (403/400; registry says READ 2026-09-14), so the table was seen as SUMMARY-ONLY; the figures match.
- 84 (Hirosaki tenshu 0.6 ha, 040) - CONFIRMED as rewritten (0.01 ha, `hirosakipark-tenshu`), and the table cell that
  still said 0.6 ha fixed to match (citation).
- 85 (no jokamachi built one, 210) - CONFIRMED as rewritten: the sentence carries `ginza-machidukuri-width`, whose
  gloss records that no page says it; the paragraph's other uncited figures removed.
- 86 (Song crematoria, 330) - CONFIRMED with a correction (citation, `wugou-song-cremation-rujia`): "Buddhist"
  dropped as unsupported.

## Open for session 2

- `entry-drift`: 150 and 330 lost body text to 155 / 333 / 336; run `scripts/_entry_owed.py` for any class whose
  `Entry:` names them.
- Pre-existing, not worked: the "Where the record is thinnest" guesses in 330 / 333 / 336 are labeled GUESS in prose
  without an absence note; the 330 roster's "(the counts - SUMMARY-ONLY)" Evidence comment was left as found.
