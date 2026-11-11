//! The Rust crates' checks (feature 444 T17, FR-011; feature 449 T067, from `rust_checks.py`; `dev/rust-tooling.md` "lint", "format",
//! "function cap"). Lint is clippy with `-D warnings`, the crates' `[lints.clippy]` denying `all` and `pedantic`; format is rustfmt; test
//! is `cargo test`; cover is 100% of a crate's lines by its own tests, `cargo llvm-cov`. No crate is no work.
//!
//! The build goes outside the tree, one directory a clone: cargo keys a path package's build by its name, so every clone sharing one
//! directory shared one test binary, and `make rust-test` once passed a test written to fail (feature 444 T16, 2026-11-01).

#![expect(
    clippy::format_collect,
    reason = "a listing's lines are short, and the map reads as the text it writes"
)]

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;
use std::time::Instant;

use fancy_regex::Regex;
use l7r_guard::shared::sha256;
use serde_json::Value;

use crate::Reply;

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
const USAGE_LOG_TOOL: &str = "rust_checks";
const CRATES: &str = "rust";
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

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BUILD_HASH: LazyLock<Regex> = LazyLock::new(|| re(r"Cs[0-9A-Za-z]+_|17h[0-9a-f]{16}E"));
static PUB_FN: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\s*pub(?:\([^)]*\))?\s+(?:const\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)"));

/// What a check depends on: `Source` the crate and the workspace's manifests, `Tree` everything but the other crates.
#[derive(Clone, Copy, PartialEq)]
enum Reads {
    Source,
    Tree,
}

/// The checks a crate's own unchanged inputs answer (feature 449 T060): `make done` on a one-line edit of one crate spent 40 s on the other.
fn kept_reads(cmd: &str) -> Option<Reads> {
    match cmd {
        "lint" | "dead" => Some(Reads::Source),
        "cover" | "test-counters" => Some(Reads::Tree),
        _ => None,
    }
}

/// Where everything runs, read once from the environment.
pub struct World {
    root: PathBuf,
    target: PathBuf,
    cargo: String,
    path_dir: PathBuf,
    target_override: Option<String>,
    no_reuse: bool,
    hamlet_features: String,
    hamlet_args: String,
    hamlet_spec: String,
    cover_work: Option<PathBuf>,
}

struct Ran {
    code: i32,
    stdout: String,
    stderr: String,
}

fn run(program: &str, args: &[String], env: &BTreeMap<String, String>) -> Ran {
    // a crate's own tests read this tree-from-wrapper variable, and it is this run's, not theirs
    match Command::new(program)
        .args(args)
        .envs(env)
        .env_remove("L7R_GATE_TREE")
        .output()
    {
        Ok(o) => Ran {
            code: o.status.code().unwrap_or(1),
            stdout: String::from_utf8_lossy(&o.stdout).into_owned(),
            stderr: String::from_utf8_lossy(&o.stderr).into_owned(),
        },
        Err(e) => Ran {
            code: 127,
            stdout: String::new(),
            stderr: format!("cannot start {program}: {e}\n"),
        },
    }
}

fn own(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

fn find_manifests(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            find_manifests(&path, out);
        } else if entry.file_name() == "Cargo.toml" {
            out.push(path);
        }
    }
}

/// The crates: the named ones, or every package under `rust/` (a workspace root names members and builds nothing itself).
fn crates(root: &Path, named: &[String]) -> Vec<PathBuf> {
    if !named.is_empty() {
        return named
            .iter()
            .map(|n| {
                if n.ends_with("Cargo.toml") {
                    root.join(n)
                } else {
                    root.join(n).join("Cargo.toml")
                }
            })
            .collect();
    }
    let mut found = Vec::new();
    find_manifests(&root.join(CRATES), &mut found);
    found.retain(|m| {
        std::fs::read_to_string(m)
            .unwrap_or_default()
            .contains("[package]")
    });
    found.sort();
    found
}

fn cargo(world: &World, args: &[&str], manifest: &Path, after: &[&str]) -> Ran {
    let mut all = own(args);
    all.push("--manifest-path".to_owned());
    all.push(manifest.display().to_string());
    if !after.is_empty() {
        all.push("--".to_owned());
        all.extend(own(after));
    }
    let target = world
        .target_override
        .clone()
        .unwrap_or_else(|| world.target.display().to_string());
    run(
        &world.cargo,
        &all,
        &BTreeMap::from([("CARGO_TARGET_DIR".to_owned(), target)]),
    )
}

