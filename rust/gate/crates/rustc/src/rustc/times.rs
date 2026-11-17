//! `make test-times CRATE=<dir>` (feature 449 T169): every test of a crate timed alone by T99's method, and those over FR-008's tenth
//! of a second listed - the crate's declared end-to-end tests marked as such.
//!
//! WHY: FR-008 holds each test under a tenth of a second, its one end-to-end test against the real command aside, and the method that
//! measures it is T99's - each test alone (`--exact`), best of three, a fresh `TMPDIR` each run, timed around the process. T160, T164,
//! T167 and T168 each timed their tests by hand to that method (T168's frictions, `specs/449-rust-codebase/plan-done.md`); this is the
//! one tool. It REPORTS and never refuses on a time (the GM's performance rule: time is never a gate): it exits 0 whatever it measured,
//! 1 only where it could time nothing (a build that failed), 2 on a malformed command line.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;
use std::time::Instant;

use l7r_guard::shared::tempdir::TempDir;

use super::cover::package_name;
use super::kept::test_targets;
use super::{cargo_in, crates, own, run_in, rust_sources, Ran, World};
use crate::Reply;

/// FR-008's bar, in seconds.
pub(super) const BAR: f64 = 0.1;
/// T99's method: best of three.
pub(super) const RUNS: usize = 3;
/// The doc comment that declares a test FR-008's one end-to-end test (the round arbiter's `ask:449-T167-realtree`).
pub(super) const END_TO_END: &str = "/// FR-008's one end-to-end test (ask:449-T167-realtree):";

/// One test's time: its name, the best of its runs, whether its last run passed.
struct Timed {
    name: String,
    best: f64,
    passed: bool,
}

/// The names of the functions the crate's sources declare end-to-end: the first `fn` after each marker line.
fn end_to_end(dir: &Path) -> BTreeSet<String> {
    let mut files = Vec::new();
    rust_sources(&dir.join("src"), &mut files);
    rust_sources(&dir.join("tests"), &mut files);
    let mut out = BTreeSet::new();
    for file in files {
        let text = std::fs::read_to_string(&file).unwrap_or_default();
        let mut marked = false;
        for line in text.lines().map(str::trim) {
            if line.starts_with(END_TO_END) {
                marked = true;
            } else if let Some(rest) = line.strip_prefix("fn ").filter(|_| marked) {
                out.insert(rest.split(['(', '<']).next().unwrap_or_default().to_owned());
                marked = false;
            }
        }
    }
    out
}

/// What a test binary runs with: cargo's variables, as `cargo test` and `run_built` (T160) give them, and `PATH` with cargo's own bin
/// directory first; the run's `TMPDIR` is added per run.
fn test_env(world: &World, manifest: &Path) -> BTreeMap<String, String> {
    let dir = manifest.parent().unwrap_or(Path::new("."));
    let target = world
        .target_override
        .clone()
        .unwrap_or_else(|| world.target.display().to_string());
    BTreeMap::from([
        (
            "PATH".to_owned(),
            format!(
                "{}:{}",
                world.path_dir.display(),
                std::env::var("PATH").unwrap_or_default()
            ),
        ),
        ("CARGO_TARGET_DIR".to_owned(), target),
        ("CARGO".to_owned(), world.cargo.clone()),
        ("CARGO_MANIFEST_DIR".to_owned(), dir.display().to_string()),
        (
            "CARGO_PKG_NAME".to_owned(),
            package_name(manifest).unwrap_or_default(),
        ),
    ])
}

/// Each test of one binary, timed alone `runs` times, the best kept.
fn time_binary(dir: &Path, exe: &str, env: &BTreeMap<String, String>, runs: usize) -> Vec<Timed> {
    let listed = run_in(Some(dir), exe, &own(&["--list", "--format", "terse"]), env);
    let names: Vec<String> = listed
        .stdout
        .lines()
        .filter_map(|l| l.strip_suffix(": test"))
        .map(str::to_owned)
        .collect();
    names
        .into_iter()
        .map(|name| {
            let (mut best, mut passed) = (f64::INFINITY, false);
            for _ in 0..runs.max(1) {
                // a fresh TMPDIR each run (T99's method), removed after it however the test ended
                let tmp = TempDir::new("test-times");
                let mut env = env.clone();
                env.insert("TMPDIR".to_owned(), tmp.display().to_string());
                let args = own(&["--exact", &name, "-q", "--test-threads=1"]);
                let start = Instant::now();
                let ran = run_in(Some(dir), exe, &args, &env);
                best = best.min(start.elapsed().as_secs_f64());
                passed = ran.code == 0;
            }
            Timed { name, best, passed }
        })
        .collect()
}

