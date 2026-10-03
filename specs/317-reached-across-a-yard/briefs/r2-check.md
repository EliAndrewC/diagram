<!-- page-load: kind=check -->
# Brief - feature 317 (reached across a yard), group R2, session 2: check and apply

You are a FRESH session for one part of feature 317. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-performance`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 rewrote 0081's drawing page (`research/questions/0081-village-lanes.drawing.html`) to say what the maps
now draw: within a share rolled per nucleated settlement (0-25%, a GUESS), a household with no way of its own may stand against a
neighbor's land and be reached across the neighbor's yard, the walk not drawn; and it footnoted (or noted as an absence) one claim
on the question page and added the 1605 highway widths to a registry entry's uses. Its handoff is
`specs/317-reached-across-a-yard/briefs/r2-handoff.md`.

**Your questions:** Q=0081

## The procedure (check, apply)

1. `make record-owed` (in `.claude/skills/diagram`) names every unit the delta owes. In the background, in one message, one agent
   per owed unit, each from its own bundle (`make check-bundle Q=0081 FOR=<check>`, `make check-bundle KEY=<key>
   FOR=source-applicability` for a key owed it, and `make check-bundle Q=0081 FOR=entry-drift KIND=<class>` for each modal
   entry-drift is owed for), each naming its own MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message. Then
   `make record && make citations` and the four record tests once; answer each check with `make record-checked`.
3. Re-check only what moved, until `make record-owed UNANSWERED=1` says no record check is owed. Commit only your files (message
   beginning `317 R2 check:`); do not push.
4. Append one line per check to `specs/317-reached-across-a-yard/briefs/r2-checks.md` (with `make append`). Your last message is
   one paragraph.
