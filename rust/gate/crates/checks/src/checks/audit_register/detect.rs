//! What a delta adds that owes an audit entry (451 T259): read off two snapshots of the tree, the merge base and the tree as it stands
//! (or a commit, for the replay over past landings). Five kinds, each a test on paths or names, never on prose, because a check that
//! fires on correct work teaches a session to escape every check:
//!
//! - a GUARD MODULE: a file `rust/guard/src/guards/<name>_hooks.rs` or `_gate.rs` (or the same under `rust/guard/shared/src/guards/`)
//!   that git lists as added against the base - a rename (`git diff -M`) is no addition, and a submodule of a guard (`<name>_hooks/x.rs`)
//!   is its guard's own;
//! - a NUMERIC CONSTANT: a module-level `const NAME: <integer or float type> =` (at column 0, so a constant inside a function, an `impl`
//!   or an inline `#[cfg(test)]` module is not read) under `rust/guard/` or the gate's checks (`rust/gate/crates/checks/src/`), whose
//!   name reads as a threshold's or a knob's (`THRESHOLD_WORDS`, a unit's alone not) and is held by no such line anywhere in that scope at the base - a constant moved between files, or a file split by the
//!   1,000-line bar, adds no name; a test file (`tests.rs`, `*_tests.rs`, a `tests/` or `testkit` directory) is not read. Known miss: a
//!   new threshold whose name the scope already holds elsewhere is not seen;
//! - a MAKE TARGET newly in the gate or landing chain: a target reached from `CHAIN`'s roots through prerequisites and `$(MAKE) <target>`
//!   calls in recipes, transitively, in the Makefile as it stands and not at the base (a target wired into the chain counts, new or not);
//! - an AGENT FILE: `.claude/agents/<name>.md` added against the base;
//! - a LANDING STEP: a push check, a landing phase or a landing gate script newly named where `STEPS` says they are named.

use std::collections::{BTreeSet, VecDeque};
use std::path::Path;
use std::process::Command;

/// The gate and landing chain's roots: what every landing runs (`make land` -> `make done` -> `make quick`, `make static`,
/// `make hooks-test`; a builder's `make closing-checks`; `make land-tooling`, `make land-batch`).
pub(super) const CHAIN: [&str; 8] = [
    "done",
    "quick",
    "static",
    "hooks-test",
    "closing-checks",
    "land",
    "land-batch",
    "land-tooling",
];

/// The scope whose numeric constants are read: the guard, the gate's checks, and the landing's crates - the land crate, and the
/// cohort crate where the push's checks live, whose waits and polls cost every landing time (measured 2026-11-26, a grep of their
/// non-test files: 10 of their 17 module-level numeric names pass the word filter, each a knob - `CLAIMS_WAIT_S`, `COMMIT_TRIES`,
/// `HANDOFF_FRESH_S`, ...).
const CONST_SCOPE: [&str; 4] = [
    "rust/guard/",
    "rust/gate/crates/checks/src/",
    "rust/gate/crates/land/src/",
    "rust/gate/crates/cohort/src/",
];

/// The types a threshold constant is declared with: the integers, the floats and `Duration`.
const NUMERIC: [&str; 15] = [
    "u8", "u16", "u32", "u64", "u128", "usize", "i8", "i16", "i32", "i64", "i128", "isize", "f32",
    "f64", "Duration",
];

/// The words of a threshold's or a knob's name (one `_`-separated part of it is enough): measured 2026-11-25 over the 84 module-level
/// numeric constants of the scope's non-test files (55 kept), these keep the caps, floors, budgets, waits, ages, rounds and counts (`CAP_TOKENS`, `POLL_CHECK_S`,
/// `STATIC_RUNS_A_TASK`, `PLAN_ROUND_CAP`, `FREE_PCT`) and drop the display sizes and fixed facts (`LARGEST`, `SHOWN`, `CHUNK`,
/// `SIGTERM`, `DAY`): a miss is cheaper than a false fire.
const THRESHOLD_WORDS: [&str; 43] = [
    "CAP",
    "MAX",
    "MIN",
    "LIMIT",
    "CEILING",
    "FLOOR",
    "BUDGET",
    "THRESHOLD",
    "PCT",
    "PERCENT",
    "RATIO",
    "SLACK",
    "LEEWAY",
    "TIMEOUT",
    "WAIT",
    "IDLE",
    "STALE",
    "STALL",
    "AGE",
    "FRESH",
    "EVERY",
    "RETRIES",
    "TRIES",
    "ROUNDS",
    "ROUND",
    "S",
    "MS",
    "SECS",
    "SECONDS",
    "MINUTES",
    "HOURS",
    "DAYS",
    "GB",
    "MB",
    "BYTES",
    "TOKENS",
    "KEEP",
    "KEPT",
    "CHARS",
    "WORDS",
    "RUNS",
    "N",
    "BAR",
];

