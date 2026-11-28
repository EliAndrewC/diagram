# Feature report - 451-time-retro-and-efficiency

Written by `make feature-report F=451` from 136990 events (2026-11-20T04:33 to 2026-11-27T22:34 UTC), 529 commits, the run log and the spec.

<!-- report split into report/ (462 T555): what is where is below -->

Load this file when: you need feature 451's report - where its time went, its rounds, tripwires and costs - or you are about to open or grep a file under its `report/`. Its small sections are below; each large one names its parts, so open the one part you need (a task's rows stand in the part whose range holds it).

WHY: a report's tables ran to megabytes (451's report.md 1,496,878 bytes); a session that read or grepped it whole spent its context on it (the GM 2026-11-27, 462 T555). Each section past 16384 bytes is cut at its table's rows into parts of at most 65536 bytes, each repeating its heading and its table's header. Do not `cat report/*` or grep the directory broadly: grep with `-l` or `-c` first, then read the one part it names.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 74 h 06 min | 51% |
| idle (over an hour) | 43 h 21 min | - |
| waiting: a background run | 32 h 50 min | 22% |
| waiting: general-purpose | 17 h 24 min | 12% |
| waiting: the GM | 9 h 04 min | 6% |
| other tool | 4 h 09 min | 3% |
| waiting: spec-fidelity | 3 h 24 min | 2% |
| spec-kit step | 1 h 03 min | 1% |
| review | 1 h 02 min | 1% |
| waiting: subagent | 57 min | 1% |
| tests | 31 min | 0% |
| waiting: round-arbiter | 21 min | 0% |
| docs | 19 min | 0% |
| waiting: quote-check | 14 min | 0% |
| waiting: record-format | 10 min | 0% |
| waiting: escalation-check | 10 min | 0% |
| waiting: source-applicability | 7 min | 0% |
| waiting: spec-fidelity-verify | 6 min | 0% |
| waiting: modal-research | 5 min | 0% |
| writing the spec | 4 min | 0% |
| land | 4 min | 0% |
| waiting: impl-drift | 4 min | 0% |
| waiting: source-reader | 3 min | 0% |
| waiting: translation-check | 2 min | 0% |
| dispatching: claims check | 2 min | 0% |
| dispatching: record check | 2 min | 0% |
| edit | 2 min | 0% |
| waiting: modal-triage | 2 min | 0% |
| waiting: modal-depiction | 1 min | 0% |
| waiting: building-review | 1 min | 0% |
| dispatching: other subagent | 1 min | 0% |
| waiting: research-pass | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| waiting: modal-form | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| gate | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| waiting: message-check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: glyph-check | 0 min | 0% |

The session's own time above; its 59567 subagent tool call(s) (of 64522) are counted apart (0 by the subagent transcripts, 59567 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 2631 run(s), 238 h 15 min in all, much of it while the session waited or worked on.

## The critical path and what was spent beside it (`make where-time`'s columns, feature 451 T11)

In 2 part(s), 130450 bytes, cut at its rows (462 T555):

