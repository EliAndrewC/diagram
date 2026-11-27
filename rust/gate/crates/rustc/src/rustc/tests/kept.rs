//! A crate's kept result (feature 449 T93, T110): what moves each check's key, and what a run keeps.

use std::process::Command;

use super::*;

/// A file's ids, code ids and interface ids, one version of it (T112, T113).
type Version = (
    BTreeMap<String, String>,
    BTreeMap<String, String>,
    BTreeMap<String, String>,
    BTreeMap<String, Vec<String>>,
);

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

/// Two crates whose tests run from a built binary, `a` declaring what its tests read and `b` with counters.
fn binary_world() -> (TempDir, Held<World>) {
    let (root, a, b) = kept_crates();
    std::fs::write(&b, "[package]\n[features]\ncounters = []\n").unwrap();
    // a declares what its tests read: its binary key carries those paths, its own sources the binary
    std::fs::write(
        &a,
        "[package]\n[package.metadata.l7r]\nreads = [\"scripts/\"]\n",
    )
    .unwrap();
    let world = world_with(&root, BINARY_CARGO);
    test_binary(&world.target.join("exe"), "binary one");
    (root, world)
}

/// The test runs: a crate's `cargo test`, or its built binary run directly (feature 449 T160).
fn test_runs(w: &World) -> usize {
    calls(w)
        .iter()
        .filter(|c| {
            c.starts_with("test --quiet --manifest")
                || c.starts_with("test --quiet --all-features --manifest")
                || c.starts_with("exe exe")
        })
        .count()
}

#[test]
fn a_test_run_is_kept_and_an_unchanged_binary_runs_no_test() {
    let (root, world) = binary_world();
    let first = answer(&world, "test", &[], false);
    assert_eq!(first.code, 0);
    assert_eq!(test_runs(&world), 2);
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
    assert_eq!(test_runs(&world), 2);
    // the counting build shares the plain one's result where its binary is the same (b has counters); a crate with none has no
    // counting build to run (T97)
    let counted = answer(&world, "test-counters", &[], false);
    assert!(counted.stdout.contains("test-counters unchanged on rust/b"));
    assert!(counted.stdout.contains(
        "test-counters passes over rust/a - no counters feature, so its counting build is its default one"
    ));
    assert_eq!(test_runs(&world), 2);
}

