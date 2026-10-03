<!-- page-load: kind=check -->
# Brief - feature 317 (reached across a yard), group R1, session 2: check and apply

You are a FRESH session for one part of feature 317. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-performance`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 rewrote the bullet "Was every house in a clustered village reached by a lane?" on
`research/questions/0081-village-lanes.html` (answer: not always - no page states a lane to every house as a rule; customary
passage over a neighbor's land cited from Wigmore 1892; Morse's Enoshima alleys to the houses in the rear) and added two registry
keys, `wigmore-1892-servitudes` and `morse-1886-homes`. Its handoff is `specs/317-reached-across-a-yard/briefs/r1-handoff.md`.
Source-reader already ran (round 2: 14 + 4 READ, 0 CONTRADICTED).

**Your questions:** Q=0081
**Your registry keys:** wigmore-1892-servitudes, morse-1886-homes

## The procedure (check, apply)

1. `make record-owed` (in `.claude/skills/diagram`) names every unit the delta owes. In the background, in one message, one agent
   per owed unit, each from its own bundle (`make check-bundle Q=0081 FOR=quote-check`, `... FOR=record-format`,
   `make check-bundle KEY=<key> FOR=source-applicability` for each key, and `make check-bundle Q=0081 FOR=entry-drift
   KIND=<class>` for each modal entry-drift is owed for), each naming its own MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message. Then
   `make record && make citations` and the four record tests once; answer each check with `make record-checked`.
3. Re-check once only what moved. Commit only your files (message beginning `317 R1 check:`); do not push.
4. Append one line per check to `specs/317-reached-across-a-yard/briefs/r1-checks.md` (with `make append`). Your last message is
   one paragraph.
