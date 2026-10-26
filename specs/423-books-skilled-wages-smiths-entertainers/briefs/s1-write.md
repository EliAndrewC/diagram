<!-- page-load: kind=assertions -->
# Brief - feature 423, books and a smith's accounts. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#19 (verbatim in `specs/423-books-skilled-wages-smiths-entertainers/request.md`,
with the canon each answer sits beside). Japan first, China beside it. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR
<the case>, NOT ATTESTED or SILENT (with its search); each in the unit the question names, in silver or copper as the source states
it; any per-year total, unit or coin conversion is this project's arithmetic, labeled. Two sources that disagree are both given,
not reconciled by guess. Say, in a sentence per question, how the findings stand against the canon the request names.

**Your passes:** `specs/423-books-skilled-wages-smiths-entertainers/passes/q1-books.md` and `passes/q3-smiths.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the
pass says, write what it says, or SILENT. Where a pass recorded a ledger outcome wrongly (the Q3 pass marked the Kawashima 2010 PDF
and the Arai BOUNDARY PDF `nothing-found` though it used them), citing them records `cited:` over it.

**Already in the record - name by file, do not repeat:** 0264 (paper and ink), 0266 (plays), 0250 (the unskilled day), 0275 (skilled against unskilled), 0276 (the kitchen knife; it cites Takekoshi 1935 and Gao Shouxian's 1736 list), 0279 (charcoal).

## Your items

1. **A new question on books** in "Money and prices", `subject=money`, its title asking what a book cost to buy, to borrow and to
   have copied. Japan: kibyoshi by the 5-leaf volume (the two retail figures, 6 and 8 mon, each as its source gives it, tertiary,
   unreconciled), the Tenpo gokan (40 leaves, 176 mon wholesale) and yomihon (7.5-15 monme trade) from Bakin's letters (佐藤 1994),
   lending fees per volume (6-30 mon in Tsutaju's time; Nagatomo's scale in silver fun, read as quoted); a classic, primer or
   reference volume SILENT with the search, the 『増益書籍目録』 lead named; a copyist's rate per leaf or day SILENT, the one 1846
   fair-copy fee given as what it is (copyist and illustrator together). China beside it: late-Ming prices (Chow 2010; Brook's
   excerpt), a hand copy under 0.4 tael, the Siku copyists' 1,000 characters a day (rewarded with rank, not cash).
2. **A new question on a maker's income** beside 0276, its title asking what a smith earned. A tool against its iron (Qing Beijing
   1736, sickle and wrought iron on one list: ATTESTED ONLY FOR a government purchase list; our arithmetic for the iron's share,
   its exclusions said); Japan: the 1822 Sakai hoe (5.5-5.6 monme, 『農具便利論』 via Kawashima 2010), the 1841 Echizen village
   smith's charges (福井県史), iron per kan only in rice (Arai, after Oka) - a Japanese ratio only as arithmetic across sources, with
   the hoe-weight caveat, and the hoe-point charge left unreconciled with the Sakai hoe; who paid for the charcoal in the itinerant
   model (『清良記』 via Kawashima 2012); output a year (Takefu's sickles per household, our arithmetic; Sakai's night quota of
   tobacco knives); a smith's gross and net income SILENT; crew size (Mino and Hida 1834-1840; Qing shops, Feng Erkang); payment in
   rice ATTESTED ONLY FOR 20th-century practice; the Edo carpenter's year as a second case, third-hand, said. One pointer in 0276.

**New registry keys** (at most ten): Kawashima 2010 and 2012, Arai BOUNDARY 2000.9, the Shizuoka library PDF, the two 福井県史 pages, Feng Erkang, 佐藤 1994 (J-STAGE), Chow 2010, the lending-fee pages you cite (prefer the ones naming 長友 or 鈴木), the Toyo University paper.

## The procedure (session S1: write)

1. `make archive-inbox`. Then claim the two new questions' numbers (`make reserve`), and `make research-claim Q="0276" FEATURE=423` for its pointer.
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `423: `.
4. Append to `specs/423-books-skilled-wages-smiths-entertainers/implementation-check.md` (create it if absent) one line per touched
   question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/423-books-skilled-wages-smiths-entertainers/briefs/handoff.md` (with `make append`; create it if absent) a
   `## Session S1` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file;
   searches; new keys; leads not followed. This is task T01.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
