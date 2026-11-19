//! `l7r-guard deps` (feature 449 T050, the port of `tests/hooks/hookdeps.py`, feature 172): what each guard suite depends on,
//! derived transitively. The failure that matters is UNDER-running: a derivation that misses a dependency skips a suite a change has broken and reports green,
//! while over-running is merely slow, so every doubtful edge here counts as a dependency.
//!
//! A reference is a file NAME standing in another file's CODE: comments and docstrings are mentions, not dependencies (every guard says "detection lives in X" in
//! prose, which made every guard depend on every helper). A Python import never writes the extension, so a stem counts where it is imported.
//!
//! `sync-with-main.sh` alone is held to the whole tree: its suite resolves script paths at run time from trees its fixtures build, an edge no static reader
//! follows. A suite that reads the whole scripts directory derives to it by its own code (`globs_tree`), matched as the code writes it, not as prose describes it.

use std::cell::{OnceCell, RefCell};
use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::rc::Rc;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::agent_prefix_hooks::lines_kept;
use crate::protocol::Reply;
use crate::shared::sha256;
use crate::suite_tools::pylex;

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
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
    /// The Rust sources `RUST_GUARD` names, listed once a run, and their bytes' digest, hashed once (feature 449 T205).
    rust_files: OnceCell<Vec<PathBuf>>,
    rust_digest: OnceCell<String>,
}

impl Tree {
    /// The index over `scripts/`, `tests/hooks/` and the root `Makefile` at `root`: every basename is unique across them, so a name identifies one file.
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
        // the root Makefile too: a suite that drives make targets names it in its code, and a Makefile-only edit left that suite fresh and
        // unrun (feature 449 T186: the make-only suite's free-text cases, red on the old Makefile, went unrun by `make hooks-test`)
        let makefile = root.join("Makefile");
        if makefile.is_file() {
            files.push(makefile);
        }
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
            rust_files: OnceCell::new(),
            rust_digest: OnceCell::new(),
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
            .map_while(Result::ok)
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

    fn drives_rust(&self, guard: &str) -> bool {
        let words = format!("{}{}", self.text(guard), self.text(&suite_of(guard)));
        words.contains("l7r-guard") || words.contains("l7r-gate")
    }

    fn rust_files(&self) -> &[PathBuf] {
        self.rust_files.get_or_init(|| {
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
        })
    }

    fn rust_inputs(&self, guard: &str) -> Vec<PathBuf> {
        if self.drives_rust(guard) {
            self.rust_files().to_vec()
        } else {
            Vec::new()
        }
    }

    /// THE RUST SOURCES HASHED ONCE A RUN (feature 449 T205): every suite that drives a binary hashed the same 13 MB of sources into
    /// its own key, about 50 times, 2.55 s of `make hooks-test`'s start before any suite ran (2026-11-19); their digest stands in for
    /// their bytes, so any byte of them still moves every such key.
    fn rust_digest(&self) -> &str {
        self.rust_digest.get_or_init(|| {
            let mut data = Vec::new();
            for path in self.rust_files() {
                data.extend(std::fs::read(path).unwrap_or_default());
            }
            sha256::hex(&data)
        })
    }

    /// The suite's key: its dependencies' bytes in `deps_for` order, a missing one skipped, then the Rust sources' digest where it
    /// drives a binary; sha256's first 16 hex digits.
    #[must_use]
    pub fn key_for(&self, guard: &str) -> String {
        let mut data = Vec::new();
        for name in self.deps_for(guard) {
            if let Some(path) = self.paths.get(&name).filter(|p| p.is_file()) {
                data.extend(std::fs::read(path).unwrap_or_default());
            }
        }
        if self.drives_rust(guard) {
            data.extend(self.rust_digest().as_bytes());
        }
        sha256::hex(&data)[..16].to_owned()
    }

    fn rel(&self, path: &Path) -> String {
        path.strip_prefix(&self.root)
            .unwrap_or(path)
            .to_string_lossy()
            .into_owned()
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

/// `l7r-guard deps`: `--all`, `--keys <guard>...`, `--deps <guard>`, or `<guard>`'s key. A Python test's freshness key (`--pydeps`, `--pystale`,
/// `--pystamp`) and the commit window over the Python tests of `scripts/` (`--window`, `make hooks-deps-window`) left with pytest (feature 449 T213).
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
        ("--deps", 2..) => {
            let named = tree
                .deps_for(&args[1])
                .into_iter()
                .filter_map(|n| tree.paths.get(&n).map(|p| tree.rel(p)));
            let deps: Vec<String> = named
                .chain(tree.rust_inputs(&args[1]).iter().map(|p| tree.rel(p)))
                .collect();
            say(deps.join(" ") + "\n")
        }
        (guard, 1..) if !guard.starts_with('-') => say(tree.key_for(guard) + "\n"),
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard deps --all | --keys <guard>... | --deps <guard> | <guard>\n"
                .to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
