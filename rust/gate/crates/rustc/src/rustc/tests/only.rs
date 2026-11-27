//! A builder's filtered test run (feature 451 T435, `only.rs`): the filter reaches every test binary, the run is kept as no crate's
//! green, and its `test` Phase line is marked.

use serde_json::Value;

use super::phases::phases;
use super::side::built;
use super::*;

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

fn only(world: Held<World>, words: &[&str]) -> Held<World> {
    world.map(|w| World {
        only: args(words),
        ..w
    })
}

fn kept(root: &Path, name: &str) -> bool {
    root.join(".git/rust-checks").join(name).exists()
}

fn exes(world: &World) -> Vec<String> {
    let mut ran: Vec<String> = calls(world)
        .into_iter()
        .filter(|c| c.starts_with("exe "))
        .collect();
    ran.sort();
    ran
}

#[test]
fn the_filter_is_a_test_run_s_alone_and_a_flag_is_no_filter() {
    let parsed = args(&["test", "--crate", "x", "--only", "land::carry  land::phase"]);
    assert_eq!(parse(&parsed), Some(("test", vec!["x".to_owned()], false)));
    assert_eq!(
        super::super::only::of(&parsed),
        ["land::carry", "land::phase"]
    );
    assert!(super::super::only::of(&args(&["test", "--crate", "x"])).is_empty());
    for refused in [
        &["test", "--only"][..],
        &["test", "--only", ""],
        &["test", "--only", "carry --exact"],
        &["lint", "--only", "carry"],
        &["test-counters", "--only", "carry"],
        &["cover", "--only", "carry"],
    ] {
        assert_eq!(parse(&args(refused)), None, "{refused:?}");
    }
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    let usage = dispatch(
        &world,
        &args(&["test-times", "--crate", "rust/a", "--only", "x"]),
    );
    assert_eq!(usage.code, 2);
    assert!(usage
        .stderr
        .contains("l7r-gate rust test --crate DIR... --only \"FILTER ...\""));
    assert!(calls(&world).is_empty());
}

#[test]
fn a_filtered_run_reaches_each_binary_and_keeps_no_green_so_the_next_whole_run_runs_the_crate() {
    let (root, world) = built("only");
    let world = only(world, &["carry"]);
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(
        exes(&world),
        [
            "exe a-it -Z unstable-options --report-time carry",
            "exe a-lib -Z unstable-options --report-time carry"
        ]
    );
    assert!(done.stdout.contains("rust-checks: test ONLY \"carry\" on rust/a: 2 ran, 0 filtered out - a part, not kept as the crate's green\n"), "{}", done.stdout);
    assert!(done.stdout.ends_with("rust-checks: test clean on 1 crate(s)\nrust-checks: ONLY \"carry\" ran a part of each crate's tests, NOT kept as its green - `make builder-checks` runs the whole crate\n"), "{}", done.stdout);
    assert!(!kept(&root, "test-a") && !kept(&root, "binary-a"));
    // the whole run after it runs every binary again, unfiltered, and keeps its green
    let world = only(world, &[]);
    let whole = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(whole.code, 0, "{}", whole.stderr);
    assert!(!whole.stdout.contains("unchanged"), "{}", whole.stdout);
    assert!(!whole.stdout.contains("ONLY"), "{}", whole.stdout);
    let whole_runs = exes(&world)
        .iter()
        .filter(|c| c.ends_with(" --report-time"))
        .count();
    assert_eq!(whole_runs, 2);
    assert!(kept(&root, "test-a") && kept(&root, "binary-a"));
    // a filtered run where the whole crate's green stands reads it and runs nothing
    let world = only(world, &["carry"]);
    let before = exes(&world).len();
    let stands = answer(&world, "test", &["rust/a".to_owned()], false);
    assert!(stands.stdout.contains("test unchanged on rust/a"));
    assert_eq!(exes(&world).len(), before);
}

