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
