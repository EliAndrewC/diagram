# `make diff-run` - the shared differential runner

Load this file when: you write or run a port's differential (FR-002's same outputs), or a plan states a differential's case count.

Feature 449 T161 (the GM's approved proposal of 2026-11-16, the differentials rerunning only what a fix touched, enforced by tooling as
his 2026-11-11 words ask; `specs/449-rust-codebase/request.md`). Every port task's comparison runs through `l7r-gate diff-run` (crate
`rust/gate/crates/diffrun/`), not a hand-written driver loop: it runs each case on both sides, compares, keeps each side's result, and
after a fix reruns only the sides whose key moved.

```
make diff-run CASES=<cases file>                      # incremental: only the sides whose key moved or that have no result
make diff-run CASES=<cases file> ONLY="<case name>"   # one case, its new side rerun
make diff-run CASES=<cases file> TWICE=1              # the old side run twice: run-to-run noise the normalizations miss
make diff-run CASES=<cases file> VERIFY=1             # every new side rerun against the kept old sides: the figures a plan cites
make diff-run CASES=<cases file> ALL=1 REASON="..."   # every side of every case; the reason goes in the report and the guard log
```

Exit 0 when every case is the same, 1 when one differs, fails to run or shows noise, 2 when the run is refused (a bad cases file, a
declared path that does not exist, a failed build, `--all` without a reason). Each case's line goes to stderr as it finishes; the summary
(the differing cases with their differences, sides rerun and kept, normalizations taken, wall time, the report's path) to stdout.

## The keys

- **Old side**: the world's definition, the old side's, the case's (its `sources` left out), the normalizations that apply to it, the
  content of every declared input (`world.inputs` and the case's `inputs`), and the old side's `fingerprint`. A fix to the port moves
  none of these, so the old side's result is kept across every rerun.
- **New side**: the same with the new side's definition and, in place of its whole `fingerprint`, the content of the case's declared
  `sources`; a case that declares none is keyed on the whole new fingerprint.
- A declared path that does not exist refuses the run (its hash would never move). A failed setup or a timeout keeps nothing.
- Both keys carry the runner's result format (`"v"` in `keys.rs`): a runner change that changes what a kept result holds raises it.
- A declaration can be too narrow, so the figures a plan reports come from `VERIFY=1`, whose report path carries `diff-run-verify`.
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
    "setup": [["python3", "-I", "{ROOT}/setup.py", "{WORLD}", "{REV}"]],
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

- `world.setup` runs into a fresh, empty `{WORLD}` for every case and side (from `root`), so a kept result never depends on which cases ran
  before it; the world is removed after its outputs are read. What a world needs beyond that (a network namespace, a loopback server, a
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

Beside `<dir>/<stem>.json`, `<dir>/<stem>.diff-run/`: `results/<case id>.old.json` and `.new.json` (each side's kept result and its key),
`reports/diff-run-<kind>-<UTC>.json` (`incremental`, `only`, `twice`, `verify`, `all`; only a verify run's path carries `diff-run-verify`;
`--verify` takes no `--only`), and `work/old`, `work/new` while a side runs. The report holds the run's kind, the reason, cases total, sides
rerun and kept, the differing cases, the normalizations taken, the wall time, and one row a case: its differences, its noise, its errors,
and each side's key, whether it reran, and its time.
