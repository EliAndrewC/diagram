# Brief - feature 291 (how many sides a homestead grove takes), group R1: the homestead grove's shape, session 1: write

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan to orient. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's
CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all (it auto-loads when you read a research file).

**What the feature is for.** The record says, flatly, that before 1868 a farmstead's grove went round the whole house
and that the windward-only grove is the modern form. Its own evidence does not bear that out, and the GM asked for the
record to be corrected "so that they cite the evidence correctly", and for the grove's sides to become a knob. The
evidence, all of it ALREADY in the record (no new source is needed; a new one is welcome only if you find it while
checking, through the procedure below):

- **Izumo plain, before Meiji: the full ring.** `yashikirin-jawiki`, in its section on the Izumo tsuijimatsu: 「明治時代以前には家の全周を囲っていたが、水害の減少と建築様式の変化から北と西側だけをカバーする鉤型の形状へと変化した。」 One region; the change is tied to flood damage lessening. (quoted at `homesteads/710`'s note `yashikirin-jawiki-9`)
- **Takada domain, 1625**: sugi "around the homestead", camellia and sasa on the south (`yashikirin-jawiki`, note `yashikirin-jawiki-8` at `homesteads/710`). Read as written: it does not say the sugi closed a ring, and it plants the south differently.
- **Sendai plain: north and west, lacking the south or east, for centuries.** `irie-2020-igune` (quoted at `0072`'s notes): the grove "is formed on the north or the west side ... and often lacks the south or the east side" (Nakajima 1963, via Irie), and trees were planted "in many layers on the north side and the west side" under Date Masamune, the first lord of the Sendai domain, on the new-field homesteads, and "maintained as a windbreak forest for more than several hundred years" (via a 1993 local society). That dates the two-sided form to the early Edo period.
- **Tonami plain: open on the east front.** `kashima-kainyo-1987` (the grove "as it has been": tall sugi from the south round to the west, hackberry, alder and some bamboo from the west round to the north, flowering and fruit trees on the east; note `kashima-kainyo-1987-8` at `0036`) and `tonami-yashikirin-haichi` (little grove on the east front; at `homesteads/046`). Undated.
- **Okinawa: north and east** (`isa-auf-fukugi-2011`, at `0036`).
- **No source counts farmsteads by grove shape.**

**The GM's rulings, 2026-09-29, to quote.** The first: *"because it does sound as if groves completely surrounding
farmhouses was a thing, then that should indeed be a tunable knob. It seems like two sides is the minimum. Three sides
would sometimes be the case, and all four sides would also sometimes be the case."* The session then proposed the
weights and the rest of the decision below, and the GM: *"Your suggestions sound great, so yes, please go with all of
that. Both the percentage split and the flood ground adjustment."*

**The decision the record states** (every number a GUESS, labeled as such; the rule stated in plain words, no engine identifier in the visible text):

- The farmstead grove's sides are rolled once per settlement, the same at every farm (grove shape is reported as regional custom): two sides 50%, three sides 30%, all four sides 20%. Two is the windward pair (the form reported in the most regions, and the only one with a general statement and an early-Edo date); three leaves open only the FRONT - the lee side where the yard and the way in are (Tonami's open east front); four closes the ring (Izumo's).
- Where the farms stand on flood-prone ground - fields of reclaimed low ground behind dikes, or houses on a dike - four sides rises to 40% and the other two keep their 5 : 3 ratio (37.5 / 22.5 / 40), because the Izumo ring's own stated cause was flood; a map may declare its ground either way.
- The windward arms are the deep stand; the other planted sides a thinner band of lesser trees - Tonami's pattern (tall cedar on the windward faces, lesser trees elsewhere); for the full ring this is a GUESS, and the thinner depth is a GUESS.
- The village's shelter belt is a different thing and is NOT this knob: it stays on one or two windward sides.

## Your items

- **0036** ("Homestead groves (yashikirin) - the real scale and prevalence"): the sentence "today wrapping the windward faces as a belt, where before 1868 it went round the whole house" rests on the Izumo passage alone and generalizes it. Rewrite it so the shapes are attributed (the evidence above, briefly - 710 carries the detail) and point at 710 for the shape; its "Before 1868" bullet likewise. Keep the rest of the entry (the size findings) as it is. The "Which faces the belt takes is rolled per map" sentence is about the WINDWARD side and stays.
- **homesteads/710** ("Was the homestead grove there before 1868, and what size and shape was it?"): the paragraph "Nor is a belt on the windward arms only" and "The decision" say the premodern record puts the grove round the homestead. Rewrite the shape half: the full ring is Izumo's (with its flood cause), the Takada order read as written, the Sendai two-sided form with its early-Edo planting (copy the `irie-2020-igune` notes from `0072` with their quotes), Tonami's open front, no count of shapes anywhere; then the decision above with the GM's rulings quoted. The size half (the Edo documents, the 1987 count) stays.
- **homesteads/480** ("What marked the edge of a farmstead ..."): its knob lists "a grove on the north and west, which also serves as the windbreak" as one edge form. Say the grove takes the sides its settlement rolls (two, three or four - pointing at 710), and leave the rest.

The village shelter-belt entries on the vegetation page are group R2's, not yours.

## The procedure (session 1: write)

1. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="homesteads"`; a section another feature holds in progress is not edited - put the exact text it owes in the handoff with `OWED-TO <feature>`. Then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram readability (diagram-readability-2) | 291 | group R1 in progress (0036, 480, 710) | 2026-09-29"`.
2. **Read narrowly**, all in one message: the three fragments and their `.notes.html`, and the `irie-2020-igune` notes of `0072` (`make notes PAGE=vegetation SECTION=030 KEYS=irie-2020-igune,irie-2020-igune-2` in `.claude/skills/diagram`, or grep the notes file for `irie`). Every quote you write is COPIED from a note already in the record, character for character - never from memory, never retranslated.
3. **Write.** Edit the fragments (never an assembled page). Footnotes: `<sup class="fn" data-note="<key>"></sup>` in the prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it; a repeat of one work in a section is `key-2`, `key-3`, ... (check which suffixes the section already uses). The GM's rulings are quoted in the prose and need no footnote (the GM's words are canon). Every GUESS labeled. Written for a casual reader: no history of the document ("used to say", "corrected"), session notes (feature numbers, identifiers) only in HTML comments. Keep each question with its notes under 20,000 bytes.
4. **Build and test**, in `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; and `python3 scripts/check-question-size.py` from the clone root.
5. **Hand off.** Write `specs/291-homestead-grove-sides/briefs/r1-handoff.md`: one line per changed question as `- SECTION=homesteads/<NNN>`, one per new registry key as `- KEY=<key>` (probably none), then a sentence per question of what it now says, and anything left open. Commit (a message beginning `291 R1:`) - `git -C` with explicit paths, only the files you changed. Do NOT run the record checks and do NOT push. Your last message is one paragraph saying what you wrote.
