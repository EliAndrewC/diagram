# The GM's request, verbatim (2026-08-29, session "Diagram tests")

> We have recently made a number of efficiency improvements to our tests. If you look in our ten most
> recent features or so, then you will see that several of the features heavily involve making
> performance improvements by eliminating tests and eliminating automated checks, which are no longer
> relevant or useful. In other cases, we implemented caching, which meant that instead of performing an
> entire settlement generation just in order to perform a single unit test, we used a cached version of
> that, thus making the unit test one or more orders of magnitude faster. In other cases, we reduced the
> number of random seeds that we were running against. In other cases, we reduced the size of the
> settlement or the items in it when performing our unit tests. things like that. Our quick tests are
> still pretty quick, And we have increased the performance of our lengthier tests. However, I imagine
> there is still considerable room for improvement. At this time, I am only interested in the tests that
> are run while we are still developing on hamlets because we are still not yet done with our hamlet
> generation, which means we have not yet moved on to villages. However, looking at the sum total of all
> of the tests that we have, which run for hamlets under any circumstances, which I believe is three
> different tiers of tests, the quick tests, the make done tests, and then the completely full test
> suite, I would like for you to look at where we can make further performance improvements. places where
> we can make these kinds of cuts do an extensive audit. and see where these patterns, which we have
> already made successful use of, can be applied. if we are Running unit tests for an automated check.
> Then let's see whether that automated check is even still actually needed. In fact, I would guess that
> we need extremely few automated checks at this point because our placement algorithm is the thing which
> is doing the actual correctness guarantees. And in almost every case, there should be no reason for an
> automated check to even be run. Similarly, I think we have gotten rid of most or all of the stored maps
> from past failures because those maps were all from a period of time when the maps were manually
> generated. And, therefore, there is no reason to see what would happen if we encountered a type of map,
> which is literally impossible to produce any longer. that kind of thing. Please proceed with that audit
> and then eliminate any automated checks, which do not comport to this new standard along with the unit
> tests associated with them, and then make whatever refactors you are able to make to increase the
> performance of the unit tests which remain It is okay if the tests become slightly less rigorous so
> long as we maintain our code coverage standards. For example, reducing the number of random seeds that
> we test against is okay but reducing our unit test code coverage is not. reducing the size of a test
> fixture settlement, which a unit test runs against in order to make it run more efficiently is fine,
> but making the test unable to validate the behavior, which we are checking for, is not fine. That kind
> of thing. Please proceed with that. And then when you are done, push your results back to main. I will
> review what you have done after the fact and decide what to focus on next. Thanks.
