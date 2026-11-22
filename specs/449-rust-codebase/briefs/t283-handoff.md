# T283 handoff - session 1 (write), 2026-11-22

- SECTION=0028
- SECTION=0229
- SECTION=0217 (claimed too: it repeats `matsumoto-dosojin-2`'s Hanami reading, which T283.3 fixes)

## Items

- T283.1 DONE - `sugiura-1973-fuzoku-7#1`'s original now ends in the footnote's full-width period (．), not 。. The archived OCR (`/diagram/.specify/source-archive/47/47ff093d7fe7/20261002T122700Z/text.txt`, footnote 2), ends the footnote with a period; the paper's body ends its sentences with 。. The same note's second passage (p. 145, 本対象集落は，位置的に見て比較的隔絶し，) is now its own passage `#2`, joined with '; '.
- T283.2 DONE - the heading's bullet now opens with the paper's own p. 146 sentence: "The hamlets lie in mountain country, with a good deal of snow in winter." This is a new note, `sugiura-1973-fuzoku-8`: 「this district, being mountain country, has a good deal of snow in winter」 (original 「この地域は山間地のため，冬季の積雪はかなり多く」, cut before the footnote marker 2)). The Sabusawa figures follow it under `-7`. The bug fixed alongside: "5 km (~16,000 ft)" now reads "(~3 mi)".
- T283.3 DONE - 花見 is now Kemi in `matsumoto-dosojin-2`'s translation in 0028's notes, 0217's notes and drawing notes ("(of Kemi, in Azusagawa)"), and in 0217's prose ("the Kemi district"). The reading けみ is from Matsumoto city's page on 花見の御柱 (けみのおんばしら), https://www.city.matsumoto.nagano.jp/soshiki/134/3992.html, which a web search returned. That page was not fetched or cited, so no ledger outcome was recorded. No glossary term carries the name.
- T283.4 DONE - the separator is now '; ' in `ido-jawiki` (in both 0028 notes files) and in `nakasendoway-dosojin` (`." / "` became `."; "`). `sugiura-1973-fuzoku-4`'s `#1` had joined the caption, the header row and the B1 row with ' / ', repeating `#2` and the B1 row. `#1` now holds only the caption (「第5表 主屋類型による各機能別」, translated "Table 5: by each function, according to main-house type"), and the header row and B1 row each follow as their own passage after '; '. No quoted words changed. The same missing '; ' was also fixed, outside the items, in `hasa-jawiki` and `jawiki-yashikigami` in 0028's notes.
- T283.5 DONE - 0229's opening now reads "...for a parish of a few dozen to a couple of hundred households, and one such temple, a small shugen hall, kept a small house for its monk." The footnote is still `onga-choshi-jiin-4`.
- T283.6 DONE - the heading `<strong>The village's shrine is its parish temple.</strong>` already had its period inside the bold. The bullet body was what lacked a closing period after its link to 0236: one is added.

## Files

- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.notes.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.notes.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.originals.html
- research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.html
- research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.notes.html
- research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.drawing.notes.html
- research/questions/0229-village-temples-tera.html
- research/questions/0229-village-temples-tera.drawing.html
- specs/449-rust-codebase/briefs/t283-handoff.md

`make glossary` ran clean. The glossary files that were already modified in the clone belong to other builders, not to this session.

## Open

