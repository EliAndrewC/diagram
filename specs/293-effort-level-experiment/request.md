# Feature 293 - the effort-level experiment - the GM's request

The GM, 2026-09-29, in session "Diagram effort": *"Please read ~/.claude/handoffs/effort-experiment.md and create
the speckit feature it describes. Ask me whatever questions you need to ask to settle on some apropriate tasks to
actually use for this experiment before you begin the actual implementation work."*

The GM's answers to the session's questions, 2026-09-29, verbatim:

- Research task: "Servants' quarters doors" (Ubame: was a servants' nagaya one dormitory behind sliding
  partitions, or a door a household? - future-work/compounds.md).
- Implementation task, first ask: "Can you pick a different implementation task?  I don't like any of these for
  this effort, especially not anything involving settlement types wihch have not yet been scripted, which is
  currently everything except hamlets."
- Implementation task, second ask: "Footpath to burial ground" (future-work/farming-communities.md, "OPEN
  2026-09-28, OWED: no way reaches a burial ground, at any size of settlement").
- Replication: "Pilot: 1 per arm per task".
- Arms: "medium vs xhigh to start with, and we can test more if there is a big difference between medium and xhigh"
- The GM's judgment after the runs, 2026-09-30, verbatim: "I understand that what I have just done in my own review is not blind. And
  therefore, I might be biased But to be honest, I don't really find either of the research pages to be particularly noticeably better than
  the other. So I think that what that speaks to is the efficiency of the subagent checks that we already have to ensure a certain minimum
  level of quality. Now, as for the medium versus X high, work. It does seem that the X high work did a better job, Though to be frank, I
  don't think that the betterness is worth taking three times as long and twice as many tokens. So I think that when it comes to
  implementation tasks, it does seem like I want to keep medium as the default and then switch to a higher level in cases where I believe
  that it will be necessary for the session to really go deep and take the initiative to do research and find semi-related bugs and fix
  them above and beyond what will turn up naturally in unit testing, etc." ... "because I am not an expert there, it might be worth doing
  some kind of blind analysis of it" ... "see whether either one is deficient or if one of them seems really strongly better than the other
  in a concrete way that we would care about" ... "Can you have this feature which we are working on include merging in the X-high effort
  version of the implementation task and doing this blind review and merging in whichever version of the research task results it deems to
  be better along with giving me an analysis of what makes the better one better and how much better it seems to be. I think at that point,
  the entire feature is mergeable back into main."
- And on the proposed review: "Let's do two runs instead of three for the effort grader. Because frankly, just knowing whether or not two
  runs match or not is good enough for telling me how reliable the results are. ... Other than that, yes, please go ahead on that basis. Do
  all of this and then land the feature in main."
- Amendment, 2026-09-30 (task I's first run found its premise gone: feature 280 M68 had removed the hamlet's own burial ground). Asked
  "How should the experiment continue?": "Replace the task (Recommended)"; asked "If replacing, which hamlet task?": "Storehouse by house size".
- Amendment, 2026-09-29: "Please change the plan so that you will instead run these tests sequentially rather than in parallel for memory reasons. Because I don't want too many things running to be a problem for the container. do not actually begin the implementation, just update the spec kit spec to account for this. Thanks."

The handoff the GM pointed at, copied verbatim (written 2026-09-29 by a session outside the containers):

# Handoff: effort-level experiment for the diagram project

Written 2026-09-29 by a Claude Code session in `~/this-laptop` (outside the containers), for a
Claude Code session inside the diagram container. **Your job: turn this into a spec-kit feature
in the diagram repo, following the project's own conventions, and tell Eli the feature number.**
Do not run the experiment as part of writing the spec; Eli will have a later session implement it.

## Why

Eli's diagram sessions are mostly long (30+ minutes), agentic, and heavily scaffolded: spec-kit
features, checklists, hooks that enforce project rules, and subagent checks of each piece of work.
The question is which effort level that work should default to, and whether the scaffolding already
delivers what a higher effort level would.

What Anthropic's docs say (platform.claude.com/docs/en/build-with-claude/effort; Claude Code:
code.claude.com/docs/en/model-config):

- Opus 5.5 **defaults to `medium`**; most other models default to `high`.
- Levels: `low` (simple, speed/cost first, e.g. subagents), `medium` (balanced agentic work),
  `high` (complex reasoning, hard coding, agentic tasks), `xhigh` (long-horizon work: agentic/coding
  tasks over 30 minutes with token budgets in the millions), `max` (deepest reasoning).
- For Opus 5.5 specifically: "Run an effort sweep on your own evals rather than carrying settings
  over from an earlier model." This experiment is that sweep, in small form.

Working hypotheses from the discussion (reasoning, not measured):

