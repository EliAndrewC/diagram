//! What a delta adds that owes an audit entry (451 T259): read off two snapshots of the tree, the merge base and the tree as it stands
//! (or a commit, for the replay over past landings). Five kinds, each a test on paths or names, never on prose, because a check that
//! fires on correct work teaches a session to escape every check:
//!
//! - a GUARD MODULE: a file `rust/guard/src/guards/<name>_hooks.rs` or `_gate.rs` (or the same under `rust/guard/shared/src/guards/`)
//!   that git lists as added against the base - a rename (`git diff -M`) is no addition, and a submodule of a guard (`<name>_hooks/x.rs`)
//!   is its guard's own;
//! - a NUMERIC CONSTANT: a module-level `const NAME: <integer or float type> =` (at column 0, so a constant inside a function, an `impl`
//!   or an inline `#[cfg(test)]` module is not read) in the tooling (`CONST_SCOPE`: the guard, the gate, the browser, the embedder), whose
//!   name reads as a threshold's or a knob's (`THRESHOLD_WORDS`, a unit's alone not) and is held by no such line anywhere in that scope at the base - a constant moved between files, or a file split by the
//!   1,000-line bar, adds no name; a test file (`tests.rs`, `*_tests.rs`, a `tests/` or `testkit` directory) is not read. Known miss: a
//!   new threshold whose name the scope already holds elsewhere is not seen;
//! - a MAKE TARGET newly in the gate or landing chain: a target reached from `CHAIN`'s roots through prerequisites and `$(MAKE) <target>`
//!   calls in recipes, transitively, in the Makefile as it stands and not at the base (a target wired into the chain counts, new or not);
//! - an AGENT FILE: `.claude/agents/<name>.md` added against the base;
//! - a LANDING STEP: a push check, a landing phase or a landing gate script newly named where `STEPS` says they are named, or a
//!   landing refusal, `make land`'s unnamed `stops.push(` calls - its first pass's and, before it, `land/unfinished.rs`'s (451 T292) -
//!   by their count (`REFUSALS`), or a LANDING SCRIPT: a
//!   `scripts/<path>.<ext>` newly written in a landing recipe (`LANDING_TARGETS`' recipes in the Makefile, the Makefile variables they
//!   expand, and the push's own scripts, `LANDING_SCRIPTS`) - a new callee is a landing step (451 T269: T258's `scripts/state-sync.sh`,
//!   called from `make land`'s recipe, landed with no entry asked). New is by name over all of them together, so a call moved from a
//!   recipe into the push script adds nothing. Known misses: a script a called script calls in its turn, a script reached by a path
//!   not written `scripts/...` (`"$(dirname "$0")/x.sh"`), and what `l7r-gate land` runs (its gates are `STEPS`'). Known false fire: a
//!   script the landing's scripts newly NAME without calling it (a message's `run scripts/x.sh`) reads as called, where nothing of
//!   them named it before - none in the replay over the last 40 landings (2026-11-26).

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

/// The scope whose numeric constants are read: the tooling - the guard, every gate crate, the browser and the embedder - whose
/// waits, caps, retries and bundle sizes cost a session time or tokens (measured 2026-11-26, a grep of the gate's crates beyond
/// checks, land and cohort: 68 more names pass the word filter, among them the run lock's `CEILING_S` and `MUTEX_S`, `LOCK_WAIT_S`,
/// `IDLE_S`, `BUNDLE_TOKENS`, `TRIAGE_SKIP_MAX`; the browser's 4 are its waits). The engine's crates (`rust/mode_a`, `rust/phases`,
/// `rust/parked`) are not read: their 64 passing names are drawing rules (`MIN_TURN_DEG`, `GATE_MAX_FT`), held by the research claims
/// and `make tunables`, not process costs.
const CONST_SCOPE: [&str; 4] = ["rust/guard/", "rust/gate/", "rust/browser/", "rust/embed/"];

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

/// The targets a rule line names and what follows its colon (its help cut), or None: a comment, an indented line, an assignment
/// and a target-specific variable (no prerequisites, and no recipe follows it) are no rule line.
fn rule(line: &str) -> Option<(Vec<&str>, &str)> {
    if line.starts_with('#') || line.starts_with(' ') {
        return None;
    }
    let (left, right) = line.split_once(':')?;
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
        return None;
    }
    let right = right.split_once("##").map_or(right, |(r, _)| r);
    let word = right.split_whitespace().next().unwrap_or_default();
    (!right.contains('=') && !["export", "unexport", "override", "private"].contains(&word))
        .then_some((names, right))
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
        let Some((names, right)) = rule(line) else {
            continue;
        };
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
/// on its line). A refusal `make land`'s first pass adds inside an existing step carries no name, so `REFUSALS` counts them.
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

