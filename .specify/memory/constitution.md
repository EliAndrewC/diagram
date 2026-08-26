<!--
SYNC IMPACT REPORT
==================
Version change: 2.7.0 → 2.8.0

Version 2.8.0 (amended 2026-08-26, feature 133 T19): the Development Workflow gains "A test's cost is a
cost, and the phase sets the standard" - the GM's ruling that, in this phase, a slow test must earn
its time: sweeps run a documented subset by default and their exhaustive form on request
(`EXHAUSTIVE=1`), with the last exhaustive green recorded in the docstring; the balance may swing
back when wrong maps become the larger problem. MINOR.

Version 2.7.0 (amended 2026-08-26, feature 133): Principle XII gains "A GUESS IS THE LAST RESORT - THE
RESEARCH PASS ALWAYS RUNS FIRST": any decision that would be labelled a guess gets the search pass
before it is recorded, whoever raised the question and however small it looks (the GM: *"that is the
kind of project that this is"*). MINOR.

Version 2.6.0 (amended 2026-08-26, feature 133): the Development Workflow gains "Reviews run at
acceptance and unlock, in the background" - under the scope lock the GM is the reviewer of the one
map on the sheet and no per-task `settlement-review` runs; a review never blocks the GM's look and is
never waited on; every pass is a ledger row. Also: linters autocorrect, never fail (ruff --fix +
format in place); the batching guard exempts image reads. MINOR.

Version 2.5.0 (amended 2026-08-26, feature 133): Principle XII gains "EVERY RENDERING DECISION IS
CAPTURED FOR THE READER WHO WILL CLICK ON IT" - the GM's statement of the long-term goal (interactive
HTML maps where a player hovers or clicks a feature and learns what it is, why it is there, and
whether it is historically accurate, a deliberate deviation, or a guess) and the three-way
classification every decision must carry from now on. The spec template gains a mandatory
"Decisions Recorded" section; the plan template's Constitution Check gains the row. MINOR.

Version 2.3.0 (amended 2026-08-25, feature 133): the Development Workflow gains "Iteration
wall-clock is the cost" - the GM's statement of the goal every guard, gate and switch in this
repository serves, recorded so every future session judges its commands, its tooling proposals and
its use of the tooling against it.

Version 2.2.0 (amended 2026-08-25): history is never rewritten - no squashing, no rebasing, no
amending of shared commits, no force pushes (GM 2026-08-25), enforced by the repo-safety hook. A
new rule in Principle VI: MINOR.

PRIOR (2.0.0 → 2.1.0):

Version 2.1.0 (amended 2026-08-25): Principle VI's performance clause becomes the GM's three-band
matrix (feature 129): any increase on the total or any seed owes an explanation confirmed by the
perf-audit subagent; >5% / >10% the subagent's escalated audit on the three criteria; >10% / >20%
the GM's personal sign-off before the push - each environment judged against its own history, a
cross-environment comparison refused. The 10% merge-blocking cap is retired (the GM: no ceiling so
long as the reviewer agrees). Records are bound to commit + numbers; the push enforces them. MINOR:
an existing principle materially expanded.

PRIOR (1.16.0 → 2.0.0):

Version 2.0.0 (amended 2026-08-25): THIS REPOSITORY'S EDITION. The constitution was copied verbatim
from gm-assistant when feature 131 split the diagram skill into its own repository, and the GM asked
for the copy to be fixed. Principles I (viewports) and II (design) govern a webapp this repository
does not contain; they are retained AS NUMBERED so the dozens of references to III-XVIII by numeral
stay true, and marked NOT APPLICABLE HERE with a pointer to gm-assistant's edition. Principle V's
canonical-sync exception is gm-assistant's; here SOURCE blocks are frozen excerpts. Principle VI's
UI bullet, Principle X's chargen references, the Technical Standards (Playwright, CherryPy, Fly,
configobj), the screenshot workflow, the memory path and the runtime-guidance path are rewritten
for /diagram. Nothing that binds the diagram engine changed in meaning. MAJOR, because two
principles are scoped out of force - the honest label for "removed", even though their numbers stay.
The version history below this entry is gm-assistant's and is kept as the shared lineage.

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Principle I/II gate entries now say "not applicable in
                              this repository" and the VI entry names make done / the review agents.
  ✅ CLAUDE.md - the version line.

PRIOR (1.14.0 → 1.15.0):

Version 1.15.0 (amended 2026-08-24): adds Principle XVIII - a guard ships with its test companion and
that companion RUNS in the gate. Motivating measurement: the enforcement audit found eight hook
scripts, eight test companions, and nothing executing any of them. Also records the two-directions
rule (fire, and stay quiet), the mention-is-not-an-invocation failure that produced seven false
positives in one feature, and the escape-checked-first rule without which a guard cannot be repaired
through the channel it guards. Enforced by `make hooks-test` as a gate phase. New principle: MINOR.


Version 1.14.0 (amended 2026-08-24): adds Principle XVII - a session never creates or edits a
README. The reason is mechanical rather than stylistic: a README is not loaded into context, a
directory CLAUDE.md is, so knowledge parked in a README is found only by luck. Motivating case: the
"an append-only log must be a DIRECTORY, because concurrent clones conflict" rule lived in
dev/perf-log/README.md; a session read and quoted it during an audit, then created a single-file
run-log.jsonl hours later. Three such READMEs became CLAUDE.md files in the same change, and
scripts/readme-hooks.sh enforces it. New principle: MINOR.


Version 1.13.1 (amended 2026-08-24): Principle XIII gains one clause - a detached
worktree baseline is a starting point, not a verdict, and each failure it reports is
checked against the clone before being called pre-existing. A fresh worktree does not
carry GITIGNORED artifacts, so tests that read them fail there for reasons unrelated to
the code. Measured during feature 127: the worktree gate reported 2 failures that both
passed in the clone at the same commit, the worktree holding 20 pool PNGs against the
clone's 28. Amendment: PATCH - it strengthens the accuracy of an existing procedure
without changing what the principle requires, the same call made for 1.12.1.


Version 1.13.0 (amended 2026-08-24): adds Principle XVI (Build What Was Asked;
Fidelity Is Not Self-Adjudicated). The default is the literal request, exceptions
are presumed wrong, and neither an exception nor a finished specification is
graded by the session that produced it - both go to an independent Opus 5
subagent, the spec reviewer receiving the GM's request VERBATIM rather than the
plan. Three review rounds, then escalate to the GM. New principle: MINOR.
Motivating case: feature 126, asked for as "farmhouses before lanes", was
specified as farmhouses before lanes EXCEPT the connector and the field spur -
an unrequested carve-out written by the implementing session and then implemented
faithfully, so the feature under-delivered while every instruction was followed.
This extends Principle I's author-is-not-reviewer rule from outputs to the
specification itself, which was the last artifact a session both wrote and graded.


Version 1.12.1 (amended 2026-08-23): replaces the two-command reference-first
workflow with ONE self-scoping command. `make maps` reads how the last run went -
passed means the whole tier with every failure reported, failed means the
reference map alone stopping at the first problem, and only widening once it is
clean. One piece of state drives both scope and verbosity. The two-command
version lasted about an hour before its own author reached for the expensive one
by habit, which is the argument: a choice is a thing that gets chosen wrong under
pressure. Applies to every settlement tier, not just hamlets. Amendment: PATCH -
it strengthens the enforcement of an existing principle without changing it.

