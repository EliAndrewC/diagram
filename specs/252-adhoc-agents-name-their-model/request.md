# Where this feature comes from

Feature 251 measured that 72 ad-hoc agent runs had been dispatched with no model and that 62 of them ran
on Fable, the session's model (`specs/251-tiered-subagent-checks/research.md` R1). Its first spec draft
carried a hook for that and `spec-fidelity` ruled the hook outside the GM's request, so 251 only wrote the
rule down and put the question to the GM with three options: (a) a hook that fills in `model: opus`,
(b) the same defaulting the read-only built-in types to `sonnet`, (c) leave it a written rule. The
session recommended (a).

## The GM's words (2026-09-19)

> You gave three options for what happens when there is a missing model on an ad hoc agent dispatch. But isn't there a fourth option, which is to have the hook reject it with a message saying that the caller has to specify a model and then reiterating the rules around what should be selected? That does seem better because the caller can then make a choice based on those things, right?

The session agreed: which model fits depends on whether the agent will read or judge, which only the
caller knows, and this repository's guard doctrine reserves a refusal for exactly "a decision only the
session can supply".

## The rule being reiterated (root `CLAUDE.md`, from feature 251)

> An ad-hoc agent is dispatched with an explicit `model` - `sonnet` to read, fetch, translate or extract, `opus` for anything that judges - and never with none: with none it runs on the session's model.
