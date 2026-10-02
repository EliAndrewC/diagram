# Brief - feature 293, task R: the servants' quarters, session 1: research and write

You are a FRESH session. This brief is the whole of what you need; do not read the feature's spec or plan to orient -
everything you read stays in your context and is paid for again on every later turn. Work in the clone you were started
in (`git rev-parse --show-toplevel`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all (it auto-loads when you read a research file). No one will answer a question during this session: where you would ask
the GM, record the question and the default you took in the handoff, and carry on.

**Ad-hoc agents.** Dispatch any ad-hoc work that checks or judges (a verdict, a review, a comparison) that no defined agent
covers to the `adhoc-judge` agent. Dispatch ad-hoc reading, fetching, translating or extracting as you normally would.

**The question.** Ubame's magistracy sheet draws its servants' quarters - a nagaya of four bays - with ONE door for the four
bays. The open item (`.claude/skills/diagram/future-work/compounds.md`, "Ubame: the servants' quarters have one door for
four bays") asks: in a samurai compound of the Edo period (or its Chinese counterpart before 1912), was the servants'
rowhouse one dormitory behind sliding partitions, with one door, or did each household or bay have a door of its own?
Answer it for the record. You do not change the Ubame sheet, the engine or any map: the record says what was found and what
the sheet should draw; changing the sheet is later work.

**Where it goes.** The research page is `buildings`. The nearest questions already on it are 060 (staff housing spans a
real spectrum), 750 (how big was the rowhouse a magistrate's staff lived in) and 900 (how were the rooms of a compound's
barracks divided) - read what they say first and extend one of them if the answer belongs there, or write ONE new question
at a free prefix from 910 to 990.

**Read narrowly.** For a few notes of a question use `make notes Q=<NNNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Coordination files are read by line, never whole**: `make lines FILE=<f> KEY=<regex>` and `make append FILE=<f>
LINE="<text>"`. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="buildings"`; a section another
feature holds is researched but not edited (put the text it owes in the handoff). Lines for 293 that you did not write are not
claims on your work - ignore them. Then `make append
FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="293 | task R in progress (buildings, servants' quarters) | <date>"`.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`).

## Your items

- R1 **The servants' quarters**: one dormitory behind sliding partitions with one door, or a door a household - researched,
  written on the buildings page as described above, and handed off.

## The procedure (session 1: research and write)

1. **Canon first, once.** If any part is a question of the SETTING, ask the GM's canon with ONE call naming every term:
   `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`).
2. **Search.** Japan before 1868 first (Edo samurai-residence plans, surviving buke yashiki and nagaya, museum and
   prefecture pages, kotobank, jawiki, J-STAGE open papers, period plans and floor plans of nagaya and 長屋門 / 中間部屋 /
   足軽長屋), China before 1912 as the counterpart (servants' quarters of official residences and courtyard houses). Search in
   Japanese and Chinese as well as English. Save every candidate page with `make source-pages OUT=/tmp/l7r-check/293-r-pages
   URLS="<u1> <u2> ..."` and grep them yourself. Keep a list of every search you ran (terms, language, where, date).
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved directory and
   each claim verbatim. Write only from what it returns READ with a quote. Judge each new source with `source-applicability`
   before its numbers or forms reach the record's rule.
4. **Decide.** One form attested, both attested (then it is a knob the maps roll per compound, with the evidence for each), or
   the record silent (an absence note saying what was searched). Say what the Ubame sheet should draw.
5. **Write** the finding for a casual reader, per `research/CLAUDE.md`: the question as the heading, footnotes that quote the
   source (in English translation, marked as one, the original after), absence notes where nothing was found, glossary terms for
   new words, and the four-class label for the drawing decision. First `Read` every file you will change ALL IN ONE MESSAGE, then
   `Edit`/`Write`. Then in `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and
   `python3 scripts/check-question-size.py` from the clone root.
6. **Hand off.** Write `handoffs/293/R-handoff.md`: one line per new or changed question as
   `- SECTION=buildings/<NNN>`, one per new registry key as `- KEY=<key>`, then the outcome in a few sentences (what the record now
   says, what the Ubame sheet should draw, what was searched and when), then anything left open. Commit (a message beginning
   `293 R:`). Do NOT run the record checks and do NOT push - the next session checks in a fresh context. Your last message is
   one paragraph saying what you wrote.
