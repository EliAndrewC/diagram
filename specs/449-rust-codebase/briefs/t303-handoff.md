# T303 handoff - session 1 (write)

- SECTION=0123
- T303.1 DONE - the bullet "No page we read puts a seat's arms in its barracks, or says what doors an armory had." now says: Kaibara's gun store is a room of the gate range; at Nirayama, in the house of the Egawa family, the Nirayama intendants, the 武器庫 is a building of its own, late Edo, 5.4 by 3.7 m, gabled, pantiled, entered at its gable end under a pent roof, its place in the compound unsaid; at Hamamashike, a Shonai guard post in Ezo finished in 1860, a city leaflet names a 武器蔵 among the storehouses without placing it, and the old plans put the powder store on the hill behind. The heading stands: the doors clause is answered only in part ("the Nirayama entry says only that its store is entered at the gable end"). The absence note `armory-barracks-doors-absence` now covers the three new pages too (its search comment and its sentence).
- T303.2 DONE - the Jiexiu heading now says "...and in a later account in an armory by its side gates." (was "an armory of its own"); the body names the 武庫, puts it across from the gatekeepers', runners' and jailers' rooms on the west, and says the text does not say whether it was a building or a room. The next bullet's "a store of their own" now reads "an armory listed by the side gates".

## New registry keys

- `egawa-nirayama-bukiko-bunka` (37070) - Cultural Heritage Online, https://bunka.nii.ac.jp/heritages/detail/122177 ; evidence late Edo; limit: an intendant's office, not a domain seat (the 1692 date in its write-up rests on the uncited `31710-touken-world-jinya`).
- `hamamashike-jinya-site-bunka` (37080) - designation text, https://online.bunka.go.jp/db/heritages/detail/189992 ; evidence 1859-1868 (layout from handed-down drawings); limit: a frontier guard post; names no weapons store.
- `ishikari-hamamashike-jinya-file` (37090) - City of Ishikari leaflet (2009), https://www.city.ishikari.hokkaido.jp/_res/projects/default_project/_page_/001/004/676/1004676_010.pdf ; limit: a frontier guard post, a leaflet citing no source. `make source-pages` cannot read this PDF's text ("NOT-CHECKED - a PDF"); it was read with curl + pdftotext, and its quote is taken from within one line of the text layer. It archived with `make source-outcome OUTCOME=cited:...`; the check session may need the archived copy for quote-check.
- All three tagged period=premodern; region=japan; kind=institutional; all three recorded `cited:` on the ledger and archived.

## Files

- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.originals.html (written by `make record`, moving the new originals)
- research/sources/010-works-cited/37070-egawa-nirayama-bukiko-bunka.html (new)
- research/sources/010-works-cited/37080-hamamashike-jinya-site-bunka.html (new)
- research/sources/010-works-cited/37090-ishikari-hamamashike-jinya-file.html (new)
- research/archive/19/19b18b44c4b4.json, research/archive/41/412065f054e4.json, research/archive/cb/cb5a5efc78e2.json (new, archived copies of the three cited pages)
- research/source-attempts.jsonl (ledger lines appended by the tools)
- l7r/diagram/interactive/assets/glossary.json (reassembled by `make glossary`; it was already modified by other builders, so its diff is not all mine)
- specs/449-rust-codebase/briefs/t303-handoff.md (this file)

## Left open

