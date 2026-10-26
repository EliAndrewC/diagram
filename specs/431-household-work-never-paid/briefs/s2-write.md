<!-- page-load: kind=assertions -->
# Brief - feature 431, city households, days off, the proverb and why the record is thin. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-research-2`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#21 (verbatim in `specs/431-household-work-never-paid/request.md`),
questions 4, 5, 6 and 7. Japan first, China beside it. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT
ATTESTED or SILENT (with its search) - with place and date. Any product of figures is this project's arithmetic, labeled. Two
sources that disagree are both given. The GM asked that the record call out explicitly that women's household work was almost
never written down at the time, that this is a reason some numbers are spotty, and that this is itself an important historical
fact about what we can know of premodern societies: that is the point of item 3's question, said in its opening. Say, in a
sentence per question, how the findings stand against the canon (`make canon`).

**Your passes:** `specs/431-household-work-never-paid/passes/d-city-and-days-off.md` and `e-proverb-and-historiography.md` -
leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it
says, or SILENT. The Hitotsubashi PDF has no text layer for `make source-pages`; the pass read it by pdftotext - get it into the
archive. Cite what reports a source as that: Morisada through the nippon.com articles, the Bunsei-era manuscript through the
modern paper, Bray through Waltner's review, Shirokiya's papers through a book's chapter titles. A page with no source or date (the
rental-shop page) is a lead. The journalist's single-against-married line (nippon.com 2020) IS given, labeled as unsourced: it
is the only statement on the comparison the GM asked for.

**Not yours** (session S1 holds them, in another clone): Tanimoto, Nagashima 2017, Pomeranz's draft, Allen et al., the Sukumo
city history, Tomioku, Buck, Fei, the Shen-shi and Bu nongshu, and the two new questions S1 writes (the farm household's unpaid
work; how long it took to make cloth).

**Already in the record - name by file, do not repeat:** 0311 (yabuiri, rest days), 0307 (clerks not allowed a household until
nearly 30), 0183 (the Edo street lot with back tenements), 0115 (servants), 0004 (household size).

## Your items

1. **City households**, a NEW money question (`make reserve KIND=question`), its title asking what a city household bought that a
   farm household made; `subject=money`; pointers from 0183 and 0004. Edo: polished rice (1727, 1744); the Bunsei budgets of a
   peddler and a carpenter; bath fees (1841-1866); the tenement's shared well, no bath, the wives washing and rinsing rice; used
   clothing (1659); water sellers; washing shops from about 1688 (whose clothes SILENT); samurai barracks men cooking for themselves
   or eating out (samurai, labeled). Q4's six items, each with its trade and its price, or SILENT with the searches: used clothing, cooked food, washing,
   mending, firewood (and charcoal), water. The GM's main question: home-work days or hours a year for a single tenement laborer and for a
   laborer or artisan with a family or an extended family - a figure or SILENT with the searches - and who in the household did the
   unpaid work. Kyoto and Osaka; China (Beijing's water carriers; prices SILENT).
2. **Other workers' days off**, extending 0311: merchant-house live-ins (the two yabuiri with pocket money and new clothes; no
   household until head clerk; a Kyoto house's Edo staff first home in the ninth year); a side trade SILENT; porters, guards and
   footmen SILENT with the searches; China SILENT.
3. **Why the record is thin**, a NEW money question, its title asking why women's household work was so rarely recorded; pointers
   from item 1 and from S1's two new questions (C2 adds those pointers once both have landed). Japan: Makihara 2020; the
   Hitotsubashi survey 2007 (the historians' sources: headmen's diaries, temple registers, commendation records, prescriptive
   texts). China: Bray through Waltner; Pomeranz on Li Bozhong's narrow base; Li Shizhong on gazetteer biographies. Any European
   statement (Duby and Perrot) only as the Hitotsubashi page reports it, labeled as another society's.
4. **The proverb**, in item 3's question or its own small question by size: the 360-day form SILENT with the searches; its halves
   in Lu Mingshan's farming almanac (begun 1314; to those who farm) and Lou Yue's poem (before 1213); Zhu Yongchun's household rule
   (gentry, nothing on wealth); the Zengguang xianwen lines only once their layer is dated; the Keian edict's "rise early" (its 1649
   date disputed; the Gunma archives); whose saying it was, testing the GM's guess that it is a farming proverb; the Japanese
   early-rising proverb's origin SILENT. The original text carried for each attested part; translations marked as such.

**New registry keys** (at most ten): as the passes name them. If more are needed, `make reserve`'s eleventh key writes a
continuation brief - follow it.

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="0311" FEATURE=431`, `Q="0183"`, `Q="0004"`, and claim the new questions'
   numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `431: `.
4. Append to `specs/431-household-work-never-paid/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/431-household-work-never-paid/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S2`
   section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads
   not followed. This is task T02.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
