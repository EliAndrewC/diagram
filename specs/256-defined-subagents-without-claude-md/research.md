# Research - 256 defined subagents launch without the root `CLAUDE.md` and the memory index

## R1 - the reading (FR-001, T01)

Done 2026-09-20 by an Opus reader over all three `CLAUDE.md` files and all twelve contracts in full, then checked
and applied by the session; one cell was overruled by the session and is marked. Cells: `S` the contract already
states it, `M` the check's job depends on it and the contract did not say it - MOVED into the contract, `-` it does
not bear on that check. Columns: BR building-review, ED entry-drift, EC escalation-check, PA perf-audit, QC
quote-check, RF record-format, SR settlement-review, SA size-audit, AP source-applicability, RD source-reader, SF
spec-fidelity, SV spec-fidelity-verify.

### The root `CLAUDE.md`

| # | rule (section) | BR | ED | EC | PA | QC | RF | SR | SA | AP | RD | SF | SV |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | the repository is the /diagram skill, under `.claude/skills/diagram/` (preamble) | S | S | S | S | S | S | S | S | S | S | S | S |
| R02 | the GM's setting notes live under `/host-l7r-repo` (preamble) | S | - | - | - | - | - | M | - | S | - | - | - |
| R03 | nothing here edits the GM's notes; no git against `/host-l7r-repo` (preamble) | - | - | - | - | - | - | - | - | - | - | - | - |
| R04 | a feature is REPOSITORY + number (preamble) | - | - | - | - | - | - | - | - | - | - | - | - |
| R05 | hyphens only (house style) | M | - | - | - | M | M | S | - | - | M | - | - |
| R06 | American spellings (house style) | S | - | - | - | M | M | S | S | - | M | - | - |
| R07 | both rules stop at a quotation and at the GM's own writing (house style) | - | - | - | - | S | S | - | - | - | S | - | - |
| R08 | "people" is a caste word (house style) | M | - | - | - | - | M | M | - | - | - | - | - |
| R09 | "domain", never "demesne" (house style) | M | - | - | - | - | M | M | - | - | - | - | - |
| R10 | gender-neutral office-holders (house style) | M | - | - | - | - | M | M | - | - | - | - | - |
| R11 | the kanji triangle (house style) | S | - | - | - | - | - | - | - | - | - | - | - |
| R12 | never contradict the GM's notes (house style) | S | - | - | - | - | S | S | - | S | - | - | - |
| R13 | a question about how a place was built is a RESEARCH question (research) | M | - | S | - | - | - | S | S | - | - | - | - |
| R14 | two supportable FORMS is a knob; a degree is calibrated liberty (research) | M | - | M | - | - | - | S | - | - | - | - | - |
| R15 | the four decision classes; an unlabeled guess is the one failure (research) | S | S | - | - | S | S | M | - | - | - | - | - |
| R16 | record the why; price an accepted limitation (research) | - | - | - | S | - | S | - | - | - | - | - | - |
| R17 | a citation is a footnote quoting verbatim from a readable public page (research) | - | - | - | - | S | - | - | - | - | S | - | - |
| R18 | an unreadable source is not cited; the absence note (research) | - | - | - | - | S | - | - | - | - | S | - | - |
| R19 | the GM's campaign notes are canon, not evidence (research) | - | - | - | - | S | - | - | - | S | - | - | - |
| R20 | a source only the GM can fetch goes on the download list (research) | - | - | - | - | - | - | - | - | - | - | - | - |
| R21 | the record is HTML under `research/`, written for a casual reader (research) | - | S | - | - | S | S | S | - | - | - | - | - |
| R22 | footnotes on citations pages; a modal is written from its `Entry:` section (research) | - | S | - | - | S | S | - | - | - | - | - | - |
| R23 | the mechanical script runs FIRST, into the agent's prompt (research) | - | - | - | - | S | S | - | S | - | S | - | - |
| R24-R27 | spec-kit, `make claim`, the task boxes, run the chain unattended (workflow) | - | - | - | - | - | - | - | - | - | - | - | - |
| R28 | do the literal thing; an exception goes to `spec-fidelity` (workflow) | - | - | - | - | - | - | - | - | - | - | S | S |
| R29 | a spec is reviewed before implementation; five rounds; a plan before a tick (workflow) | - | - | - | - | - | - | - | - | - | - | S | S |
| R30 | a worktree or a clone carries no gitignored artifacts (workflow) | M | - | - | M | - | - | S | M | - | - | - | - |
| R31 | fix defects where you find them - for a reviewer, REPORT what is outside the delta (workflow) | - | - | - | - | - | - | M | - | - | - | - | - |
| R32 | reviews at acceptance, in the background, one map per agent, ledgered (workflow) | S | - | - | - | - | - | S | - | - | - | - | - |
| R33 | findings for the GM go through `escalation-check` first (workflow) | - (*) | - | S | - | - | - | S | S | - | - | - | - |
| R34 | every check runs on the tier its file pins (workflow) | S | - | S | - | - | S | S | S | - | S | S | S |
| R35 | everything runs through `make`; a bare interpreter is refused or rewritten (verification) | M | - | - | S | - | - | S | M | - | - | S | S |
| R36 | background the long run; never poll (verification) | - | - | - | M | - | - | M | - | - | - | - | - |
| R37 | ruff, pyrefly, the coverage floor, the file-length bar (verification) | - | - | - | - | - | - | - | - | - | - | - | - |
| R38 | read derived data from the recorded manifest (verification) | - | - | - | - | - | - | S | - | - | - | - | - |
| R39 | batch the lookups; the batching hook blocks single-call recon turns (verification) | M | M | M | M | S | S | S | M | S | S | S | S |
| R40 | work in the clone; `/diagram` is a mirror (clones) | M | M | M | M | M | M | S | M | M | M | M | M |
| R41 | the stop-work procedure and its routes (clones) | - | - | - | - | - | - | - | - | - | - | - | - |
| R42 | `git -C`, one tree per command, no bare `cd` (clones) | M | - | M | M | - | - | S | M | - | - | M | M |
| R43 | a paid prompt may be answered by the session (clones) | - | - | - | - | - | - | - | - | - | - | - | - |
| R44-R47 | the guard doctrine: companions, escapes and their reasons, what is deliberately unenforced (enforced) | - | - | - | - | - | - | - | - | - | - | - | - |
| R48-R50 | key paths, the migration plan, no active-plan pointer | - | - | - | - | - | - | - | - | - | - | - | - |

