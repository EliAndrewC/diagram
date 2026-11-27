# The pre-warm keeps the small lane's keys (451 T367, T411)

Load this file when: weighing the pre-warm's lint passes (`L7R_PREWARM_LINT`) or a builder's first wide build after a handout.

**The tellings** (`tellings.py`, read-only, its output `tellings.txt`): the clone's event log from 2026-11-27T00:20Z (T347
landed) to 03:30:03Z (this tree's handout for T367), 14 handouts. In pool trees, a crate's FIRST test build after a handout was
told wide 28 times of 29; those 28 are 42% of the 67 test-build tellings told wide (the other 39: a crate rebuilt after a
dependency's edit, `rust/gate` most of all, which builds on every gate crate). A lint's passes are told since T355 (about 01:53Z):
of a crate's first lint after a handout, 4 of 9 pass tellings were wide, the 5 alone standing on a key the tree's previous task
left.

**The waits it could save, measured in the same window, are small.** 13 `slot-wait` lines, 283.5 s: one, 4.0 s, in a first test
build after a handout; none in a lint since T355; the other 279.5 s in later builds and lints of a tree (mostly
`rust/gate/crates/reviews` at 01:49 to 02:00, while a gate ran). A wait needs both wide slots held, so how much the first builds
wait is the load's; the fix removes the wide slot from them whatever the load.

**The hand run** (`demo.txt`): the pre-warm on this tree with the new code (`rust/guard`, `rust/gate/crates/rustc`, `rust/gate`
moved since the handout's base) took 23.7 s of wall: 3.0 s of test builds (warmed already at the handout), then the lint passes,
17.3 s (`rust/guard` 6.1 + 0.5, `rustc` 1.5 + 0.5, `rust/gate` 7.6 + 1.1; the clippy units of `rust/guard` and `rust/gate` last
built by the tree's previous task, `rustc`'s by this builder's own lint before one code edit). The `make builder-checks` after it:
the test build `slot-tell 0` and `slot-small 0` (0.13 s), each lint pass the same, the lint 0.3 s.
