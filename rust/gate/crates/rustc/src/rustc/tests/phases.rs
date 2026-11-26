//! The checks' phase lines (feature 451 T05, plan D4, FR-003): each step a check runs - a test binary's build, its run, a family's
//! coverage build, a crate's coverage run, a lint, a format - writes one `Phase` line to the event log with its wall-clock span, so a
//! `make static`'s compile and tests are told apart; a kept result ran nothing and writes none.

use serde_json::Value;

use super::side::built;
use super::*;
use crate::Reply;
use l7r_shared::guards::event_log_hooks::now_stamp;

/// Every `Phase` line in the tree's event logs, in the order written (the log a line is filed in is the process's feature's, so every
/// log is read).
pub(super) fn phases(root: &Path) -> Vec<Value> {
    let mut logs: Vec<PathBuf> = std::fs::read_dir(root.join(".git/l7r-events"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    logs.sort();
    logs.iter()
        .flat_map(|p| {
            std::fs::read_to_string(p)
                .unwrap_or_default()
                .lines()
                .filter_map(|l| serde_json::from_str::<Value>(l).ok())
                .collect::<Vec<_>>()
        })
        .filter(|v| v["ev"] == "Phase")
        .collect()
}

/// The lines one call wrote: those past the `before` already there, each a rust phase of this tree whose span lies inside the call's.
fn during(root: &Path, before: usize, go: impl FnOnce() -> Reply) -> (Reply, Vec<Value>) {
    let began = now_stamp(std::time::SystemTime::now());
    let reply = go();
    let ended = now_stamp(std::time::SystemTime::now());
    let new: Vec<Value> = phases(root).into_iter().skip(before).collect();
    for line in &new {
        let (t0, t1) = (line["t0"].as_str().unwrap(), line["t1"].as_str().unwrap());
        assert!(
            began.as_str() <= t0 && t0 <= t1 && t1 <= ended.as_str(),
            "{line} outside {began}..{ended}"
        );
        assert_eq!(line["src"], "rust", "{line}");
        assert_eq!(line["t"], line["t1"], "{line}");
        assert_eq!(line["clone"], root.display().to_string(), "{line}");
    }
    (reply, new)
}

/// Each line's step and crates, sorted (the side-by-side runs finish in any order).
fn steps(lines: &[Value]) -> Vec<(String, Vec<String>, i64)> {
    let mut got: Vec<(String, Vec<String>, i64)> = lines
        .iter()
        .map(|l| {
            let crates = l["crates"]
                .as_array()
                .unwrap()
                .iter()
                .map(|c| c.as_str().unwrap().to_owned())
                .collect();
            (
                l["step"].as_str().unwrap().to_owned(),
                crates,
                l["code"].as_i64().unwrap(),
            )
        })
        .collect();
    got.sort();
    got
}

fn step(name: &str, krate: &str, code: i64) -> (String, Vec<String>, i64) {
    (name.to_owned(), vec![krate.to_owned()], code)
}

#[test]
fn a_test_run_writes_each_crate_s_build_and_its_run_and_a_kept_result_writes_none() {
    let (root, world) = built("phases");
    let (done, lines) = during(&root, 0, || answer(&world, "test", &[], false));
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [
            step("build", "rust/a", 0),
            step("build", "rust/b", 0),
            step("test", "rust/a", 0),
            step("test", "rust/b", 0),
        ]
    );
    assert!(lines.iter().all(|l| l["make"] == "static"), "{lines:?}");
    // nothing moved: the kept result stands, nothing ran, nothing is written
    let (again, lines) = during(&root, 4, || answer(&world, "test", &[], false));
    assert!(again.stdout.contains("test unchanged on rust/a"));
    assert_eq!(lines, Vec::<Value>::new());
}

#[test]
fn a_fresh_test_run_books_its_build_apart_and_lint_and_format_one_line_a_crate() {
    let (root, world) = built("phases-fresh");
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    // a fresh run compiles from cold: its `cargo test`'s build is asked first, `--no-run`, and booked `build`; the run that follows
    // compiles nothing and is booked `test` (the plan review, 2026-11-20: the GM asked how much time goes to recompiling)
    let (done, lines) = during(&root, 0, || {
        answer(&fresh, "test", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [step("build", "rust/a", 0), step("test", "rust/a", 0)]
    );
    let asked: Vec<String> = calls(&fresh)
        .into_iter()
        .filter(|c| c.starts_with("test"))
        .collect();
    assert!(
        asked[0].starts_with("test --no-run --quiet --manifest-path")
            && asked[1].starts_with("test --quiet --manifest-path"),
        "{asked:?}"
    );
    assert!(lines[0]["t1"].as_str() <= lines[1]["t0"].as_str());
    let (done, lines) = during(&root, 2, || answer(&fresh, "lint", &[], false));
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [step("lint", "rust/a", 0), step("lint", "rust/b", 0)]
    );
    let (done, lines) = during(&root, 4, || answer(&fresh, "format", &[], true));
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [step("format", "rust/a", 0), step("format", "rust/b", 0)]
    );
    // a check that runs no cargo writes none
    let (_, lines) = during(&root, 6, || answer(&fresh, "dead", &[], false));
    assert_eq!(lines, Vec::<Value>::new());
}

/// The counting-free run (`make counters-inert`'s `test-no-counters`) is split as a fresh run is, with its own features on both calls;
/// a build that fails is booked `build` with its code, and nothing runs after it.
#[test]
fn a_counting_free_run_books_its_build_apart_and_a_failed_build_runs_nothing() {
    let (root, world) = built("phases-no-counters");
    std::fs::write(
        root.join("rust/a/Cargo.toml"),
        "[package]\nname = \"pkg-a\"\n\n[features]\ncounters = []\nother = []\n",
    )
    .unwrap();
    let (done, lines) = during(&root, 0, || {
        answer(&world, "test-no-counters", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [step("build", "rust/a", 0), step("test", "rust/a", 0)]
    );
    let asked: Vec<String> = calls(&world)
        .into_iter()
        .filter(|c| c.starts_with("test"))
        .collect();
    assert!(
        asked[0].starts_with("test --no-run --quiet --features other --manifest-path")
            && asked[1].starts_with("test --quiet --features other --manifest-path"),
        "{asked:?}"
    );
    let broken = world_with(&root, "exit 101");
    let (done, lines) = during(&root, 2, || {
        answer(&broken, "test-no-counters", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 1);
    assert_eq!(steps(&lines), [step("build", "rust/a", 101)]);
    assert_eq!(calls(&broken).len(), 1, "{:?}", calls(&broken));
}

/// A build that named no binary (feature 451 T05): the binary key's build passed and wrote its `build` line, so the `cargo test` after
/// it compiles nothing, is booked `test` alone, and no build is asked again.
#[test]
fn a_build_that_named_no_binary_is_booked_once_and_its_run_alone() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "exit 0");
    let (done, lines) = during(&root, 0, || {
        answer(&world, "test", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [step("build", "rust/a", 0), step("test", "rust/a", 0)]
    );
    let builds: Vec<String> = calls(&world)
        .into_iter()
        .filter(|c| c.starts_with("test --no-run"))
        .collect();
    assert_eq!(builds.len(), 1, "{builds:?}");
    assert!(builds[0].starts_with("test --no-run --message-format=json"));
}

#[test]
fn a_coverage_run_writes_its_family_s_build_and_each_crate_s_run() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, LCOV_CARGO);
    std::fs::write(world.target.join("lcov"), "").unwrap();
    let (done, lines) = during(&root, 0, || {
        answer(&world, "cover", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        steps(&lines),
        [
            step("cover-build", "rust/a", 0),
            step("cover-run", "rust/a", 0)
        ]
    );
    // a failing crate's run says its code
    std::fs::write(world.target.join("failtest"), "").unwrap();
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    let (_, lines) = during(&root, 2, || {
        answer(&fresh, "cover", &["rust/a".to_owned()], false)
    });
    assert_eq!(
        steps(&lines),
        [
            step("cover-build", "rust/a", 0),
            step("cover-run", "rust/a", 1)
        ]
    );
}

#[test]
fn a_failed_build_writes_its_build_and_no_run() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "exit 101");
    let (done, lines) = during(&root, 0, || {
        answer(&world, "cover", &["rust/a".to_owned()], false)
    });
    assert_eq!(done.code, 1);
    assert_eq!(steps(&lines), [step("cover-build", "rust/a", 101)]);
}

#[test]
fn the_run_s_target_is_its_make_s_first_goal_or_the_gate_s_own_form() {
    use super::super::phase::{run_target, step_of};
    assert_eq!(run_target("make static", "test"), "static");
    assert_eq!(
        run_target("make -j 4 FRESH=1 rust-test CRATE=x", "test"),
        "rust-test"
    );
    assert_eq!(
        run_target("/home/u/.cache/l7r-rust test --crate a", "test"),
        "rust-test"
    );
    // a goal-less make names no goal (feature 451 T15: `invoked` reads it as `.DEFAULT_GOAL`)
    assert_eq!(run_target("make -j 4", "lint"), "rust-lint");
    assert_eq!(step_of("test-counters"), Some("test"));
    assert_eq!(step_of("cover"), None);
}
