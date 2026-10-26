# Research: Faster landings

## R1 - Did today's `cover-changed` miss the coverage reds? (FR-003a)

- **Finding** (`m:coverage-reds-replay`): of today's 6 coverage reds, the 5 that name lines name 8 lines, and all 8 are EXISTING
  lines that lost their coverage - a test or caller deleted with its pass, or code moved behind a new branch - none added. The
  sixth was the gate not counting new tests marked `tooling`, which `cover-changed`'s run counted.
- **So**: `cover-changed` asks only the lines a change ADDS, by design (its docstring), so it could see none of the five; and it
  runs a different selection from the floor's. FR-003's check therefore asks EVERY line of each changed module (not only added
  lines) with the tests the gate's floor counts for it.
