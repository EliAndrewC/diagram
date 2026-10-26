# Research: feature 429

## R1 - the gm-question detector, measured (FR-002, D168), 2026-10-26

**Corpus.** `measure/finals.py` read the last 60 main-session transcripts under `~/.claude/projects/-diagram*/`
and took each turn's final assistant text (the last assistant text before a user record carrying text): 1,426 final
messages. The transcripts are not committed (they are session records); the labels are, in `measure/`.

**Labels, independent of the detector.** A Sonnet reader, given only the messages and the definition (ASKS: a
question, a choice, or a request for a decision, approval, go-ahead or action put to the GM; NONE: a report, answers to
his own questions, verification steps), labeled two seeded random samples it never saw scored:

- `labels-r1.json`: 81 messages (80 drawn with seed 429, plus the 2026-10-25 feature 417 message, index 1164): 8 ASKS.
- `labels-holdout.json`: 100 messages drawn after the detector was first widened (seed 4292, none from r1): 11 ASKS.

**Results** (`python3 measure/finals.py 60 <finals.json>`, then `python3 measure/detect.py <finals.json> measure/labels-r1.json measure/labels-holdout.json`; the labels are keyed by the sha1 of each message's text, so a grown corpus still finds them - re-run 2026-10-26 on 1,435 messages: 8 of 8, 10 of 11, no false alarm):

| detector | flags of 1,426 | r1 recall | r1 false alarms | holdout recall | holdout false alarms |
|---|---|---|---|---|---|
| first draft (ask phrases + a "?" line naming you/your/I) | 65 | 5 of 8 | 0 of 73 | - | - |
| widened on r1's three misses ("for you to decide", "approve or decline", "ask of you", "needs your ...", "waiting on you") | 86 | 8 of 8 (fitted) | 0 of 73 | **9 of 11** | **0 of 89** |
| widened on the holdout's misses ("yours to decide", "if you want ... I") - as shipped | 88 | 8 of 8 (fitted) | 0 of 73 | 10 of 11 (fitted) | 0 of 89 |

The honest out-of-sample figure (a one-shot observation, 2026-10-26, by `measure/detect.py`) is the holdout's **9 of 11 recall with no false alarm in 89**, taken before its
misses were fitted. The 2026-10-25 feature 417 message is caught by every version ("1. Should I switch off the settle's
16 repair steps one at a time ..."). The one message the shipped detector still misses offers rather than asks ("I can
raise it too if you want."). A miss costs what the GM pays today; a false alarm costs one cheap `escalation-check`
pass, and the block is once per message.

**Seeded sample of the first draft's hits** (25 of 65, seed 1): every one put a question, choice or approval to the GM,
e.g. "Shall I amend T02 to include the four check-cost fixes?", "Fold it into 417, or keep it separate?", "Say go and
I'll run it end to end."

## R2 - when is a subagent finished? (FR-001, D167), 2026-10-26

- `meta.json` carries `"finished": true` once an agent finishes on this harness (2.1.310), but 6,607 of the 7,078 meta
  files on this machine carry no `finished` key (older harnesses), so the transcript is read too: a finished agent's last
  record is an assistant message with `stop_reason: end_turn` (both finished agents of this session; a running one
  ended on an `attachment` record mid-run).
- `agent-stall-hooks.sh pending` (an agent whose last record is a tool_result) was NOT used: a review mid tool call ends
  on an assistant `tool_use` record and would read as finished. Unfinished is therefore "not finished by meta, not ended
  on end_turn, not acked after a TaskStop" - stalled or not (spec-fidelity round 1).

## R3 - asks and offers told apart (FR-006, amendment 1), 2026-10-26

The GM, after the landing: offers are not questions, but an offer is due only above a threshold of significance
(`request.md`, amendment 1). The detector now reads two kinds of line: an ASK (the earlier patterns, less the two that
were offers - "let me know if" and "if you want ... I") and an OFFER ("if you'd rather", "happy to", "I can switch /
revert / raise ...", "say so and I'll"); an ask on the same line wins. Both owe the filter once per message, with a
different instruction: a question is judged by the five tests, an offer by its significance (`escalation-check`'s
offer section).

**Labels.** The 181 messages of R1's two samples, relabeled by a Sonnet reader three ways (ASKS: must be answered before
the work goes on; OFFER: a decision already made, offered back; NONE): `measure/labels-3way.json`, keyed by message sha1.
19 ASKS, 1 OFFER, 161 NONE.

**Result** (a one-shot observation, 2026-10-26, `measure/detect.py <finals.json> measure/labels-3way.json`): asks read
as asks 18 of 19, the offer read as an offer 1 of 1, no false alarm in 161. The one ask missed is borderline - "T05,
re-landing the well patch, is next when you want it" - which the labeler itself called close to an offer. One offer in
181 messages is thin: offers were rare when every one was treated as a question, so the offer patterns rest mostly on
their wording, and the significance test is the filter's judgment rather than a pattern.