- The "Nirayama intendants" wording rests on the title of a related-items link on the Cultural Heritage Online page (「韮山代官江川家関係資料」), a weak anchor quote-check may reject; if it does, drop "the Nirayama intendants" from the bullet (the intendant's-office limit stays in the 37070 write-up).
- "Ezo" has no glossary term (pent roof, pantile, gable end and intendant do); record-format may ask for one or a plain gloss.

- How common a separate weapons store was stays SILENT (2 of 31 職方典 entries name one); not written into the page, as no item asked for it.
- Any `Research:` claim or pop-up echoing "an armory of its own" or "the Japanese gun store we read of" is the orchestrator's to restate.
- Owed checks for the next session: quote-check, translation-check (new originals), source-reader (three new notes), source-applicability (three new write-ups), record-format; the 0123 claim is kept.
## Check session (T303 session 2)
CHECKED quote-check 0123 (9 owed notes, 26 footnotes) - r1: 22 VERBATIM, 21 SUPPORTS, 1 PARTIAL (egawa: Nirayama in Izu and 武器庫 unquoted; the Nirayama intendants was SUPPORTED) - applied by hand: the note now quotes the entry's title and address; r2: egawa VERBATIM, SUPPORTS
CHECKED record-format 0123 - r1: 23/23 words, 4/4 candidates, 1 VOCABULARY (Ezo) - applied: glossary term 28290-Ezo; r2: 25/25 words, 0 findings - nothing
CHECKED translation-check 0123 egawa/hamamashike/ishikari - r1: 9 pairs, 6 FAITHFUL, 3 LOOSE (hamamashike 等 dropped; hamamashike decided-to; ishikari every kind/first among them) - applied (3 EDITs); r2: egawa's 2 new pairs FAITHFUL - nothing
CHECKED source-reader 0123#egawa-nirayama-bukiko-bunka - r1: 5 READ, 1 NOT-FOUND (registry 1692 date) - fixed by the applicability EDIT; r2: 8 READ, 1 NOT-FOUND (registry background unsourced) - applied 1 EDIT (says-none-of-this made exact)
CHECKED source-reader 0123#hamamashike-jinya-site-bunka - 8 READ - nothing
CHECKED source-reader 0123#ishikari-hamamashike-jinya-file - 6 READ, 1 CONTRADICTED (registry: cites no source; it lists 浜益村史 1980) - fixed by the applicability EDIT (same sentence)
CHECKED source-applicability egawa-nirayama-bukiko-bunka - r1: WITH-LIMITS, limits MISSING - applied 1 EDIT; r2: WITH-LIMITS, limits HONEST, tags RIGHT - its 2 sourcing EDITs NOT applied (see OPEN)
CHECKED source-applicability hamamashike-jinya-site-bunka - r1: WITH-LIMITS, limits OVERSTATED (garrison, not a settled seat) - applied 2 EDITs; then 'people' reworded by hand (house style); r2: WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED source-applicability ishikari-hamamashike-jinya-file - WITH-LIMITS, limits MISSING one (garrison scale), OVERSTATED two (not a settled seat; cites no source) - applied 2 EDITs
APPLICABILITY egawa-nirayama-bukiko-bunka - APPLICABLE-WITH-LIMITS - one intendant's house-office, not a domain seat or a county yamen: fits a county magistracy only by analogy (a hereditary family's house-office over several provinces vs an appointed official in a state-built yamen over one county); no place in the compound, contents or doors beyond the gable-end entry; the background (hereditary, shogunal land) rests on no cited source
APPLICABILITY hamamashike-jinya-site-bunka - APPLICABLE-WITH-LIMITS - the Shonai domain's main seat on the Ezo frontier (1859-1868) with a county magistrate, a daikan and a magistrate's office, but fortified (earthwork, squared gate, palisades, moat) as an ordinary magistracy was not, soldiers among its 193, short-lived; layout from old drawings, not excavation; names no weapons store, no sizes; nuance unfixed: headed by a deputy commissioner over other posts, a level above a county seat
APPLICABILITY ishikari-hamamashike-jinya-file - APPLICABLE-WITH-LIMITS - the same post as a magistrate's seat governing settlers, but its arms served a garrison of over 200 retainers posted against Russia, larger and more military than a county compound: shows that a seat kept a separate weapons store, not how a civil magistracy stocked or placed arms; one listed reference not tied to the building list; no place, size or build
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.notes.html
CHANGED research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.originals.html (by make record)
CHANGED research/sources/010-works-cited/37070-egawa-nirayama-bukiko-bunka.html
CHANGED research/sources/010-works-cited/37080-hamamashike-jinya-site-bunka.html
CHANGED research/sources/010-works-cited/37090-ishikari-hamamashike-jinya-file.html
CHANGED l7r/diagram/interactive/assets/glossary/28290-Ezo.json (new)
CHANGED l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt (rebuilt by make glossary / make record; shared, not all mine)
CHANGED dev/review-ledger.md and the record-checked ledger (by make record-checked; shared)
OPEN egawa sourcing: applicability r2 proposed citing Cultural Heritage Online's Historic Site entry 韮山役所跡 https://online.bunka.go.jp/heritages/detail/192622 (hereditary intendants from 1596; the Nirayama office governed Izu and Suruga, the Edo office Musashi, Sagami and Kai; the office grounds hold the Egawa house) and restating 'several provinces' as 'two provinces, half of an intendancy of five' - needs a new registry key, not done here; source-reader's NOT-FOUND on the write-up's background stands until then
OPEN 'guard post' wording: both Hamamashike verdicts found an administrative seat (county magistrate, magistrate's office, settlers); 0123's armory bullet and armory-barracks-doors-absence still say 'guard post' - orchestrator's to restate (record-format has had two rounds)
OPEN re-stamped units: record-checked BUNDLE= stamped every unit in each bundle - all 19 quote-check units of 0123 (judged this session) and all 10 translation units, of which the 7 already answered at start (gujin-tushu-jicheng-juan338-zhwikisource-2/-3/-4, jiandao-zdic, neixiang-xianya-zhwiki-2, neixiang-yamen-4, tamba-kashiwara-jinya-2) were NOT re-judged this session
OPEN pop-ups: none owed only because 0123 moved, so no modal-triage ran; modal-depiction:sheet/main-gate stays owed (0093 and its own change too); sheet/armory held by its ruling
OPEN quote-check r2 OUTSIDE THE CHANGE: 'regulation fixed which way the office faced' - r1 judged its footnote neixiang-xianya-zhwiki SUPPORTS, so likely settled
OPEN the new glossary term Ezo owes make page-check for whoever lands this
OPEN ishikari note quote stops before 鎮守など (source-reader, no EDIT, nothing misstated)
DONE make record CHECK=1 clean; make record-owed names none of 0123/egawa/hamamashike/ishikari; 0123 under 20,000 bytes; claim released
