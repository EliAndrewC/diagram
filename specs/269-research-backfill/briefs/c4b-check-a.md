# Brief - feature 269 (the research backfill), group C4B: cities/sizing, session 2a: check and apply

You are a FRESH session for one part of feature 269. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-supplemental`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 265: 0090, 070, 150, 170, 210;
0175, 0176; 0190, 012, 020, 030, 050, 060, 070, 080, 160; 0081; towns 040, 080,
090, 100, 130; cities/capitals 040, 150, 155, 330-336. Feature 267: 0091, 0093, 0094, 0102, 0103, 0104, 0105, 0106, 0107, 0108, 0109, 0110, 0111, 0112, 0117, 0239, 0076,
0240, fields 220-240. Feature 268: 0215, 0220, 0221, 0222, 0223. Where a finding OWES one of those
a correction, say exactly what in the handoff; the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`); a write session's eleventh registry key is refused - then follow its message (write the
unreached items to `$L7R_CONTINUE` as a brief of this same shape, commit, stop).
**Coordination files are read by line, never whole** (feature 274): `make lines FILE=<f> KEY=<regex>` and
`make append FILE=<f> LINE="<text>"`. **Claims first (FR-011):** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md
KEY="<each page your items name>"`; skip any item another session has claimed since, naming it in the handoff; then
`make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram supplemental | 269 | group C4B in progress | <date>"`.
Read only your own lines of a handoff (`make lines FILE=<handoff> KEY="SECTION=<yours>|KEY=<yours>"`), and add to a
checks report with `make append`.

Session 1 researched this group and committed; its handoff is `specs/269-research-backfill/briefs/c4b-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** PAGE=cities/sizing SECTION=030, PAGE=cities/sizing SECTION=010
**Your registry keys:** KEY=satsuma-gaijo-datamax, KEY=reimeikan-satsuma-gaijo, KEY=sendai-castles-jawiki

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
4. **Commit** with a message beginning `269 C4B check:`; do not push.
5. **Report.** Append to `specs/269-research-backfill/briefs/c4b-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
