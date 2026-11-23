# T342a handoff - session 1: write (feature 449 T343, T344, T349)

- SECTION=0116 0101 0093 0123

- A1 DONE - 0116 drawing page: "Our maps keep a plaster storehouse (kura) about 6-10 ft from the buildings round it, as a fire gap." Its body now adds that the gap does not bind a privy built onto a building's end, which may back a kura or a granary, this project's GUESS on the record's silence. The footnote is a new absence note, `privy-storehouse-absence` ("no publicly readable source"). Its comment lists the T331 pass's searches and names the Zhaijing (宅經) passage without citing it (I did not read the page or reserve a key). Its visible sentence says that none of the searched plans, inventories or rules puts a privy and a storehouse together with a distance or a reason. A comment records the county sheet's garrison privy, which backs its granary 0.5 ft off.
- A2 DONE - 0101 drawing page: a new placement bullet sits before the hatch bullet: "A privy built onto a building's end may back a storehouse or a granary - a GUESS." Its body says no page we read keeps a privy or its cesspit off a storehouse's wall, and it links to 0116's drawing page. Its footnote repeats the same `privy-storehouse-absence` note, word for word, in 0101's drawing notes file.
- A3 DONE - 0101 findings: the heading is now "A local farmer came regularly with a cart to buy up a communal toilet's night soil." The body says it is one case and does not say every collector was a farmer or came with a cart. The note is unchanged.
- A4 DONE - 0116 drawing page: the sentence now reads "Our earlier plans scattered separate labeled buildings with loose ground between them; our maps now close up that loose ground and leave the rest open." I dropped "a dozen". A grounds comment names the 2026-07 packing sweep (Hayakawa's west column), feature 007 (Ochiba's cell and barracks) and research 190. Passage #2 of `takayama-jinya-jawiki-6` (the storehouse list) is dropped from both notes files and both originals files. Neither citing sentence is about the surviving buildings. The gloss now reads "(the sentence ... The hearing court (shirasu) also cites)".
- A5 DONE - 0123 findings, Pingyao bullet: the first mention "imperial encyclopedia" now links to the 第0338卷 wikisource page the `gujin-tushu-jicheng-juan338-zhwikisource` note links, followed by "the Gujin tushu jicheng (古今圖書集成)".
- A6 DONE - 0093 drawing page, "How wide is each form drawn?": a one-bay gate's posts are drawn outside the passage. The hand-drawn plans draw them about 2 ft square. The generated plans draw them 2 ft along the wall and lengthen them to about 4.3 ft across it, so they stand past the wall's ink on both faces. That is a map drawing convention. A new sentence says a side gate's posts are drawn as dark blocks about 2 to 2.7 ft along the wall and about 4 ft across it, standing past the wall's ink on both faces, larger than a post would be so they read at the plan's scale. That is also a convention: no page we read measures a side gate's post. A comment holds the px measurements. The 16 by 14 px south service gates are not stated as a side gate's size. The Evidence comment gained a "convention (...)" entry to match.

## Files

- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html
- research/questions/0101-privies-setchin.drawing.html
- research/questions/0101-privies-setchin.drawing.notes.html
- research/questions/0101-privies-setchin.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.notes.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.originals.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.notes.html
- research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.originals.html
- research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html
- specs/449-rust-codebase/briefs/t342a-handoff.md

## Open

