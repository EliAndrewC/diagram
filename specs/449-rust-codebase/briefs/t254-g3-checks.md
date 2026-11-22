# Brief - feature 449 task T266 (bundle T254), group G3 (city temples' kuri quotation), session 2: check and apply

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every
command). `scripts/container/page-session-rules.md` is in your system prompt; the research record's `CLAUDE.md` loads
when you touch `research/`.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits by name. Edit only what a check's finding needs, and list every file you changed in the
handoff. Never push. Do not edit `docs/building-programs.md`, any `Research:` claim, `dev/claims-index.json` or `pool/`:
the claims the page edits re-owe are the orchestrator's (do not run `make claims-*`).

**Your units:** question `0227` and the registry entry `kuri-jawiki`; every pop-up
owed only because 0227 moved (triaged first); and anything else the write session's handoff lists.

## What to do

1. Read the write session's handoff by line: `make lines FILE=specs/449-rust-codebase/briefs/t254-g3-handoff.md
   KEY='^- |^G3|^## '`. Then `make record-owed` - it names every unit the delta owes. Work exactly the units it names
   that belong to your units above; a unit it names that is NOT yours (another builder's, or groups G1 and G2's pages and
   pop-ups, already checked) is left and reported.
2. For each owed check, run its mechanical pre-pass first (`make quote-verbatim Q=<NNNN> NOTES=<k>` before quote-check,
   `make record-prepass Q=<NNNN>` before record-format), then `make check-bundle` for it, and dispatch the checks in ONE
   message in the FOREGROUND, each naming its bundle's MANIFEST (never a path under `/diagram`). The pop-ups run in
   order: `make modal-bundle FOR=modal-form`, apply its EDITs (`make apply-edits`), then `modal-research`, then
   `modal-depiction`; a pop-up owed only because a page it names moved is triaged first (`make modal-triage`,
   `make modal-triaged`).
3. Apply each round's findings in ONE turn (`make apply-edits` for EDIT blocks; a hand fix that leaves a note's link,
   quotes and claim sentences as they were is declared with `make record-checked CHECK=quote-check ... FIXED_BY=`).
   Record every answer: `make record-checked CHECK=<check> BUNDLE=<dir> RESULT="<counts>"`. A finding under `OUTSIDE THE
   CHANGE` is not fixed here: list it in the handoff. A fix owes its second round; a third round on one subject goes to
   the `round-arbiter` (`make arbiter-bundle`), not to the GM. If a check dispatch is refused as tied to another task,
   pass `DECIDE_OK="bundle T254 record checks"`.
4. `make record CHECK=1`, `make record`, `make glossary`, and `make record-owed` again: it must name nothing of your
   units. `make quote-verbatim Q=0227 NOTES=kuri-jawiki` must show no DIFFERS or NOT-ON-PAGE but reference-marker-only ones. Then
   `make research-claim Q="0227" FEATURE=449 STATUS=done`.
5. Append the results to the handoff with `make append FILE=specs/449-rust-codebase/briefs/t254-g3-handoff.md LINE="..."`:
   one line per check run (`CHECKED <check> <unit> - <counts> - <applied or nothing>`), every file you changed
   (`CHANGED <path>`), and anything left open with why (`OPEN ...`). Your last message is one paragraph: what was
   checked, what was applied, what is open.
