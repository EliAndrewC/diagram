<!-- A DRAFT for the talk before the port resumes, written 2026-11-27 by one read-only web research agent at the GM's word ("if you are able to do whatever ... research ... would help inform that discussion in advance, then that would be useful"). Its quotations are as the fetch tool returned them and have NOT been checked against their pages; nothing in it is decided. Load this file when: weighing whether the primary session becomes an orchestrator. -->

# Orchestrator vs integration agent: what practitioners and vendors have published

Date of research: 2026-11-26. All pages were fetched through WebFetch, which returns text passed through a small summarizing model. Quotations below are as that tool returned them and marked as quotations; a few may be lightly normalized. Where a page is a vendor doc with no date shown, I say "no date shown".

## Part 1. What the sources SAY

### A. Orchestrator-worker patterns and their failure modes

**A1. Anthropic, "How we built our multi-agent research system"** (2025-06-13). https://www.anthropic.com/engineering/multi-agent-research-system (read)
- "the lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously."
- "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries." Vague briefs led to subagents that "perform the exact same searches as other agents" (duplicated work).
- "Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator." and "This prevents information loss during multi-stage processing." (artifacts over summaries)
- Lead is synchronous: "the lead agent can't steer subagents, subagents can't coordinate."
- Cost: agents use about 4x the tokens of chat, multi-agent about 15x.
- Poor fit: domains where "all agents to share the same context" and tasks with "fewer truly parallelizable tasks than research," such as most coding work.
- Bears on us: confirms that the lead should hold plans and references, not details; but it also names most coding as a weak fit for fan-out, and the lead being synchronous is the bottleneck we measured.

**A2. Cognition, "Don't Build Multi-Agents"** (2025-06-12). https://cognition.com/blog/dont-build-multi-agents (read)
- "Share context, and share full agent traces, not just individual messages."
- "Actions carry implicit decisions, and conflicting decisions carry bad results."
- "The simplest way to follow the principles is to just use a single-threaded linear agent."
- Bears on us: the argument against parallel writers. Our builders are parallel writers in separate trees; conflicts at carry time are where these hidden decisions collide. It argues for task partitioning, not for abandoning builders.

**A3. Cognition, "Multi-Agents: What's Actually Working"** (2026-04-22). https://cognition.com/blog/multi-agents-working (read)
- "multiple agents contribute intelligence to a task while writes stay single-threaded"
- "a manager splits work, children execute, the manager synthesizes and reports back."
- "Managers trained on small-scoped delegation default to being overly prescriptive"
- "Agents assume they share state with their children when they don't."
- "a reasonable 80/20 solution is to just share a fork of the full context of the primary model"
- On conflicts: the post gives one example, "always invoking the smart friend for merge conflicts" (the tool returned only this fragment; it is not a design).
- Bears on us: a vendor that once said "don't" now endorses manager/worker with single-threaded writes. Our integration step IS the single-threaded write. That favors one integrator (not several) and keeping it separate from the builders.

**A4. Cursor, "Scaling agents"** (2026-01-14). https://cursor.com/blog/scaling-agents (read)
- Planners "continuously explore the codebase and create tasks"; workers "focus entirely on completing them" and "don't coordinate with other workers."
- Flat self-coordination failed: "Agents would hold locks for too long, or forget to release them entirely." and "Twenty agents would slow down to the effective throughput of two or three."
- THE closest published case to our question: a dedicated integrator was tried and dropped because it "created more bottlenecks than it solved," and workers could resolve their own conflicts.
- "Hundreds of workers run concurrently, pushing to the same branch with minimal conflicts."
- Bears on us: direct counter-evidence to "a standing integration agent in its own tree". Their fix was to push conflict resolution and rebase back to the worker, not to a central integrator. Caveat: they run workers on one branch with fine-grained tasks, a different shape from batch gating with a heavy full gate.

**A5. Anthropic, "Building a C compiler with a team of parallel Claudes"** (2026-02-05). https://www.anthropic.com/engineering/building-c-compiler (read)
- "I don't use an orchestration agent." Agents pick the "next most obvious" problem and claim tasks with lock files in `current_tasks/`.
- "Each agent clones a local copy to `/workspace`, and when it's done, pushes from its own local container to upstream." Agents pull and merge others' changes before pushing.
- "Merge conflicts are frequent, but Claude is smart enough to figure that out."
- "Having 16 agents running didn't help because each was stuck solving the same task." (parallelism collapsed on one monolithic task)
- Cost: "2 billion input tokens ... 140 million output tokens, a total cost just under $20,000", about 2,000 sessions over two weeks.
- Bears on us: no coordinator at all; the shared test suite is the integrator and each worker rebases itself. Parallelism stops paying when work is not decomposable.

