<!-- page-load: kind=split -->
# Brief - feature 291 (how many sides a homestead grove takes), group R4: vegetation/030 back under the size cap

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all ("A question has a size").

**What is wrong.** `vegetation/030` ("Does a shelter belt wrap the settlement? No - it stands on one or two windward
sides") is 20,226 bytes with its notes, over the 20,000 cap, since this feature added the GM's 2026-09-29 ruling to it
(the farmstead's own grove now rolls its sides; the village belt stays on one or two windward sides). `make quick`
fails on it.

**Your questions:** PAGE=vegetation SECTION=030

## The procedure

1. Read the fragment and its notes in one message.
2. Bring it under the cap WITHOUT cutting a finding: first tighten its own prose where it restates what another entry
   already holds (the farmstead grove's rule is at `homesteads/715`, "Which sides of the house did a homestead grove
   take?" - point there, do not restate it); if that is not enough, split it along its topics per the record's
   `CLAUDE.md` (each part its own question, heading and Sources line; the joins point, they do not restate; a finding
   stays with its decision), and repoint every inbound link to a moved anchor - the modal classes' `Entry:` tags
   included (`grep -rn "shelter belt wrap" .claude/skills/diagram/l7r/diagram/interactive/classes/`), which
   `scripts/check-entry-headings.py` enforces.
3. In `.claude/skills/diagram`: `make record && make citations`, the four record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`), and `python3 scripts/check-question-size.py` from the clone root.
4. Check what moved, in the background: `make check-bundle PAGE=vegetation SECTION=<NNN> FOR=record-format` for
   `record-format` on each question you changed or made (and `FOR=quote-check` for `quote-check` on any note that moved).
   Apply with `make apply-edits FROM=<output_file>`; re-run the tests once.
5. Commit only your files (message beginning `291 R4:`); do not push. Append one line to
   `specs/291-homestead-grove-sides/briefs/r4-checks.md` (with `make append`): the sizes before and after, what moved,
   the verdicts. Your last message is one paragraph.
