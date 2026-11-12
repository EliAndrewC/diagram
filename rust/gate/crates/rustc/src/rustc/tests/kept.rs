//! A crate's kept result (feature 449 T93, T110): what moves each check's key, and what a run keeps.

use std::process::Command;

use super::*;

#[test]
fn a_crate_s_key_moves_with_its_own_inputs_and_not_the_other_crates() {
    let (root, a, b) = two_crates();
    let both = [a.clone(), b];
    let key = |cmd: &str, reads: Reads, changes: &[(&str, &str)], compiler: &str| {
        let mut map = ids(&BASE);
        map.extend(ids(changes));
        verdict_key(&root, &a, cmd, reads, &both, &map, compiler)
    };
    let source = key("lint", Reads::Source, &[], "cargo 1");
    assert_eq!(
        source,
        key(
            "lint",
            Reads::Source,
            &[("rust/b/src/l.rs", "9")],
            "cargo 1"
        )
    );
    assert_ne!(
        source,
        key(
            "lint",
            Reads::Source,
            &[("rust/a/src/l.rs", "9")],
            "cargo 1"
        )
    );
    assert_ne!(
        source,
        key(
            "lint",
            Reads::Source,
            &[("rust/Cargo.lock", "9")],
            "cargo 1"
        )
    );
    assert_eq!(
        source,
        key("lint", Reads::Source, &[("scripts/x.py", "9")], "cargo 1")
    );
    assert_ne!(source, key("lint", Reads::Source, &[], "cargo 2"));
    assert_ne!(source, key("dead", Reads::Source, &[], "cargo 1"));
    // tests that declare nothing they read are keyed on their sources alone (feature 449 T93): a spec's edit runs none of them
    let quiet = key("cover", Reads::Tests, &[], "cargo 1");
    assert_eq!(
        quiet,
        key("cover", Reads::Tests, &[("Makefile", "9")], "cargo 1")
    );
    assert_ne!(
        quiet,
        key(
            "cover",
            Reads::Tests,
            &[("rust/a/src/l.rs", "9")],
            "cargo 1"
        )
    );
    // a declared path moves the key, and nothing else outside the crate does
    std::fs::write(
        &a,
        "[package]\n\n[package.metadata.l7r]\nreads = [\"scripts/\"]\n\n[dependencies]\n",
    )
    .unwrap();
    let narrow = key("cover", Reads::Tests, &[], "cargo 1");
    assert_ne!(
        narrow,
        key("cover", Reads::Tests, &[("scripts/x.py", "9")], "cargo 1")
    );
    assert_eq!(
        narrow,
        key("cover", Reads::Tests, &[("Makefile", "9")], "cargo 1")
    );
    std::fs::write(&a, "[package]\n[package.metadata.l7r]\nreads = [\".\"]\n").unwrap();
    let tree = key("cover", Reads::Tests, &[], "cargo 1");
    assert_ne!(
        tree,
        key("cover", Reads::Tests, &[("Makefile", "9")], "cargo 1")
    );
    // the whole tree is the whole tree: the checks' tests read every crate's files (file-scale caught `rustc.rs` at 1,105 lines)
    assert_ne!(
        tree,
        key(
            "cover",
            Reads::Tests,
            &[("rust/b/src/l.rs", "9")],
            "cargo 1"
        )
    );
    assert_eq!(
        tree,
        key(
            "cover",
            Reads::Tests,
            &[("dev/run-log/2026-11/r.json", "9")],
            "cargo 1"
        )
    );
}

#[test]
fn a_crate_built_from_another_by_path_moves_with_it() {
    let (root, a, b) = two_crates();
    std::fs::write(&a, "[package]\n[dependencies]\nb = { path = \"../b\" }\n").unwrap();
    let both = [a.clone(), b.clone()];
    let base = ids(&[("rust/a/src/l.rs", "1"), ("rust/b/src/l.rs", "2")]);
    let moved_b = ids(&[("rust/a/src/l.rs", "1"), ("rust/b/src/l.rs", "9")]);
    let moved_a = ids(&[("rust/a/src/l.rs", "9"), ("rust/b/src/l.rs", "2")]);
    for (cmd, reads) in [("lint", Reads::Source), ("cover", Reads::Tests)] {
        assert_ne!(
            verdict_key(&root, &a, cmd, reads, &both, &base, "c"),
            verdict_key(&root, &a, cmd, reads, &both, &moved_b, "c")
        );
        assert_eq!(
            verdict_key(&root, &b, cmd, reads, &both, &base, "c"),
            verdict_key(&root, &b, cmd, reads, &both, &moved_a, "c")
        );
    }
}