1. Scaffolding and effort overlap only partly. Checks catch mistakes **after** they happen, and
   effort makes them less likely in the first place. With strong checks, lower effort may show up as
   more rework loops (rejections, review rounds, fixes), not as worse final output. If so, higher
   effort could cost **less** overall time and tokens, not more.
2. Effort should matter most where checks are weakest: **research** (a plausible but wrong or
   shallow synthesis passes every check) and upstream work (a flawed plan or spec gets enforced
   faithfully). It should matter least in **implementation** work that tests and guards cover
   well.
3. The payoff may differ by task type, so we test both.

## Design

**Arms:** Opus 5.5 at `high` and at `xhigh`. (`medium` could be added later as a third arm; that
adds cost.)

**Tasks:** two real, currently wanted tasks from the diagram backlog. Eli picks them, and the spec
session can propose candidates.
- **Research task:** e.g. a settlement or map research question, where Eli knows the material
  well enough to judge the result.
- **Implementation task:** clear acceptance criteria and test coverage.
- Size: roughly 30-60 minutes at `high`. Small enough to afford, long enough that "long-horizon"
  effects can show up. It must be a genuinely valid task: the better result gets kept, and the
  other gets discarded, not merged.

**How each run gets its effort level.** Pick whichever the project's tooling supports:
- **Preferred: separate top-level sessions**, e.g. headless `claude -p --effort <level>` in each
  clone. This tests the actual decision (a session's default effort). `--effort` overrides
  settings files for that session.
- **Fallback: subagents**, using two agent definitions that are identical except for their effort
  frontmatter. (Agent types take model and effort from their definition; check the Claude Code
  subagent docs for the exact key. The project's agent-model hook requires dispatches to name a
  model.) Subagents are a less faithful test than full sessions.

**Controls:**
- Same model, same starting commit, a separate clone per run, a byte-identical task prompt, and the
  same hooks and tooling.
- **Pin the effort of the checker/reviewer subagents** so that it is the same in both arms. Otherwise
  a better score in one arm might come from its more thorough reviewers, not its main session. Record
  which level they ran at.
- No human help during a run. If a run has to ask Eli something, answer both arms identically and
  log it.
- **Memory:** Claude containers share a 9 GB cap, and memwatch has already warned at 8 GB with
  diagram sessions alone. Run the arms **one after the other**, or confirm there is headroom
  before running them concurrently. A run killed by OOM (exit 137) is void.
- Alternate or randomize which arm runs first.

**Replication (a decision for Eli):** results from one run per arm are anecdotes. The same effort
level run twice can differ a lot.
- Recommended: **2 runs per arm per task** (8 runs total).
- Pilot option: 1 per arm per task (4 runs), clearly labeled as a pilot, then expand only if it
  shows a large difference.

## What to measure

Per run:
- **Tokens:** input, output, cache-read, and cache-creation tokens, summed from the session
  transcript JSONL (`message.usage` on each assistant message under `~/.claude/projects/...`),
  **including subagent transcripts**. Background-agent completion notices also report tokens,
  tool uses, and duration.
- **Usage limit consumed:** Eli is on a subscription, so the share of his usage limit a run eats is
  more relevant than dollars. Note it if it can be observed.
- **Wall-clock time** and **number of tool calls**.
- **Rework signals** (the key test of hypothesis 1): guard/hook refusals, failed checks, review
  rounds and rejections, escalations, and test failures before the final pass. Whatever the
  project's hooks already log is ideal.
- **Quality:**
  - A rubric per task, written **before** any run.
  - Blinded comparison: outputs labeled A/B by someone other than the grader, graded by a fixed
    grader subagent (fixed model and effort) and by Eli, who is the final judge for research.
  - For implementation, also: acceptance criteria met, review findings, defects found later,
    and diff quality/size.
  - Record *how* the outputs differ (depth, correctness, missed items, better approach found), not
    just which one wins.

## Output

A short report in the repo: a per-task table (arm × run: tokens, time, tool calls, rework counts,
quality score), qualitative differences, and a recommendation per task type. Propose a decision
rule up front, for example: adopt `xhigh` for a task type if blinded quality is clearly better, or
if rework drops enough that its time and tokens come out comparable to `high`.

The setting that results would go in the diagram repo's `.claude/settings.local.json`
(`effortLevel`, or `modelSettings.claude-opus-5-5.effortLevel`), not in the committed,
hook-guarded `settings.json`, unless Eli prefers otherwise. Individual sessions can still override
it with `/effort`.

## Caveats to keep in the spec

- Small n. Treat the results as directional.
- The results are specific to Opus 5.5 plus this tooling, as of late 2026. Re-run a reduced version
  when the model or the scaffolding changes significantly.
- The experiment itself is expensive. Keep the tasks small but real.
