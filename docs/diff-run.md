# `make diff-run` - the shared differential runner

Load this file when: you write or run a port's differential (what moved, FR-002's signal), or a plan states a differential's case count.

Feature 449 T161 (the GM's approved proposal of 2026-11-16, the differentials rerunning only what a fix touched, enforced by tooling as
his 2026-11-11 words ask; `specs/449-rust-codebase/request.md`). Every port task's comparison runs through `l7r-gate diff-run` (crate
`rust/gate/crates/diffrun/`), not a hand-written driver loop: it runs each case on both sides, compares, keeps each side's result, and
after a fix reruns only the sides whose key moved.

**A difference is a signal, not a bar** (feature 449 T180, the GM 2026-11-18, constitution XIII: *"remove any references to things
needing to be bitwise identical or anything like that as an exactness standard"*). The run exits 1 when any case differs; that
exit says something moved, which the session reads for whether everything still works - the tests pass, the callers get their
job done, the research claims hold, the audit checks give the same verdicts. A port whose differences keep all of that lands
with them named in its record; no difference is by itself a refusal, a new ask or a reason to copy the old side's bytes. FR-001c
still reads a differential with no difference as one condition of a straight task (no per-task review); a task with differences
gets its review, which judges them by the same rule.

```
make diff-run CASES=<cases file>                      # incremental: only the sides whose key moved or that have no result
make diff-run CASES=<cases file> ONLY="<case name>"   # one case, its new side rerun
make diff-run CASES=<cases file> TWICE=1              # the old side run twice: run-to-run noise the normalizations miss
make diff-run CASES=<cases file> VERIFY=1             # every new side rerun on whole worlds: the figures a plan cites
make diff-run CASES=<cases file> ALL=1 REASON="..."   # every side of every case; the reason goes in the report and the guard log
make diff-run CASES=<cases file> ... JOBS=4           # any of the above, its owed sides on 4 workers (`--jobs 4`)
```

Exit 0 when every case is the same, 1 when one differs, fails to run or shows noise, 2 when the run is refused (a bad cases file, a
declared path that does not exist, a failed build, `--all` without a reason, a `JOBS` that is not a whole number 1 or more). Each case's
line goes to stderr as it finishes, in the cases' order; the summary (the differing cases with their differences, sides rerun and kept,
normalizations taken, wall time, the report's path) to stdout.

## Several workers (`JOBS=n`)

Feature 449 T173: T170's verify run took 392.6 s wall for 105 cases whose sides' own commands summed to 11.6 s; the rest was each side's
world - a whole checkout, the setup, two snapshots, the removal - about 1.8 s a side, 210 sides one after another. `JOBS=n` runs the owed
sides (the ones not kept) on n workers, clamped to their count; the default, 1, is the run as it always was. The builds still run once,
before any case. The kept results, the keys, the report and its case order, the printed lines and their order, and every error are a
serial run's: the main thread builds each case's row once it and every case before it are done, and an error that names a worker's
world names `work/<side>` as a serial run would. Measured on T170's 105 cases, every side rerun (a fresh state, `VERIFY=1`, whole worlds,
22 cores, 2026-11-17): 375.8 s at JOBS=1, 220.5 s at 2, **151.5 s at 4**, 162.2 s at 6, 181.6 s at 8, each report's 105 cases agreeing
with the serial one's, kept results and lines too. Past 4 the workers contend (a guess: the checkouts' writes, the host's load stayed under 10 of 22) - the sides' own commands summed 11.2 s at 1,
17.7 s at 4, 30.0 s at 8 - so JOBS=4 is the figure to use on this host until a world costs less to build (one run each; 4 against 6 within what the load between runs could move, 4 against 8 not).

**When JOBS is safe**: the runner's own worlds are distinct (`work/<side>-<worker>`), so a cases file is safe on several workers when its
setup and steps write only inside `{WORLD}` - their guard log, their scratch, their output all under it. A harness that writes a fixed
path outside its world (a file under `{ROOT}`, a shared cache it rebuilds, a port it listens on) has two sides writing it at once: it stays
serial, or moves that path under `{WORLD}`. Reading outside the world (the repository, a binary built once by `build`) is safe. Each
world is a full checkout where the file declares one (about 252 MB for this repository); since T179 each worker keeps one a side for
the run with its `.git` copy, so n workers hold 2n of them on disk at once.

## The keys

