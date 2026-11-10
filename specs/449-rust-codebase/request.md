# Feature 449 - the GM's request, verbatim

## 2026-11-07

Asked during feature 444 T36 (the gate's wall time), after the session measured where a one-line Rust edit's `make done` spends
its time, the hooks' cost per tool call, and what a port to Rust would and would not change:

"So while I don't think we need to port the Python code to Rusts that runs in hooks, because startup time for hooks is just generally more important.  How much would that affect this?"

"Wouldn't the hooks being in Rust also make the hook tests run faster?"

"I think what we're finding is that our Python code is just to inefficient and should probably all be ported to Rust, so I think I want to just move forward with that, making this a Rust codebase instead of a Python codebase."

The GM, 2026-11-09, on a stuck background check: "I thought we had tooling to prevent a stuck command from blocking us from doing work for that amount of time."

The GM, 2026-11-09: "I don't think we need to port the past feature harnesses if those are not still used."

The GM, 2026-11-09: "Let's delete rather than port our tooling which runs our tests remotely on AWS."

2026-11-10, on the Python unit tests:

"Okay, well, how about this: Since we are getting rid of all the Python code anyway, what if we just deleted all of the Python unit tests now? And then if literally any of our tests or gates required that to work, we can edit them to no longer run unit tests on any of the Python stuff. I mean, after all, we know that the Python stuff works and we are no longer changing it. Except insofar as we are deleting it. So we should theoretically be able to just delete every unit test now. And then that will help ensure that our older, slower tests are not slowing down our development iteration loop."

"Yes delete everything except that group, please."

"and then: which of our static checks are static checks on the python code which can also go away now?"

"Sounds good, please proceed with that, thanks."
