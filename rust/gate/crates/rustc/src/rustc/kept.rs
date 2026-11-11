//! A crate's kept result (feature 449 T060, T93): what a check of a crate depends on, as one key - its sources, the crates it builds
//! from, the workspace's manifests and what its tests declare they read - and, for the tests, a second key over the compiled test
//! binaries, asked only when the first moved. A check whose key stands is not run again.

use std::collections::{BTreeMap, BTreeSet};
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::sha256;
use serde_json::Value;

use super::{cargo, crates, own, re, run, rust_text, World};
use crate::Reply;

/// The append-only records every run writes: no test reads them, and keying on them would re-run every crate's tests after every run.
const RECORDS: [&str; 4] = [
    "dev/run-log/",
    "dev/bypass-log/",
    "dev/perf-log/",
    "dev/idle-log/",
];
const WORKSPACE: [&str; 6] = [
    "rust/Cargo.toml",
    "rust/Cargo.lock",
    "clippy.toml",
    "rust/clippy.toml",
    "rust-toolchain",
    "rust-toolchain.toml",
];

static TREE_READER: LazyLock<Regex> =
    LazyLock::new(|| re(r"CARGO_MANIFEST_DIR|\btop\(\)|\btoplevel\(\)"));

/// What a check depends on: `Source` the crate, the crates it builds from and the workspace's manifests; `Tests` that and what its tests
/// read of the tree at run time, as its manifest declares (`[package.metadata.l7r] reads`, feature 449 T93).
#[derive(Clone, Copy, PartialEq)]
pub(super) enum Reads {
    Source,
    Tests,
}

/// The checks a crate's own unchanged inputs answer (feature 449 T060, T93): `make done` on a one-line edit of one crate spent 40 s on
/// the other, and a port agent ran `make rust-test` fourteen times while iterating, every crate's tests each time.
pub(super) fn kept_reads(cmd: &str) -> Option<Reads> {
    match cmd {
        "lint" | "dead" => Some(Reads::Source),
        "test" | "test-counters" | "cover" => Some(Reads::Tests),
        _ => None,
    }
}

