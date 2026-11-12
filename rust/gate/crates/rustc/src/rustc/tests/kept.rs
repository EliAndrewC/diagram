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

/// A crate's `cargo test` is its unit tests alone when it has no binary, integration test, example, bench or doctest (T111).
#[test]
fn a_crate_whose_unit_tests_are_its_whole_cargo_test() {
    let (root, a, _) = two_crates();
    let dir = root.join("rust/a");
    assert!(super::super::unit_tests_only(&a));
    for (path, text) in [
        ("src/main.rs", "fn main() {}\n"),
        ("tests/t.rs", "\n"),
        ("examples/e.rs", "\n"),
    ] {
        let at = dir.join(path);
        std::fs::create_dir_all(at.parent().unwrap()).unwrap();
        std::fs::write(&at, text).unwrap();
        assert!(!super::super::unit_tests_only(&a), "{path}");
        std::fs::remove_file(&at).unwrap();
        let _ = std::fs::remove_dir(at.parent().unwrap());
    }
    assert!(super::super::unit_tests_only(&a));
    std::fs::write(&a, "[package]\n[[bin]]\nname = \"x\"\n").unwrap();
    assert!(!super::super::unit_tests_only(&a));
    std::fs::write(&a, "[package]\n").unwrap();
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
    std::fs::write(root.join("rust/b/src/main.rs"), "fn main() {}\n").unwrap();
    let world = world_with(&root, LCOV_CARGO);
    std::fs::write(world.target.join("lcov"), "").unwrap();
    assert_eq!(answer(&world, "cover", &[], false).code, 0);
    let ran_before = calls(&world)
        .iter()
        .filter(|c| c.starts_with("test --quiet"))
        .count();
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
    let ran = calls(&world)
        .iter()
        .filter(|c| c.starts_with("test --quiet"))
        .count();
    assert_eq!(ran - ran_before, 1, "b alone ran its tests");
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
