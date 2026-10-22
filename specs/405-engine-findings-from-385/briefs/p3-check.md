<!-- page-load: kind=check -->
# Brief - feature 405, page session 3: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-backlog-pages`); the research record's `CLAUDE.md` applies to you above all.

**What moved.** Sessions 1-2 revised drawing pages 0246, 0081, 0014, 0043, 0196 and the glossary, in commits opening
`405: `. Their handoff is `specs/405-engine-findings-from-385/briefs/p-handoff.md`.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed
   unit, each from its own bundle (`make check-bundle Q=<n> FOR=<check>`, after `make quote-verbatim Q=<n>` for
   quote-check) and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave` workflow.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT:
   none`. Then run `make record && make citations` and the record tests once, and answer each check with `make
   record-checked`. Commit each fix with a message opening `405: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first (`make
   arbiter-bundle`). Do not push.
4. Append one line per check to `specs/405-engine-findings-from-385/briefs/p-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
