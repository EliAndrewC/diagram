# Spec-kit hooks and the subagent-check TDD procedure

*Project reference, split out of [`../CLAUDE.md`](../CLAUDE.md) so it is loaded on demand rather than in every session's context. CLAUDE.md keeps the short always-on version of these rules and points here for the full spec.*

**Load this file when:** the GM asks for a new rule that a REVIEW SUBAGENT should enforce (settlement-review, building-review), or you need the spec-kit auto-commit hook details.

---

**Subagent-check TDD (REQUIRED procedure for improving review subagents)**: when the GM asks for a new rule that a review subagent (e.g. `building-review`) should enforce, do NOT simply apply the fix and write the rule into the agent. The current artifacts contain the motivating defect - that is the failing test. Procedure:

1. Add only the **general, category-level rule** to the agent definition. Never name the specific instance yet - that would test nothing about whether the check generalizes.
2. Run the agent against the artifact that contains the known defect, unfixed.
3. **If it flags the defect**, the rule generalizes: now fix the artifacts, and only now record the specific instance in the agent definition as a validated example for future runs.
4. **If it misses**, sharpen the general rule and re-run - do not shortcut by naming the instance. Escalation ladder from the first application (2026-07): a trait buried in a checklist gets skimmed; adding a protocol step barely helps; what reliably works is making the agent's **output format demand an enumerated sweep** (a mandatory report section listing every item checked) - models do what the required output structure forces.
5. Record the red/green outcome in the artifact's review log.

**Gotcha (harness behavior)**: agent definitions are snapshotted when the session registers them - mid-session edits to `.claude/agents/*.md` do NOT reach agents launched by type, which silently invalidates the TDD run. When iterating on an agent definition, launch a `general-purpose` agent instructed to Read the definition file and adopt it; the registered type picks up the changes next session.

**Spec-kit hooks**: `.specify/extensions.yml` defines auto-commit hooks before each spec-kit step. Under the session-clone workflow (below), spec-kit work happens inside the session's clone, where committing is the session's job - the auto-commit hooks may run there. Never run them against main `/diagram` or `/host-l7r-repo`.

---

## The spec-kit doctrine in full

*CLAUDE.md keeps each rule in a line or two; this is the record - the GM's rulings and the
incidents behind them.*

**When to use spec-kit:**

