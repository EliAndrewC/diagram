# `tests/soak/` - the tier ABOVE the gate

**This directory is the home of the tests that roll MORE than the gate strictly needs** (constitution VI v2.23.0, GM 2026-09-08,
feature 216: *"the correct place for the kind of test in which we make more map rolls than are strictly necessary is in the AWS
tests. or the CI tests"*). It is declared and EMPTY: its Python tests went with the Python engine, and `make soak`, which ran them
under pytest, left with pytest (feature 449 T213). Its rules and history before that are in git history.

The gate proves the code is *exercised*; the soak asks whether it holds up under REALISTIC LOAD - the same generator over many
seeds, the same assertions on larger maps, cost and termination under load, invariants that only mean something in bulk.

**The membership rule**: a test belongs here if removing it does not change coverage. A test that reaches a line nothing else
reaches is misfiled and belongs at the gate.

**What a soak run can NEVER catch** (GM 2026-09-05): *"many of the failure cases on random seeds are things like a village lane
meeting the criteria but then looking wrong"*. That is the GM's eye, or the `settlement-review` agent.

When the tier earns a test again, it is a Rust test with a make target of its own that refuses on an empty suite rather than
report a vacuous green.
