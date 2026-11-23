# Brief - feature 449 T318, T319 and T327 (0220, 0088, 0123), session 2: check and apply

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every
command). `scripts/container/page-session-rules.md` is in your system prompt; the research record's `CLAUDE.md` loads
when you touch `research/`.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits by name. Edit only what a check's finding needs, and list every file you changed in the
handoff. Never push, and never write or push the archive's real remote. Do not edit any `Research:` claim,
`dev/claims-index.json`, `pool/`, `docs/`, `rust/` or any pop-up (do not run `make claims-*`).

**Your units:** the blocks and notes of 0220 and 0088 the write session's handoff names (T318, T327); and T319 below.
Owed units of those questions that predate the write session are other builders': leave and report them.

**T319 - an unchecked support.** 0123's opening says a Qing local office "faced south, by regulation", resting on the
note `neixiang-xianya-zhwiki` (in 0123's notes and drawing notes), which no check has read. Its text is unchanged, so
nothing owes it: build its bundles anyway with `NOT_OWED_OK="449 T319: the faced-south support never checked"` -
`make check-bundle Q=0123 NOTES=neixiang-xianya-zhwiki FOR=quote-check NOT_OWED_OK=...` after
`make quote-verbatim Q=0123 NOTES=neixiang-xianya-zhwiki`, and a source-reader bundle for the same note - and dispatch
quote-check and source-reader on them. If the source does not support "by regulation" (or "faced south"), restate the
sentence in 0123 to what the source says, and report in the handoff that the road, main-gate, family-quarters,
inner-court, residence and outer-court pop-ups repeat it (you do not edit pop-ups).

## What to do

1. Read the write session's handoff by line: `make lines FILE=specs/449-rust-codebase/briefs/t317b-handoff.md
   KEY='^- |^T3[0-9]+|^## |^CHECKED|^OPEN'`. Then `make record-owed`: work exactly the units it names that are yours.
2. For each owed check, run its mechanical pre-pass first (`make quote-verbatim Q=<NNNN> NOTES=<k>` before quote-check,
   `make record-prepass Q=<NNNN>` before record-format), then `make check-bundle` for it, and dispatch the checks
   (T319's with them) in ONE message in the FOREGROUND, each naming its bundle's MANIFEST (never a path under
   `/diagram`). A pop-up owed only because a page moved is triaged (`make modal-triage`, `make modal-triaged`); one the
   triage names is reported OPEN, not checked here.
3. Apply each round's findings in ONE turn (`make apply-edits` for EDIT blocks). Record every answer:
   `make record-checked CHECK=<check> BUNDLE=<dir> RESULT="<counts>"`. A finding under `OUTSIDE THE CHANGE` is not fixed
   here: list it in the handoff. A fix owes its second round; a third round on one subject goes to the `round-arbiter`
   (`make arbiter-bundle`). If a check dispatch is refused as tied to another task, pass
   `DECIDE_OK="T317 bundle page session record checks"`.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`, and `make record-owed` again: it must name
   nothing of your units. Then `make research-claim Q="0220 0088 0123" FEATURE=449 STATUS=done`.
5. Append the results to the handoff with `make append FILE=specs/449-rust-codebase/briefs/t317b-handoff.md LINE="..."`:
   one line per check run (`CHECKED <check> <unit> - <counts> - <applied or nothing>`), every file you changed
   (`CHANGED <path>`), and anything left open with why (`OPEN ...`). Your last message is one paragraph: what was checked,
   what was applied, what is open.
