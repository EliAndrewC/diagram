# Brief - feature 319, G4: 0028 calls a drift a deliberate deviation. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**The defect** (found by the farmhouse modal's `modal-depiction` check, 2026-10-04). Two drawing pages contradict each other.
`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html`, the group "A farm's byre is not drawn as a
stable wing of the house (magariya).", ends "leaving out the wing is a deliberate deviation". But
`research/questions/0029-farmhouses-minka.drawing.html` makes the house's plan a per-settlement form - "The L-shaped house
belongs in the north: the magariya ..." - and the engine's claims index marks the code that draws every house as one straight
rectangle DRIFTED against it (`HousesMixin.house#farmhouse glyph`). A deliberate deviation is the SETTING differing from history
by canon or a GM ruling (the record's CLAUDE.md, the four classes); no ruling makes the stable wing one, and the GM ruled the
farmhouse's single roof form, the same kind of case, "NOT a deliberate convention" (2026-10-04) - a drift left on the claims
report to be fixed.

## Your items (one drawing page; no new registry key)

- 0028's drawing page: the magariya group says what is true - the stable wing belongs to the L-shaped plan, one of the
  farmhouse's regional plan forms at How our maps draw farmhouses (0029's drawing page, linked), and the maps place the byre in
  the forms at How our maps draw and place byres; drop the "deliberate deviation". Do not describe engine code or the claims
  report on the page. Fix the group's lead line and its `Evidence:` comment to match. Any other page calling leaving out the
  wing a deviation (grep `research/questions/` for "magariya") is yours too.

Do NOT edit any modal file or any engine code.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0028"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G4 in progress (0028 magariya) | 2026-10-04"`.
2. Edit the fragment (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
3. Write `specs/319-modal-writeups/briefs/g4-handoff.md` (one `- SECTION=<NNNN>/<id>` line and a sentence), commit only your
   files (message beginning `319 G4:`), do not push. Your last message is one paragraph.
