# Brief - feature 319, G6: 0072 and 0036 disagree on a grove's conifer share. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**The defect** (found by the windbreak modal's `modal-research` check, 2026-10-05). `research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html`
asks "What share of a grove's trees were conifers?" and answers that no page we read gives one, and its `Evidence:` comment
classes "cedar the commonest tree in a grove" as a guess. But `research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html`
already records a count: "Of the 1,542 trees counted, 735 - 48% - were cedar" (its notes cite `kashima-kainyo-1987`), in the
farmhouse groves of one Tonami hamlet.

## Your items (one question; no new registry key expected)

- 0072: answer the conifer-share question with what 0036 records - for farmhouse groves in one Tonami hamlet, nearly half the
  trees were cedar - linking 0036, with its limit (one hamlet's farmhouse groves; no count for a village belt); keep the
  absence for a VILLAGE belt's share; correct the `Evidence:` comment (cedar the commonest tree is read for those farmhouse
  groves, a guess for a village belt). Cite the passage as 0036 cites it (reuse its note's key and quotation). Its drawing page
  (`0072-...drawing.html`) may say the conifer is the commonest crown in a conifer-led belt as a GUESS - if it calls that
  unsourced where 0036 now gives a farmhouse figure, say so there in a clause too.

Do NOT edit any modal file or any engine code.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0072"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G6 in progress (0072 conifer share) | 2026-10-05"`.
2. Read 0036's passage and its note; run the source-reader agent from a bundle on the passage you will quote, in the FOREGROUND.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/g6-handoff.md` (one `- SECTION=<NNNN>/<id>` line and a sentence), commit only your
   files (message beginning `319 G6:`), do not push. Your last message is one paragraph.
