<!-- page-load: kind=assertions -->
# Brief - feature 450, the tomato, what set the pace of spread, and the Tokugawa restrictions. Session S5: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's words on EliAndrewC/diagram#22 (verbatim in `specs/450-cotton-and-new-crops/request.md`), questions 3 (the tomato) and 4. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - with place and date. A date for a neighboring place, century or plant is SILENT, the nearest named. Two sources that disagree
are both given. Any product of two sources' figures is this project's arithmetic, labeled. In analytical prose it is "commoners" or "the population", never "people".

**History only.** No fragment says how common any crop is in Rokugan; that is the GM's decision. An intro paragraph, where a question needs one, may say what the canon holds (`make canon`) and nothing about what it should hold. Nothing edits the canon.

**Your pass:** `specs/450-cotton-and-new-crops/passes/``e-tomato-spread-factors.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. **Its reading is the pass's, not yours: test it.**

`make source-pages` refused the Isono (Keio), Crosby (Warwick) and MAFF Kyushu PDFs as having no text layer: read them by pdftotext, archive them, and give the checks an archive copy or page images. Ho, Mazumdar, Chen and Kung, Marks,
Totman, Tashiro and Toby were not read: cite only what was (Crosby on Ho, labeled; a blog summary of Mazumdar is not Mazumdar). The pass's count of Isono's year-rows counts rows, not plants: leave it out, or give it as this project's arithmetic on rows. Reading 南蠻枾 as the tomato is the modern writers' identification.
清良記's 赤茄子 sits in an eggplant list: not the tomato. Crosby's "quick" and Li's "late" conflict: give both. Anything from outside the four countries is marked COMPARATIVE in prose; the source kind `comparative` is only for another society's money.

**Already in the record - name by file, do not repeat:** the crop questions of session S4.

## Your items

1. **The tomato**, a NEW money question, its title asking when the tomato became common in China, Japan, Korea and India; `subject=money` first. Per country, first recorded, first cultivated, common use, the lag. Both positions tested with dates, either way: that
   tomatoes were not a big part of Japanese cuisine even when available, and that China did not cultivate them on a large scale for centuries.
2. **What set the pace**, a NEW money question, its title asking why one new crop spread quickly and another slowly in China and Japan: the factors historians name, each with author and the crops it applies to, their disagreements given. Where Japan has no such account read, say so.
3. **The Tokugawa restrictions**, a NEW money question, its title asking whether the restrictions on foreign trade stopped new crops reaching Japan: named crops with dates and routes, before and after the edicts, their dates from a source you read.
   Point items 1 and 3 at the tobacco, sweet potato and white potato questions by title, from session S4's handoff.

**New registry keys** (at most ten): as the pass names them, the best-evidenced first. `make reserve`'s eleventh key writes a continuation brief - follow it.

## The procedure (session S5: write)

1. `make archive-inbox`. Claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`). `make money-candidates CHECK=1` must exit 0. Commit with messages opening `450: `.
4. Append to `specs/450-cotton-and-new-crops/implementation-check.md` (create it if absent) one line per touched question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/450-cotton-and-new-crops/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S5` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
