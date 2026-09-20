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

## The GM's words after the feature landed (2026-09-20) - the amendment

The session reported what it had left: `settlement-review` telling the agent to import a module no make target
wraps, two cosmetic path and description duplications, that the spec review had cut a tier-test guard requiring the
field of every agent file as unrequested, and that only two of the twelve agents had a seeded proof. The GM:

> Please fix anything left unfixed, including the settlement-review issue tou mentioned and the two cosmetic path and description duplications, etc.  I do indeed want the guard enforced by a test - and Why would the fidelity reviewer have cut something which enforces something that I want and ask for? I mean, the fidelity reviewer should be checking to see whether you're doing something different from what I asked for, not preventing you from writing automated checks to make sure that the thing that I asked for actually happens. So I'm concerned if something like this was dropped, not in spite of the fidelity reviewer, but because of it.
>
> Is there any particular reason not to test the other 10 reviewers with seeded proofs?

## The GM's answer on the amendment's results (2026-09-20) - three recommendations approved

The session reported the eight pairs and the fidelity-contract proof and put three decisions, in these words:

> 1. **T08.** Should I accept the fidelity-contract change with the honest record that its proof is inconclusive? That lets everything land. I recommend yes, and I would sharpen the "new behavior presented as a check" wording in the same change. The alternative is that everything waits.
> 2. **`spec-fidelity` and the field.** I can keep the field on or take it off for this one agent. It gates every spec, its saving is small (16k to 10k tokens on the first turn), and its results are the least settled. I recommend taking it off until a three-samples-per-leg test, about 4 weight units, can tell field from variance.
> 3. **`settlement-review`.** A single pair costs about 9 weight units and cannot separate a miss from variance; three samples per leg would be about 27. `perf-audit` has nothing to replay, so a proof needs a manufactured slowdown between two commits, roughly a day of session work. My recommendation is to skip both for now and watch their first real dispatches, but it is your call.

The GM:

> go with your recommendations to all three
