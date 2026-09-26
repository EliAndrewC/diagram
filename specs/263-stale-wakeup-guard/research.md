# Research - feature 263 (measurements)

## R1 - What a pending cron looks like in the Stop payload (measured 2026-09-26, one-shot)

Method: the tab-title hook keeps each session's last Stop payload (`/tmp/tab-title-<uid>/<pid>.stop.json`). One
`CronCreate` one-shot (a stand-in for a reminder the GM asked for) and one `ScheduleWakeup` (60 s) were created, the
turn ended, and the payload was read on the wakeup. `session_crons` held:

    {"id": "106428e0", "schedule": "17 9 24 12 *", "recurring": false, "prompt": "MEASUREMENT PROBE (feature 263): ..."}
    {"id": "e1f0ebb6", "schedule": "58 20 * * *",  "recurring": false, "prompt": "Feature 263 measurement: read ..."}

The two are the same shape: no field says which tool made a cron. The wakeup's `prompt` is verbatim the `prompt`
argument of the `ScheduleWakeup` call in the transcript; the reminder's matches no `ScheduleWakeup` call. So the
transcript is the discriminator (FR-002, FR-003). Both probes were cancelled (the wakeup fired and auto-deleted; the
reminder by `CronDelete`).

## R2 - The incident (2026-09-26)

A fallback `ScheduleWakeup` (1500 s) set while a prose-fix agent ran stayed pending after the agent reported and the
work landed; `CronList` showed `43582eac - Every day at 8:51 PM (one-shot)`; the tab showed the hourglass until it was
cancelled by hand.

## R3 - A live /loop, measured (2026-09-26, one-shot)

History first: 123 transcripts on this host call `ScheduleWakeup`; none invokes `/loop` (the only `/loop` text is
this feature's own session discussing it). Every wakeup ever set here was an out-of-loop fallback.

Then one loop was run for real: the `loop` skill invoked with a trivial input, one tick, then stopped.
- The invocation lands in the transcript as a `Skill` tool call (`{"skill": "loop", "args": "<input>"}`), and each
  wakeup FIRING lands as a user entry `<command-message>loop</command-message> <command-name>/loop</command-name>
  <command-args><input></command-args>`.
- The loop's wakeup, pending at turn end, was `{"id": "0ec9c84c", "schedule": "4 21 * * *", "recurring": false,
  "prompt": "/loop <input>"}` - the skill's contract (the prompt is the loop input prefixed with `/loop `) holds.
- It ended with `ScheduleWakeup(stop: true)`, whose result: "Loop stopped - any dynamic loop in this session is ended;
  there was no pending wakeup to cancel" (the tick had already fired).

So a wakeup is a loop's own when its prompt is `/loop <...>` (or the autonomous sentinel), and the loop is live while
the transcript's latest loop event is an invocation rather than a stop (FR-001, FR-002).
