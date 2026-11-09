# The iteration switches (feature 132; the scope axis retired in feature 185, the remote axis in feature 449)

**Load this when:** you are about to throw or release a switch.

## What they are

Committed, repository-wide switches in one tracked file, `dev/switches.json`:

| axis | states | what it governs | throw / release |
|---|---|---|---|
| **claims** | `report` (default) / `clean` | whether an open claims finding refuses a landing | `make claims-clean REASON=...` / `make claims-report-only REASON=...` |
| **port** | `rust-only` (default) / `integrated` | whether the Python stages run beside the Rust ones | `make port-integrated REASON=...` / `make port-rust-only REASON=...` |

`make switches` prints them, with the reason, who threw each and when. The history is the file's git log - each target commits its
own change.

**A REASON IS REQUIRED and there is no override.** A switch is a tracked file, so throwing it is a diff someone reads: *"a reason
someone will READ is a decision you have to defend."*

**A MALFORMED FILE FAILS CLOSED** - claims at `clean`, the port at its last committed state, with `MALFORMED` in the description.

**AN UNKNOWN KEY IS IGNORED, and that is load-bearing:** a clone from before an axis was retired still carries its block, and it is
simply not looked at.

## Do not reinstate the scope axis, and keep `idle_context`

The **scope** axis was retired by feature 185 (GM 2026-09-05: *"please go ahead and retire the concept of the scope lock and the
scope unlock, i.e. retiring both the concept and the specific make targets"*). Do not bring back a piece of it in isolation.

**`switches.idle_context` STAYS**, though it looks like part of the lock. The Makefile's `DONE_NAME` picks `idle-done` over `done` from
it, and the green targets deliberately omit `idle-done`: that omission is how an unattended idle gate **neither grants nor revokes a
push**.

`mapcheck`'s own `--scope auto|reference|all` and the `SCOPE=` make variable also stay: they are its breadth argument, not the retired
axis.
