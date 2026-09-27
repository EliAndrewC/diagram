# Feature 272 group T - handoff from session 1 (research and write), 2026-09-27

## Sections

- SECTION=religion-and-death/580
- SECTION=religion-and-death/590
- SECTION=religion-and-death/595
- SECTION=religion-and-death/020
- SECTION=religion-and-death/030

595 is new: 590 went over the 20,000-byte cap and was split along its topics (temples / the small shrine); the two point at each other.

## New registry keys

- KEY=zojoji-history
- KEY=zojoji-keidai
- KEY=kaneiji-jawiki
- KEY=chion-in-jawiki
- KEY=zuiryuji-jawiki
- KEY=daxiangguo-zhwiki
- KEY=kaiyuansi-quanzhou-zhwiki
- KEY=kanazawa-teramachidai-plan
- KEY=hirosaki-rekimachi-ch4
- KEY=zenringai-jawiki
- KEY=hirosaki-shinteramachi-matinami
- KEY=matsukura-2008-taito
- KEY=kanzaki-shrines-kushida
- KEY=wujunzhi-wikisource
- KEY=wujunzhi-12-wikisource
- KEY=wujunzhi-32-wikisource
- KEY=wujinzang-zhwiki
- KEY=izumo-kokuso-jawiki
- KEY=kamigamo-plan-kyoto
- KEY=kamigamo-shake-okeihan

Changed registry entry: `inexhaustible-treasuries` (a session comment only; it stays Not cited). The PDFs
(kanazawa-teramachidai-plan, hirosaki-rekimachi-ch4, matsukura-2008-taito) were saved with curl + pdftotext into
`/tmp/l7r-check/272-t-pages/30-*.txt`; `make source-pages` could not read them. A `sanjiejiao-enwiki` key was
reserved and not used (its sentence has the treasuries both destroyed and spared); the stub was deleted.

## Items

- FR-006 580 ACCURATE - every great temple read (Zojoji, Kan'ei-ji, Chion-in, Zuiryuji at Takaoka, Daxiangguo, Kaiyuan at Quanzhou) sets gates and main halls on one axis with a cloister, bell tower and sutra house to the sides, abbot's quarters behind, sub-temples as separate lots and mausolea outside, on 19 to 250 acres with main halls of about 45 by 35 m - for the maps: a spec rule for the great temple's plan (accurate) and its main hall at about 90 by 70 ft (guess); the setting's great complexes at ~73,000 sq ft (560) are now labeled a DEVIATION (less than a tenth of Quanzhou's temple), which no generator has to change, but 560's decision line could point at 580.
- FR-006 590 KNOB - a temple quarter meets its street in two attested forms (Kanazawa): the walled row (precincts side by side, wall and gate on the street) and the gate-land row (town houses on narrow deep lots along the street, each temple behind them at the end of an approach); precincts are sorted by sect, main halls face the street, graveyards at the back, town houses among the temples (Hirosaki), Edo temple-quarter blocks 7,300-9,000 m² - for the maps: a generator laying out a teramachi should roll the street form per quarter and pack two or three ~35,000 sq ft precincts to a block (this project's arithmetic).
- FR-006 595 ACCURATE (buildings) / SILENT (plot) - a small shrine is a sanctuary 1 ken square before a worship hall 3 by 2 ken, with at most a shrine office and a lesser shrine, or sits on a slice of a temple's precinct; small shrines' grounds run 250-500 m² in one Saga district, mostly hamlet shrines - for the maps: a town shrine plot of ~3,500 sq ft is a labeled guess.
- FR-001 020 CONTRADICTION-RESOLVED - the "Three Officials temples filed under Altars and Shrines" claim rested on memory and is gone (its glossary term `0680-Three Officials.json`, whose definition repeated it, was deleted as unused); the Song gazetteer of Suzhou (1192) is cited instead: cults' shrines, Daoist abbeys, the temples inside the wall (thirty, this project's count) and those outside each under its own heading; a county seat's count stays SILENT with both searches - for the maps: nothing.
- FR-001 030 (Inexhaustible Treasuries, notes 1 and 2) CONTRADICTION-RESOLVED - "interest-earning endowments ... liquidated in 713 as fraudulent banking" is rewritten to what is readable: donated wealth lent out at a profit, the Chang'an treasury destroyed on Xuanzong's order in 713 (wujinzang-zhwiki); the motive is an absence note with both searches and a TO-DOWNLOAD entry - for the maps: nothing.
- FR-001 030 (generations, note 3) ACCURATE - the Izumo shrine's chief priesthood is counted past eighty generations, father to son - for the maps: nothing.
- FR-001 030 (the clergy house, note 4) CONTRADICTION-RESOLVED - the record said the eye could not pick temple families out "because in reality it could not"; Kamigamo's shrine-priest houses were one-story, gabled, walled with a gate, unlike the town houses beside them, so the identical monk house is now labeled a DEVIATION; a Chinese married priest's or a Japanese temple family's house stays SILENT - for the maps: the drawn monk_house is unchanged; drawing it walled with a gate would be the historically attested form for a Japanese priest family, a GM choice.

## FR-007 (the Hoshigaoka country-shrine sheet and village)

- FR-007: 595's small shrines (a sanctuary 1 ken square before a worship hall 3 by 2 ken, some 18 by 12 ft) - contradicts the sheet's 66 by 32 ft one-roof building only if that building is read as the shrine's worship hall; as the villagers' hall with the monk's kitchen and dwelling nothing read sizes it, and the Kanzaki shrines keep no dwelling. Worth the orchestrator's look, not a clear contradiction.
- FR-007: none for 580, 590, 020 and 030 (walled temple precincts and walled priest houses are temples' and a great shrine's priest quarter, not a village shrine's precinct; Hoshigaoka draws no temple).

## TO-DOWNLOAD entries appended

- 272. Neil Schmid, "Giving while keeping" (2019) - the motive of the 713 order (030).
- 273. 御府内寺社備考 (NDL) - a single ordinary Edo temple's plot and a town ward shrine's ground (590, 595).

## Owed to other owners

- religion-and-death 040 (R2): its absence note (the same text as 030's note 4, "no page read says a clergy household's dwelling was built like a commoner's") is answered by kamigamo-plan-kyoto and kamigamo-shake-okeihan: Kamigamo's priest-family houses were one-story, gabled and tiled, walled with a gate, unlike the town houses beside them; 040 should cite them and relabel the identical house a deviation, as 030 now does.
- religion-and-death 560 (R4, this clone): the ~73,000 sq ft great complex is now called a deviation in 580; 560's decision line could point at 580.
- religion-and-death 010 (B37): `daxiangguo-zhwiki` now carries the 540 mu / 64 cloisters / several thousand monks passage in Chinese, beside 010's `daxiangguo-enwiki`.

## Left open

- No provincial Japanese great temple's precinct area, no single temple's frontage and depth, no Edo town ward shrine's ground and no Chinese lane temple's size were found (absence notes in 580, 590, 595).
- The record checks (quote-check, record-format, source-applicability on the 20 new write-ups, entry-drift if any) were not run, per the brief.