/// Split from the test above (feature 449 T167, FR-008's tenth of a second: its seven runs of the checks together took 237 ms): from the
/// same first run, a binary that moved, a build that fails and a fresh run.
#[test]
fn a_moved_binary_or_a_failed_build_runs_and_a_fresh_run_runs_every_crate() {
    let (root, world) = binary_world();
    assert_eq!(answer(&world, "test", &[], false).code, 0);
    assert_eq!(test_runs(&world), 2);
    // a binary that moved runs; a build that fails is asked again plain, so its failure is cargo's to tell, and nothing runs (feature
    // 451 T05: the build booked apart from the run)
    test_binary(&world.target.join("exe"), "binary two");
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! moved again\n").unwrap();
    assert_eq!(answer(&world, "test", &[], false).code, 0);
    assert_eq!(test_runs(&world), 3);
    std::fs::write(world.target.join("nobuild"), "").unwrap();
    std::fs::write(root.join("rust/a/src/lib.rs"), "//! and again\n").unwrap();
    let failed = answer(&world, "test", &[], false);
    assert_eq!(failed.code, 1);
    assert!(failed.stderr.contains("test FAILED on rust/a"));
    assert_eq!(test_runs(&world), 3);
    assert_eq!(
        calls(&world)
            .iter()
            .filter(|c| c.starts_with("test --no-run --quiet --manifest"))
            .count(),
        1
    );
    std::fs::remove_file(world.target.join("nobuild")).unwrap();
    // a fresh run runs every crate, each built first
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    assert_eq!(answer(&fresh, "test", &[], false).code, 0);
    assert_eq!(test_runs(&fresh), 5);
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

/// A crate's `cargo test` is its unit tests alone when it has no binary holding a test, integration test, example, bench or doctest
/// (T111; a binary with no test and a `text` block are none, T57).
#[test]
fn a_crate_whose_unit_tests_are_its_whole_cargo_test() {
    let (root, a, _) = two_crates();
    let dir = root.join("rust/a");
    assert!(super::super::unit_tests_only(&a));
    // a binary that holds no test adds none to `cargo test` (feature 451 T57): a test, a `cfg(test)` or a module file it declares does
    let in_main = "fn main() {}\n#[cfg(test)]\nmod t {\n    #[test]\n    fn x() {}\n}\n";
    for (path, text, alone) in [
        ("src/main.rs", "use std::io;\nfn main() {}\n", true),
        ("src/bin/x.rs", "fn main() {}\n", true),
        ("src/main.rs", in_main, false),
        ("src/main.rs", "mod helper;\nfn main() {}\n", false),
        (
            "src/main.rs",
            "pub(crate) mod helper;\nfn main() {}\n",
            false,
        ),
        ("src/bin/x.rs", "#[test]\nfn x() {}\nfn main() {}\n", false),
        ("tests/t.rs", "\n", false),
        ("examples/e.rs", "\n", false),
        ("benches/b.rs", "\n", false),
    ] {
        let at = dir.join(path);
        std::fs::create_dir_all(at.parent().unwrap()).unwrap();
        std::fs::write(&at, text).unwrap();
        assert_eq!(super::super::unit_tests_only(&a), alone, "{path}: {text}");
        std::fs::remove_file(&at).unwrap();
        let _ = std::fs::remove_dir(at.parent().unwrap());
    }
    assert!(super::super::unit_tests_only(&a));
    // a declared binary's own path is read; a declared test, example or bench is a target of its own
    let tool = dir.join("tool/x.rs");
    std::fs::create_dir_all(tool.parent().unwrap()).unwrap();
    std::fs::write(&tool, "fn main() {}\n").unwrap();
    std::fs::write(
        &a,
        "[package]\n[[bin]]\nname = \"x\"\npath = \"tool/x.rs\"\n",
    )
    .unwrap();
    assert!(super::super::unit_tests_only(&a));
    std::fs::write(&tool, in_main).unwrap();
    assert!(!super::super::unit_tests_only(&a));
    for declared in ["[[test]]", "[[example]]", "[[bench]]"] {
        std::fs::write(&a, format!("[package]\n{declared}\nname = \"x\"\n")).unwrap();
        assert!(!super::super::unit_tests_only(&a), "{declared}");
    }
    std::fs::write(&a, "[package]\n").unwrap();
    // a `text` block is never a doctest, an indented line inside it neither; any other fence is one - in `side.rs`'s reading too,
    // `has_doctests`, so `make rust-test` runs no `cargo test --doc` for a crate whose only blocks are `text` ones (T57)
    for (text, doctest) in [
        ("//! ```text\n//! a\n//!     b\n//! ```\n", false),
        (
            "/// ```text\n/// a\n/// ```\n///\n///     let x = 1;\npub fn f() {}\n",
            true,
        ),
        (
            "/// ```rust\n/// assert!(true);\n/// ```\npub fn f() {}\n",
            true,
        ),
        ("/// ```ignore\n/// x\n/// ```\npub fn f() {}\n", true),
        ("/// ```textual\n/// x\n/// ```\npub fn f() {}\n", true),
    ] {
        std::fs::write(dir.join("src/lib.rs"), text).unwrap();
        assert_eq!(super::super::unit_tests_only(&a), !doctest, "{text}");
        assert_eq!(super::super::kept::has_doctests(&a), doctest, "{text}");
    }
    std::fs::write(
        dir.join("src/lib.rs"),
        "/// ```\n/// assert!(true);\n/// ```\npub fn f() {}\n",
    )
    .unwrap();
    assert!(!super::super::unit_tests_only(&a));
    std::fs::write(dir.join("src/lib.rs"), "//! x\n// ```\n").unwrap();
    // a plain comment is no doctest
    assert!(super::super::unit_tests_only(&a));
    // an indented block after an empty doc line, or opening a doc comment, is a doctest; inside a paragraph it continues it
    for (text, doctest) in [
        ("/// a\n///\n///     let x = 1;\npub fn f() {}\n", true),
        ("fn g() {}\n///     let x = 1;\npub fn f() {}\n", true),
        ("///     let x = 1;\npub fn f() {}\n", true),
        ("//! 1. a list item\n//!      continued\n", false),
        ("#[cfg(not(coverage))]\nfn f() {}\n", true),
        ("/// counts toward its coverage).\npub fn f() {}\n", false),
    ] {
        std::fs::write(dir.join("src/lib.rs"), text).unwrap();
        assert_eq!(super::super::unit_tests_only(&a), !doctest, "{text}");
    }
}

/// A coverage pass keeps the crate's tests' green result where its unit tests are its whole `cargo test`, and only there (T111).
#[test]
fn a_coverage_pass_keeps_the_tests_of_a_crate_with_unit_tests_alone() {
    let (root, _, _) = kept_crates();
    // a binary holding a test is a test target the coverage run (`--lib`) never builds (451 T57)
    std::fs::write(
        root.join("rust/b/src/main.rs"),
        "fn main() {}\n#[test]\nfn t() {}\n",
    )
    .unwrap();
    let world = world_with(&root, LCOV_CARGO);
    std::fs::write(world.target.join("lcov"), "").unwrap();
    assert_eq!(answer(&world, "cover", &[], false).code, 0);
    // a crate's tests run through `cargo test`, or from the binary the key's build named (feature 449 T160), which notes each run
    let runs = || {
        let direct = std::fs::read_to_string(world.target.join("runs")).unwrap_or_default();
        let through_cargo = calls(&world)
            .iter()
            .filter(|c| c.starts_with("test --quiet"))
            .count();
        (direct.lines().count() + through_cargo, direct)
    };
    let (ran_before, _) = runs();
    let tests = answer(&world, "test", &[], false);
    assert!(
        tests.stdout.contains("test unchanged on rust/a"),
        "{}",
        tests.stdout
    );
    assert!(
        !tests.stdout.contains("test unchanged on rust/b"),
        "{}",
        tests.stdout
    );
    let (ran, direct) = runs();
    assert_eq!(ran - ran_before, 1, "b alone ran its tests");
    assert!(
        direct
            .lines()
            .last()
            .unwrap_or_default()
            .ends_with("rust/b"),
        "{direct}"
    );
}

/// THE COVERED RUN ALONE (feature 451 T57): a crate with a binary that holds no test - the guard, the gate's binary, the engines - has
/// its whole `cargo test` in the coverage run, so a failing test is caught there, by the crate's name, and a green pass answers for
/// the crate's plain tests: `make rust-test` after it stands on it, building and running nothing. Before T57 such a crate's plain
/// test binary was built and run again after every coverage pass (the guard's alone: 25 builds, 4.5 min, and 23 runs, 2.1 min, after
/// a green coverage run with no edit between, measured 2026-11-21 over the event log's Phase lines since 2026-11-20T12:35Z).
#[test]
fn a_failing_test_is_caught_by_the_covered_run_alone_and_a_green_one_answers_for_the_plain_run() {
    let (root, _, _) = kept_crates();
    std::fs::write(
        root.join("rust/b/src/main.rs"),
        "//! the binary\nuse std::io;\nfn main() {}\n",
    )
    .unwrap();
    let world = world_with(&root, LCOV_CARGO);
    std::fs::write(world.target.join("lcov"), "").unwrap();
    std::fs::write(world.target.join("failtest"), "").unwrap();
    let red = answer(&world, "cover", &["rust/b".to_owned()], false);
    assert_eq!(red.code, 1, "{}", red.stdout);
    assert!(
        red.stderr.contains("cover FAILED on rust/b"),
        "{}",
        red.stderr
    );
    // a red coverage pass answers for nothing: the plain run is still owed, and runs
    let builds = || {
        calls(&world)
            .iter()
            .filter(|c| c.starts_with("test --no-run --message-format=json"))
            .count()
    };
    let before = builds();
    let plain = answer(&world, "test", &["rust/b".to_owned()], false);
    assert!(
        !plain.stdout.contains("test unchanged on rust/b"),
        "{}",
        plain.stdout
    );
    assert_eq!(builds() - before, 1, "the plain test binary is built");
    std::fs::remove_file(world.target.join("failtest")).unwrap();
    std::fs::write(root.join("rust/b/src/lib.rs"), "//! y\n").unwrap();
    assert_eq!(
        answer(&world, "cover", &["rust/b".to_owned()], false).code,
        0
    );
    let before = builds();
    let plain = answer(&world, "test", &["rust/b".to_owned()], false);
    assert!(
        plain.stdout.contains("test unchanged on rust/b"),
        "{}",
        plain.stdout
    );
    assert_eq!(
        builds(),
        before,
        "nothing built: the coverage pass answered"
    );
}

/// A comment-only edit moves no lint, test or coverage key, and moves format's and dead's, which read comments; a file the crate's
/// tests declare they read keeps its whole text in the key (T112).
#[test]
fn a_comment_only_edit_moves_no_lint_test_or_coverage_key() {
    let (root, a, b) = two_crates();
    let all = [a.clone(), b];
    let file = root.join("rust/a/src/lib.rs");
    let version = |text: &str, id: &str| {
        std::fs::write(&file, text).unwrap();
        let ids = BTreeMap::from([("rust/a/src/lib.rs".to_owned(), id.to_owned())]);
        let (code, interface, includes) = super::super::kept::code_ids(&root, &ids);
        (ids, code, interface, includes)
    };
    let key = |cmd: &str, reads: Reads, v: &Version| {
        super::super::kept::verdict_key_with(
            &root,
            &a,
            cmd,
            reads,
            &all,
            &v.0,
            "c",
            Some((&v.1, &v.2, &v.3)),
        )
    };
    let one = version("pub fn f() {}\n", "1");
    let commented = version("// why f\npub fn f() {} // and how\n", "2");
    let changed = version("pub fn f() { g(); }\n", "3");
    for (cmd, reads) in [
        ("lint", Reads::Source),
        ("test", Reads::Tests),
        ("cover", Reads::Tests),
    ] {
        assert_eq!(key(cmd, reads, &one), key(cmd, reads, &commented), "{cmd}");
        assert_ne!(key(cmd, reads, &one), key(cmd, reads, &changed), "{cmd}");
    }
    assert_ne!(
        key("format", Reads::Own, &one),
        key("format", Reads::Own, &commented)
    );
    assert_ne!(
        key("dead", Reads::Source, &one),
        key("dead", Reads::Source, &commented)
    );
    std::fs::write(
        &a,
        "[package]\n[package.metadata.l7r]\nreads = [\"rust/a/src/\"]\n",
    )
    .unwrap();
    // a lint runs no test, so a declared read moves no lint key
    assert_eq!(
        key("lint", Reads::Source, &one),
        key("lint", Reads::Source, &commented)
    );
    assert_ne!(
        key("test", Reads::Tests, &one),
        key("test", Reads::Tests, &commented),
        "a declared read keeps its comments"
    );
    let gone = BTreeMap::from([("rust/a/src/lib.rs".to_owned(), String::new())]);
    assert!(
        super::super::kept::code_ids(&root, &gone).0.is_empty(),
        "a deleted file has no code"
    );
}

/// A lint that reads plain comments, configured in a manifest, a clippy.toml or an attribute, keeps comments in the lint keys (T112).
#[test]
fn a_comment_reading_lint_is_found_where_it_is_configured() {
    let (root, _, _) = two_crates();
    let ids = BTreeMap::from([
        ("rust/Cargo.toml".to_owned(), "1".to_owned()),
        ("rust/a/src/lib.rs".to_owned(), "2".to_owned()),
        ("rust/clippy.toml".to_owned(), "3".to_owned()),
        ("notes.md".to_owned(), "4".to_owned()),
    ]);
    let found = || super::super::kept::comment_lints(&root, &ids);
    assert!(!found());
    std::fs::write(root.join("notes.md"), "undocumented_unsafe_blocks = 1\n").unwrap();
    assert!(
        !found(),
        "only a manifest, clippy.toml or Rust file configures a lint"
    );
    std::fs::write(
        root.join("rust/Cargo.toml"),
        [
            "[workspace.lints.clippy]\nundocumented_",
            "unsafe_blocks = \"deny\"\n",
        ]
        .concat(),
    )
    .unwrap();
    assert!(found());
    std::fs::write(root.join("rust/Cargo.toml"), "[workspace]\n").unwrap();
    // split, so this file's own text configures no lint for the tree scan
    let attribute = ["#![deny(clippy::unnecessary_", "safety_comment)]\n"].concat();
    std::fs::write(root.join("rust/a/src/lib.rs"), attribute).unwrap();
    assert!(found());
}

/// A dependency's body-only edit moves no lint key of the crate built on it, and moves its test and coverage keys, the dependency's own
/// lint key and, with a signature edit, the dependent's lint key (T113).
#[test]
fn a_dependency_s_body_edit_moves_its_dependents_lint_key_only_through_its_interface() {
    let (root, g, mid, _low) = nested_crates();
    let all = [g.clone(), mid.clone()];
    let file = root.join("rust/g/crates/mid/src/lib.rs");
    let version = |text: &str, id: &str| {
        std::fs::write(&file, text).unwrap();
        let ids = BTreeMap::from([("rust/g/crates/mid/src/lib.rs".to_owned(), id.to_owned())]);
        let (code, interface, includes) = super::super::kept::code_ids(&root, &ids);
        (ids, code, interface, includes)
    };
    let key = |manifest: &Path, cmd: &str, reads: Reads, v: &Version| {
        super::super::kept::verdict_key_with(
            &root,
            manifest,
            cmd,
            reads,
            &all,
            &v.0,
            "c",
            Some((&v.1, &v.2, &v.3)),
        )
    };
    let one = version("pub fn mid_only() { low_used(); }\n", "1");
    let body = version("pub fn mid_only() { low_used(); low_used(); }\n", "2");
    let signature = version("pub fn mid_only(x: u8) { low_used(); }\n", "3");
    assert_eq!(
        key(&g, "lint", Reads::Source, &one),
        key(&g, "lint", Reads::Source, &body)
    );
    assert_ne!(
        key(&g, "lint", Reads::Source, &one),
        key(&g, "lint", Reads::Source, &signature)
    );
    assert_ne!(
        key(&g, "test", Reads::Tests, &one),
        key(&g, "test", Reads::Tests, &body)
    );
    assert_ne!(
        key(&g, "cover", Reads::Tests, &one),
        key(&g, "cover", Reads::Tests, &body)
    );
    assert_ne!(
        key(&mid, "lint", Reads::Source, &one),
        key(&mid, "lint", Reads::Source, &body)
    );
}

/// A test or coverage key reads the files the crate's sources compile in, wherever they are; a lint key does not (found under T113).
#[test]
fn a_test_key_reads_what_the_crate_s_sources_include() {
    let (root, a, b) = two_crates();
    let all = [a.clone(), b];
    std::fs::create_dir_all(root.join("data")).unwrap();
    std::fs::write(
        root.join("rust/a/src/lib.rs"),
        "const T: &str = include_str!(\"../../../data/table.tsv\");\nconst U: &[u8] = include_bytes!(\"./x.bin\");\n",
    )
    .unwrap();
    let version = |id: &str| {
        let ids = BTreeMap::from([
            ("rust/a/src/lib.rs".to_owned(), "1".to_owned()),
            ("data/table.tsv".to_owned(), id.to_owned()),
        ]);
        let (code, interface, includes) = super::super::kept::code_ids(&root, &ids);
        (ids, code, interface, includes)
    };
    let (one, two) = (version("t1"), version("t2"));
    assert_eq!(
        one.3["rust/a/src/lib.rs"],
        ["data/table.tsv", "rust/a/src/x.bin"]
    );
    let key = |cmd: &str, reads: Reads, v: &Version| {
        super::super::kept::verdict_key_with(
            &root,
            &a,
            cmd,
            reads,
            &all,
            &v.0,
            "c",
            Some((&v.1, &v.2, &v.3)),
        )
    };
    assert_ne!(
        key("test", Reads::Tests, &one),
        key("test", Reads::Tests, &two)
    );
    assert_ne!(
        key("cover", Reads::Tests, &one),
        key("cover", Reads::Tests, &two)
    );
    assert_eq!(
        key("lint", Reads::Source, &one),
        key("lint", Reads::Source, &two)
    );
}

/// A compiled-in path never spans a line (found by feature 451 T347): `core`'s own reader of `include_str!` lines names the macros in
/// strings, and the text from one such string's quote to the next quote, lines and all, was read as a path - which the kept views,
/// a line a file, gave back cut at its first line, so every key that reads the compiled-in files moved once after each rebuild of
/// the checks, and a test build told alone (`kept/alone.rs`) was not until its second run.
#[test]
fn a_compiled_in_path_never_spans_a_line_so_the_kept_views_read_back_as_they_were_read() {
    let (root, _, _) = two_crates();
    let text = "fn f() {\n    for word in [\"include_str!(\", \"include_bytes!(\"] {\n        drop(word);\n    }\n}\nconst S: &str = \"x\";\n";
    std::fs::write(root.join("rust/a/src/lib.rs"), text).unwrap();
    let ids = ids(&[("rust/a/src/lib.rs", "1")]);
    let cache = root.join("views");
    let fresh = super::super::kept::code_ids_kept(&root, &ids, Some(&cache)).2;
    let kept = super::super::kept::code_ids_kept(&root, &ids, Some(&cache)).2;
    assert_eq!(fresh, kept);
    assert_eq!(fresh["rust/a/src/lib.rs"], ["rust/a/src/, "]);
}

/// The code views are kept by each file's path and content (feature 449 T160): a file whose blob id stands is not read again, one that
/// moved is, and a cache under another stamp is not trusted.
#[test]
fn the_code_views_are_kept_by_content_and_read_again_where_it_moved() {
    let (root, _, _) = two_crates();
    let cache = root.join("views");
    let lib = "rust/a/src/lib.rs";
    std::fs::write(root.join(lib), "include!(\"x.rs\");\n// note\nfn f() {}\n").unwrap();
    let ids = BTreeMap::from([(lib.to_owned(), "id1".to_owned())]);
    let first = super::super::kept::code_ids_kept(&root, &ids, Some(&cache));
    assert_eq!(first, super::super::kept::code_ids(&root, &ids));
    assert_eq!(first.2[lib], ["rust/a/src/x.rs"]);
    // the file gone, its content id standing: the kept views answer, nothing is read
    std::fs::remove_file(root.join(lib)).unwrap();
    assert_eq!(
        super::super::kept::code_ids_kept(&root, &ids, Some(&cache)),
        first
    );
    // a cache under another stamp (its views code moved) is not read: with the file gone there is nothing to answer
    let text = std::fs::read_to_string(&cache).unwrap();
    std::fs::write(&cache, text.replacen("l7r-rust views", "another stamp", 1)).unwrap();
    assert!(super::super::kept::code_ids_kept(&root, &ids, Some(&cache))
        .0
        .is_empty());
    // a moved content id is read again, and the cache then holds the tree's files alone
    std::fs::write(root.join(lib), "fn g() {}\n").unwrap();
    let moved = BTreeMap::from([(lib.to_owned(), "id2".to_owned())]);
    let second = super::super::kept::code_ids_kept(&root, &moved, Some(&cache));
    assert_ne!(second.0[lib], first.0[lib]);
    assert!(second.2.is_empty());
    let kept = std::fs::read_to_string(&cache).unwrap();
    assert_eq!(kept.lines().count(), 2, "{kept}");
    assert!(kept.contains("rust/a/src/lib.rs id2\t") && !kept.contains(" id1\t"));
}

/// The views are kept by the code that computes them (feature 451 T434, restating T341's test, whose last step held a rebuilt binary
/// to nothing kept): a rebuilt `l7r-rust` whose views code is the same keeps every view, and a cache under another stamp - the views
/// code moved - is thrown away whole and written again under the new one.
#[test]
fn a_rebuilt_binary_keeps_its_views_and_a_moved_views_code_does_not() {
    let (root, _, _) = two_crates();
    let (cache, lib) = (root.join("views"), "rust/a/src/lib.rs");
    std::fs::write(root.join(lib), "fn f() {}\n").unwrap();
    let ids = BTreeMap::from([(lib.to_owned(), "id1".to_owned())]);
    let first = super::super::kept::code_ids_kept(&root, &ids, Some(&cache));
    let stamp = || {
        std::fs::read_to_string(&cache)
            .unwrap()
            .lines()
            .next()
            .unwrap()
            .to_owned()
    };
    let before = stamp();
    assert!(before.starts_with("l7r-rust views "));
    // the file gone, so only the kept views can answer; the binary's own size, time and content are no part of the stamp
    std::fs::remove_file(root.join(lib)).unwrap();
    assert_eq!(
        super::super::kept::code_ids_kept(&root, &ids, Some(&cache)),
        first
    );
    assert_eq!(stamp(), before);
    // the views code moved: nothing kept answers, and the cache is written again under the new stamp
    let moved =
        super::super::kept::code_ids_kept_by(&root, &ids, Some(&cache), "l7r-rust views other");
    assert!(moved.0.is_empty());
    assert_eq!(stamp(), "l7r-rust views other");
}