Version 1.12.0 (amended 2026-08-23): makes the reference-settlement rule
STRUCTURAL rather than advisory. Every step of a generator feature is now two
steps - working on the reference settlement, then working across the pool - and
both are tasks with their own verification. The tooling defaults to the cheap
thing on purpose (SUPERSEDED BY 1.12.1 - that version's two commands, `make
map` and `make full-hamlet-sweep`, are gone; use `make maps`), because a wide
sweep that is cheap to invoke is what lets a session drift onto it unnoticed.
`make done` remains the backstop, which is what makes narrow defaults safe: the
gate re-checks the whole pool, so forgetting the sweep costs time, never
correctness. Amendment: MINOR. Motivating measurement: feature 126 spent five
10-12 minute four-map cycles chasing one connectivity defect that the reference
hamlet answered in 67 seconds - and the slow loop was itself the cause, because
waiting ten minutes for an answer is what tempts a session into guessing another
fix instead of measuring again.

Version 1.11.0 (amended 2026-08-23): adds Principle XV (Keep Going) and
rewrites Principle XIII's exits. The GM starts work and leaves the computer
for hours, so a session that stops to ask which option to take costs that
entire span, not a few seconds - and when one of the options is "fix it and
make it work", that is always the answer. XIII's three exits are no longer a
menu: FIX is the expected outcome, REVERT requires a written impossibility
investigation rather than a preference, and a WAIVER is the GM's to grant
after a fix has genuinely been attempted. Also adds the performance bookends
to Principle VI and the single-artifact rule for generators. New principle:
MINOR per the versioning policy. Motivating case: feature 126 (2026-08-23),
which produced four successive wrong diagnoses without measuring between
them and then stopped to ask the GM to choose among three options, one of
which was simply to fix the defect.
MINOR: Principle XIV (Fix Defects Where You Find Them) ADDED (GM-directed,
2026-08-17): "anytime we are working on the diagram skill and you in the
course of implementing a feature come across some new defect - even if it is
a defect that did not have anything to do with what you were working on - I
would like you to fix it as part of that work ... in general, we should fix
bugs before writing new code." A defect found during a piece of work is
fixed in that work; the ONLY exception is one whose fix would be a complete
overhaul or a giant architectural change, which is deferred with the
measurement and the sketch. This deliberately NARROWS Principle XIII's
"ledgered, not fixed under someone else's feature": that clause governs the
MERGE BAR (a pre-existing failure does not block your push) and no longer
licenses ledgering a defect you found and could have fixed. New principle:
MINOR per the versioning policy. Motivating case: the /diagram paddy
size-floor work (2026-08-17), where three `settlement-review` findings -
lane frontage regressed past the engine's own recorded 94 ft threshold, the
three shared byres collapsing onto three farmsteads, and a windbreak clipped
with 23 clumps drawn wholly off-canvas - had nothing to do with paddy basin
size, and the GM directed that all three be fixed before the feature landed
rather than ledgered. The rationale in his words: keep the foundation rock
solid, then hold that level of functionality as the skill expands into new
settlement types.

Sections updated:
  - Core Principles: Principle XIV added; Principle XIII's "ledgered, not
    fixed" sentence now cross-references XIV so the two do not read as
    contradicting each other.

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Constitution Check gains a
                              Principle XIV entry.
  ✅ CLAUDE.md - "Verification before reporting done" gains the
                              fix-what-you-find rule.
  ✅ .claude/skills/diagram/CLAUDE.md - the always-on list gains it, since
                              /diagram is where it bites hardest.
  ✅ .claude/skills/diagram/dev/reviews.md - states that a review finding
                              outside the delta is still yours to fix.

PRIOR (1.7.0 → 1.8.0):

PRIOR (1.8.0 → 1.9.0):
MINOR: Principle XII (Historical Grounding Bookends) gains two GM-directed
rules, 2026-08-18. (a) RESEARCH PRECEDES A RULING: a question about how a
place was actually built, farmed or lived in is answered by a research pass
BEFORE it reaches the GM, and an ask that does reach them must state what was
searched and why the finding does not settle it. Binds the review loop above
all, since a reviewer's "wants a one-line ruling" describes a question, not a
delegation. (b) TWO SUPPORTABLE ANSWERS BECOME A KNOB, NOT A CHOICE: where
research shows a thing was genuinely done more than one way, the variation
becomes a tunable per-settlement knob rather than a pick, because a project
goal is settlements within historical norms that differ from one another as
far as the research justifies - players must tell two maps apart at a glance.
This AMENDS the existing calibrated-liberty clause and takes precedence where
they differ; liberty survives only for a DEGREE along a continuum, never for a
choice between distinct FORMS. Motivating cases: the byre-beside-a-well and
back-rank-access questions, both of which had been queued as GM rulings and
were answered by a single research pass.

PRIOR (1.7.0 → 1.8.0):
MINOR: Principle XIII (No Known Regressions) ADDED (GM-directed,
2026-08-17): "never count our work as being done when there are known
regressions. Nothing should EVER be merged back into main if even one
single new regression was added." Two independently-binding halves - work
is not done while a known regression exists, AND nothing merges to main
carrying one. A regression is defined against a MEASURED baseline (taken on
unmodified code, in a detached worktree, never a stash); pre-existing
failures are explicitly NOT regressions and stay ledgered. The principle
enumerates what does NOT excuse one - smallness, "it is only a cohort
seed", having documented it, being net-positive, and the residue having
"rotated" under a re-roll - and names the only three exits: fix, revert, or
an explicit GM waiver for that specific regression. New principle: MINOR
per the versioning policy. Motivating case: the /diagram fan-toe needle fix
(2026-08-17), which resolved the GM-ruled sunburst on all four shipped
hamlets and 22 of 24 cohort seeds while regressing seeds 9 and 11 on
paddy_plot_seams_shared - net-positive, fully diagnosed, ledgered with an
implementation sketch, and under this principle still NOT mergeable.

Sections updated:
  - Core Principles: Principle XIII added.
  - Governance/Compliance: the stop-work ritual may commit in-clone but
    MUST NOT push a regressed state.

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Constitution Check gains a
                              Principle XIII entry (baseline measured,
                              zero new regressions at merge).
  ✅ CLAUDE.md - "Verification before reporting done" gains the
                              no-regressions merge gate; the session-clone
                              stop-work ritual now states the push bar.
  ✅ .claude/skills/diagram/CLAUDE.md - the cohort-baseline rule now says
                              a rotated residue is not a defense.

PRIOR (1.6.1 → 1.7.0):
MINOR: Principle X clause 14 (Rosters That Restate Code Are Derived, Not
Maintained) added (GM-directed, 2026-08-16). Clause 13 says a large file
prompts the split question; clause 14 says a roster-shaped file - one whose
bulk restates declarations the code already carries - takes a different
fix entirely: census the consumed surface, move the roster's safety
property into a guard test proven to fire, then DERIVE the surface (star
imports for re-export __init__s, introspection/generation for derivable
registry rows) instead of maintaining or splitting the roster. Drawn from
feature 027 (check_village/__init__.py, 3,148 -> 63 lines, zero consumer
changes), the named exemplar. New rule: MINOR per the versioning policy.

Sections updated:
  - Core Principles: Principle X clause 14 added.

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Principle X gate entry extended
                              with the clause-14 derive-don't-maintain
                              commitment.
  ✅ CLAUDE.md - "Files stay at human scale" operational mirror extended
                              with the clause-14 short form + the 027
                              exemplar pointer.

Deferred TODOs:
  - (carried) automated file-length check; clause 12's deferred
    expression-counting gate check.

PRIOR (1.6.0 → 1.6.1):
PATCH: Principle X clause 13 (Files Stay at Human Scale) clarified
(GM-directed, 2026-08-16): unit TEST files are covered exactly as source
files. The managed cost is context-window tokens, and a test file is loaded
under the same conditions as source - a session loads test_settlement.py to
modify one test the same way it loads settlement.py to use one function - so
nothing about being a test changes the economics, and tests get no
exemption. The ordered-data justification (a registry whose row order is the
execution contract) remains the only carve-out. Clarification of existing
reach, no new rule: PATCH per the versioning policy. Motivating case:
test_checks.py (11,475 lines) and test_settlement.py (7,123 lines), split by
feature 025 alongside settlement.py itself.

Sections updated:
  - Core Principles: Principle X clause 13 wording extended (tests
    included).

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Principle X gate entry says
                              "source or test file".
  ✅ CLAUDE.md - "Files stay at human scale" operational mirror says tests
                              are covered.

Deferred TODOs:
  - Automated file-length check (flags source files past the threshold
    lacking a justification header) - recorded alongside clause 12's
    deferred expression-counting gate check.

PRIOR (1.4.2 → 1.5.0):
MINOR: Principle X (Python Discipline) materially expanded - clause 12
(Functions Stay at Human Scale) added (GM-directed, 2026-08-15). A function
past a few hundred logical statements is suspect; past ~1,000 it is a defect
unless an inline annotation justifies why it must remain one body. Measured
in logic units (statements/expressions), never raw lines, so wrapped strings
and long call signatures never force a split. The 10-line-function dogma is
explicitly rejected. Motivating case: check_village.py's gate() reached
12,944 lines one check at a time, and the cost surfaced as an architecture
problem (nothing inside it could be invoked separately) before anyone chose
it.

Sections updated:
  - Core Principles: Principle X clause 12 added.

Templates requiring review/update:
  ✅ .specify/templates/plan-template.md - Principle X gate entry now names
                              the function-scale clause.
  ✅ CLAUDE.md - spec-kit working-style + single-constitution notes land in
                              Development Workflow the same day.

Deferred TODOs:
  - Automated expression-counting gate check (fails past threshold unless
    the function carries the justification annotation) - recorded in
    Principle X clause 12 as future work, deliberately not implemented as
    part of the 2026-08-15 gate-registry feature.

PRIOR (1.4.1 → 1.4.2):
PATCH: Technical Standards runtime bump - Python 3.13 -> 3.14 (GM, 2026-07-20),
matching the new standard dev container; the Fly prod image, both lockfiles,
both pyproject.toml pins (webapp + diagram skill), and CLAUDE.md move together.
Also drops the stale note that the chargen webapp pinned 3.10 (it no longer
does). No principle changes.

PRIOR (1.4.0 → 1.4.1):
PATCH: Principle XII gains a "calibrated liberty" clause (GM, 2026-07-19) -
where research shows a thing is plausible but the DEGREE is genuinely unclear,
a favorable reading within the plausible range may be chosen deliberately, on
condition that the choice and its range are disclosed in research.md and beside
the rule in code. Conjunctive conditions; does not license inventing a range or
overriding a finding that is actually clear. Also CORRECTS a factual claim in
XII's own motivating example: the 桑基魚塘 dike-pond system did NOT replace
rice across whole districts as the norm - the mixed scatter was normal, and the
principle's opening gate caught the error on its first outing (feature 010).

PRIOR (1.3.0 → 1.4.0):
MINOR: Principle XII (Historical Grounding Bookends) ADDED - any feature that
changes what a generator asserts about the world must open with a historical-
grounding analysis and close with a verification of the RENDERED ARTIFACT.
Motivated by the /diagram `rape` land-use overlay, which passed every
automated check and its tests while depicting two seasons of one crop
rotation standing simultaneously; only looking at the picture caught it.

PRIOR (1.2.0 → 1.3.0):
Principle I (Accessibility-First Viewports) materially expanded
to require scroll-through verification and to forbid column-height
asymmetry past 2.5× ratio. The added requirements were already implicit
in the principle's intent but had been missed in practice because no
artifact captured them - the new dom_audit layout-balance rule + the
multi-scroll contact sheets in screenshot.py now enforce them.

Principles (12) - Principle XII added; Principle I previously expanded:
  I.   Accessibility-First Viewports (NON-NEGOTIABLE)        [EXPANDED]
  II.  Bold, Intentional Design                              [unchanged]
  III. Pool Data Conventions                                 [unchanged]
  IV.  One Canonical Home for GM Source                      [unchanged]
  V.   Protecting the GM's Writing (NON-NEGOTIABLE)          [unchanged]
  VI.  Verify Before Reporting Done                          [unchanged]
  VII. De-Localized Generation by Default                    [unchanged]
  VIII.Direct Voice Over Framing Distance                    [unchanged]
  IX.  Setting Integration                                   [unchanged]
  X.   Python Discipline (NON-NEGOTIABLE)                    [unchanged]
  XI.  Japanese Authenticity (NON-NEGOTIABLE)                [unchanged]
  XII. Historical Grounding Bookends (NON-NEGOTIABLE)        [ADDED]

Sections updated:
  - Core Principles: Principle I expanded with layout-balance + scroll-
    through-review rules.
  - Development Workflow (operational mirror in CLAUDE.md): contact-sheet
    artifact + persona-based review now required for UI changes.

Templates requiring review/update:
  ✅ webapp/tests/screenshot.py - produces multi-scroll contact sheets.
  ✅ webapp/tests/dom_audit.py - adds layout-balance rule (sibling-height
                              ratio cap inside flex/grid containers).
  ✅ /gm-assistant/.claude/agents/frontend-review.md - new independent
                              reviewer agent (Constitution mirror).
  ⚠  .specify/templates/plan-template.md - Constitution Check entry
                              for Principle I should now mention "no
                              dead-space; contact sheet attached".
                              Deferred until next /speckit-specify run.

Deferred TODOs: none.

------------------------------------------------------------
Version 1.2.0 history (amended 2026-05-27):
  Principle XI (Japanese Authenticity) added covering kanji ↔ romaji ↔
  meaning alignment.

Version 1.1.0 history (amended 2026-05-27):
  Principle X (Python Discipline) added; Technical Standards / Workflow
  expanded with concrete tooling (ruff, mypy, pytest-cov, uv pip compile,
  configobj, pydantic-settings).

Version 1.0.0 history (initial ratification on 2026-05-27):
  Introduced Principles I-IX, the Technical Standards / Development
  Workflow / Governance sections, and the Constitution Check gate in the
  plan template.
-->

# L7R Diagram Constitution

This constitution governs the L7R Diagram project - the settlement and building
map generator (`/diagram`) for a custom Legend of the Five Rings tabletop RPG
setting, split out of the GM's `gm-assistant` toolkit on 2026-08-25 (feature
131). It is the highest-level guide for how Claude Code agents and human
contributors collaborate on this codebase. All specifications, plans,
implementations, and reviews MUST comply with the principles below.

It began as a verbatim copy of gm-assistant's constitution and the two diverge
from 2.0.0. The principle NUMBERS are shared lineage and are never reused: every
spec, plan, hook message and code comment in this repository cites principles by
numeral, so a principle that does not apply here is kept in place and marked
rather than deleted.

## Core Principles

### I. Accessibility-First Viewports (NON-NEGOTIABLE)

**NOT APPLICABLE IN THIS REPOSITORY.** This principle governs the webapp and
generated HTML pages, which live in gm-assistant. The diagram repository ships
SVG/PNG maps reviewed by `settlement-review`, `building-review` and
`size-audit` (Principle VI), not browser pages. The text is retained unchanged
for the shared numbering; gm-assistant's edition is the one in force for it.

The GM uses Chrome at 200% browser zoom on a 1850×1173 outer window
(effective CSS viewport ≈ 925×525). All UI work - webapp pages, generated
HTML, embedded previews - MUST be verified at the GM's actual viewport at
**both 100% and 200% zoom** before being declared done.

The following are **clipping** violations:
- Text truncated by `text-overflow: ellipsis` where the truncated portion
  carries information (clan names, named entities, type descriptors, etc.).
- Text or visuals clipped by `overflow: hidden` because a child exceeded
  its container's width or height.
- Elements whose `scrollWidth` or `scrollHeight` exceeds their corresponding
  `offsetWidth` or `offsetHeight` (excluding intentional internally-scrollable
  regions).
- Sticky / fixed elements that occupy more than ~25% of the 200%-zoom viewport
  height without strong justification.
- Tap/click targets smaller than 32×32 CSS pixels.
- Body / paragraph text smaller than 1rem; small-caps labels smaller than
  0.7rem.

The following are **balance** violations (added in v1.3.0):
- Inside a horizontal flex or grid container ≥600px wide with two or more
  visible children, sibling-element heights MUST NOT differ by more than
  **2.5×** when the taller sibling exceeds 200px. (The original failure
  mode: a short hero column beside a tall card stack produces a column of
  dead space below the hero when the user scrolls. Either bring the
  short column up in height or stack the layout vertically.)
- A vertical region larger than **30% of the viewport height** that is
  empty of content, decoration, or intentional negative space (no
  watermark, no rule, no whitespace clearly serving the composition) is
  itself a violation. Empty space is allowed only as a designed element.

A UI change is not complete until the verification workflow has produced:
  (a) **screenshots at the four standard viewports** (GM-100 1850×1050,
      GM-200 925×525, tablet 800×1100, mobile 390×844), captured as
      **multi-scroll contact sheets** for any page taller than 1.3× the
      viewport so mid-scroll layout is visible;
  (b) a **zero-issue DOM-audit report** covering both clipping and
      layout-balance rules above;
  (c) a **persona-driven review pass**: the reviewer (whether the same
      agent, the GM, or the frontend-review subagent at
      `.claude/agents/frontend-review.md`) MUST consider the page from
      the user's perspective ("Eli is opening this page; what is he
      trying to do here?") rather than as a static visual artifact.

The author of a UI change SHOULD NOT also be the sole reviewer. Where
practical, route the contact sheet to the frontend-review subagent for an
independent pass. The author rationalizes choices the reviewer would not.

### II. Bold, Intentional Design

**NOT APPLICABLE IN THIS REPOSITORY** - same reason as Principle I: it governs
frontend pages, which this repository has none of. Map style is governed by the
skill's own style library and design doctrine (`.claude/skills/diagram/SKILL.md`,
`settlements/`, `buildings/`). Text retained for the shared numbering.

Frontend work uses the official `frontend-design` Claude Code plugin and
follows its discipline: commit to a clear aesthetic direction per page,
avoid timid neutrals and generic AI aesthetics, and reject default typefaces
that no longer carry character (Inter, Roboto, Arial, system sans). Where the
content is Japanese-themed, the typographic system MUST pair a distinctive
display serif with a refined body serif and a Japanese mincho face; the
current canonical pairing is **Fraunces + EB Garamond + Shippori Mincho**.

A coherent palette is preferred to a balanced one: dominant tone, sharp
accent, intentional negative space. The current canonical palette is warm
washi paper, sumi ink, and vermillion accent (`#F4E8CC` / `#14110E` /
`#B8332A`). Deviations are permitted but MUST be deliberate, not accidental.

