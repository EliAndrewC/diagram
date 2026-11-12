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

mod code;
use crate::Reply;

/// The append-only records every run writes: no test reads them, and keying on them would re-run every crate's tests after every run.
const RECORDS: [&str; 4] = [
    "dev/run-log/",
    "dev/bypass-log/",
    "dev/perf-log/",
    "dev/idle-log/",
];
/// What every crate's build reads beside its own sources: `.cargo/config.toml` its flags (rust-lld, feature 449 T96), so a change to it
/// runs every check again.
const WORKSPACE: [&str; 7] = [
    "rust/Cargo.toml",
    "rust/Cargo.lock",
    ".cargo/config.toml",
    "clippy.toml",
    "rust/clippy.toml",
    "rust-toolchain",
    "rust-toolchain.toml",
];

/// What rustfmt reads beside a crate's own files: its configuration, wherever rustfmt finds it (none is tracked today, 2026-11-11).
const RUSTFMT: [&str; 4] = [
    "rustfmt.toml",
    ".rustfmt.toml",
    "rust/rustfmt.toml",
    "rust/.rustfmt.toml",
];

/// A doc comment's code block, which rustdoc runs as a doctest: a fence, or a line indented four spaces past the doc marker's own that
/// starts a block - after an empty doc line or a line that is not a doc comment - since an indented line inside a paragraph continues it
/// (markdown; the plan review of T111).
static DOC_FENCE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?m)^\s*//[/!].*```|(?:^\s*//[/!][ \t]*$|^(?!\s*//[/!]).*$|\A)\n?^\s*//[/!] {5,}\S")
});
/// Code that reads the coverage build's own cfg: `cfg(coverage)`, `cfg(not(coverage))`, `cfg!(...)` and `cfg_attr(...)` forms.
static COVERAGE_CFG: LazyLock<Regex> =
    LazyLock::new(|| re(r"\bcfg(?:_attr)?!?\s*\([^)]*\bcoverage\b"));
static TREE_READER: LazyLock<Regex> =
    LazyLock::new(|| re(r"CARGO_MANIFEST_DIR|\btop\(\)|\btoplevel\(\)"));

/// What a check depends on: `Source` the crate, the crates it builds from and the workspace's manifests; `Tests` that and what its tests
/// read of the tree at run time, as its manifest declares (`[package.metadata.l7r] reads`, feature 449 T93); `Own` the crate's own files,
/// the workspace's manifests and rustfmt's configuration alone (T110).
#[derive(Clone, Copy, PartialEq)]
pub(super) enum Reads {
    Source,
    Tests,
    Own,
}

/// The checks a crate's own unchanged inputs answer (feature 449 T060, T93): `make done` on a one-line edit of one crate spent 40 s on
/// the other, and a port agent ran `make rust-test` fourteen times while iterating, every crate's tests each time.
pub(super) fn kept_reads(cmd: &str) -> Option<Reads> {
    match cmd {
        "lint" | "dead" => Some(Reads::Source),
        "test" | "test-counters" | "cover" => Some(Reads::Tests),
        // RUSTFMT KEPT PER CRATE (feature 449 T110; the GM 2026-11-11): a crate's formatting is its own files' alone, yet every
        // `make static` re-checked all 19 crates, 2.1 s of a core edit's 29 s and of an idle run's 4.6 s (2026-11-11)
        "format" => Some(Reads::Own),
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

/// What this check of this crate depends on, as one id: a change to any of it runs the check again (the tests' form; a run's adds the
/// code ids, `verdict_key_with`).
#[cfg(test)]
pub(super) fn verdict_key(
    root: &Path,
    manifest: &Path,
    cmd: &str,
    reads: Reads,
    all: &[PathBuf],
    ids: &BTreeMap<String, String>,
    compiler: &str,
) -> String {
    verdict_key_with(root, manifest, cmd, reads, all, ids, compiler, None)
}

/// A run's two views of each Rust file (T112, T113): its code id, and its interface id.
pub(super) type Views<'a> = (
    &'a BTreeMap<String, String>,
    &'a BTreeMap<String, String>,
    &'a Includes,
);

/// The files each Rust file compiles in (`include_str!`, `include_bytes!`, `include!`), as paths from the tree's root.
pub(super) type Includes = BTreeMap<String, Vec<String>>;

static INCLUDE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\binclude(?:_str|_bytes)?!\s*\(\s*"([^"]+)""#));

/// The paths a Rust file at `path` (from the root) compiles in, resolved from its directory.
fn included(path: &str, text: &str) -> Vec<String> {
    let dir: Vec<&str> = path.split('/').collect();
    INCLUDE
        .captures_iter(text)
        .flatten()
        .map(|c| {
            let mut at: Vec<&str> = dir[..dir.len() - 1].to_vec();
            for part in c[1].split('/') {
                match part {
                    ".." => drop(at.pop()),
                    "." => {}
                    p => at.push(p),
                }
            }
            at.join("/")
        })
        .collect()
}

