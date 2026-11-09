<!-- page-load: kind=assertions -->
# Brief - feature 450, the species, and India and Korea. Session S3: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's words on EliAndrewC/diagram#22 (verbatim in `specs/450-cotton-and-new-crops/request.md`), question 2. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - with place and date. A date for a neighboring place, century or plant is SILENT, the nearest named. Two sources that disagree
are both given. Any product of two sources' figures is this project's arithmetic, labeled. In analytical prose it is "commoners" or "the population", never "people".

**History only.** No fragment says how common any crop is in Rokugan; that is the GM's decision. An intro paragraph, where a question needs one, may say what the canon holds (`make canon`) and nothing about what it should hold. Nothing edits the canon.

**Your pass:** `specs/450-cotton-and-new-crops/passes/``c-species-india-korea.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. **Its reading is the pass's, not yours: test it.**

Pass C prints an English Wikipedia URL beside two archived works (Tanimoto, archive 42/4288c884928c; Bishop, af/afb75ffbad3a): take each source's URL from
`make archive-find`, never those. The species names changed: Fortune and EB 1911 say G. herbaceum where Hutchinson 1947 and later work say G. arboreum; say so. An India acreage share (2-3%) rests on one
modern web essay, a Korean volume of 500,000 bolts on one author's OCR'd page: each says so. The 1398 obituary is retrospective. That Korea carried the PLANT to Japan is not shown; say what is.

**Already in the record - name by file, do not repeat:** the Japan and China questions of sessions S1 and S2.

## Your items

1. **Was cotton a New World crop?** A NEW money question, its title asking which cottons grew in Asia before 1492 and when the American kinds came; `subject=money` first.
   Each species and its date of arrival and importance, across India, China, Korea and Japan. The premise tested. The GM's specific point answered: name the event and date that close the window from a source you read (the edicts of the 1630s or the shogunate's founding in 1603), say which his "~100 years" fits, and answer
   both halves: whether those years had any bearing on Japanese cotton, and whether Japan probably did not have cotton in them, from the dates in the Japan question.
2. **Cotton in India and Korea**, a NEW money question, its title asking when cotton became ordinary in India and in Korea; the five stages per country, each with one of the four verdicts (India's stage of cloth arriving mainly as an import too, the 19th century's factory cloth searched; the pass did not search it); the same five stages as the Japan question. Korea's role, if any, in cotton reaching Japan, the cloth and the plant each with its own verdict and dates. Point at the Japan and China questions by title.

**New registry keys** (at most ten): as the pass names them, the best-evidenced first. `make reserve`'s eleventh key writes a continuation brief - follow it.

## The procedure (session S3: write)

1. `make archive-inbox`. Claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`). `make money-candidates CHECK=1` must exit 0. Commit with messages opening `450: `.
4. Append to `specs/450-cotton-and-new-crops/implementation-check.md` (create it if absent) one line per touched question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/450-cotton-and-new-crops/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S3` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
