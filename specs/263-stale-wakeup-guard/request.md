# The GM's request (verbatim, 2026-09-26)

Context: the GM noticed their "Diagram buildings" terminal tab showing the hourglass (background work pending)
when the session was waiting for them. The cause was a timed wakeup the session had scheduled with
`ScheduleWakeup` as a fallback while a background agent ran; the agent reported back, the work landed, and the
wakeup was never cancelled, so every turn ended with a pending session cron. The session cancelled it and said it
had "saved a note to cancel fallback wake-ups once the work they guard is done." The GM:

> So you say that you've saved a note to cancel fallback wake-ups. What's the work the guard has done? But do you just mean that you've saved something in a memory or whatever? Because I think our experience is that these kinds of things need to be mechanical. It needs to be literally impossible for them to do the wrong thing. Or else we will just end up doing the wrong thing a lot. So how does that influence this decision and how we should guard against this?

The session proposed two mechanical layers: (1) refuse `ScheduleWakeup` unless the session is actually running
`/loop` (the tool's own contract is /loop-only, and the harness already wakes a session when background work
finishes); (2) at turn end, when a timed wakeup is still pending with nothing running in the background and no
`/loop`, block the turn from ending and name the exact cancel. It flagged the one design question - what the
second layer must never block (reminders the GM asks for; `/loop`) - to be MEASURED from the real turn-end payload
rather than guessed. The GM:

> Yes, please go ahead and implement that as a new feature. Also, I see that the icon has disappeared from the diagram research session. And also the diagram research session seems to have a "(2)" in its terminal title. Is that indicating the number of active subagents or something? I guess I'm not really clear on what is being communicated there, though I honestly don't object to that because seeing like what is happening when there's an hourglass or something seems okay, but right now it just looks bugged. I mean, you can potentially fix that as part of this feature, I guess, although since I think the code that makes this work is outside of this repo, then I don't know that that would make a difference. But really, I mostly just want it fixed and such, so. Yeah, please proceed with that. Thanks.

The tab-title fix (the "(2)" and the missing icon) lives in `~/.claude/hooks/tab-title.sh`, outside this
repository, and was fixed directly the same turn (see spec, Assumptions).
