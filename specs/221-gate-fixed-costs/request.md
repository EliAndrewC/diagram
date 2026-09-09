# Feature 221 - the GM's request, verbatim (2026-09-09)

After feature 220 landed, the GM asked how long `make done` takes now, and then:

> Yeah. Go ahead and do a profile of the gates phases. And, also, just in general, how long the tests
> take to run and what that time is spent on and whether there is any more low hanging fruit involved.

The session measured the gate phase by phase and the test suite three ways (research R1 reproduces the
tables) and answered with four items, which the GM then approved, so they are reproduced here as the
request's substance:

> **Low-hanging fruit, in order of value**
>
> 1. Workers are capped at 6 on a 22-CPU box. The cap came from the memory ceiling measured before
>    feature 208 moved the page raster out of the workers. Re-measure peak memory at 8, 10 and 12
>    workers with feature 208's method; if two concurrent gates still fit under 8 GiB, raise the cap.
>    This is the cheapest change and the biggest: I would expect the 47 s to land near 30 s.
> 2. Coverage contexts. The gate traces the whole engine with a context per test on every run because
>    the incremental gate merges on them. The scoped run without contexts is 15 s for the same tests
>    that take far longer under the gate. Measure the contexts' share on the full tree; if it is more
>    than 10 s, the question is whether an incremental run needs them or only the baseline run does.
> 3. The bookkeeping prints three full coverage tables, about 2.5 s each. The first one is pytest-cov's
>    own and is meaningless on an incremental run. Print one.
> 4. The two village rolls in `tests/full`. Ask `make roll-audit` whether they still carry lines nothing
>    else reaches; if not, feature 216's doctrine moves them to the soak tier.
>
> I would take items 1 and 3 together as one small feature, with item 2 measured inside it and item 4
> checked by the audit. Say the word and I'll claim it.

The GM:

> All four of those sound good, so please make a feature that includes all four of them. Thanks.

A correction the session owes on item 1's premise, found while writing the spec: the cap of 6 was not set
by feature 208's memory ceiling but by feature 213's measurement of the gate at 4, 6 and 8 workers (346,
301, 297-322 s, "the smallest count within 10% of the fastest", with the memory two idle workers give back
to other sessions' gates as the tie-break) - taken when the gate rolled 37 hamlets and was roll-bound. The
item stands as approved: re-measure on the gate as it is now, memory included, and set the cap by the same
rule.