/// The cargo feature flags naming every feature of the crate but `left_out` (none when that leaves none).
fn features_but(manifest: &Path, left_out: &str) -> Vec<String> {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let section = re(r"(?ms)^\[features\]\n(.*?)(?:^\[|\z)")
        .captures(&text)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    let names = re(r"(?m)^([A-Za-z_][\w-]*)\s*=");
    let rest: Vec<String> = names
        .captures_iter(&section)
        .flatten()
        .map(|c| c[1].to_owned())
        .filter(|n| n != left_out)
        .collect();
    if rest.is_empty() {
        Vec::new()
    } else {
        vec!["--features".to_owned(), rest.join(",")]
    }
}

/// Each file's lines no test ran and the first line of each function no test called: the one reader of the floor (a closure never
/// called counts though its line runs, as llvm-cov's `--fail-under-lines` summary counts it).
fn lcov_missed(text: &str) -> BTreeMap<String, Vec<u32>> {
    let mut lines: BTreeMap<String, BTreeSet<u32>> = BTreeMap::new();
    let mut calls: BTreeMap<(String, u32, String), u64> = BTreeMap::new();
    let mut path = String::new();
    let mut starts: BTreeMap<String, u32> = BTreeMap::new();
    for line in text.lines() {
        if let Some(p) = line.strip_prefix("SF:") {
            p.clone_into(&mut path);
            starts.clear();
        } else if let Some((at, name)) = line.strip_prefix("FN:").and_then(|r| r.split_once(',')) {
            starts.insert(name.to_owned(), at.parse().unwrap_or(0));
        } else if let Some((n, name)) = line.strip_prefix("FNDA:").and_then(|r| r.split_once(',')) {
            if let Some(at) = starts.get(name) {
                let slot = calls
                    .entry((
                        path.clone(),
                        *at,
                        BUILD_HASH.replace_all(name, "").into_owned(),
                    ))
                    .or_default();
                *slot = (*slot).max(n.parse().unwrap_or(0));
            }
        } else if let Some((at, n)) = line.strip_prefix("DA:").and_then(|r| r.split_once(',')) {
            if n.split(',').next() == Some("0") {
                lines
                    .entry(path.clone())
                    .or_default()
                    .insert(at.parse().unwrap_or(0));
            }
        }
    }
    for ((p, at, _), n) in calls {
        if n == 0 {
            lines.entry(p).or_default().insert(at);
        }
    }
    lines
        .into_iter()
        .map(|(p, v)| (p, v.into_iter().collect()))
        .collect()
}

fn rust_sources(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            rust_sources(&path, out);
        } else if crate::checks::has_ext(&path.to_string_lossy(), "rs") {
            out.push(path);
        }
    }
}

/// The outermost crate directory holding `manifest`'s: the gate binary's for each of the gate's crates (`rust/gate/crates/*`, feature
/// 449 T92), a crate's own otherwise.
fn family(manifest: &Path) -> PathBuf {
    let own = manifest.parent().unwrap_or(Path::new("."));
    own.ancestors()
        .filter(|d| {
            std::fs::read_to_string(d.join("Cargo.toml")).is_ok_and(|t| t.contains("[package]"))
        })
        .last()
        .unwrap_or(own)
        .to_path_buf()
}

/// Every `.rs` file under `dir`, their text joined in path order.
fn rust_text(dir: &Path) -> String {
    let mut files = Vec::new();
    rust_sources(dir, &mut files);
    files.sort();
    files
        .iter()
        .map(|p| std::fs::read_to_string(p).unwrap_or_default())
        .collect::<Vec<_>>()
        .join("\n")
}

/// Each `pub fn` of the crate nothing calls: rustc's `dead_code` sees only private items. A gate crate's function is called from the
/// other gate crates too, so the calls are counted over its family's sources (`family`), the names read from its own.
fn dead_public(manifest: &Path) -> Vec<String> {
    let own = rust_text(&manifest.parent().unwrap_or(Path::new(".")).join("src"));
    let rust = rust_text(&family(manifest));
    let names: BTreeSet<String> = PUB_FN
        .captures_iter(&own)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    // One pass over the text's words, counted once: a Unicode `\b` search per name took hours on the guard crate's thousands of
    // names, where the Python's took seconds. A word is a maximal run of `\w`, as Python's `\b` bounds one.
    let mut uses: BTreeMap<&str, usize> = BTreeMap::new();
    for word in rust.split(|c: char| !c.is_alphanumeric() && c != '_') {
        *uses.entry(word).or_default() += 1;
    }
    names
        .into_iter()
        .filter(|n| uses.get(n.as_str()) <= Some(&1))
        .collect()
}

