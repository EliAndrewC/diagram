<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R1, session 2b: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What the feature is for.** The record said, flatly, that before 1868 a farmstead's grove went round the whole house.
Session 1 rewrote the homestead grove's entries so each shape is attributed to its region, and made the grove's sides
a knob rolled per settlement (two, three or four). Its handoff is `specs/291-homestead-grove-sides/briefs/r1-handoff.md`
- read only your own lines (`make lines FILE=<handoff> KEY="SECTION=homesteads/480"`).

**Your questions:** PAGE=homesteads SECTION=480
**Your registry keys:** none

## The procedure (check, apply)

1. **Check, all in one message, in the background**: `make check-bundle PAGE=homesteads SECTION=480 FOR=quote-check`
   for `quote-check`, and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each agent naming
   its own MANIFEST.md and nothing else.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. Then
   `make record && make citations` and the four record tests (`make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`) ONCE.
3. **Re-check ONCE, only what moved.** A PARTIAL left after it is labeled honestly and left.
4. **Commit** only the files you changed (`git -C` with paths), message beginning `291 R1 check:`; do not push.
5. **Report.** Append to `specs/291-homestead-grove-sides/briefs/r1-checks.md` (with `make append`) one line: its
   verdicts and anything left open. Your last message is one paragraph.
