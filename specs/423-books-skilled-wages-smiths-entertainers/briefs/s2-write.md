<!-- page-load: kind=assertions -->
# Brief - feature 423, skilled and trusted labor, and entertainers. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#19 (verbatim in `specs/423-books-skilled-wages-smiths-entertainers/request.md`,
with the canon each answer sits beside). Japan first, China beside it. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR
<the case>, NOT ATTESTED or SILENT (with its search); each in the unit the question names, in silver or copper as the source states
it; any per-year total, unit or coin conversion is this project's arithmetic, labeled. Two sources that disagree are both given,
not reconciled by guess. Say, in a sentence per question, how the findings stand against the canon the request names.

**Your passes:** `specs/423-books-skilled-wages-smiths-entertainers/passes/q2-skilled.md` and `passes/q4-entertainers.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the
pass says, write what it says, or SILENT. Where a pass recorded a ledger outcome wrongly (the Q3 pass marked the Kawashima 2010 PDF
and the Arai BOUNDARY PDF `nothing-found` though it used them), citing them records `cited:` over it.

**Already in the record - name by file, do not repeat:** 0250 (the unskilled day), 0275 (skilled against unskilled), 0252 (Regency servants; comparative - do not use for a Rokugani figure), 0262, 0266 (plays: the city kabuki and puppet companies of about 43 and 26), 0261 (cloth).

## Your items

1. **Skilled and trusted labor**, in 0275 or a sibling question by size (0275's prose cap is 20,000 bytes): a merchant house's
   live-in clerk by seniority and a scribe by the day; an armed escort of goods or cash, and China's biaoju, per day or per trip;
   a household cook, a lord's cook and a lady's maid, each with what came in kind. The ledger's unverified Kanazawa lead (0.7-1
   koku a year for servants, 3 for a young steward) confirmed, narrowed or contradicted, cited from the work it came from (never
   the ledger), or SILENT if its source is not found. Against the canon: stipend = rank squared for samurai clerks; servants and
   cooks hinin.
2. **Entertainers**, beside 0266 or in it by size: a traveling troupe's takings per performance and per year and their sharing, a
   street performer's day, a star actor's yearly pay, a traveling or rural troupe's size, a costume (ordinary and fine), a shamisen,
   a flute and a tsuzumi; Japan first (kabuki, rural troupes, Morisada), China beside it. Against the canon: the county troupe of
   about 5-10 earning most on market day, with performances at the magistrate's manor; entertainers hinin.

**New registry keys** (at most ten): as the passes name them; at most ten.

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="0275" FEATURE=423` and `Q="0266"`, and claim any new question's number (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `423: `.
4. Append to `specs/423-books-skilled-wages-smiths-entertainers/implementation-check.md` (create it if absent) one line per touched
   question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/423-books-skilled-wages-smiths-entertainers/briefs/handoff.md` (with `make append`; create it if absent) a
   `## Session S2` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file;
   searches; new keys; leads not followed. This is task T02.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