fn timed(step: &str, program: &str, args: &[String], env: &BTreeMap<String, String>) -> Ran {
    let began = Instant::now();
    let mut done = run(program, args, env);
    let _ = writeln!(
        done.stderr,
        "rust-checks: cover {step} {:.1} s",
        began.elapsed().as_secs_f64()
    );
    done
}

fn glob_prefix(dir: &Path, prefix: &str) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().starts_with(prefix))
        .map(|e| e.path())
        .collect()
}

fn remove(path: &Path) {
    if path.is_dir() {
        let _ = std::fs::remove_dir_all(path);
    } else {
        let _ = std::fs::remove_file(path);
    }
}

/// Instrument, run the crate's tests, and write the report. Only the last run's profiles are cleared and only the tests' binary is built:
/// `llvm-cov clean` rebuilt the crate from scratch on every run (the GM 2026-11-07: "Are we recompiling EVERYTHING every time?").
fn cover(world: &World, manifest: &Path, work: &Path, report: &[String]) -> Ran {
    let manifest_arg = manifest.display().to_string();
    let target = work.join("target");
    let mut env = BTreeMap::from([
        (
            "PATH".to_owned(),
            format!(
                "{}:{}",
                world.path_dir.display(),
                std::env::var("PATH").unwrap_or_default()
            ),
        ),
        ("CARGO_TARGET_DIR".to_owned(), target.display().to_string()),
    ]);
    let shown = run(
        &world.cargo,
        &[
            own(&["llvm-cov", "show-env", "--manifest-path"]),
            vec![manifest_arg.clone()],
        ]
        .concat(),
        &env,
    );
    for line in shown.stdout.lines() {
        if let Some((k, v)) = line.split_once('=') {
            env.insert(
                k.trim_start_matches("export ").to_owned(),
                v.trim().trim_matches(['\'', '"']).to_owned(),
            );
        }
    }
    for old in std::fs::read_dir(&target)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| crate::checks::has_ext(&p.to_string_lossy(), "profraw"))
    {
        remove(&old);
    }
    let deps = target.join("debug/deps");
    for old in glob_prefix(&deps, &own_libs(manifest)) {
        remove(&old);
    }
    let lib = [
        own(&["--lib", "--quiet", "--manifest-path"]),
        vec![manifest_arg.clone()],
    ]
    .concat();
    let built = timed(
        "build",
        &world.cargo,
        &[
            own(&["test", "--no-run", "--message-format=json"]),
            lib.clone(),
        ]
        .concat(),
        &env,
    );
    let keep: BTreeSet<String> = built
        .stdout
        .lines()
        .filter(|l| l.starts_with('{'))
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter_map(|v| v["executable"].as_str().map(str::to_owned))
        .collect();
    // every other test binary goes: llvm-cov's report reads each one in the build, and in the one build the gate's crates share
    // (feature 449 T92) another crate's binary carries this crate's code with none of this run's counts
    if !keep.is_empty() {
        for old in glob_prefix(&deps, "") {
            let shown = old.display().to_string();
            if !keep.contains(&shown) && old.extension().is_none() {
                remove(&old);
            }
        }
    }
    eprint!("{}", built.stderr);
    if built.code != 0 {
        return built;
    }
    let tests = timed("tests", &world.cargo, &[own(&["test"]), lib].concat(), &env);
    eprint!("{}", tests.stderr);
    if tests.code != 0 {
        return tests;
    }
    run(
        &world.cargo,
        &[
            own(&["llvm-cov", "report"]),
            report.to_vec(),
            vec!["--manifest-path".to_owned(), manifest_arg],
        ]
        .concat(),
        &env,
    )
}