- The new note `sugiura-1973-fuzoku-8` and the split note `-7` are owed source-reader, quote-check and translation-check. The edited notes and prose of 0028, 0217 and 0229 are owed record-format and quote-check where `make record-owed` names them. Any `Research:` claim or pop-up citing 0028's heading on the snowy district, or 0217's Kemi bullet, is for the orchestrator to triage.
- `make record CHECK=1`, `make record`, `make glossary` and `make question-sizes` all ran clean; none of these three questions is over 20,000 bytes.
- The claims on 0028, 0217 and 0229 are released (`STATUS=done`).
## Checks (session 2)
CHECKED quote-check 0028 - r1: 9 READABLE, 7 VERBATIM, 8 SUPPORTS, 1 PARTIAL (jawiki-yashikigami); r2: 10 READABLE, 10 VERBATIM, 10 SUPPORTS - applied: heading now 'it often stood in a corner of the plot, and then often to the northwest or northeast'; sugiura-1973-fuzoku-7's passage #2 (supported nothing) dropped with its original
CHECKED quote-check 0217 - r1: 3 VERBATIM, 2 SUPPORTS, 1 PARTIAL; r2: 4 VERBATIM, 3 SUPPORTS, 1 PARTIAL - applied: the Kemi sentence names Kamitemachi, Nakamachi and Shimomachi; drawing page 'In Matsumoto most dosojin stand at a settlement's entrance'
CHECKED quote-check 0229 - r1: 8 VERBATIM, 8 SUPPORTS, 1 unfootnoted; r2: 9 VERBATIM, 9 SUPPORTS, 0 unfootnoted - applied: kasuga-mura-no-tera footnote on 'Some villages had a temple of their own, and some had several.'
CHECKED record-format 0028 - r1: 29/29 words, 0/0/0; r2: 0/0/0 plus a missing full stop - applied: full stop after the yashikigami block's link to 0219
CHECKED record-format 0217 - r1, r2, r3: 23/23 words, 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0229 - r1, r2: 23/23 words, 0/0/0 - nothing
CHECKED translation-check 0028 - r1: 5 pairs, 4 FAITHFUL, 1 LOOSE (sugiura-1973-fuzoku-7's glosses in round parentheses); r2: 4 FAITHFUL - applied: Sabusawa [寒風沢] and Showa 32 [1957]
CHECKED translation-check 0217 - 1 pair FAITHFUL - nothing
CHECKED source-reader 0028 hasa-jawiki, ido-jawiki (page and drawing), jawiki-yashikigami, nakasendoway-dosojin - all READ - nothing
CHECKED source-reader matsumoto-dosojin-2 (0028, 0217, 0217.drawing) - 6 READ, 1 READ with a dropped hedge, 1 CONTRADICTED - applied: the Nakamura sentence now ends 'and other stones' (など); the drawing's 'the one entrance counted has two' (the city's account describes five entrances) now reads 'a GUESS, stretched from the one entrance quoted here, which has two'. The reading Kemi for 花見 is confirmed on the PDF (けみ, line 46)
CHECKED source-reader sugiura-1973-fuzoku-4, -7, -8 - r1: 3 READ (scope: Table 5 runs on to p. 151); r2: 3 READ - applied: -4's gloss says 'header columns on p. 150'
CHECKED modal-triage (two rounds, the whole bundle, other builders' pages included) - recorded with make modal-triaged; TOUCHES on my pages: hamlet/privy, hamlet/storage-shed, hamlet/wood-shed (0028), sheet/hall-and-dwelling, sheet/the-monk-s-rooms (0229)
CHANGED research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html
CHANGED research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.notes.html
CHANGED research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.originals.html
CHANGED research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.html
CHANGED research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.drawing.html
CHANGED research/questions/0229-village-temples-tera.html
CHANGED specs/449-rust-codebase/briefs/t283-handoff.md
OPEN pop-ups the triage names TOUCHES, not checked here (the orchestrator's): hamlet/privy, hamlet/storage-shed, hamlet/wood-shed (modal-accuracy, -gaps, -references, page 0028); sheet/hall-and-dwelling (accuracy, gaps, references, depiction) and sheet/the-monk-s-rooms (accuracy, gaps, references), page 0229
OPEN outside the change, registry: 4960-jawiki-yashikigami 'Used for' says 'especially the NE 鬼門'; the page gives NW and NE together and calls NE-as-demon-gate a later overlay (source-reader's EDIT: 'often the NW or NE'). 7370-nakasendoway-dosojin calls the horse-headed Kannon 'the guardian of horses and travelers'; the page says only baggage horses. 7350-ido-jawiki 'Used for' omits the shared wells 0028 now cites it for. 7360-hasa-jawiki: the article's headword is 稲木, reached as 稲架
OPEN outside the change, 0028: sugiura-1973-fuzoku-4's ranking leaves out the p. 151 half of Table 5's B1 row (bath 0.39, storage and well sheds 0.32), which would need a p. 151 quote; sugiura-1973-fuzoku-5 lacks '; ' before 'Table 5, all-houses row', its passage #2 (4.38 / 4.57 a household) supports nothing, and its all-houses row's blank column needs naming off the scan; the Table 2/5 cells are images that can only be checked by eye
OPEN outside the change, 0217: jizo-bosatsu-jawiki (opening paragraph) is NOT-READABLE by the script, so it needs re-quoting or an absence note; the drawing notes' copy of matsumoto-dosojin-2 has '(of Kemi, in Azusagawa)', which the page's copy lacks; 'Kamitemachi' is the project's reading of 上手町, the same characters at Iriyamabe read わでまち (Wademachi); the tooltip for 'chō' in 'Kumano-chō' may show the unit
OPEN outside the change, 0229: '200 prayer households' in onga-choshi-jiin-4 may want a tooltip; homemate-shichido-garan-5's host gives 503 (archived copy VERBATIM), so it is a candidate for the download list
Session 2 ran make record CHECK=1, make record and make glossary clean; make record-owed names nothing of 0028/0217/0229 but the pop-ups above. Claims on 0028 and 0229 released (STATUS=done).
