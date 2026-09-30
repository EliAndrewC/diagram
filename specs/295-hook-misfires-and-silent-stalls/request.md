# Feature 295 - hook misfires and silent stalls

The GM's words, verbatim (2026-09-30):

> I would also like for you to file a feature about the tooling problems. one feature for all four tooling problems that you hit. do not actually implement the feature, just go ahead and file it and let me know the feature number. Thanks.

The four problems, as the session reported them (2026-09-30, during feature 291's landing):

1. `finished-run-hooks.sh` does not see a background waiter on a chained run's own done-marker (a detached
   `bash -c "make ...; echo DONE >> log"` watched by a backgrounded `until grep -q DONE log` loop), so it blocked a dozen
   turns that were correctly covered, each insisting "nothing will wake this session".
2. `review-round-hooks.sh` routed a constitution-XVI EXCEPTION check to `spec-fidelity` into a later round of the spec
   review (`spec-fidelity-verify`), because the feature held a review snapshot; the verify agent declined it as outside its
   contract and the check had to be re-dispatched with `REVIEW_ROUND_OK`. The hook matched the feature id, not the mode the
   prompt asked for.
3. A headless page session (`make page-session`) that dispatches its checks as background agents does not wake when their
   results arrive: R12's check session committed, dispatched five re-checks, received all five results within three
   minutes, and sat idle for about two and a half hours until the session was killed and the runner resumed it.
4. No watchdog sees a stall from outside the session. The in-session hourly `CronCreate` check (added 2026-09-30) runs only
   while the session lives; a host-side watchdog that notices a session idle for over an hour with unfinished work - and
   notifies the GM or nudges the session - was proposed and not built. (The same day's `no-poll` fix - self-matching
   waits refused, a 90-minute ceiling on every wait - landed; this item is what it does not cover.)

## Item 5 (added 2026-09-30, from the Diagram reorg session, feature 292)

The GM's words, verbatim: "Feature 295 is about tooling changes, and it sounds like we need a tooling change to turn this kind of watcher into a cron. Is that something that could be done in a hook? I'm not asking you to make the change, but can you add this to the list of tooling deficiencies, which are already being tracked by that spec kit feature? That way we can try to address all of the tooling issues at once."

5. A periodic report built as a backgrounded one-shot watcher loses its schedule across a usage-limit window. Feature
   292's hourly progress report was a `run_in_background` loop that exits after an hour; the harness wakes the session
   on its exit and the session re-arms it. When the exit lands while the account is over its usage limit, the
   notification reaches a session that cannot run, nothing re-arms it, and the updates stop until the limit resets
   (observed twice on 2026-09-30, about two hours of missed updates each time). A recurring `CronCreate` job keeps its
   schedule by itself (292 switched to one, `23 * * * *`). A related misfire from the same watcher: its stall check read
   a session in the page-session runner's usage-limit retry wait ("failed ... waiting 15 min ... then resuming it") as
   stalled, its transcript idle for the whole wait. The proposed change (the GM asks whether a hook can do it): a
   PreToolUse hook on Bash that recognizes a backgrounded PERIODIC-report loop - a `run_in_background` command whose loop
   exits on elapsed time, or a POLL_OK reason naming a periodic report - and steers it to `CronCreate` with the equivalent
   schedule, as `wakeup-hooks.sh` steers an out-of-loop `ScheduleWakeup`; a hook cannot create the cron, but it can
   refuse with the exact `CronCreate` call. Event-driven waits (a failure, a stall, a finished queue) are not periodic and
   stay background watchers. Related to item 3.
