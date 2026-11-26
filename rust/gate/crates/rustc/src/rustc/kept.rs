//! A crate's kept result (feature 449 T060, T93): what a check of a crate depends on, as one key - its sources, the crates it builds
//! from, the workspace's manifests and what its tests declare they read - and, for the tests, a second key over the compiled test
//! binaries, asked only when the first moved. A check whose key stands is not run again.

use std::collections::{BTreeMap, BTreeSet};
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::sha256;
use serde_json::Value;

use super::{crates, own, re, run, rust_text, World};

pub(super) mod alone;
mod code;
use crate::Reply;
pub(super) use alone::Told;

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
/// A doc comment's `text` block, which rustdoc never runs (feature 451 T57): taken out, as an empty doc line, before a doctest is
/// looked for (`holds_doctest`) - every fence of the workspace's but none was one, observed 2026-11-21, method: every `//[/!]` line
/// opening a fence listed - so a crate whose only fences are `text` ones is still its unit tests alone, and `make rust-test` runs no
/// `cargo test --doc` for it (`has_doctests`). Only `text`: a bare fence, `rust`, `ignore` or any other word is still one.
static TEXT_BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?ms)^[ \t]*//[/!][ \t]*```text[ \t]*$.*?^[ \t]*//[/!][ \t]*```[ \t]*$\n?")
});
/// What makes a binary a test target of its own: a test (`#[test]`, `#[tokio::test]`), code under `cfg(test)`, or a module file it
/// declares (`mod x;`), whose tests the coverage run (`--lib`) never builds (T57).
static BIN_TEST: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?m)#\[\s*(?:\w+::)*test\b|\bcfg(?:_attr)?!?\s*\([^)]*\btest\b|^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+\w+\s*;",
    )
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
        .map_while(Result::ok)
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

pub(super) fn git_z(root: &Path, args: &[&str]) -> Vec<String> {
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
    // the files the work tree changed or deleted and those git does not track, from one `git ls-files`: the same paths `git diff
    // --name-only` and `git ls-files --others` gave from two (feature 449 T167, a process less a run of the checks and of their tests)
    let (here, gone): (Vec<String>, Vec<String>) = git_z(
        root,
        &[
            "ls-files",
            "-z",
            "--modified",
            "--others",
            "--exclude-standard",
        ],
    )
    .into_iter()
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

/// A path is on one line: a string that only names the macro (`core`'s reader of these lines) once ran to the next quote, lines and
/// all, and the kept views, a line a file, gave that "path" back cut short, so a key moved after each rebuild (feature 451 T347).
static INCLUDE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\binclude(?:_str|_bytes)?!\s*\(\s*"([^"\n]+)""#));