(*) The reader marked R33 `M` for BR. Overruled by the session: routing a review's findings through
`escalation-check` is what the dispatching SESSION does with the report, not something the reviewer does, and BR's
moved QUESTIONABLE wording already says a question of that tier is a research pass and never "a GM ruling".

The guard table (R45) was put to the seven agents that hold `Bash`: five guards can fire on their work -
`make-only` (R35), `batching` (R39), `main-tree` (R40), `no-poll` (R36) and `git -C` (R42) - and each is moved on its
own row where it bears; the rest cannot fire on anything these twelve do, or explain themselves when they do. R47 is
why R08-R10 are MOVED and not left: nothing mechanical catches the caste sense of "people", office-holder pronouns
or "demesne", so the checks that read every drawn string, and the one that drafts glossary text, are the only net.

### The skill's `CLAUDE.md` - all twelve agents read or run something under that tree

| # | rule | who |
|---|---|---|
| N01 | nothing runs outside make; a packaged module is run through its target | M: BR, SA. S: PA, SR, SF, SV |
| N02 | a performance increase is never silently absorbed; never pass `AS=perf-audit` yourself | S: PA |
| N03 | never let an aggregate stand in for the distributed thing a verdict is about | S: SR |
| N04 | a rule about a map is a test of the PLACER; `check_village` is deleted | M: SR |
| N05 | non-vacuity is asserted - a verification that never ran looks like one that passed | M: EC. S: SR |
| N06 | read geometry from the manifest; batch the crops; a restating diagnostic lies | S: SR |
| N07 | the per-candidate-scan shape; trust the A/B, not cProfile's seconds | S: PA |
| N08 | a finding OUTSIDE the delta is still yours | M: SR (the scope half was S) |
| N09 | build what was asked; an exception goes to an independent subagent | S: SF, SV |
| N10 | never write a number into a record that was not measured on the artifact | S: PA, SR, SA, SF, SV |
| N11 | research before you ask the GM; two forms is a KNOB; liberty is a DEGREE | M: BR, EC. S: SR |
| N12 | a KIND of feature needs a class and an explanation | S: ED |

