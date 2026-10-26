# Research: Faster landings

## R1 - Did today's `cover-changed` miss the coverage reds? (FR-003a)

- **Finding** (`m:coverage-reds-replay`): of today's 6 coverage reds, the 5 that name lines name 8 lines, and all 8 are EXISTING
  lines that lost their coverage - a test or caller deleted with its pass, or code moved behind a new branch - none added. The
  sixth was the gate not counting new tests marked `tooling`, which `cover-changed`'s run counted.
- **Which modules** (same key, re-run by `bash specs/430-faster-landings/replay-reds.sh`): THREE of the five name lines in a module
  their delta changed (31f739f5d, d92ff2c90, 39ea51383); TWO name a module their delta did not touch - 7f209090b `law.py:933`
  (its delta changed the modules that called it) and 449e7df7b `checks.py:141` (its delta deleted the field spur that reached it).
- **So**: `cover-changed` asks only the lines a change ADDS, by design (its docstring), so it could see none of the five; and it
  runs a different selection from the floor's. FR-003's check asks EVERY line of each changed module (the GM's "on the changed
  modules") with the tests the gate's floor counts for it: it catches three of the five line-naming reds and the sixth. The two
  whose lost line sits in an unchanged module stay the gate's to catch - the narrowing FR-009 asks stated, at a price of 2 of
  today's 6 reds (one 4-5 minute gate each).
