# Brief - feature 269 (the research backfill), group A1: archetypes: dike-pond, session 2b: check and apply

You are a FRESH session for one part of feature 269. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-supplemental`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 265: buildings 010, 070, 150, 170, 210;
cities/river-cities 010-040; urban-features 010, 012, 020, 030, 050, 060, 070, 080, 160; ways 020; towns 040, 080,
090, 100, 130; cities/capitals 040, 150, 155, 330-336. Feature 267: buildings 240-640, vegetation 170-200,
religion-and-death 220-260, fields 220-240. Feature 268: religion-and-death 080-126. Where a finding OWES one of those
a correction, say exactly what in the handoff; the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `python3 /diagram/.clones/.tools/reserve-prefix.py registry <key> --root /diagram/.clones/diagram-supplemental` (or `glossary "<term>"`) prints the stub's path; fill it in.
**Claims first (FR-011).** Before any research, read `/diagram/.clones/RESEARCH-CLAIMS.md`. Skip any item of yours
that another session has claimed since, and name it in the handoff. Then set 269's line there to say group A1 is
in progress; edit only that line.

Session 1 researched this group and committed; its handoff is `specs/269-research-backfill/briefs/a1-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** PAGE=archetypes SECTION=220, PAGE=archetypes SECTION=230
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
4. **Commit** with a message beginning `269 A1 check:`; do not push.
5. **Report.** Append to `specs/269-research-backfill/briefs/a1-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
