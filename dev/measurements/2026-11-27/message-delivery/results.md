# How a message to a builder in mid-work is delivered, 2026-11-26/27 (451 T297, its second half)

Asked by 451 T297: "verify once how a message sent to a builder in mid-work is delivered, recording it in the builder brief".
Measured once, read-only, from what already happened. All times are UTC.

Method. `t297-delivery.py` (beside this file; run as
`python3 -I t297-delivery.py <session>.jsonl <session>/subagents 2000 > t297-all-sends.tsv`) streams the coordinating
session's transcript (`~/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl`, 285 MB) for every
`SendMessage` tool call (229 ids, every one on a timestamped line) and the tool result it got. It then finds the message in
the addressee's own transcript (`subagents/agent-<id>.jsonl`): a `queued_command` attachment whose `prompt` holds the
message's opening, or a user turn that holds it. The arrival is the matched line's timestamp, and its place is its position
in the file. A coordinator message's attachment is written straight after the tool result it rides on. A background task's
`task-notification` attachment carries its enqueue time instead, so the matcher takes coordinator messages only. "What the
builder was in at send time" is its last assistant block before the send. `t297-arrive.py` (run after `t297-sends.py <session>.jsonl t297-sends.json`, in the same
directory) prints each 2026-11-26/27 row's neighbors: the calls before and after the arrival. Builder names come from each `agent-<id>.meta.json`. Whether a builder
acted on a message was read by hand from its next steps and its report. A send's time is the timestamp of the session's
assistant line that holds the call, so each delay includes the SendMessage hooks' run.

## The night's 14 sends (every SendMessage of 2026-11-26/27)

Result words: Q-0 means "Message queued for delivery ... at its next tool round. Sending this moved nothing it is running to
the background just now". Q-bg means "... Moved 1 running tool call to the background without stopping it, so that round no
longer waits for it". R means "Resuming agent <id>" (the builder's turn had ended).

| send | builder (meta description) | result | in at send | arrival in the builder | delay | acted on |
|---|---|---|---|---|---|---|
| 11-26 01:26:20 | Finish 451 T254 review and checks | Q-0 | a text block, Bash running | 01:26:23, attachment after its Bash result | 2.8 s | already under way: it had read `closing.log` at 01:26:05 and written "Ours. Fix both lints." at 01:26:18, before arrival; after it, a clippy run and the `text += &format!` fix (01:27:00); a later lint came from its own closing-check re-run (01:31:39) |
| 11-26 02:45:15 | Build 451 T259 audit register | Q-0 | Bash | 02:45:22, attachment after Bash result | 6.6 s | yes, next step: fetched process-decisions at 8cf3a26e68, built the `kind` field |
| 11-26 06:09:59 | T250 last five comments | R | turn ended ("waiting on closing checks") | 06:10:00, user turn | 1.2 s | yes, next step: fetched the ids, `make decide` passed by 06:10:50 |
| 11-26 19:07:46 | Build 451 T304 carry flake and index lock | R | turn ended 18:03 ("waiting on the carry loops") | 19:07:48, user turn | 2.2 s | yes: load generators stopped 19:08:09, 21 s after arrival |
| 11-26 21:19:49 | Measure 451 T336 pre-warm link failure | Q-bg | a foreground Bash (a measurement arm) | 21:19:52, attachment after the moved call's "moved to the background" result | 3.5 s | yes: "Scope change received" at 21:20:01; handoff written 21:29:50, report "MEASUREMENT done" |
| 11-26 21:30:24 | Measure then fix: 451 T347 slot wait | Q-0 | an advisor call (from 21:30:04) | 21:33:11, after the advisor and one Bash | 167.2 s | yes (informational): no edit to `prewarm.rs` or `rustc.rs` ("I changed none"); the T336 constraint was carried into its handoff |
| 11-26 23:37:40 | Fix: 451 T381 coverage in the brief block | R | turn ended ("waiting on the plan review") | 23:37:41, user turn | 1.2 s | yes, next step: `git restore` of its 8 paths, report at 23:37:56. But the plan review it had launched in the background ran on: TaskStop was called, and at 23:40:53 it wrote that the review "I could not stop has now finished" (its `make plan-verdict` was refused, the section being gone) |
| 11-27 00:09:27 | Measure: 451 T373 Edit hook latency | Q-0 | an advisor call (from 00:09:14) | 00:12:47, after the advisor and one Bash (a grep) | 199.8 s | largely moot: its record (`dev/measurements/2026-11-26/edit-hook/t373-results.md`) was written at 00:07:51, before the send, and at 00:09:14 it wrote "Deliverable is durable"; it edited the record and reported at 00:13:33, 46 s after arrival, "stopped measuring on the coordinator's word" |
| 11-27 00:09:30 | Fix: 451 T324 T345 resumed agents' time | Q-0 | an advisor call (from 00:06:48 to 00:11:14) | 00:11:26, after the advisor and one Bash | 115.2 s | yes, conditional: both fixes were built (last source edit before the send 00:00:31), so it took the "both built" branch; plan section and report by 00:18:11 |
| 11-27 03:08:19 | Build half: 451 T313 queue and pool kept full | R | stopped 02:05 by the usage limit | 03:08:20, user turn | 1.3 s | yes, next step: `git status` as told; report at 03:10:01 |
| 11-27 03:08:21 | Fix: 451 T355 lint in the small lane | R | stopped 02:08 by the usage limit | 03:08:22, user turn | 1.3 s | yes, next step: `git status` and a ps for half-run measurements, as told |
| 11-27 03:08:23 | Fix: 451 T308 two tiers in the tooling | R | stopped 02:05 by the usage limit | 03:08:24, user turn | 1.3 s | yes: "Noted: the landed-task count will come from the record" at 03:08:27 |
| 11-27 03:08:25 | Fix: 451 T314 state-sync suite flake | R | stopped 02:06 by the usage limit | 03:08:26, user turn | 1.2 s | yes, next step: read its kept output, then made the race certain in a scratch copy, as told |
| 11-27 03:45:04 | Fix: 451 T313 two review objections | Q-0 | Bash | 03:45:15, attachment after a Bash result | 11.3 s | yes, at the point the message named: "Built here: T395" written in its section edit at 03:59:01 (14 min later, the section edit it was told to fold the line into) |

