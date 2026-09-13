# The GM's request, verbatim (2026-09-12)

On researching the problem:

> Okay. Yeah. Go ahead and go deep on researching if there's a good way to do that. I mean, I guess,
> worst case scenario, we could stop using xdist and instead just have, like, ten different test
> suites, but then I don't know how we would balance them by time and whatnot. You know? So that
> doesn't seem like a good solution. But surely we cannot be the only people running into this
> problem. So there must be some kind of solution. So, yeah, see if you could figure something out and
> tell me what you come up with in terms of proposals. Thanks.

On what to build, after the proposals were priced:

> Yes. Please do proposals one and two as part of the same spec kit feature, and I agree that we should
> not touch the worker count. Thanks. However, do not actually implement the spec kit feature yet. Just
> design it because before you start, there's another piece that I think is probably worth doing. If I
> had to guess, then I would say that the reason why our tests, which we are collecting, are taking up
> so much RAM is probably that we have quite a lot of test fixtures, which are currently implemented in
> Python code, which is to say that the test module itself is maybe defining a giant dictionary or some
> other global data structure, which represents the various maps which are being tested. Am I correct
> about that? Because if so, then it sounds like we could save a tremendous amount of RAM if we move to
> those global variables, or they might not even be global variables. They might just be fixed or
> functions. But either way, they are Python code that gets imported. And if we move those into
> something like JSON data files, then that would mean that the modules themselves get much, much
> smaller. and I would guess that many, many megabytes, probably hundreds of megabytes if I had to
> guess of our tests, would suddenly go away because in addition to not collecting tests that we are
> not going to run, which is good and we're... should still do that. But in addition to that, we would
> be not loading those data structures into memory unless the tests actually run.

On the deferred-import item, and on the part the first scan could have missed:

> Yes. We should include the deferred import Item with this feature.
>
> One last thing, though. It may be the case that module level imports are not contributing to the
> size in that way, but what about fixtures that return a constant? ... that would not show up on your
> scan that you did, but would still very much be contributing to the problem that I am describing.
> Because when the module is imported, then that function would be imported, which means that it would
> add to the memory. Right? ... One way that you could probably do this reasonably efficiently without
> just reading every file is by looking at the size of every function because extremely large functions
> are probably an indicator that that function is abnormal in some way. And if you have a function
> whose code is a megabyte long, then that is probably a function with an enormous data structure
> inside of it. Perhaps a pytest fixture which is returning one. I am prepared to believe that I am
> wrong about all of this and that maybe all of our functions are just individually small, and we
> simply have lots of them. However, it is not normal for unit tests to take this much RAM without the
> kind of pattern that I am describing, at least not in my experience.

On the shapely item, and on taking the feature to the end:

> That's really good to know, thanks. Yes. Please do the shapely lazy accessor per module thing. You
> can add that to this spec kit feature, then go ahead and begin work on the spec kit feature. Take the
> spec kit feature from start to finish. and then land it back in the main checkout in the normal way
> when you are completely done. Thanks.

## What "proposal one" and "proposal two" were

The GM's "Please do proposals one and two" answers a numbered list put to them in the session. The two
they approved, as they were worded to them:

> **1. Restrict the run's paths to what the incremental plan will actually run.** This is the one lever
> that cuts collection rather than filtering after it, and it is fully supported - paths and node ids
> restrict the walk before import, and since every worker gets the controller's argv verbatim their
> collections stay identical, so the protocol is satisfied. Worth up to 566 of the 922 MiB, on every
> incremental gate, which is most gates. The module set can be derived from the plan alone with nothing
> circular: `tests.json` already holds every test's fixture closure from the last full run, and git
> gives the changed test modules. A new test cannot escape, because adding one changes its module. One
> cost to pay deliberately: the baseline is written only on full runs, which already run everything.
>
> **2. Stop pinning the collected items** (`ci/selection.py:215`). `remember_all` keeps every `Item`
> alive on every worker so the baseline can see the deselected ones, when all it needs is
> `{nodeid: fixture_ids(it)}`. Small, correct on its own, and it is what makes deselection actually
> free memory - so it belongs with 1.

The third item, "the deferred import Item", was put to them as: *"the 820 MiB above collection"* aside,
**"the only other thing in the collection budget that is ours rather than CPython's"** - one module
parsing the whole tree's AST at import time and one heavyweight library import, about 13 MiB per worker.
