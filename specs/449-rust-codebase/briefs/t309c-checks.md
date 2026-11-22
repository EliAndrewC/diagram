# Brief - feature 449 bundle T302 (the record's leftover findings), session 10: check and apply (0123, a T303 check finding)

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every
command). `scripts/container/page-session-rules.md` is in your system prompt; the research record's `CLAUDE.md` loads
when you touch `research/`.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits by name. Edit only what a check's finding needs, and list every file you changed in the
handoff. Never push. Do not edit any `Research:` claim, `dev/claims-index.json`, `pool/` or any pop-up: the claims the
page edit re-owes are the orchestrator's (do not run `make claims-*`).

**Your units:** question 0123 (its drawing page) and anything else the write session's handoff lists.

## What to do

1. Read the write session's handoff by line: `make lines FILE=specs/449-rust-codebase/briefs/t309c-handoff.md
   KEY='^- |^T2|^## '`. Then `make record-owed` - it names every unit the delta owes. Work exactly the units it names
   that belong to your units above; a unit it names that is NOT yours (another builder's) is left and reported.
2. For each owed check, run its mechanical pre-pass first (`make quote-verbatim Q=<n> NOTES=<k>` before quote-check,
   `make record-prepass Q=<n>` before record-format), then `make check-bundle` for it, and dispatch the checks in ONE
   message in the FOREGROUND, each naming its bundle's MANIFEST (never a path under `/diagram`). A pop-up owed only
   because one of your pages moved is triaged (`make modal-triage`, `make modal-triaged`); one the triage names is reported OPEN, not
   checked here.
3. Apply each round's findings in ONE turn (`make apply-edits` for EDIT blocks). Record every answer:
   `make record-checked CHECK=<check> BUNDLE=<dir> RESULT="<counts>"`. A finding under `OUTSIDE THE CHANGE` is not fixed
   here: list it in the handoff. A fix owes its second round; a third round on one subject goes to the `round-arbiter`
   (`make arbiter-bundle`), not to the GM. If a check dispatch is refused as tied to another task, pass
   `DECIDE_OK="T302 bundle page session record checks"`.
4. `make page-check` (the new Ezo glossary term, l7r/diagram/interactive/assets/glossary/28290-Ezo.json, owes it). `make record CHECK=1`, `make record`, `make glossary`, and `make record-owed` again: it must name nothing of your
   units. Then `make research-claim Q="0123" FEATURE=449 STATUS=done`.
5. Append the results to the handoff with `make append FILE=specs/449-rust-codebase/briefs/t309c-handoff.md LINE="..."`:
   one line per check run (`CHECKED <check> <unit> - <counts> - <applied or nothing>`), every file you changed
   (`CHANGED <path>`), and anything left open with why (`OPEN ...`). Your last message is one paragraph: what was
   checked, what was applied, what is open.