Every other rule in that file was read and bears on no check's job: the namespace-portion rule, the directory and
`dev/` tables, the command map and its timings, the `quick` budget, the draw-order, footprint and randomness rules,
the legacy-pool freeze, the migration plan and the timing ledger.

### `research/CLAUDE.md` - read under by QC, RF, AP, RD, ED, SR and EC; BR, SA, PA, SF and SV do not work there

| # | rule | who |
|---|---|---|
| Q01-Q03 | who the record is for; the heading is the reader's question; a modal names its entries | S: ED, RF |
| Q04 | the four labels; a CONVENTION is a glyph scaled or colored to read, a DEVIATION is the fiction differing | M: SR. S: ED, QC |
| Q05 | every reference is a link | S: QC, RF, AP |
| Q06 | the footnote form, 「」, the translation marked with the original after | S: QC, RD |
| Q07 | a translation is this project's own English and follows house style | M: QC, RD |
| Q08 | the three footnote forms and what a grounds note may never carry | M: EC (the vocabulary of "silent"). S: QC, RF, RD |
| Q09 | a page the container cannot fetch is not thereby unreadable; the GM's saved copies | M: QC, RD |
| Q10-Q12 | the two checks that hold feature 194; the three reader rules; one glossary | S: QC, RF |
| Q13 | the registry `SOURCES.html` is NOT under the session-note and history rules | M: RF |
| Q14-Q15 | each work explained once in its registry entry; a source judged before it is used | S: RF, AP |
| Q16-Q18 | the record is HTML; one home per topic; when a modal's section moves | S: ED, QC, RF, SR |

Every other rule in that file was read and bears on no check's job (anchor stability, the conversion history, the
settled-absence procedure, the download list's FORMAT, the feature-229 inventory, the declared-silent form).

### What was written, and where

Two sentences serve most of the twelve. The CLONE sentence (R40, with R42 for the agents that hold `Bash`) went
into eleven contracts beside the batching line; `settlement-review` already said it in its first stage, and its
`Inputs` paragraph, which contradicted that with the mirror's path, was corrected. The BATCHING line of feature 255
went into the five contracts that lacked it (BR, ED, EC, PA, SA) - 255 had left three of those out of ITS scope;
here it is a rule each was relying on the root file for. The rest, per agent: BR - the house-style bullet (R05,
R08-R10), `make pack-audit` for the bare module (R35/N01), the gitignored-render note (R30), and a QUESTIONABLE tier
reworded from "a GM ruling" to a research pass and a knob (R13, R14, N11); SA - `make pack-audit`, the render note;
SR - the deleted `check_village` battery replaced by where the rules are tested now (N04), the convention label
(R15, Q04), where the GM's notes are (R02), report what is outside the delta (R31, N08), no sleep-loop on a running
gate (R36), the caste / domain / pronoun line (R08-R10); PA - both legs timed in worktrees, no sleep loop (R30, R36);
EC - a fork between two supported forms is a knob and not the GM's (R14, N11), an empty grep is not a missing norm
(N05), the vocabulary of "silent" (Q08); QC and RD - a translation follows house style (R05, R06, Q07), a refused
host is not an unreadable page and the GM's saved copies (Q09); RF - the registry exemption (Q13), house style for
what it drafts (R05, R06, R08-R10). ED, AP, SF and SV needed only the shared sentences.

### Stale things the reading found in the contracts

