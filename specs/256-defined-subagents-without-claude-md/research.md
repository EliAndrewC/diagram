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

## R4 - what was proven and what was not (FR-005)

Two agents have a seeded proof: `spec-fidelity-verify` and `record-format`. Three have no recorded run to replay and
carry the field on the reading alone, as the GM agreed: `perf-audit`, `building-review`, `size-audit`. The other
seven DO have recorded runs and were not re-run either, by D1's sizing: `entry-drift`, `escalation-check`,
`quote-check`, `settlement-review`, `source-applicability`, `source-reader`, `spec-fidelity`. Ten of the twelve
therefore rest on R1's reading and on the field behaving for them as it measurably did for the two. The first real
dispatch of each after landing is the next evidence; a check that comes back asking what a rule is, or breaking a
guard it was never told of, is a contract to amend (FR-004's route), not a reason to unset the field.
