---
kind: adopted
title: the builders' queue is a file code reads, and a free pool tree is not left idle
for: a pool tree freed by a builder's end goes to the queue's next task without the session remembering to hand it out, because the queue is a file whose every state is computed, make builder-done and make builder-next name the next entry with its command, and a Stop over a free tree and a READY entry is refused
measured: 2026-11-27
measurement: dev/measurements/2026-11-27/tree-idle/results.md - the three warm pool trees idle 336 of 1,440 tree-minutes (23%) of 2026-11-26T17:00Z to 2026-11-27T01:00Z with the queue never short: 170 with the session in its own turn, 105 with a landing running, 46 with the session stopped. The BEFORE figure only: the mechanism is not yet measured running - the after-measurement over a like window is 451 T401's
command: python3 dev/measurements/2026-11-27/tree-idle/tree-idle.py (the table again); bash tests/hooks/test-pool-idle-hooks.sh (28 cases; of its then 26, 9 measured to fail with the guard's holding branch removed and 2 with tasks-done.md unread, and 1 of the 28 with another feature's queue.txt hiding this one, 2026-11-27); make rust-test CRATE=rust/guard/shared (builder_queue::tests) and CRATE=rust/gate/crates/task (builder_queue::tests, builder_done::tests); make guard-log GUARD=pool-idle (its blocks and escapes); make queue; make builder-next
falsifier: the tree-idle table re-measured over a like window (eight hours, three warm trees, the queue never short; 451 T401) not falling; or the share of the coordinating session's Stops escaped (POOL_IDLE_OK lines of make guard-log GUARD=pool-idle against the day's Stops) passing the threshold - the sign that the block is answered and not acted on, which is what retired 451 T88's Stop block (T183: 23 turns spent only answering such blocks)
threshold: GUESS knobs, both: the three warm trees idle more than 15% of such a window (23% before), or POOL_IDLE_OK on more than 1 Stop in 5 of a day (either reopens it); L7R_BUILDERS (3) is a GUESS knob
cost: one read of the clone's pool registry at every Stop of a session with a clone, and where a tree is free under the count one read of each queue, its tasks.md, the pool's log and one git for-each-ref; a Stop refused until the session dispatches or writes the escape's line; one line of queue.txt kept by hand for each dispatch, which stays until its task is landed
last-audited: 2026-11-27
cadence-days: 7
covers: rust/guard/src/guards/pool_idle_hooks.rs
covers: rust/guard/shared/src/builder_queue.rs
covers: L7R_BUILDERS
---

451 T313, with T395 and the first half of T297 (`rust/guard/shared/src/builder_queue.rs`, `rust/gate/crates/task/src/builder_queue.rs`,
`rust/guard/src/guards/pool_idle_hooks.rs`). The GM, 2026-11-26: "what you are doing sounds like something that we want our tooling
to actually enforce. Because otherwise you just have to remember to keep our tasks in flight". The queue is
`specs/<feature>/queue.txt`, one entry a line (a dispatch: its tasks, its kind, its crates and files, what it waits on); `make queue`
lists it with each state computed - landed, built, in flight, waiting, READY; `make builder-next` and `make builder-done`'s first
step name the next READY entry (performance work first, FR-013) that overlaps no task holding a tree, with its `make builder-brief` command; and the coordinating
session's Stop is refused while a pool tree stands free, fewer than `L7R_BUILDERS` trees are held and such an entry exists.

Weighed and not taken: tab-separated columns or a fenced block of `queue.md` (a tab cannot be seen and a short row reads as another
row; a fence in prose breaks with the prose - the reasons are at the head of `builder_queue.rs`); a typed state column (a state
somebody types goes stale, as `queue.md`'s "LANDED" and "In flight" did within hours); holding back on an in-flight task the queue
does not list (its files are unknown, so it is named `not checked` and holds nothing - holding on it would idle the pool for every
task dispatched outside the queue); the guard asking the gate's binary (it reads the shared module in process: no build, no
process, nothing to time out at a Stop).

Accepted limitations, chosen by the builder (451 T313's build half) for the reviewer to weigh: (1) BUILT BY COUNT, the build half's choice, misfired two
ways (the plan review's round 1): two `make builder-done` runs for one entry (a builder at its cap and its successor) ended the
task's next entry undispatched, and one run ending two entries (a kept tree's build and closing halves) left the second READY.
Rebuilt after that round (it was to be 451 T416): `make builder-next` prints `ENTRY=<k>`, the entry's ordinal among its first
task's lines; `make builder-brief` logs it on a `brief` line beside the take; `make builder-done` writes the tree's last named
entry since its take on its `done` line; an entry is built when a done line names it or a later entry of its tasks. A done line
naming none counts as before - the larger of the two, not their sum, so a successor briefed by hand without `ENTRY=` re-offers an
entry (seen) rather than skip one (unseen). Removing a line before its task lands renames the entries after it: the header of
every queue.txt says a line stays. (2) "carried" is the done ref being gone, so a carry finished by hand reads as waiting until the next
`make builder-done` clears the ref. (3) this reverses 451 T183's retirement of T88's Stop block (D10, on the GM's "does nothing and
adds nothing to the context if we are still active"): T313's words are later; the block is one short message naming one command.

The rule is deliberately thin (the closing half, 2026-11-27): the GM is weighing whether the primary session becomes a pure
orchestrator, so the guard holds no state and reads nothing of its own - everything it judges is `shared::builder_queue::idle`,
and where the coordination moves the rule moves with the queue. Its block says the escape STARTS a line of the final message
(after a bullet or in backticks the token is not taken); both wordings passed message-check on 2026-11-27. The count
`L7R_BUILDERS` (3) is the pool's three warm trees as run on 2026-11-26, a GUESS knob beside `docs/process-decisions.md`'s "Two
code builders at once" (decided there as "to be re-measured" at three and four once the warm pool and the build slot were in):
the guard keeps a count, it does not settle one, and a session holding the count lower exports `L7R_BUILDERS` or writes the
escape. Unbuilt of T313's line: the second tier's gate proposed at trial 458's threshold (451 T415).

A `queue.txt` that cannot be read hides no other (the closing half, 2026-11-27, a defect a test showed): features 269 and 280 hold
a page session's file of that name in another form, and the first version of the rule stopped at the first unreadable queue in
directory order, so in the live clone the guard could never have reached feature 451's queue. The walk now goes on past it, and
the unread queue is recorded only where no queue has an entry to hand out. `make queue` and `make builder-next` with no `F=`
still stop at the first such file (451 T418); with `F=` or `SPECIFY_FEATURE` they read the one queue.