#[test]
fn an_unchanged_crate_keeps_its_green_result_and_a_failure_is_never_kept() {
    let (root, ..) = two_crates();
    assert!(Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    let world = world_with(&root, "[ -f \"$(dirname \"$0\")/fail\" ] && exit 1\nexit 0");
    let clippy = |w: &World| {
        calls(w)
            .iter()
            .filter(|c| c.starts_with("clippy --quiet --all-targets --manifest"))
            .count()
    };
    assert_eq!(answer(&world, "lint", &[], false).code, 0);
    assert_eq!(clippy(&world), 2);
    let again = answer(&world, "lint", &[], false);
    assert!(again.stdout.contains("its last green result stands"));
    assert_eq!(clippy(&world), 2, "nothing moved");
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! y\n").unwrap();
    assert_eq!(answer(&world, "lint", &[], false).code, 0);
    assert_eq!(clippy(&world), 3, "only the crate that moved");
    std::fs::write(root.join("rust/b/src/lib.rs"), "//! y\n").unwrap();
    std::fs::write(world.target.join("fail"), "").unwrap();
    let failed = answer(&world, "lint", &[], false);
    assert_eq!(failed.code, 1);
    assert!(
        failed.stderr.contains("lint FAILED on rust/b")
            && failed
                .stderr
                .contains("1 crate(s) failed lint - fix what clippy names")
    );
    let before = clippy(&world);
    assert_eq!(answer(&world, "lint", &[], false).code, 1);
    assert_eq!(clippy(&world), before + 1, "a failure is run again");
    std::fs::remove_file(world.target.join("fail")).unwrap();
    let full = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    assert_eq!(answer(&full, "lint", &[], false).code, 0);
    assert_eq!(clippy(&full), before + 3, "a full run runs everything");
}

/// A format check's green result is kept per crate (T110); `make format`, which rewrites the files its key was read from, keeps nothing.
#[test]
fn a_format_check_is_kept_and_a_rewrite_is_not() {
    let (root, _, _) = kept_crates();
    let world = world_with(&root, "exit 0");
    let checks = |w: &World| {
        calls(w)
            .iter()
            .filter(|c| c.starts_with("fmt --check"))
            .count()
    };
    let rewrites = |w: &World| {
        calls(w)
            .iter()
            .filter(|c| c.starts_with("fmt --manifest"))
            .count()
    };
    assert_eq!(answer(&world, "format", &[], true).code, 0);
    assert_eq!(checks(&world), 2);
    assert!(answer(&world, "format", &[], true)
        .stdout
        .contains("format unchanged on rust/a"));
    assert_eq!(checks(&world), 2, "nothing moved");
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! y\n").unwrap();
    assert_eq!(answer(&world, "format", &[], false).code, 0);
    assert_eq!(rewrites(&world), 1, "the moved crate is rewritten");
    assert_eq!(answer(&world, "format", &[], true).code, 0);
    // a rewrite kept nothing, so the check runs
    assert_eq!(checks(&world), 3);
}

#[test]
fn a_test_run_is_kept_and_an_unchanged_binary_runs_no_test() {
    let (root, a, b) = kept_crates();
    std::fs::write(&b, "[package]\n[features]\ncounters = []\n").unwrap();
    // a declares what its tests read: its binary key carries those paths, its own sources the binary
    std::fs::write(
        &a,
        "[package]\n[package.metadata.l7r]\nreads = [\"scripts/\"]\n",
    )
    .unwrap();
    let world = world_with(&root, BINARY_CARGO);
    std::fs::write(world.target.join("exe"), "binary one").unwrap();
    let runs = |w: &World| {
        calls(w)
            .iter()
            .filter(|c| {
                c.starts_with("test --quiet --manifest")
                    || c.starts_with("test --quiet --all-features --manifest")
            })
            .count()
    };
    let first = answer(&world, "test", &[], false);
    assert_eq!(first.code, 0);
    assert_eq!(runs(&world), 2);
    assert!(first
        .stdout
        .contains("rust-checks: test on rust/a: test result: ok. 1 passed"));
    // nothing moved: the first key stands, and no build is asked
    let builds = calls(&world).len();
    let again = answer(&world, "test", &[], false);
    assert_eq!(
        again.stdout,
        "rust-checks: test unchanged on rust/a - its last green result stands\nrust-checks: test unchanged on rust/b - its last green result stands\nrust-checks: test clean on 2 crate(s)\n"
    );
    // only the compiler's version
    assert_eq!(calls(&world).len(), builds + 1);
    // a source moved but its binary did not: built, not run
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! moved\n").unwrap();
    let rebuilt = answer(&world, "test", &[], false);
    assert!(rebuilt.stdout.contains("test unchanged on rust/a"));
    assert_eq!(runs(&world), 2);
    // the counting build shares the plain one's result where its binary is the same (b has counters); a crate with none has no
    // counting build to run (T97)
    let counted = answer(&world, "test-counters", &[], false);
    assert!(counted.stdout.contains("test-counters unchanged on rust/b"));
    assert!(counted.stdout.contains(
        "test-counters passes over rust/a - no counters feature, so its counting build is its default one"
    ));
    assert_eq!(runs(&world), 2);
    // a binary that moved runs; a build that fails runs, and its failure is cargo's to tell
    std::fs::write(world.target.join("exe"), "binary two").unwrap();
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! moved again\n").unwrap();
    assert_eq!(answer(&world, "test", &[], false).code, 0);
    assert_eq!(runs(&world), 3);
    std::fs::write(world.target.join("nobuild"), "").unwrap();
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! and again\n").unwrap();
    assert_eq!(answer(&world, "test", &[], false).code, 0);
    assert_eq!(runs(&world), 4);
    // a fresh run runs every crate and builds nothing first
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    assert_eq!(answer(&fresh, "test", &[], false).code, 0);
    assert_eq!(runs(&fresh), 6);
}

#[test]
fn a_named_crate_is_kept_and_its_key_follows_the_crates_it_builds_from() {
    let (root, a, _) = kept_crates();
    std::fs::write(&a, "[package]\n[dependencies]\nb = { path = \"../b\" }\n").unwrap();
    let world = world_with(&root, "exit 0");
    let named = ["rust/a".to_owned()];
    let clippy = |w: &World| calls(w).iter().filter(|c| c.starts_with("clippy")).count();
    assert_eq!(answer(&world, "lint", &named, false).code, 0);
    assert_eq!(clippy(&world), 2);
    assert!(answer(&world, "lint", &named, false)
        .stdout
        .contains("lint unchanged on rust/a"));
    assert_eq!(clippy(&world), 2);
    std::fs::write(root.join("rust/b/src/lib.rs"), "//! moved\n").unwrap();
    assert_eq!(answer(&world, "lint", &named, false).code, 0);
    assert_eq!(clippy(&world), 4, "b moved, and a builds from it");
    // b taken back: a's earlier green key is among those kept
    std::fs::write(root.join("rust/b/src/lib.rs"), "//! x\n").unwrap();
    assert!(answer(&world, "lint", &named, false)
        .stdout
        .contains("lint unchanged on rust/a"));
    // a crate named outside rust/ is keyed too
    std::fs::create_dir_all(root.join("tests/fx/src")).unwrap();
    std::fs::write(root.join("tests/fx/Cargo.toml"), "[package]\n").unwrap();
    std::fs::write(root.join("tests/fx/src/lib.rs"), "//! x\n").unwrap();
    let outside = ["tests/fx".to_owned()];
    assert_eq!(answer(&world, "lint", &outside, false).code, 0);
    assert!(answer(&world, "lint", &outside, false)
        .stdout
        .contains("lint unchanged on tests/fx"));
}