- `report/02-the-critical-path-and-what-was-spent-1.md` (65435 bytes, rows - to T01)
- `report/02-the-critical-path-and-what-was-spent-2.md` (65303 bytes, rows T02 to all)

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 51 min |
| make builder-checks | 40 min |
| make apply-edits | 27 min |
| make carry | 25 min |
| make builder-done | 12 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 602 | BLOCKED 124, CHANGES REQUIRED 1, CLEAR 459, FAITHFUL 1, NOT-REVIEWABLE 6, findings 1 |
| general-purpose | 572 | BLOCKED 37, CLEAR 204, FAIL 3, PASS 11, clean 24, findings 464 |
| message-check | 81 | BLOCKED 1, FAIL 9, PASS 74 |
| impl-drift | 54 | findings 61 |
| round-arbiter | 48 | CLEAR 13, FAIL 1, FAITHFUL 1, clean 1, findings 29 |
| record-format | 43 | clean 1, findings 36 |
| modal-research | 36 | clean 7, findings 27 |
| quote-check | 35 | clean 4, findings 27 |
| escalation-check | 32 | CLEAR 1, findings 29 |
| modal-form | 30 | clean 7, findings 22 |
| source-reader | 27 | clean 2, findings 24 |
| modal-depiction | 25 | clean 10, findings 16 |
| building-review | 20 | NEEDS-WORK 3, NOT-REVIEWABLE 3, PASS 4 |
| source-applicability | 14 | findings 14 |
| glyph-check | 13 | PASS 9 |
| modal-triage | 13 | findings 13 |
| size-audit | 12 | NEEDS-WORK 3, NOT-REVIEWABLE 2, PASS 3 |
| claims-triage | 9 | findings 6 |
| translation-check | 9 | FAITHFUL 9 |
| claude-code-guide | 4 | findings 1 |
| research-pass | 4 | findings 3 |
| Explore | 2 | findings 2 |
| fork | 2 | findings 3 |
| Plan | 1 | findings 1 |
| claude | 1 | findings 1 |
| intro-check | 1 | findings 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 2, FAITHFUL 2 |

## Rounds per checked thing (two or more)

Counted inside the window: a subject's rounds before SINCE are not, so its rounds past the first are those within the window, and where SINCE falls between its rounds this table reads fewer than the plan re-rounds above, which count a later round whose first fell before SINCE (feature 451 T11).

