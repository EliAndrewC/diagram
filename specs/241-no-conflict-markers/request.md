# The GM's request, verbatim

Raised after the second incident of the night, while the 227/237 landing was still being worked
(2026-09-13):

> Please proceed with the fix. After you've made the fix, let's talk about a tooling fix for the
> `git add -A` issue that keeps happening.

Then, on being given the diagnosis - that `add -A` is not wrong in general, but is never right while a
merge is unresolved, and that the state is exactly detectable:

> Okay. Based on your explanation, then I would say that you should go ahead and implement that concrete
> proposal for the git add -A problem. I mean, go ahead and land your current round of changes on main
> before you've implemented. But then after that, yes. Please go ahead and implement what you are
> describing and then land that on main as well. Thanks.

And after the landing, when the session announced the claim instead of making it:

> You just said you were claiming it, but then didn't do anything. So please actually claim it and then
> implement the feature and then land it back in main. Thanks.