/// The words of a unit's name: a constant named by these alone (`GB`, `DAY_MICROS`, `SECONDS_A_DAY`) is a conversion, not a knob.
const UNIT_WORDS: [&str; 22] = [
    "A", "PER", "B", "KB", "MB", "GB", "TB", "NS", "MS", "S", "SECS", "SECOND", "SECONDS",
    "MINUTE", "MINUTES", "HOUR", "HOURS", "DAY", "DAYS", "WEEK", "MICROS", "NANOS",
];

/// Is `name` a threshold's or a knob's, by its words?
pub(super) fn is_threshold(name: &str) -> bool {
    let parts: Vec<&str> = name.split('_').collect();
    parts.iter().any(|p| THRESHOLD_WORDS.contains(p))
        && !parts.iter().all(|p| UNIT_WORDS.contains(p))
}

/// One thing the delta adds that owes an entry: its kind and the name an entry's `covers:` line gives it.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub(super) struct Item {
    pub(super) kind: &'static str,
    pub(super) name: String,
}

/// Where the delta's far end is read: the working tree (dirty and untracked files counted), or a commit (the replay).
pub(super) enum Head<'a> {
    Tree,
    Rev(&'a str),
}

fn git(root: &Path, args: &[&str]) -> String {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default()
}

/// Is `path` a guard module, as the module doc says?
pub(super) fn is_guard_module(path: &str) -> bool {
    let Some(file) = ["rust/guard/src/guards/", "rust/guard/shared/src/guards/"]
        .iter()
        .find_map(|dir| path.strip_prefix(dir))
    else {
        return false;
    };
    !file.contains('/') && (file.ends_with("_hooks.rs") || file.ends_with("_gate.rs"))
}

/// Does `name` end in `.md`, in any case?
pub(super) fn is_markdown(name: &str) -> bool {
    Path::new(name)
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("md"))
}

/// Is `path` an agent file?
pub(super) fn is_agent(path: &str) -> bool {
    path.strip_prefix(".claude/agents/")
        .is_some_and(|f| !f.contains('/') && is_markdown(f))
}

/// Is `path` a non-test Rust file of the constants' scope?
pub(super) fn in_const_scope(path: &str) -> bool {
    let tests = path
        .split('/')
        .any(|seg| seg == "tests" || seg == "testkit")
        || path.ends_with("/tests.rs")
        || path.ends_with("_tests.rs")
        || path.ends_with("/testkit.rs");
    Path::new(path)
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("rs"))
        && CONST_SCOPE.iter().any(|s| path.starts_with(s))
        && !tests
}

/// The NAME a line declares as a module-level numeric constant, or None.
pub(super) fn const_name(line: &str) -> Option<&str> {
    let mut rest = line;
    if let Some(after) = rest.strip_prefix("pub") {
        rest = match after.strip_prefix('(') {
            Some(vis) => vis.split_once(')')?.1,
            None => after,
        };
        rest = rest.strip_prefix(' ')?;
    }
    let rest = rest.strip_prefix("const ")?;
    let (name, ty) = rest.split_once(':')?;
    let name = name.trim();
    let ty = ty.split_once('=')?.0.trim();
    let upper = name.starts_with(|c: char| c.is_ascii_uppercase())
        && name
            .chars()
            .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_');
    (upper && NUMERIC.contains(&ty) && is_threshold(name)).then_some(name)
}

/// The names of `text`'s module-level numeric constants.
pub(super) fn const_names(text: &str) -> BTreeSet<String> {
    text.lines()
        .filter_map(const_name)
        .map(str::to_owned)
        .collect()
}