| check | subject | rounds |
|---|---|---|
| message-check | guard-messages | 46 |
| impl-drift | claims-owed | 12 |
| modal-research | modal-batch | 11 |
| modal-form | modal-batch | 10 |
| claims-triage | claims-triage | 8 |
| modal-depiction | modal-batch | 8 |
| modal-triage | modal-triage-diagram-backlog | 7 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T243 | 7 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T285 | 6 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T87 | 5 |
| quote-check | q-0138 | 4 |
| record-format | q-0018 | 4 |
| record-format | q-0019 | 4 |
| record-format | q-0138 | 4 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T110 | 4 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T184 | 4 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T198 | 4 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T315 | 4 |
| general-purpose | guard-messages | 3 |
| impl-drift | claims--magistrate-s-manor-county-magistracy-garrison-emphasis-knob | 3 |
| impl-drift | claims-rust-mode-a-src-reads-rs-take-the-page-s-reads | 3 |
| message-check | msg | 3 |
| modal-form | modal-sheet-granary | 3 |
| quote-check | q-0018 | 3 |
| quote-check | q-0019 | 3 |
| source-applicability | key-chiu-2015-yuehu | 3 |
| source-reader | key-l7r-lineages-whole | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T03 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T113 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T141 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T153 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T158 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T160 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T170 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T186 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T188 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T192 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T193 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T235 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T250 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T251 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T253 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T259 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T265 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T292 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T307 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T308 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T313 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T44 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T46 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T47 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T83 | 3 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T89 | 3 |
| impl-drift | claims-docs-buildings-md-sacred-features-arch-dimensions | 2 |
| impl-drift | claims-f1-r3 | 2 |
| impl-drift | claims-ogram-rules-rs-hierarchy-the-storehouses-under-the-residence | 2 |
| impl-drift | p1-claims-field-polder-rs | 2 |
| modal-depiction | depiction-hamlet-buckwheat | 2 |
| modal-depiction | depiction-hamlet-farm-holding | 2 |
| modal-depiction | depiction-hamlet-soy | 2 |
| modal-depiction | fb-md5 | 2 |
| modal-depiction | t317-md2 | 2 |
| modal-form | form-hamlet-marsh | 2 |
| modal-form | form-sheet-barracks | 2 |
| modal-form | modal-sheet-barracks | 2 |
| modal-form | modal-sheet-office-hall | 2 |
| modal-research | gq-research | 2 |
| modal-research | modal-choice-winter_crop--none | 2 |
| modal-research | modal-sheet-granary | 2 |
| modal-research | research-hamlet-marsh | 2 |
| modal-triage | mt | 2 |
| modal-triage | mt2 | 2 |
| quote-check | q-0001 | 2 |
| quote-check | q-0098 | 2 |
| quote-check | q-0140 | 2 |
| quote-check | q-0156 | 2 |
| quote-check | q-0173 | 2 |
| record-format | q-0001 | 2 |
| record-format | q-0098 | 2 |
| record-format | q-0140 | 2 |
| record-format | q-0156 | 2 |
| record-format | q-0173 | 2 |
| record-format | q-0193 | 2 |
| record-format | q-0238 | 2 |
| round-arbiter | arbiter-batch | 2 |
| round-arbiter | arbiter-s-diagram-backlog-rust-guard-src-guards-context-cap-hooks-rs | 2 |
| source-applicability | key-danzaemon-jawiki | 2 |
| source-applicability | key-xie-2021-duomin-ningbo | 2 |
| source-applicability | key-xie-2021-duomin-shaoxing | 2 |
| source-reader | key-chen-2021-foshan-jitang-whole | 2 |
| source-reader | key-chiu-2015-yuehu-whole | 2 |
| source-reader | key-fei-1939-whole | 2 |
| source-reader | key-ihns-bunongshu-whole | 2 |
| source-reader | key-king-forty-centuries-whole | 2 |
| source-reader | key-l7r-budgets-whole | 2 |
| source-reader | key-minle-dou-people-whole | 2 |
| source-reader | key-wuhurec-wanchun-whole | 2 |
| spec-fidelity | plan-449-rust-codebase-T233 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T05 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T06 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T09 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T102 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T104 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T105 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T108 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T11 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T112 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T115 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T118 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T12 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T123 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T13 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T14 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T15 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T151 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T159 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T16 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T167 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T169 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T171 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T174 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T175 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T177 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T179 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T182 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T183 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T185 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T187 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T195 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T196 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T197 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T20 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T202 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T207 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T21 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T213 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T215 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T217 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T219 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T220 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T228 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T229 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T230 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T232 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T233 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T236 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T237 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T240 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T245 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T248 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T25 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T254 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T257 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T263 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T268 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T272 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T274 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T289 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T298 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T299 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T300 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T309 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T31 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T310-de6c9d0b | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T32 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T324 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T325 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T33 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T359 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T36 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T364 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T391 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T43 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T443-33952447 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T446-de6c9d0b | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T45 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T505-de6c9d0b | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T506-de6c9d0b | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T51 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T55 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T57 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T67 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T71 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T74 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T77 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T79 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T80 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T81 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T88 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T91 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T94 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T98 | 2 |
| spec-fidelity | plan-451-time-retro-and-efficiency-T99 | 2 |
| translation-check | q-0018 | 2 |
| translation-check | q-0019 | 2 |
| translation-check | q-0156 | 2 |

## Process signals

- gates: green 33, red 8
- spec rounds: none recorded
- plan reviews BLOCKED: 279 recorded in commits, 124 returned
- reversals (A -> B -> A): 55 - fields.rs 10:23; fields.rs 10:23; fields.rs 10:23; set_down_hooks.rs 13:20; no_poll_hooks.rs 13:28; no_poll_hooks.rs 13:53; no_poll_hooks.rs 13:54; no_poll_hooks.rs 14:06
- check dispatches 319 over 215747 changed lines: cascade ratio 0.00
- tasks ticked: 536 of 537

## Tripwires (FR-010) - what fired, or would have

