# Research - 248 reviews one per map

## R1. What the serialized review cost, and what the ledger says the review catches

**This session's measurement** (observed 2026-09-14, from the session transcript's tool timestamps): feature
247's settlement-review was ONE agent dispatched over four maps, 45 tool uses, 655 s wall - 11 of the
feature's 36 minutes, the largest single wait. The agent's own report opened with *"I was handed FOUR maps
in one agent. Per my contract that should be four parallel agents - the sweeps share no work across maps,
so this run serialized them."* The contract already said so (`.claude/agents/settlement-review.md`); nothing
enforced it. `make verify` printed one line - *"DISPATCH NOW, in the same turn: settlement-review over
inashiro kashikawa mizuguchi sawada"* - and a session following it literally dispatches one agent.

**The ledger, 2026-09-11 to 2026-09-14** (`docs/review-ledger.md`, the settlement-review rows):

| feature type | passes | caught something the author had missed |
|---|---|---|
| layout (226, 227, 230) | 19 | every pass - 226's sun-strip contradiction on the shipped maps, 227's five defects invisible to a green gate, 230's fourteen rounds |
| rendering or performance (222 to 225, 228, 245, 247) | 9 | none on a map; one delivered-artifact miss (222's pages shipped without their pictures) |

So the review earns its time on a layout change and has caught nothing on a rendering one, which is the
GM's question answered: *"whether we can skip it for features like this one specifically, i.e. changing a
glyph rendering convention rather than tweaking actual map features"*.

## R2. Where the push refusal's time went

Every push-time check, timed on this clone (observed 2026-09-14, `date` around each script):
duplicate-defs 0.98 s, the conflict-marker scan over 3,147 files 0.33 s, file-scale, entry headings,
spec-lint, gate-stamp, entry-gate, plan-gate each under 0.15 s, review-gate 0.02 s. The refusal cost
three model turns, not a check: the refusal, two reads to recall the notes-file format, and the push
itself (56 s, the landing and the mirror's render-sync). The redundancy is the cost: since feature 240
the reviewer writes `<clone>/.git/review-verdicts/<map>.json` as its last act, keyed on the engine
key, and `review-gate.sh` still demands the 2026-07-27 form beside it - the map's `.notes.md` touched in
the same push. Two records of one pass, one of them hand-written.

## R3. What a hook can guarantee about a dispatch, and what it cannot

A `PreToolUse` hook on the Agent tool runs BEFORE the agent starts, sees `subagent_type` and the prompt,
and may refuse (exit 2), rewrite that one call's input, or add context; the pair guard already resolves
the session's clone, asks `_review_owed.py` which maps are owed, and runs `_review_prereq.py` over the
prompt (the check that refused feature 247's first dispatch for a missing render). A `Stop` hook may
refuse a turn from ending and can read the session transcript (the subagent transcripts under
`<transcript dir>/<session>/subagents/`, which `agent-stall-hooks.sh` and `review_pending` already read).

What no hook can do: launch an agent, split one Agent call into several, or make the model put several
calls in one message. So the property "one agent per map, all of them, in parallel" decomposes into
what can be enforced mechanically - the wrong shape never runs (a multi-map dispatch is refused before
it starts), a turn never closes with an owed map undispatched - and what can only be measured after the
fact (whether the dispatches shared one message). The same class of guarantee as the paired gate
(feature 151) and the still-going-run rule (feature 246): the wrong thing is impossible, the right thing
is the only way to finish, and the census says whether it happened.

**Can parallelism be detected?** The harness issues the tool calls of one assistant message together, so
their dispatch times lie within seconds of each other; sequential dispatches are a model turn apart at
least (tens of seconds, usually minutes, because the second waits on nothing but the session). A spread
of the owed maps' dispatch times under 60 s is parallel; over it, serialized. Recorded, never refused -
by the time it can be judged the agents have run.

## R4. The task classification, and what "rendering-only" is

Every spec-kit task is classified when it is created (`research: rendering | physical | procedure`,
CLAUDE.md, constitution v2.12.0); `tests/test_task_research_boxes.py` gates the physical form's boxes.
A rendering task is *"a map convention with nothing physical behind it"*; a physical task *"is about how a
place was built, farmed, planted or lived in"*; a procedure task is tooling. The GM's words name the first
class exactly - *"changing a glyph rendering convention rather than tweaking actual map features to comport
to historical norms"* - so the waiver is a feature whose tasks are ALL `research: rendering`. A procedure
feature that moves a manifest (a placer refactor, a performance lever) is NOT waived: it changed the
layout by a mechanism nobody researched, which is the case the review exists for, and feature 226's
first pass is the record of what a re-seating can do to shipped maps. The active feature is the one the
clone's `.specify/feature.json` names (the pointer `sync-with-main.sh` already reads for the in-progress
rule), and its `tasks.md` must exist and hold at least one task.

## R5. The maps a dispatch names

`_review_prereq.stale_maps` already reads a dispatch's prompt for `review-snapshot/<map>` (the snapshot
directory the reviewer's contract tells it to read). A prompt names the maps it asks to review by those
directories; a prompt naming none of them names its maps by bare name (a word match against the owed
set). Counting bare names in a prompt that also names a snapshot would count a map mentioned for context
("unlike Kashikawa's ...") as a second review, so the snapshot form wins when present. The per-map prompt
files `make verify` writes (FR-002) name exactly one snapshot each, so a session that dispatches from
them never meets the bare-name rule.