/// The targets a Makefile's rule lines define, and each one's edges: its prerequisites and the targets its recipe runs by `$(MAKE)`.
pub(super) fn make_graph(text: &str) -> Vec<(String, Vec<String>)> {
    let mut rules: Vec<(String, Vec<String>)> = Vec::new();
    let mut current: Vec<usize> = Vec::new();
    for line in text.lines() {
        if let Some(recipe) = line.strip_prefix('\t') {
            let called = make_calls(recipe);
            for &at in &current {
                rules[at].1.extend(called.iter().cloned());
            }
            continue;
        }
        if line.trim().is_empty() {
            continue;
        }
        current.clear();
        if line.starts_with('#') || line.starts_with(' ') {
            continue;
        }
        let Some((left, right)) = line.split_once(':') else {
            continue;
        };
        let names: Vec<&str> = left.split_whitespace().collect();
        let plain = |n: &&str| {
            !n.starts_with('.')
                && n.chars()
                    .all(|c| c.is_ascii_alphanumeric() || "_-".contains(c))
        };
        if names.is_empty()
            || !names.iter().all(plain)
            || right.starts_with('=')
            || right.starts_with(':')
        {
            continue;
        }
        let right = right.split_once("##").map_or(right, |(r, _)| r);
        let word = right.split_whitespace().next().unwrap_or_default();
        if right.contains('=') || ["export", "unexport", "override", "private"].contains(&word) {
            // a target-specific variable: no prerequisites, and no recipe follows it
            continue;
        }
        let prereqs: Vec<String> = right
            .split_whitespace()
            .filter(|w| !w.starts_with('$') && !w.starts_with('|'))
            .map(str::to_owned)
            .collect();
        for name in names {
            let at = rules
                .iter()
                .position(|(n, _)| n == name)
                .unwrap_or_else(|| {
                    rules.push((name.to_owned(), Vec::new()));
                    rules.len() - 1
                });
            rules[at].1.extend(prereqs.iter().cloned());
            current.push(at);
        }
    }
    rules
}

/// The targets a recipe line runs by `$(MAKE)`: the words after it up to a shell separator, its options and assignments passed over.
fn make_calls(recipe: &str) -> Vec<String> {
    let mut out = Vec::new();
    for (_, after) in recipe
        .match_indices("$(MAKE)")
        .map(|(at, m)| (at, &recipe[at + m.len()..]))
    {
        let end = after.find(|c| ";|&),".contains(c)).unwrap_or(after.len());
        for word in after[..end].split_whitespace() {
            if word.starts_with('-')
                || word.contains('=')
                || word.contains('$')
                || word.contains('"')
            {
                continue;
            }
            out.push(word.to_owned());
        }
    }
    out
}

/// Every target `CHAIN`'s roots reach in `text`, the roots among them.
pub(super) fn chain_reach(text: &str) -> BTreeSet<String> {
    let graph = make_graph(text);
    let mut seen: BTreeSet<String> = BTreeSet::new();
    let mut todo: VecDeque<String> = CHAIN.iter().map(|s| (*s).to_owned()).collect();
    while let Some(name) = todo.pop_front() {
        if !seen.insert(name.clone()) {
            continue;
        }
        for (_, edges) in graph.iter().filter(|(n, _)| *n == name) {
            todo.extend(edges.iter().cloned());
        }
    }
    let defined: BTreeSet<&str> = graph.iter().map(|(n, _)| n.as_str()).collect();
    seen.retain(|n| defined.contains(n.as_str()));
    seen
}

/// The paths `head` adds against `base` (renames not counted), of the guard modules and agent files.
fn added_paths(root: &Path, base: &str, head: &Head<'_>) -> Vec<String> {
    // `-M`: a renamed module is listed `R`, not `A`, so a rename adds nothing
    let mut args = vec!["diff", "-M", "--name-status", base];
    if let Head::Rev(rev) = head {
        args.push(rev);
    }
    args.extend(["--", "rust/guard", ".claude/agents"]);
    let mut added: Vec<String> = git(root, &args)
        .lines()
        .filter_map(|l| l.strip_prefix("A\t"))
        .map(str::to_owned)
        .collect();
    if let Head::Tree = head {
        added.extend(
            git(
                root,
                &[
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                    "--",
                    "rust/guard",
                    ".claude/agents",
                ],
            )
            .lines()
            .map(str::to_owned),
        );
    }
    added.retain(|p| is_guard_module(p) || is_agent(p));
    added
}

