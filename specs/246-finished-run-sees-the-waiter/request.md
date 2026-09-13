# The GM's request, verbatim

2026-09-13, session "Diagram performance", after feature 245 landed. The GM had watched the finished-run guard refuse the same gate's turn-end three times in a row:

> Okay, so here's a general question about timing and efficiency.  I see that several times during that session we ran into the issue where you got this message:
> ```
> ● A waiter on the gate's log is already running in the background and will wake this session with the verdict; ending the turn to let both
>   waiting for it:
>     pid 2366194 done
>     pid 2367874 test-full
>     pid 2367876 test
>
>   Wait for it: background a loop on its log (`until grep -qE "verification-state|GATE FAILED" <log>; do sleep 20; done`)
>   and the no-poll guard will add the proof-of-life check for you. Then REPORT WHAT IT SAID.
>   Reporting a result you have not seen is the thing this prevents: on 2026-09-12 a gate failed 58 s
>   after a turn ended on "the gate is running" and sat unread for 52 minutes.
> ● The gate is in its test phase; the background waiter on its log is still armed and will report the verdict. Ending the turn again as the
>   hook allows.
> ```
> We put this hook into place because we kept repeatedly, overand over again, no matter what instructions were given, running into situations where a Claude code session would say something like "waiting for the job to finish" but then not actually wait for the job to finish, so I'd need to come back and say "hey the job finished", etc.  That seems to no longer be happening anymore, which is great.  However, the fact that we keep seeing this message over and over again makes me wonder whether we should take a different approach; it seems generally not good if we keep stepping on the same rake over and over again; perhaps there should be a different automatic hook behavior, like automatically starting a timer that prompts you every N minutes until the task is finished or something?  Don't make any changes yet, but tell me what you think about all of this.

The session's assessment (research R1 carries its measurements): the guard fires on states that are already correct because it cannot see an armed wait, its "once per run" is once per make PHASE because it keys on the child PIDs, its prescribed loop duplicates the harness's own completion wakeup, and a periodic timer would be polling by another name; the change proposed was to make the guard see a harness-tracked run and a live waiter loop mechanically, let both through with a one-line context, key the refusal on the root make, and keep the refusal only for a detached run with no watcher. The GM:

> That sounds good, please implement that.
