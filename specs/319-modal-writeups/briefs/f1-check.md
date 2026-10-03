<!-- page-load: kind=check -->
# Brief - feature 319 (modal write-ups), F1, session 2: check and apply

You are a FRESH session for one part of feature 319. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 added what a farmhouse's walls were made of (0029, or a new question it links) and how a farmhouse was
closed at night and in bad weather (0117). Its handoff is `specs/319-modal-writeups/briefs/f1-handoff.md`.

**Your questions:** the ones the handoff names.

## The procedure (check, apply)

1. `make record-owed` (in `.claude/skills/diagram`) names every unit the delta owes. In the background, in one message, one agent
   per owed unit, each from its own bundle (`make check-bundle Q=<NNNN> FOR=<check>`, `make check-bundle KEY=<key>
   FOR=source-applicability` for a key owed it, and `make check-bundle Q=<NNNN> FOR=entry-drift KIND=<class>` for each modal
   entry-drift is owed for), each naming its own MANIFEST.md. Do NOT edit any modal class for an entry-drift finding about the
   farmhouse (`Farmhouse` in `interactive/classes/homestead.py`): feature 319 is rewriting that modal; answer its entry-drift
   with `make record-checked` and say so in the result. Any OTHER class's DRIFTED finding is applied as usual.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message. Then
   `make record && make citations` and the four record tests once; answer each check with `make record-checked`.
3. Re-check only what moved, until `make record-owed UNANSWERED=1` says no record check is owed. Commit only your files (message
   beginning `319 F1 check:`); do not push.
4. Append one line per check to `specs/319-modal-writeups/briefs/f1-checks.md` (with `make append`). Your last message is one
   paragraph.