### III. Pool Data Conventions

Generated content of a kind that recurs (relics, names, vows, swords, etc.)
lives as individual markdown files with YAML frontmatter, organized into
per-category directories under `/.claude/skills/<skill>/pool/<category>/`.
Each entry's frontmatter MUST carry the fields needed for scriptable
filtering - at minimum a category slug (e.g. `fortune`) and a clan
designator (`clan: any | crab | crane | ...`).

Pool entries MUST be reusable across campaigns. They MUST NOT bake in
specific cities (`Kyuden X`, `Shiro X`, `Shinden X`) either in frontmatter
or prose. Where a clan-level designation is appropriate, use that (e.g.
"a temple of Ebisu in Crab lands"); where no clan is implied by the named
entity, use `clan: any`.

### IV. One Canonical Home for GM Source

Each piece of GM source content - text inside `<!-- SOURCE: GM NOTES - DO
NOT MODIFY -->` markers - has exactly **one** canonical home file. Other
files that need that content reference it by path and section rather than
duplicating the SOURCE block. This keeps canonical-source syncs surgical:
when the GM updates their notes, only one downstream file must change per
concept, and drift between duplicate copies is impossible.

When deciding where a source block belongs:
- Generation guidance (how to write a kind of thing, with worked examples)
  belongs in the relevant skill's `SKILL.md`.
- Setting reference (demographics, geography, hierarchies, fixed facts)
  belongs in a file under the relevant reference directory.
- If both, place it where the content leans heavier and have the other
  side reference.

**Exception:** `/notes/canonical-source.txt` is a sync diff baseline; it
intentionally mirrors the GitHub canonical source and is the one duplicate
the system requires.

### V. Protecting the GM's Writing (NON-NEGOTIABLE)

Content between `<!-- SOURCE: GM NOTES - DO NOT MODIFY -->` and
`<!-- END SOURCE -->` markers is the GM's original writing. It MUST NEVER
be modified, rephrased, summarized, reworded, or "improved" by any agent.
Only the GM may edit those sections, and only when they explicitly
instruct an agent to do so.

There is no automated exception in this repository. (gm-assistant's edition
carries one - its canonical-source sync workflow.) Here a SOURCE block is a
frozen point-in-time excerpt of the GM's notes; drift from the canonical
`/host-l7r-repo/setting/l7r.md` is expected and is never "corrected".

AI-generated content (preferences, generation instructions, examples of
liked/disliked output, scaffolding, layout text) lives outside SOURCE
markers and MAY be updated freely.

### VI. Verify Before Reporting Done

No agent or skill may report a task complete without verifying the actual
artifacts. Specifically:

- **Python**: the gate is `make done` in `.claude/skills/diagram/` (lint,
  format, `mypy --strict`, the hook suites, pytest with the coverage floors -
  nothing runs outside make, per feature 127). Target 100% line coverage on
  pure logic. External boundaries are tested via saved fixtures, not via
  transport-layer mocks.
- **Maps**: a Mode B map is reviewed by `settlement-review` and a Mode A
  plan by `building-review` + `size-audit` before it ships (the author is
  not a reliable reviewer of their own visual output); `review-gate.sh`
  enforces it at push time.
- **Delegated work**: When a subagent or skill reports completion, the
  caller MUST spot-check the artifacts (read a sample of changed files,
  run a verification query) before relaying the result to the user.
  "The agent said it was done" is not sufficient.

- **Generators: ONE ARTIFACT UNTIL IT WORKS, then the sweep** (GM 2026-08-23).
  A change to a generator is proven on a SINGLE named artifact first. The full
  cohort / pool sweep runs once, AFTER that artifact is fully working - never as
  the loop you iterate inside. Feature 126 is the case that produced this clause:
  a 48-map cohort was launched while the approach was still being tried out, one
  seed near-hung, and thirty minutes bought no result at all. A single hamlet
  rebuilds in well under a minute, so the same thirty minutes is thirty
  experiments instead of nothing.
  - The canonical hamlet is **Inashiro**, unless the feature names a better one
    and says why.
  - **EVERY STEP OF A FEATURE IS TWO STEPS** (GM 2026-08-23): get it working on
    the reference settlement, THEN get it working everywhere. A plan or task list
    that says only "make X work" is incomplete - it must say "make X work on the
    reference settlement" and, separately, "make X work across the pool". The
    second half is a distinct task with its own verification, not a footnote to
    the first.
  - **THERE IS ONE COMMAND, AND IT PICKS ITS OWN SCOPE** (GM 2026-08-23).
    `make maps` reads how the LAST run went and decides:

        last run PASSED -> the whole tier, reporting EVERY failure together
        last run FAILED -> the REFERENCE map alone, stopping at the FIRST
                           problem; only if it passes does it go on to the rest
        no last run     -> treated as FAILED

    **One piece of state drives both the scope and the verbosity**, and for the
    same reason: a failed previous run means you are mid-fix and want the fastest
    signal, so the run is narrow and stops early; a passed previous run means you
    are verifying breadth, so it is wide and collects everything - which is what
    `make done` already does. `SCOPE=reference` / `SCOPE=all` says what you mean
    when you know better; an adaptive default is right, but a tool that cannot be
    told the truth gets worked around instead of used.

    **There is deliberately NO second command.** An earlier version of this rule
    offered `make map` and `make full-hamlet-sweep` and relied on the session
    choosing correctly. A choice is a thing that gets chosen wrong under
    pressure: the reference-first rule was written into this constitution and
    violated by its own author six hours later, at a cost of five 10-12 minute
    four-map cycles chasing a defect the reference hamlet answered in 67 seconds.
    *"Just remembering to do the right thing always is much worse than having
    good tooling."*

    **Sequential is cheaper than it looks.** A reference run that passes costs
    about a minute before the wide run starts; a reference run that FAILS saves
    the wide run entirely. The apparent loss of parallelism is bought back many
    times over across a feature.

    **This is the general pattern for every settlement tier**, not a hamlet
    special case - `mapcheck.py` is a tier table, and villages, towns and cities
    each get a row and a named reference map as they gain live scripted gens.
  - **BYPASSING THE GATE COSTS A WRITTEN, AUDITED JUSTIFICATION** (GM 2026-08-24).
    `REF_OK=1` does not merely permit the expensive run: it demands a reason in
    prose and appends it to `dev/bypass-log.jsonl` with the date, target and
    commit. A flag you can type is a speed bump; a reason someone will READ is a
    decision you have to defend.

    **Every diagram feature MUST audit that log as a closing step** - read the
    entries added during the feature and state, in the feature's own artifacts,
    whether each bypass was justified in retrospect. Legitimate reasons: the
    reference map is itself under surgery; bisecting a knowingly-red tree; the
    subject is a check that only fires on a non-reference map. Not legitimate:
    wanting to see everything, or impatience.

    The rule exists because three separate guards were added during feature 126
    and each was walked around by reaching for a command the guard did not cover
    - `cohort_audit` when `make maps` was gated, `make done` and `make test` when
    both of those were. The measured cost inside that one feature: six 20-25
    minute cohorts, most launched over a tree already known to be broken. A guard
    on one command out of four is not a guard, and a guard with no audit trail
    cannot tell you it is being evaded.

  - **`make done` IS THE BACKSTOP, and it is why narrow defaults are safe.** The
    gate re-checks the whole pool, so a session that forgets the sweep entirely
    still cannot ship a map it broke. Cheap defaults trade no correctness - only
    the moment you find out.
  - The final sweep stays MANDATORY whenever shared code changed - this clause
    changes WHEN it runs, never WHETHER.
  - A feature that adds a KNOB owes one artifact per knob VALUE, not one per
    artifact in the pool: three maps, not forty-eight.

