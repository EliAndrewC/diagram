# Request - feature 386, verbatim

## The GM's question, 2026-10-17

> How long do our unit tests take these days? Like, how long are the quick tests? And then separately, I know that we
> have this notion of uh, running through lots of maps on lots of different seeds, and it does seem like that does find
> issues, so I'm guessing that we probably want to keep doing it, but in general, like, do we feel like we are running the
> tests that run on a lot of seeds at the right stage in the development process? And how long do those tests take to
> run? Like the runs where we run all the different seeds? You know, because I think we have like 50-something of them
> now or something.

## The session's answer: the measurements and the recommendation (as given to the GM)

Measured on main `e2f755b5f` (2026-10-17): `make quick ALL=1` 112 s; `make done` 161-282 s on the day's green runs;
`make cohort` (10 seeds + the 6 pinned rows) 48 s uncached; `make cohort N=48` (54 maps) 114 s uncached; ~10 s either
way when the roll cache serves a commit someone already rolled. The cohort is in no gate: sessions run it by hand.

The log (`dev/cohort-log/`): on 2026-10-12/13 about 30 ten-seed cohorts passed, then the next 48-seed run failed on seeds
17, 21, 40 and 45. Seeds 1-48 all pass on main now, but 48 seeds nobody had rolled (400-447) failed 6 times (12%): 403,
404, 408, 409, 425, 439.

> **My recommendation:**
> - Keep the 10-seed cohort per fix. At 48 s it's the right inner loop.
> - Run 48 seeds when a feature or batch lands. At about 2 min that's cheap next to a 3-4 min gate, and it's what would
>   have caught 17/21/40/45 the same day.
> - Add a block of **fresh seeds** that rotates each run, recorded as a failure rate rather than a pass/fail, so we can
>   see how well the generator handles seeds it has never been tuned on.
>
> That would change the cohort default and the landing route, so it's a feature. If you want it, I'll file it.

## The GM's approval, 2026-10-17

> Sounds good, please implement your recommendation as a feature - file it and then implement it now, thanks.
