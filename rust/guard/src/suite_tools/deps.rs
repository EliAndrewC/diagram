//! `l7r-guard deps` (feature 449 T050, the port of `tests/hooks/hookdeps.py`, feature 172): what each guard suite and each Python test of `scripts/` depends on,
//! derived transitively. The failure that matters is UNDER-running: a derivation that misses a dependency skips a suite a change has broken and reports green,
//! while over-running is merely slow, so every doubtful edge here counts as a dependency.
//!
//! A reference is a file NAME standing in another file's CODE: comments and docstrings are mentions, not dependencies (every guard says "detection lives in X" in
//! prose, which made every guard depend on every helper). A Python import never writes the extension, so a stem counts where it is imported.
//!
//! `sync-with-main.sh` alone is held to the whole tree: its suite resolves script paths at run time from trees its fixtures build, an edge no static reader
//! follows. A suite that reads the whole scripts directory derives to it by its own code (`globs_tree`), matched as the code writes it, not as prose describes it.

use std::cell::RefCell;
use std::collections::{BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::rc::Rc;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::agent_prefix_hooks::lines_kept;
use crate::protocol::Reply;
use crate::shared::sha256;
use crate::shared::tool::ask;
use crate::suite_tools::pylex;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

const HELD_WHOLE_TREE: &str = "sync-with-main.sh";
/// A suite that drives `l7r-guard` tests the binary built from these (feature 449 T004), which the name index over scripts/ and tests/hooks/ never sees.
const RUST_GUARD: [&str; 4] = [
    "rust/guard",
    "rust/gate",
    "rust/Cargo.toml",
    "rust/Cargo.lock",
];

static GLOB_TUPLE: LazyLock<Regex> =
    LazyLock::new(|| re(r#""scripts"\s*,\s*\(\s*"\*\.sh"\s*,\s*"\*\.py""#));
// A test that builds a script path at run time, or names the scripts directory as a path's end, depends on all of it (feature 375 amendment 3).
static BUILDS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#""scripts"\s*/\s*[A-Za-z_(]|join\([^)]*"scripts"\s*,\s*[A-Za-z_]|f"[^"]*scripts/\{|\{[^}]*\}/scripts|"scripts"\s*,\s*\(\s*"\*"#,
    )
});
static NAMES_DIR: LazyLock<Regex> = LazyLock::new(|| re(r#"(?m)"scripts"\s*(?:\)|,|\]|$)"#));
static TESTS_IMPORT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\s*(?:from|import)\s+(tests(?:\.\w+)+)"));

fn walk_into(dir: &Path, deep: bool, keep: &dyn Fn(&str) -> bool, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if entry.file_type().is_ok_and(|t| t.is_dir()) {
            if deep {
                walk_into(&path, deep, keep, out);
            }
        } else if keep(&entry.file_name().to_string_lossy()) {
            out.push(path);
        }
    }
}

fn every_file(under: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    walk_into(under, true, &|_| true, &mut out);
    out.sort();
    out
}

/// `_strip`: the file with its comments and, for Python, its docstrings removed.
fn strip(name: &str, raw: &str) -> String {
    let plain = |l: &str| {
        l.trim_end_matches([
            '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\u{85}', '\u{2028}', '\u{2029}',
        ])
        .to_owned()
    };
    let lines: Vec<String> = lines_kept(raw).into_iter().map(plain).collect();
    let dropped = if suffix(name) == "py" {
        pylex::read(raw)
            .map(|f| f.docstring_lines)
            .unwrap_or_default()
    } else {
        BTreeSet::new()
    };
    let kept = lines
        .iter()
        .enumerate()
        .filter(|(i, _)| !dropped.contains(&(i + 1)))
        .map(|(_, l)| l);
    let code = kept
        .filter(|l| !l.trim_start().starts_with('#'))
        .map(|l| l.split(" #").next().unwrap_or_default());
    code.collect::<Vec<_>>().join("\n")
}

fn suffix(name: &str) -> &str {
    name.rsplit_once('.').map_or("", |(_, e)| e)
}

fn suite_of(guard: &str) -> String {
    format!(
        "test-{}",
        guard
            .strip_suffix(".py")
            .map_or_else(|| guard.to_owned(), |g| format!("{g}.sh"))
    )
}

/// The tree a derivation reads, its name index built once.
pub struct Tree {
    root: PathBuf,
    here: PathBuf,
    scripts: PathBuf,
    index: Vec<(String, PathBuf)>,
    paths: HashMap<String, PathBuf>,
    shared: Vec<String>,
    imports: Regex,
    texts: RefCell<HashMap<String, Rc<str>>>,
}

impl Tree {
    /// The index over `scripts/` and `tests/hooks/` at `root`: every basename is unique across both, so a name identifies one file.
    #[must_use]
    pub fn at(root: &Path) -> Self {
        let root = root.canonicalize().unwrap_or_else(|_| root.to_path_buf());
        let (here, scripts) = (root.join("tests/hooks"), root.join("scripts"));
        let mut files = Vec::new();
        walk_into(
            &scripts,
            true,
            &|n| suffix(n) == "sh" || suffix(n) == "py" || suffix(n) == "txt",
            &mut files,
        );
        walk_into(
            &here,
            false,
            &|n| suffix(n) == "sh" || suffix(n) == "py",
            &mut files,
        );
        files.retain(|p| !p.components().any(|c| c.as_os_str() == "__pycache__"));
        files.sort();
        let name_of = |p: &PathBuf| {
            p.file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default()
        };
        // A name kept twice (a forwarder under scripts/hooks/ and its suite's link) keeps its first place and its last path, as the dict this was did.
        let named: Vec<(String, PathBuf)> = files.iter().map(|p| (name_of(p), p.clone())).collect();
        let paths: HashMap<String, PathBuf> = named.iter().cloned().collect();
        let mut seen = HashSet::new();
        let index: Vec<(String, PathBuf)> = named
            .iter()
            .filter(|(n, _)| seen.insert(n.clone()))
            .map(|(n, _)| (n.clone(), paths[n].clone()))
            .collect();
        let helper = |(n, p): &(String, PathBuf)| {
            let parent = p.parent().unwrap_or(p);
            parent != scripts
                && parent != scripts.join("hooks")
                && !n.starts_with("test-")
                && !n.ends_with("-gate.sh")
        };
        let mut shared: BTreeSet<String> = index
            .iter()
            .filter(|e| helper(e))
            .map(|(n, _)| n.clone())
            .collect();
        // `patch.py`, a top-level command the list named too, left with its port to `l7r-gate patch` (feature 449 T135)
        shared.extend(["hookrun.sh".to_owned()]);
        let shared: Vec<String> = shared.into_iter().collect();
        let mut stems: Vec<String> = shared
            .iter()
            .filter_map(|h| h.strip_suffix(".py"))
            .map(|s| fancy_regex::escape(s).into_owned())
            .collect();
        stems.sort_by_key(|s| std::cmp::Reverse(s.len()));
        let imports = re(&format!(
            r"(?:^|\n)\s*(?:from|import)\s+({})\b",
            stems.join("|")
        ));
        Self {
            root,
            here,
            scripts,
            index,
            paths,
            shared,
            imports,
            texts: RefCell::new(HashMap::new()),
        }
    }

    fn text(&self, name: &str) -> Rc<str> {
        if let Some(t) = self.texts.borrow().get(name) {
            return Rc::clone(t);
        }
        let path = self
            .paths
            .get(name)
            .cloned()
            .unwrap_or_else(|| self.here.join(name));
        let text: Rc<str> = std::fs::read_to_string(path).unwrap_or_default().into();
        self.texts
            .borrow_mut()
            .insert(name.to_owned(), Rc::clone(&text));
        text
    }

    fn code(&self, name: &str) -> String {
        strip(name, &self.text(name))
    }

    fn globs_tree(&self, name: &str) -> bool {
        let code = self.code(name);
        let body = if code.is_empty() {
            self.text(name).to_string()
        } else {
            code
        };
        body.contains("scripts/*.sh") || body.contains("scripts/*.py") || found(&GLOB_TUPLE, &body)
    }

    /// The shared helpers `body` references, itself excluded.
    fn refs(&self, name: &str, body: &str) -> Vec<String> {
        let imported: HashSet<&str> = self
            .imports
            .captures_iter(body)
            .flatten()
            .filter_map(|c| c.get(1))
            .map(|m| m.as_str())
            .collect();
        let wanted = |h: &&String| {
            h.as_str() != name
                && (body.contains(h.as_str())
                    || h.strip_suffix(".py").is_some_and(|s| imported.contains(s)))
        };
        self.shared.iter().filter(wanted).cloned().collect()
    }

    /// Every shared helper reachable from `seeds`, through helpers: a dependency reached only through another helper still counts.
    fn closure(&self, seeds: Vec<String>) -> BTreeSet<String> {
        let (mut seen, mut stack) = (BTreeSet::new(), seeds);
        while let Some(name) = stack.pop() {
            if seen.insert(name.clone()) {
                stack.extend(
                    self.refs(&name, &self.code(&name))
                        .into_iter()
                        .filter(|h| !seen.contains(h)),
                );
            }
        }
        seen
    }

    /// The names whose contents are this suite's freshness key, sorted for a stable hash.
    #[must_use]
    pub fn deps_for(&self, guard: &str) -> Vec<String> {
        let suite = suite_of(guard);
        if guard == HELD_WHOLE_TREE || self.globs_tree(guard) || self.globs_tree(&suite) {
            let all: BTreeSet<String> = self.index.iter().map(|(n, _)| n.clone()).collect();
            return all.into_iter().collect();
        }
        self.closure(vec![guard.to_owned(), suite])
            .into_iter()
            .collect()
    }

    fn rust_inputs(&self, guard: &str) -> Vec<PathBuf> {
        let words = format!("{}{}", self.text(guard), self.text(&suite_of(guard)));
        if !words.contains("l7r-guard") && !words.contains("l7r-gate") {
            return Vec::new();
        }
        let mut found: Vec<PathBuf> = RUST_GUARD
            .iter()
            .flat_map(|r| {
                let at = self.root.join(r);
                if at.is_file() {
                    vec![at]
                } else {
                    every_file(&at)
                }
            })
            .filter(|q| q.is_file())
            .collect();
        found.sort();
        found
    }

    /// The suite's key: its dependencies' bytes in `deps_for` order, a missing one skipped, then the Rust sources; sha256's first 16 hex digits.
    #[must_use]
    pub fn key_for(&self, guard: &str) -> String {
        let mut data = Vec::new();
        for name in self.deps_for(guard) {
            if let Some(path) = self.paths.get(&name).filter(|p| p.is_file()) {
                data.extend(std::fs::read(path).unwrap_or_default());
            }
        }
        for path in self.rust_inputs(guard) {
            data.extend(std::fs::read(path).unwrap_or_default());
        }
        sha256::hex(&data)[..16].to_owned()
    }

    fn rel(&self, path: &Path) -> String {
        path.strip_prefix(&self.root)
            .unwrap_or(path)
            .to_string_lossy()
            .into_owned()
    }

    /// The indexed files `body` reaches: a Python file what it imports and what a string constant of its code names (equal to a file's stem, or ending in its
    /// name), any other file every name standing in it. A prose string that merely mentions a file reaches nothing.
    fn word_refs(&self, name: &str, body: &str) -> BTreeSet<String> {
        let by_mention = || {
            self.index
                .iter()
                .filter(|(n, _)| n != name && body.contains(n.as_str()))
                .map(|(n, _)| n.clone())
                .collect()
        };
        let Some(facts) = (suffix(name) == "py").then(|| pylex::read(body)).flatten() else {
            return by_mention();
        };
        let mut stems: HashMap<&str, &str> = HashMap::new();
        for (n, _) in self.index.iter().filter(|(n, _)| n != name) {
            stems
                .entry(n.rsplit_once('.').map_or(n.as_str(), |(s, _)| s))
                .or_insert(n);
        }
        let mut out: BTreeSet<String> = facts
            .imported
            .iter()
            .filter_map(|i| stems.get(i.as_str()))
            .map(|s| (*s).to_owned())
            .collect();
        for constant in &facts.strings {
            let whole = constant.trim();
            let tail = whole.rsplit('/').next().unwrap_or(whole);
            for key in [
                whole,
                whole.trim_start_matches('_'),
                tail,
                tail.trim_start_matches('_'),
            ] {
                if key != name && self.paths.contains_key(key) {
                    out.insert(key.to_owned());
                } else if let Some(s) = stems.get(key) {
                    out.insert((*s).to_owned());
                }
            }
        }
        out
    }

    fn py_closure(&self, seeds: BTreeSet<String>) -> BTreeSet<String> {
        let (mut seen, mut stack): (BTreeSet<String>, Vec<String>) =
            (BTreeSet::new(), seeds.into_iter().collect());
        while let Some(name) = stack.pop() {
            if !seen.contains(&name) && self.paths.contains_key(&name) {
                let body = if suffix(&name) == "py" {
                    self.text(&name).to_string()
                } else {
                    self.code(&name)
                };
                stack.extend(
                    self.word_refs(&name, &body)
                        .into_iter()
                        .filter(|r| !seen.contains(r)),
                );
                seen.insert(name);
            }
        }
        seen
    }

    /// The files whose contents are a Python test file's freshness key: itself, each conftest above it, the tests/ modules it imports, and the scripts it reaches -
    /// or all of scripts/ and tests/hooks/ when it builds a script path at run time, names or globs the tree, or reaches no script at all.
    #[must_use]
    pub fn pydeps(&self, test: &Path) -> Vec<PathBuf> {
        let test = test.canonicalize().unwrap_or_else(|_| test.to_path_buf());
        let raw = std::fs::read_to_string(&test).unwrap_or_default();
        let name = test
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let code = strip(&name, &raw);
        let mut files = BTreeSet::from([test.clone()]);
        let tests = self.root.join("tests");
        for dir in test
            .ancestors()
            .skip(1)
            .take_while(|d| d.starts_with(&tests))
        {
            files.extend(Some(dir.join("conftest.py")).filter(|c| c.is_file()));
        }
        for capture in TESTS_IMPORT.captures_iter(&raw).flatten() {
            let module = capture.get(1).map_or("", |m| m.as_str()).replace('.', "/");
            files.extend(Some(self.root.join(format!("{module}.py"))).filter(|p| p.is_file()));
        }
        let reached: BTreeSet<PathBuf> = self
            .py_closure(self.word_refs(&name, &raw))
            .iter()
            .filter_map(|n| self.paths.get(n))
            .cloned()
            .collect();
        let scripts = reached
            .iter()
            .any(|p| p.starts_with(&self.scripts) || p.starts_with(&self.here));
        let whole = found(&BUILDS, &code)
            || found(&NAMES_DIR, &code)
            || code.contains("scripts/*.sh")
            || code.contains("scripts/*.py")
            || !scripts;
        if whole {
            files.extend(self.index.iter().map(|(_, p)| p.clone()));
        } else {
            files.extend(reached);
        }
        files.into_iter().collect()
    }

    fn py_key(&self, test: &str) -> String {
        let mut data = Vec::new();
        for path in self.pydeps(&self.root.join(test)) {
            data.extend(self.rel(&path).into_bytes());
            data.push(0);
            data.extend(std::fs::read(&path).unwrap_or_default());
            data.push(0);
        }
        sha256::hex(&data)[..16].to_owned()
    }

    fn stamp_of(gitdir: &Path, test: &str) -> PathBuf {
        gitdir.join("hooks-test/py").join(test.replace('/', "__"))
    }

    /// The test files whose key differs from their last green stamp.
    #[must_use]
    pub fn py_stale(&self, gitdir: &Path, tests: &[String]) -> Vec<String> {
        let stale = |t: &&String| {
            std::fs::read_to_string(Self::stamp_of(gitdir, t))
                .map_or(true, |s| s.trim() != self.py_key(t))
        };
        tests.iter().filter(stale).cloned().collect()
    }

    /// Stamp each test file green.
    pub fn py_stamp(&self, gitdir: &Path, tests: &[String]) {
        for test in tests {
            let stamp = Self::stamp_of(gitdir, test);
            let _ = stamp.parent().map(std::fs::create_dir_all);
            let _ = std::fs::write(stamp, format!("{}\n", self.py_key(test)));
        }
    }

    fn roster(&self) -> Vec<String> {
        let mut hooks = Vec::new();
        walk_into(
            &self.scripts.join("hooks"),
            false,
            &|n| n.ends_with("-hooks.sh"),
            &mut hooks,
        );
        let mut names: Vec<String> = hooks
            .iter()
            .filter_map(|p| p.file_name())
            .map(|n| n.to_string_lossy().into_owned())
            .collect();
        names.sort();
        names.extend(["review-gate.sh", "l7r-gate.sh", "sync-with-main.sh"].map(str::to_owned));
        names
    }

    /// How many of `tests` each of the `count` first-parent commits up to `from` touching scripts/ or tests/hooks/ would re-run, and the mean (feature 375's SC-014).
    fn window(&self, from: &str, count: &str, tests: &[String]) -> String {
        let git = |args: &[&str]| ask(&self.root, "git", args, "").out;
        let deps: Vec<BTreeSet<String>> = tests
            .iter()
            .map(|t| {
                self.pydeps(&self.root.join(t))
                    .iter()
                    .map(|p| self.rel(p))
                    .collect()
            })
            .collect();
        let commits = git(&[
            "log",
            "--first-parent",
            "-n",
            count,
            "--format=%h",
            from,
            "--",
            "scripts",
            "tests/hooks",
        ]);
        let (mut out, mut total, mut seen) = (String::new(), 0, 0);
        for commit in commits.lines() {
            let changed = git(&[
                "diff-tree",
                "-m",
                "--first-parent",
                "--no-commit-id",
                "--name-only",
                "-r",
                commit,
            ]);
            let changed: BTreeSet<String> = changed.lines().map(str::to_owned).collect();
            let runs = deps.iter().filter(|d| !d.is_disjoint(&changed)).count();
            let _ = writeln!(out, "{commit} {runs}");
            total += runs;
            seen += 1;
        }
        let tenths = (total * 10 + seen / 2) / seen.max(1);
        let _ = writeln!(
            out,
            "mean {}.{} of {}",
            tenths / 10,
            tenths % 10,
            tests.len()
        );
        out
    }

    fn keys(&self, guards: &[String]) -> String {
        guards
            .iter()
            .map(|g| {
                format!(
                    "{g} {}
",
                    self.key_for(g)
                )
            })
            .collect::<Vec<_>>()
            .concat()
    }
}

/// The tree a tool works on: the wrapper's `L7R_GUARD_TREE`, else this directory.
#[must_use]
pub fn tool_root() -> PathBuf {
    std::env::var("L7R_GUARD_TREE").map_or_else(
        |_| std::env::current_dir().unwrap_or_default(),
        PathBuf::from,
    )
}

/// `l7r-guard deps`: `--all`, `--keys <guard>...`, `--deps <guard>`, `--pydeps <test>`, `--pystale|--pystamp <gitdir> <test>...`, `--window <from> <count> <test>...`, or `<guard>`'s key.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    answer(&Tree::at(&tool_root()), args)
}

