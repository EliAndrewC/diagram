//! `make test-times` (feature 449 T169): each test of a crate timed alone by T99's method, over a fake cargo and a stand-in test binary.

use std::collections::BTreeSet;

use super::*;
use crate::rustc::times::{test_times, BAR, END_TO_END};

/// A fake cargo whose `--no-run` build names one test binary, `<target>/a-lib`, and fails for a crate whose manifest says `broken`.
const ONE_BINARY: &str = r#"d="$(dirname "$0")"; for m in "$@"; do :; done
case "$1 $2" in
  "test --no-run") if grep -q broken "$m"; then echo 'error: could not compile' >&2; exit 101; fi
    echo '{"executable":"'"$d/a-lib"'","target":{"kind":["lib"],"name":"a"},"profile":{"test":true}}';;
esac
exit 0"#;

/// The stand-in binary: three tests and a benchmark listed; a run notes its test and its TMPDIR, and `m::broken` fails.
const BINARY: &str = r#"#!/bin/sh
d="${0%/*}"
if [ "$1" = --list ]; then printf 'm::fast: test\nm::whole_run: test\nm::broken: test\nbench_it: benchmark\n'; exit 0; fi
echo "run $2 $TMPDIR $CARGO_PKG_NAME" >> "$d/runs"
[ "$2" = m::broken ] && exit 1
exit 0
"#;

fn timed_world() -> (TempDir, Held<World>) {
    let (root, a, _) = two_crates();
    std::fs::write(&a, "[package]\nname = \"pkg-a\"\n").unwrap();
    std::fs::write(
        root.join("rust/a/src/lib.rs"),
        format!("//! x\n#[test]\nfn fast() {{}}\n{END_TO_END} the real command.\n#[test]\nfn whole_run() {{}}\n"),
    )
    .unwrap();
    let world = world_with(&root, ONE_BINARY);
    crate::write_executable(&world.target.join("a-lib"), BINARY);
    (root, world)
}

fn runs(world: &World) -> Vec<String> {
    std::fs::read_to_string(world.target.join("runs"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

#[test]
fn every_test_runs_alone_each_time_in_a_fresh_tmpdir_and_the_best_is_kept() {
    let (_root, world) = timed_world();
    let done = test_times(&world, &["rust/a".to_owned()], 1000.0, 2);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let ran = runs(&world);
    // three tests, two runs each, the benchmark never run; each run with cargo's variables
    assert_eq!(ran.len(), 6, "{ran:?}");
    assert!(ran.iter().all(|r| r.ends_with(" pkg-a")));
    let tmps: BTreeSet<&str> = ran.iter().map(|r| r.split(' ').nth(2).unwrap()).collect();
    assert_eq!(tmps.len(), 6, "a fresh TMPDIR each run: {ran:?}");
    assert!(
        tmps.iter().all(|t| !Path::new(t).exists()),
        "each removed after its run"
    );
    assert!(done
        .stdout
        .contains("rust/a: 3 test(s), each alone (--exact), best of 2"));
    assert!(done
        .stdout
        .contains("rust/a: 0 over the bar, 0 of them declared end-to-end; 3 under"));
    // a failing test is named, its verdict left to `make rust-test`: time is never a gate, so the exit stands at 0
    assert!(done.stdout.contains("FAILED m::broken"));
}

#[test]
fn a_test_over_the_bar_is_listed_and_a_declared_end_to_end_one_marked() {
    let (_root, world) = timed_world();
    let done = test_times(&world, &["rust/a".to_owned()], 0.0, 1);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let marked: Vec<&str> = done
        .stdout
        .lines()
        .filter(|l| l.contains("declared end-to-end,"))
        .collect();
    assert_eq!(marked.len(), 1, "{}", done.stdout);
    assert!(marked[0].contains("m::whole_run"));
    assert!(done
        .stdout
        .contains("3 over the bar, 1 of them declared end-to-end; 0 under"));
    assert_eq!(done.stdout.matches("  OVER ").count(), 3);
}

#[test]
fn a_build_that_fails_times_nothing_and_no_crate_is_a_usage_error() {
    let (root, world) = timed_world();
    std::fs::write(
        root.join("rust/b/Cargo.toml"),
        "[package]\nname = \"broken\"\n",
    )
    .unwrap();
    let done = test_times(&world, &["rust/b".to_owned()], BAR, 1);
    assert_eq!(done.code, 1);
    assert!(
        done.stderr.contains("rust/b: the tests did not build")
            && done.stderr.contains("could not compile")
    );
    assert!(runs(&world).is_empty());
    // through the command line: no crate is a usage error, and `--check` is no flag of it
    let none = dispatch(&world, &["test-times".to_owned()]);
    assert_eq!(none.code, 2);
    assert!(none.stderr.contains("make test-times CRATE=<crate dir>"));
    let flagged = dispatch(&world, &["test-times".to_owned(), "--check".to_owned()]);
    assert_eq!(flagged.code, 2);
    assert!(flagged
        .stderr
        .contains("l7r-gate rust test-times --crate DIR..."));
    let named = dispatch(
        &world,
        &[
            "test-times".to_owned(),
            "--crate".to_owned(),
            "rust/b".to_owned(),
        ],
    );
    assert_eq!(named.code, 1);
}
