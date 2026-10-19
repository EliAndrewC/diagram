# Money research requests - working one

**Load this file when:** you work a money research request: a GitHub issue on `EliAndrewC/diagram` from the gm-assistant
agent asking for money questions (feature 389).

gm-assistant's money skill says what things cost in Rokugan. Its history is researched HERE, in this record, with the
same search passes, citations and checks as every other question; the skill cites the question files. The GM, 2026-10-18:
*"you would say what research you need, they would do the research, and then you would be able to pull the research when
they're done."*

## Working the issue

The user-level "Working a GitHub issue" rule applies: `python3 ~/.claude/hooks/issue_watch.py start <issue>`, then
`show`; acknowledge on the issue with the plan; work it as a `research record` feature (the GM approves it as any other);
answer on the issue; the ASKER closes it once it has verified the answer. Never close it yourself.

**A request carries** three things; ask on the issue for any that is missing:
1. the question;
2. the figure the skill needs from it (a ratio, a price, a range, a wage);
3. the canon it must sit beside (`setting/l7r.md` "Money", `setting/budgets.md`, read with `make canon`), and whether
   Japan or China comes first. Tokugawa price and wage series are the richest data, so a request may name Japan first;
   the research-pass contract follows the prompt.

**An answer returns** three things:
1. each question's fragment FILE, `research/questions/NNNN-<heading id>.html` (never a built page);
2. the verdict for each figure: ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT;
3. what is still open: a source on `research/to-download.md`, a pass not yet run, a figure no source gives.

**History is recorded as found.** Where it contradicts the canon, the answer says so and the contradiction goes to the GM
(through `escalation-check`), who decides. Nothing here edits the canon.

## In the record

- A money question carries `subject=money` first (its home is the "Money and prices" section) and has no drawing page;
  no map draws a price. A question that is also about a map takes both subjects, and a drawing page only if a map draws it.
- **The feature that writes the FIRST money question deletes the section's `awaiting` line** in `research/contents.json`;
  `make record CHECK=1` refuses it once a question is homed there.
- `make impl-check F=<n>` closes on a line in the feature's `implementation-check.md`, since no code here decides a
  price:
  `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<the question's terms>' l7r pool`
- **A source on another society's money** (a Regency household's wages, a Dickensian price) is a COMPARATIVE source:
  `research/CLAUDE.md`, "Comparative money sources", for what it may be used for and how it is marked.
- A source the GM owns in print (Goldsmith's *Premodern Financial Systems*, McClain and Wakita's *Osaka*) goes on the
  download list (`make download-add`). The GM's group's old emails and spreadsheets (`/host-l7r-repo/money/`, digested in
  its `digest.md`) are LEADS: a figure from them is cited from the work it came from, never from the email.