Fixed here, because each sat in a passage the moved rules touched (constitution XIV): the deleted `check_village`
battery named as the live gate (SR); pool paths one folder short of feature 161's layout (BR, SA, SR); `tools/
pack_audit.py`, a file that is now a package behind `make pack-audit` (BR, SA); "all paths are under `/diagram/`",
the mirror (BR, SA, SR); a negative fixture under `pool/regressions/`, a directory that no longer exists (BR); BR's
QUESTIONABLE tier offering "a GM ruling"; EC protecting a two-forms fork as the GM's; and, in the skill's
`CLAUDE.md`, "Three rounds, then escalate" where the GM made it five on 2026-08-30. Left, and listed so they are not
lost: `settlement-review` tells the agent to import `l7r.diagram.tools.scatter_audit.parse_bases`, which no make
target wraps any longer; three descriptions end with a literal `(Tools: ...)` that duplicates the frontmatter; and
several contracts cite `tests/test_agent_models.py` by a path that is right only from the skill directory.

## R2 - the proof (FR-003, T03): the field stands on all three cases

Method (observed 2026-09-20; method: `measure/dispatch_seeded.sh` - a headless Sonnet session in the case's worktree
dispatches the agent ONCE with the recorded prompt, so the agent runs as a SUBAGENT, where the field acts; turns,
first-turn input and weight are the subagent's own, from its transcript, usage folded per message id at R1's rates
of feature 251). Both legs of a pair run the SAME contract, moved rules included; the only difference is the
`omitClaudeMd: true` line. The cases are feature 255's R3 rounds and R2 section. A worktree is its own project, so
neither leg loads the memory index: this is the proof of the `CLAUDE.md` files leaving (the index is R3's).

| case | agent | recorded findings | control (no field): result, turns, first turn, weight | with the field: result, turns, first turn, weight |
|---|---|---|---|---|
| feature 250 round 2 | `spec-fidelity-verify` | CHANGES REQUIRED: FR-004's unrequested scope; its added half has no success criterion | both items; 4 turns; 56,017; 0.70 | both items; 4 turns; 11,536; 0.39 |
| feature 250 round 2, after the fix | `spec-fidelity-verify` | FAITHFUL | FAITHFUL; 3 turns; 54,783; 0.55 | FAITHFUL; 6 turns; 10,301; 0.40 |
| homesteads, "The garden's sun, and how far the windbreak shades" | `record-format` | two stray `</strong>`, a sentence contradicting its clause, the fetch-verdict phrase "the pages read record", `the frame`, `clump` | five of six - `the frame` MISSED; 8 turns; 63,134; 1.22 | all six; 7 turns; 7,552; 1.03 |
| total | | | 15 turns; 2.47 | 17 turns; 1.82 |

**Every run with the field caught everything its control caught** (and on the third case one recorded finding the
control missed), so FR-004's second pair was never needed. The weight is about a quarter lower with the field and
the first turn is a fifth to an eighth of what it was - far more than the root file's 5 k, because in a real check
the nested `CLAUDE.md` files were arriving too. One run was DISCARDED unscored and re-run, as the plan requires: the
first `tw-250` leg with the field, whose Sonnet dispatcher dropped 57 characters of the recorded prompt (its result
is kept beside the case as `discarded/`; it too returned both items). Assumption checked: the harness honors the
field in a project agent FILE, not only in an inline agent - the first-turn column is the evidence.

## R3 - a real defined agent's first turn, from where the index loads (FR-006, T04)

(observed 2026-09-20; method: `measure/first_turn.sh .claude/agents/entry-drift.md /diagram` - the agent defined
inline from its own frontmatter and contract body at its pinned model, dispatched once from `/diagram` by a Haiku
session on a one-line prompt; nothing written under the mirror.)

| leg | `entry-drift`'s first-turn input |
|---|---|
| as it was | 20,435 tokens |
| with `omitClaudeMd: true` | 4,477 tokens |

About 16 k tokens leave every turn of the smallest check: the root `CLAUDE.md` and the memory index together.

## R4 - what was proven and what was not, AT THE FIRST LANDING (FR-005; superseded by R6's tally - FR-011)

Two agents have a seeded proof: `spec-fidelity-verify` and `record-format`. Three have no recorded run to replay and
carry the field on the reading alone, as the GM agreed: `perf-audit`, `building-review`, `size-audit`. The other
seven DO have recorded runs and were not re-run either, by D1's sizing: `entry-drift`, `escalation-check`,
`quote-check`, `settlement-review`, `source-applicability`, `source-reader`, `spec-fidelity`. Ten of the twelve
therefore rest on R1's reading and on the field behaving for them as it measurably did for the two. The first real
dispatch of each after landing is the next evidence; a check that comes back asking what a rule is, or breaking a
guard it was never told of, is a contract to amend (FR-004's route), not a reason to unset the field.

## R5 - Amendment 1: the guard, the leftovers (FR-007, FR-009)

`test_every_agent_launches_without_the_claude_md_files` in `tests/test_agent_models.py`: 8 passed with the field in
all twelve; with the field removed from `entry-drift.md` the test FAILED naming `['entry-drift']`; restored, 8 passed
(observed 2026-09-20; method: `make test-file FILE=tests/test_agent_models.py`, three times). `make scatter-bases
MAP=<pool map> [BOX=...]` wraps the engine's `parse_bases` through `scripts/_scatter_bases.py` (the engine module has
no command-line entry and none was added, so the delta stays DIRECT; four tests in `tests/tooling/`) and
`settlement-review` names it; the three `(Tools: ...)` description tails are cut; seven contracts cite the tier table
by its real path.

## R6 - Amendment 1: eight more seeded pairs (FR-010), scored by an independent reader

Method as R2 (observed 2026-09-20; method: `measure/dispatch_seeded.sh`; each leg's reply read IN FULL and scored
finding by finding, in both directions, by an Opus agent that did not write the change - the session is not a
reliable scorer of its own feature; where two legs contradicted each other on a fact, the scorer checked the source).
"Missed" counts control findings the with-field leg did not make; "only on" counts the reverse.

| case | agent | control findings | hit with the field | missed with the field | found ONLY with the field | planted / recorded finding (on / off) | turns on / off | weight on / off |
|---|---|---|---|---|---|---|---|---|
| farmhouse modal | `entry-drift` | 3 | 1 (+1 weaker) | **the DRIFTED verdict itself - IN-STEP returned, on two independent samples** | 0 | recorded DRIFTED: no / yes | 4 / 4 | 0.55 / 0.90 |
| feature 242's draft | `escalation-check` | 8 | 5 (+1 classified as the recorded run did) | 2 (the headline counts; the requested rewrite) | 2 | recorded's six verdicts: 6 of 6 / 5 of 6 | 6 / 4 | 0.36 / 0.59 |
| capitals fn-235..240 | `quote-check` | 12, one a false positive | 9 (+1 weaker) | 1 sub-finding | 4, and it correctly rejected the control's false positive | - | 11 / 4 | 1.17 / 1.00 |
| dike-pond claims | `source-reader` | 15 | 11 | 4 sub-quotes; all five claim verdicts agree | 8 | both partial passages: yes / yes | 10 / 6 | 0.70 / 0.91 |
| feature 251's spec, round 1 | `spec-fidelity` | 3 required changes | 1 | **2, both examined and ruled "faithful"** | 0 | recorded's three: 1 of 3 / 3 of 3 | 3 / 5 | 0.62 / 0.71 |
| Shanghai county wall | `source-applicability` | 10 true, 2 false positives | 7 | 2 (the two moat lengths; one era limit) | 3 (1 true, 2 false positives) | recorded's two limits: one each | 18 / 5 | 2.01 / 1.05 |
| Ochiba sheet, scale bar removed | `building-review` | 12 | 7 (+2 partial) | 4, one a verified fire-gap defect between two buildings | 9 | planted defect: yes / yes | 9 / 6 | 1.76 / 1.99 |
| Ochiba sheet, one bath enlarged | `size-audit` | 12 | 7 (+3 weaker) | 2 | 4, one substantive | planted defect: yes / yes | 5 / 6 | 1.53 / 1.69 |

**By FR-003's rule as written - "misses nothing its control caught" - the field fails all eight**, and so would any
second run of the same agent on the same input: in six of the eight BOTH legs caught things the other did not, in
comparable number, which is the run-to-run variance feature 255 measured (R1's two candidate runs, R6's two
reviews). Both planted defects were caught by both legs. Two results are NOT variance: **`entry-drift` and
`spec-fidelity` lost one-sidedly** - nothing found only with the field, the control and the recorded run agreeing
against it, and in both the with-field run SAW the item and ruled the other way. The scorer also named where the
with-field legs' losses cluster elsewhere: re-verifying a documented tolerance or overrule rather than accepting it
(the bath's fire tub, the glyph-exemption list, the cell's contradictory record). Two legs cost MORE with the field
(`quote-check`, and `source-applicability` at 18 turns against 5, paging `SOURCES.html` for a block the control found
at once). One leg (`size-audit` with the field) was re-run for a dispatcher that did not pass the prompt verbatim.

**FR-004's route, taken for the two one-sided losses** - the miss read against what the field removes, and a GENERAL
rule written into the contract where something accounts for it, then the with-field leg run once more:

| agent | what the removed files carried that the contract did not | the rule moved | the re-run (with the field) |
|---|---|---|---|
| `entry-drift` | the root file's research doctrine - a reader is never told a thing is attested when it is not; the four classes; an unlabeled guess is the one failure - which is what makes a newly disclosed LIMIT on a source a finding and not maintenance | the `Note:` is the modal's accounting of read / guess / extension, and a change to the standing of anything it counts is a moved finding even when `What:` and `Why:` are untouched | **DRIFTED, the recorded finding, in the recorded place**; 4 turns, 0.52 |
| `spec-fidelity` | the root and skill files' measure-never-assume rule, and the habit of following a rule literally to see whether it does what it claims | question 6: does each requirement DO what it says it is for - a rollback that does not roll back, a scope decided by an unmeasured premise | the unmeasured-premise item now RAISED; the step-back item still passed; and the unrequested-guard item, which the first with-field run had raised, NOT raised this time. One of the recorded three, a different one; 6 turns, 0.95 |

So `entry-drift` is repaired and `spec-fidelity` is not settled: three with-field runs (counting R7's) raised one,
one and two of their recorded items, never the same set, against a control that raised all three once. Nothing here
can say whether that is the field or the agent's own variance at N=1 per leg. Per FR-004 the field stays set and the
case goes to the GM.

**The tally (FR-011).** With a seeded pair of their own: `spec-fidelity-verify`, `record-format` (R2), and the eight
above - ten of twelve. Without: `settlement-review` and `perf-audit`, put to the GM with their reasons and prices:
`settlement-review` - one pair is about 9 weight units by feature 255's R6 (5.37 and 3.94 for its two runs), the
eight pairs above cost 17.5 together (the sum of their sixteen weights), and R6 shows two careful passes over one map finding different real defects,
so a single pair cannot separate a miss from variance; three samples a leg would be about 27 units. `perf-audit` -
no recorded run and no frozen artifact; a pair needs a manufactured performance increase between two commits with
its recorded explanation, roughly a day's session work before the first run, the runs themselves about 2 units each.

## R7 - Amendment 1: the fidelity reviewer and the enforcement of what was asked (FR-008)

The cause was in the contract: question 4 of `spec-fidelity.md` listed "extra verification the GM did not request"
as scope inflation, so round 1 cutting this feature's guard was the contract working as written. Both contracts now
carry the GM's distinction. Proof (observed 2026-09-20; method: `dispatch_seeded.sh` on round 1's own recorded
prompt, tree at the spec's first commit), scored by the same independent reader against round 1's four items:

| round 1's item | amended contract | control: the UNAMENDED contract, same setting |
|---|---|---|
| 1 the failure branch leaves the field unset | raised | raised |
| 2 "nothing is moved from the memory index" too broad | NOT raised (cleared as within) | raised |
| 3 the guard cut as unrequested | **kept, citing the new rule** | **also kept** - "it mechanizes the GM's ruling" |
| 4 SC-004 mislabels what went unproven | not raised | not raised |
| new | FR-004 does not say which contract the proof's legs run | - |

A first amended run was discarded as evidence: its contract paragraph NAMED this feature's guard as the worked
example, so it had been shown its own answer; the example was made general before the run above. **SC-007 as written
is NOT met**: the amended run kept the guard, but so did the control - the original cut does not reproduce, so this
proof cannot show the amendment CAUSES the keep - and neither run raised all of the other three items. What the
contract change does do is state the GM's rule where the reviewer reads it; what it risks is R6's last row, where a
with-field `spec-fidelity` run passed a guard the recorded review had called unrequested ("within, as enforcement").
That guard REFUSES and rewrites dispatches the request never touched, which is the "new behavior riding in as a
check" the paragraph excludes - so the wording may need to be sharper. T08 stays open on this.
