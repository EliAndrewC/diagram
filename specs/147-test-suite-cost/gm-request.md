# The GM's request, verbatim (2026-08-29)

This is the text feature 147 is graded against. It is the GM's own words, unedited.

> Okay. Sounds great. when you say that it landed at that commit, I assume you mean that that was pushed
> back to the main checkout, which is perfect. Now I think it's time that we do another pass on efficiency.
> Have we added enough things to make quick, to make it slower than we want? I ask not because I have any
> specific reason to think that this has happened, but because this general thing has happened in the past.
> So it's worth asking about now. Also, how long is the previously four to five minutes worth of tests now?
> what efficiency improvements remain? What things are we currently doing which are computationally
> expensive in our tests? which we could probably hack away at. I mean, you mentioned that some of the tests
> take ten minutes to run. That feels like something that we could probably get down. And I don't even know
> that we have even attempted to take an optimization pass on that particular set of tests, have we? can you
> do an audit and see if you are able to apply any of the lessons that we have used in our last several
> rounds of performance improvements? things like caching rather than recomputing every time or running on a
> smaller suite that does not have many thousands of polygons or things to overlap with. or running on way
> more random seeds than what we actually need in order to get decent test coverage. I don't know. Stuff
> like that. We've made a whole lot of performance improvements, and I feel like we should be able to apply
> the same techniques we already have to get that ten minutes down to something much, much more reasonable.
> So go ahead and open another feature for this and then start with an audit, and I will take acceptance as
> the final task of the feature because it is likely that I will add new tasks after your initial findings.
> Go ahead and see what you're able to do with this general direction first, and then I will take a look
> after you have taken a stab at it. Thanks.
