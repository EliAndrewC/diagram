# Brief - feature 250: split ONE research question under the size cap

You are a FRESH session with one job: the question `.claude/skills/diagram/research/vegetation/150-bamboo-how-common-where-it-stood-and-how-to-show-it.html` is 28,711 bytes with its notes, over the 20,000-byte cap
(`scripts/check-question-size.py`, feature 250 D14). Split it. Work in this clone (`/diagram/.clones/diagram-research`); its CLAUDE.md files
apply; read the rule as written in `.claude/skills/diagram/research/CLAUDE.md`, "A question has a size", and nothing
else to orient.

1. Read the question and its notes (`.claude/skills/diagram/research/vegetation/150-bamboo-how-common-where-it-stood-and-how-to-show-it.notes.html`). Find its TOPICS - the separate things a map reader might ask about -
   not its entry parts: a finding stays with the decision it drove and with the departures that qualify it.
2. Split it: each topic its own question, a free prefix after `150` (they count by ten), an `<h2 id>` that is the
   question a reader would ask, the Grounds/Evidence comments that apply, its own `Sources:` line naming exactly the
   keys its notes quote, and the notes its sentences cite moved into its own `.notes.html` - every note in exactly one
   place, none rewritten. Keep the ORIGINAL question's heading and id on the part that carries its main finding (map
   modals and links point at it). The sentences that join the parts POINT - a link and what the other question is
   about - and never restate the other part's evidence.
3. Every part under 20,000 bytes with its notes. If a part cannot get there without stripping a finding of what it
   needs, stop and say so rather than splitting it further.
4. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py
   tests/interactive/test_record.py"`, and `python3 ../../../scripts/check-entry-headings.py`. Commit. Do not push.
5. Report in one paragraph, which the session that dispatched you will use to judge the split: the questions you
   made, each one's size, and for each part WHAT IT RELIES ON FROM THE OTHERS - and whether a reader, or a check that
   reads that part alone, has what it needs.