/// The paths a Rust file at `path` (from the root) compiles in, resolved from its directory.
fn included(path: &str, text: &str) -> Vec<String> {
    let dir: Vec<&str> = path.split('/').collect();
    INCLUDE
        .captures_iter(text)
        .map_while(Result::ok)
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
    for (path, id) in key_inputs(root, manifest, cmd, reads, all, ids, views) {
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

/// The files a check's key of a crate reads (the paths [`verdict_key_with`] hashes): the crate's inputs, the files its Rust files compile
/// in for a test or coverage key, and for the dead check its whole family. [`Kept::reads_any`] asks it of the caller's files (451 T86).
fn key_inputs<'a>(
    root: &Path,
    manifest: &Path,
    cmd: &str,
    reads: Reads,
    all: &[PathBuf],
    ids: &'a BTreeMap<String, String>,
    views: Option<Views<'a>>,
) -> Vec<(&'a str, &'a str)> {
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
    keyed
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
/// crates' checks, 29 s of `make static` no verdict depended on (2026-11-11). Read from the work tree once a run; a run keeps them by
/// content (`code_ids_kept`), this the tests' form with nothing kept.
#[cfg(test)]
pub(super) fn code_ids(
    root: &Path,
    ids: &BTreeMap<String, String>,
) -> (BTreeMap<String, String>, BTreeMap<String, String>, Includes) {
    code_ids_kept(root, ids, None)
}

/// One Rust file's views: its code id, its interface id and the files it compiles in.
type Views3 = (String, String, Vec<String>);

/// THE VIEWS KEPT BY CONTENT (feature 449 T160): `code_ids` read and hashed all 1,000 tracked Rust files, 10 MB, on every `l7r-rust`
/// call - 0.63-0.69 s of the 0.72-0.78 s each check spent before it ran anything, six calls a `make done` (observed 2026-11-17, a timer
/// around each step, reverted). A file's views are a function of its path and its content, which its blob id names, so they are kept in
/// `cache` under `<path> <blob id>` and a run reads only the files whose content moved. The cache is this binary's alone - its first line
/// names the binary by size and time - so a change to how a view is read starts it again; it holds only the tree's current files, and is
/// replaced whole by a rename, so two checks running at once each leave a whole one.
pub(super) fn code_ids_kept(
    root: &Path,
    ids: &BTreeMap<String, String>,
    cache: Option<&Path>,
) -> (BTreeMap<String, String>, BTreeMap<String, String>, Includes) {
    let stamp = this_binary();
    let kept: BTreeMap<String, Views3> = cache
        .and_then(|c| std::fs::read_to_string(c).ok())
        .filter(|text| text.lines().next() == Some(stamp.as_str()))
        .map(|text| text.lines().skip(1).filter_map(views_line).collect())
        .unwrap_or_default();
    let mut now: BTreeMap<String, Views3> = BTreeMap::new();
    let (mut code, mut interface, mut includes) =
        (BTreeMap::new(), BTreeMap::new(), Includes::new());
    for (p, id) in ids
        .iter()
        .filter(|(p, id)| !id.is_empty() && crate::checks::has_ext(p, "rs"))
    {
        let at = format!("{p} {id}");
        let views = kept.get(&at).cloned().or_else(|| {
            let t = std::fs::read_to_string(root.join(p)).ok()?;
            Some((
                format!("code:{}", sha256::hex(code::code_text(&t).as_bytes())),
                format!(
                    "interface:{}",
                    sha256::hex(code::interface_text(&t).as_bytes())
                ),
                included(p, &t),
            ))
        });
        let Some(views) = views else { continue };
        code.insert(p.clone(), views.0.clone());
        interface.insert(p.clone(), views.1.clone());
        if !views.2.is_empty() {
            includes.insert(p.clone(), views.2.clone());
        }
        now.insert(at, views);
    }
    if let Some(c) = cache.filter(|_| now != kept) {
        let body: String = now
            .iter()
            .map(|(at, (c, i, inc))| format!("{at}\t{c}\t{i}\t{}\n", inc.join("\t")))
            .collect();
        let tmp = c.with_extension(format!("{}.tmp", std::process::id()));
        let _ = std::fs::create_dir_all(c.parent().unwrap_or(Path::new(".")));
        if std::fs::write(&tmp, format!("{stamp}\n{body}")).is_ok() {
            let _ = std::fs::rename(&tmp, c);
        }
    }
    (code, interface, includes)
}

/// A kept line, `<path> <blob id>\t<code id>\t<interface id>[\t<included>...]`.
fn views_line(line: &str) -> Option<(String, Views3)> {
    let mut parts = line.split('\t');
    let at = parts.next()?.to_owned();
    let code = parts.next()?.to_owned();
    let interface = parts.next()?.to_owned();
    let inc: Vec<String> = parts.filter(|s| !s.is_empty()).map(str::to_owned).collect();
    Some((at, (code, interface, inc)))
}

/// This binary, named by its size and modification time: a rebuild of the checks (a change to how a view is read) is another binary.
fn this_binary() -> String {
    let meta = std::env::current_exe().and_then(std::fs::metadata);
    let (len, when) = meta.map_or((0, 0), |m| {
        let when = m
            .modified()
            .ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map_or(0, |d| d.as_nanos());
        (m.len(), when)
    });
    format!("l7r-rust views {len} {when}")
}

/// The second key, asked only when the first moved (feature 449 T93): the crate's compiled test binaries and what its tests read at run
/// time - every input but its Rust sources, which the binaries are, and all of what it declares. An edit that leaves the binaries as they
/// were (a dependency's code the tests never reach) runs nothing, and the counting build shares the plain one's result where the
/// binaries are the same, as for every crate with no feature of its own. The binaries come back too, in the order `cargo test` runs
/// them, so a run that is owed runs them without asking cargo again (feature 449 T160, `side.rs`).
fn binary_key(
    world: &World,
    cmd: &str,
    manifest: &Path,
    kept: &Kept,
    told: &Told,
    passed: &mut bool,
) -> Option<(String, Vec<String>)> {
    let (all, ids, compiler) = (&kept.all, &kept.ids, &kept.compiler);
    let args = binary_args(cmd);
    let began = std::time::SystemTime::now();
    // in the lane it was told: a build of this crate alone takes the small lane, never a wide slot (feature 451 T347)
    let built = told.cargo(world, &args, manifest);
    super::phase::wrote(world, "build", &[manifest], began, built.code);
    *passed = built.code == 0;
    let exes = executables(&built.stdout);
    let order = test_targets(&built.stdout);
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
    Some((sha256::hex(&hash), order))
}

/// The binary key's build: the crate's test build, its binaries named as JSON; the counting build's with every feature.
fn binary_args(cmd: &str) -> Vec<&'static str> {
    let mut args = vec!["test", "--no-run", "--message-format=json", "--quiet"];
    if cmd == "test-counters" {
        args.push("--all-features");
    }
    args
}

/// Does `path` lie under a declared read (`"."` the whole tree)?
fn under(path: &str, read: &str) -> bool {
    read == "." || path.starts_with(read)
}

/// The test binaries a `--message-format=json` build names, in the order `cargo test` runs them: the library's unit tests, then each
/// binary's, then each integration test's, each kind by its target's name (feature 449 T160).
pub(super) fn test_targets(stdout: &str) -> Vec<String> {
    let mut found: Vec<(usize, String, String)> = stdout
        .lines()
        .filter(|l| l.starts_with('{'))
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        // a test build's artifacts only: with an integration test, cargo's build names a binary target's plain executable too
        .filter(|v| v["profile"]["test"] != Value::Bool(false))
        .filter_map(|v| {
            let exe = v["executable"].as_str()?.to_owned();
            let kind = v["target"]["kind"][0].as_str().unwrap_or_default();
            let rank = ["lib", "bin", "test"]
                .iter()
                .position(|k| *k == kind)
                .unwrap_or(3);
            Some((
                rank,
                v["target"]["name"].as_str().unwrap_or_default().to_owned(),
                exe,
            ))
        })
        .collect();
    found.sort();
    found.dedup_by(|a, b| a.2 == b.2);
    found.into_iter().map(|(_, _, exe)| exe).collect()
}

/// Does the crate's library hold a doctest - a doc comment's code block, which `cargo test` runs and no test binary holds (T160)? Read
/// as `unit_tests_only` reads one (`holds_doctest`): a fence or an indented block, but for a `text` block, which rustdoc never runs -
/// so the five crates whose only blocks were `text` ones ran a `cargo test --doc` of no test on every `make rust-test` (feature 451
/// T57).
pub(super) fn has_doctests(manifest: &Path) -> bool {
    let src = manifest.parent().unwrap_or(Path::new(".")).join("src");
    src.join("lib.rs").is_file() && holds_doctest(&rust_text(&src))
}

/// Do these sources hold a doctest: a code block (`DOC_FENCE`) once their `text` blocks are taken out (`TEXT_BLOCK`)? A pattern that
/// cannot be read says yes, so a doctest is never missed.
fn holds_doctest(sources: &str) -> bool {
    TEXT_BLOCK
        .try_replacen(sources, 0, "///\n")
        .map_or(true, |docs| DOC_FENCE.is_match(&docs).unwrap_or(true))
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

/// Where a crate's kept result for `cmd` lives: under the clone's git directory `dir`, none outside a repository (`dir` empty). The
/// directory is the one [`Kept::read`] asked git for, once a run: asked again for each crate and check it was a `git` started two or
/// three times a crate, a run of the runner's tests about 20 ms (feature 449 T167, FR-008's tenth of a second).
fn kept_path(dir: &str, cmd: &str, manifest: &Path) -> Option<PathBuf> {
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
    /// The clone's git directory, empty outside a repository: where every crate's kept results live.
    pub(super) git_dir: String,
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
    pub(super) fn read(world: &World, cmd: &str, reads: Reads, found: &[PathBuf]) -> Self {
        let mut all = crates(&world.root, &[]);
        all.extend(
            found
                .iter()
                .filter(|m| !all.contains(m))
                .cloned()
                .collect::<Vec<_>>(),
        );
        let ids = content_ids(&world.root);
        let git_dir = crate::plan::git_line(&world.root, &["rev-parse", "--absolute-git-dir"]);
        // only the checks a comment cannot change read the views (`BY_CODE`): a format or dead key reads the whole text (T160)
        let (code, interface, includes) = if BY_CODE.contains(&cmd) {
            let cache =
                (!git_dir.is_empty()).then(|| Path::new(&git_dir).join("rust-checks/code-views"));
            code_ids_kept(&world.root, &ids, cache.as_deref())
        } else {
            (BTreeMap::new(), BTreeMap::new(), Includes::new())
        };
        Kept {
            reads,
            git_dir,
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

    /// Does `cmd`'s key of `manifest` read any of `files`? The kept key's own inputs ([`key_inputs`]), so a crate that builds on a
    /// caller's crate, or whose tests read a caller's file, is the caller's too (451 T86).
    pub(super) fn reads_any(
        &self,
        root: &Path,
        cmd: &str,
        manifest: &Path,
        files: &BTreeSet<String>,
    ) -> bool {
        let views =
            Some((&self.code, &self.interface, &self.includes)).filter(|_| BY_CODE.contains(&cmd));
        key_inputs(root, manifest, cmd, self.reads, &self.all, &self.ids, views)
            .iter()
            .any(|(p, _)| files.contains(*p))
    }

    /// How many of the workspace's crates `manifest` builds from, its dependencies' own counted: the pre-warm builds the crate with
    /// the fewest first (feature 451 T316), so a crate is built before the crates that build on it.
    pub(super) fn builds_from(&self, root: &Path, manifest: &Path) -> usize {
        depended(root, manifest, &self.all).len()
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
    /// The test binaries the binary key's build named, in `cargo test`'s order: none unless that build ran and named some (T160).
    pub(super) exes: Vec<String>,
    /// The binary key's build ran and passed (feature 451 T05): its `build` phase line is written and the test binaries are built, so a
    /// `cargo test` after it - a build that named no binary - compiles nothing and is booked `test` alone.
    pub(super) built: bool,
    /// What the binary key's build was told before it started (feature 451 T347, `kept/alone.rs`): the small lane where it compiles
    /// this crate alone. `stepped`'s second asking of a red build runs in the same lane. A build nothing told is a wide one.
    pub(super) told: Told,
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
        let at = inputs.and_then(|k| kept_path(&k.git_dir, cmd, manifest));
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
            exes: Vec::new(),
            built: false,
            told: Told::wide(),
        };
        if world.no_reuse || verdict.key.is_none() {
            return (verdict, false);
        }
        if verdict.kept.iter().any(|l| Some(l) == verdict.key.as_ref()) {
            return (verdict, true);
        }
        if cmd.starts_with("test") {
            if let Some(k) = k {
                verdict.told = Told::of(world, cmd, manifest, k, &binary_args(cmd));
            }
            if let Some((binary, exes)) = k.and_then(|k| {
                binary_key(world, cmd, manifest, k, &verdict.told, &mut verdict.built)
            }) {
                verdict.binary = Some(binary);
                verdict.exes = exes;
            }
            verdict.passed_at = k.and_then(|k| kept_path(&k.git_dir, "binary", manifest));
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
        let at = kept_path(&inputs.git_dir, "test", manifest);
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

/// Is the crate's `cargo test` its unit tests alone - no binary holding a test, no integration test, example, bench or doctest beside
/// its library, which `cargo test` builds and runs and a coverage run (`--lib`) does not (T111)? A doc comment holding a code block
/// counts as a doctest, but for a `text` one (`holds_doctest`).
///
/// A BINARY THAT HOLDS NO TEST ADDS NONE (feature 451 T57; the GM 2026-11-20, FR-013): `cargo test` builds a binary target in its test
/// cfg and runs its harness, which with no test in it runs nothing - every binary of the workspace's (`src/main.rs`, `src/bin/`, a
/// `[[bin]]`'s path) held none, observed 2026-11-21, method: each read for `#[test]`, `cfg(test)` and `mod x;`. Its compiling is
/// `make static`'s lint (`clippy --all-targets`, the binary's test cfg too) and the launchers' own builds. So the guard, the gate's
/// binary, `pool`, the engines, the browser and the embedder, and the crates whose only fences are `text` ones, have their whole
/// `cargo test` in the coverage run, and a green pass answers for their plain run: before T57 the guard's plain test binary was built
/// and run again after its coverage pass, 25 builds (4.5 min) and 23 runs (2.1 min) after a green coverage run with no edit between,
/// measured 2026-11-21 (the event log's Phase lines since 2026-11-20T12:35Z; an upper bound, as an edit made by the shell, or of the
/// tree its tests read, is not seen there).
pub(super) fn unit_tests_only(manifest: &Path) -> bool {
    let dir = manifest.parent().unwrap_or(Path::new("."));
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let targets = ["tests", "examples", "benches"];
    let declared = ["[[test]]", "[[example]]", "[[bench]]"];
    let sources = rust_text(&dir.join("src"));
    // the premise a coverage pass rests on, held where it could break: code reading the coverage build's own cfg
    !targets.iter().any(|t| dir.join(t).exists())
        && !declared.iter().any(|d| text.contains(d))
        && !BIN_TEST.is_match(&bin_text(dir, &text)).unwrap_or(true)
        && !holds_doctest(&sources)
        && !COVERAGE_CFG.is_match(&sources).unwrap_or(true)
}

/// The text of the crate's binaries: `src/main.rs`, every file under `src/bin/`, and each `[[bin]]`'s `path`.
fn bin_text(dir: &Path, manifest: &str) -> String {
    let mut text = std::fs::read_to_string(dir.join("src/main.rs")).unwrap_or_default();
    text.push_str(&rust_text(&dir.join("src/bin")));
    let mut in_bin = false;
    for line in manifest.lines().map(str::trim) {
        if line.starts_with('[') {
            in_bin = line == "[[bin]]";
        } else if let Some(path) = line
            .strip_prefix("path")
            .filter(|_| in_bin)
            .and_then(|rest| rest.split('"').nth(1))
        {
            text.push_str(&std::fs::read_to_string(dir.join(path)).unwrap_or_default());
        }
    }
    text
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
