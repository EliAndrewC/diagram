# Brief - feature 291 (how many sides a homestead grove takes), group R2: the village belt and the way through, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan to orient. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's
CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What the feature is for.** The GM ruled on 2026-08-29 for the north-and-west hook and against a knob for the grove's
shape, and the village belt's entry records that ruling. On 2026-09-29, after being shown that the full ring is
reported only for the Izumo plain while the Sendai grove stood on two sides for centuries and the Tonami grove was
open on its east front, the GM reversed it for the FARMSTEAD grove: *"because it does sound as if groves completely
surrounding farmhouses was a thing, then that should indeed be a tunable knob. It seems like two sides is the minimum.
Three sides would sometimes be the case, and all four sides would also sometimes be the case."* - and, approving the
proposed weights, the flood-ground adjustment and the rest: *"Your suggestions sound great, so yes, please go with all
of that. Both the percentage split and the flood ground adjustment."* The proposal the GM approved included that "the
homestead grove only" is the knob and the village's shelter belt stays on one or two windward sides. The farmstead
grove's rule itself is written in the homestead grove's own entry, "Was the homestead grove there before 1868, and
what size and shape was it?" (session R1 wrote it; point there, do not restate it).

## Your items

- **0072** ("Does a shelter belt wrap the settlement? No - it stands on one or two windward sides"): its
  paragraph "A knob the record handed us, and the ruling that declined it" records the 2026-08-29 ruling as deciding
  the grove's shape. Keep that ruling, quoted, and add the 2026-09-29 ruling after it, quoted: it reverses the first for
  the farmstead's own grove, whose sides are now rolled (pointing at the homestead grove's entry); the VILLAGE belt
  stays on one or two windward sides, on this entry's own evidence (the Chinese separate patches; the Sendai grove on
  the north or west) and by the GM's approval of "the homestead grove only". The first ruling's second reason - that a
  belt's shape tells the reader where the wind comes from - still holds for the belt, and the farmstead grove keeps it
  too, its windward arms being the deep ones. Say where "Both forms are reported" treats the Izumo ring as a general
  alternative that it is one region's. Nothing about the belt's rule changes.
- **vegetation/620** ("How did a lane get through a belt?"): "A planted run was continuous. Before the Meiji era the
  Izumo homestead grove enclosed the whole circuit of the house" is right about Izumo; make sure it reads as Izumo's and
  not as all groves', and add that a farmstead grove rolled on all four sides is broken once, at the middle of its
  front, for a way in about 12 ft wide - a physical necessity (the farm must be reached), the width a GUESS since no page
  read gives an opening's width - pointing at the homestead grove's entry.

## The procedure (session 1: write)

1. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="vegetation"`; a section another feature
   holds in progress is not edited - put the exact text it owes in the handoff with `OWED-TO <feature>`. Then
   `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R2 in progress (0072, 620) | 2026-09-29"`.
2. **Read narrowly**, all in one message: the two fragments and their `.notes.html`. Every quote you write is COPIED
   from a note already in the record, character for character. The GM's rulings are quoted in the prose and need no
   footnote.
3. **Write.** Edit the fragments (never an assembled page). Written for a casual reader: session notes only in HTML
   comments; the two rulings are given in order as the GM's decisions, not as a history of the page. Every GUESS
   labeled. Keep each question with its notes under 20,000 bytes.
4. **Build and test**, in `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; and `python3 scripts/check-question-size.py` from the clone root.
5. **Hand off.** Write `specs/291-homestead-grove-sides/briefs/r2-handoff.md`: one line per changed question as
   `- SECTION=vegetation/<NNN>`, then a sentence per question of what it now says, and anything left open. Commit
   (message beginning `291 R2:`) - only the files you changed. Do NOT run the record checks and do NOT push. Your last
   message is one paragraph saying what you wrote.