/// The paths a crate's tests read of the tree at run time (`[package.metadata.l7r] reads = ["scripts/", ...]`, `"."` the whole tree,
/// the other crates' files too, but the append-only records): a change to one runs its tests again. Before T93 every crate's tests were keyed on the whole tree, so editing a
/// spec ran all eighteen.
pub(super) fn declared_reads(manifest: &Path) -> Vec<String> {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let section = re(r"(?ms)^\[package\.metadata\.l7r\]\n(.*?)(?:^\[|\z)")
        .captures(&text)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    let list = re(r"(?ms)^reads\s*=\s*\[(.*?)\]")
        .captures(&section)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    re(r#""([^"]*)""#)
        .captures_iter(&list)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect()
}

/// The crates whose own sources name the tree outside the crate (`CARGO_MANIFEST_DIR`, `top()`, `toplevel()`) and whose manifest
/// declares nothing they read: a kept result keyed on their sources alone could stand over a tree their tests no longer pass on.
pub(super) fn undeclared(found: &[PathBuf]) -> Vec<&PathBuf> {
    found
        .iter()
        .filter(|m| {
            declared_reads(m).is_empty()
                && TREE_READER
                    .is_match(&rust_text(
                        &m.parent().unwrap_or(Path::new(".")).join("src"),
                    ))
                    .unwrap_or(false)
        })
        .collect()
}

fn hash_file(path: &Path) -> String {
    sha256::hex(&std::fs::read(path).unwrap_or_default())
}

fn git_z(root: &Path, args: &[&str]) -> Vec<String> {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    let out = done.map(|o| o.stdout).unwrap_or_default();
    String::from_utf8_lossy(&out)
        .split('\0')
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect()
}

/// `{path: content id}`: each file's git blob id - the index's for a tracked file, `git hash-object`'s where the work tree differs or
/// git does not track it, empty for a file deleted from the work tree. One id for one content whether it is edited, staged or committed
/// (feature 449 T93): a hash of the bytes for the edited file and the index's blob id once committed had run every crate a commit
/// touched once more after it.
pub(super) fn content_ids(root: &Path) -> BTreeMap<String, String> {
    let mut ids: BTreeMap<String, String> = BTreeMap::new();
    for record in git_z(root, &["ls-files", "-s", "-z"]) {
        if let Some((meta, path)) = record.split_once('\t') {
            ids.insert(
                path.to_owned(),
                meta.split_whitespace().nth(1).unwrap_or("").to_owned(),
            );
        }
    }
    let changed = git_z(root, &["diff", "--name-only", "-z"]);
    let others = git_z(root, &["ls-files", "--others", "--exclude-standard", "-z"]);
    let (here, gone): (Vec<String>, Vec<String>) = changed
        .into_iter()
        .chain(others)
        .partition(|p| root.join(p).is_file());
    for path in gone {
        ids.insert(path, String::new());
    }
    let blobs = blob_ids(root, &here);
    ids.extend(here.into_iter().zip(blobs));
    ids
}

/// `git hash-object` of each path, one process for them all.
fn blob_ids(root: &Path, paths: &[String]) -> Vec<String> {
    if paths.is_empty() {
        return Vec::new();
    }
    let mut input = paths.join("\n");
    input.push('\n');
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["hash-object", "--stdin-paths"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .and_then(|mut child| {
            let stdin = child.stdin.take();
            stdin.map_or(Ok(()), |mut s| s.write_all(input.as_bytes()))?;
            child.wait_with_output()
        });
    let out = done.map(|o| o.stdout).unwrap_or_default();
    String::from_utf8_lossy(&out)
        .lines()
        .map(str::to_owned)
        .collect()
}

/// The lines of a kept file, oldest first.
fn kept_lines(path: Option<&Path>) -> Vec<String> {
    path.and_then(|p| std::fs::read_to_string(p).ok())
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

/// Add `new` to a kept file's lines, the last eight kept: an edit tried and taken back finds its earlier green result.
fn keep_line(path: Option<&Path>, mut lines: Vec<String>, new: Option<String>) {
    if let (Some(path), Some(new)) = (path, new) {
        lines.retain(|l| *l != new);
        lines.push(new);
        let from = lines.len().saturating_sub(8);
        let _ = std::fs::create_dir_all(path.parent().unwrap_or(path));
        let _ = std::fs::write(path, lines[from..].join("\n") + "\n");
    }
}

fn rel_dir(manifest: &Path, root: &Path) -> String {
    format!(
        "{}/",
        manifest
            .parent()
            .unwrap_or(root)
            .strip_prefix(root)
            .unwrap_or(Path::new(""))
            .display()
    )
}

/// A path relative to `base`, as a manifest writes a path dependency.
pub(super) fn relative(to: &Path, base: &Path) -> String {
    let (a, b): (Vec<_>, Vec<_>) = (to.components().collect(), base.components().collect());
    let same = a.iter().zip(&b).take_while(|(x, y)| x == y).count();
    let up = vec![".."; b.len() - same];
    let down: Vec<String> = a[same..]
        .iter()
        .map(|c| c.as_os_str().to_string_lossy().into_owned())
        .collect();
    [up.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(), down]
        .concat()
        .join("/")
}

/// The crates of `all` that `manifest` builds from by path, and those they build from: a dependency's dependency's edit changes this
/// crate's build too (the gate's crates are four deep, feature 449 T92).
fn depended<'a>(root: &Path, manifest: &Path, all: &'a [PathBuf]) -> Vec<&'a PathBuf> {
    let mut found: Vec<&PathBuf> = Vec::new();
    let mut todo = vec![manifest.to_path_buf()];
    while let Some(at) = todo.pop() {
        let text = std::fs::read_to_string(&at).unwrap_or_default();
        let parent = at.parent().unwrap_or(root);
        for m in all {
            if m.as_path() != manifest
                && !found.contains(&m)
                && text.contains(&format!(
                    "\"{}\"",
                    relative(m.parent().unwrap_or(root), parent)
                ))
            {
                found.push(m);
                todo.push(m.clone());
            }
        }
    }
    found
}

/// What this check of this crate depends on, as one id: a change to any of it runs the check again.
pub(super) fn verdict_key(
    root: &Path,
    manifest: &Path,
    cmd: &str,
    reads: Reads,
    all: &[PathBuf],
    ids: &BTreeMap<String, String>,
    compiler: &str,
) -> String {
    let mut hash: Vec<u8> = format!("{cmd}\n{compiler}\n").into_bytes();
    for (path, id) in inputs(root, manifest, reads, all, ids) {
        hash.extend(format!("{path} {id}\n").into_bytes());
    }
    sha256::hex(&hash)
}

/// The second key, asked only when the first moved (feature 449 T93): the crate's compiled test binaries and what its tests read at run
/// time - every input but its Rust sources, which the binaries are, and all of what it declares. An edit that leaves the binaries as they
/// were (a dependency's code the tests never reach) runs nothing, and the counting build shares the plain one's result where the
/// binaries are the same, as for every crate with no feature of its own.
fn binary_key(
    world: &World,
    cmd: &str,
    manifest: &Path,
    all: &[PathBuf],
    ids: &BTreeMap<String, String>,
    compiler: &str,
) -> Option<String> {
    let mut args = vec!["test", "--no-run", "--message-format=json", "--quiet"];
    if cmd == "test-counters" {
        args.push("--all-features");
    }
    let built = cargo(world, &args, manifest, &[]);
    let exes = executables(&built.stdout);
    if built.code != 0 || exes.is_empty() {
        return None;
    }
    let mut hash: Vec<u8> = format!("binary\n{compiler}\n").into_bytes();
    for exe in &exes {
        hash.extend(format!("{}\n", hash_file(Path::new(exe))).into_bytes());
    }
    let declared = declared_reads(manifest);
    for (path, id) in inputs(&world.root, manifest, Reads::Tests, all, ids) {
        if !crate::checks::has_ext(path, "rs") || declared.iter().any(|d| under(path, d)) {
            hash.extend(format!("{path} {id}\n").into_bytes());
        }
    }
    Some(sha256::hex(&hash))
}

/// Does `path` lie under a declared read (`"."` the whole tree)?
fn under(path: &str, read: &str) -> bool {
    read == "." || path.starts_with(read)
}

/// The executables a `--message-format=json` build names.
pub(super) fn executables(stdout: &str) -> BTreeSet<String> {
    stdout
        .lines()
        .filter(|l| l.starts_with('{'))
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter_map(|v| v["executable"].as_str().map(str::to_owned))
        .collect()
}

/// The `(path, content id)` pairs a check of this crate depends on.
fn inputs<'a>(
    root: &Path,
    manifest: &Path,
    reads: Reads,
    all: &[PathBuf],
    ids: &'a BTreeMap<String, String>,
) -> Vec<(&'a str, &'a str)> {
    let declared = if reads == Reads::Tests {
        declared_reads(manifest)
    } else {
        Vec::new()
    };
    let mine: Vec<String> = std::iter::once(rel_dir(manifest, root))
        .chain(
            depended(root, manifest, all)
                .iter()
                .map(|m| rel_dir(m, root)),
        )
        .collect();
    let dirs: Vec<String> = all
        .iter()
        .map(|m| rel_dir(m, root))
        .chain(std::iter::once(rel_dir(manifest, root)))
        .collect();
    // a path belongs to the crate whose directory holds it most nearly: the gate's `crates/*` sit inside the binary's (feature 449 T92)
    let owner = |p: &str| {
        dirs.iter()
            .filter(|d| p.starts_with(d.as_str()))
            .max_by_key(|d| d.len())
    };
    ids.iter()
        .filter(|(path, _)| {
            owner(path).is_some_and(|o| mine.contains(o))
                || WORKSPACE.contains(&path.as_str())
                || (declared.iter().any(|d| under(path, d))
                    && !RECORDS.iter().any(|r| path.starts_with(r)))
        })
        .map(|(p, i)| (p.as_str(), i.as_str()))
        .collect()
}