pub(crate) fn answer(tree: &Tree, args: &[String]) -> Reply {
    let say = |stdout: String| Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    };
    let flag = args.first().map_or("", String::as_str);
    match (flag, args.len()) {
        ("--all", _) => say(tree.keys(&tree.roster())),
        ("--keys", 2..) => say(tree.keys(&args[1..])),
        ("--pystale", 2..) => say(tree.py_stale(Path::new(&args[1]), &args[2..]).join("\n") + "\n"),
        ("--pystamp", 2..) => {
            tree.py_stamp(Path::new(&args[1]), &args[2..]);
            say(String::new())
        }
        ("--window", 3..) => say(tree.window(&args[1], &args[2], &args[3..])),
        ("--pydeps", 2..) => {
            let deps: Vec<String> = tree.pydeps(&tree.root.join(&args[1])).iter().map(|p| tree.rel(p)).collect();
            say(deps.join(" ") + "\n")
        }
        ("--deps", 2..) => {
            let named = tree.deps_for(&args[1]).into_iter().filter_map(|n| tree.paths.get(&n).map(|p| tree.rel(p)));
            let deps: Vec<String> = named.chain(tree.rust_inputs(&args[1]).iter().map(|p| tree.rel(p))).collect();
            say(deps.join(" ") + "\n")
        }
        (guard, 1..) if !guard.starts_with('-') => say(tree.key_for(guard) + "\n"),
        _ => Reply { stdout: String::new(), stderr: "usage: l7r-guard deps --all | --keys <guard>... | --deps <guard> | --pydeps <test> | --pystale|--pystamp <gitdir> <test>... | --window <from> <count> <test>... | <guard>\n".to_owned(), code: 2 },
    }
}

#[cfg(test)]
mod tests;