- 10:23 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/event_log_hooks/fields.rs
- 10:23 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/event_log_hooks/fields.rs
- 10:23 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/event_log_hooks/fields.rs
- 13:20 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/set_down_hooks.rs
- 13:28 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/no_poll_hooks.rs
- 13:53 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/no_poll_hooks.rs
- 13:54 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/no_poll_hooks.rs
- 14:06 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/no_poll_hooks.rs
- 14:35 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/static_runs_hooks.rs
- 14:39 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/event_log_hooks/fields.rs
- 14:40 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/static_runs_hooks.rs
- 14:40 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/static_runs_hooks.rs
- 15:34 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/context_cap_hooks.rs
- 16:12 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/context_cap_hooks.rs
- 16:14 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/context_cap_hooks.rs
- 23:45 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/house_style_hooks.rs
- 00:02 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/house_style_hooks.rs
- 06:06 reversal:/diagram/.clones/diagram-backlog/specs/451-time-retro-and-efficiency/plan.md
- 09:59 reversal:/diagram/.clones/diagram-backlog/rust/gate/crates/record/src/record/stale_terms.rs
- 16:04 reversal:/diagram/.clones/diagram-backlog/rust/guard/shared/src/tree/bind.rs
- 17:03 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/static_runs_hooks.rs
- 19:07 reversal:/diagram/.clones/diagram-backlog/rust/guard/shared/src/tree/bind.rs
- 19:07 reversal:/diagram/.clones/diagram-backlog/rust/guard/shared/src/tree/bind.rs
- 19:15 reversal:/diagram/.clones/diagram-backlog/rust/guard/shared/src/speckit.rs
- 21:24 round:modal-depiction|modal-batch@3
- 21:41 round:modal-research|modal-batch@3
- 21:52 round:modal-form|modal-batch@3
- 21:54 round:modal-research|modal-batch@4
- 21:54 round:modal-form|modal-batch@4
- 21:54 round:modal-depiction|modal-batch@4
- 22:04 round:building-review|building-review--county-magistracy-example@3
- 22:07 round:modal-form|modal-batch@5
- 22:07 round:modal-research|modal-batch@5
- 22:07 round:modal-depiction|modal-batch@5
- 01:24 round:building-review|building-review--county-magistracy-example@4
- 12:19 reversal:/diagram/.clones/diagram-backlog/specs/451-time-retro-and-efficiency/plan.md
- 20:14 round:modal-form|modal-batch@6
- 20:19 round:modal-research|modal-batch@6
- 22:18 round:modal-research|modal-batch@7
- 18:50 round:impl-drift|claims-owed@3
- 20:37 round:modal-research|modal-batch@8
- 20:44 round:modal-form|modal-batch@7
- 20:44 round:modal-depiction|modal-batch@6
- 01:57 round:quote-check|q-0018@3
- 01:57 round:quote-check|q-0019@3
- 01:57 round:record-format|q-0018@3
- 01:57 round:record-format|q-0019@3
- 02:06 round:record-format|q-0018@4
- 02:06 round:record-format|q-0019@4
- 06:53 round:impl-drift|claims-owed@4
- 12:45 reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/review_round_hooks.rs
- 14:00 round:modal-form|modal-batch@8
- 14:02 round:modal-research|modal-batch@9
- 17:02 reversal:/diagram/.clones/diagram-backlog-t228/rust/guard/shared/src/checks/reply.rs
- 17:02 reversal:/diagram/.clones/diagram-backlog-t228/rust/guard/shared/src/checks/reply.rs
- 18:49 reversal:/diagram/.clones/diagram-backlog-t245/rust/guard/src/guards/scratch_sweep_hooks/sweep.rs
- 18:50 reversal:/diagram/.clones/diagram-backlog-t245/rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs
- 20:19 reversal:/diagram/.clones/diagram-backlog-t227/rust/guard/shared/src/checks/rounds.rs
- 20:20 reversal:/diagram/.clones/diagram-backlog-t227/rust/guard/shared/src/checks/handle.rs
- 20:23 reversal:/diagram/.clones/diagram-backlog-t227/rust/guard/shared/src/checks/rounds.rs
- 23:00 reversal:/diagram/.clones/diagram-backlog-t248/rust/guard/shared/src/checks/rounds.rs
- 23:00 reversal:/diagram/.clones/diagram-backlog-t248/rust/guard/shared/src/checks/rounds.rs
- 04:28 reversal:/diagram/.clones/diagram-backlog-t250/research/questions/0014-bunds-between-the-paddies-aze.drawing.html
- 05:07 round:impl-drift|claims-owed@5
- 05:45 round:quote-check|q-0138@3
- 05:45 round:record-format|q-0138@3
- 07:00 round:source-applicability|key-chiu-2015-yuehu@3
- 07:55 round:impl-drift|claims-owed@6
- 08:34 round:impl-drift|claims-owed@7
- 18:57 round:impl-drift|claims-owed@8
- 20:11 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/src/suite_tools/messages.rs
- 21:32 reversal:/diagram/.clones/diagram-backlog-t271/rust/guard/src/guards/builder_brief_hooks.rs
- 21:49 reversal:/diagram/.clones/diagram-backlog-t271/rust/guard/src/guards/builder_brief_hooks.rs
- 21:49 reversal:/diagram/.clones/diagram-backlog-t271/rust/guard/src/guards/builder_brief_hooks.rs
- 01:57 reversal:/diagram/.clones/diagram-backlog-t269/rust/guard/src/guards/pool_idle_hooks.rs
- 03:19 reversal:/diagram/.clones/diagram-backlog-t269/rust/guard/src/guards/pool_idle_hooks.rs
- 03:19 reversal:/diagram/.clones/diagram-backlog-t269/rust/guard/shared/src/builder_queue.rs
- 04:42 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/src/guards/context_cap_hooks/band.rs
- 04:42 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/tree.rs
- 04:45 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/tree.rs
- 06:41 reversal:/diagram/.clones/diagram-backlog-t269/rust/gate/crates/land/src/land.rs
- 07:18 reversal:/diagram/.clones/diagram-backlog-b1/rust/gate/crates/rustc/src/rustc/kept.rs
- 07:31 reversal:/diagram/.clones/diagram-backlog-b1/rust/gate/crates/rustc/src/rustc/tests/prewarm.rs
- 08:10 reversal:/diagram/.clones/diagram-backlog-t271/rust/guard/shared/src/guards/event_log_hooks/reversal/index.rs
- 13:36 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/checks/handle/part.rs
- 13:37 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/checks/handle/part.rs
- 13:37 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/checks/handle/part.rs
- 13:37 reversal:/diagram/.clones/diagram-backlog-t270/rust/guard/shared/src/checks/handle/part.rs
- 20:16 reversal:/diagram/.clones/diagram-backlog-t271/rust/guard/src/guards/gate_write_hooks.rs
- 21:02 red-gate

