<!-- page-load: kind=assertions -->
# Brief - feature 428, how often players performed. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-research-2`). The project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's questions on EliAndrewC/diagram#20 (verbatim in `specs/428-working-days-and-performances/request.md`,
with the canon each answer sits beside), part 3. Japan first, China beside it, England as the GM's own comparison. Every figure
gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - per kind of troupe:
performances a day, days a week, run lengths, idle months, closures. Any yearly total is this project's arithmetic, labeled. Say,
in a sentence, how the findings stand against the canon the request names, plainly: where no source shows the county troupe's
weekly market-day rhythm, write that it is not attested; never soften a finding to fit the canon.

**Your pass:** `specs/428-working-days-and-performances/passes/q3-performances.md` - leads, not citations: read each passage on
its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. The pass saved page copies
under `/tmp/l7r-pass/q428-*`; get each page into the record's tooling with `make archive-find` / `make source-pages`.

**Already in the record - name by file, do not repeat:** 0308 (entertainers: city stars on yearly contracts from the 11th month;
Shima villages hiring puppet companies for three-day runs twice a year), 0266 (plays; Buhler's Funai diary: Hamanoichi's runs,
the 1728 Nakatsu nine fair days and 15 shows), 0214 (roofed playhouses; Kotohira about three times a year before 1835), 0187
(plays on shrine ground at festivals).

## Your items

1. **How often players performed**, a NEW money question (`make reserve KIND=question`), its title asking how often players
   performed; `subject=money`; a pointer to it from 0308, 0214 and 0187. (a) A successful troupe with its own roofed playhouse -
   the licensed theaters of Edo, Kyoto and Osaka first, a castle town's permanent playhouse where one is found: daylight only,
   programs a day and a year, HOW LONG A PROGRAM ran in hours (a figure or SILENT), the theatrical year, idle months, rain, fire, mourning (narimono choji), the puppet theaters; (b)
   shrine-ground troupes in a provincial city (miyaji shibai): license terms, licenses a year; (c) a country troupe touring
   villages and a county town: engagements and their days. China beside it: Beijing theaters' hours and the four-day rotation,
   village and temple-fair hires, fair seasons, mourning. Against the canon: the county troupe of about 5-10 making most of its
   money on market day and touring the village districts the rest of the week; provincial cities' competing troupes; a domain
   capital's entertainers tied to one establishment.
2. **England, the GM's comparison**, a NEW question in the "Comparative money" section (`research/CLAUDE.md` "Comparative money
   sources": `subject=comparative,money`; the source's kind `comparative` in `research/source-tags.json`): Shakespeare's company
   and its peers - time of day, days a week, how often the bill changed, new plays, performances a year, Lent, summer and plague
   closures, the Blackfriars winter house. Chambers 1923 (Gutenberg 67423) relays Henslowe's diary and the primary documents: say
   so in its write-up. Never a Rokugani figure.

**New registry keys** (at most ten): as the pass names them; at most ten. If more are needed, `make reserve`'s eleventh key
writes a continuation brief - follow it.

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="0308" FEATURE=428`, `Q="0214"`, `Q="0187"`, and claim the new questions'
   numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `428: `.
4. Append to `specs/428-working-days-and-performances/implementation-check.md` (create it if absent) one line per touched
   question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/428-working-days-and-performances/briefs/handoff.md` (with `make append`; create it if absent) a
   `## Session S2` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file;
   searches; new keys; leads not followed. This is task T02.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
