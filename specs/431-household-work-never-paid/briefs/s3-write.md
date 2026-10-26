<!-- page-load: kind=assertions -->
# Brief - feature 431, the cross-pointers. Session S3: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-money-research`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md`
above all.

**What is asked.** Feature 431 wrote six money questions in two sessions that could not see each other: 0312 (what work a farm
household did that was never paid), 0313 (how long it took to make cloth), 0314 (modern hand weaving, comparative), 0315 (what a
city household bought that a farm household made), 0316 (why women's household work was so rarely written down), 0317 (the
early-rising proverb), and extended 0311 with other workers' days off. The joins between them are missing. A pointer POINTS (a
sentence naming the other question by its title and linking it the way the record links questions); it never restates the other's
evidence. New prose needs no new source; add none.

## Your items

1. Pointers TO 0316 from 0312, 0313 and 0315, each where that page says a figure for women's household work is missing: the
   reason (such work was rarely written down at the time) is 0316's to give. 0312's prose is at about 19,970 bytes against the
   20,000 cap: make room by tightening words elsewhere in the same section, never by cutting a finding; if it cannot fit, split by
   `research/CLAUDE.md` "A question has a size" and say so in the handoff.
2. Pointers TO 0312 (and 0313 where cloth bears) from 0311, 0004 and 0183 - one sentence each, where each page touches the
   household's own work or its trades.
3. A pointer from 0312 to 0317 (the early-rising saying belongs beside the farm household's year), and from 0317 to 0312.
4. 0313's note `tiangong-kaiwu-zhisi`: cut the clause 以其苗長也 and its English from the quotation (and its stored original) -
   translation-check left 'sprouts' CANNOT-TELL twice and the page's prose does not use the clause; mark the cut with an ellipsis.

## The procedure (session S3: write)

1. `make research-claim Q="<n>" FEATURE=431` for each question you edit.
2. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_glossary_source.py"`)
   and `make quick`'s question-size check passes. Commit with messages opening `431: `.
3. Append to `specs/431-household-work-never-paid/briefs/handoff.md` (with `make append`) a `## Session S3` section:
   `- SECTION=<NNNN>/<id>` per section changed, and what each pointer says. This is part of task T03.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