## Each task, split at its decision points

In 1 part(s), 24344 bytes, cut at its rows (462 T555):

- `report/08-each-task-split-at-its-decision-points-1.md` (24344 bytes, rows T01 to T312)

## Each task's phases (plan D32)

In 8 part(s), 442621 bytes, cut at its rows (462 T555):

- `report/09-each-task-s-phases-plan-d32-1.md` (55237 bytes, rows T01 to T49)
- `report/09-each-task-s-phases-plan-d32-2.md` (56537 bytes, rows T49 to T51)
- `report/09-each-task-s-phases-plan-d32-3.md` (59020 bytes, rows T51 to T122)
- `report/09-each-task-s-phases-plan-d32-4.md` (63876 bytes, rows T122 to T195)
- `report/09-each-task-s-phases-plan-d32-5.md` (65118 bytes, rows T192 to T391)
- `report/09-each-task-s-phases-plan-d32-6.md` (64844 bytes, rows T399 to T406)
- `report/09-each-task-s-phases-plan-d32-7.md` (60523 bytes, rows T313 to T373)
- `report/09-each-task-s-phases-plan-d32-8.md` (18894 bytes, rows T420 to T312)

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

In 18 part(s), 875669 bytes, cut at its rows (462 T555):

- `report/10-each-task-s-decision-log-skeleton-plan-1.md` (40202 bytes, rows T01 to T108)
- `report/10-each-task-s-decision-log-skeleton-plan-2.md` (32872 bytes, rows T49 to T49)
- `report/10-each-task-s-decision-log-skeleton-plan-3.md` (32861 bytes, rows T49 to T49)
- `report/10-each-task-s-decision-log-skeleton-plan-4.md` (59539 bytes, rows T49 to T114)
- `report/10-each-task-s-decision-log-skeleton-plan-5.md` (32868 bytes, rows T51 to T51)
- `report/10-each-task-s-decision-log-skeleton-plan-6.md` (32856 bytes, rows T51 to T51)
- `report/10-each-task-s-decision-log-skeleton-plan-7.md` (65264 bytes, rows T51 to T87)
- `report/10-each-task-s-decision-log-skeleton-plan-8.md` (32899 bytes, rows T122 to T122)
- `report/10-each-task-s-decision-log-skeleton-plan-9.md` (32898 bytes, rows T122 to T122)
- `report/10-each-task-s-decision-log-skeleton-plan-10.md` (64677 bytes, rows T122 to T91)
- `report/10-each-task-s-decision-log-skeleton-plan-11.md` (59837 bytes, rows T94 to T190)
- `report/10-each-task-s-decision-log-skeleton-plan-12.md` (63559 bytes, rows T184 to T221)
- `report/10-each-task-s-decision-log-skeleton-plan-13.md` (58987 bytes, rows T219 to T282)
- `report/10-each-task-s-decision-log-skeleton-plan-14.md` (54787 bytes, rows T308 to T419)
- `report/10-each-task-s-decision-log-skeleton-plan-15.md` (63116 bytes, rows T404 to T424)
- `report/10-each-task-s-decision-log-skeleton-plan-16.md` (57469 bytes, rows T409 to T427)
- `report/10-each-task-s-decision-log-skeleton-plan-17.md` (63006 bytes, rows T428 to T373)
- `report/10-each-task-s-decision-log-skeleton-plan-18.md` (30420 bytes, rows T420 to T312)

