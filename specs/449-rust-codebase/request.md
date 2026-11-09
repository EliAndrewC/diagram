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
