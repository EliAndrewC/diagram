<!-- page-load: kind=assertions -->
# Brief - feature 431, the farm household's unpaid work and the fiber chain. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-research`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#21 (verbatim in `specs/431-household-work-never-paid/request.md`),
questions 1, 2 and 3. Japan first, China beside it. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT
ATTESTED or SILENT (with its search) - per household member, task or stage, with place and date. Any product of two sources'
figures (a robe's days from a bolt's, hemp days from Nagahara's tenfold) is this project's arithmetic, labeled. A study's estimate
or assumption is reported as one, never as a count. Two sources that disagree are both given. Where a figure for women's household
work is missing, say so and say why: such work was rarely written down at the time (the GM's addendum; session S2 writes the
question on why the record is thin - point at it by its title, "why women's household work was so rarely recorded", once it
exists, or leave the pointer to C1). Say, in a sentence per question, how the findings stand against the canon (`make canon`):
`budgets.md`'s peasants weaving waraji "the same evening", `l7r.md`'s silk "heavily gendered" and its family of five on 7.5 koku.

**Your passes:** `specs/431-household-work-never-paid/passes/a-japan-household.md`, `b-china-household.md` and `c-fiber-chain.md` -
leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it
says, or SILENT. Local copies the passes used (Tanimoto's and Pomeranz's LSE drafts by pdftotext; Nagashima 2017 and the JAS 2003
exchange as page images) go through `make archive-find` / `make source-pages` (an image page goes to the checks with `IMAGES=`).
Cite drafts with their "not to be quoted" headers said; Nagahara's tenfold through Nagashima and Tanimoto, never as Nagahara; the
Seiryoki through the Sukumo city history and Nagashima; Lu Village through Hu Yukun (third-hand). The European experiments
(Mannering, Bender Jorgensen) are NOT cited: craft-time rates, not money sources, outside the comparative exception.

**Not yours** (session S2 holds them, in another clone): the Keian edict pages (Gunma archives, ja.wikipedia), pass D's and pass
E's sources, and 0311, 0004 and 0183 (S2 edits them). Name night work from Tomioku and Nagashima.

**Already in the record - name by file, do not repeat:** 0311 (work year, rest days, Li and Pomeranz's 200 spinning days), 0004
(household size), 0209 (dyers and weavers as a trade), 0183 (side trades), 0306 (a smith's pay).

## Your items

1. **The farm household's unpaid work**, a NEW money question (`make reserve KIND=question`), its title asking what work a farm
   household did that was never paid; `subject=money`. (Pointers to it from 0311, 0004 and 0183 are added after both writes land - S2 holds those three questions; do not edit them.) (a) The year by member and season:
   the Seiryoki's annual man-days (293 male and over 200 female field days a cho, night work uncounted; fuel 120, ox and horse care
   120, fertilizer grass 40, silkworms 20, house repair 20, ditch dredging 20, tools and mat and rain-cape materials 12, tea 10;
   811 in all for 1 cho 2 tan 5 se); the peasant wife "like an actor playing every part"; Nagashima's division of tasks, the Imai
   accounts (1821) and the Muramatsu house rules; Tomioku (Meiji-Taisho memory, labeled); Saito's Yamanashi 1879 shares; China: the
   Shen-shi nongshu's rainy-day work (c. 1640, hired men on a managed farm), the Bu nongshu (1658), Buck (1921-25, productive work
   only), Fei (1936), Hu Yukun on Lu Village. Per member in hours: SILENT with the searches. (b) The task list: each task with who
   did it and its time, or SILENT (cooking, water, miso and soy, pickling, straw goods per unit, sewing, araihari, child care). (c)
   The GM's hypothesis, both halves, with the verdicts the passes reach - test them against the pages, do not take them on trust.
2. **The fiber chain**, a NEW money question, its title asking how long it took to make cloth; pointers from 0209, 0306 and item 1.
   Cotton from ginned fiber: Tanimoto's 4 days a tan, 12.8 tan a year for the household, 39.4 for sale, one woman about seven
   months; China 7 (or 6) days a bolt hand-spun, 3 machine-spun, spinning four hours to one of weaving (Pomeranz's draft; the JAS
   2003 exchange); the 200-day maximum (Allen et al.); the Songnan poems (through Zheng Tianting); Tiangong kaiwu's reeling and ramie
   splitting (1637). Akita 1808-10 bought against made (shares this project's arithmetic). Hemp and silk per tan in Japan, growing,
   dyeing and sewing a robe: SILENT with the searches.

**New registry keys** (at most ten): as the passes name them. If more are needed, `make reserve`'s eleventh key writes a
continuation brief - follow it.

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="0209" FEATURE=431`, `Q="0306"`, and
   claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `431: `.
4. Append to `specs/431-household-work-never-paid/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/431-household-work-never-paid/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S1`
   section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads
   not followed. This is task T01.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
