<!-- page-load: kind=assertions -->
# Brief - feature 450, tobacco, the sweet potato and the white potato. Session S4: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's words on EliAndrewC/diagram#22 (verbatim in `specs/450-cotton-and-new-crops/request.md`), question 3. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - with place and date. A date for a neighboring place, century or plant is SILENT, the nearest named. Two sources that disagree
are both given. Any product of two sources' figures is this project's arithmetic, labeled. In analytical prose it is "commoners" or "the population", never "people".

**History only.** No fragment says how common any crop is in Rokugan; that is the GM's decision. An intro paragraph, where a question needs one, may say what the canon holds (`make canon`) and nothing about what it should hold. Nothing edits the canon.

**Your pass:** `specs/450-cotton-and-new-crops/passes/``d-tobacco-potatoes.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. **Its reading is the pass's, not yours: test it.**

Keep the plants strictly apart. Sources use 薯, 芋, 甘藷, 番薯, 山藥, 馬鈴薯 loosely, and modern Korean 감자 is the white potato while 감저 is the sweet potato: each date says which plant
it concerns and how that is known. Where it cannot be known, the date is ATTESTED ONLY FOR the word. The Songxi gazetteer of 1700 ("grows on trees", bitter black tubers) fits Solanum badly: not a secure first
record. Laufer's Ming and Qing authors are in his English; Ho is read only through a summary and Crosby, never as Ho; the 1598 date for Japan and the 1633 date for Korea are disputed, both sides given. Much of the dating is
tertiary (Wikipedia, popular pages, Encykorea): say what each verdict stands on. Try the primary texts the pass could not reach once (露書, 景岳全書's 烟 entry, 宛署雜記 for Shen Bang).

**Already in the record - name by file, do not repeat:** 0006 and 0020 (dry-field crops and cash crops on rice land).

## Your items

1. **Tobacco**, a NEW money question, its title asking when tobacco was first grown and became common in China, Japan, Korea and India; `subject=money` first. Per country, China and Japan first: first
   recorded, first cultivated, common use, who used it, the lag in years.
2. **The sweet potato**, a NEW money question, the same shape, its plant words kept as the cautions say.
3. **The white potato**, a NEW money question, the same shape; or a statement that it was not common before a stated date.

**New registry keys** (at most ten): as the pass names them, the best-evidenced first. `make reserve`'s eleventh key writes a continuation brief - follow it.

## The procedure (session S4: write)

1. `make archive-inbox`. Claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`). `make money-candidates CHECK=1` must exit 0. Commit with messages opening `450: `.
4. Append to `specs/450-cotton-and-new-crops/implementation-check.md` (create it if absent) one line per touched question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/450-cotton-and-new-crops/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S4` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