#[test]
fn a_filtered_run_leaves_the_counting_build_s_binary_unpassed() {
    let (root, world) = built("only");
    std::fs::write(
        root.join("rust/a/Cargo.toml"),
        "[package]\nname = \"pkg-a\"\n[features]\ncounters = []\n",
    )
    .unwrap();
    let world = only(world, &["carry"]);
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    let world = only(world, &[]);
    let counted = answer(&world, "test-counters", &["rust/a".to_owned()], false);
    assert_eq!(counted.code, 0, "{}", counted.stderr);
    assert!(!counted.stdout.contains("unchanged"), "{}", counted.stdout);
    assert_eq!(
        exes(&world)
            .iter()
            .filter(|c| c.ends_with(" --report-time"))
            .count(),
        2
    );
}

#[test]
fn a_filter_that_runs_no_test_fails_its_crate() {
    let (root, world) = built("only");
    for exe in ["a-lib", "a-it"] {
        crate::write_executable(
            &world.target.join(exe),
            "#!/bin/sh\necho 'test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 9 filtered out; finished in 0.01s'\n",
        );
    }
    let world = only(world, &["nosuch"]);
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 1);
    assert!(done.stderr.contains("rust-checks: test ONLY \"nosuch\" ran no test of rust/a - name a module path its tests hold (e.g. land::carry), or drop ONLY= to run the whole crate"), "{}", done.stderr);
    assert!(done.stderr.contains("1 crate(s) failed test"));
    assert!(!kept(&root, "test-a"));
}

#[test]
fn a_fresh_filtered_run_hands_the_words_to_cargo_and_its_doctests_and_keeps_nothing() {
    let (root, world) = built("only");
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! ```\n//! x\n//! ```\n").unwrap();
    // the binaries named, the doc pass is cargo's: the filter after its `--`
    let world = only(world, &["carry", "phase"]);
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    let doc: Vec<String> = calls(&world)
        .into_iter()
        .filter(|c| c.starts_with("test --doc"))
        .collect();
    assert_eq!(doc.len(), 1, "{doc:?}");
    assert!(doc[0].ends_with("rust/a/Cargo.toml -- carry phase"));
    // a fresh run asks no key: `cargo test` itself, the words after its `--`, and still nothing kept
    let fresh = only(world_with(&root, BINARY_CARGO), &["carry", "phase"]).map(|w| World {
        no_reuse: true,
        ..w
    });
    let done = answer(&fresh, "test", &["rust/b".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let run: Vec<String> = calls(&fresh)
        .into_iter()
        .filter(|c| c.starts_with("test --quiet"))
        .collect();
    assert_eq!(run.len(), 1, "{run:?}");
    assert!(run[0].ends_with("rust/b/Cargo.toml -- carry phase"));
    assert!(!kept(&root, "test-b") && !kept(&root, "binary-b"));
}

#[test]
fn a_filtered_run_s_test_line_is_marked_and_a_whole_run_s_is_not() {
    let (root, world) = built("only");
    let world = only(world, &["carry", "phase"]);
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    let world = only(world, &[]);
    assert_eq!(
        answer(&world, "test", &["rust/a".to_owned()], false).code,
        0
    );
    let tests: Vec<Value> = phases(&root)
        .into_iter()
        .filter(|l| l["step"] == "test")
        .collect();
    assert_eq!(tests.len(), 2, "{tests:?}");
    assert_eq!(tests[0]["only"], "carry phase");
    assert!(tests[1].get("only").is_none(), "{}", tests[1]);
    // the build line is the crate's build, whatever ran after it: no mark
    assert!(phases(&root)
        .iter()
        .filter(|l| l["step"] == "build")
        .all(|l| l.get("only").is_none()));
}

#[test]
fn a_filter_with_no_crate_is_refused_with_the_command_to_run() {
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    let bare = args(&["test", "--only", "land::carry"]);
    assert_eq!(parse(&bare), None);
    let refused = dispatch(&world, &bare);
    assert_eq!(refused.code, 2);
    assert_eq!(refused.stderr, "rust-checks: test ONLY \"land::carry\" names no crate - every crate the filter misses would fail; add CRATE=<dir>, as in `make rust-test CRATE=rust/gate/crates/land ONLY=\"land::carry\"`\n");
    assert!(calls(&world).is_empty());
    // the generic usage for every other malformed line
    assert!(dispatch(&world, &args(&["lint", "--only", "x"]))
        .stderr
        .starts_with("usage:"));
}
