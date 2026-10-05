<!-- page-load: kind=check -->
# Brief - feature 319 (modal write-ups), H4, session 2: check and apply

You are a FRESH session for one part of feature 319. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-html-2`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 settled record conflicts on the farmstead's fixtures (0023, 0028, 0045, 0006). Its handoff is `specs/319-modal-writeups/briefs/h4-handoff.md`. A `Research:` claim in the engine that cites a changed block is owed a claims re-check at the push, not by you: leave it. The `hamlet/...`, `choice/...` and `sheet/...` modal units are not yours.

**Your questions:** the ones the handoff names.

## The procedure (check, apply)

1. `make record-owed` (in `.claude/skills/diagram`) names every unit the delta owes. In the FOREGROUND, in one message (a headless session is never woken by a background agent), one agent
   per owed unit, each from its own bundle (`make check-bundle Q=<NNNN> FOR=<check>`, `make check-bundle KEY=<key>
   FOR=source-applicability` for a key owed it, and `make check-bundle Q=<NNNN> FOR=entry-drift KIND=<class>` for each modal
   entry-drift is owed for), each naming its own MANIFEST.md. Do NOT edit any modal class for an entry-drift finding about the
   garden (`assets/modals/hamlet/garden.md`): feature 319 is rewriting that modal; answer its entry-drift
   with `make record-checked` and say so in the result. Any OTHER class's DRIFTED finding is applied as usual.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message. Then
   `make record && make citations` and the four record tests once; answer each check with `make record-checked`.
3. Re-check only what moved, until `make record-owed UNANSWERED=1` says no record check is owed. Commit only your files (message
   beginning `319 H4 check:`); do not push.
4. Append one line per check to `specs/319-modal-writeups/briefs/h4-checks.md` (with `make append`). Your last message is one
   paragraph.
