# Feature 172 - the GM's request, verbatim

Context: the GM asked whether `hooks-test` needed to run as part of `make done` at all, expecting that
it should be skipped when the hooks had not changed. The session measured it and reported that this
already exists and costs 0 s when nothing changed - and that the sharper problem is that every suite
is declared to depend on all four SHARED helpers, so a one-line fix to `_gatecost.py` re-runs 21
suites when 2 could be affected.

The GM's instruction:

> Yes. Go ahead and do the dependency refinement as its own feature. That seems worth doing as it
> would have paid off a lot over the last couple of days.

Their reasoning in the message before it, which is what the feature is measured against:

> I mean, is it actually necessary to Run the Hooks tests as part of make done? I would have expected
> that we would run the hooks tests only when the hooks have updated. Right? I mean, We are already
> doing a lot of work to make sure that we skip over unnecessary tests if the parts of the engine that
> those tests run on has not already changed. So could we not do something similar where if the hooks
> have not changed, then we do not run the hooks tests? that feels like the obvious thing to do. And
> then at that point, it doesn't matter as much if make done is slower. I mean, obviously, we can
> still try to make the Hook's tests more efficient, but it just becomes less of a big deal at that
> point, I think.