/// Each source file of the crate with the lines its tests do not reach; a failed run names the crate, not a line.
fn uncovered(world: &World, manifest: &Path, work: &Path) -> BTreeMap<String, Vec<u32>> {
    let lcov = work.join("lcov.info");
    let _ = std::fs::create_dir_all(work);
    let done = cover(
        world,
        manifest,
        work,
        &own(&["--lcov", "--output-path", &lcov.display().to_string()]),
    );
    let parent = manifest.parent().unwrap_or(Path::new("."));
    let text = std::fs::read_to_string(&lcov);
    let (Ok(text), 0) = (text, done.code) else {
        let (out, err) = (tail(&done.stdout), tail(&done.stderr));
        eprintln!("rust-checks: the coverage run failed on {} - fix what it names (a failing test), then ask again:\n{out}{err}", parent.file_name().unwrap_or_default().to_string_lossy());
        return BTreeMap::from([(parent.display().to_string(), vec![0])]);
    };
    let canon = |p: &Path| {
        format!(
            "{}/",
            std::fs::canonicalize(p).unwrap_or_default().display()
        )
    };
    let mine = canon(parent);
    // a crate nested in this one's directory (the gate's `crates/*` under the binary's) owns its own lines: 100% of a crate's lines by
    // its own tests (feature 449 T92)
    let nested: Vec<String> = crates(&world.root, &[])
        .iter()
        .filter_map(|m| m.parent())
        .map(canon)
        .filter(|d| d != &mine && d.starts_with(&mine))
        .collect();
    lcov_missed(&text)
        .into_iter()
        .filter(|(p, _)| {
            let at = std::fs::canonicalize(p)
                .unwrap_or_default()
                .display()
                .to_string();
            at.starts_with(&mine) && !nested.iter().any(|n| at.starts_with(n.as_str()))
        })
        .collect()
}

