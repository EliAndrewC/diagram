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