- **Generators: PERFORMANCE IS BOOKENDED, not remembered** (GM 2026-08-23).
  A spec-kit feature that touches the diagram generators records a performance
  snapshot BEFORE it changes anything and again BEFORE it ships:

      make perf LABEL=<NNN>-start     # first thing, on unmodified code
      make perf LABEL=<NNN>-end       # last thing, before the push
      make perf-report AGAINST=<NNN>-start

  **THREE BANDS, on BOTH measurements, PER ENVIRONMENT** (GM 2026-08-24 and
  2026-08-25; feature 129 - this replaces the two-band rule of 2026-08-24,
  whose 10% "cap" is now band 3's total line rather than a merge-blocking
  ceiling: *"there is no ceiling for allowing it to go forward so long as the
  subagent reviewer agrees"*, with the GM's own sign-off above it):

      band            on the TOTAL     on ANY SINGLE SEED   what it takes
      1  explain      any increase     any increase         a written explanation AND a perf-audit subagent confirming it matches the stage delta
      2  audit        > 5%             > 10%                the subagent independently finds the increase NECESSARY, COMMENSURATE with the functionality gained, and with NO GOOD WAY AROUND IT
      3  GM sign-off  > 10%            > 20%                the GM personally, at a terminal, BEFORE the work is committed back to main

  - A band fires when EITHER measurement crosses its line; each rung keeps
    everything below it. Feature 128's pair - total -29.9%, seed 47 +30.7% -
    is band 3: faster overall, and still the GM's to sign off.
  - **Each ENVIRONMENT is judged against its own history** - local against
    local, CodeBuild against CodeBuild - and a feature satisfies every
    environment it runs in. A cross-environment comparison is REFUSED, never
    displayed: on machines of different sizes the percentage is
    indistinguishable from a regression. Every snapshot records its
    environment explicitly; nothing infers it from a CPU count.
  - Explained means what CAUSED the change, in the session's words; the
    tooling pre-populates the delta and the per-stage breakdown so nothing is
    retyped, and a machine-written line is noticed, not explained. The
    measured per-seed noise floor (1.7% on this laptop) may be CITED in an
    explanation; it is never a bar below which nothing is owed.
  - The records - explanation, confirmation, audit, sign-off - are one file
    per event in `dev/perf-log/`, bound to the end snapshot's commit and exact
    percentages (a stale one is refused by name), carrying who granted them. A
    negative or inconclusive verdict never lets the work proceed.
  - Nothing distinguishes a subagent's shell from the session's (measured,
    feature 129 research R1), so the confirm/audit commands PROMPT and decline
    unless the caller declares `AS=perf-audit`; the `perf-audit` agent is the
    only one that does, and the main session launches it rather than writing
    the record itself. The gate PRINTS what a delta owes (`make done`); the
    PUSH enforces it (`make perf-review` in `sync-with-main.sh`).
  - Evidence is tiered: the per-stage delta every snapshot already carries
    (free, always) answers which stage grew; `make perf-profile` (cProfile of
    one stage of one seed, +225% on that stage - measured) answers which
    function, only when the stage delta cannot. Raw profiles stay out of this
    repository; the derived table (kilobytes) is committed and stands alone.

  Calibration: feature 126, the incident that created these bookends, was +51%
  total and +146% on its worst seed - band 3 five times over.

  - **Seeds, not one map.** The reference hamlet is rolled across a fixed seed
    set, because a single seed can be pathologically good as easily as bad.
  - **The start snapshot is also a health check.** Read the trend before
    beginning: if performance has drifted since the last feature, the first work
    is finding out why, not adding to it.
  - Snapshots live one-file-per-run in `.claude/skills/diagram/dev/perf-log/`, so
    concurrent clones never conflict. Never edit or delete one.
  - **History is never rewritten: no squashing, no rebasing, no amending of
    shared commits, no force pushes** (GM 2026-08-25). Every landing is a real
    merge commit with its parents. Two reasons: the commit history is the
    project's record of decisions; and the verified-tree records, the review
    records and the bookends are keyed by the content and commits that were
    tested - a rewrite would silently invalidate a paid verification. The
    `main` ruleset refuses force pushes and deletions to every credential;
    `scripts/repo-safety-hooks.sh` refuses `git rebase`, `pull --rebase`,
    `merge --squash` and `commit --amend` in a session.

  - This does not replace `GEN_TIME_BUDGETS`, which is a per-gen ceiling. This is
    a trend, and it answers the other question: is it getting slower, and when.

  Feature 126 is why this exists: it moved a stage and took one seed from 65s to
  160s, and nothing noticed until a 48-map cohort stalled a 20-worker pool for
  thirty minutes and was killed twice with no result.

Trust-but-verify is the working mode. Reporting a thing as done without
verification is a constitutional violation, not just a quality issue.

### VII. De-Localized Generation by Default

When generating an instance of a kind that the pool already organizes
(relics, names, temples, vows, etc.), the default framing is generic and
reusable: no specific city, no campaign-tied named samurai, no fixed
geographic coordinates. Use clan-level designators in temple / location
fields; let named entities sit at the family or peasant level rather than
the household level when no specific household is requested.

Specific scoping (Kyuden X, the Reiji domain, named PCs/NPCs, specific
campaign hooks) is permitted only when the user explicitly requests it.
When the user gives a specific scoping for in-session use, the resulting
content is for that session - it does not enter the pool until it has
been de-localized.

### VIII. Direct Voice Over Framing Distance

When writing in-world content - especially relic descriptions, vows, temple
material, and other quasi-religious or institutional writing - the
institution's own voice is used as direct statement of fact. Avoid
meta-narrational framings that hold the supernatural at distance:

- ❌ "The temple holds that the staff glows when Bishamon's favor is upon
  the inquirer."
- ✓ "The staff glows when Bishamon's favor is upon the inquirer."

- ❌ "Tradition says that a bandit who waylays a traveler within sight of
  the cord is tagged."
- ✓ "A bandit who waylays a traveler within sight of the cord is tagged."

Phrases to avoid: *"the temple holds that…," "tradition says that…,"
"the monks understand that…," "skeptics report no effect," "the temple
acknowledges privately that…"*

The supernatural ambiguity that the GM's setting cultivates lives in the
**layered evidence** (each piece of "proof" individually thin) and the
**unfalsifiability of soft claims** ("may," "are graced with," "some
pilgrims find"), NOT in distancing language about belief vs. skepticism.
Failure modes range from comfortable to harmful proof; the institution's
voice asserts what its own theology says, not what it "thinks."

### IX. Setting Integration

When generating content, draw on the GM's source notes under `/setting/`,
`/cosmology/`, `/campaigns/`, etc. for tone, style, and setting details.
Setting facts that are established in those notes MUST NOT be contradicted.

Skills SHOULD cross-reference reference directories rather than duplicate
their content. The CLAUDE.md files inside reference directories serve as
indexes - consult them before writing new content of an indexed kind, and
update them when adding new files.

When a relic, vow, or temple references a Fortune, clan family, lineage,
or setting figure, the reference MUST match the canonical setting as
established in `/cosmology/`, `/setting/`, and `/campaigns/`. New named
figures invented during generation MUST NOT collide with names already
in the campaign-names cache (see `/.claude/skills/name/campaign-names.txt`)
or with established figures in the GM's notes.

### X. Python Discipline (NON-NEGOTIABLE)

Python code in this project - the diagram engine and its generators, checks,
pipeline and tools under `.claude/skills/diagram/l7r/diagram/` - MUST meet
the following standards. Failing
any single rule is reason enough to refuse "done" status.

1. **Lint passes**: `ruff check` MUST pass on all production paths. The
   ruff configuration lives in a versioned `pyproject.toml`. Ruff is the
   single canonical lint tool (replaces flake8 / isort / pyupgrade /
   pylint); do not run alternatives alongside it.

2. **Format is canonical**: `ruff format --check` MUST pass. Ruff format
   is the single formatter (replaces black / autopep8); do not run
   alternatives alongside it.

3. **Type checking is strict**: `mypy --strict` MUST pass on production
   modules. Public functions and methods carry full type annotations.
   The per-module ratchet that once relaxed the legacy engine modules is
   fully retired (all of `settlement/`, `check_village/`, `waterfields/`
   are strict); new code is strict from the start.

4. **Red-green TDD**:
   - New non-trivial behavior is introduced **test-first**: the test
     exists and fails (red) before the implementation lands (green).
   - Bug fixes begin with a failing test that reproduces the bug.
   - Trivial code (one-line accessors, dataclass declarations, plain
     data transforms with no logic) is exempt.
   - In the commit history, where practical, a `test:` commit precedes
     or accompanies the `feat:` / `fix:` commit. Solo iteration may
     squash these; the principle is the order of work, not the shape of
     the history.

5. **100% line coverage on pure logic**: `pytest --cov-fail-under=100`
   is the enforcement gate for pure-logic packages. External-boundary
   modules (HTTP clients, browser sessions, Claude API calls, DB
   sessions, file I/O against external services) test against **saved
   fixtures** of real responses, not transport-layer mocks. Fixtures
   live in a `fixtures/` directory alongside the tests.

6. **Pinned dependencies**: `requirements.txt` is generated from
   `requirements.in` via `uv pip compile` (or `pip-compile`). Installing
   a package without updating the source-of-truth file is a violation.
   `development-secrets.ini` and similar secret-bearing files MUST stay
   gitignored.

7. **No swallowed exceptions in production code**: bare `except:` or
   `except Exception: pass` are forbidden. Always re-raise, log
   specifically, or handle a known exception type explicitly.

8. **No `print` in production code**: use `logging.getLogger(__name__)`.
   `print` is permitted in scripts and one-off dev tools; banned in
   library and service code that other modules import.

9. **Test names describe behavior, not implementation**: prefer
   `test_picks_random_name_when_no_filters_given` over
   `test_pick_name_1`. The intent of the test should read off the name.

10. **`pytest.parametrize` for variant inputs**: prefer a single
    parametrized test over a family of near-identical tests. The
    parameter list documents the variation surface explicitly.

11. **Configuration over hardcoding**: Magic strings and
    environment-dependent constants MUST NOT be hardcoded in production
    paths - the repository root, in particular, is derived from git
    (`gate-stamp`, the hooks, the ritual all do), never written as a
    literal, because it was `/gm-assistant` and is now `/diagram`.

12. **Functions stay at human scale** (added v1.5.0, GM-directed
    2026-08-15): a function that has grown past a few hundred logical
    statements is suspect and rarely the right shape in Python; past
    roughly 1,000 it is a defect unless an inline annotation at the
    definition explains why it must remain one body. Size is measured
    in LOGIC UNITS (statements/expressions), never raw lines: a call
    or string literal wrapped across lines counts once, so formatting
    never forces a split. The 10-line-function dogma is explicitly
    REJECTED - over-fragmentation damages design more than length
    does, and a deep-but-cohesive engine function is legitimate at a
    scale a utility function never is. The failure mode is GROWTH: no
    single edit crosses the line, so the line must be checked rather
    than felt. Deferred future work, recorded here so it is not lost:
    an automated gate check counting expressions per function, failing
    past the threshold unless the justification annotation is present.
    Motivating case: `check_village.py`'s `gate()` reached 12,944
    lines one check at a time, and the cost surfaced as an
    architecture problem - nothing inside it could be invoked
    separately - long before anyone would have chosen that shape.

13. **Files stay at human scale** (added v1.6.0, GM-directed 2026-08-15):
    a source file that has grown past roughly 1,000 lines prompts a
    question that MUST actually be asked: should this become a package
    of subfiles? The unit here is RAW LINES - deliberately unlike
    clause 12's logic units - because the motivating cost is token
    economy: a session that needs one function from a file pays
    context-window tokens for the whole file, and that cost scales with
    text, not logic. Unit TEST files are covered exactly as source files
    (clarified v1.6.1, GM-directed 2026-08-16): a test file is loaded
    under the same conditions as source - you load test_settlement.py to
    modify one test the same way you load settlement.py to use one
    function - so nothing about being a test changes the economics, and
    tests get no exemption. The target shape is a directory-module whose
    CLAUDE.md indexes the subfiles with a "look here when" line each,
    per the project's slim-index / load-on-demand doc pattern, so a
    future session loads only the part it needs. Like clause 12 this is
    an ask-the-question line, not a mandate: over-fragmentation damages
    design more than length does, and a file that is one cohesive
    ordered dataset (a registry whose row order IS the execution
    contract) may stay large - with an inline justification at the top
    saying why. The failure mode is the same GROWTH pattern as clause
    12: no single edit crosses the line, so the line must be checked
    rather than felt. Motivating case: `check_village.py` reached
    35,603 lines one check at a time and cost a full context window to
    consult; feature 024 split it into the `check_village/` package,
    the exemplar of the practice.

14. **Rosters that restate code are derived, not maintained** (added
    v1.7.0, GM-directed 2026-08-16): when a file's bulk is a
    hand-maintained roster whose rows restate what the code already
    declares elsewhere - a package `__init__` explicitly importing
    thousands of names its submodules define, an `__all__` list
    duplicating the import block above it, registry rows a machine
    could regenerate by introspecting the functions they point at -
    splitting it per clause 13 is the WRONG fix: duplicated
    information does not shrink by being divided. The right fix
    DERIVES the surface from the single source of truth (star imports
    for a re-export surface; introspection or generation for
    derivable rows) and moves any safety property the explicit roster
    was providing into a test that fails loudly (e.g. a guard against
    silent star-import shadowing), proven to fire on a synthetic case
    before it is trusted. Method, in order: CENSUS the consumed
    surface first - grep who actually reads each name, because most
    of a grown roster has zero consumers and simply drops; write the
    guard/surface test against the CURRENT file so the rewrite must
    preserve what is actually used; then derive; then run the full
    gate. The line against clause 13's ordered-data carve-out is
    INFORMATION: a roster stating real decisions (execution order,
    curation, hand-written per-row metadata that exists nowhere else)
    is data and may stay; rows reproducible from the code they
    reference are duplication and must go - and when one file mixes
    both, derive the derivable facts and keep the decided ones. The
    question is per-fact, not per-file. Motivating case:
    `check_village/__init__.py`, 3,148 lines of import rosters plus a
    duplicate `__all__` restating what 18 submodules already
    declared, reduced to 63 derived lines by feature 027 with zero
    consumer changes - the exemplar; full method in
    `specs/027-init-star-imports/`.

### XI. Japanese Authenticity (NON-NEGOTIABLE)

Any content this project generates or surfaces in Japanese script - relic
names, sword names, given names, place names, temple titles, vow refrains,
filter labels, decorative kanji - MUST satisfy a three-way alignment:

1. **The kanji are real Japanese characters.** Not Chinese-only characters
   absent from Japanese use, not invented glyphs, not mojibake. Each
   character must be one a Japanese reader could parse.

2. **The romaji is a plausible reading of the kanji.** A native speaker
   reading the kanji aloud could arrive at the romaji. On-yomi vs kun-yomi
   compounds are both acceptable; sokuon / rendaku contractions (e.g.,
   `鉄 + 旋 → tessen`) are acceptable; truly non-existent readings are not.
   The project's romaji convention strips long-vowel macrons (`ō` → `ou`,
   `ū` → `uu`); follow that style for consistency.

3. **The English name connects to the kanji's meaning.** Not necessarily a
   literal gloss - poetic translation is welcome - but a reader who knew
   what the kanji meant should be able to see the connection. "The Half-
   Mirror" rendered as `別れ鏡 / Wakare-Kagami` ("Parting Mirror") works:
   the English name takes the kanji's image and renders it idiomatically.
   `五代 / Goshu` would not work: the romaji simply does not match.

**Compound nouns** SHOULD be real Japanese words where possible. Constructed
compounds are permitted when the constituent characters carry meanings that
combine sensibly *and* the construction is explained in surrounding prose
(see `鉄旋 / Tessen` in `ebisu/sandals-of-the-walking-monk-tessen.md`, where
the prose names the character `旋 'circuit, turning'` as part of the monk's
identity). A constructed compound with no in-fiction explanation is a
violation.

**Stylized name readings** (a kun-yomi reading where Sino-Japanese would be
expected, an obscure kanji choice for a personal name) are permitted but
should be deliberate - preferably explained in prose if they would surprise
a reader. `業道 / Narimichi` is borderline-acceptable as a Buddhist-themed
monastic name; the same reading without monastic framing would not be.

**Hiragana-only words** (e.g., `お露 / Otsuyu` mixing honorific お with the
kanji 露) are acceptable when they reflect real Japanese naming or naming-
adjacent conventions. Avoid katakana except for explicitly foreign elements.

**Enforcement**: every kanji-bearing entry - every relic, every sword, every
generated name - MUST pass the kanji ↔ romaji ↔ meaning triangle. When
generating new content, the skill MUST verify each entry against the triangle
before adding it to a pool. When reviewing an existing pool (e.g., after
this constitution was amended), entries that fail are content bugs to be
fixed, not stylistic preferences to be argued.

This principle is NON-NEGOTIABLE because the project's stated aesthetic
(Principle II) is built on Japanese cultural authenticity; a relic catalog
that says one thing in kanji, another in romaji, and a third in English
undermines the whole reading experience for any player who knows Japanese.

### XII. Historical Grounding Bookends (NON-NEGOTIABLE)

Any feature that changes what a **generator asserts about the world** - the
`/diagram` settlement and compound engines above all, but equally any future
generator that draws or states how a place was farmed, built, or lived in -
MUST be bookended by historical-grounding work: an analysis BEFORE it is
built, and a verification of the ARTIFACT after.

**Opening gate (Phase 0, before any design).** For every element the feature
adds or changes, the plan MUST state, in `research.md`:

1. **What the historical reality was** (China-first, Japan corroborating, per
   the `/diagram` doctrine), in enough detail to be checkable - not "terraces
   existed" but what determined their placement, extent, and season.
2. **Whether the proposed design matches it**, explicitly. A design that does
   not match MUST be changed or dropped at this point, not implemented and
   revisited.
3. **What determines the element in reality** - topography, season, tenure,
   economy. This matters because a generator usually gets the *existence* of
   a thing right and its *governing variable* wrong.

**Closing gate (final phase, before "done").** The feature MUST re-examine
the **rendered artifact** - the PNG, not the code and not the intent - and
confirm each element still matches the Phase 0 findings. This is a separate
step from the automated gate: `check_village` proves internal consistency,
never historical truth. A map can pass every check and still depict something
that never existed.

**Why the artifact and not the code (the motivating failure).** The
`land_use_overlay` knob shipped a `rape` value that recolored a random ~32%
of paddy plots yellow. It passed every automated check, was covered by tests,
and carried a grounded-sounding docstring citing the real 油菜 winter
rotation. It was still wrong: rice and rape are the two halves of ONE
rotation in the SAME plot (rice May-Oct; rape sown into the drained stubble
Oct-Nov, flowering Mar-Apr), so they are never both standing - the map
depicted two seasons at once. Nothing in the code could reveal that; only
looking at the picture and asking "what season is this?" could. The same pass
also showed the second failure mode: the overlay scattered plots at random
when the real governing variable was topography - deep-water lotus goes on the
wettest ground, and the 桑基魚塘 dike-ponds were dug out of the low
flood-prone hollows.

**A correction this principle caught on its own first outing (feature 010),
worth keeping as a warning.** The original wording here claimed the dike-pond
system "replaced rice across whole districts rather than dotting among it,"
and a feature was specified to DELETE the overlay on that basis. Phase 0
research refuted it: a scatter of dike-ponds among rice was the system's
NORMAL state (Shunde county was ~4.6% dike-pond in 1581; at Lake Tai mulberry
sat on the *tang* banks with rice remaining the polder's main crop
permanently), and the wall-to-wall landscape is the rare end state. The lesson
is not merely that the claim was wrong - it is that a **confident, plausible,
kanji-citing sentence written into a governing document was wrong**, and only
the opening gate caught it. Grounding claims already recorded here are inputs
to research, never substitutes for it.

**Calibrated liberty where the record is genuinely unclear (GM, 2026-07-19).**
The bookends demand honesty about the evidence, NOT paralysis when the
evidence is thin. Where all three of the following hold:

1. the research shows the thing is **plausibly true**,
2. the **degree** to which it was true is genuinely unclear or
   region-dependent, and
3. a particular reading within that plausible range **serves the project's
   goals** (legibility, visual variation, playability),

then the favorable reading MAY be chosen deliberately. The conditions are
conjunctive and the obligation is disclosure: the choice, its plausible range,
and the fact that we picked from within it for a stated non-historical reason
MUST be written into `research.md` and alongside the rule in the code. What
this clause does NOT license is inventing a range that the research does not
support, or using "the record is unclear" to dodge a finding that is actually
clear - the `rape` rotation was not a matter of degree, and no amount of
project convenience makes rice and rape stand in the same field at once.

**RESEARCH PRECEDES A RULING - the GM is the last resort, not the first
(GM, 2026-08-18).** A question about how a place was actually built, farmed or
lived in is a RESEARCH question, and it is answered by a research pass before
it is ever put to the GM. *"This is a category of question which should ALWAYS
be based on historical research when possible, so I should only be asked for a
ruling on this kind of question when a research pass has already been done and
has turned out to be inconclusive."*

This binds the review loop in particular, because that is where such questions
surface: a reviewer writing "this wants a one-line ruling" is describing a
QUESTION, not delegating it. Run the search first. Only if the record is
genuinely silent or contradictory does the question reach the GM - and when it
does, the ask MUST state what was searched, what was found, and why the finding
does not settle it. An unresearched question presented as a ruling spends the
GM's attention on work the project could have done, and it launders "I did not
look" into "the evidence is unclear".

**TWO SUPPORTABLE ANSWERS BECOME A KNOB, NOT A CHOICE (GM, 2026-08-18).** This
AMENDS the calibrated-liberty clause above, and takes precedence over it where
the two differ. When research shows a thing was genuinely done more than one
way, the project does NOT pick the reading it likes and write the other off.
It makes the variation a **tunable knob with per-settlement variance**, so a
map can be rolled either way and two maps can honestly differ.

The reason is a project goal, not a historical one: these maps exist for
players who must tell one settlement from another at a glance. *"One of our
goals in this map generation project is to be able to produce settlements which
are within historical norms while being as different from one another as is
justifiable by our historical research."* Every place where the record permits
two forms is therefore a place the generator can differ WITHOUT leaving those
norms - which is exactly the variation worth having, and picking one form
throws it away permanently.

So the ladder for any such question is:

1. **Research it.** If the record is decisive, implement what it says - there
   is no knob and no ruling (the `rape` rotation was decisive; so was the
   threshing yard's sun).
2. **If the record supports two or more forms, add the knob**, rolled per
   settlement like every other knob (`_knobs.py`, seeded from the map's own
   seed so a value depends only on (seed, knob name)). Record the range and
   its evidence where the knob lives.
3. **Only if the record is silent or self-contradictory** does the GM rule -
   and the ask carries the research that failed to settle it.

Calibrated liberty survives for the case a knob cannot express: a single
element whose DEGREE is uncertain along a continuum (how large, how dense, how
often) where the project needs one figure to draw. Where the uncertainty is
between DISTINCT FORMS, it is a knob.

**A GUESS IS THE LAST RESORT - THE RESEARCH PASS ALWAYS RUNS FIRST (GM 2026-08-26).**
The rule above ("research precedes a ruling") binds when a question is about
to be put to the GM. This one binds EARLIER and WIDER: whenever a session is
about to make any decision about how a place was built, farmed, planted or
lived in and does not know what the record would show - whether the question
came from the GM, a reviewer, a test, or the session's own uncertainty, and
however small it looks - it runs the search pass FIRST, before choosing and
before writing the decision down. The "guess" label of the three-way
classification below is reserved for a record that was searched and found
silent; an unsearched decision may not wear it. The GM: *"if a question came
up where we had to make this kind of a decision and we didn't know what the
research would show, we should just always do the research. because that is
the kind of project that this is."* Motivating case: the marsh-margin form
(feature 133 T12) was chosen on ecological reasoning and recorded as a guess;
the research pass, run the same day on the GM's instruction, found the reed ->
sedge -> alder/willow hydrosere in the Japanese and Chinese record, confirmed
the form as accurate, and surfaced a second supportable form (an alder-willow
carr) that became a knob candidate - none of which a guess could have given.

**EVERY RENDERING DECISION IS CAPTURED FOR THE READER WHO WILL CLICK ON IT (GM
2026-08-26).** The record-the-why rules (`CLAUDE.md`: the why of every
research-driven rule; the alternatives declined when a limitation is
accepted) have a purpose beyond protecting the next session from redoing the
research, and the purpose decides what must be captured. The GM's long-term
goal, in their words: *"one of my goals is to be able to create HTML versions
of these maps. After all, the maps themselves begin as coordinates, which get
rendered into SVG, which get converted to png image files, but that could
easily also be extended to render an HTML version ... a player might hover
over a brush land and then see it highlighted and then be able to click on it
to learn more about it. This would allow us to do things like explain why is
there a brush land here, what is meant by these glyphs that are being
rendered, and so forth. And then, of course, this would be most useful when
rendering city maps where players might highlight a type of building and then
see every building of that type highlighted and then be able to click on it
to learn more about that type of building ... a tannery or a dojo or a Samurai
country estate ... Why are they placed where they are on the map? What are
some interesting historical facts about them?"* Their examples of what that
reader is told: a tannery stands by water because hides are soaked, so it is
always beside a stream, a drainage ditch or a river on our maps; wells are
drawn larger than true size because a well matters to a premodern settlement
and must be visible; a few samurai country estates stand nearer the city than
the attested distance so that the feature is visible without zooming out, and
so the GM has one to point to when players visit one.

So every decision about how a map is rendered - a glyph, a size, a placement
rule, a distance, a density, a color convention - MUST be recorded in a form
that reader can be shown, and MUST say which of THREE things it is:

1. **Historically accurate** - what the record says, with the finding that
   grounds it (Principle XII's research bookends already require this).
2. **A deliberate deviation** - drawn other than the record says, and WHY:
   legibility (the well), showing a feature type on the sheet (the near
   estate), consistency with Legend of the Five Rings canon, or a priced
   trade-off (`CLAUDE.md`: record the accepted limitation and the
   alternatives declined).
3. **A guess** - the record is silent or gives no firm number, and this is
   what we chose and on what reasoning. Unsourced reasoning is not a fault,
   but an unlabelled guess is: the reader must never be told a guess is a
   finding. (Today's example: "a bog's margin is sedge grading into reed, and
   woody cover stands on the dry ground above it" was the reasoning behind
   letting grass alone grade into the marsh - it is plausible and it is
   unsourced, and `research/vegetation.md` says so.)

Where it lives: the finding and its classification in the skill's `research/`
file for that feature family (the interactive map will read from there); the
operative rule in the `settlements/` or `buildings.md` doc; the pointer at the
point of change in the code. A feature's `spec.md` lists, in its "Decisions
Recorded" section, every rendering decision it made and where each landed -
the spec review (Principle XVI) checks that section against the diff. This
will be built long after the decisions are made; the record is kept now
because a decision unrecorded at the time it is made is unrecoverable later,
and because *"it is very important that all decisions that we make about how
maps are rendered be captured so that we can communicate both what is
historically accurate and what deviates as well as the things that we had to
make guesses about because there simply are not firm numbers about such
things."*

**Enforcement.** `/speckit-plan` MUST record both gates in its Constitution
Check. A feature that cannot state its grounding is not ready to build. The
findings MUST be written where the rule lives (per the "record the why" rule
in CLAUDE.md) - including grounding that led to *rejecting* a design, so a
future pass does not reinvent it.

This principle is NON-NEGOTIABLE because the failure it guards against is
SILENT: historically impossible output looks perfectly fine, passes the gate,
and is only caught if a human happens to ask about it.

### XIII. No Known Regressions (NON-NEGOTIABLE)

GM, 2026-08-17: *"never count our work as being done when there are known
regressions. Nothing should EVER be merged back into main if even one single
new regression was added."*

**The rule, in two halves.** Work is NOT done while a known regression exists,
and **nothing merges into main carrying even one new regression.** Both halves
bind independently: a change may be finished in the sense that its feature
works and still be un-mergeable, and that is the normal case this principle
exists to make visible.

**What counts as a regression.** Anything that worked before the change and
does not work after it - a test or check that passed and now fails, a pool
artifact that was green and now is not, a cohort seed that passed and now
fails, a measured rate that went down. It is defined against a **measured**
baseline, never a remembered one: take the baseline on unmodified code (a
detached worktree, not a stash) before judging your own numbers.

**A WORKTREE BASELINE IS A STARTING POINT, NOT A VERDICT** (added 2026-08-24,
measured during feature 127). A detached worktree is still the right way to take a
baseline - a stash mutates the tree under any review agent reading it - but a fresh
worktree does NOT carry gitignored artifacts. On 2026-08-24 the worktree gate reported
2 failed / 3420 passed; both failures passed in the clone on the same commit, because
the worktree held 20 pool PNGs against the clone's 28 and renders are gitignored. So
**every failure a worktree baseline reports is checked against the clone before it is
called pre-existing.**

This cuts both ways and the quiet direction is the dangerous one. A spurious baseline
failure is loud and gets investigated. But the same gap can make a test pass ONLY in
the worktree, and then a real regression is invisible from the moment the baseline is
taken. Neither reading is available without the second check, and neither error
announces itself.

**Pre-existing failures are NOT regressions** and do not block your merge.
The distinction is exactly "did this pass before my change", which is why the
baseline is mandatory rather than advisory. **But "not a regression" is not
"not your problem":** this clause governs the MERGE BAR only, and
**Principle XIV** governs what you do about a defect you actually found -
fix it in the work at hand, ledger it only when its fix would be an
architectural overhaul. Read the two together; taken alone, this paragraph
has been misread as a licence to ledger anything that predates the diff.

**What does NOT excuse a regression:**

- It is small, or it is one seed out of twenty-four.
- It is on a cohort seed, a fixture, or a map nobody ships. Every one of
  those is a test bed precisely because it stands in for the maps that are
  not written yet.
- It is *documented*. Writing a regression down is how it gets tracked; it
  is not how it gets permitted. A ledger entry is not a waiver.
- The change fixes more than it breaks. Net-positive is an argument for
  doing the work, never for merging it broken.
- **The residue "rotated".** In a seeded cohort a change that alters draw
  counts re-rolls every map, so failures move rather than persist in place.
  That is a real effect and it is NOT a defense: where seed-level comparison
  survives, any check that passed on a seed and now fails is a regression;
  where the re-roll makes per-seed comparison meaningless, the pass RATE must
  not drop AND every newly-failing check must be individually diagnosed.

**FIXING IT IS THE EXIT** (GM 2026-08-23). There are three in principle -
FIX it, REVERT the change, or obtain an explicit GM waiver - but they are
not peers, and treating them as a menu is itself the error:

- **FIX is the default and the expected outcome.** A session that has found
  a path forward TAKES it. "I could fix this, but here are three options,
  which do you prefer?" is not a report, it is a stall.
- **REVERT requires a demonstrated impossibility**, not a preference and not
  fatigue. The bar is an investigation written down: what was measured, what
  was tried, why each attempt failed, and why the remaining approaches are
  exhausted or unreasonable. Reverting because a fix looks like work is not
  an exit, it is an abandonment.
- **WAIVER is the GM's to grant, never the session's to assume.** Asking for
  one is only honest after the fix has been genuinely attempted.

A session that truly cannot fix a regression stops and says so - and "stops
and says so" means the work stays in the clone, unpushed, with the
impossibility investigation attached. But see Principle XV: stopping is
expensive, and the bar for it is high.

**Enforcement.** `/speckit-plan` records this in its Constitution Check. The
stop-work ritual does not run to completion on a red or regressed state: a
session may commit inside its own clone (mid-task work is sacred) but MUST
NOT push to main. Where a domain has a cohort or sweep, its measured
before/after numbers are the evidence, and they belong in the commit message
or the feature's notes.

This principle is NON-NEGOTIABLE because main is the shared integration
point: a regression merged there is silently inherited by every other
session and by every artifact generated afterwards, and the person who pays
for it is never the person who introduced it. The trade "I gained a feature
and lost a check" is legible for about a day and invisible forever after.

### XIV. Fix Defects Where You Find Them (NON-NEGOTIABLE)

GM, 2026-08-17: *"anytime we are working on the diagram skill and you in the
course of implementing a feature come across some new defect - even if it is a
defect that did not have anything to do with what you were working on - I would
like you to fix it as part of that work ... in general, we should fix bugs
before writing new code."*

**The rule.** A defect discovered in the course of a piece of work is FIXED in
that piece of work, whether or not it has anything to do with the feature. Not
filed, not deferred to "its own pass", not handed to a future session - fixed,
in the same change, with the same verification every other fix gets.

**The one exception** is a defect whose fix would be a complete overhaul or a
giant architectural change: a stage reordering, a new subsystem, a rewrite of a
placement engine. Those are deferred - and deferring one is a real deliverable,
not a shrug: it carries the MEASUREMENT that establishes the defect, the
mechanism, and the implementation sketch, so the next session starts from
evidence rather than from a complaint. "This would take a while" is not the
exception; "this cannot be done without changing the architecture" is.

**Why this outranks the convenience of a tidy diff.** The reason is the GM's,
and it is about compounding: the value of this project's generators comes from
being able to expand them - new settlement tiers, new archetypes - on top of a
foundation whose behavior is known-good. Every defect left in place is a
defect the next tier inherits and builds over, and by then it is entangled with
work that assumed it. Fixing on contact keeps the floor level as the building
gets taller. It also removes the incentive that makes ledgers rot: a session
that may fix what it finds writes down only what it genuinely cannot, so the
ledger stays short and every entry in it is real.

**Interaction with Principle XIII.** XIII says a pre-existing failure is not a
regression and does not block your merge; that remains true and is about the
MERGE BAR. XIV is about your OBLIGATION once you have seen the defect. Together:
a pre-existing failure you never touched does not stop you shipping, and one you
found gets fixed rather than ledgered. Where they appear to conflict, XIV
decides what you do and XIII decides what blocks the push.

**Where the defects actually come from, and so where this bites.** Mostly from
the review subagents (`settlement-review`, `building-review`, `backstory-review`,
`frontend-review`), which are pointed at a DELTA and reliably find things
outside it - that is a feature of an independent reviewer, not scope creep by
it. A finding outside the delta is still yours. The same applies to a defect a
diagnostic surfaces, a number that looks wrong while measuring something else,
and a comment that turns out to describe code that no longer exists.

This principle is NON-NEGOTIABLE because the alternative is invisible: a
skipped fix costs nothing today, shows up as "the generator has always been a
bit off here" in a month, and is unattributable by the time it blocks a tier.

### XV. Keep Going (NON-NEGOTIABLE)

**The GM starts work and leaves.** That is how this project is actually used:
a request is kicked off and the computer is unattended for hours. A session
that stops to ask "which of these should I do?" does not cost a few seconds
of the GM's attention - it costs the entire span until they return, and they
come back to find the work exactly where they left it. GM, 2026-08-23:
*"it is bad for me to come back and find that you could have kept going but
decided to just stop and ask what to do next. And if one of the options is
actually, yes, go ahead and fix it and make it work, then that is always the
option that I want."*

**So: when a path forward exists, take it.** Finish the feature. If one
avenue is blocked, work the parts that are not blocked. The standing answer
to "should I keep going?" is yes.

**The ONLY reason to stop and ask** is a genuine belief that the thing
cannot be done - that there is a high probability no approach accomplishes
it. Not that it is hard, not that it is taking longer than expected, not
that there are several ways to proceed and one of them is nicer. If the
options list contains "fix it and make it work", that is the answer and it
does not need confirming.

**Two things this does NOT license:**

- **It is not "any means".** The bounds of ordinary, authorized, ethical work
  are unchanged - this principle is about persistence, never about reaching
  for access, systems or actions that were not granted.
- **It is not thrashing.** Persistence means continuing to make PROGRESS, not
  continuing to make CHANGES. When stuck, the next step is a MEASUREMENT, not
  another speculative edit. A session that changes code on four successive
  hypotheses without measuring between them is not keeping going, it is
  churning - and it will burn the unattended hours producing nothing, which
  is the same failure as stopping. (Feature 126, 2026-08-23, is the recorded
  case of both halves: four wrong diagnoses in a row, and then a stop to ask
  which of three options to take when one of them was "fix it".)

**Interaction with the stop-and-ask calculus.** The older rule - interrupt
only when a wrong guess is expensive to unwind - still holds for AMBIGUITY
about what is wanted. This principle governs DIFFICULTY in delivering what is
already known to be wanted, and there the answer is to keep working.

**Interaction with XIII.** A regression that cannot be pushed does not end
the session's work; it redirects it. Keep fixing, or keep building the parts
that are not blocked, until the regression is fixed or the impossibility is
demonstrated in writing.

**Enforcement.** A standing goal (the `/goal` mechanism) means exactly this:
continue until the objective is met or shown impossible. Reporting progress
is welcome at any point; reporting progress is not the same as stopping.

### XVI. Build What Was Asked; Fidelity Is Not Self-Adjudicated (NON-NEGOTIABLE)

**The default is the literal thing.** When the GM asks for X, build X - not "X
except where Y". Being able to construct a persuasive argument for an exception is
not evidence that the exception is wanted; it is the ordinary result of having
thought about the problem, and such an argument will be available every time.

**An exception is never approved by the session that wants it.** If you believe one
is genuinely necessary, it goes to an independent subagent (Opus 5), whose question
is exactly: *is this a real exception, or is this a session carving out a case
contrary to what it was told?* Hand it the GM's request VERBATIM. If it agrees the
exception is valid, proceed - and raise it with the GM AFTER the implementation
works, not before, because the GM's preferred mode is to start long work and return
to something finished. If it disagrees, build the literal thing.

**Every spec-kit specification is reviewed against the GM's own words before
implementation begins.** The reviewer is an independent subagent and its input is
the GM's REQUEST AS WRITTEN - not the plan, not a paraphrase. A spec checked against
its own plan is being tested for self-consistency, which a wrong spec passes
comfortably. The question is: does this specification implement what was actually
asked, and does it add anything that was not?

**AT MOST three rounds, and stop at the first clean verdict.** A `FAITHFUL` verdict
on round one ends the review - there is no quota to fill and re-reviewing a spec the
reviewer has already passed buys nothing. A `CHANGES REQUIRED` verdict means: revise,
re-review. If the THIRD review still returns changes, STOP and put it to the GM.
Three failures to express a request as a specification is a persistent
misunderstanding, and a fourth attempt by the same session will not locate it.

**A scope-expansion finding is an ordinary finding.** "This spec does more than was
asked" goes through the same revise-and-re-review loop as anything else; it is not a
special case and it does not short-circuit the rounds. It becomes a stop only the way
every other finding does - by surviving three of them (GM 2026-08-24, declining the
tighter rule the implementing session proposed).

**Why this exists** (GM 2026-08-24). Feature 126 was "put the farmhouses down before
the lanes". The specification that came out of it said farmhouses before lanes
EXCEPT the connector and the field spur - a carve-out the GM never asked for,
written by the implementing session on a provenance argument, and placed at FR-003
where only a full reading would find it. The implementation then followed its spec
faithfully. Both of those ways register no-build corridors, so both went on
constraining precisely the placement the feature existed to free: the feature
under-delivered, and no instruction was ever disobeyed. Note also that the
provenance argument was only half-sound - a road to the county town can predate a
hamlet, but the path from a hamlet to its own paddy cannot, and nothing in the
process was positioned to notice.

**This is the QA separation every engineering organization runs on**, and this
constitution already believes it. Principle I holds that the author of a design is
not a reliable reviewer of it, which is why `frontend-review`, `building-review`,
`settlement-review` and `backstory-review` exist. Every one of those guards an
OUTPUT. This extends the same rule one step earlier, to the specification - the one
artifact still being written and graded by the same session.

**Interaction with XV (Keep Going).** This is not licence to stop. The reviews run
inside the work, the session keeps building while it acts on them, and escalation
happens only after the third round. Asking the GM to choose among options remains
the thing XV forbids.

**Interaction with the stop-and-ask calculus.** An exception is not ambiguity. Where
a request is genuinely unclear, the older calculus applies. Where a request is clear
and you want to depart from it, this principle applies, and the answer is to build
what was asked.

### XVIII. A Guard Ships With Its Test, And That Test Runs (NON-NEGOTIABLE)

**Every guard - a hook, a gate check, a refusal of any kind - ships in the same change as a test
companion, and that companion runs in the gate.** GM 2026-08-24.

**Both halves, because each has failed on its own.**

*A guard without a test is not implemented.* This project already knows that from the other
direction: `T034`'s rule is that a guard whose test does not fail when the guard is DELETED is
decoration. A guard with no test at all cannot be checked either way.

*A test nothing runs cannot fail.* The 2026-08-24 enforcement audit found **eight hook scripts, eight
test companions, and nothing that executed any of them.** The convention of writing them was healthy;
the convention of running them did not exist. They had been passing, or not, unobserved.

**What the test must cover - two directions, always:**

- It **FIRES** on the case the guard exists to catch.
- It **STAYS QUIET** on correct work, and this half is the one that protects the project. A guard
  that fires on legitimate work teaches a session that the escape hatch is part of the routine, which
  is precisely the habit these guards exist to break. Feature 127's own guards did this **seven
  times** - on a grep, a commit message, a docstring, a fixture argument, a redirect, a test harness,
  and once on a hook that could not edit its own repair. Every one of those is now a regression case.

**The recurring failure has a name: a MENTION IS NOT AN INVOCATION.** Matching a name anywhere in a
command, a path, or a body will eventually match prose that talks ABOUT the thing. Anchor to a real
command position, require the operator adjacent to its target, walk an AST for calls rather than
grepping source - and put the case that fooled you into the table.

**And the escape is checked FIRST.** A guard whose escape is evaluated after its tests cannot be
repaired through the channel it guards: every command carrying the fix contains the offending text.
That happened, and it cost a session three blocked attempts at its own bugfix.

**Enforcement**: `make hooks-test` runs every `scripts/test-*-hooks.sh` and fails if any guard has no
companion. It is a phase of `make done`, so a guard added without a test turns the gate red.

### XVII. A README Is Written By A Human, For A Human (NON-NEGOTIABLE)

**Never create or edit a README.** GM 2026-08-24: *"you personally should literally never touch a
readme file because a readme file is something that should be written by a human for a human."*

**The mechanical reason, which is the important one.** A README is NOT loaded into a session's
context. A directory `CLAUDE.md` is, automatically, whenever work happens in that directory. So
anything a session must KNOW in order to act correctly is invisible in a README - it will be found
only by a session that happens to look, which is to say by luck.

That is not theoretical. `dev/perf-log/README.md` carried the rule that an append-only shared log
must be a DIRECTORY, because concurrent clones conflict on every push. A session read that file
during an unrelated audit, quoted from it, and hours later created a single-file `run-log.jsonl` -
breaking a rule it had read the same day. Had the file been a `CLAUDE.md`, it would have been in
context at the moment the decision was made.

**Where knowledge goes instead:**

- **`CLAUDE.md` in the directory it governs** - auto-loaded exactly when relevant, which is the
  whole reason this project splits documentation by directory rather than piling it into one file.
- **A topic doc referenced from a CLAUDE.md**, when it is long enough that loading it always would
  be waste. That is the established `docs/` and `dev/` pattern.

**What a README is still for**: a human arriving at the repository, or at a published subproject,
who wants an orientation. The GM writes those. If a README is factually wrong, say so and offer the
correction rather than making it.

**Enforcement**: `scripts/readme-hooks.sh` intercepts a Write or Edit to any `README*`, and any
shell command that writes one. It carries no silent escape - a genuine exception is the GM's to make.

## Technical Standards

**Languages and runtimes**
- Python 3.14 (system Python in the dev container; bumped from 3.13 when
  the standard dev container moved to 3.14, GM-directed 2026-07-20).
- `resvg` renders SVG to PNG (no fallback renderer), with the DejaVu
  faces installed - `container-scripts/setup-dev-env.sh` establishes both.

**Python tooling (per Principle X)**
- **Lint + format**: `ruff` (lint + formatter, single tool). Config lives
  in `.claude/skills/diagram/pyproject.toml`.
- **Type checking**: `mypy --strict` on production modules, configured in
  the same `pyproject.toml`; `l7r/` is a PEP 420 namespace portion and
  never gains an `__init__.py`.
- **Testing**: `pytest` + `pytest-cov` + `pytest-xdist`, always under a
  make target (`make quick`, `make done`, `make done FULL=1`); the
  coverage floors are set by the Makefile, 100% on every measured module
  except the ratcheted `settlement/` package.
- **Dependency management**: source-of-truth in
  `.claude/skills/diagram/requirements.in` / `requirements-dev.in`, compiled
  to the `.txt` lockfiles with `pip-compile`, pinned; a re-lock that bumps
  ruff or mypy is a reviewed change, since it can change what the gate says.
- **Logging**: stdlib `logging` with `logging.getLogger(__name__)`.

**Test layout**
- Tests live under `.claude/skills/diagram/tests/`, mirroring the source
  layout (`tests/CLAUDE.md` indexes them).
- Frozen negative fixtures - manifests of maps that were once wrong - live
  in `pool/regressions/`; saved fixtures for external boundaries live in a
  `fixtures/` subdirectory next to the tests that consume them.
- Test names describe behavior (not implementation); parametrize
  variant inputs. A map-rolling test carries `@pytest.mark.rolls_map`.

**Repository layout conventions**
- The skill stays at `.claude/skills/diagram/` - the same path as before
  the split, so nothing in the engine, the pool generators or the guards
  moved. The engine is `l7r/diagram/`; shipped maps are `pool/<tier>/`;
  staged maps are `wip/`.
- The GM's setting notes are read from gm-assistant, mounted read-only at
  `/gm-assistant`; the canonical `l7r.md` is never edited from here.

**Secrets**
- `development-secrets.ini` files MUST be gitignored. The corresponding
  `.example` template stays in the repo with empty values. No secret
  values may be committed.

## Development Workflow

**Specification → Plan → Tasks → Implement**
This project uses the spec-kit workflow. Significant features SHOULD start
with `/speckit-specify`, refine with `/speckit-clarify` if needed, plan
with `/speckit-plan`, decompose with `/speckit-tasks`, and execute with
`/speckit-implement`. Constitutional principles are enforced at the plan
gate via the *Constitution Check* section of `plan-template.md`.

**Map review workflow (mandatory before a map ships)**
The verification described in Principle VI: a Mode B map goes to
`settlement-review`, a Mode A plan to `building-review` and `size-audit`,
and the findings are acted on before the map enters `pool/`.
`scripts/review-gate.sh` refuses the push otherwise.

**Python "done" checklist (mandatory per Principle X)**
A Python change is not complete until `make done` is green in
`.claude/skills/diagram/` - it runs, together and reporting every failure
at once:

1. `ruff check`
2. `ruff format --check`
3. `mypy --strict` (on production modules)
4. `make hooks-test` (every guard's test companion, Principle XVIII)
5. `pytest -n auto` with the Makefile's coverage floors
   (`make done FULL=1` also re-gates every pool map and runs the
   perf gate)

Nothing in this list is run bare - `scripts/make-only-hooks.sh` refuses
it. The TDD order - write failing test, watch it fail, implement,
watch it pass, refactor - is the working mode for new code.

**Iteration wall-clock is the cost (GM 2026-08-25, feature 133)**
The GM's words, which are the goal every guard, gate, switch and
short-circuit in this repository serves: *"iterations are expensive in
terms of wall clock time. And if me asking for a simple change results in
half an hour of work being done when it should have only taken five
minutes, then that limits the number of changes that I can make in a
single day."* And: *"This is a core motivation behind everything that we
have done in the tooling, and gating that exists for this repository.
Every future session should keep this in mind as a project goal. both for
the commands that we choose to run and for the way in which we look for
opportunities to improve our tooling and for how we interact with that
tooling."* So a session asks, of every command, whether the cheaper one
answers the question; batches changes so one verification covers many;
and when a simple task took long, names which of the GM's three causes
applied - more complicated than expected, lengthier tests than needed, or
more cycles than needed (small change, long test, repeat) - and, when it
is the tooling, proposes the tooling change. A paid or lengthy run that
the tooling was about to start is a finding to record even when a switch
stopped it (feature 133 FR-004).

**Reviews run at acceptance and unlock, in the background (GM 2026-08-26,
feature 133 T12).** Three serial `settlement-review` passes on one task added
~10 minutes and the second passed a map the GM rejected on sight. While the
scope switch is locked the GM looks at every result and IS the reviewer of the
one map on the sheet: no per-task review runs; the independent review runs
once at acceptance and at unlock (the pool re-roll, where the agent earns its
time). Whenever a review runs it runs in the background after the map is
handed back - or beside a LONG gate, never `make quick` - is never waited on,
and lands its findings as follow-ups. Every pass is a row in
`docs/review-ledger.md`, and a miss becomes a rule in the agent, proven to
fire on the unfixed artifact. Doctrine: `.claude/skills/diagram/dev/reviews.md`.

**A test's cost is a cost, and the phase sets the standard (GM 2026-08-26,
feature 133 T19).** The GM: *"our project has gone through a phase in which
for a long time, we had problems with the maps being wrong. And so we really
ratcheted up our standards for what it took to make a map pass. But now that
we have locked in on a way to generate maps in a scripted way which is
generally correct ... having tests that take a long time to run is the bigger
problem, and that is impairing our ability to move forward."* So, in this
phase: a test above the quick suite's cutoff (~0.5 s) must EARN its time. Ask
of each one what is taking the time, and whether the test gives nearly all of
its value cheaper - one seed instead of a sweep, two cardinals instead of
four, a 3-fan comb instead of a 5-fan one, one axis of a matrix instead of the
product, the tier's own maps instead of the whole pool. A sweep that is kept
runs its documented subset by default and its full form under `EXHAUSTIVE=1`
(`tests/_scope.py`); the docstring records the date the exhaustive form last
ran green, so the subset is a recorded decision and the full check can be
re-run whenever there is cause. Evidence, not habit, decides: the GM's
judgment is that seed-dependent passes slipping through is *"not based on any
real evidence in this case"*, and the balance is expected to swing back -
*"we might reach a point ... where we find that maps with problems being
generated is a larger issue than the iteration time"* - at which point the
subsets widen again. Either way it is a documented setting, not a lost
standard.

**Cycle discipline (GM 2026-08-26, feature 133 T10)**
The round trip, not the test, is the cost: a quick run is ~35 s and the
model turn around it is longer. Measured on the first task of the
acceptance period, ~30 of 57 minutes were cycles - four convention misses
found one per run, two records written before they were measured. So a
session MUST (1) re-read the whole diff for convention misses before the
first test run and fix everything a failing run lists before the next
one; (2) use the scaffold where one exists (`make new-check`) rather than
hand-writing a convention; (3) never write a number into a record that
was not measured on the artifact, with the measuring tool where one
exists (`make sun-audit`); and (4) run one verification at the end of a
batch, never one per rule. A spec-kit task that adds a check, a rule or
a record carries these steps in its own text, so the discipline is read
at the moment it applies rather than remembered.

**Delegation**
Subagents are used for parallel generation and large-context work.
Whenever a subagent is delegated a task whose output is shipped to the
user (file edits, generated content), the calling agent MUST verify the
delegated work before reporting success.

**Memory and persistent context**
The agent maintains persistent memory at
`/home/agent/.claude/projects/-diagram/memory/`. Memory entries follow
the format and rules described in the harness system prompt; this
constitution does not duplicate them, but the agent's behavior MUST be
consistent with both the constitution and the memory rules.

## Governance

This constitution supersedes ad-hoc development practices for the L7R
Diagram project. Where this document conflicts with other guidance, this
document wins; where this document is silent, defer to the project's
`CLAUDE.md` and the conventions established there.

**Amendment procedure**
- The GM (project owner) approves all amendments.
- Amendments are made by editing `.specify/memory/constitution.md` and
  re-running `/speckit-constitution` with the change described in natural
  language. The skill produces a new Sync Impact Report and propagates
  changes to dependent templates.
- After amendment, dependent artifacts (plan template, spec template,
  tasks template, runtime guidance docs) MUST be reviewed for
  consistency and updated if needed.

**Versioning policy** (semver applied to governance)
- MAJOR: A principle is removed, redefined with materially incompatible
  meaning, or NON-NEGOTIABLE designation is lifted from a principle that
  had it.
- MINOR: A new principle or section is added, or an existing principle is
  materially expanded.
- PATCH: Clarification, wording, typo fixes, non-semantic refinements.

**Compliance**
- Every plan generated via `/speckit-plan` includes a Constitution Check
  gate that verifies the plan against each principle. Plans that fail
  the check MUST be revised before tasks are generated.
- A green `make done` is the automatic compliance signal for Python;
  a shipped map carries its review record (`review-gate.sh`).
- Generated content is checked against the pool conventions (Principle
  III) and the de-localization rule (Principle VII) before being added to
  a pool.

**Runtime guidance**
`/diagram/CLAUDE.md` and the per-directory CLAUDE.md files (the skill's
`.claude/skills/diagram/CLAUDE.md` above all) remain the day-to-day runtime
guidance. This constitution is the higher-level authority; CLAUDE.md
operationalizes it.

**Version**: 2.8.0 | **Ratified**: 2026-05-27 | **Last Amended**: 2026-08-26
