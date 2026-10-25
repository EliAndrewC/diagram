# Brief - feature 418, the Hoei and Shotoku market rates and Canton's cash. Session 1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#13 (verbatim in `specs/418-hoei-rates-and-canton-cash/request.md`)
for the market rates of 1706-1718 - monme of silver a ryo of gold, and mon a monme (or kanmon a ryo) - to build an era for
1712-1718, and for Canton's own cash rate in the 1830s. Your pass: `specs/418-hoei-rates-and-canton-cash/passes/rates.md`
(leads, not citations: read each passage on its page before citing it; where it does not read as the pass says, write what the
page says, or SILENT). Page images of Kusama's 『三貨図彙』 (NDL pid 1279564, internet-public; NDL's machine text is refused):
`/diagram/.clones/diagram-money-pages/.git/418-pass/418img/1279564-k409.png` to `-k419.png` (printed pp. 803-823), for `IMAGES=`
and for your own reading; the *Chinese Repository* texts in `.../418-pass/418cr/` and `418cr3/`. Quote as printed; a garbled
character bracketed.

**Already in the record - name by file, do not repeat:** 0287 (how much silver was a monme, a ryo and a bu, coinage by coinage:
the coinages' fineness, the 1700 and later rates, its "1706-1721 mixed coins, not converted"); 0277 (copper in silver, the
Osaka and Edo series); 0289 (the tael, the string of cash and the dollar, the Canton dollar at 0.71-0.75 tael); 0295 if it has
landed in your clone (feature 416's Edo three monies) - do not edit it.

## Your items

1. **0287: the market rates of 1705-1719.** A table, a row a year, from Kusama: the gold rate as he gives it (monme a ryo, the
   gold named as he names it - Genroku; Keicho or Genroku; Kenji beside it from 1710; Keicho or new from 1718), the copper rate
   (monme a kanmon), and the silver each is quoted in (Genroku to 1706; Hoei Futatsuho from 1706-1707 to 1713; "current silver",
   Eiji, Mitsuho and Yotsuho together, 1714-1717; new silver from the eleventh month of 1718); a year with a second dated rate
   (1707 autumn, 1712 tenth month, 1713 intercalary fifth month, 1714 fifth-sixth and twelfth months) gives it too. Mon a monme
   is this project's arithmetic (1,000 / monme a kanmon), labeled so. 1715 and 1716: SILENT in Kusama.
   - Which silver chiefly passed: Kusama's own words (p. 804 for 1706, p. 816 for 1714, p. 820 for 1717), quoted with their
     translation, ATTESTED. A separate market rate for Eiji, Mitsuho or Yotsuho: NOT ATTESTED (the market quoted them as one).
   - The law's split, not the market's: the decrees of 1714 (pp. 816-817) and 1718 (pp. 821-822) and p. 822's rice restated in
     each silver, as legal ratios.
   - Kusama's place: if a readable page on Kusama Naokata (kotobank, jawiki) says he was an Osaka money-changer, cite it and
     label the rates ATTESTED ONLY FOR one Osaka merchant's compilation; if not, "one merchant's compilation", unplaced.
   - Edo, 1714 and 1717-1718: jawiki 宝永四ツ宝丁銀 and 享保丁銀, ATTESTED ONLY FOR what jawiki states, their printed sources
     (『両替年代記』 1933; 田谷 1963) named as not read.
   - The coin-walk table (`coin-walk-edo-kahei-nenpyo`, already cited) named as a derivative: its rice columns match Kusama's to
     the digit (1707, 1714), its silver column does not (1711, 1714) - this project's comparison, labeled so.
   - Revise "1706-1721 mixed coins, not converted" to what is now known (which years have a rate and in which silver).
   - 0277: one pointer sentence to the new copper rates in 0287, no copy.
2. **0289: Canton's cash, the 1830s.** The *Chinese Repository* searched by name, and what it gives: Canton, May 1837, "$ ¼ ...
   equal to 250 cash" (vol. 6 p. 44; a letter-writer's conversion: ATTESTED ONLY FOR cash per dollar, about 1,000); the 1835-1836
   review of Thompson calling Canton's "1,000 cash = 1 tael" nominal (vol. 4; no market number); Xu Naiji's memorial, 1836, 1,200
   or 1,300 cash a tael "of late years" (vol. 5 p. 140; empire-wide; read the page image for the OCR's "past^"); the other
   places, each ATTESTED ONLY FOR its place (Tianjin 1832, Nan'ao 1832, Fujian 1835, Taiwan 1838). Canton's own cash per tael:
   SILENT, with the volumes searched and the leads not followed (Lin Man-houng, Wang Yeh-chien, Morse, the *Canton Register*).
   1,000 cash a dollar at the page's 0.71-0.72 tael a dollar is about 1,390-1,410 cash a tael: this project's arithmetic,
   labeled so.

**New registry keys** (at most ten): Kusama's 『三貨図彙』 (NDL 1279564), the *Chinese Repository* volumes cited (check which
are registered: 0288 and 0289 already cite it), jawiki 宝永四ツ宝丁銀 and 享保丁銀, a Kusama biography page.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0287" FEATURE=418` and `Q="0289"`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` and `l7r/diagram/interactive/record/money.py`
   say (a rate between coins is NOT marked; `make money-candidates CHECK=1` must exit 0). Commit with messages opening `418: `.
4. Append to `specs/418-hoei-rates-and-canton-cash/implementation-check.md` (create it):
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/418-hoei-rates-and-canton-cash/briefs/handoff.md` (create it) a `## Session 1` section: `- SECTION=<NNNN>/<id>`
   for each section you changed; per figure asked, its verdict and the fragment file; each search named; the new keys; leads
   not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
