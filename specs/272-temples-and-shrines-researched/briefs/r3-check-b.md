# Brief - feature 272 (temples and shrines researched), group R3: the village temple and wayside shrines, session 2b: check and apply

You are a FRESH session for one part of feature 272. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-shrines-2`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md`
above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** religion-and-death 130-206 and new 270-300 (feature 269's
burial group R1, in `/diagram/.clones/diagram-supplemental`); religion-and-death 220-260 (feature 267); every page
other than religion-and-death. Where a finding OWES one of those a correction, say exactly what in the handoff; the
orchestrator sends it to the owner. Other groups of THIS feature run beside you in sibling clones: stay inside your
own sections and range.
**FR-007 - the drawn country shrine.** For EVERY finding, say in the handoff whether it contradicts the Hoshigaoka
country-shrine sheet or its village map: the sheet (`pool/country-shrines/hoshigaoka-shrine/`) draws an open grove
with no fence or wall round the precinct, torii 12 ft apart on the approach, a 66 by 32 ft one-roof building (the
villagers' hall with the country monk's kitchen and dwelling at its ends), a stone basin and a sacred tree by the
approach; the village (`legacy-hand-authored-pool/villages/hoshigaoka/`) carries that shrine and no temple of its own.
A line per contradicting finding, `FR-007: <finding> - contradicts <what is drawn>`, or `FR-007: none`. Do NOT edit
the sheet or the map; the orchestrating session applies what contradicts them.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.

Session 1 researched this group and committed; its handoff is `specs/272-temples-and-shrines-researched/briefs/r3-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** PAGE=religion-and-death SECTION=520, PAGE=religion-and-death SECTION=530
**Your registry keys:** none - the last group has them

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE=<page> SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format`, each agent naming its own MANIFEST.md and nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source
   `source-applicability` rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess), and the
   key is listed in your report. Then `make glossary` if a term was added, `make record && make citations` and the four
   record tests ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`). A
   PARTIAL left after it is labeled honestly in the note and left.
4. **Owed modals.** `python3 scripts/_entry_owed.py` (from the clone root) names each map or sheet modal whose `Entry:`
   points at a question you changed. For each pair on YOUR questions: `make check-bundle PAGE=<page> SECTION=<NNN>
   KIND=<Class> FOR=entry-drift` (a class name two modules share is qualified: `household.Well`), one `entry-drift`
   agent per bundle, apply with `make apply-edits`, and append one line per pair to
   `specs/272-temples-and-shrines-researched/briefs/owed-verdicts.md`:
   `- <Class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. Then
   `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py
   tests/interactive/test_compound_kinds.py"`.
5. **Commit** with a message beginning `272 R3 check:`; do not push.
6. **Report.** Append to `specs/272-temples-and-shrines-researched/briefs/r3-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
