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
The same "match invocations not mentions" problem every guard here has. The answer is COLUMN 0: git writes
each marker at the start of a line, so an indented example and every inline marker in a backtick span are
already excluded by the rule itself, and this page, the spec and the suite all pass unflagged. A file that
must carry a real triple at column 0 declares `CONFLICT_MARKERS_OK: <reason>` in its first 40 lines, and
the command escape `CONFLICT_MARKERS_OK="<reason>"` covers the one-off.

### The backstop

A guard can be escaped, and a marker can arrive by a route no hook sees - including a commit made outside
this session. So a gate phase scans every TRACKED file and fails, the way
`tests/tooling/test_makefile_recipe_comments.py` backstops the recipe-comment guard. That is what turns
incident 2 from "lint fails somewhere downstream" into a named, specific failure naming the files.

## R4 - three things the first implementation got wrong: two found by its review, one by its own audit listing

Recorded because each was a plausible decision that a reader would otherwise make again.

**1. A fenced block was exempted, and that exemption would have passed 7 of the 23 files.** The reasoning
was sound as far as it went - a doc showing a conflict puts it in a fence - and it is wrong about git: a
merge writes its markers at column 0 wherever the conflict falls, and a conflict inside a Markdown file's
fenced block looks exactly like a conflict shown as an example. Of incident 2's 23 files, 7 were Markdown
or HTML. The exemption was removed and replaced with the file-level `CONFLICT_MARKERS_OK: <reason>` marker,
which is argued rather than inferred; the suite now asserts BOTH halves - a fenced triple is flagged, and
the same file passes once it declares the marker.

**2. The guard enumerated git's pathspecs itself, and so missed the incident it was built for.** The first
`staged_by()` read the command for `-A`, `.` and explicit paths and asked `git status` about the tree. Two
defects, measured against the corpus:

| shape | first implementation | why |
|---|---|---|
| `CL=<clone>; git -C $CL add -A` - **the recorded incident** | rc=0, permitted | no `VAR=` expansion, and the hook's cheap bail-out filter demanded the literal substring `git add`, which this command does not contain |
| `git add .` in a clean subdirectory, a marker elsewhere in the tree | would have refused | `.` is scoped to the cwd; the enumeration asked about the whole tree |

The second is the worse one: it fires on correct work, which is the failure this design exists to avoid.
Both are gone because the question is now asked of git - `git add --dry-run --ignore-missing` with the
command's own arguments, in the tree the command's `cd`s, `-C` and `VAR=` assignments resolve to. Feature
204's `_hm_tree.py judge` walks the same ground for the same reason, and was the model.

**3. The file-level exemption exempted the detector itself, and the listing is what found it.** The
exemption was first read as `CONFLICT_MARKERS_OK:` appearing anywhere in a file's first 40 lines. The
`make audit` listing was added so a carve-out could be enumerated (feature 173's reason), and its very
first run printed one file: `scripts/_hm_conflict.py`, whose docstring describes the marker in a backtick
span with a `<reason>` placeholder. So the one file whose entire job is to tell a mention from an
invocation had silently exempted itself from its own backstop. A declaration now has to stand at the
START of its line - modulo indentation and comment punctuation, the way `check-file-scale.py` reads
`FILE_SIZE_OK` - and a placeholder reason is documentation rather than a declaration. The listing prints
zero files, which is the number this feature ships with, and three selftest cases hold the distinction.

This is the third time in this one feature that the defect was "a mention counted as an invocation", and
it is the project's oldest guard lesson (CLAUDE.md, "When you add a guard"). The pattern worth carrying
forward: the thing that caught it was making the carve-out ENUMERABLE, not reading the code again.

## R5 - why the backstop runs at the PUSH as well as at the gate

`check-file-scale.py` and `spec-lint.py` both run in the skill Makefile's `static` phase AND in
`sync-with-main.sh` at push time, each for a stated reason: their delta takes the DIRECT route and runs no
gate at all. This check has the strongest version of that claim. The delta that lands a marker is a MERGE,
and a merge's content is whatever the two sides touched - of incident 2's 23 files, 15 were manifests,
notes and research pages, and a landing of only those paths dispatches no build and runs no gate. The gate
phase is where a finding arrives cheaply, before the map roll is paid for; the push is where it is
unavoidable. Both call `--selftest` first, like every static check in that block: a checker that cannot
fail is worth nothing.
