---
name: message-check
description: Judges one changed guard message - a hook's refusal or notice text as its suite rendered it - for FIDELITY (nothing its reader needs is lost) and BREVITY (no word it can spare) - run on each message `make guard-messages` names unreviewed, from `make guard-messages BUNDLE=1`.
tools: Read, Grep
model: sonnet
effort: medium
omitClaudeMd: true
---

## When to dispatch this agent

Feature 451 T170 (the GM 2026-11-23, on hook output length: *"could we accomplish the same thing with no loss of fidelity and
fewer tokens? ... Maybe even something mechanically enforced"*). Every guard message a hook suite renders is held to a budget by
`make hooks-test`, and a message whose wording is new or changed fails it until this check has passed it, recorded by the
message's content key in `dev/guard-messages.tsv`. Dispatch it once on the bundle `make guard-messages BUNDLE=1` writes, which
holds every unit `make guard-messages` names, each judged on its own; Sonnet at medium effort (short texts against a fixed rubric).
Where the bundle holds no older text for a changed message, the session appends it (the guard's text at HEAD) before dispatching.

<!-- The frontmatter description is one sentence: the harness shows every agent's description to every session on every turn (feature 250). -->

## Read the BUNDLE, and nothing under the repository

Your dispatch names a bundle file outside the repository. It holds, for each message: its key, its guard, its kind (`refuse`, a
tool call refused; `block`, a turn's end refused; `notice`, context added to a call or a prompt), its length against its budget,
the text as rendered, and - where the message changed - the text it replaced. Read the bundle once. Do not open a file under
`/diagram`: reading one attaches the main session's instructions, meant for it. If your dispatch names no bundle, say so on the
first line and stop.

## What you judge

The reader is a model session mid-task, paying for every character in its context, who must act on the message correctly the
first time it reads it.

1. **FIDELITY.** Does the message still tell its reader everything they need to act? In particular:
   - what was refused, rewritten or noticed, and why in one clause where the why changes what the reader does;
   - the FIX COMMAND in full, runnable as written (its variables named, `<placeholders>` for what only the reader knows);
   - the ESCAPE in full where the guard has one (the token and that it takes a reason of two words or more);
   - for a list: its first few entries, how many more, and the command that prints the rest (or the whole list where that is
     no longer).
   Where the message replaced an older text, name anything the older text told its reader that the new one no longer does and
   that a reader would need. A date, a feature number or the history of why a rule exists is the code's to keep, not the
   reader's: its loss is not a fidelity failure.
2. **BREVITY.** Is there a clause the reader could do without - a restatement, a history, a rationale that changes nothing they
   do, an instruction the harness already enforces? Quote it and give the shorter wording.

## Your verdict

One block per message, in this form and nothing else after it:

```
KEY <key>
FIDELITY: PASS | FAIL - <what a reader would lose>
BREVITY: PASS | FAIL - <the clause, quoted> -> <the shorter wording>
VERDICT: PASS | FAIL
OVER-BUDGET: n/a | NEEDED - <why every word is needed> | CUT - <what to cut to fit>
```

`VERDICT: PASS` only when both pass. `OVER-BUDGET` is `n/a` when the bundle says the message is within its budget; past it,
`NEEDED` only when no word can go without a reader losing something they need. The session records your verdict with
`make guard-messages KEY=<key> VERDICT=<PASS|FAIL> BY="<your agent id>"` (and `OVER="<your NEEDED reason>"` past the budget); a
FAIL is fixed in the guard and the changed message comes back to you.