/// The landing's unnamed refusals: `make land`'s first pass refuses through `stops.push(` in `land/cheap.rs`, each call one refusal
/// with no name of its own, so they are counted - the k-th is the item `landing refusal land/cheap.rs #k`, and a delta that raises
/// the count adds the new numbers (measured 2026-11-26, the count at each of the last 21 landings on main: 6 every time, so the count
/// moves only when a refusal is added or removed).
///
/// And the refusals BEFORE that pass (451 T292): `land/unfinished.rs` refuses an unfinished carry-over ahead of the landing alone and
/// the first pass, through the same call, so its file is counted the same way - the check read `cheap.rs` alone, and T292's refusal
/// would have landed asking no entry.
const REFUSALS: ([&str; 2], &str) = (
    [
        "rust/gate/crates/land/src/land/cheap.rs",
        "rust/gate/crates/land/src/land/unfinished.rs",
    ],
    "stops.push(",
);

/// The refusal items `head` adds: the numbers past the base's count up to the head's.
pub(super) fn refusal_items(file: &str, before: &str, after: &str) -> Vec<Item> {
    let call = REFUSALS.1;
    (before.matches(call).count() + 1..=after.matches(call).count())
        .map(|k| Item {
            kind: "landing refusal",
            name: format!("landing refusal {file} #{k}"),
        })
        .collect()
}

/// The make targets whose recipes are a landing: what they call is a landing step.
const LANDING_TARGETS: [&str; 3] = ["land", "land-batch", "land-tooling"];

/// The push's own scripts, read whole: what `make land-tooling`'s recipe runs, and the push every landing ends with.
const LANDING_SCRIPTS: [&str; 2] = ["scripts/land-tooling.sh", "scripts/sync-with-main.sh"];

/// The recipe lines of `LANDING_TARGETS` in a Makefile, with the value of each Makefile variable they expand (`$(LAND_RUN)`), and of
/// each those expand in turn, after them.
pub(super) fn landing_recipes(makefile: &str) -> String {
    let (mut text, mut vars) = (String::new(), Vec::new());
    let (mut landing, mut held): (bool, Option<&str>) = (false, None);
    for line in makefile.lines() {
        if let Some(name) = held {
            // a variable's value carried over a `\`-ended line
            vars.push((name, line));
            held = line.ends_with('\\').then_some(name);
        } else if let Some(recipe) = line.strip_prefix('\t') {
            if landing {
                text.push_str(recipe);
                text.push('\n');
            }
        } else if !line.trim().is_empty() {
            // as `make_graph` reads it: a blank line keeps the rule, any other line that is no rule's ends it
            landing = rule(line)
                .is_some_and(|(names, _)| names.iter().any(|n| LANDING_TARGETS.contains(n)));
            if let Some((name, value)) = line.split_once('=') {
                let name = name.trim_end_matches([' ', ':', '?', '+']);
                vars.push((name, value));
                held = line.ends_with('\\').then_some(name);
            }
        }
    }
    let (mut seen, mut from) = (BTreeSet::new(), 0);
    while let Some(at) = text[from..].find("$(") {
        from += at + 2;
        let name: String = text[from..]
            .chars()
            .take_while(|c| c.is_ascii_alphanumeric() || *c == '_')
            .collect();
        if text[from + name.len()..].starts_with(')') && seen.insert(name.clone()) {
            for (_, value) in vars.iter().filter(|(n, _)| *n == name) {
                text.push_str(value);
                text.push('\n');
            }
        }
    }
    text
}

/// The scripts `text` names: each `scripts/<path>` that ends in a file's extension, a `#` line's not read (a glob, a directory and
/// a path with a variable in it, `scripts/gates/$g.sh`, name no one script).
pub(super) fn script_names(text: &str) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    for line in text.lines().filter(|l| !l.trim_start().starts_with('#')) {
        for (at, _) in line.match_indices("scripts/") {
            let path = &line[at..];
            let end = path
                .find(|c: char| !(c.is_ascii_alphanumeric() || "_./-".contains(c)))
                .unwrap_or(path.len());
            let path = path[..end].trim_end_matches('.');
            if !path.ends_with('/') && Path::new(path).extension().is_some() {
                out.insert(path.to_owned());
            }
        }
    }
    out
}

/// The scripts the landing's recipes and the push's scripts name at `rev` (None: the working tree).
fn landing_scripts(root: &Path, rev: Option<&str>) -> BTreeSet<String> {
    let mut text = landing_recipes(&file_at(root, rev, "Makefile"));
    for path in LANDING_SCRIPTS {
        text.push_str(&file_at(root, rev, path));
        text.push('\n');
    }
    script_names(&text)
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
    for path in REFUSALS.0 {
        let file = path.rsplit_once("/src/").map_or(path, |(_, f)| f);
        out.extend(refusal_items(
            file,
            &file_at(root, Some(base), path),
            &file_at(root, rev, path),
        ));
    }
    let before = landing_scripts(root, Some(base));
    out.extend(
        landing_scripts(root, rev)
            .difference(&before)
            .map(|n| Item {
                kind: "landing script",
                name: format!("landing script {n}"),
            }),
    );
    out.sort();
    out
}
