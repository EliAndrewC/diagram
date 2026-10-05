<!-- page-load: kind=split -->
# Brief - feature 319, H15: three questions over the size cap after the record fixes - 0081, 0091, 0196. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**Why.** Feature 319's record fixes (H1-H14) settled conflicts the modal checks found, and three questions grew past the
20,000-byte prose cap that `python3 scripts/check-question-size.py` (from the clone root) holds at the gate:

- `research/questions/0081-village-lanes.html` - 20,672 bytes (672 over)
- `research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html` - 20,090 bytes (90 over)
- `research/questions/0196-communal-wells-ido.html` - 20,044 bytes (44 over)

Bring each under the cap the way the record's rules say (`docs/research-record-rules.md`, "A question has a size", at the
clone root): a question that is over because it holds two topics is SPLIT along its topics - a finding stays with its decision,
each part its own question file and heading, tags and contents section as the record's CLAUDE.md says, and the joins point
rather than restate; a question that is over by a sentence's worth of repetition is TRIMMED of the repetition, never of a
finding, a footnote or an absence note. 0081 most likely wants a split; 0091 and 0196 most likely want a trim. Do not change
what any finding says, what any note quotes, any engine code or any modal file. A new question file takes its number from
the next free one (`ls research/questions | tail`) and its heading id slug as the record's CLAUDE.md says; every pointer to a
moved block is updated (`make fragment-move` moves a whole question; for a split, grep `research/questions/0081-` across the
skill, `l7r/`, `buildings*`, `dev/` and `specs/` and repoint any pointer whose subject moved).

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="<NNNN>"` for each question, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | H15 in progress (0081, 0091, 0196) | 2026-10-05"`.
2. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py tests/interactive/test_record_questions.py"`; `python3 scripts/check-question-size.py` from the clone root must print nothing for these three; `python3 scripts/check-research-pointers.py` from the clone root must pass.
3. Write `specs/319-modal-writeups/briefs/h15-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched or created and a sentence each), commit only your files (message beginning `319 H15:`), do not push. Your last message is one paragraph.
