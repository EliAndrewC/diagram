# 429-memory-rules-as-guards - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
## T01 - no engine edit while a map review runs (FR-001, SC-001)

### T01 Approach (checklist part A)

1. **The goal, in the world.** An engine edit cannot turn a running review's verdict into NOT-REVIEWABLE.
2. **The constraints.** FR-001; the engine list is `delta.is_engine()`; the review types are `pair-hooks.sh`'s.
3. **Where each comes from.** G: the GM's request and the approved proposal (`request.md`); O: the incidents of
   features 261 and 317.
4. **Do they describe the world here?** Yes: `research.md` R2.
5. **The order.** the decider, the hook, its wiring, its suite.
6. **The exits.** a refusal with the compliant routes; no token escape (the compliant route is to wait or TaskStop).
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-engine-freeze-hooks.sh` green: refused with a live review, passes after it
   finishes, passes for a doc or test, passes for a non-review agent, passes for a stall acked; an old unfinished review refuses until acked.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

**D167 - a new guard, `engine-freeze-hooks.sh`, with its decider `lib/hm_engine_freeze.py`.** It finds the session's
subagents directory from the payload's `transcript_path` and keeps every agent whose `meta.json` `agentType` is in the
map-review set and that has not FINISHED - not `"finished": true`, not ended on an assistant `end_turn`, not acked after
a TaskStop (`<subagents>/../stall-ack/<id>`) - stalled or not, however old (spec-fidelity round 1; the plan review struck
an age bound as a narrowing FR-001 does not have); a stalled one is named with the ack command. An engine path
in this session's clone is refused while any remain. The review set and the engine list are read from their one copy
(`pair-hooks.sh`'s `REVIEW_AGENTS_RE`, `delta.is_engine()`), never restated.

<!-- plan-archive: archived 2026-10-26 -->
## T02 - a question for the GM goes through escalation-check (FR-002, SC-002)

### T02 Approach (checklist part A)

1. **The goal, in the world.** No question or decision reaches the GM unfiltered, review or no review.
2. **The constraints.** FR-002; the existing review-armed branch is unchanged.
3. **Where each comes from.** G: request; O: the 2026-10-25 incident; the measurement above.
4. **Do they describe the world here?** Yes: `research.md` R1.
5. **The order.** the detector in `scripts/hooks/lib/hm_gm_question.py`, the Stop branch, the suite.
6. **The exits.** blocked once per final message (keyed by its hash), never a loop; a filter dispatched since the GM's
   last message passes it.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** the escalation suite gains the 10-25 shape (blocked once), a report (passes), a filtered turn
   (passes), and the second stop on one message (passes).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

**D168 - the detector lives in `lib/hm_gm_question.py`; `measure/detect.py` scores it.** A line outside code, block quotes and quoted
text that carries an ask phrase ("should I", "shall I", "do you want", "want me to", "which ... do you", "your call",
"or should I", "say go", "for you to decide", "needs your ...", "yours to decide") or ends in "?" with "you"/"your"/"I" in it. "Since the GM's last message" is read from the
transcript: an `Agent` tool_use with `subagent_type` `escalation-check` after the last user record that carries text.

<!-- plan-archive: archived 2026-10-26 -->
## T03 - gm-assistant's main tree is not edited from here (FR-003, SC-003)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant's pushes are never refused by a diagram session's leftover edits.
2. **The constraints.** FR-003; a gm-assistant clone and the rest of `/host-l7r-repo` stay writable.
3. **Where each comes from.** G: request; O: diagram#10.
4. **Do they describe the world here?** Yes: measured above.
5. **The order.** the hook, its wiring, its suite.
6. **The exits.** Edit/Write: refused, no escape (a clone is the route). Bash: refused, `GM_TREE_OK: <reason>` escape.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-gm-tree-hooks.sh` green on each write form and each passing path.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

**D169 - a new guard, `gm-tree-hooks.sh`, matching INVOCATIONS.** Edit/Write/NotebookEdit by `file_path`. Bash by its
write targets only - a `>`/`>>` redirection target, a `tee` argument, a `sed -i` file, the last argument of `cp`/`mv` -
parsed with `hookmatch.py`'s splitter, so a `grep` or `cat` of the tree is untouched. A path is in the tree when its
resolved form is under `/host-l7r-repo/gm-assistant/` and not under its `.clones/`.

