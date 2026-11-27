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
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::Reply;

mod alive;
mod assertline;
mod cover;
mod drain;
mod fmtfile;
mod kept;
mod left;
mod lint;
mod only;
mod phase;
mod prewarm;
mod run;
mod runlock;
mod side;
mod slot;
mod stale;
mod times;
use cover::uncovered_each;
#[cfg(test)]
use kept::{content_ids, declared_reads, relative, verdict_key};
use kept::{
    kept_reads, undeclared, undeclared_refusal, unit_tests_only, Kept, Reads, Told, Verdict,
};
use run::{
    cargo, cargo_call, cargo_in, cargo_small, leak_checked, run, run_in, run_seen, tested, Ran,
};

/// Each run is recorded for `make tool-yield`, as `usage_log` records a Python tool's.
const USAGE_LOG_TOOL: &str = "rust_checks";
const CRATES: &str = "rust";
fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BUILD_HASH: LazyLock<Regex> = LazyLock::new(|| re(r"Cs[0-9A-Za-z]+_|17h[0-9a-f]{16}E"));
static PUB_FN: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\s*pub(?:\([^)]*\))?\s+(?:const\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)"));

/// Where everything runs, read once from the environment.
pub struct World {
    /// The tree, and the environment its guard reads see (feature 451 T38: a test's own, never a session's exports).
    root: l7r_shared::env::Rooted,
    target: PathBuf,
    cargo: String,
    path_dir: PathBuf,
    target_override: Option<String>,
    no_reuse: bool,
    hamlet_features: String,
    hamlet_bin: String,
    hamlet_dev: bool,
    hamlet_args: String,
    hamlet_spec: String,
    cover_work: Option<PathBuf>,
    /// The run's make target, which each step's phase line names (feature 451 T05, `phase.rs`).
    make: String,
    /// The machine's build slots, one held around each cargo call that compiles (feature 451 T284, `slot.rs`).
    slots: slot::Slots,
    /// The small lane beside them, for a test build of one crate alone (feature 451 T347, `slot.rs`, `kept/alone.rs`).
    small: slot::Slots,
    /// A `test` run's filter words (`--only`, `make rust-test ONLY=`, feature 451 T435, `only.rs`): handed to each test binary, the
    /// run kept as no crate's green and its `test` Phase line marked; empty for every other run.
    only: Vec<String>,
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

/// The cargo feature flags naming every feature of the crate but `left_out` (none when that leaves none).
fn features_but(manifest: &Path, left_out: &str) -> Vec<String> {
    let rest: Vec<String> = features(manifest)
        .into_iter()
        .filter(|n| n != left_out)
        .collect();
    if rest.is_empty() {
        Vec::new()
    } else {
        vec!["--features".to_owned(), rest.join(",")]
    }
}

/// The names of the crate's own features (its manifest's `[features]`).
fn features(manifest: &Path) -> Vec<String> {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let section = re(r"(?ms)^\[features\]\n(.*?)(?:^\[|\z)")
        .captures(&text)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    re(r"(?m)^([A-Za-z_][\w-]*)\s*=")
        .captures_iter(&section)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect()
}

/// Does the crate name itself in its `[dev-dependencies]` (`path = "."`, feature 451 T325)? It does so to turn a test-only feature
/// of its own on in its test build, which every pass of the lint that reads `[dev-dependencies]` then has on too.
fn names_itself(manifest: &Path) -> bool {
    let text = std::fs::read_to_string(manifest).unwrap_or_default();
    let section = re(r"(?ms)^\[dev-dependencies\]\n(.*?)(?:^\[|\z)")
        .captures(&text)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    re(r#"(?m)^[\w-]+\s*=.*\bpath\s*=\s*"\.""#)
        .is_match(&section)
        .unwrap_or(false)
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
    let uses = family_words(&family(manifest));
    let names: BTreeSet<String> = PUB_FN
        .captures_iter(&own)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    names
        .into_iter()
        .filter(|n| uses.get(n.as_str()) <= Some(&1))
        .collect()
}

/// Each word of a family's sources and how often it appears. One pass over the text's words, counted once: a Unicode `\b` search per
/// name took hours on the guard crate's thousands of names, where the Python's took seconds. A word is a maximal run of `\w`, as
/// Python's `\b` bounds one.
///
/// COUNTED ONCE A RUN (feature 449 T160): the dead check's key is its whole family (T100), so any gate edit re-ran it on all 27 of the
/// gate's crates, and each counted the family's 6.5 MB again - 5.1-5.8 s of `make static` after a one-crate edit (observed 2026-11-17).
/// The counts are kept for the process by the family and a hash of its text, so the 26 crates after the first read the text and find
/// them, and a text that moved (a test's fixture between its steps) is counted afresh.
fn family_words(dir: &Path) -> std::sync::Arc<BTreeMap<String, usize>> {
    use std::hash::{Hash as _, Hasher as _};
    type Counted = BTreeMap<(PathBuf, u64), std::sync::Arc<BTreeMap<String, usize>>>;
    static COUNTED: std::sync::Mutex<Counted> = std::sync::Mutex::new(BTreeMap::new());
    let rust = rust_text(dir);
    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    rust.hash(&mut hasher);
    let at = (dir.to_path_buf(), hasher.finish());
    let mut counted = COUNTED
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    counted
        .entry(at)
        .or_insert_with(|| {
            let mut uses: BTreeMap<String, usize> = BTreeMap::new();
            for word in rust.split(|c: char| !c.is_alphanumeric() && c != '_') {
                *uses.entry(word.to_owned()).or_default() += 1;
            }
            std::sync::Arc::new(uses)
        })
        .clone()
}

fn tail(text: &str) -> &str {
    let at = text.char_indices().rev().nth(3999).map_or(0, |(i, _)| i);
    &text[at..]
}

fn check(world: &World, cmd: &str, manifest: &Path, formatting_check: bool) -> Ran {
    match cmd {
        // told nothing, so each pass a wide slot: a run's lint is `stepped`'s, which hands the run's content ids on (`lint.rs`)
        "lint" => lint::linted(world, manifest, None),
        "test" | "test-counters" | "test-no-counters" => tested(world, cmd, manifest).0,
        "hamlet" => {
            // `HAMLET_BIN` runs another of the crate's binaries, `HAMLET_DEV` it in the dev profile (feature 449 T224: the work-budget
            // review's Mode A counts, `l7r-mode-a` with its counters, whose dev build shares the test builds' dependencies - 19 s
            // where a release build of its geometry and rendering crates starts from nothing)
            let mut args = vec!["run"];
            if !world.hamlet_dev {
                args.push("--release");
            }
            args.push("--quiet");
            if !world.hamlet_features.is_empty() {
                args.extend(["--features", world.hamlet_features.as_str()]);
            }
            args.extend(["--bin", world.hamlet_bin.as_str()]);
            let after: Vec<&str> = if world.hamlet_args.is_empty() {
                vec![world.hamlet_spec.as_str()]
            } else {
                world.hamlet_args.split_whitespace().collect()
            };
            cargo(world, &args, manifest, &after)
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
            let (mut got, said) = uncovered_each(world, &[&manifest.to_path_buf()]);
            eprint!("{said}");
            cover_ran(&got.remove(manifest).unwrap_or_default())
        }
        _ if formatting_check => cargo(world, &["fmt", "--check"], manifest, &[]),
        // a message the pass put on a line of its own is named here, where it is written, not by a landing's cover (451 T114)
        _ => assertline::format_crate(world, manifest),
    }
}

/// A test run's `cargo test` words: the counting build's every feature, the counting-free one's every feature but `counters`; `no_run`
/// its build alone, the same build the run then finds fresh.
fn test_args(cmd: &str, manifest: &Path, no_run: bool) -> Vec<String> {
    let mut args = own(&["test"]);
    if no_run {
        args.push("--no-run".to_owned());
    }
    args.push("--quiet".to_owned());
    match cmd {
        "test-counters" => args.push("--all-features".to_owned()),
        "test-no-counters" => args.extend(features_but(manifest, "counters")),
        _ => {}
    }
    args
}

/// `check`, its phase line written where it is a step of its own (feature 451 T05, `phase::step_of`): here, in `answer`'s loop, and not
/// inside `check`, whose coverage run writes its own lines in `uncovered_each`.
///
/// A TEST RUN'S BUILD BOOKED APART (feature 451 T05; the plan review 2026-11-20, the GM: "how much time are we spending on recompiling
/// things"): the `cargo test` run here - a fresh run, `test-no-counters` - compiled inside its one call, and a fresh run is where a
/// crate compiles from cold. Its build is asked first, `--no-run` with the run's own words, and booked `build`; the run then finds it
/// fresh and is booked `test`. A build that fails is the crate's answer, in cargo's own words, and nothing runs after it. Where the
/// binary key's build ran and passed (`built`: a build that named no binary), it wrote the `build` line and the run compiles nothing,
/// so no build is asked again; where it failed, the build is asked again here, so the failure reads as cargo's and not as JSON -
/// in the lane the binary key's build was told (`told`, feature 451 T347), so a red build of one crate alone waits on no wide slot.
///
/// A LINT IS TOLD PASS BY PASS (feature 451 T355, `lint.rs`), from the run's content ids (`inputs`), inside its `lint` line's span.
fn stepped(
    world: &World,
    cmd: &str,
    manifest: &Path,
    formatting_check: bool,
    (built, told): (bool, &Told),
    inputs: Option<&Kept>,
) -> Ran {
    if phase::step_of(cmd) == Some("test") && !built {
        let words = test_args(cmd, manifest, true);
        let args: Vec<&str> = words.iter().map(String::as_str).collect();
        let began = std::time::SystemTime::now();
        // a link on a session a killed build left mixed is healed and asked once more (`stale.rs`, feature 451 T336)
        let built = stale::built(world, &args, manifest, told);
        phase::wrote(world, "build", &[manifest], began, built.code);
        if built.code != 0 {
            return built;
        }
    }
    let began = std::time::SystemTime::now();
    let (done, caught) = match phase::step_of(cmd) {
        _ if cmd == "lint" => (lint::linted(world, manifest, inputs), None),
        // a test run past its bound is recorded alive, its record named on its line (`alive.rs`, feature 451 T463)
        Some("test") => tested(world, cmd, manifest),
        _ => (check(world, cmd, manifest, formatting_check), None),
    };
    if let Some(step) = phase::step_of(cmd) {
        phase::wrote_alive(
            world,
            step,
            &[manifest],
            began,
            done.code,
            caught.as_deref(),
        );
    }
    done
}

/// A crate's coverage verdict: each file with the lines no test reaches.
fn cover_ran(got: &BTreeMap<String, Vec<u32>>) -> Ran {
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

fn fix_for(cmd: &str) -> &'static str {
    match cmd {
        "lint" => "fix what clippy names (an exception is `#[expect(lint, reason = \"...\")]`)",
        "format" => "run `make format CRATE=<dir>` (or `FILE=<path>`, one file alone; bare `make format` rewrites every crate); where it names an assert's message on a line of its own, bind the values to locals first so the assert fits one line",
        "test" => "fix the failing test cargo names",
        "cover" => "test the lines llvm-cov names, from the crate's tests",
        "dead" => "delete the pub fn it names, or call it",
        "hamlet" => "fix the stage or the spec the driver names above",
        "test-no-counters" => "fix the test whose result hangs on the counters",
        _ => "fix the test the counting build fails: a count's assertion, or a result the counters change",
    }
}

/// A crate's directory as the checks name it, from the tree's root.
fn shown(world: &World, manifest: &Path) -> String {
    let dir = manifest.parent().unwrap_or(&world.root);
    dir.strip_prefix(&world.root)
        .unwrap_or(Path::new(""))
        .display()
        .to_string()
}

/// A green result kept: `make format` rewrites the files its key was read from, so only a check's is; a coverage pass keeps the crate's
/// tests' too where they are all its `cargo test` runs (T111); a filtered test run keeps none (451 T435).
fn keep_green(
    world: &World,
    cmd: &str,
    manifest: &Path,
    verdict: Verdict,
    inputs: Option<&Kept>,
    formatting_check: bool,
) {
    // a filtered run is a part of the crate's tests: no green kept, so the next whole run runs it (`only.rs`, 451 T435)
    if (cmd == "format" && !formatting_check) || !world.only.is_empty() {
        return;
    }
    verdict.keep();
    if let Some(k) = inputs.filter(|_| cmd == "cover" && unit_tests_only(manifest)) {
        Verdict::keep_tests(world, manifest, k);
    }
}

/// The runs of every owed crate that go together rather than a crate at a time: the coverage (T105, T108) and the tests (feature 449
/// T160, `side.rs`); a counting-free run (`test-no-counters`) keeps no result, and goes a crate at a time.
fn owed_together(
    world: &World,
    cmd: &str,
    asked: &[(&PathBuf, Option<(Verdict, bool)>)],
) -> BTreeMap<PathBuf, Ran> {
    match cmd {
        "cover" => owed_coverage(world, asked)
            .into_iter()
            .map(|(m, got)| (m, cover_ran(&got)))
            .collect(),
        "test" | "test-counters" => side::tests_side_by_side(world, cmd, asked),
        _ => BTreeMap::new(),
    }
}

/// The coverage of every crate whose kept result does not stand, run together (T105, T108).
fn owed_coverage(
    world: &World,
    asked: &[(&PathBuf, Option<(Verdict, bool)>)],
) -> BTreeMap<PathBuf, BTreeMap<String, Vec<u32>>> {
    let owed: Vec<&PathBuf> = asked
        .iter()
        .filter(|(_, a)| a.as_ref().is_some_and(|(_, stands)| !stands))
        .map(|(m, _)| *m)
        .collect();
    let (got, said) = uncovered_each(world, &owed);
    eprint!("{said}");
    got
}

/// THE CALLER'S FILES (feature 451 T86): a file listing, one path a line from the tree's root, the files of the task whose `make
/// closing-checks` runs this check - the clone's uncommitted files less those another task's edits alone name (`closing-checks.sh`). WHY:
/// about 12 of 2026-11-21's closing runs went red only on another builder's half-done files in the same clone, measured 2026-11-21 (the
/// night's closing runs, T86's plan section). Only that script sets it, so `make static`, `make done` and a landing judge every crate.
const CALLER: &str = "L7R_RUST_CALLER";

/// Is a red crate the caller's: no caller named (every crate is), the listing unreadable, a check with no kept key, or a key that reads
/// one of the caller's files - its own, a crate's it builds from, a file its tests read or compile in, its family's for the dead check.
fn caller_reads(world: &World, cmd: &str, manifest: &Path, inputs: Option<&Kept>) -> bool {
    let Some(listing) = world.root.opt(CALLER).filter(|v| !v.is_empty()) else {
        return true;
    };
    // outside a repository the tree's ids are empty: no key can say what it reads
    let (Ok(text), Some(kept)) = (
        std::fs::read_to_string(listing),
        inputs.filter(|k| !k.ids.is_empty()),
    ) else {
        return true;
    };
    let files: BTreeSet<String> = text.lines().map(str::to_owned).collect();
    kept.reads_any(&world.root, cmd, manifest, &files)
}

/// A green test run's line for its crate: the first binary's summary, or a filtered run's count, a filter that ran no test made
/// its crate's failure (`only.rs`, feature 451 T435).
fn test_line(world: &World, cmd: &str, shown: &str, done: &mut Ran, stdout: &mut String) {
    if done.code != 0 {
        return;
    }
    if !world.only.is_empty() {
        only::judge(world, shown, done, stdout);
    } else if cmd.starts_with("test") {
        if let Some(summary) = done.stdout.lines().find(|l| l.starts_with("test result:")) {
            let _ = writeln!(stdout, "rust-checks: {cmd} on {shown}: {summary}");
        }
    }
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
    let reads = kept_reads(cmd);
    if reads == Some(Reads::Tests) {
        let blind = undeclared(&found);
        if !blind.is_empty() {
            return undeclared_refusal(world, &blind);
        }
    }
    let inputs = reads.map(|r| Kept::read(world, cmd, r, &found));
    let (mut bad, mut apart) = (0, 0);
    // every crate's kept result asked first, so the coverage the rest owe is built together (T105) and run side by side (T108)
    let asked: Vec<(&PathBuf, Option<(Verdict, bool)>)> = found
        .iter()
        .map(|manifest| {
            // THE COUNTING BUILD IS RUN ONLY WHERE THERE IS ONE (feature 449 T97): a crate with no `counters` feature builds the same
            // with `--all-features` as without (core's one other, `testkit`, is on in its test build already), so its counting build
            // was its default test build run a second time - every gate crate and the guard, 59-113 s of a landing's `make done`
            // (2026-11-11), whose tests `make static`'s `cover` runs anyway. Only a crate with the feature has counters to prove inert.
            let counted =
                cmd != "test-counters" || features(manifest).iter().any(|f| f == "counters");
            let ask = counted.then(|| Verdict::ask(world, cmd, manifest, inputs.as_ref()));
            (manifest, ask)
        })
        .collect();
    let mut together = owed_together(world, cmd, &asked);
    for (manifest, ask) in asked {
        let shown = shown(world, manifest);
        let Some((verdict, stands)) = ask else {
            let _ = writeln!(
                stdout,
                "rust-checks: test-counters passes over {shown} - no counters feature, so its counting build is its default one"
            );
            continue;
        };
        if stands {
            let _ = writeln!(
                stdout,
                "rust-checks: {cmd} unchanged on {shown} - its last green result stands"
            );
            continue;
        }
        let (lane, ids) = ((verdict.built, &verdict.told), inputs.as_ref());
        let mut done = together
            .remove(manifest)
            .unwrap_or_else(|| stepped(world, cmd, manifest, formatting_check, lane, ids));
        if cmd == "hamlet" {
            stdout.push_str(&done.stdout);
        }
        test_line(world, cmd, &shown, &mut done, &mut stdout);
        if done.code != 0 {
            let counted = caller_reads(world, cmd, manifest, inputs.as_ref());
            *if counted { &mut bad } else { &mut apart } += 1;
            let said = if counted {
                format!("rust-checks: {cmd} FAILED on {shown}")
            } else {
                format!("rust-checks: APART {cmd} red on {shown} - another task's: its {cmd} key reads none of this task's files ({CALLER}, 451 T86), so not counted")
            };
            let _ = writeln!(stderr, "{said}\n{}{}", done.stdout, done.stderr);
        } else {
            // a pipe a leftover process held past its program's exit is said on a green crate too (451 T364, `drain.rs`)
            stderr.push_str(&drain::held_on(&shown, &done.stderr));
            keep_green(
                world,
                cmd,
                manifest,
                verdict,
                inputs.as_ref(),
                formatting_check,
            );
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
    let clean = found.len() - apart;
    let _ = match apart {
        0 => writeln!(stdout, "rust-checks: {cmd} clean on {clean} crate(s)"),
        _ => writeln!(stdout, "rust-checks: {cmd} clean on {clean} crate(s) of this task's; {apart} red on another task's files alone, reported apart"),
    };
    stdout.push_str(&only::noted(world));
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
    let found = crates(&world.root, named);
    let (got, said) = uncovered_each(world, &found.iter().collect::<Vec<_>>());
    eprint!("{said}");
    all.extend(got.into_values().flatten());
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
            // a filtered run is a `test` run's alone (`only.rs`, feature 451 T435): the rest keep results a part would stand in for
            only::FLAG if cmd == "test" => {
                only::words(rest.next()?)?;
            }
            _ => return None,
        }
    }
    // a filter with no crate is refused, its message `only::uncrated`'s (feature 451 T435)
    only::uncrated(args).is_none().then_some((cmd, named, flag))
}

fn cargo_exe(installed: &Path) -> String {
    if installed.is_file() {
        installed.display().to_string()
    } else {
        "cargo".to_owned()
    }
}

/// The run's target directory: the one `CARGO_TARGET_DIR` gives (not empty), else the tree's in the home cache. WHY THE GIVEN ONE
/// (451 T440): the run lock and its record (`runlock.rs`), the coverage families' directories and the pre-warm's lock are written under
/// this; taken from home whatever was given, a run with HOME elsewhere and a scratch target wrote them under the real HOME's cache, a
/// directory its cargo never built in (451 T312's empty-HOME proof, 2026-11-27).
fn target_of(home: &Path, tree: &str, set: Option<&str>) -> PathBuf {
    set.filter(|s| !s.is_empty()).map_or_else(
        || home.join(".cache/l7r-cargo-target").join(tree),
        PathBuf::from,
    )
}

fn world_here(make: String) -> World {
    let tree = std::env::var_os("L7R_GATE_TREE").map_or_else(crate::top, PathBuf::from);
    let home = PathBuf::from(std::env::var_os("HOME").unwrap_or_default());
    let name = tree
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let cargo_bin = home.join(".cargo/bin/cargo");
    let var = |k: &str| std::env::var(k).unwrap_or_default();
    let root = l7r_shared::env::Rooted::process(tree);
    World {
        slots: slot::Slots::of(root.reader(), &home),
        small: slot::Slots::small(root.reader(), &home),
        target: target_of(
            &home,
            &name,
            std::env::var("CARGO_TARGET_DIR").ok().as_deref(),
        ),
        cargo: cargo_exe(&cargo_bin),
        path_dir: home.join(".cargo/bin"),
        target_override: std::env::var("CARGO_TARGET_DIR").ok(),
        // every crate run fresh only through the make escape `FRESH=1 REASON="..."`, which records why, or `make done FULL=1`'s own
        // logged path (feature 449 T93): `INCREMENTAL=0` and `FULL` turned reuse off silently
        no_reuse: !var("L7R_RUST_FRESH").is_empty(),
        hamlet_features: var("HAMLET_FEATURES"),
        hamlet_bin: Some(var("HAMLET_BIN"))
            .filter(|b| !b.is_empty())
            .unwrap_or_else(|| "hamlet".to_owned()),
        hamlet_dev: !var("HAMLET_DEV").is_empty(),
        hamlet_args: var("HAMLET_ARGS"),
        hamlet_spec: var("HAMLET_SPEC"),
        cover_work: std::env::var_os("L7R_RUST_COVER_WORK").map(PathBuf::from),
        make,
        root,
        only: Vec::new(),
    }
}

fn dispatch(world: &World, args: &[String]) -> Reply {
    // `make format FILE=<path>` (feature 451 T34, `fmtfile.rs`): the files named, alone
    if args.iter().any(|a| a == "--file") {
        return fmtfile::format_files(world, args);
    }
    // `test-times` (feature 449 T169) times tests and keeps no result, so it is not one of the checks `parse` reads
    if args.first().map(String::as_str) == Some("test-times") {
        let mut rest = args.to_vec();
        "test".clone_into(&mut rest[0]);
        if let Some((_, named, false)) = parse(&rest).filter(|_| only::of(&rest).is_empty()) {
            return times::test_times(world, &named, times::BAR, times::RUNS);
        }
    }
    let Some((cmd, named, flag)) = parse(args) else {
        return Reply {
            stdout: String::new(),
            stderr: only::uncrated(args).unwrap_or_else(|| format!(
                "usage: l7r-gate rust {{{}}} [--crate DIR]... [--check]\n       l7r-gate rust test --crate DIR... --only \"FILTER ...\"\n       l7r-gate rust format --file PATH... [--check]\n       l7r-gate rust test-times --crate DIR...\n",
                COMMANDS.join(",")
            )),
            code: 2,
        };
    };
    if cmd == "uncovered" {
        uncovered_json(world, &named)
    } else {
        answer(world, cmd, &named, flag)
    }
}

/// THE RUN'S LOCK (feature 451 T23, `rustc/runlock.rs`): a check holds every directory it writes for its whole length, shared with
/// the checks of its own run (the outermost `make`), waited for by another run's; a usage error writes nothing and takes none.
fn locked_dispatch(world: &World, args: &[String], taker: &runlock::Taker) -> Reply {
    let mut words = args.to_vec();
    if let Some(first) = words.first_mut().filter(|w| *w == "test-times") {
        "test".clone_into(first);
    }
    // a usage error writes nothing, and nor does a one-file format (`--file`, which `parse` does not read, T34): neither takes the lock
    if parse(&words).is_none() {
        return dispatch(world, args);
    }
    let held = runlock::take(&runlock::dirs_of(world), taker, &args[0], &mut |line| {
        eprint!("{line}");
    });
    match held {
        Ok(_held) => dispatch(world, args),
        Err(why) => Reply {
            stdout: String::new(),
            stderr: why,
            code: 1,
        },
    }
}

/// `l7r-gate rust <cmd> [--crate DIR]... [--check]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let cmd = args.first().map_or("", String::as_str);
    // the pre-warm (feature 451 T316, `prewarm.rs`) is no run of the checks: it joins no run's lock - a real run in its tree is what
    // ends it - and its phase lines name it, never the `make builder-tree` that started it and is gone
    if cmd == prewarm::STEP {
        let world = world_here(prewarm::STEP.to_owned());
        return prewarm::run(&world, &args[1..], &prewarm::Knobs::of(&world));
    }
    let taker = runlock::Taker::here();
    // the filter is read from the arguments alone, never the environment: make exports `ONLY=` to every recipe, and only
    // `make rust-test` hands it on (feature 451 T435)
    let world = World {
        only: only::of(args),
        ..world_here(phase::run_target(&taker.run_what, cmd))
    };
    let reply = locked_dispatch(&world, args, &taker);
    crate::stamp::record_for(
        &world.root,
        USAGE_LOG_TOOL,
        if reply.code == 0 { "passed" } else { "refused" },
    );
    reply
}

#[cfg(test)]
mod tests;