/// One crate: its tests built, listed and timed; the build's failure as a `Ran`.
fn time_crate(world: &World, manifest: &Path, runs: usize) -> Result<Vec<Timed>, Ran> {
    let args = ["test", "--no-run", "--message-format=json", "--quiet"];
    let built = cargo_in(world, &args, manifest, &[], None);
    if built.code != 0 {
        return Err(built);
    }
    let dir = manifest.parent().unwrap_or(Path::new("."));
    let env = test_env(world, manifest);
    Ok(test_targets(&built.stdout)
        .iter()
        .flat_map(|exe| time_binary(dir, exe, &env, runs))
        .collect())
}

fn shown(root: &Path, manifest: &Path) -> String {
    let dir = manifest.parent().unwrap_or(root);
    dir.strip_prefix(root).unwrap_or(dir).display().to_string()
}

/// One crate's report: every test over `bar` (the declared end-to-end ones marked), the slowest under it, and the counts.
fn report(
    out: &mut String,
    crate_dir: &str,
    mut timed: Vec<Timed>,
    e2e: &BTreeSet<String>,
    (bar, runs): (f64, usize),
) {
    // slowest first, a tie in name order (the sort is stable)
    timed.sort_by(|a, b| a.name.cmp(&b.name));
    timed.sort_by(|a, b| b.best.total_cmp(&a.best));
    let is_e2e = |t: &Timed| e2e.contains(t.name.rsplit("::").next().unwrap_or_default());
    let over: Vec<&Timed> = timed.iter().filter(|t| t.best >= bar).collect();
    let _ = writeln!(
        out,
        "test-times: {crate_dir}: {} test(s), each alone (--exact), best of {runs}, a fresh TMPDIR each run, timed around the process; FR-008's bar {bar:.3} s",
        timed.len()
    );
    for t in &over {
        let mark = if is_e2e(t) {
            "  (declared end-to-end, ask:449-T167-realtree - FR-008 exempts it)"
        } else {
            ""
        };
        let _ = writeln!(out, "  OVER {:.3} s  {}{mark}", t.best, t.name);
    }
    for t in timed.iter().filter(|t| t.best < bar).take(3) {
        let _ = writeln!(out, "       {:.3} s  {}", t.best, t.name);
    }
    for t in timed.iter().filter(|t| !t.passed) {
        let _ = writeln!(
            out,
            "  FAILED {} - its time is listed; whether it passes is `make rust-test`'s to say",
            t.name
        );
    }
    let declared = over.iter().filter(|t| is_e2e(t)).count();
    let _ = writeln!(
        out,
        "test-times: {crate_dir}: {} over the bar, {declared} of them declared end-to-end; {} under",
        over.len(),
        timed.len() - over.len()
    );
}

/// `l7r-gate rust test-times --crate DIR...`, timed against `bar` with `runs` runs a test: the report on stdout; exit 0 whatever the
/// times, 1 when a crate's tests did not build, 2 with no crate named.
pub(super) fn test_times(world: &World, named: &[String], bar: f64, runs: usize) -> Reply {
    if named.is_empty() {
        return Reply {
            stdout: String::new(),
            stderr: "usage: make test-times CRATE=<crate dir> (l7r-gate rust test-times --crate DIR...): each test of the crate timed alone, best of three\n".to_owned(),
            code: 2,
        };
    }
    let (mut stdout, mut stderr, mut code) = (String::new(), String::new(), 0);
    for manifest in crates(&world.root, named) {
        let crate_dir = shown(&world.root, &manifest);
        match time_crate(world, &manifest, runs) {
            Ok(timed) => {
                let e2e = end_to_end(manifest.parent().unwrap_or(Path::new(".")));
                report(&mut stdout, &crate_dir, timed, &e2e, (bar, runs));
            }
            Err(built) => {
                code = 1;
                let _ = writeln!(
                    stderr,
                    "test-times: {crate_dir}: the tests did not build, so nothing was timed - fix what cargo names:\n{}{}",
                    built.stdout, built.stderr
                );
            }
        }
    }
    Reply {
        stdout,
        stderr,
        code,
    }
}
