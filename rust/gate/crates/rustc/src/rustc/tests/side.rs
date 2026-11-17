//! The owed crates' tests run side by side from their built binaries (feature 449 T160, `side.rs`).

use super::*;

/// A fake cargo whose `--no-run` build names two binaries a crate, its integration test first and its library's second, as cargo's JSON
/// may; a `--doc` run is noted and passes.
const TWO_BINARIES: &str = r#"d="$(dirname "$0")"; for m in "$@"; do :; done; c="$(basename "$(dirname "$m")")"
case "$1 $2" in
  "test --no-run") echo '{"reason":"build-finished"}'
    echo '{"executable":"'"$d/$c"'-it","target":{"kind":["test"],"name":"it"}}'
    echo '{"executable":"'"$d/$c"'-lib","target":{"kind":["lib"],"name":"x"}}';;
esac
exit 0"#;

/// Two crates in a repository, `a` named `pkg-a`, with the fake build's four binaries in the world's target.
fn built(tag: &str) -> (TempDir, Held<World>) {
    let (root, a, _) = kept_crates();
    std::fs::write(&a, "[package]\nname = \"pkg-a\"\n").unwrap();
    let world = world_with(&root, TWO_BINARIES);
    for c in ["a", "b"] {
        for t in ["lib", "it"] {
            test_binary(&world.target.join(format!("{c}-{t}")), tag);
        }
    }
    (root, world)
}

#[test]
fn the_binaries_run_in_cargo_s_order_from_the_crate_with_cargo_s_variables() {
    let (root, world) = built("one");
    let probe = world.target.join("a-lib");
    crate::write_executable(
        &probe,
        "#!/bin/sh\necho \"exe a-lib $*\" >> \"$(dirname \"$0\")/calls\"\necho \"$PWD|$CARGO_MANIFEST_DIR|$CARGO_PKG_NAME|$CARGO|$CARGO_TARGET_DIR\" > \"$(dirname \"$0\")/env-a\"\ncase \"$TMPDIR\" in */l7r-rust-tests-a-p*) echo own-tmp >> \"$(dirname \"$0\")/env-a\";; esac\necho 'test result: ok. 7 passed'\n",
    );
    let done = answer(&world, "test", &[], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let ran: Vec<String> = calls(&world)
        .into_iter()
        .filter(|c| c.starts_with("exe "))
        .collect();
    let mut sorted = ran.clone();
    sorted.sort();
    assert_eq!(
        sorted,
        ["exe a-it -q", "exe a-lib -q", "exe b-it -q", "exe b-lib -q"]
    );
    // within a crate the library's unit tests first, as `cargo test` runs them, and no `cargo test` was asked
    let at = |name: &str| ran.iter().position(|c| c.starts_with(name)).unwrap();
    assert!(at("exe a-lib") < at("exe a-it") && at("exe b-lib") < at("exe b-it"));
    assert!(!calls(&world).iter().any(|c| c.starts_with("test --quiet")));
    // the first binary's summary is the crate's, as the first of `cargo test`'s was
    assert!(done
        .stdout
        .contains("rust-checks: test on rust/a: test result: ok. 7 passed"));
    let dir = root.join("rust/a").display().to_string();
    let env = std::fs::read_to_string(world.target.join("env-a")).unwrap();
    assert_eq!(
        env,
        format!(
            "{dir}|{dir}|pkg-a|{}|{}\nown-tmp\n",
            world.cargo,
            world.target.display()
        )
    );
    // nothing moved: no binary is built or run again
    let before = calls(&world).len();
    assert!(answer(&world, "test", &[], false)
        .stdout
        .contains("test unchanged on rust/b"));
    assert_eq!(
        calls(&world).len(),
        before + 1,
        "only the compiler's version"
    );
}

#[test]
fn a_failing_binary_stops_its_crate_and_a_leak_fails_it() {
    let (root, world) = built("one");
    crate::write_executable(
        &world.target.join("b-lib"),
        "#!/bin/sh\necho \"exe b-lib $*\" >> \"$(dirname \"$0\")/calls\"\necho boom; exit 101\n",
    );
    crate::write_executable(
        &world.target.join("a-it"),
        "#!/bin/sh\ntouch \"$TMPDIR/l7r-leak-t160\"\necho 'test result: ok. 1 passed'\n",
    );
    let done = answer(&world, "test", &[], false);
    assert_eq!(done.code, 1);
    assert!(
        done.stderr.contains("test FAILED on rust/b\nboom"),
        "{}",
        done.stderr
    );
    assert!(
        !calls(&world).iter().any(|c| c.starts_with("exe b-it")),
        "the crate's later binaries are not run"
    );
    assert!(
        done.stderr.contains("test FAILED on rust/a")
            && done
                .stderr
                .contains("left 1 entry in their TMPDIR, which they must remove: l7r-leak-t160"),
        "{}",
        done.stderr
    );
    assert!(done.stderr.contains("2 crate(s) failed test"));
    drop(root);
}

#[test]
fn a_crate_with_a_doctest_runs_cargo_s_doc_pass_with_its_features() {
    let (root, world) = built("one");
    std::fs::write(
        root.join("rust/b/Cargo.toml"),
        "[package]\n[features]\ncounters = []\n",
    )
    .unwrap();
    std::fs::write(root.join("rust/b/src/lib.rs"), "//! ```\n//! x\n//! ```\n").unwrap();
    assert_eq!(answer(&world, "test-counters", &[], false).code, 0);
    let docs: Vec<String> = calls(&world)
        .into_iter()
        .filter(|c| c.starts_with("test --doc"))
        .collect();
    assert_eq!(docs.len(), 1, "{docs:?}");
    assert!(docs[0].starts_with("test --doc --quiet --all-features --manifest-path"));
    assert!(docs[0].ends_with("rust/b/Cargo.toml"));
    // a library with no code block, a crate with no library, and a block found
    assert!(!super::super::kept::has_doctests(
        &root.join("rust/a/Cargo.toml")
    ));
    std::fs::remove_file(root.join("rust/b/src/lib.rs")).unwrap();
    assert!(!super::super::kept::has_doctests(
        &root.join("rust/b/Cargo.toml")
    ));
    std::fs::write(
        root.join("rust/a/src/lib.rs"),
        "//! a\n//!\n//!     let x = 1;\n",
    )
    .unwrap();
    assert!(super::super::kept::has_doctests(
        &root.join("rust/a/Cargo.toml")
    ));
}

#[test]
fn cargo_s_json_gives_the_binaries_in_the_order_cargo_test_runs_them() {
    let json = [
        r#"{"executable":"/t/z-it","target":{"kind":["test"],"name":"z"}}"#,
        r#"{"executable":"/t/b-it","target":{"kind":["test"],"name":"b"}}"#,
        r#"{"executable":"/t/main","target":{"kind":["bin"],"name":"main"}}"#,
        r#"{"executable":null,"target":{"kind":["lib"],"name":"x"}}"#,
        r#"{"executable":"/t/lib","target":{"kind":["lib"],"name":"x"}}"#,
        r#"{"executable":"/t/odd","target":{"kind":["bench"],"name":"o"}}"#,
        r#"{"executable":"/t/bare"}"#,
        r#"{"executable":"/t/plain","target":{"kind":["bin"],"name":"main"},"profile":{"test":false}}"#,
        "not json",
    ]
    .join("\n");
    assert_eq!(
        super::super::kept::test_targets(&json),
        ["/t/lib", "/t/main", "/t/b-it", "/t/z-it", "/t/bare", "/t/odd"]
    );
}