/// Where a crate's kept result for `cmd` lives: the clone's git directory, none outside a repository.
fn kept_path(root: &Path, cmd: &str, manifest: &Path) -> Option<PathBuf> {
    let dir = crate::plan::git_line(root, &["rev-parse", "--absolute-git-dir"]);
    (!dir.is_empty()).then(|| {
        Path::new(&dir).join("rust-checks").join(format!(
            "{cmd}-{}",
            manifest
                .parent()
                .and_then(Path::file_name)
                .unwrap_or_default()
                .to_string_lossy()
        ))
    })
}

/// What a kept check reads once a run: the tree's content ids, the compiler, and every crate (a named crate's key still follows the
/// crates it builds from, which a named run does not list).
pub(super) struct Kept {
    pub(super) reads: Reads,
    pub(super) ids: BTreeMap<String, String>,
    pub(super) compiler: String,
    pub(super) all: Vec<PathBuf>,
}

impl Kept {
    pub(super) fn read(world: &World, reads: Reads, found: &[PathBuf]) -> Self {
        let mut all = crates(&world.root, &[]);
        all.extend(
            found
                .iter()
                .filter(|m| !all.contains(m))
                .cloned()
                .collect::<Vec<_>>(),
        );
        Kept {
            reads,
            ids: content_ids(&world.root),
            compiler: run(&world.cargo, &own(&["--version"]), &BTreeMap::new())
                .stdout
                .trim()
                .to_owned(),
            all,
        }
    }
}