/// The checks a comment cannot change (T112): clippy, the tests and coverage. rustfmt formats comments, and the dead check counts a
/// word in one as a use, so they read the whole text.
const BY_CODE: [&str; 4] = ["lint", "test", "test-counters", "cover"];

/// `verdict_key`, each Rust file of a check in `BY_CODE` keyed by its code (`code`, its text without its plain comments) where it is
/// given, but for a file the crate's tests declare they read, whose comments they may read.
#[expect(
    clippy::too_many_arguments,
    reason = "verdict_key's seven, and the code ids beside them"
)]
pub(super) fn verdict_key_with(
    root: &Path,
    manifest: &Path,
    cmd: &str,
    reads: Reads,
    all: &[PathBuf],
    ids: &BTreeMap<String, String>,
    compiler: &str,
    views: Option<Views>,
) -> String {
    let views = views.filter(|_| BY_CODE.contains(&cmd));
    // what the crate's tests declare they read: a test or coverage key's, never a lint's, which runs no test
    let declared = if reads == Reads::Tests {
        declared_reads(manifest)
    } else {
        Vec::new()
    };
    let own = rel_dir(manifest, root);
    let dirs: Vec<String> = all
        .iter()
        .map(|m| rel_dir(m, root))
        .chain(std::iter::once(own.clone()))
        .collect();
    let owner = |p: &str| {
        dirs.iter()
            .filter(|d| p.starts_with(d.as_str()))
            .max_by_key(|d| d.len())
            .cloned()
    };
    let mut hash: Vec<u8> = format!("{cmd}\n{compiler}\n").into_bytes();
    let mut keyed: Vec<(&str, &str)> = inputs(root, manifest, reads, all, ids);
    // WHAT THE TESTS COMPILE IN (found under T113): a file a crate's sources include sits outside them where it is another crate's
    // (`guard` compiles in the record crate's HTML entity table), and no key of the crate read it, so a kept test result stood over a
    // changed table. A test or coverage key reads every file its Rust files include.
    if let Some((_, _, includes)) = views.filter(|_| reads == Reads::Tests) {
        let extra: Vec<(&str, &str)> = keyed
            .iter()
            .filter_map(|(p, _)| includes.get(*p))
            .flatten()
            .map(|p| (p.as_str(), ids.get(p).map_or("", String::as_str)))
            .collect();
        keyed.extend(extra);
        keyed.sort_unstable();
        keyed.dedup();
    }
    // THE DEAD CHECK READS ITS WHOLE FAMILY (feature 449 T100): it counts a `pub fn`'s callers across every crate of the family (all of
    // `rust/gate/`), so a dependent crate dropping the last call made a function dead with this crate's own inputs unmoved, and its kept
    // green result stood. Its key is every file of the family.
    if cmd == "dead" {
        let fam = relative(&super::family(manifest), root);
        keyed.extend(
            ids.iter()
                .filter(|(p, _)| Path::new(p.as_str()).starts_with(&fam))
                .map(|(p, i)| (p.as_str(), i.as_str())),
        );
        keyed.sort_unstable();
        keyed.dedup();
    }
    for (path, id) in keyed {
        let read = declared.iter().any(|d| under(path, d));
        // THE DEPENDENCIES' INTERFACE (T113): a lint key reads a file of a crate this one builds from by its interface
        let theirs = cmd == "lint" && owner(path).is_some_and(|o| o != own);
        let view = views.map(|(code, interface, _)| if theirs { interface } else { code });
        let id = view
            .and_then(|v| v.get(path))
            .filter(|_| !read)
            .map_or(id, String::as_str);
        hash.extend(format!("{path} {id}\n").into_bytes());
    }
    sha256::hex(&hash)
}

/// A lint that reads plain comments, configured: clippy's `SAFETY:` comment lints (the restriction group, not enabled 2026-11-11, the plan
/// review of T112) named in a manifest or a `clippy.toml`, or in a lint attribute of a Rust file.
static COMMENT_LINT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?m)^\s*(?:undocumented_unsafe_blocks|unnecessary_safety_comment)\s*=|(?:warn|deny|forbid|expect)\s*\([^)]*clippy::(?:undocumented_unsafe_blocks|unnecessary_safety_comment)",
    )
});

/// Is a lint that reads plain comments configured in the tree?
pub(super) fn comment_lints(root: &Path, ids: &BTreeMap<String, String>) -> bool {
    ids.keys()
        .filter(|p| {
            p.ends_with("Cargo.toml")
                || p.ends_with("clippy.toml")
                || crate::checks::has_ext(p, "rs")
        })
        .any(|p| {
            COMMENT_LINT
                .is_match(&std::fs::read_to_string(root.join(p)).unwrap_or_default())
                .unwrap_or(true)
        })
}

