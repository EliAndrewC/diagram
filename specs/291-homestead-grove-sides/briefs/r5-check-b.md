<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R5, session 2b: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 added to `homesteads/150` that no village belt is drawn where the farms carry their own
groves, and that a linear hamlet's farms front a street along the road; and to `vegetation/154` that a farm drawn with
its own grove carries its bamboo inside that grove. Its handoff is `specs/291-homestead-grove-sides/briefs/r5-handoff.md`.

**Your questions:** PAGE=homesteads SECTION=150; PAGE=vegetation SECTION=154
**Your registry keys:** none

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle PAGE=<p> SECTION=<q> FOR=quote-check` for
   `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R5 check:`); do not push.
4. Append one line per question to `specs/291-homestead-grove-sides/briefs/r5-checks.md` (with `make append`). Your
   last message is one paragraph.