/// The files of the crate's own library in a build's `deps`, which a coverage run clears: `lib<name>-` (the package's name; any
/// `libl7r_` where the manifest names none). Only its own, so the gate's crates share one coverage build (feature 449 T92).
fn own_libs(manifest: &Path) -> String {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    re(r#"(?m)^name\s*=\s*"([^"]+)""#)
        .captures(&text)
        .ok()
        .flatten()
        .map_or_else(|| "libl7r_".to_owned(), |c| format!("lib{}-", &c[1]))
}

/// The directory a crate's coverage build is kept in (a test shares one over its copies of a fixture): one a family of crates
/// (`family`), so the gate's crates build their shared dependencies once.
fn cover_dir(world: &World, manifest: &Path) -> PathBuf {
    let family = family(manifest);
    let name = family.file_name().unwrap_or_default().to_string_lossy();
    world
        .cover_work
        .clone()
        .unwrap_or_else(|| world.target.join(format!("cover-{name}")))
}

fn tail(text: &str) -> &str {
    let at = text.char_indices().rev().nth(3999).map_or(0, |(i, _)| i);
    &text[at..]
}

fn check(world: &World, cmd: &str, manifest: &Path, formatting_check: bool) -> Ran {
    match cmd {
        "lint" => {
            let plain = cargo(
                world,
                &["clippy", "--quiet", "--all-targets"],
                manifest,
                &["-D", "warnings"],
            );
            if plain.code == 0 {
                cargo(
                    world,
                    &["clippy", "--quiet", "--all-targets", "--all-features"],
                    manifest,
                    &["-D", "warnings"],
                )
            } else {
                plain
            }
        }
        "test" => cargo(world, &["test", "--quiet"], manifest, &[]),
        "test-counters" => cargo(world, &["test", "--quiet", "--all-features"], manifest, &[]),
        "hamlet" => {
            let mut args = vec!["run", "--release", "--quiet"];
            if !world.hamlet_features.is_empty() {
                args.extend(["--features", world.hamlet_features.as_str()]);
            }
            args.extend(["--bin", "hamlet"]);
            let after: Vec<&str> = if world.hamlet_args.is_empty() {
                vec![world.hamlet_spec.as_str()]
            } else {
                world.hamlet_args.split_whitespace().collect()
            };
            cargo(world, &args, manifest, &after)
        }
        "test-no-counters" => {
            let flags = features_but(manifest, "counters");
            let mut args = vec!["test", "--quiet"];
            args.extend(flags.iter().map(String::as_str));
            cargo(world, &args, manifest, &[])
        }
        "dead" => {
            let dead = dead_public(manifest);
            let why: String = dead
                .iter()
                .flat_map(|n| {
                    [
                        "  pub fn ",
                        n.as_str(),
                        ": nothing in Rust calls it - delete it, or call it\n",
                    ]
                })
                .collect();
            Ran {
                code: i32::from(!dead.is_empty()),
                stdout: String::new(),
                stderr: why,
            }
        }
        "cover" => {
            let got = uncovered(world, manifest, &cover_dir(world, manifest));
            let listing: String = got
                .iter()
                .map(|(p, v)| {
                    format!(
                        "{p} - lines no test reaches: {}\n",
                        v.iter().map(u32::to_string).collect::<Vec<_>>().join(", ")
                    )
                })
                .collect();
            Ran {
                code: i32::from(!got.is_empty()),
                stdout: listing,
                stderr: String::new(),
            }
        }
        _ => cargo(
            world,
            if formatting_check {
                &["fmt", "--check"]
            } else {
                &["fmt"]
            },
            manifest,
            &[],
        ),
    }
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

/// `{path: content id}`: each tracked file's index blob, or a hash of its bytes where the work tree differs or git does not track it.
fn content_ids(root: &Path) -> BTreeMap<String, String> {
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
    for path in changed.into_iter().chain(others) {
        let id = hash_file(&root.join(&path));
        ids.insert(path, id);
    }
    ids
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
fn relative(to: &Path, base: &Path) -> String {
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
fn verdict_key(
    root: &Path,
    manifest: &Path,
    cmd: &str,
    reads: Reads,
    all: &[PathBuf],
    ids: &BTreeMap<String, String>,
    compiler: &str,
) -> String {
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
    let mut hash: Vec<u8> = format!("{cmd}\n{compiler}\n").into_bytes();
    for (path, id) in ids {
        let kept = if reads == Reads::Source {
            owner(path).is_some_and(|o| mine.contains(o)) || WORKSPACE.contains(&path.as_str())
        } else {
            owner(path).is_none_or(|o| mine.contains(o))
                && !RECORDS.iter().any(|r| path.starts_with(r))
        };
        if kept {
            hash.extend(format!("{path} {id}\n").into_bytes());
        }
    }
    sha256::hex(&hash)
}

fn fix_for(cmd: &str) -> &'static str {
    match cmd {
        "lint" => "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)",
        "format" => "run `make format`",
        "test" => "fix the failing test cargo names",
        "cover" => "test the lines llvm-cov names, from the crate's tests",
        "dead" => "delete the pub fn it names, or call it",
        "hamlet" => "fix the stage or the spec the driver names above",
        "test-no-counters" => "fix the test whose result hangs on the counters",
        _ => "fix the test the counting build fails: a count's assertion, or a result the counters change",
    }
}

fn kept_path(root: &Path, cmd: &str, manifest: &Path) -> PathBuf {
    let dir = crate::plan::git_line(root, &["rev-parse", "--absolute-git-dir"]);
    Path::new(&dir).join("rust-checks").join(format!(
        "{cmd}-{}",
        manifest
            .parent()
            .and_then(Path::file_name)
            .unwrap_or_default()
            .to_string_lossy()
    ))
}

fn answer(world: &World, cmd: &str, named: &[String], formatting_check: bool) -> Reply {
    let found = crates(&world.root, named);
    let (mut stdout, mut stderr) = (String::new(), String::new());
    if found.is_empty() {
        return Reply {
            stdout: format!("rust-checks: no Rust crate under {CRATES}/ - nothing to {cmd}\n"),
            stderr,
            code: 0,
        };
    }
    let reads = kept_reads(cmd).filter(|_| named.is_empty());
    let ids = if reads.is_some() {
        content_ids(&world.root)
    } else {
        BTreeMap::new()
    };
    let compiler = if reads.is_some() {
        run(&world.cargo, &own(&["--version"]), &BTreeMap::new())
            .stdout
            .trim()
            .to_owned()
    } else {
        String::new()
    };
    let mut bad = 0;
    for manifest in &found {
        let shown = manifest
            .parent()
            .unwrap_or(&world.root)
            .strip_prefix(&world.root)
            .unwrap_or(Path::new(""))
            .display()
            .to_string();
        let key =
            reads.map(|r| verdict_key(&world.root, manifest, cmd, r, &found, &ids, &compiler));
        let kept = key.as_ref().map(|_| kept_path(&world.root, cmd, manifest));
        if !world.no_reuse
            && key.is_some()
            && kept.as_ref().and_then(|k| std::fs::read_to_string(k).ok()) == key
        {
            let _ = writeln!(
                stdout,
                "rust-checks: {cmd} unchanged on {shown} - its last green result stands"
            );
            continue;
        }
        let done = check(world, cmd, manifest, formatting_check);
        if cmd == "hamlet" {
            stdout.push_str(&done.stdout);
        }
        if done.code == 0 && cmd.starts_with("test") {
            if let Some(summary) = done.stdout.lines().find(|l| l.starts_with("test result:")) {
                let _ = writeln!(stdout, "rust-checks: {cmd} on {shown}: {summary}");
            }
        }
        if done.code != 0 {
            bad += 1;
            let _ = writeln!(
                stderr,
                "rust-checks: {cmd} FAILED on {shown}\n{}{}",
                done.stdout, done.stderr
            );
        } else if let (Some(path), Some(text)) = (&kept, &key) {
            let _ = std::fs::create_dir_all(path.parent().unwrap_or(&world.root));
            let _ = std::fs::write(path, text);
        }
    }
    if bad > 0 {
        let _ = writeln!(
            stderr,
            "rust-checks: {bad} crate(s) failed {cmd} - {}",
            fix_for(cmd)
        );
        return Reply {
            stdout,
            stderr,
            code: 1,
        };
    }
    let _ = writeln!(
        stdout,
        "rust-checks: {cmd} clean on {} crate(s)",
        found.len()
    );
    Reply {
        stdout,
        stderr,
        code: 0,
    }
}

const COMMANDS: [&str; 9] = [
    "lint",
    "format",
    "test",
    "test-counters",
    "test-no-counters",
    "hamlet",
    "cover",
    "dead",
    "uncovered",
];

/// `uncovered --crate X`: the crate's unreached lines as JSON, for `cover_changed.py` until it is ported (T071).
fn uncovered_json(world: &World, named: &[String]) -> Reply {
    let mut all: BTreeMap<String, Vec<u32>> = BTreeMap::new();
    for manifest in crates(&world.root, named) {
        all.extend(uncovered(world, &manifest, &cover_dir(world, &manifest)));
    }
    Reply {
        stdout: serde_json::to_string(&all).unwrap_or_default() + "\n",
        stderr: String::new(),
        code: 0,
    }
}

fn parse(args: &[String]) -> Option<(&str, Vec<String>, bool)> {
    let cmd = args
        .first()
        .map(String::as_str)
        .filter(|c| COMMANDS.contains(c))?;
    let (mut named, mut flag, mut rest) = (Vec::new(), false, args[1..].iter());
    while let Some(word) = rest.next() {
        match word.as_str() {
            "--check" => flag = true,
            "--crate" => named.push(rest.next()?.clone()),
            _ => return None,
        }
    }
    Some((cmd, named, flag))
}

fn cargo_exe(installed: &Path) -> String {
    if installed.is_file() {
        installed.display().to_string()
    } else {
        "cargo".to_owned()
    }
}

fn world_here() -> World {
    let tree = std::env::var_os("L7R_GATE_TREE").map_or_else(crate::top, PathBuf::from);
    let home = PathBuf::from(std::env::var_os("HOME").unwrap_or_default());
    let name = tree
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let cargo_bin = home.join(".cargo/bin/cargo");
    let var = |k: &str| std::env::var(k).unwrap_or_default();
    World {
        target: home.join(".cache/l7r-cargo-target").join(name),
        cargo: cargo_exe(&cargo_bin),
        path_dir: home.join(".cargo/bin"),
        target_override: std::env::var("CARGO_TARGET_DIR").ok(),
        no_reuse: var("INCREMENTAL") == "0" || !var("FULL").is_empty(),
        hamlet_features: var("HAMLET_FEATURES"),
        hamlet_args: var("HAMLET_ARGS"),
        hamlet_spec: var("HAMLET_SPEC"),
        cover_work: std::env::var_os("L7R_RUST_COVER_WORK").map(PathBuf::from),
        root: tree,
    }
}

fn dispatch(world: &World, args: &[String]) -> Reply {
    let Some((cmd, named, flag)) = parse(args) else {
        return Reply {
            stdout: String::new(),
            stderr: format!(
                "usage: l7r-gate rust {{{}}} [--crate DIR]... [--check]\n",
                COMMANDS.join(",")
            ),
            code: 2,
        };
    };
    if cmd == "uncovered" {
        uncovered_json(world, &named)
    } else {
        answer(world, cmd, &named, flag)
    }
}

/// `l7r-gate rust <cmd> [--crate DIR]... [--check]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let world = world_here();
    let reply = dispatch(&world, args);
    crate::stamp::record_for(
        &world.root,
        USAGE_LOG_TOOL,
        if reply.code == 0 { "passed" } else { "refused" },
    );
    reply
}

#[cfg(test)]
mod tests;