**A6. Anthropic, "Effective context engineering for AI agents"** (2025-09-29). https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (read)
- "specialized sub-agents can handle focused tasks with clean context windows." A subagent may use "tens of thousands of tokens or more" and returns "a condensed, distilled summary of its work (often 1,000-2,000 tokens)."
- Bears on us: supports an orchestrator that receives only short summaries; it does not say how to avoid loss at handoff.

**A7. Claude Code docs: subagents** (no date shown). https://code.claude.com/docs/en/sub-agents (read the first 100,000 of 114,792 characters)
- "Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions."
- "When subagents complete, their results return to your main conversation. Running many subagents that each return detailed results can consume significant context."
- "Background subagents run concurrently while you continue working." Results arrive "as a completion notification in a later turn."
- "By default, a subagent can spawn subagents of its own, up to three layers below the main conversation." (so an integrator agent may itself dispatch agents)
- `isolation: worktree` gives "an isolated copy of the repository."
- Bears on us: the platform already supports a coordinator that dispatches background agents and receives notifications; a pure-dispatch orchestrator is a supported shape.

**A8. Claude Code docs: agent teams** (no date shown, experimental). https://code.claude.com/docs/en/agent-teams (read in full)
- "Agent teams add coordination overhead and use significantly more tokens than a single session." "For sequential tasks, same-file edits, or work with many dependencies, a single session or subagents are more effective."
- "Start with 3-5 teammates for most workflows." "Three focused teammates often outperform five scattered ones." "Having 5-6 tasks per teammate keeps everyone productive and lets the lead reassign work if someone gets stuck."
- Failure mode of the lead: "Sometimes the lead starts implementing tasks itself instead of waiting for teammates." Remedy given: "Wait for your teammates to complete their tasks before proceeding".
- "Too small: coordination overhead exceeds the benefit." "Letting a team run unattended for too long increases the risk of wasted effort."
- Bears on us: the vendor names the exact failure the owner worries about (lead does work itself), and gives 3-5 as a working size, matching our 3-4 builders.

**A9. Claude Code docs: costs** (no date shown). https://code.claude.com/docs/en/costs (read)
- "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"
- "Every subagent, and every agent a dynamic workflow spawns, sends its own requests on top of the main conversation's."
- "Claude Code sends your full conversation with every request" and a long session re-reads history at the cached rate, so an always-open orchestrator that idles still pays when it wakes (cache TTL, "Cache misses: your first message after a break longer than the cache lifetime misses the cache").
- Bears on us: a long-running coordinator has a cost that grows with its context; keeping its context small (summaries only) is also a cost lever.

**A10. Microsoft AutoGen, Magentic-One** (no date shown). https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html (read)
- Orchestrator is "the lead agent responsible for task decomposition and planning"; it keeps a Task Ledger and "At each step of its plan, the Orchestrator creates a Progress Ledger where it self-reflects on task progress"; if stalled it "can update the Task Ledger and create a new plan."
- Bears on us: a worked example of an orchestrator whose state is explicit ledgers (a pattern we already have in task lists); the page reports no throughput data.

**A11. OpenAI, agent orchestration guide** (no date shown). https://developers.openai.com/api/docs/guides/agents/orchestration (read; the page did not cover code-vs-LLM orchestration)
- "Handoffs are the clearest fit when a specialist should own the next response rather than merely helping behind the scenes." Agents-as-tools: the manager "keeps ownership of the reply."
- "Splitting too early creates more prompts, more traces, and more approval surfaces."
- Bears on us: handoff (integrator owns the batch) versus agent-as-tool (coordinator keeps ownership and gets a result back) is the exact design choice; OpenAI says to split late.

**A12. LangChain/LangGraph supervisor docs.** NOT OPENED: the docs URL redirected and returned nothing. The following comes from a search-result summary only, so treat as unverified: supervisor wraps subagents as tools, "All routing passes through the main agent," runs sequentially by default; a "custom workflow" pattern mixes deterministic and agentic steps; a single agent with the right tools can often do as well. Source list seen: https://docs.langchain.com/oss/python/langchain/multi-agent/index.html