- **Feature work** (a new generator, a new tier, a new tool, a new guard) -> invoke `/speckit-specify` and follow through plan -> tasks -> implement. The Constitution Check section in `.specify/templates/plan-template.md` is the gate that enforces the constitution at plan-time; skipping spec-kit on feature work means skipping that gate.
- **Tweaks and iteration** (wording fixes, regenerating one item, fixing one bug) -> just do the work directly. The constitution still applies, but the formal spec/plan/tasks flow is overkill.
- **Ambiguous cases** -> ask before chain-firing `/speckit-specify`.
- **A FEATURE IS FILED ONLY WITH THE GM'S APPROVAL** (GM 2026-10-10, feature 377: *"I have had problems where past Claude Code sessions have seen that there was work to be done, and then without asking me, filing a [spec-kit] feature for it, and then maybe they told me, but they told me in the middle of like two days worth of scrolling text where there's no way that I would have ever even seen it ... So I think that spec kit features should not be filed without my explicit approval"*). Found work that is not yours to do now is PROPOSED, in the turn's final message where the GM will read it, never only mid-stream; and the proposal prefers extending and reopening the feature the work came from over a new number (the GM, on feature 376: *"I probably would have preferred for the existing feature to be extended and then reopened rather than filing a new feature"*). A feature the GM approves carries `**Approved**: the GM, YYYY-MM-DD, "<their words, verbatim>"` in its `spec.md`: three words or more, the GM's own (a picked `AskUserQuestion` answer is quoted with its question). From feature 377 on, `scripts/hooks/feature-approval-hooks.sh` refuses a `git add` or commit that would stage a NEW feature without it, reading the GM's own messages in the session's transcript (typed prompts, messages sent mid-turn, answers to questions), with no escape; spec-lint's check 6 re-checks the form at the push for a commit the hook could not see (outside a session, or inside a `make` target). A feature to approve is not a reason to stop work: put the proposal in the final message and carry on. Reopening is the GM's preferred path and needs no approval when the session does the work and closes the feature again; what needs it is a reopen that LANDS open (amendment 1, the GM: *"the thing that I want to be asked about before it happens is having the number of features with open work that is not handled increase without my knowledge"*), refused at a session's `sync-with-main.sh done` or `push` for any feature number, by `make speckit-todo`'s own open/closed rule. New features before 377 are never checked.
- **Every task is classified `research: rendering` or `research: physical` when it is created, and a physical task carries its research as checkboxes** - `research pass`, `source-reader confirmed`, `recorded and cited`, `quote-check confirmed` and `source-applicability confirmed` (the `source-applicability` agent judged each new source BEFORE its numbers, claims or details reached a map or a rule) - that must be ticked before the task is. A rendering task is a map convention with nothing physical behind it (a caption's wrap); a physical task is about how a place was built, farmed, planted or lived in (a house's distance from the paddy). "The record already answers it" ticks the research-pass box WITH the pointer; enforced by `tests/test_task_research_boxes.py` at the gate.
- **Run the chain end-to-end, unattended** (GM 2026-08-15). Spec-kit here is externalized working memory - the same discipline that keeps a handoff to a human from dropping work: break it down, write it down, mark things off only when verified. It is NOT stage-gate ceremony, and the constitution is maintained pragmatically rather than artisanally. When implementing a spec-kit feature, run specify -> plan -> tasks -> implement straight through without pausing for GM approval between stages, answer each stage's own questions yourself, and record every resolved decision in the artifact where it arose.
- **Stop-and-ask calculus** (GM 2026-08-15): interrupt the run ONLY when a wrong guess would be expensive to unwind - an hour-plus of implementation that might be thrown away buys a question first. When a choice is cheap to adjust after the fact, make the call, finish the task, report what was chosen, and offer the adjustment. **A question about how the PROCESS goes - a cap, a waiver, a stuck choice of route - goes to the round arbiter first** (`make arbiter-ask`; about a spec or plan review's round, with `REVIEW=spec|plan`, so an accept stands as that review's verdict - feature 409; feature 379, GM 2026-10-10: *"things should go to the arbiter at the point where they were previously coming to me"*); a question about what to build stays the GM's. Asking beats redoing; redoing beats blocking on trivia. **This covers AMBIGUITY about what is wanted, and nothing else.** Difficulty in delivering something already known to be wanted is governed by constitution **Principle XV (Keep Going)**, and there the answer is to keep working.
- **THE GM STARTS WORK AND LEAVES** (GM 2026-08-23, constitution XV, NON-NEGOTIABLE). Stopping to ask "which of these should I do?" does not cost seconds of their attention - it costs the whole span until they return, and they come back to find the work where they left it. When a path forward exists, TAKE it; if one avenue is blocked, work the parts that are not. The only reason to stop is a genuine belief the thing cannot be done at all. If the options list contains "fix it and make it work", that is the answer and it does not need confirming. Two limits: this is never a license to exceed ordinary authorized work, and persistence means continuing to make PROGRESS, not continuing to make CHANGES - when stuck, the next step is a MEASUREMENT, not another speculative edit.
- **DO THE LITERAL THING; AN EXCEPTION IS NOT YOURS TO APPROVE** (GM 2026-08-24, constitution Principle XVI, NON-NEGOTIABLE). Asked for X, build X - never "X except where Y". This is the exact tension the project's own answer to spec-kit creates: sessions are told to answer their own questions rather than stop constantly, and the failure mode of that instruction is a session quietly resolving a question the GM had already answered. **The resolution is that exceptions are presumed wrong.** If one still looks necessary, an independent Opus subagent decides - given the GM's request VERBATIM - and the honest question to put to it is "am I carving out a case contrary to what I was told?". If it agrees, carry on and raise it with the GM once the implementation WORKS; the GM starts long work and comes back to a finished thing, so a mid-flight question costs them the whole span. The motivating case is a spec that said "farmhouses before lanes EXCEPT the connector and the field spur" when the GM had said "farmhouses before lanes".
- **A SPEC IS REVIEWED AGAINST THE GM'S OWN WORDS, BY SOMEONE ELSE** (same principle). Before implementation, hand the finished `spec.md` and the GM's request AS WRITTEN to an independent subagent: does this specify what was asked, and does it add anything that was not? Not the plan - a spec graded against its own plan is being checked for self-consistency, which a wrong spec passes. Adjust and re-review up to **five** times; if the FIFTH round still returns changes, the round arbiter rules before a sixth (feature 379: never the GM first; its `accept` stands as the verdict at the review gate), because that many failures means a persistent misunderstanding another attempt will not find. The cap exists to end an argument going nowhere, NOT to cut off a review still finding new, smaller things each round. **Watch the number**: if features start hitting five, the drafting is the problem, not the cap. **THE CAP COUNTS THE INITIAL REVIEW ONLY** (GM 2026-09-12: *"we should probably clarify the five round cap on reviews. That is intended for the initial creation of the spec ... it is completely fine to go past five rounds because what you're really doing is you're resetting the counter every time you make a change ... once the spec is accepted, then we set the counter to zero the next time that any changes are made mid implementation or later"*): the five rounds are the spec's first acceptance; a spec amended AFTER it was accepted - mid-implementation, because the design changed under measurement, or later - is re-reviewed on a counter reset to zero, five rounds again from the amendment.
- **One constitution for the whole repo, deliberately** (GM 2026-08-15): spec-kit's Constitution Check reads a single file, and the domain separation the project needs already exists in layers - the constitution carries universal principles; each domain's operational doctrine lives in its auto-loading directory CLAUDE.md (the diagram skill's is the exemplar); SKILL.md stays the usage-facing index. A rule that applies to only one domain belongs in that domain's CLAUDE.md, not in a forked constitution.

## Regressions and defects: the full rule

**FIXING IT IS THE EXIT.** Principle XIII's three ways out are not a menu (GM 2026-08-23): FIX is the expected outcome, REVERT requires a WRITTEN impossibility investigation rather than a preference, and a waiver is the GM's to grant after a fix has genuinely been attempted. A session that has found a path forward takes it.

**NO KNOWN REGRESSIONS - and nothing merges to main carrying one** (constitution Principle XIII, NON-NEGOTIABLE, GM 2026-08-17: *"never count our work as being done when there are known regressions. Nothing should EVER be merged back into main if even one single new regression was added."*). Two separate bars, and work routinely clears the first and fails the second:

- **A regression is measured, not remembered.** It is anything that passed before your change and fails after it - a test, a pool artifact, a cohort seed, a rate. Take the baseline on unmodified code in a **detached worktree** (`git worktree add --detach /tmp/base HEAD`), never by stashing - a stash mutates the tree under any review agent currently reading it. **And check each failure the worktree reports against your clone before calling it pre-existing**: a fresh worktree carries no GITIGNORED artifacts, so tests that read them fail there for reasons that have nothing to do with the code. The reverse is the dangerous half - the same gap can make a test pass ONLY in the worktree, hiding a real regression from the moment the baseline is taken.
- **Pre-existing failures are NOT regressions** - they do not block your push, and that distinction is exactly why the baseline is mandatory. They are NOT left alone either: one you find is fixed in the work at hand (Principle XIV). The old wording here - "they stay ledgered and are not fixed under someone else's feature" - was struck by the GM on 2026-10-01 (*"I didn't think that we had a rule about not fixing someone else's pre-existing failure under your feature ... We should strike that as a rule ... We should definitely fix the pre-existing failure"*), after it led a session to escalate a bug it had already traced instead of fixing it.
- **None of these excuses one**: it is small; it is "only" a cohort seed or a fixture; you documented it (a ledger entry tracks a regression, it does not permit one); the change fixes more than it breaks; or the residue "ROTATED" because a re-roll moved which seeds fail. On rotation specifically - where per-seed comparison survives, a check that passed on a seed and now fails is a regression; where the re-roll makes per-seed comparison meaningless, the pass RATE must not drop **and** every newly-failing check must be individually diagnosed.
- **Three exits only: fix it, revert it, or get the round arbiter's waiver** (`make arbiter-ask`, the GM reviewing it after landing - feature 379) for that specific regression. If you cannot fix it, STOP and say so - the work stays in the clone, **unpushed**. `sync-with-main.sh done` is not run on a regressed state; committing inside your own clone is still fine and correct (mid-task work is sacred).

**FIX DEFECTS WHERE YOU FIND THEM - bugs before new code** (constitution Principle XIV, NON-NEGOTIABLE, GM 2026-08-17: *"anytime we are working on the diagram skill and you in the course of implementing a feature come across some new defect - even if it is a defect that did not have anything to do with what you were working on - I would like you to fix it as part of that work ... in general, we should fix bugs before writing new code."*). A defect you find while doing something else is fixed IN that work, with the same verification anything else gets - not filed, not deferred to "its own pass". The **only** exception is a fix that would be a complete overhaul or a giant architectural change (a stage reordering, a new subsystem, a placement engine rewritten), and deferring one is a deliverable rather than a shrug: it carries the MEASUREMENT that establishes the defect, the mechanism, and an implementation sketch.

- **Do NOT reach for Principle XIII's "pre-existing failures stay ledgered."** That clause is about what BLOCKS a push. This one is about what you owe a defect you have actually seen. A pre-existing failure you never touched does not stop you shipping; one you found gets fixed.
- **Most of these arrive from the review subagents**, which are pointed at a DELTA and reliably find things outside it - that is an independent reviewer working, not scope creep. Same for a defect a diagnostic surfaces, a number that looks wrong while you were measuring something else, or a comment describing code that no longer exists.
- **The why is compounding** (the GM's own reasoning): the point of these generators is to expand them onto a foundation whose behavior is known-good. Every defect left in place is one the next tier inherits and builds over, entangled by then with work that assumed it. Keeping the floor level is what lets the building get taller.
- **Record a fix that FAILED, at the point of change.** A cheap wrong lever that measurably did nothing saves the next session from pulling it again - see the front-row lane cap's two recorded dead ends in [`hamletgen/homesteads.py`](../l7r/diagram/hamletgen/homesteads/__init__.py).

## Measured, enforced, escalated (feature 375)

The GM, 2026-10-10: *"anything that requires someone to just remember to do the right thing is not tenable"*. Feature 372's waves
105-111 cost about 120 dispatches for a dozen rows, the time going to loops, not fixes; feature 375 built each fix into the
tooling. **Measured**: a hook writes every tool call to the feature's event log, and `make feature-report F=NNN WRITE=1` turns
it into where the time went - every feature closes with one. **Decide, then check**: a task's decisions carry a verdict before
its checks run (`make decide`); a page is frozen while its checks run; a round's own edits go in once. **Owed by what changed**:
a pop-up's checks are triaged against the blocks that moved; a procedure claim is owed by its own line. **Escalated without
stopping**: a tripwire (a third round, a block that comes back, two red gates, checks out of proportion to the change) owes the
`round-arbiter` one binding ruling - continue, accept or process fault - in place of the GM's waiver, and the GM reviews every
ruling after the feature lands (`make gm-review`, `make gm-reviewed`). The full record: `specs/375-enforced-wave-process/`.
A ruling's `tooling_fix` is made, not lost (feature 379, the GM 2026-10-10: *"always implement this kind of tooling change
when recommended by the arbiter"*): it is an open item that holds every `make tick` and the closing check until `make
arbiter-fix-done` (what was built, its test) or, for an overhaul of a process, `make arbiter-fix-declined` - each a row of
the GM's review, and never a feature filed.

## Review subagents

**Review checks run on their OCCASION, in the background, never per task (GM 2026-08-26; feature 294, GM 2026-10-01)** - the GM looking at the map is the faster reviewer of a change that moves things under rules already judged; a check runs when what it judges is new or changed (an element new to a map, a glyph redrawn or re-placed, a map new to the pool, a declared occasion). Doctrine and the ledger in [`docs/reviews.md`](reviews.md). Every pass is a row in [`review-ledger.md`](../dev/review-ledger.md) - verdict, what it caught that the author missed, and what it missed that the GM then saw - so "is it pulling its weight" is a total, not an impression.

**Every subagent check runs on the TIER its file pins - a model and an effort - whatever the session runs on** (GM 2026-09-07: *"our subagent checks should all specifically use the Opus model, regardless of what the main claude code session uses"*; GM 2026-09-19, feature 251: tiered by model and effort, judgment on Opus, the mechanical parts moved into scripts). `tests/test_agent_models.py` holds the table and fails the gate on a file that omits either key, inherits, or disagrees with it. A downgrade stands only after SEEDED-FAULT runs - the new tier re-run on recorded checks with known findings (`specs/251-tiered-subagent-checks/measure/seeded.py`), **three runs a leg** (GM 2026-09-21). The count is the correction feature 260 left behind rather than made: 260 replaced the bar for whether a check may READ LESS, because "it reports the same findings" asks two open-ended reports to agree and no pair of runs ever does. The seeded-fault rule is not broken that way - its target is fixed in advance, which is the same structural fix - but it was written "a run", singular, while feature 256 measured that ONE run of a judging agent is not a stable oracle (both legs of most pairs caught what the other missed, and `spec-fidelity` was left unsettled pending *"a three-samples-a-leg run"*). A single run invites a downgrade on variance, in either direction, and nothing catches a review agent that has quietly started under-calling. Three is 256's own number, inherited rather than measured; measuring where the verdicts stop moving would mean re-running 251's cases three a leg across several agents, and is a feature rather than this line. On 2026-09-19, before the count was written down, Sonnet for `record-format` and `source-reader` and medium effort for later `spec-fidelity` rounds each missed a recorded finding and went back up, while `quote-check`, `entry-drift` and `escalation-check` held at medium; the follow-up runs then put `record-format` on Opus at medium (every finding hit at about two thirds of the cost) and confirmed the rest (`research.md` R7). Later `spec-fidelity` rounds are routed by `review-round-hooks.sh` to `spec-fidelity-verify`, the same review on a shorter contract, and are refused first when the feature directory still carries the old value of something the change replaced (`make stale-terms F=<n>`, feature 253 - a cheap net with a narrow, measured reach: it sees a value left behind, not a sentence made false). An ad-hoc agent is dispatched with an explicit `model` - `sonnet` to read, fetch, translate or extract, `opus` for anything that judges, `haiku` only for a plain description of a page (it misread a table's columns where sonnet did not) - and never with none: the census (`make agent-census`) found 72 ad-hoc runs with no model, 62 of them on Fable.

**What every dispatch of a check shares lives in its agent file (GM 2026-10-17, feature 383 amendment 6).** Only a subagent's system prompt - a defined agent's file - is reused across launches: its first message, which holds the
instruction files and the launch prompt, has no cache breakpoint, so anything in it that is not identical as a whole is written
to the cache fresh (383 research R16) (1.25x the input rate at the 5-minute tier
subagents get; a read is 0.1x). Measured over 1,395 runs of 2026-10-10..17 (`make subagent-cache`, research R13 of 383): a
defined agent dispatched minutes after another of its type writes ~2.5-3.5k tokens fresh on its first call - its prompt and the
harness's environment block - and reads its agent file from the cache; `spec-fidelity`, keeping the instruction files, wrote
~25.8k fresh even back to back, and the ad-hoc triage agents ~29.2k; the modal checks' bundles each repeated the guidelines,
15-17k characters. So: a check dispatched again and again is a DEFINED agent (the claims and modal triage became two); text its
bundles would repeat is in its agent file (`make agent-sync` writes the modal guidelines there, `tests/test_agent_sync.py`
keeps them in step); a bundle carries only its unit (`tests/tooling/test_bundle_shared_text.py`: two bundles of a check share
under 2,000 characters); a prompt repeats nothing of another of its type, wherever it would sit - only the agent file is reused across launches, text placed first in a prompt is not (383 research R16, a proxy capture) - and a wave of 4 or more of one type goes through the `check-wave` workflow, which wakes the session once (383 amendment 7; `agent-prefix-hooks.sh` refuses a 4th hand launch within ten seconds, `workflow-hooks.sh` holds each unit to the Agent guards). A defined agent's file is read when a
session starts: a change to one reaches a session's dispatches after it restarts.

**Review subagents are pre-authorized (GM 2026-07-27).** Claude Code's default system prompt tells a session not to call the Agent tool unless the user asked - a sensible default that nonetheless sits ABOVE CLAUDE.md in the instruction hierarchy, so it silently outranked the mandate to run `settlement-review` before shipping a Mode B map, and maps went out unreviewed with nothing warning. The fix is [`scripts/container/append-system-prompt.md`](../scripts/container/append-system-prompt.md), loaded via `--append-system-prompt` by the `claude()` wrapper that `setup-dev-env.sh` installs into `~/.bashrc`: it lands AFTER that line with the same authority and grants standing authorization for the review agents only. **If a review agent ever gets skipped again, check `type claude` first** - the wrapper is per-container and dies with a rebuild. Since 383 amendment 7 it also authorizes `Workflow` for a wave of 4 or more of the named check jobs, through `check-wave`; broad fan-out, any other `Workflow`, and deep research still need an explicit request.

## Models tried

Load this section when: someone proposes running a review check on a cheaper model, or asks whether one was tried. The GM,
2026-10-17, on finding no record of these trials: *"I have checked and I cannot find any record of us having tried those"* - so
every trial, either way, is a row here. The method is `scripts/measure/model_trial.py` (a recorded Opus run with known
findings re-run in a clone at the commit it read, three runs a leg); a check moves only when every run finds every known
finding and raises no false alarm. The tier each check runs on is `tests/test_agent_models.py`.

| check | tried | when | result | record |
|---|---|---|---|---|
| record-format | Sonnet (the alias at the time), medium and high | 2026-09-19 | missed findings; stays Opus | `specs/251-tiered-subagent-checks/research.md` R5, R7 |
| source-reader | Sonnet (the alias at the time), high | 2026-09-19 | missed findings; stays Opus | 251 R5 |
| spec-fidelity-verify | Opus at medium effort | 2026-09-19 | missed findings; stays high | 251 R5 |
| quote-check, entry-drift, escalation-check | Opus at medium effort | 2026-09-19 | held; medium | 251 R5 |
| settlement-review, fix-check | Sonnet (the alias at the time), high | 2026-10 (feature 294 T34) | found the seeded fault 3 of 3; ON SONNET | `specs/294-settlement-review-rethink/` |
| spec-fidelity, glyph-check, impl-drift, building-review, modal-form, modal-research, modal-depiction | Sonnet 5.5 | 2026-10-17 | each missed a known finding in all or most runs; stay Opus. Sonnet found two real modal errors Opus had missed | `specs/383-tooling-caches-and-hourly-step-back/research.md` R10 |
| translation-check, intro-check, record-style, source-applicability, size-audit, round-arbiter, perf-audit, source-filter | - | never | on Opus untried | - |

## The development workflow of the root CLAUDE.md, in full

(moved VERBATIM from the root CLAUDE.md on 2026-10-17, feature 383 amendment 6, plan D44: the root keeps one line per rule and an index)

Spec-driven development under `.specify/memory/constitution.md`; this file operationalizes it. The
full doctrine with the GM's rulings and the incidents behind them: `docs/spec-kit-and-reviews.md`.

- Feature work (a new generator, tier, tool or guard) is a spec-kit feature: `/speckit-specify` ->
  plan -> tasks -> implement. A tweak (a wording fix, one bug, one regenerated map) is done directly.
  Ask before chain-firing on an ambiguous case.
- A spec number comes from `make claim SLUG=<slug>` (one lock over every clone; `PEEK=1` looks
  without claiming). It prints the `SPECIFY_FEATURE` and `SPECIFY_FEATURE_DIRECTORY` exports; export
  BOTH. Commit and push the spec directory as soon as `spec.md` exists. No feature branches: commit on
  `main` inside the clone.
- Open work lives in `specs/` only (feature 330: the old backlog directory became features). **A feature is filed only
  with the GM's approval** (feature 377, GM 2026-10-10: *"spec kit features should not be filed without my explicit
  approval"*): propose it in the turn's FINAL message, never only mid-stream, and prefer extending and reopening the
  feature the work came from over a new one. A session may reopen a feature to do work itself and close it again
  without asking; a reopen that LANDS open needs the approval too (amendment 1: the count of features with open work
  never grows without the GM). Once the GM says yes, the `spec.md` carries
  `**Approved**: the GM, YYYY-MM-DD, "<their words, verbatim>"`; from 377 on, a commit staging a new feature without
  it, or with words the GM did not write in the session, is refused (`feature-approval-hooks.sh`). Ask `make
  speckit-todo` what is open: filed, planned, in progress. Each spec names what it touches in an `**Affects**:` line (tags from
  `.specify/affects.json`: the diagram kinds, tooling, research, ...), and its stage - `now`, `village`, `town`, `provincial city`,
  `capital` - is derived as the earliest among its tags (`BY=affects` groups by tag, `AFFECTS=<tag>` lists only that tag's; `CHECK=1`, run at the push, holds it). Everything owed when a tier is scripted is ONE feature, that tier's placeholder
  (`placeholders` in `.specify/affects.json`: 380 village, 381 town, 382 provincial city; GM 2026-10-10): a new item owed at
  a tier is added to its placeholder, never filed on its own (`CHECK=1` refuses one). A feature closes when every task is ticked, or when its status line opens
  `Done`, `Superseded by NNN` or `Withdrawn` with the evidence beside it.
- Every task is `research: rendering` or `research: physical`; a physical task carries the boxes
  `research pass`, `source-reader confirmed`, `recorded and cited`, `quote-check confirmed` and
  `source-applicability confirmed`, ticked before the task is (`tests/test_task_research_boxes.py`).
- Every feature ends with `make feature-report F=NNN WRITE=1` - where its time and dispatches went, from the hooks' event
  log; its last `make tick`, a closing status line and `make gm-reviewed` refuse without it, and without any measurement
  another spec carried to it (`Carried: SC-nnn -> NNN <key>`). A feature lands with the GM's review open when it has a row
  for him (an arbiter ruling, `make accept`); `make gm-review` lists them. (Feature 375.) A row the GM discussed in the session and
  agreed needs no more action IS his review: run `make gm-reviewed F=NNN WORDS="<his words, verbatim>"` in that turn (GM 2026-10-10).
- Decide first, then check (feature 375): a task's decisions carry a verdict before its checks run - the plan-stage review,
  or `make decide F= T=` on a plan section naming the task (`make task-start` names the task). A tripwire is not the session's
  to judge: its refusal names `make arbiter-bundle`, and an advisor asked about a loop is handed that MANIFEST too.
- Run the chain end to end, unattended. The GM starts work and leaves: answer each stage's own
  questions, record each decision in the artifact where it arose, and stop only when a wrong guess
  would cost an hour-plus to unwind or the thing genuinely cannot be done. Persistence means
  PROGRESS, not changes: when stuck, the next step is a measurement. A PROCESS stop - a cap, a waiver,
  a stuck choice of route - goes to the round arbiter first (`make arbiter-ask`), never straight to
  the GM (feature 379, GM 2026-10-10: *"things should go to the arbiter at the point where they were
  previously coming to me"*); what to build stays the GM's question.
- Do the literal thing (constitution XVI). Asked for X, build X, never "X except where Y". An
  exception that still looks necessary is put to an independent `spec-fidelity` subagent with the
  GM's request verbatim; if it agrees, carry on and raise it with the GM once the implementation
  works.
- A spec is reviewed against the GM's own words by `spec-fidelity` before implementation
  (`scripts/gates/review-gate.sh` refuses the push otherwise): up to five rounds on the initial acceptance,
  then the round arbiter rules (a sixth round waits for it; feature 379); an amendment after acceptance resets the counter. A plan's decisions are
  reviewed by the same agent before a task is ticked (`make tick`, `scripts/gates/plan-gate.sh`) - block by block since 375
  amendment 11: a changed block owes `make plan-delta F=<n>` (a review of that block alone, on a lean bundle), never the whole
  plan again, and `make plan-archive F=<n>` moves finished sections to `plan-done.md`, which no review reads. A later
  round is handed the previous verdict and the diff by `scripts/hooks/review-round-hooks.sh`.
- No known regressions (constitution XIII). A regression is measured, never remembered: the baseline
  is taken in a detached worktree (`git worktree add --detach /tmp/base HEAD`, never a stash) and
  each failure is checked against the clone, because a worktree carries no gitignored artifacts.
  A pre-existing failure does not block a push, but one you find is fixed in the work at hand
  (XIV; GM 2026-10-01: "We should definitely fix the pre-existing failure"). Three exits: fix it,
  revert it with a written impossibility investigation, or the round arbiter's waiver (`make arbiter-ask`; the GM
  reviews it after landing); fixing is the expected one. A regressed state stays in the clone, unpushed.
- Fix defects where you find them (constitution XIV), in the same work with the same verification.
  The only deferrable fix is a complete overhaul, and deferring one delivers the measurement, the
  mechanism and a sketch. Record a fix that FAILED at the point of change.
- Review checks (`glyph-check`, `settlement-review`, `fix-check`, `building-review`, `size-audit`) run ON
  THEIR OCCASION (feature 294): an element new to a map, a glyph redrawn or re-placed, a map or sheet new to the
  pool, or an occasion the feature declares in its `tasks.md` `## Occasions` - never because a manifest moved
  (`review_owed.py`; `docs/reviews.md` has the table). One unit per agent, on a green gate,
  two rounds at most; every pass is a row of the ledger's measured table with its cost (`make review-cost`). To improve one, add
  the general rule, prove it fires on the unfixed artifact, then fix the artifact. Findings for the
  GM go through `escalation-check` first. Every check runs on the TIER its file pins - a model and an
  effort, never inherited (`tests/test_agent_models.py` holds the table; judgment is on Opus, and a
  downgrade stands only after seeded-fault runs on known findings - THREE a leg, because one run of a
  judging agent is not a stable oracle; which checks were tried on which model, and how they did: `docs/spec-kit-and-reviews.md`
  "Models tried"). An ad-hoc agent is dispatched with
  an explicit `model` - `sonnet` to read, fetch, translate or extract, `opus` for anything that judges -
  and never with none: with none it runs on the session's model, and `agent-model-hooks.sh` refuses it
  (`haiku` only for a plain description of a page - it misread a table's columns where sonnet did not). A DEFINED agent launches without this file, the nested `CLAUDE.md` files and the memory index
  (`omitClaudeMd: true`, feature 256, GM 2026-09-19: *"If there's something that a subagent should know, it should be in
  the subagent specification"*) - a rule a check needs is written in its contract, and a new agent file carries the field;
  an ad-hoc agent keeps all three (the tier test enforces the field on every agent file; `spec-fidelity`'s exception ended
  2026-10-17 when three runs a leg found every recorded item without the files - feature 383 research R14). **What every dispatch of a check shares lives in its
  agent file** (feature 383 amendment 6, the GM 2026-10-17: *"any context that subagents share in common is put either into
  their system prompt, ideally, or ... at the very beginning of the prompt"*): only a subagent's system prompt - its agent
  file - is reused across launches; text placed first in a launch prompt is not (feature 383 research R16, a proxy capture),
  so a bundle or a prompt carries only its unit; `agent-prefix-hooks.sh` refuses a large block a prompt repeats from an
  earlier dispatch of its type wherever it sits, and a 4th hand launch of a type within ten seconds (a wave goes through
  `check-wave`, amendment 7), `tests/tooling/test_bundle_shared_text.py` holds the bundles to it, `make agent-sync` writes a shared source
  into its agents' files, and `make subagent-cache` measures what each type writes fresh. The review agents are pre-authorized through
  `scripts/container/append-system-prompt.md`; if one is skipped, check `type claude` first.