- `make record CHECK=1`, `make record`, `make glossary` and `make question-sizes` all exit 0. question-sizes lists only 0059 and 0009 over 20,000 bytes; neither is mine.
- `l7r/diagram/interactive/assets/modals/sheet/inner-court.md` shows as modified in the clone. I did not edit it; it is another builder's work.
- The new sentences in A1, A2 and A6 that say no page we read measures or places something carry an absence note in A1 and A2. A6's has no note, following the page's existing unfootnoted "no page we read measures a one-bay gate's pillar". The checks may ask for one.
## Checks (session 2)
CHECKED quote-check 0093.drawing (bunka-adachi/omi/fujioka-yakuimon, bunka-saito-nagayamon, ken-to-feet-grounds) - 4 VERBATIM, 1 GROUNDS, 1 unfootnoted - applied: the side-gate clause "larger than a post would be, so they read" now "drawn large so they read at the plan's scale"
CHECKED quote-check 0101 (guernica-night-soil-2, privy-storehouse-absence) - 8 VERBATIM, 8 SUPPORTS, 1 absence, 0 unfootnoted - nothing
CHECKED quote-check 0116 (takayama-jinya-jawiki-6 x2, how-our-maps-size-a-compound-and-its-buildings-2, privy-storehouse-absence) - 2 VERBATIM, 2 SUPPORTS, 2 absence - nothing
CHECKED quote-check 0123 (gujin-tushu-jicheng-juan338-zhwikisource) - 10 VERBATIM, 10 SUPPORTS, 2 absence - nothing
CHECKED source-reader 0116 + 0116.drawing takayama-jinya-jawiki-6 - 2 READ - nothing
CHECKED record-format 0093 - 0/0/0 - nothing; round 2 after quote-check's fix - 0/0/0 - nothing
CHECKED record-format 0101 - 2 VOCABULARY - applied: privy-storehouse-absence (0101.drawing.notes) "house-siting plans" now "house-siting plans (kaso-zu)"; the other (a Kōka shunjū glossary term for tajima-2007-night-soil) is OPEN below
CHECKED record-format 0116 - 1 HISTORY - applied: "Our earlier plans scattered ...; our maps now close up" now "Our maps do not scatter separate labeled buildings with loose ground between them: they close up that loose ground and leave the rest open."
CHECKED record-format 0123 - 0/0/0 - nothing
CHECKED modal-triage (two rounds, the second after this session's edits moved 0093/0101/0116 drawing pages) - round 1 19 of 40 sent on, round 2 9 of 18 sent on; the rest answered untouched
CHANGED research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html
CHANGED research/questions/0101-privies-setchin.drawing.notes.html
CHANGED research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html
OPEN pop-ups the triage named, not checked here (another builder's): modal-depiction main-gate, latrine, inner-court, storehouse, granary, tax-archive, outer-court, office-hall, residence, rear-yard; modal-accuracy/gaps/references choice/town_nearness--near, choice/town_nearness--far, sheet/armory
OPEN pop-ups owed before this session (their About/Depiction changed, predating it): day-office, genkan, inner-court, latrine, official-study, side-gate, writing-rooms (modal-form/research/depiction as record-owed batches them)
OPEN privy-storehouse-absence is no longer word for word in its two copies: 0101's now reads "house-siting plans (kaso-zu)", 0116's does not (0116's record-format ruled "house-siting" plain English); left alone so as not to re-owe 0116's checks
OPEN OUTSIDE THE CHANGE (record-format 0101): the tajima-2007-night-soil note names "Kôka Shunjû" with no glossary term; the agent's draft definition (a 1707 Kaga farming manual by Tsuchiya Matasaburō) is from its own knowledge and needs a source before it is written
OPEN OUTSIDE THE CHANGE (quote-check 0093): the main page's "How wide was a one-bay gate" says "about 6 to 9 ft" for the three examples the drawing page now gives as "6 to 8.5 ft" (2.6 m is 8.5 ft)
OPEN OUTSIDE THE CHANGE (quote-check 0116): the how-our-maps-size-a-compound-and-its-buildings-2 absence note says what a named page does say (CLAIM-FROM-UNREAD) and names the jawiki storehouse, jin'ya and fire-brigade articles without links
OPEN OUTSIDE THE CHANGE (source-reader): registry 5220-takayama-jinya-jawiki says "the 1816 rebuild of the office block as one range" (the source says 部分, parts) and still lists the storehouse rows under "Used for", right only if another note still quotes that passage