/// A crate's kept result for one check: where its keys live and the last eight green ones, this run's key, and for a test run the
/// binary key and where the binaries that passed are kept (`test` and `test-counters` share them, so a binary either built once is green
/// for both).
pub(super) struct Verdict {
    at: Option<PathBuf>,
    kept: Vec<String>,
    key: Option<String>,
    binary: Option<String>,
    passed_at: Option<PathBuf>,
    passed: Vec<String>,
}

impl Verdict {
    /// The crate's kept result for `cmd`, and whether it stands: its key among the last green ones, or, for a test run, a binary that
    /// already passed (its key then kept too). A fresh run (`L7R_RUST_FRESH`) stands on nothing, and still keeps what it finds green.
    pub(super) fn ask(
        world: &World,
        cmd: &str,
        manifest: &Path,
        inputs: Option<&Kept>,
    ) -> (Self, bool) {
        let at = inputs.and_then(|_| kept_path(&world.root, cmd, manifest));
        let k = inputs.filter(|_| at.is_some());
        let key = k.map(|k| {
            verdict_key(
                &world.root,
                manifest,
                cmd,
                k.reads,
                &k.all,
                &k.ids,
                &k.compiler,
            )
        });
        let mut verdict = Verdict {
            kept: kept_lines(at.as_deref()),
            at,
            key,
            binary: None,
            passed_at: None,
            passed: Vec::new(),
        };
        if world.no_reuse || verdict.key.is_none() {
            return (verdict, false);
        }
        if verdict.kept.iter().any(|l| Some(l) == verdict.key.as_ref()) {
            return (verdict, true);
        }
        if cmd.starts_with("test") {
            verdict.binary =
                k.and_then(|k| binary_key(world, cmd, manifest, &k.all, &k.ids, &k.compiler));
            verdict.passed_at = kept_path(&world.root, "binary", manifest);
            verdict.passed = kept_lines(verdict.passed_at.as_deref());
            if verdict
                .binary
                .as_ref()
                .is_some_and(|b| verdict.passed.contains(b))
            {
                keep_line(
                    verdict.at.as_deref(),
                    verdict.kept.clone(),
                    verdict.key.clone(),
                );
                return (verdict, true);
            }
        }
        (verdict, false)
    }

    /// A green run: its key kept, and its binary among those that passed.
    pub(super) fn keep(self) {
        keep_line(self.at.as_deref(), self.kept, self.key);
        keep_line(self.passed_at.as_deref(), self.passed, self.binary);
    }
}

/// The refusal when a crate's sources read the tree undeclared.
pub(super) fn undeclared_refusal(world: &World, blind: &[&PathBuf]) -> Reply {
    let names: String = blind
        .iter()
        .map(|m| format!("  {}\n", rel_dir(m, &world.root)))
        .collect();
    Reply {
        stdout: String::new(),
        stderr: format!("rust-checks: these crates' sources name the tree outside the crate (CARGO_MANIFEST_DIR, top(), toplevel()) but their Cargo.toml declares nothing their tests read, so a kept result could stand over a tree the tests no longer pass on:\n{names}add `[package.metadata.l7r]` with `reads = [\"<path>/\", ...]` (\".\" the whole tree) to each Cargo.toml\n"),
        code: 1,
    }
}
