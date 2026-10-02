<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R10, session 2: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 reconciled 0081 and ways/100 on a field road's width (the 3-shaku figure attributed to Ieyasu's testament, and its standing) and said how the map's 3 and 5 ft widths stand beside it. Its handoff is
`specs/291-homestead-grove-sides/briefs/r10-handoff.md`.

**Your questions:** Q=0081; PAGE=ways SECTION=100
**Your registry keys:** any the handoff names as new

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle Q=<NNNN> FOR=quote-check` for
   `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md; and `source-applicability` (`make check-bundle KEY=<k>`) on any registry key the handoff names as new.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R10 check:`); do not push.
4. Append one line to `specs/291-homestead-grove-sides/briefs/r10-checks.md` (with `make append`). Your last message is
   one paragraph.