**A13. Practitioner posts on parallel agents in worktrees** (dev.to; no controlled data).
- https://dev.to/sahil_kat/how-to-keep-parallel-coding-agents-from-stepping-on-each-other-e5g (read; "Posted April 24" year not shown): "When a worker branch is ready, the lead reviews it from the main worktree." "You can run 2-5 Claude Code, Codex, or Aider sessions simultaneously." "Git worktrees solve filesystem isolation but not runtime isolation" (ports, shared databases, API rate limits).
- https://dev.to/0xandrewshu/from-1-to-3-parallel-claude-code-agents-how-i-broke-past-16-utilization-mee (read; "Mar 17", year not shown): "stuck at 16% Claude Code utilization"; after parallelizing "I was quickly hitting 45+% consistently"; "I could only handle 1 workload that required active attention"; "you become an engineering manager." Bears on us: this is the same bottleneck (the coordinator's attention) with a human as coordinator; numbers are one person's.
- Search-snippet only (not opened): further dev.to and heyvaldemar.com ("merge debt") posts say worktrees defer conflicts to merge time, that three to four parallel tasks is a common comfortable level, and that sequencing merges matters. I found no write-up of a standing integration agent beyond tools (agent-merge, crosslink swarm merge, "Intent" Coordinator) seen only in search results.

### B. Merge queues and integration in human CI

**B1. GitHub merge queue docs** (no date shown). https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue (read)
- "the merge queue ensures that they are merged in a first-in-first-out order." Each PR is tested against the target branch plus the changes ahead of it.
- Admins set min and max group size and "build concurrency".
- On failure the queue removes the failing PR and retests the rest without it.
- The queue "does not require a pull request author to update their pull request branch."
- Bears on us: the queue, not the author, does the carry; the author is freed. A failed PR goes back to its author.

**B2. GitLab merge trains** (no date shown). https://docs.gitlab.com/ci/pipelines/merge_trains/ (read)
- "Each merge request is compared to the other, earlier merge requests, to ensure they all work together." "The pipelines all run in parallel." Default maximum "20 pipelines in parallel."
- "If a merge train pipeline fails, the merge request is not merged." It is removed, later pipelines restart, and repair is the author's: "Fix the cause, then add the merge request to the merge train again."
- Bears on us: in human practice, nobody in the queue repairs; a red change is ejected and returned to its author.

**B3. Zuul gating** (no date shown). https://zuul-ci.org/docs/zuul/latest/gating.html (read)
- Speculative execution "assumes that all jobs will succeed and tests them in parallel accordingly."
- On failure ahead, "changes that were expecting it to succeed are re-tested without the failed change."
- Cost warning: "If this happens frequently, then Zuul can end up using increasingly large amounts of test resources for little gain." Worst case "changes are tested one at a time"; the window shrinks quickly after failures and grows slowly.
- Bears on us: the failure rate decides whether speculation pays; with expensive gates a high red rate wastes work.

**B4. Trunk merge queue, batching** (no date shown). https://docs.trunk.io/merge-queue/optimizations/batching (read)
- Trunk will "test multiple pull requests together as a single unit"; on failure it "automatically splits the batch and retests to identify only the failing PR(s)", by halving: "splits the batch in half rather than peeling off individual PRs."
- Cost: you "essentially give up the proof that every pull request in complete isolation can safely be merged."
- Mergify (search snippet only, page not opened): bisection "adds a couple of extra CI runs".
- Bears on us: our "one full gate per batch, repair on red" is batching; the vendor model for red is automatic bisection and ejection, not a model repair.

**B5. Jane Street, "Making 'never break the build' scale"** (2014-07-06). https://blog.janestreet.com/making-never-break-the-build-scale/ (read)
- Before: "a change would sometimes take 24 hours to get through the build-bot"; full build "two hours and up."
- Batch speculation: "speculate en masse by merging multiple requests together"; if a group fails you cannot tell the culprit, so requests are tested individually; with simple speculation "all failing requests are rejected back to their owner."
- Bears on us: same lesson, an old one: when the gate is slow, reduce the number of gate runs (batch) and reject failures to the owner.