Every message of the night arrived, 14 of 14, and none was ignored. 12 were acted on at the builder's next step or at the
point the message named, one of them by choosing between the message's branches (T324). One had been anticipated: the
builder was already doing it (T254). One was largely moot: the builder had finished what it asked (T373). One withdrawal
(T381) was obeyed in full, but it did not stop a review agent the builder had already launched in the background.

The three slow ones (115-200 s) were each held by an advisor call. In each hold window the builder made one tool call and
nothing the message forbade. T347 edited its own measurement script. T373 ran a read-only grep. T324 ran what it called a
background measurement that restores `book.rs` (a copy kept first), which its "both built" branch allowed.

## The whole session (2026-11-12 to 11-27, every SendMessage)

`t297-summary.txt`, from `t297-all-sends.tsv`:

| result | sends | located in the builder | median delay | 90th pct | longest |
|---|---|---|---|---|---|
| Q-0 (queued, moved nothing) | 80 | 80 | 6.1 s | 128.5 s | 199.8 s |
| Q-bg (queued, a running call moved to the background) | 14 | 14 | 1.5 s | 5.6 s | 8.3 s |
| R (resumed) | 130 | 126 (4 of 11-12/16 have no transcript file) | 0.2 s | 1.2 s | 19.3 s |
| refused or other | 5 | - | - | - | - |

- Form. A queued message arrived as a `queued_command` attachment, rendered to the builder as a system reminder ("The
  coordinator sent a message while you were working: ..."), placed after the last tool result of the builder's current tool
  round. That held in 91 of 94 cases. In the other 3, the builder finished first and was resumed with the message as a user
  turn, as the result promises ("If it finishes first, it is resumed with the message"). A resumed builder got the same text
  as a user turn within about 1 s.
- What holds a queued message. Every delay over 60 s, 10 of 10, was an advisor call (109 to 200 s). The message waits for the
  next client tool result, and an advisor call is a server tool, so it is no round. The hold lasts as long as the advisor
  call: the longest seen ran 4 min 27 s (T324's, 00:06:48 to 00:11:14). The 21 delays of 10-60 s had, as the builder's last
  block at send time, a Bash in 15, a text block in 3, an advisor call in 2 and an Edit in 1. A foreground call is moved to the background (Q-bg) so that it does not hold
  the message. Its side effect, seen with T336, is that the builder is told the command "was moved to the background" and
  then waits on its output by hand: T336 started a foreground `until grep ...` on the moved task's output file.
- Refused: two resumes by the guard (a builder past the 300k cap, 11-20; a builder whose task had landed, 11-25). Three were
  to another session by name (11-24), one of them ambiguous with two sessions named alike.

## The rule it supports (for `scripts/container/builder-brief.md`, a section on re-scoping a builder in flight)

A message sent to a builder with `SendMessage` reaches it. None was lost of the 220 located, 2026-11-12 to 11-27. It arrives
at one of two moments, and the result's first words say which. "Resuming agent" means the builder's turn had ended: it was
waiting on a background job, stopped by a usage limit, or done. It gets the message as a user turn within about a second.
"Message queued for delivery ... at its next tool round" means the builder is mid-turn. The message is attached after the
last tool result of its current round: median 6 s, and 1.5 s when the result says a running call was moved to the
background. An advisor call holds it until the call ends, up to about 4.5 minutes (all 10 delays over a minute). On
2026-11-26/27 builders took up 14 of 14: 12 at their next step or at the point the message named, one already doing it, one
already done. So do not resend a queued message: the result itself says, if the builder finishes first, "wait for that
notification before resending". Write a re-scope to survive an advisor call's few minutes: as a stop at the next boundary, or
as branches the builder picks from what it has built ("if job 2 is not yet built, do not start it"), never as "stop what you
are doing now". A withdrawal stops the builder's own edits, but not an agent or job it already launched in the background
(T381's plan review ran on after TaskStop), so name what to stop and expect a late notice from it. A message after the
builder's report resumes a finished builder, which the brief's "ends at its report" rule keeps for a question it asked.
Measured in `dev/measurements/2026-11-27/message-delivery/results.md` (451 T297).

## Levers

None filed. The table shows no message lost. The latest action, 200 s after a send, cost nothing: the hold windows held one
permitted tool call each, and T373 had already written its record. A lever to deliver during an advisor call would save at most
an advisor call's length (up to about 4.5 minutes, seen ten times in 220 sends) of a builder already near its end, and is not
filed. Neither is a lever for T381's case: the message was neither lost nor late, and what ran on was the builder's own
background agent, which the rule paragraph covers.
