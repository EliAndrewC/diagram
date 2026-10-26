# GM-review audit: the rubric (shared by every batch)

This is an AUDIT of the existing GM-review queue, not a draft: judge each row by your contract's tests of what deserves the GM, as sharpened below.

You judge rows of the diagram project's GM-review queue (`make gm-review`). Each row is a JSON object from a feature's
`specs/<feature>/gm-review.jsonl`, written AUTOMATICALLY whenever the round arbiter ruled or made a fix: `kind` is `arbiter`
(a ruling: `ruling` accept / continue / change-route / process-fault, with `asked`, `why`, `what`), `arbiter-fix-done` (a
tooling fix the arbiter ordered and the session made: `tooling_fix`, `note`, `test`) or `accepted`. `trigger` says what woke the
arbiter: `round:` a review check hit its round cap; `hour:` the hourly step-back; `ask:` a session asked it; `red-gate:` a
second red gate in a row; `cascade:`, `reversal:` other tripwires. `id` is `<feature>#<line>`.

## Why this audit exists (the GM, 2026-10-26, dictated)

"the idea behind the GM review was basically that I felt like a lot of features were hanging open for way too long because there
were way too many questions getting escalated to me. So I wanted things to be able to close so that we could move forward, and
then I could look at them later. The problem is, I think that most of what's ending up in GM review is just stuff that I
shouldn't have to answer ... this is yet another case of stuff being raised to my attention that should just be handled by the
arbiter and the implementation generally ... I would be really curious to know what the categories of things that exist in GM
review are, and which of those things just should not end up there in the first place, and what process improvements we can
make to reduce this down so that anything that ends up in GM review I actually know is important and that I should look at it.
Because right now I've basically concluded that I should just ignore it because it is almost purely a distraction, which is bad,
because that probably means that there are a few important things buried in there that I really should look at"

## What deserves the GM (YES), the project's own tests

The GM is the game master and the project's owner, not a reviewer of process. A row is YES only if a reasonable owner would
want to know it even when busy:
1. It overrode, narrowed, reinterpreted or set aside something the GM himself said or ruled (his quoted words, an
   `**Approved**:` line, a ruling in `docs/gm-rulings.md`), or decided something only he can decide (what to BUILD, a new
   standing rule of the project, spending money).
2. It accepted a known defect or limitation with a real cost to what he gets: maps that are wrong or uglier, a research
   reading of the setting or money that could be wrong, a check permanently weakened or switched off.
3. It changed what ships in a way he would see (a map, a page, a money figure) on the arbiter's or session's judgment
   alone, with the record silent.
4. A systemic process fault that keeps recurring and that tooling has NOT fixed (one he would want to fund a fix for).

MAYBE: one of those might hold but the row does not say enough to tell; say what is missing.

NO (the common case): a round-cap ruling that findings converged and the work may proceed; a ruling to continue; a tooling fix
the arbiter ordered that only changes process (a guard, a message, a bundle, a test) and landed with its test; an hourly
step-back's routine reading; a red-gate diagnosis that was fixed; wording, labels, ledger rows; anything the record or the
reviewers settled (whether a finding applies to a case is the record's and reviewers' to rule, never the GM's - GM 2026-10-25).

Be strict. The GM's complaint is that almost nothing in the queue is his; the audit is useful only if YES is rare and
defensible. Judge from the row itself; open a file in the repository (`/diagram/.clones/diagram-memories`) only when a YES or
MAYBE turns on it, and say what you read.

## For each row return

- `id` exactly as given.
- `category`: a short kebab-case slug for WHAT the row is about. Prefer these, add your own only when none fits:
  `round-cap-accept` (a check's rounds converged, accepted), `round-cap-continue` (one more round allowed),
  `step-back-routine` (hourly reading, nothing changed), `tooling-fix-process` (a guard/gate/bundle/message/test fix),
  `red-gate-fix` (a red gate diagnosed and fixed), `route-change` (the arbiter changed how a task proceeds),
  `process-fault` (the arbiter named a process fault), `scope-or-ruling-touch` (touches the GM's words or a ruling),
  `accepted-limitation` (a known defect or cost accepted), `research-reading` (a judgment about what a source says or
  applies to), `map-or-output-change` (what ships changed on judgment).
- `gm_worthy`: YES / MAYBE / NO.
- `summary`: one line, plain English, what the row says.
- `why_yes`: for YES or MAYBE only, which test (1-4) and why, in one or two sentences; empty otherwise.
- `prevention`: for NO rows, the smallest rule that would have kept it OUT of the queue (e.g. "never queue a round-cap
  accept", "queue a tooling fix only when it weakens a check"); for YES rows, whether it should have reached the GM
  immediately instead of sitting in a queue.

## Output

Return ONLY one JSON object per row, one per line (JSON Lines), no prose before or after, keys exactly: id, category, gm_worthy, summary, why_yes, prevention.
