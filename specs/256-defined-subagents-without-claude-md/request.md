# Where this feature comes from

Feature 255's fixed-context probes (2026-09-19, `specs/255-cheaper-checks-by-tooling/research.md` R5 and R7) measured
that every subagent this repository defines is handed the root `CLAUDE.md` (about 5.0 k tokens) and the session
memory index (about 6.7 k) on its first turn, re-read on every turn after; and that one agent-frontmatter field,
`omitClaudeMd: true`, removes both (a probe's first turn fell from 14,094 tokens to 2,290).

## The GM's words (2026-09-19), on being shown R5

> Oh, I had no idea that the memory index and the root Claude.md were handed to every subagent. That really doesn't seem like something that we should be doing, right? Because, I mean, the memories are all intended for the main session, and I don't think the subagents should need them. If there's something that a subagent should know, it should be in the subagent specification. The same is true with the Claude.md, really. I mean, if there's something that the subagent needs to do, then it should be told that. Now, I guess if we're talking about subagents that we have not specifically defined, and just a, uh, I forget what you call them, but like an unnamed subagent, like the kind that a session dispatches, then Okay, that's fine, I guess. And it makes sense that they would get the Claude.md and that they would get the memories. But I think our defined subagents should not.

## The session's proposal, and the GM's answer (2026-09-19)

The session proposed, in these words:

> I propose a small feature of its own, 256:
>
> 1. Grep each of the twelve contracts against the root `CLAUDE.md` to find rules a check relies on, and move those into its contract.
> 2. Add `omitClaudeMd: true` to the twelve agent files.
> 3. Prove it on recorded findings: the twin's two review rounds and one `record-format` case, each with a same-setting control, as in 255. That is about 6 runs and 6-8 weight units.
>
> The three agents with no recorded runs (`perf-audit`, `building-review`, `size-audit`) cannot be tested that way. For those I would do step 1 carefully and flip the field without a seeded run, if you agree.
>
> Say "go" and I will claim 256 and run the chain end to end.

The GM:

> go