- **Old side**: the world's definition, the old side's, the case's (its `sources` left out), the normalizations that apply to it, the
  content of every declared input (`world.inputs` and the case's `inputs`), and the old side's `fingerprint`. A fix to the port moves
  none of these, so the old side's result is kept across every rerun.
- **New side**: the same with the new side's definition and, in place of its whole `fingerprint`, the content of the case's declared
  `sources`; a case that declares none is keyed on the whole new fingerprint.
- A declared path that does not exist refuses the run (its hash would never move). A failed setup or a timeout keeps nothing.
- Both keys carry the runner's result format (`"v"` in `keys.rs`): a runner change that changes what a kept result holds raises it.
- A declaration can be too narrow, so the figures a plan reports come from `VERIFY=1`, whose report path carries `diff-run-verify`.
- Where `world.checkout.sparse` is declared, both keys also name the worlds the run builds - sparse or whole (feature 449 T169) - so no
  side kept from a sparse world stands in a `VERIFY=1` or `ALL=1` run, whose worlds are always whole, nor the reverse.
  `make decide` refuses a sentence stating a differential's case count (`cases` with a figure, beside `differential` or `same outputs`)
  that cites no `diff-run-verify...json` path.

## The cases file (JSON)

Every path is relative to `root` (default: the cases file's directory). `{NAME}` is filled from `vars`, the side's `vars`, and
`{WORLD}` (the case's fresh world directory), `{SIDE}` (`old` / `new`) and `{ROOT}`; a step argument that is exactly `{CMD}` becomes
the side's `cmd`. Each process gets the runner's environment less make's own variables (`MAKEFLAGS`, `MAKELEVEL`, `MFLAGS`,
`MAKEOVERRIDES`, so a run through `make diff-run` behaves as one from the shell) and `env_drop_prefixes`, then `world.env`, the side's `env` and the case's
`env` (`null` unsets), plus `DIFF_RUN_WORLD` and `DIFF_RUN_SIDE`.

```json
{
  "vars": {"C": "{WORLD}/clone"},
  "world": {
    "checkout": {"repo": "/diagram/.clones/x", "rev": "{REV}", "into": "clone", "sparse": ["docs", "l7r", "scripts"]},
    "setup": [["python3", "-I", "{ROOT}/fixtures.py", "{WORLD}"]],
    "cwd": "{C}", "wrap": ["{ROOT}/ns.sh"],
    "files": ["clone/research/archive", "home", "server.log"], "ignore": [".git"],
    "extras": [{"name": "log remote", "cmd": ["git", "-C", "{WORLD}/remote.git", "log", "--format=%s"]},
               {"name": "server", "path": "{WORLD}/server.log"}],
    "env": {"L7R_GATE_STALE_OK": "1"}, "env_drop_prefixes": ["L7R_"],
    "timeout_s": 900, "max_text_bytes": 5000000, "inputs": ["setup.py", "pages"]
  },
  "sides": {
    "old": {"label": "py", "cmd": ["python3", "{ROOT}/old_tool.py"], "vars": {"REV": "<old sha>"},
            "fingerprint": [{"git": "/diagram/.clones/x", "rev": "<old sha>"}]},
    "new": {"label": "rs", "cmd": ["scripts/gates/l7r-gate.sh", "record", "archive"], "vars": {"REV": "<new sha>"},
            "build": [["sh", "-c", "env -u L7R_GATE_STALE_OK /diagram/.clones/x/scripts/gates/l7r-gate.sh --version"]],
            "fingerprint": ["/diagram/.clones/x/rust/gate", "/diagram/.clones/x/rust/guard"]}
  },
  "normalizations": [
    {"name": "stamp", "regex": "\\d{8}T\\d{6}Z", "replace": "<stamp>"},
    {"name": "server-log-sorted", "sort": "\\n", "on": ["files"], "where": "^server\\.log$"},
    {"name": "sorted-stdout", "sort": "\\n", "on": ["stdout"], "opt_in": true}
  ],
  "cases": [
    {"name": "url direct", "steps": [["{CMD}", "url", "http://www.site-a.test/p/p10.html"]],
     "sources": ["/diagram/.clones/x/rust/gate/crates/archive"], "inputs": ["pages/p10.html"]},
    {"name": "set up mid-case", "env": {"GM": "0"}, "norms": ["sorted-stdout"], "files": ["home"],
     "steps": [["{CMD}", "report"], {"argv": ["bash", "-c", "mkdir -p {WORLD}/gm"], "compare": false}, ["{CMD}", "report"]]}
  ]
}
```

- `world.checkout` (feature 449 T169), when given, is made first: `repo` cloned (`--shared`) into `{WORLD}/<into>` at `rev`. `rev`
  `WORKTREE` is the repository's `HEAD` with its uncommitted changes and untracked, unignored files laid over it (a port's new side before
  it is committed). `sparse` limits the clone to the named paths - git's cone: each named directory whole, plus the files directly in the
  root and in each named directory's ancestors - FOR ITERATING ONLY: an incremental, `ONLY=` or `TWICE=1` run builds sparse worlds, and a
  `VERIFY=1` or `ALL=1` run ALWAYS builds whole ones, the list ignored, its report and summary saying `worlds: whole`. WHY: a list too
  narrow for what a case reads fails both sides alike, which the comparison reads as agreement - a false pass in the comparison FR-002
  reads (T169's plan review) - so the figures a plan cites, a verify's, are never built on a sparse world. The cost is the verify's. On
  T168's 76 cases: an incremental run on sparse worlds 50.0 s; the first `VERIFY=1` after it 265.6 s, both sides of every case rerun on
  whole worlds; a second `VERIFY=1` 131.5 s, the old sides kept from the first (observed 2026-11-17, feature 449 T169, `make diff-run` on
  T168's harness; every whole-world result equal to a whole checkout's by T168's own setup). With a checkout, `setup` may be empty; given,
  it runs after, over the clone. A `WORKTREE` world's content is keyed only through the new side's `fingerprint` and `sources`, so declare
  there what the cases exercise.
- `world.setup` runs into a fresh, empty `{WORLD}` for every case and side (from `root`), so a kept result never depends on which cases ran
  before it; the world is removed after its outputs are read. A WHOLE world's checkout is the one thing kept between cases (feature 449
  T179, `reuse.rs`): each worker makes it once a run for each side and, before each later case, resets it to what a fresh one is - the
  world outside the checkout emptied, the checkout's `.git` put back from a copy taken when it was made (its index with its time), `git
  read-tree -u --reset HEAD`, `git clean -ffdx`, the working tree laid again for `WORKTREE`, every path's mode put back - then runs the
  setup again; it is removed at the run's end. A test holds a reset world equal to a fresh one (every path, its bytes and mode, the
  index, HEAD, refs and `git status`) after cases that write, delete, add untracked and ignored files, change modes and kinds, stage,
  commit, stash and write under `.git/`. A moved ref of the repository, a changed checkout or `GIT_` variable, or a reset step that fails
  makes the world anew; sparse worlds are always fresh. `--fresh-worlds` (on `l7r-gate diff-run`) turns the reuse off.
  WHY: a whole world's checkout of 27,770 files took 1.25-1.33 s and its removal 0.27-0.30 s of a side's 1.6 s; a reset 0.1-0.2 s.
  Measured on T174's and T175's harnesses (`VERIFY=1 JOBS=4` from an empty state, one binary, fresh and reused alternating, the host's
  load 0.8-5 of 22 cores, 2026-11-18): T174's 113 cases 152.4 s fresh, 51.0 s reused; T175's 207 cases 376.1 s fresh, 164.5 s reused -
  every report's rows the same as the run's earlier verify. What a world needs beyond that (a network namespace, a loopback server, a
  bare remote) is the setup script's and `wrap`'s, which the runner runs and, through `inputs`, keys.
- Compared: each step's exit, stdout and stderr (a step with `"compare": false` runs unrecorded), every file under `files` (default the
  whole world; `ignore` names directories skipped) that the steps created, changed or deleted, and each `extras` entry (a file anywhere,
  or a command's stdout, read before and after) as `<name>`. A file that is not UTF-8 compares as `<bytes N sha>`, a text past
  `max_text_bytes` as `<text N sha>`.
- A side's `build` commands run once a run, before anything is keyed: they make its binaries current, since the new key reads sources and
  the result comes from a binary. Keep them cheap when nothing changed.
- Normalizations apply in order after the world's path becomes `<WORLD>`: `regex` + `replace` (default `<name>`), or `sort` (the text split
  at the separator regex, the pieces sorted); `on` limits them to `stdout`, `stderr`, `files`, `names`; `where` to files whose raw name
  matches; `opt_in` to the cases naming them in `norms`. Names that meet after normalization are numbered (`#2`) in their raw order and the
  report lists `name-rank`. The report lists each normalization that changed something, by the number of cases.

## The state directory

Beside `<dir>/<stem>.json`, `<dir>/<stem>.diff-run/`: `results/<case id>.old.json` and `.new.json` (each side's kept result and its
key; a whole world's `.old.whole.json` and `.new.whole.json` where a sparse list is declared),
`reports/diff-run-<kind>-<UTC>.json` (`incremental`, `only`, `twice`, `verify`, `all`; only a verify run's path carries `diff-run-verify`;
`--verify` takes no `--only`), and `work/old`, `work/new` while a side runs (`work/old-<w>`, `work/new-<w>`, each worker's own, on a run of
several workers; a whole world's checkout, with its `.git` copy `work/<side>[-<w>].git`, for the whole run, T179). The report holds the run's kind, the reason, cases total, sides
rerun and kept, the differing cases, the normalizations taken, the worlds (`whole` or `sparse`), the wall time, and one row a case:
its differences, its noise, its errors,
and each side's key, whether it reran, and its time.