<!-- plan-archive: archived 2026-10-26 -->
## T04 - a reroll says whether it moved the map, against HEAD (FR-004, SC-004)

### T04 Approach (checklist part A)

1. **The goal, in the world.** A wave records "moved" or "unchanged" from the comparison with HEAD, printed for it.
2. **The constraints.** FR-004.
3. **Where each comes from.** G: request; O: feature 328 wave 68.
4. **Do they describe the world here?** Yes: 5 tracked manifests.
5. **The order.** `scripts/measure/maps_moved.py`, the target, the line at the end of `make map`, a test.
6. **The exits.** a report, never a refusal.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/tooling/test_maps_moved.py` green: a fixture repo with one changed manifest names it alone.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

**D170 - `git diff --quiet HEAD` per tracked pool manifest, plus untracked manifests.** `maps_moved.py [--only <gen>]`
prints `moved against HEAD: <manifest>` per differing file or `no pool manifest moved against HEAD`; `make map` calls it
with `--only` for its own map.

<!-- plan-archive: archived 2026-10-26 -->
## T05 - the records and the docs (FR-005, SC-005)

### T05 Approach (checklist part A)

1. **The goal, in the world.** Each new guard is in the guard table, records its firings, and the rules that said
   "remember" now point at the tooling.
2. **The constraints.** FR-005.
3. **Where each comes from.** G: request.
4. **Do they describe the world here?** n/a - records and docs.
5. **The order.** after T01-T04.
6. **The exits.** `make hooks-test` green.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test` green; `docs/guards.md` rows; `l7r/diagram/CLAUDE.md`'s reroll line names
   `make maps-moved`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
## T06 - found while working: `make guard-edit` refused every hook (constitution XIV)

### T06 Approach (checklist part A)

1. **The goal, in the world.** `make guard-edit FILE=scripts/hooks/<x>-hooks.sh` grants the permit the guard-file guard asks for.
2. **The constraints.** The permit's guard list is the guard-file guard's list.
3. **Where each comes from.** O: 2026-10-26, T02's edit of `escalation-hooks.sh`: the guard demanded `make guard-edit`, and
   `make guard-edit` answered "is not a guard file" - `hm_guard_permit.py`'s pattern still read `scripts/<x>-hooks.sh`,
   from before the hooks moved to `scripts/hooks/` (2026-10-08), so sessions fell back to inline markers.
4. **Do they describe the world here?** Yes: reproduced, and the new test case fails on the unfixed pattern.
5. **The order.** the test case, then the pattern.
6. **The exits.** n/a.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-guard-file-hooks.sh` green with the case (52 of 53 on the unfixed pattern).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

**D171 - `_GUARD` reads `/scripts/(hooks/)?<name>-hooks.sh`**, so both layouts are guards and a suite stays excluded.
<!-- plan-archive: archived 2026-10-26 -->
## T07 - amendment 1: offers are not questions, but owe a significance test (FR-006, SC-006)

### T07 Approach (checklist part A)

1. **The goal, in the world.** The GM sees an offer only when the decision it hands back mattered, and never as a question.
2. **The constraints.** FR-006; FR-002's question branch unchanged.
3. **Where each comes from.** G: amendment 1 in `request.md`; O: `research.md` R3.
4. **Do they describe the world here?** Yes: R3, three-way labels.
5. **The order.** the detector's split, the refusal text, escalation-check's offer section, the suite, R3.
6. **The exits.** an offer-only message refused once with the significance instruction; an ask wins on a mixed message.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-escalation-hooks.sh` section 10 green; R3's counts.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

**D172 - one detector, two kinds of line; one filter, two instructions.** `hm_gm_question.classify` returns ask lines and
offer-only lines (an ask on the same line wins); `judge` prints `ask` or `offer` with the first line. An offer still owes
the once-per-message `escalation-check`, because the GM's threshold of significance is a judgment the filter makes
(its offer section: KEEP a decision that might otherwise have been floated as a question, CUT a routine one, cut a message
offering back most of its decisions down to the one or two that clear the bar). No count cap: a pattern cannot weigh
significance.
