# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0103, 0009, 0107), session 2: check and apply

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every
command). `scripts/container/page-session-rules.md` is in your system prompt; the research record's `CLAUDE.md` loads
when you touch `research/`.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone; the orchestrating session commits by name. Edit only what a check's
finding needs, and list every file you changed in the handoff. Never push, and never push the archive by hand
(`make reserve`'s own archive step is by design). Do not edit any `Research:` claim, `dev/claims-index.json`, `pool/`,
`docs/`, `rust/` or any pop-up (do not run `make claims-*`). Touch no question but 0103, 0009 and 0107.

**Your units:** the blocks, notes, registry entries and glossary terms of 0103, 0009 and 0107 the write session's handoff names
(E1-E3). Owed units of those questions that predate the write session are other builders': leave and report them.

## What to do

1. Read the write session's handoff by line: `make lines FILE=specs/449-rust-codebase/briefs/t371e-handoff.md
   KEY='^- |^E[1-9]|^## |^CHECKED|^OPEN'`. Then `make record-owed`: work exactly the units it names that are yours.
2. For each owed check, run its mechanical pre-pass first (`make quote-verbatim Q=<NNNN> NOTES=<k>` before quote-check,
   `make record-prepass Q=<NNNN>` before record-format), then `make check-bundle` for it, and dispatch the checks in ONE
   message in the FOREGROUND, each naming its bundle's MANIFEST (never a path under `/diagram`). A pop-up owed only
   because a page moved is triaged (`make modal-triage`, `make modal-triaged`); one the triage names is reported OPEN,
   not checked here.
3. Apply each round's findings in ONE turn (`make apply-edits` for EDIT blocks). Record every answer:
   `make record-checked CHECK=<check> BUNDLE=<dir> RESULT="<counts>"`. A finding under `OUTSIDE THE CHANGE` is not fixed
   here: list it in the handoff. A finding whose fix is a pop-up, a `pool/` file or a `docs/` file is not applied
   here either (they are another builder's): list it as `OPEN`. A fix owes its second round; a third round on one
   subject goes to the `round-arbiter` (`make arbiter-bundle`). If a check dispatch is refused as tied to another task,
   pass `DECIDE_OK="T371 bundle page session record checks"`.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`, and `make record-owed` again: it must name
   nothing of your units. Do NOT release the claims (the next brief and the orchestrator still hold these pages).
5. Append the results to the handoff with `make append FILE=specs/449-rust-codebase/briefs/t371e-handoff.md LINE="..."`:
   one line per check run (`CHECKED <check> <unit> - <counts> - <applied or nothing>`), every file you changed
   (`CHANGED <path>`), and anything left open with why (`OPEN ...`). Your last message is one paragraph: what was checked,
   what was applied, what is open.
