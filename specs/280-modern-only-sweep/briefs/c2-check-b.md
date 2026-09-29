<!-- page-load: kind=check -->
# Brief - feature 280 (the modern-only sweep), group C2: cities/river-cities: offtake angles, private landings and the boatmen's shrine, session 2b: check and apply

You are a FRESH session for one part of feature 280. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-supplemental-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**What the feature is for.** The GM, 2026-09-28: *"We should eliminate anything which is only modern"* and *"We should
avoid anything that appears only on modern lists."* Each item below is a form a map draws (or a figure it uses) that an
audit found MAY be attested only in the modern period. Your job is to find out, searching for a PREMODERN attestation
FIRST, and to record what you find. You do not change the engine or the maps: the eliminations are a later phase.

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**A held section is researched, never edited, and never skipped.** A section is HELD when the claims file names it
in progress for another feature (religion-and-death 124-129 are feature 279's while its line is open), or when
feature 269 rewrote it and has not landed - whatever 269's claim line says, "done, committed in clone" included: any
output from `git -C /diagram/.clones/diagram-supplemental log origin/main..HEAD --oneline -- .claude/skills/diagram/research/<page>/<NNN>-*`
means unlanded. For an item on a held section, do the research all the same, but do not edit the section: put the
outcome in the handoff as usual, with `OWED-TO <feature>` and the exact text the section owes (the finding and its
footnotes), so the orchestrator applies it once the hold clears. No item leaves your session without an outcome.
**Coordination files are read by line, never whole** (feature 274): `make lines FILE=<f> KEY=<regex>` and
`make append FILE=<f> LINE="<text>"`. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md
KEY="<each page your items name>"` (a held section is handled as above, never skipped); then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram supplemental (diagram-supplemental-2) | 280 |
group C2 in progress (<the sections>) | <date>"`. Read only your own lines of a handoff (`make lines
FILE=<handoff> KEY="SECTION=<yours>|KEY=<yours>"`), and add to a checks report with `make append`.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`), never "the highest + 10" by eye; a write session's eleventh registry key is refused - then
follow its message (write the unreached items to `$L7R_CONTINUE` as a brief of this same shape, commit, stop).

Session 1 researched this group and committed; its handoff is `specs/280-modern-only-sweep/briefs/c2-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** PAGE=cities/river-cities SECTION=070, PAGE=cities/river-cities SECTION=600
**Your registry keys:** KEY=hamura-tamagawa-josui, KEY=kotobank-suitengu, KEY=sumidagawa-jinja-jawiki

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE=<page> SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format`, each agent naming its own MANIFEST.md and nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`. An ABSENCE note that says what was searched is checked as
   one: its search is stated, dated and specific.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source
   `source-applicability` rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess), the key
   is listed in your report, and where that turns a PREMODERN-ATTESTED item into MODERN-ONLY, say so in the report.
   Then `make glossary` if a term was added, `make record && make citations` and the four record tests ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`). A
   PARTIAL left after it is labeled honestly in the note and left.
4. **Commit** with a message beginning `280 C2 check:`; do not push.
5. **Report.** Append to `specs/280-modern-only-sweep/briefs/c2-checks.md` (with `make append`) one line per question and key: its
   verdicts (quote-check, record-format, source-applicability), any outcome the checks changed, and anything left
   open. Your last message is one paragraph.
