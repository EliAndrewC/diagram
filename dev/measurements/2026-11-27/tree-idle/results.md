# Do builders wait on the second tier? Pool trees' idle minutes, 2026-11-26T17:00Z to 2026-11-27T01:00Z

Asked by the GM, 2026-11-27, on `make task-time`'s figure of 123.3 blocking minutes for the second tier over this window (its
report says to expect near zero): "if our tooling indicates that we have spent over 2 hours blocking on the second tier then
that's a HUGE problem, either with our measurements or with our process, and we should get to the botom of that ASAP."

Method (`tree-idle.py`, read-only; its output is beside this file): each builder the coordinating session dispatched is tied to
its pool tree by the tree's path in its brief (the session's transcript: 98 builders) and to its first start and last stop in
the 451 event log; a tree is BUSY from a builder's first start to its last stop (so a builder stopped on its own plan review
counts as busy), and IDLE otherwise. Each idle 10 seconds is classed by what the session was doing: a landing running (the
`Phase` lines of `make land`, 19 runs, 119 minutes), else the session in its own turn (between a prompt or notice and its
Stop), else the session stopped. Measured once; the classes overlap in cause (a landing runs in the background of a turn).

| tree | minutes of the window | busy | idle |
|---|---|---|---|
| diagram-backlog-t269 | 480 | 401 | 79 |
| diagram-backlog-t270 | 480 | 373 | 107 |
| diagram-backlog-t271 | 480 | 330 | 150 |
| the three warm trees | 1440 | 1104 | 336 (23%) |
| diagram-backlog-b1 (made 20:39, the fourth) | 261 | 117 | 144 |

The three warm trees' idle minutes, by what the session was doing (gaps of 3 minutes or more, 321 of the 336):

| the session | idle tree-minutes |
|---|---|
| in its own turn (committing, carrying, resolving a carry's conflicts, repairing a red gate, writing a brief or a reply) | 170 |
| a landing running | 105 |
| stopped, its turn ended (waiting on a notice or the GM) | 46 |

What it shows. The report's figure is loosely defined (27.6 of its 123.3 minutes are booked as waiting on the GM), but what it
points at is real: the trees stood idle 23% of the window, and nothing in the queue was short. The cause is the ORDER the
session works a builder's end in - commit, carry, resolve, check, land, and only then brief the next builder - so a tree waits
on the whole second tier and on the session's turns, though nothing requires it to: `make carry` takes `COMMIT=`, so a tree
can be freed and handed out again as soon as its builder's work is committed. The longest gaps are the three trees idle
together from 22:01 to 22:28 (a red gate, two hand-resolved carries and a hung test: 74 tree-minutes) and t271 from 23:44
(40 minutes). At the window's median of about 37 builder minutes a task, 336 idle tree-minutes is about nine tasks.

Not measured: how much of the 170 minutes is each activity (the carry's hand resolutions, 451 T300; a red gate's repair; the
briefs; the replies to the GM); a tree idle because its task's next builder (a closing half) waited on the session is counted
the same as one idle between tasks.
