# Brief - feature 319, G3: 0038 and 0039 disagree on daikon. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**The defect** (found by the garden modal's `modal-research` check, 2026-10-04). 0039 (`research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.html`)
now classes WHICH vegetables grew in the kitchen bed as silence ("no list says which grew beside the house"; that the bed held
the daily greens is a GUESS). 0038 (`research/questions/0038-sunlight-and-shade-on-the-farm.html`) states as fact, in a lead
line, "Daikon, the kitchen bed's autumn crop, needs six hours of sun in the season of the longest shadows", and its drawing page
(`0038-sunlight-and-shade-on-the-farm.drawing.html`, "A kitchen bed keeps the same 39 ft.") says "A bed's autumn daikon, and in
this project's reading its other autumn greens". What IS recorded: daikon is a sun crop, and autumn daikon is sown in early
autumn and pulled late autumn into winter (0038's own notes); and an early Edo-period farm book lists daikon among the greens a
household ate in the first and the tenth months (0039, `ehime-kenshi-seiryoki`).

## Your items (one question and its drawing page; no new registry key expected)

- 0038 and its drawing page: make both say only what is recorded - daikon an autumn-into-winter sun crop that households ate
  in those months - and that its growing in the kitchen bed is this project's reading, a GUESS (in the words 0039 uses), linking
  0039. The sun rule itself and its numbers do not change: say, where the drawing page grounds the 39 ft on the bed's autumn
  crop, that the rule rests on that reading. Keep each `Evidence:` comment honest. Any other sentence in the record that calls
  daikon the bed's crop as fact (grep `research/questions/` for "daikon") is yours too.

Do NOT edit any modal file or any engine code.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0038"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G3 in progress (0038 daikon) | 2026-10-04"`.
2. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
3. Write `specs/319-modal-writeups/briefs/g3-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 G3:`), do not push. Your last message is one paragraph.