**B6. The "not rocket science rule".** The original post (Graydon Hoare, 2014) was NOT opened. The Graphite article (https://graphite.com/blog/bors-and-merge-queues) returned 404; I read only a third-party summary (https://www.plushcap.com/content/graphite/blog/graphite-not-rocket-science-how-bors-and-googles-tap-inspired-modern-merge-queues-1): the rule "advocates for automatically maintaining code repositories that always pass all tests," and Bors "struggled with throughput." Treat as secondary. Zuul's own statement is the closest primary text: a gate "should always test each change applied to the tip of the branch exactly as it is going to be merged."
- Bears on us: the rule is about the main branch always being green and the process being automated, not about agents.

### C. Workflows versus agents

**C1. Anthropic, "Building effective agents"** (2024-12-19). https://www.anthropic.com/engineering/building-effective-agents (read)
- "Workflows are systems where LLMs and tools are orchestrated through predefined code paths." Agents "dynamically direct their own processes and tool usage."
- "workflows offer predictability and consistency for well-defined tasks"; "Agentic systems often trade latency and cost for better task performance."
- Orchestrator-workers: "a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results." (the page notes the tooling has changed since)
- Bears on us: the carry-gate-land path is well-defined, which this source assigns to workflows; deciding what to build next is the open-ended part.

**C2. Claude Code docs: dynamic workflows** (no date shown). https://code.claude.com/docs/en/workflows.md (read in full)
- "The difference is who holds the plan." Table: for subagents, skills and agent teams the decider is Claude "turn by turn"; for workflows "The script."
- "A workflow script holds the loop, the branching, and the intermediate results itself, so Claude's context holds only the final answer."
- Scale: workflows "Dozens to hundreds of agents per run"; agent teams "A handful of long-running peers." Limits: up to 16 concurrent agents by default, 1,000 agents per run, no filesystem or shell access from the script itself, no mid-run user input ("For sign-off between stages, run each stage as its own workflow").
- Resume: a failed agent in the middle of a fan-out "reruns work that already finished" on relaunch (A, B, C, D with B failed reruns B, C, D).
- Example prompt shapes: "Keep fixing until a check passes ... until the type check passes or two rounds in a row make no progress."
- Bears on us: the platform's own guidance is that the plan lives in a script when the loop is repetitive and fan-out is wide. Note the limits: a workflow runs to completion in the background and cannot take mid-run input, which fits a per-batch gate but not an open-ended session.

**C3. Claude Code docs: run agents in parallel** (no date shown). https://code.claude.com/docs/en/agents.md (read)
- Subagents "do a side task in their own context and return a summary"; agent view lets you "hand them off, check status at a glance, and step in only when one needs you"; "`/batch` ... split one large change into 5 to 30 worktree-isolated subagents."
- "Do the tasks touch the same files? Isolate the work with worktrees."

### D. Numbers collected

| Number | Source |
|---|---|
| 4x tokens (agent vs chat), 15x (multi-agent vs chat) | A1 |
| about 7x tokens for teams in plan mode | A9 |
| 3-5 teammates recommended; 5-6 tasks per teammate | A8 |
| 2-5 sessions (practitioner) | A13 |
| 20 agents -> effective throughput of 2-3 (lock contention, flat structure) | A4 |
| 16 agents, about 2,000 sessions, about $20,000, two weeks | A5 |
| 16% -> 45%+ utilization by going from 1 to 3 agents | A13 |
| GitLab default 20 parallel train pipelines | B2 |
| gate 2 hours and up, 24 hour waits before batching | B5 |
| 16 concurrent agents, 1,000 per run (Claude Code workflows) | C2 |

No source gave a controlled measurement of coordinator idle time, integration latency, or the throughput effect of a dedicated integrator. The Cursor integrator remark (A4) has no numbers attached.

## Part 2. Sources I could not open or read fully
- LangGraph / LangChain supervisor docs: redirect, nothing returned (search summary only).
- Graphite "bors-and-merge-queues": 404 (secondary summary only). Hoare's original "not rocket science" post: not opened.
- Mergify, Aviator, Uber SubmitQueue, Chromium CQ: not opened; search found no Uber or Chromium material.
- The Cognition "Devin bots" coverage (New Stack): search snippet only.
- Claude Code subagents page: last 14,792 characters not read.

## Part 3. Synthesis (my own, not the sources')

(a) Synthesis, under 400 words.

Agreement. Every source that addresses it says the lead should plan, delegate and receive short results, and keep detail in artifacts or worker contexts (A1, A6, A7, C2). Vendors name the lead doing the work itself as a failure (A8). All say writes are where parallelism hurts: conflicting hidden decisions (A2), same-file edits (A8), a monolithic task that 16 agents all hit (A5). Human CI practice is uniform: batch to cut gate runs, eject a red change back to its author, retest the rest (B1-B5). Platform docs say a script should hold the plan when the steps are known and repeated (C1, C2).

Disagreement. Cursor tried a dedicated integrator and dropped it as a bottleneck (A4); Cognition now endorses single-threaded writes (A3), which is an integrator by another name; Anthropic's compiler run used no orchestrator and no integrator (A5); Claude Code's agent-teams docs keep a lead that supervises. The split is really about where conflict resolution lives: with the worker (Cursor, compiler, merge-queue authors), or with one central writer (Cognition).

Not addressed. None of the sources measures an idle coordinator, a coordinator whose context is full of integration detail, or an integration agent running a heavy multi-minute gate while builders wait. None describes a repair of a red batch by an agent (human CI returns it to the author, which here means a builder). None covers a long-lived session's own context growth across a work day apart from the cost note (A9). Almost no numbers on 3-4 workers.

Strongest hint for our setup: the thing that idles worktrees is dispatch latency, and the consistent human-CI answer is "authors are not involved in carry; the queue is." Every source supports moving the carry and gate out of the dispatching loop; none supports one particular way to do it.

## Part 4. Options the sources support for THIS setup

**Option 1. Coordinator dispatches only, plus one standing integration agent in its own tree.** Matches the owner's proposal and OpenAI's handoff idea (A11) and Cognition's single-threaded writes (A3).
- Suggested cost: one more long-running context (A9: history re-read each request); more tokens (A1, A8); a second serial lane that can itself become the bottleneck (A4, which tried and dropped it).
- Risks: summary loss between builder and integrator (A1 says use artifacts, not summaries: pass commit ids and a record file); the integrator is only useful if its queue is shorter than the builders' completion rate; conflict resolution by someone who lacks the builder's intent (A3 "share a fork of the full context").
- Sources do not show it working or failing at our scale.

**Option 2. Scripted pipeline per builder (build, commit, carry, local check) with the coordinator handling only exceptions.** Supported by C1 and C2 (known steps belong in code, the coordinator's context holds only the answer) and by the merge-queue model B1-B2 (the queue does the carry, the author is freed).
- Cost: authoring and maintaining the script; a workflow runs without mid-run user input and cannot touch the filesystem itself (C2), so every step is still an agent or a command run by one; failed middle agents rerun later ones on resume (C2).
- Risk: a script cannot judge a conflict; each exception falls back to the coordinator, so the coordinator is idle only if exceptions are rare. Ask what fraction of carries conflict (see c).

**Option 3. Merge-queue script (carry plus one full gate per batch plus bisection), with an agent called only on a red batch.** The closest analogue to B1-B5: batch, bisect or eject, authors repair.
- Cost: the gate time per batch bounds throughput (B5); bisection adds gate runs (B4); a high red rate makes speculation wasteful (B3).
- Risk: "repair" in human CI is done by the author; here the author is a builder that may have ended. Sources give no precedent for an agent repairing a red batch other than "invoke a stronger model" (A3). Tradeoff B4: you give up proof that each change alone passes.

**Option 4. Cursor/compiler style: builders rebase and carry their own work, no integrator.** Supported by A4 and A5.
- Cost: each builder pays the gate's wall time, and the integration order is no longer controlled by one party.
- Risk: only supported by sources whose work is fine-grained and whose gate is cheap; ours is a heavy, once-per-batch gate, so the fit is uncertain.

A combination the sources do not contradict: Option 3's script as the carry/gate/bisect engine, Option 2's rule that a builder is re-dispatched (not the coordinator) to repair its own red change, and the coordinator reduced to dispatch plus a short status relay. That is my reading, not a published design.

## Part 5. Questions the sources cannot answer, which a measurement would

1. What share of carries conflict, and what share of batches go red, over the last N batches? (Decides between Options 2/3 and 1: B3 says a high red rate wastes speculation; A8 says the lead should only handle exceptions.)
2. Of the 23% idle time, how many minutes are carry, conflict resolution, gate wait, repair, and dispatch-itself (model thinking time)? The sources assume the lead's time is the cost; ours may be gate wall time, which no agent split fixes.
3. Does a repair by a fresh integrator agent succeed as often as repair by the coordinator or by the original builder? (A3 says shared context helps; nothing measures it.)
4. How large is the coordinator's context at hour 4 and hour 8, and does response latency or error rate grow with it? (A9 gives the mechanism, not the size.)
5. Is the gate itself parallelizable or cacheable so that batching matters less? (B4 mentions test caching for bisection as a vendor feature.)
6. With 3-4 builders and one gate lane, what is the queueing delay: is the integration lane utilization above about 80%? If so a second integrator or smaller batches helps; if not, an integrator adds cost only.
7. How many tokens does a standing integrator add per batch versus the coordinator doing it? (A1, A8, A9 give multiples only for other setups.)
