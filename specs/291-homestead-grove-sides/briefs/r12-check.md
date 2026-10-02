<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R12, session 2: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 researched a row farm's dry-field holding beside its paddy and which way its grove faced when its street ran on its windward side, and wrote the findings into homesteads/156 (or a question beside it). Its handoff is
`specs/291-homestead-grove-sides/briefs/r12-handoff.md`.

**Your questions:** PAGE=homesteads SECTION=156 (and any new question the handoff names)
**Your registry keys:** any the handoff names as new

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle Q=<NNNN> FOR=quote-check` for
   `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md; and `source-applicability` (`make check-bundle KEY=<k>`) on any registry key the handoff names as new.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R12 check:`); do not push.
4. Append one line to `specs/291-homestead-grove-sides/briefs/r12-checks.md` (with `make append`). Your last message is
   one paragraph.