/// COMMENT-INSENSITIVE KEYS (feature 449 T112; the GM 2026-11-11): each Rust file's code id, its text without its plain comments
/// (`code::code_text`), so a comment-only edit moves no lint, test or coverage key - a one-line comment in core had re-run all 17 gate
/// crates' checks, 29 s of `make static` no verdict depended on (2026-11-11). Read from the work tree once a run.
pub(super) fn code_ids(
    root: &Path,
    ids: &BTreeMap<String, String>,
) -> (BTreeMap<String, String>, BTreeMap<String, String>, Includes) {
    let texts: Vec<(&String, String)> = ids
        .iter()
        .filter(|(p, id)| !id.is_empty() && crate::checks::has_ext(p, "rs"))
        .filter_map(|(p, _)| Some((p, std::fs::read_to_string(root.join(p)).ok()?)))
        .collect();
    let view = |tag: &str, of: fn(&str) -> String| -> BTreeMap<String, String> {
        texts
            .iter()
            .map(|(p, t)| {
                (
                    (*p).clone(),
                    format!("{tag}:{}", sha256::hex(of(t).as_bytes())),
                )
            })
            .collect()
    };
    let includes = texts
        .iter()
        .map(|(p, t)| ((*p).clone(), included(p, t)))
        .filter(|(_, i)| !i.is_empty())
        .collect();
    (
        view("code", code::code_text),
        view("interface", code::interface_text),
        includes,
    )
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
    let others = if reads == Reads::Own {
        Vec::new()
    } else {
        depended(root, manifest, all)
    };
    let mine: Vec<String> = std::iter::once(rel_dir(manifest, root))
        .chain(others.iter().map(|m| rel_dir(m, root)))
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
                || (reads == Reads::Own && RUSTFMT.contains(&path.as_str()))
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
    /// Each Rust file's code id, for the checks a comment cannot change (T112).
    pub(super) code: BTreeMap<String, String>,
    /// Each Rust file's interface id, what a dependent's lint reads of it (T113).
    pub(super) interface: BTreeMap<String, String>,
    /// The files each Rust file compiles in.
    pub(super) includes: Includes,
    /// Is a lint that reads plain comments (the `SAFETY:` comment lints) configured anywhere? Then lint keys keep the whole text.
    pub(super) comment_lints: bool,
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
        let ids = content_ids(&world.root);
        let (code, interface, includes) = code_ids(&world.root, &ids);
        Kept {
            reads,
            comment_lints: comment_lints(&world.root, &ids),
            code,
            interface,
            includes,
            ids,
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
            verdict_key_with(
                &world.root,
                manifest,
                cmd,
                k.reads,
                &k.all,
                &k.ids,
                &k.compiler,
                Some((&k.code, &k.interface, &k.includes))
                    .filter(|_| !(cmd == "lint" && k.comment_lints)),
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

    /// A coverage pass's word for the crate's tests (feature 449 T111; the GM 2026-11-11): the coverage run ran every test `cargo test`
    /// runs, instrumented, where the crate has no other test target (`unit_tests_only`), and no code depends on the coverage build
    /// (`cfg(coverage)`), so its tests' green result is kept too - `make rust-test` then `make static` ran each owed crate's tests twice.
    /// Only the key: asking the binary key would build the plain test binary, the cost this saves.
    pub(super) fn keep_tests(world: &World, manifest: &Path, inputs: &Kept) {
        let at = kept_path(&world.root, "test", manifest);
        let key = verdict_key_with(
            &world.root,
            manifest,
            "test",
            inputs.reads,
            &inputs.all,
            &inputs.ids,
            &inputs.compiler,
            Some((&inputs.code, &inputs.interface, &inputs.includes)),
        );
        keep_line(at.as_deref(), kept_lines(at.as_deref()), Some(key));
    }

    /// A green run: its key kept, and its binary among those that passed.
    pub(super) fn keep(self) {
        keep_line(self.at.as_deref(), self.kept, self.key);
        keep_line(self.passed_at.as_deref(), self.passed, self.binary);
    }
}

/// Is the crate's `cargo test` its unit tests alone - no binary, integration test, example, bench or doctest beside its library, which
/// `cargo test` builds and runs and a coverage run (`--lib`) does not (T111)? A doc comment holding a code fence counts as a doctest.
pub(super) fn unit_tests_only(manifest: &Path) -> bool {
    let dir = manifest.parent().unwrap_or(Path::new("."));
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let targets = ["src/main.rs", "src/bin", "tests", "examples", "benches"];
    let declared = ["[[bin]]", "[[test]]", "[[example]]", "[[bench]]"];
    let sources = rust_text(&dir.join("src"));
    // the premise a coverage pass rests on, held where it could break: code reading the coverage build's own cfg
    !targets.iter().any(|t| dir.join(t).exists())
        && !declared.iter().any(|d| text.contains(d))
        && !DOC_FENCE.is_match(&sources).unwrap_or(true)
        && !COVERAGE_CFG.is_match(&sources).unwrap_or(true)
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