/// The module-level numeric constant names of the scope at `rev` (None: the working tree, untracked files too).
fn scope_consts(root: &Path, rev: Option<&str>) -> BTreeSet<String> {
    // `-h` drops the path, which the test-file filter needs: the scope's files are listed first and only the kept ones grepped
    let listed = match rev {
        Some(rev) => git(
            root,
            &[
                "ls-tree",
                "-r",
                "--name-only",
                rev,
                "--",
                CONST_SCOPE[0],
                CONST_SCOPE[1],
                CONST_SCOPE[2],
                CONST_SCOPE[3],
            ],
        ),
        None => git(
            root,
            &[
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                CONST_SCOPE[0],
                CONST_SCOPE[1],
                CONST_SCOPE[2],
                CONST_SCOPE[3],
            ],
        ),
    };
    let kept: Vec<&str> = listed
        .lines()
        .filter(|p| in_const_scope(p) && (rev.is_some() || root.join(p).is_file()))
        .collect();
    if kept.is_empty() {
        return BTreeSet::new();
    }
    let mut args = vec!["grep", "-h", "-I", "--no-color"];
    if rev.is_none() {
        args.push("--untracked");
    }
    args.extend(["-E", "^(pub(\\([^)]*\\))? )?const [A-Z][A-Z0-9_]*:"]);
    args.extend(rev);
    args.push("--");
    args.extend(kept);
    const_names(&git(root, &args))
}

/// `path` at `rev` (None: the working tree's).
fn file_at(root: &Path, rev: Option<&str>, path: &str) -> String {
    match rev {
        Some(rev) => git(root, &["show", &format!("{rev}:{path}")]),
        None => std::fs::read_to_string(root.join(path)).unwrap_or_default(),
    }
}

/// Where a landing's named steps are written, the text that opens a step's name there, and the kind: the push's checks table
/// (`Row("<name>"`), the landing's phases (`self.phase("<name>"`) and the gate scripts its first pass runs (`GATES`, every quoted name
/// on its line). A refusal `make land`'s first pass adds inside an existing step (`stops.push(...)`, 6 of them, observed 2026-11-26,
/// method: a grep of `land/cheap.rs`) carries no name, so it is not read.
const STEPS: [(&str, &str, &str); 3] = [
    (
        "rust/gate/crates/cohort/src/push.rs",
        "Row(\"",
        "push check",
    ),
    (
        "rust/gate/crates/land/src/land.rs",
        "self.phase(\"",
        "landing phase",
    ),
    (
        "rust/gate/crates/land/src/land/cheap.rs",
        "const GATES",
        "landing gate",
    ),
];

/// The step names `text` holds after `opener`: the name a quote-ended opener opens, or every quoted name on an opener's line.
pub(super) fn step_names(text: &str, opener: &str) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    for line in text.lines() {
        let Some((_, after)) = line.split_once(opener) else {
            continue;
        };
        let parts: Vec<&str> = after.split('"').collect();
        if opener.ends_with('"') {
            out.insert(parts[0].to_owned());
        } else {
            out.extend(parts.iter().skip(1).step_by(2).map(|n| (*n).to_owned()));
        }
    }
    out
}

/// Everything `head` adds against `base` that owes an entry, in order.
pub(super) fn items(root: &Path, base: &str, head: &Head<'_>) -> Vec<Item> {
    let rev = match head {
        Head::Tree => None,
        Head::Rev(r) => Some(*r),
    };
    let mut out: Vec<Item> = added_paths(root, base, head)
        .into_iter()
        .map(|p| Item {
            kind: if is_agent(&p) {
                "agent file"
            } else {
                "guard module"
            },
            name: p,
        })
        .collect();
    let before = scope_consts(root, Some(base));
    out.extend(scope_consts(root, rev).difference(&before).map(|n| Item {
        kind: "numeric constant",
        name: n.clone(),
    }));
    let before = chain_reach(&file_at(root, Some(base), "Makefile"));
    out.extend(
        chain_reach(&file_at(root, rev, "Makefile"))
            .difference(&before)
            .map(|n| Item {
                kind: "make target in the gate chain",
                name: format!("make {n}"),
            }),
    );
    for (path, opener, kind) in STEPS {
        let before = step_names(&file_at(root, Some(base), path), opener);
        out.extend(
            step_names(&file_at(root, rev, path), opener)
                .difference(&before)
                .map(|n| Item {
                    kind,
                    name: format!("{kind} {n}"),
                }),
        );
    }
    out.sort();
    out
}
