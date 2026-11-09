<!-- page-load: kind=assertions -->
# Brief - feature 450, China's cotton. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's words on EliAndrewC/diagram#22 (verbatim in `specs/450-cotton-and-new-crops/request.md`), question 1, the China half. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - with place and date. A date for a neighboring place, century or plant is SILENT, the nearest named. Two sources that disagree
are both given. Any product of two sources' figures is this project's arithmetic, labeled. In analytical prose it is "commoners" or "the population", never "people".

**History only.** No fragment says how common any crop is in Rokugan; that is the GM's decision. An intro paragraph, where a question needs one, may say what the canon holds (`make canon`) and nothing about what it should hold. Nothing edits the canon.

**Your pass:** `specs/450-cotton-and-new-crops/passes/``b-china-cotton.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. **Its reading is the pass's, not yours: test it.**

Zurndorfer's GEHN papers and Pomeranz 1998 are marked not for citation: cite each with that said. Pelliot's English renderings are his. Conflicts to
give both sides of: Qiu Jun's "not yet levied" against the Yuan shi's 1296 summer tax; the Nongsang jiyao as Song (Zurndorfer) or Yuan (Pelliot); Huang Daopo's date;
富有 (plentiful, or "some of the rich"); 蘭干 as cotton (Zurndorfer) or ramie (Qu Dajun); whether Hou Hanshu's 帛疊 and 布 mean cotton at all. Buck (1930) is outside the
window: named as the nearest, never the verdict. Yangzi cultivation by the 12th century is a modern reading of Song poems, and says so.

**Already in the record - name by file, do not repeat:** 0261 (cloth prices), 0313 (cloth labor), 0288 (a year's necessities in China).

## Your items

1. **China's cotton**, a NEW money question, its title asking when cotton became ordinary clothing in China; `subject=money` first. The same five stages as
   Japan's, each dated with its place, the frontier regions (Hainan, Yunnan, the northwest) and the Yangzi kept as separate stages; the state's part; what it replaced and how
   fast; by region (Jiangnan, North China, the far south) and by class. Any share of households, acreage or clothing, or SILENT. The direct question answered: in what century
   cotton clothing became widespread, worn by whom. Point at the Japan question by its title, from session S1's handoff.

**New registry keys** (at most ten): as the pass names them, the best-evidenced first. `make reserve`'s eleventh key writes a continuation brief - follow it.

## The procedure (session S2: write)

1. `make archive-inbox`. Claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`). `make money-candidates CHECK=1` must exit 0. Commit with messages opening `450: `.
4. Append to `specs/450-cotton-and-new-crops/implementation-check.md` (create it if absent) one line per touched question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/450-cotton-and-new-crops/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S2` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
