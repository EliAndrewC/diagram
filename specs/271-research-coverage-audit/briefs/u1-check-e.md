# Brief - feature 271 (the research coverage backfill), group U1: urban-features: public fixtures and works on the map, session 2e: check and apply

You are a FRESH session for one part of feature 271. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-research-3`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 267: buildings 240-640, vegetation 170-200,
religion-and-death 220-260, fields 220-240 (magistracy and compound buildings); feature 268: religion-and-death 080-126;
feature 270: the country/village shrine hall's size; feature 269: every section its inventory
(`/diagram/.clones/diagram-supplemental/specs/269-research-backfill/inventory.md`) names, and its new ranges (fields
250-360, homesteads 250-360, water 290-360, vegetation 210-290, archetypes 200-270, religion-and-death 270-330,
cities/defenses 100-140, cities/government 100-140, cities/fabric 160-190, cities/hinterland 060-090, cities/sizing
030-050, settlements 030 and 090-110). Where a finding OWES one of those a correction, say exactly what in the handoff;
the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.
**Claims first (FR-002).** Before any research, read `/diagram/.clones/RESEARCH-CLAIMS.md`. Skip any item of yours
that another session has claimed since, and name it in the handoff. Then set 271's line there to say group U1 is
in progress; edit only that line.

Session 1 researched this group and committed; its handoff is `specs/271-research-coverage-audit/briefs/u1-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** PAGE=urban-features SECTION=120
**Your registry keys:** KEY=mlit-tokaido-kosatsuba, KEY=mlit-tokaido-qa-kosatsuba, KEY=kotobank-kosatsu, KEY=shiojiri-iwadare-kosatsuba, KEY=nakatsugawa-kosatsuba, KEY=kotobank-tsujiido, KEY=seiyo-karihama-ido, KEY=kotobank-tsurube-ido, KEY=hiratsuka-tsurube, KEY=yokkaichi-hanetsurube, KEY=ndl-crd-tsurube-ido, KEY=bunka-tokugawaen-ido, KEY=whb-gujing, KEY=motoyashiki-kiln-jawiki, KEY=kitakyushu-saienba-kiln, KEY=umakato-noborigama, KEY=mikawachi-noborigama, KEY=kotobank-hisabetsu-buraku, KEY=joetsu-hisabetsu-history, KEY=uw-edo-manifold

**Coordination with the other sessions** - hold your questions to these while checking; where one duplicates another
session's section, cut it to a pointer and cite that section:
COORDINATION (A132): 267 R25 kept the magistracy bench's own board apart from the town's kosatsuba - cite it for the distinction

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
   `specs/250-close-the-record-checks/owed-verdicts.md`:
   `- <Class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. Then
   `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py
   tests/interactive/test_compound_kinds.py"`.
5. **Commit** with a message beginning `271 U1 check:`; do not push.
6. **Report.** Append to `specs/271-research-coverage-audit/briefs/u1-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
