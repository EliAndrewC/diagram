<!-- page-load: kind=assertions -->
# Brief - feature 450, Japan's cotton. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** The GM's words on EliAndrewC/diagram#22 (verbatim in `specs/450-cotton-and-new-crops/request.md`), question 1, the Japan half. Every figure gets a verdict - ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT (with its search) - with place and date. A date for a neighboring place, century or plant is SILENT, the nearest named. Two sources that disagree
are both given. Any product of two sources' figures is this project's arithmetic, labeled. In analytical prose it is "commoners" or "the population", never "people".

**History only.** No fragment says how common any crop is in Rokugan; that is the GM's decision. An intro paragraph, where a question needs one, may say what the canon holds (`make canon`) and nothing about what it should hold. Nothing edits the canon.

**Your pass:** `specs/450-cotton-and-new-crops/passes/``a-japan-cotton.md` - leads, not citations: read each passage on its page before citing it; where a page does not read as the pass says, write what it says, or SILENT. **Its reading is the pass's, not yours: test it.**

Tanimoto's paper is marked not to be quoted: cite it as 0312 and 0313 do, with that said. Nagahara 2004 is read only through
Yajima 2017 (and Tanimoto): cite those, never Nagahara. Kawakatsu was read as a Wayback copy (the JEF page is 403). The 慶長見聞集 clipping has no
context, so assert no direction from it. The Aomori page's flat "not permitted" and Ishiyama's edict series disagree: give both. Sumptuary rules are
ceilings: say what they allowed, never what anyone owned. The Akita and Aomori shares are this project's arithmetic, labeled. Try the leads the pass could not open
once (the samurai-archives Cotton page, the u-nagano 五人組帳, the kyoritsu paper on warrior dress); a page still unreadable stays out.

**Already in the record - name by file, do not repeat:** 0261 and 0274 (cloth prices), 0313 (cloth labor), 0312 (household weaving), 0209 (dyers and weavers as a trade), 0006 and 0020 (dry-field crops and cash crops on rice land).

## Your items

1. **Japan's cotton**, a NEW money question (`make reserve KIND=question`), its title asking when cotton became ordinary clothing in Japan;
   `subject=money` first. The five stages in order, each dated and with its place: first reliable record of the plant or cloth; cloth arriving mainly
   as an import; first cultivation on any scale; cultivation as a regular commercial crop; cotton as the normal clothing of commoners. What it replaced
   (hemp, ramie, kudzu and other bast fibers, silk) and how fast. By region, the cold north against the Kinai, and by class, low-ranking samurai against peasants and
   townsmen. Any share of households or clothing a source gives, or SILENT. The direct question answered by region: in what century a cotton kimono became
   widespread, worn by whom, the sources' disagreement stated.
2. A one-line pointer to item 1 from `research/questions/0261-what-did-cloth-and-clothing-cost.html`, where it speaks of cotton cloth.

**New registry keys** (at most ten): as the pass names them, the best-evidenced first. `make reserve`'s eleventh key writes a continuation brief - follow it.

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="0261" FEATURE=450`. Claim the new questions' numbers (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`). `make money-candidates CHECK=1` must exit 0. Commit with messages opening `450: `.
4. Append to `specs/450-cotton-and-new-crops/implementation-check.md` (create it if absent) one line per touched question: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/450-cotton-and-new-crops/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S1` section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads not followed.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