## What each check cost, per changed line (215747 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 603 | 24 h 11 min | 99639k | 4550.0k | 0.003 | 0.5k |
| modal-research | 48 | 2 h 42 min | 87873k | 615.8k | 0.000 | 0.4k |
| modal-depiction | 41 | 1 h 47 min | 50148k | 369.5k | 0.000 | 0.2k |
| building-review | 24 | 2 h 12 min | 22530k | 459.4k | 0.000 | 0.1k |
| impl-drift | 83 | 1 h 23 min | 14984k | 411.3k | 0.000 | 0.1k |
| size-audit | 9 | 1 h 03 min | 13143k | 151.8k | 0.000 | 0.1k |
| glyph-check | 17 | 51 min | 10054k | 192.4k | 0.000 | 0.0k |
| record-format | 43 | 28 min | 5734k | 134.3k | 0.000 | 0.0k |
| spec-fidelity-verify | 6 | 18 min | 4564k | 59.9k | 0.000 | 0.0k |
| quote-check | 35 | 34 min | 3728k | 138.6k | 0.000 | 0.0k |
| modal-form | 42 | 31 min | 2636k | 157.8k | 0.000 | 0.0k |
| source-reader | 26 | 25 min | 2630k | 103.8k | 0.000 | 0.0k |
| escalation-check | 32 | 19 min | 2466k | 95.8k | 0.000 | 0.0k |
| source-applicability | 15 | 23 min | 1562k | 72.9k | 0.000 | 0.0k |
| message-check | 84 | 12 min | 1383k | 88.8k | 0.000 | 0.0k |
| translation-check | 9 | 4 min | 386k | 19.8k | 0.000 | 0.0k |
| intro-check | 1 | 0 min | 23k | 0.8k | 0.000 | 0.0k |

This report took 548.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
