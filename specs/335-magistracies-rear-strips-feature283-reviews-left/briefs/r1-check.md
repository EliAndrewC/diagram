<!-- page-load: kind=check -->
# Brief - feature 335, R1, session 2: check and apply

You are a FRESH session for one part of feature 335. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-magistracies`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 recorded that a guest's roji carries no well (0104's drawing page) and the one door convention -
wholly inside the building, flush to the wall it opens through (0117's drawing page). Its handoff is
`specs/335-magistracies-rear-strips-feature283-reviews-left/briefs/r1-handoff.md`. A `Research:` claim in the engine that cites a
changed block is owed a claims re-check at the push, not by you: leave it. Do not edit any sheet, modal or engine file.

**Your questions:** the ones the handoff names.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the FOREGROUND, in one message (a headless session is never woken by a
   background agent), one agent per owed unit, each from its own bundle (`make check-bundle Q=<NNNN> FOR=<check>`, `make
   check-bundle KEY=<key> FOR=source-applicability` for a key owed it, and `make check-bundle Q=<NNNN> FOR=entry-drift KIND=<class>`
   for each modal entry-drift is owed for), each naming its own MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message. Then
   `make record && make citations` and the four record tests once; answer each check with `make record-checked`.
3. Re-check only what moved, until `make record-owed UNANSWERED=1` says no record check is owed. Commit only your files (message
   beginning `335 R1 check:`); do not push.
4. Append one line per check to `specs/335-magistracies-rear-strips-feature283-reviews-left/briefs/r1-checks.md` (with
   `make append`). Your last message is one paragraph.
