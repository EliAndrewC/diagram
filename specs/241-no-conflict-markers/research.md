# Research - feature 241, no conflict markers

## R1 - the two incidents, both in one day

| | when | how it happened | what it cost | what caught it |
|---|---|---|---|---|
| 1 | 2026-09-12, morning | a conflicted merge, `git add -A`, commit | `pool/hamlets/kuwabata/kuwabata.json` committed with markers | `make notes-census` could not PARSE the file - an accident |
| 2 | 2026-09-13, ~02:00 | the same, merging main's feature 230 into the 227/237 clone | **23 files** committed with markers: six engine modules, five test modules, five manifests, five notes files, two research pages | the gate's lint phase, after the commit |

The second one is the measurement that matters. The merge had to be redone from the merge base, because
the markers were already in a commit and the history here is never rewritten; the resolution that followed
took about an hour of a session that had already been working for eight.

**The shape is identical both times and it is not "`add -A` is wrong".** Resolving every file and then
running `git add -A` is the normal, correct end of a merge. What both incidents share is that `add -A`
says NOTHING about what it swept up, so a file still holding `<<<<<<<` goes in silently.

## R2 - why the state-based rule is the wrong rule

The obvious guard is "refuse `git add -A` while `.git/MERGE_HEAD` exists". It would have caught both
incidents and it is still wrong:

- **it fires on correct work.** The end of every resolved merge is exactly `git add -A` with MERGE_HEAD
  still present. A guard that refuses the correct command teaches a session to pattern-match past every
  guard, which this project's own doctrine names as the more expensive failure (CLAUDE.md, "Deliberately
  NOT enforced").
- **it misses the marker that arrives another way** - a `git am`, a patch script, a marker typed into a
  file by hand. Incident 2's 23 files came from a merge; nothing says the next one will.
- **and it cannot tell the difference** between a session that resolved everything and one that resolved
  nothing, which is the only distinction that matters.

## R3 - the rule: CONTENT, not state

**A `git add` or `git commit` that would stage a file containing a conflict TRIPLE is refused.** A triple
is a `<<<<<<<` line, a later `=======` line, and a later `>>>>>>>` line, each at the start of a line - the
shape `git merge` leaves, not any one of its parts.

- **precise**: it describes the harm rather than a state that correlates with it;
- **silent on correct work**: a resolved merge has no markers, so the normal `add -A` passes untouched;
- **complete**: it catches the marker however it arrived;
- **cheap**: one read per path the command would actually stage.

### What it must not fire on

A file that TALKS about conflict markers - this research page, the guard's own suite, a doc about merges.
The same "match invocations not mentions" problem every guard here has. Two answers, both needed: a marker
inside a fenced or indented block is prose, not a conflict; and the escape `CONFLICT_MARKERS_OK="<reason>"`
for the file that carries one on purpose.

### The backstop

A guard can be escaped, and a marker can arrive by a route no hook sees - including a commit made outside
this session. So a gate phase scans every TRACKED file and fails, the way
`tests/tooling/test_makefile_recipe_comments.py` backstops the recipe-comment guard. That is what turns
incident 2 from "lint fails somewhere downstream" into a named, specific failure naming the files.
