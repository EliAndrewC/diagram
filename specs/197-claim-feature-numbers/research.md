# Research - 197 Claim feature numbers under a lock

Both entries are `research: rendering` - measurements of this repository's own history and tooling,
nothing about how a place was built.

## R2 - The collision census: how often did two sessions claim one number?

Measured 2026-09-07 on main's history (`git log --diff-filter=A -- 'specs/*/spec.md'`, the number
taken off each added path, `sort | uniq -d`; renames from `git log --diff-filter=R --name-status -- specs/`).

**Fourteen numbers have been claimed by two features at some point**: 134, 136, 139, 144, 146, 147,
148, 152, 154, 158, 161, 182, 191, 195. One is still a collision on main today: **195**
(`195-cite-only-what-can-be-read`, claimed `f2083d5e4`; `195-target-descriptions-and-two-removals`,
claimed `0bfc26c01`; both 2026-09-06).

The others were resolved by the loser renumbering - which is the cost the GM named. The renumber
commits since the protocol was written down (2026-08-16), with their own descriptions of what happened:

| date | commit | what it says |
|---|---|---|
| 2026-08-29 | `f3799dfab` | 155: renumber this session's feature 152 -> 155 (the peer's claim landed first) |
| 2026-08-29 | `d10cb7b79` | 156: ... and the renumber to 156 |
| 2026-08-30 | `84ca0bf79` | 162: renumber - specs/161 was claimed in main by another session |
| 2026-08-30 | `ba228aeee` | 166: renumber from the duplicate 164 - two peers claimed 164 and 165 mid-flight |
| 2026-09-05 | `8d78ebe5c` | 182: renumber - 181 was claimed by a peer session between sync-in and push |
| 2026-09-05 | (same feature) | 182 -> 184 (`R100 specs/182-make-target-naming-audit -> specs/184-...`) - **renumbered twice** |
| 2026-09-05 | `640f72da9` | 186: renumbered from 184 (another session's 184 landed concurrently) |
| 2026-09-06 | `82618327a` | 191 -> 194: renumbered after a concurrent session's 191 landed |

So the "claim at specify, renumber on collision" protocol did what it promised - collisions were
found - and cost a renumber roughly every other day, once twice on one feature, and it still let one
through (195), because the check happens at the PUSH and both 195s were pushed as claims within a
window where neither pull saw the other.

**Why the old protocol could not do better.** Its one source was main's `specs/` after `sync-in`. An
unpushed claim in a sibling clone was invisible by construction - it exists only in
`<mirror>/.clones/<other>/specs/` until that session pushes. The tool reads exactly that directory
(spec.md, source 3), which is the whole of the difference.

## R1 - The concurrency proof

(Filled in by T03: the twelve-process test with the lock in place, and the same test run once with the
flock lines removed, with the duplicate count it produced.)
