//! The crate checks, over a fake cargo.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    answer, check, content_ids, crates, dead_public, declared_reads, dispatch, features_but,
    kept_reads, lcov_missed, own_libs, parse, relative, run, tail, uncovered, undeclared,
    verdict_key, workspace_only, Reads, World,
};
use crate::checks::scratch;
use l7r_guard::shared::tempdir::{Held, TempDir};

fn fake_cargo(dir: &Path, body: &str) -> String {
    let path = dir.join("cargo");
    crate::write_executable(
        &path,
        &format!(
            "#!/usr/bin/env bash\necho \"$@\" >> \"{}/calls\"\n{body}\n",
            dir.display()
        ),
    );
    path.display().to_string()
}

fn world_with(root: &Path, body: &str) -> Held<World> {
    let target = scratch("rustc-target");
    let world = World {
        root: root.to_owned(),
        cargo: fake_cargo(&target, body),
        path_dir: target.to_path_buf(),
        target_override: None,
        no_reuse: false,
        hamlet_features: String::new(),
        hamlet_args: String::new(),
        hamlet_spec: "spec.json".to_owned(),
        cover_work: None,
        target: target.to_path_buf(),
    };
    target.hold(world)
}

fn calls(world: &World) -> Vec<String> {
    std::fs::read_to_string(world.target.join("calls"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

fn two_crates() -> (TempDir, PathBuf, PathBuf) {
    let root = scratch("rustc");
    for name in ["a", "b"] {
        std::fs::create_dir_all(root.join(format!("rust/{name}/src"))).unwrap();
        std::fs::write(root.join(format!("rust/{name}/Cargo.toml")), "[package]\n").unwrap();
        std::fs::write(root.join(format!("rust/{name}/src/lib.rs")), "//! x\n").unwrap();
    }
    std::fs::write(root.join("rust/Cargo.toml"), "[workspace]\n").unwrap();
    let (a, b) = (
        root.join("rust/a/Cargo.toml"),
        root.join("rust/b/Cargo.toml"),
    );
    (root, a, b)
}

fn ids(pairs: &[(&str, &str)]) -> BTreeMap<String, String> {
    pairs
        .iter()
        .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
        .collect()
}

const BASE: [(&str, &str); 5] = [
    ("rust/a/src/l.rs", "1"),
    ("rust/b/src/l.rs", "2"),
    ("rust/Cargo.lock", "3"),
    ("scripts/x.py", "4"),
    ("Makefile", "5"),
];

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
fn the_one_reader_counts_a_closure_never_called_on_a_line_that_runs() {
    let text = "SF:/c/src/lib.rs\nFN:3,f\nFN:3,f_closure\nFNDA:4,f\nFNDA:0,f_closure\nDA:3,4\nDA:5,0\nDA:6,2\nend_of_record\nSF:/c/src/b.rs\nFN:1,g\nFNDA:1,g\nDA:1,1\nend_of_record\n";
    assert_eq!(
        lcov_missed(text),
        BTreeMap::from([("/c/src/lib.rs".to_owned(), vec![3, 5])])
    );
    let twice = "SF:/c/src/lib.rs\nFN:7,_RNvCsAAA_3lib1h\nFN:7,_RNvCsBBB_3lib1h\nFNDA:0,_RNvCsAAA_3lib1h\nFNDA:2,_RNvCsBBB_3lib1h\nDA:7,2\nFNDA:1,unknown\nend_of_record\n";
    assert_eq!(lcov_missed(twice), BTreeMap::new());
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

#[test]
fn no_crate_is_no_work_and_nothing_is_kept_outside_a_repository() {
    let empty = scratch("rustc-empty");
    let world = world_with(&empty, "exit 0");
    assert!(answer(&world, "format", &[], false)
        .stdout
        .contains("no Rust crate under rust/"));
    let (root, ..) = two_crates();
    let world = world_with(&root, "exit 0");
    let named = ["rust/a".to_owned()];
    assert!(answer(&world, "dead", &named, false)
        .stdout
        .contains("dead clean on 1 crate(s)"));
    assert!(answer(&world, "dead", &named, false)
        .stdout
        .contains("dead clean on 1 crate(s)"));
    assert_eq!(calls(&world), ["--version", "--version"]);
    assert_eq!(
        crates(&root, &["rust/a/Cargo.toml".to_owned()]),
        [root.join("rust/a/Cargo.toml")]
    );
    assert_eq!(crates(&root, &[]).len(), 2);
}

#[test]
fn each_command_asks_cargo_as_it_should() {
    let (root, a, _) = two_crates();
    let world = world_with(
        &root,
        "echo 'test result: ok. 3 passed'\necho run-output\nexit 0",
    );
    for (cmd, want) in [
        ("test", "test --quiet"),
        ("test-counters", "test --quiet --all-features"),
        ("format", "fmt --manifest"),
        ("hamlet", "run --release --quiet --bin hamlet"),
    ] {
        let before = calls(&world).len();
        let done = check(&world, cmd, &a, false);
        assert_eq!(done.code, 0);
        assert!(calls(&world)[before].starts_with(want));
    }
    assert!(calls(&world).last().unwrap().ends_with("-- spec.json"));
    let before = calls(&world).len();
    check(&world, "format", &a, true);
    assert!(calls(&world)[before].starts_with("fmt --check"));
    let summary = answer(&world, "test", &["rust/a".to_owned()], false);
    assert!(summary
        .stdout
        .contains("rust-checks: test on rust/a: test result: ok. 3 passed"));
    let shown = answer(&world, "hamlet", &["rust/a".to_owned()], false);
    assert!(shown.stdout.contains("run-output"));
}

#[test]
fn a_hamlet_run_takes_its_features_and_arguments_and_a_target_directory_can_be_named() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, "echo \"$CARGO_TARGET_DIR\"\nexit 0").map(|w| World {
        hamlet_features: "counters".to_owned(),
        hamlet_args: "--budget x".to_owned(),
        target_override: Some("/t".to_owned()),
        ..w
    });
    let done = check(&world, "hamlet", &a, false);
    assert_eq!(done.stdout.trim(), "/t");
    assert!(
        calls(&world)[0].contains("--features counters --bin hamlet")
            && calls(&world)[0].ends_with("-- --budget x")
    );
}

#[test]
fn the_counters_out_build_names_every_other_feature() {
    let dir = scratch("features");
    let manifest = dir.join("Cargo.toml");
    std::fs::write(
        &manifest,
        "[package]\n\n[features]\ncounters = []\nother-one = []\n\n[deps]\nx = 1\n",
    )
    .unwrap();
    assert_eq!(
        features_but(&manifest, "counters"),
        ["--features", "other-one"]
    );
    std::fs::write(&manifest, "[package]\n[features]\ncounters = []\n").unwrap();
    assert_eq!(features_but(&manifest, "counters"), Vec::<String>::new());
    let world = world_with(&dir, "exit 0");
    std::fs::write(&manifest, "[package]\n[features]\ncounters = []\nb = []\n").unwrap();
    check(&world, "test-no-counters", &manifest, false);
    assert!(calls(&world)[0].starts_with("test --quiet --features b"));
}

#[test]
fn a_public_function_nothing_calls_is_refused() {
    let (root, a, _) = two_crates();
    std::fs::write(
        root.join("rust/a/src/lib.rs"),
        "pub fn used() {}\npub fn orphan() {}\nfn f() { used(); }\n",
    )
    .unwrap();
    assert_eq!(dead_public(&a), ["orphan"]);
    let world = world_with(&root, "exit 0");
    let done = check(&world, "dead", &a, false);
    assert_eq!(done.code, 1);
    assert_eq!(
        done.stderr,
        "  pub fn orphan: nothing in Rust calls it - delete it, or call it\n"
    );
}

const LCOV_CARGO: &str = r#"case "$1 $2" in
  "llvm-cov show-env") echo "export FOO='bar'"; echo "not an assignment";;
  "llvm-cov report") out=""; while [ $# -gt 0 ]; do [ "$1" = "--output-path" ] && out="$2"; shift; done; [ -n "$out" ] && cat "$(dirname "$0")/lcov" > "$out";;
  "test --no-run") echo '{"executable":"'"$CARGO_TARGET_DIR"'/debug/deps/l7r_x-keep"}'; echo 'not json'; echo '{"reason":"x"}';;
esac
[ -f "$(dirname "$0")/failtest" ] && [ "$1" = test ] && [ "$2" != --no-run ] && { echo boom; exit 1; }
exit 0"#;

#[test]
fn what_a_crate_s_tests_leave_in_their_tmpdir_fails_it_by_name_and_goes() {
    let (root, a, _) = two_crates();
    let world = world_with(
        &root,
        "echo \"$TMPDIR\" > \"$(dirname \"$0\")/tmpdir\"\nexit 0",
    );
    let clean = check(&world, "test", &a, false);
    assert_eq!(clean.code, 0, "{}", clean.stderr);
    let used = std::fs::read_to_string(world.target.join("tmpdir")).unwrap();
    let under = std::env::temp_dir().join("l7r-rust-tests-a-");
    assert!(used.trim().starts_with(&under.display().to_string()));
    assert!(!Path::new(used.trim()).exists());
    let leaky = world_with(
        &root,
        // the process's shared directory is not a leak: the runner removes it with the run's directory
        "mkdir \"$TMPDIR/l7r-leak-1\" \"$TMPDIR/l7r-test-scratch\"; touch \"$TMPDIR/l7r-leak-2\"\nexit 0",
    );
    for cmd in ["test", "test-counters", "test-no-counters"] {
        let done = check(&leaky, cmd, &a, false);
        assert_eq!(done.code, 1, "{cmd}");
        assert!(done.stderr.contains(
            "the tests left 2 entries in their TMPDIR, which they must remove: l7r-leak-1, l7r-leak-2"
        ));
        assert!(done.stderr.contains("TempDir::new(tag)"));
    }
    let one = world_with(
        &root,
        "echo \"$TMPDIR\" > \"$(dirname \"$0\")/tmpdir\"; touch \"$TMPDIR/l7r-leak\"\nexit 0",
    );
    let said = check(&one, "test", &a, false).stderr;
    assert!(said.contains("left 1 entry in"));
    let used = std::fs::read_to_string(one.target.join("tmpdir")).unwrap();
    assert!(!Path::new(used.trim()).exists());
    let cover = world_with(&root, &format!("touch \"$TMPDIR/l7r-cover\"\n{LCOV_CARGO}"));
    std::fs::write(cover.target.join("lcov"), "").unwrap();
    assert_eq!(check(&cover, "cover", &a, false).code, 1);
}

#[test]
fn the_floor_reads_the_lines_and_clears_only_what_it_must() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, LCOV_CARGO);
    let source = std::fs::canonicalize(root.join("rust/a/src/lib.rs")).unwrap();
    std::fs::write(
        world.target.join("lcov"),
        format!(
            "SF:{}\nDA:3,0\nend_of_record\nSF:/elsewhere/b.rs\nDA:1,0\nend_of_record\n",
            source.display()
        ),
    )
    .unwrap();
    let work = world.target.join("cover-a");
    let deps = work.join("target/debug/deps");
    std::fs::create_dir_all(&deps).unwrap();
    for name in ["libl7r_old", "l7r_x-keep", "l7r_x-stale", "l7r_x-stale.d"] {
        std::fs::write(deps.join(name), "").unwrap();
    }
    std::fs::create_dir_all(deps.join("libl7r_dir")).unwrap();
    std::fs::write(work.join("target/old.profraw"), "").unwrap();
    let done = check(&world, "cover", &a, false);
    assert_eq!(done.code, 1);
    assert_eq!(
        done.stdout,
        format!("{} - lines no test reaches: 3\n", source.display())
    );
    assert!(
        !deps.join("libl7r_old").exists()
            && !deps.join("libl7r_dir").exists()
            && !deps.join("l7r_x-stale").exists()
    );
    assert!(deps.join("l7r_x-keep").exists() && deps.join("l7r_x-stale.d").exists());
    assert!(!work.join("target/old.profraw").exists());
    std::fs::write(world.target.join("lcov"), "").unwrap();
    assert_eq!(check(&world, "cover", &a, false).code, 0);
}

#[test]
fn a_coverage_run_that_fails_names_the_crate_and_not_a_line() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, LCOV_CARGO);
    std::fs::write(world.target.join("failtest"), "").unwrap();
    let work = world.target.join("w");
    let got = uncovered(&world, &a, &work);
    assert_eq!(
        got,
        BTreeMap::from([(a.parent().unwrap().display().to_string(), vec![0])])
    );
    let broke = world_with(&root, "[ \"$2\" = --no-run ] && exit 1\nexit 0");
    assert_eq!(uncovered(&broke, &a, &broke.target.join("w")).len(), 1);
}

#[test]
fn uncovered_answers_in_json_at_a_directory_a_test_shares() {
    let (root, _, _) = two_crates();
    let shared = scratch("shared");
    let world = world_with(&root, LCOV_CARGO).map(|w| World {
        cover_work: Some(shared.to_path_buf()),
        ..w
    });
    std::fs::write(world.target.join("lcov"), "").unwrap();
    let done = dispatch(
        &world,
        &[
            "uncovered".to_owned(),
            "--crate".to_owned(),
            "rust/a".to_owned(),
        ],
    );
    assert_eq!(done.stdout, "{}\n");
    assert!(shared.join("lcov.info").is_file());
}

#[test]
fn the_arguments_are_parsed_and_each_failure_says_its_fix() {
    let args = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let parsed = args(&["format", "--check", "--crate", "x"]);
    assert_eq!(parse(&parsed), Some(("format", vec!["x".to_owned()], true)));
    assert_eq!(parse(&args(&["nothing"])), None);
    assert_eq!(parse(&args(&["lint", "--crate"])), None);
    assert_eq!(parse(&args(&["lint", "--what"])), None);
    let (root, ..) = two_crates();
    // a counting build is run only where the crate has counters (T97)
    std::fs::write(
        root.join("rust/a/Cargo.toml"),
        "[package]\n[features]\ncounters = []\n",
    )
    .unwrap();
    let world = world_with(&root, "exit 1");
    assert_eq!(dispatch(&world, &args(&["nothing"])).code, 2);
    for (cmd, fix) in [
        ("format", "run `make format`"),
        ("test", "fix the failing test cargo names"),
        ("hamlet", "fix the stage"),
        ("test-no-counters", "hangs on the counters"),
        ("test-counters", "a count's assertion"),
        ("cover", "test the lines llvm-cov names"),
    ] {
        assert!(answer(&world, cmd, &["rust/a".to_owned()], false)
            .stderr
            .contains(fix));
    }
    std::fs::write(root.join("rust/a/src/lib.rs"), "pub fn orphan() {}\n").unwrap();
    assert!(answer(&world, "dead", &["rust/a".to_owned()], false)
        .stderr
        .contains("delete it, or call it"));
}

#[test]
fn the_kept_checks_and_the_small_helpers() {
    assert!(
        kept_reads("lint") == Some(Reads::Source)
            && kept_reads("cover") == Some(Reads::Tests)
            && kept_reads("format").is_none()
    );
    assert_eq!(
        relative(Path::new("/r/rust/b"), Path::new("/r/rust/a")),
        "../b"
    );
    assert_eq!(tail("abc"), "abc");
    assert_eq!(tail(&"x".repeat(5000)).len(), 4000);
    let missing = run("/no/such/program", &[], &BTreeMap::new());
    assert_eq!(missing.code, 127);
}

#[test]
fn a_tree_s_content_is_its_index_and_what_differs_from_it() {
    let dir = scratch("ids");
    let git = |args: &[&str]| {
        assert!(Command::new("git")
            .arg("-C")
            .arg(&dir)
            .args(["-c", "user.email=t@t", "-c", "user.name=t"])
            .args(args)
            .status()
            .unwrap()
            .success());
    };
    git(&["init", "-q"]);
    std::fs::write(dir.join("a"), "1").unwrap();
    git(&["add", "-A"]);
    git(&["commit", "-qm", "c"]);
    let before = content_ids(&dir);
    std::fs::write(dir.join("a"), "2").unwrap();
    std::fs::write(dir.join("b"), "3").unwrap();
    let after = content_ids(&dir);
    assert!(before["a"] != after["a"] && after.contains_key("b") && !before.contains_key("b"));
    // one id for one content, edited, staged or committed (feature 449 T93); a deleted file's is empty
    git(&["add", "-A"]);
    assert_eq!(content_ids(&dir), after);
    git(&["commit", "-qm", "d"]);
    assert_eq!(content_ids(&dir), after);
    std::fs::remove_file(dir.join("a")).unwrap();
    assert_eq!(content_ids(&dir)["a"], "");
}

#[test]
fn the_command_line_runs_from_the_environment() {
    let reply = super::cli(&["nothing".to_owned()]);
    assert_eq!(reply.code, 2);
    assert!(reply.stderr.contains("usage: l7r-gate rust"));
}

#[test]
fn a_nested_source_is_read_a_check_is_dispatched_and_cargo_is_found() {
    let (root, a, _) = two_crates();
    std::fs::create_dir_all(root.join("rust/a/src/sub")).unwrap();
    std::fs::write(root.join("rust/a/src/sub/m.rs"), "pub fn deep() {}\n").unwrap();
    assert_eq!(dead_public(&a), ["deep"]);
    let world = world_with(&root, "exit 0");
    assert_eq!(
        dispatch(
            &world,
            &["dead".to_owned(), "--crate".to_owned(), "rust/b".to_owned()]
        )
        .code,
        0
    );
    assert_eq!(super::cargo_exe(Path::new("/no/such/cargo")), "cargo");
    assert_eq!(super::cargo_exe(&a), a.display().to_string());
}

/// The linker's flags are every build's input (feature 449 T96): a changed `.cargo/config.toml` runs every crate's checks again, though
/// no crate owns it and none declares it.
#[test]
fn the_cargo_config_moves_every_check_s_key() {
    let (root, a, b) = two_crates();
    let both = [a.clone(), b];
    for (cmd, reads) in [("lint", Reads::Source), ("cover", Reads::Tests)] {
        let mut moved = ids(&BASE);
        moved.insert(".cargo/config.toml".to_owned(), "9".to_owned());
        let before = verdict_key(&root, &a, cmd, reads, &both, &ids(&BASE), "c");
        let after = verdict_key(&root, &a, cmd, reads, &both, &moved, "c");
        assert_ne!(before, after, "{cmd}");
    }
}

/// Every cargo call runs from the tree's root, where cargo finds `.cargo/config.toml` (rust-lld, feature 449 T96), whatever directory
/// started the check: the test, both lints, and the coverage run's show-env, build, tests and report.
#[test]
fn every_cargo_call_runs_from_the_tree_s_root() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, "pwd >> \"$(dirname \"$0\")/cwd\"");
    assert_eq!(check(&world, "test", &a, false).code, 0);
    assert_eq!(check(&world, "lint", &a, false).code, 0);
    let _ = uncovered(&world, &a, &world.target.join("cover"));
    let seen = std::fs::read_to_string(world.target.join("cwd")).unwrap();
    let want = std::fs::canonicalize(&root).unwrap().display().to_string();
    assert_eq!(seen.lines().count(), 7, "{seen}");
    assert!(seen.lines().all(|l| l == want), "{seen}");
}

/// The rust-lld `.cargo/config.toml` links with is the active toolchain's (feature 449 T96): no toolchain is pinned, and one that moves
/// leaves the `-B` path naming a directory that is gone, every link failing with gcc's "cannot find 'ld'".
#[test]
fn the_configured_rust_lld_is_the_active_toolchain_s() {
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let config = std::fs::read_to_string(tree.join(".cargo/config.toml")).unwrap();
    let named = config
        .split("link-arg=-B")
        .nth(1)
        .and_then(|r| r.split('"').next());
    let cargo = std::env::var("CARGO").unwrap_or_default();
    let rustc = Path::new(&cargo).with_file_name("rustc");
    let sysroot = Command::new(&rustc)
        .args(["--print", "sysroot"])
        .output()
        .unwrap();
    let want = format!(
        "{}/lib/rustlib/x86_64-unknown-linux-gnu/bin/gcc-ld",
        String::from_utf8_lossy(&sysroot.stdout).trim()
    );
    let fix = format!("set the -B path in .cargo/config.toml to {want}");
    assert_eq!(named, Some(want.as_str()), "{fix}");
    let lld = Path::new(&want).join("ld.lld");
    assert!(lld.is_file(), "{fix}: {} is missing", lld.display());
}

/// FR-008's one end-to-end test: the real cargo over the fixture crate, every other test here standing a fake cargo in its place.
#[test]
fn the_real_cargo_tests_a_real_crate() {
    let root = scratch("rustc-real");
    let fixture =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../tests/fixtures/rust/fixture");
    let crate_dir = root.join("rust/fixture");
    std::fs::create_dir_all(crate_dir.join("src")).unwrap();
    for name in ["Cargo.toml", "rust-toolchain.toml", "src/lib.rs"] {
        std::fs::copy(fixture.join(name), crate_dir.join(name)).unwrap();
    }
    let target = scratch("rustc-real-target");
    let world = World {
        root: root.to_path_buf(),
        cargo: "cargo".to_owned(),
        path_dir: target.to_path_buf(),
        target_override: None,
        no_reuse: true,
        hamlet_features: String::new(),
        hamlet_args: String::new(),
        hamlet_spec: "spec.json".to_owned(),
        cover_work: None,
        target: target.to_path_buf(),
    };
    let got = answer(&world, "test", &[], false);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    assert!(got.stdout.contains("test result: ok"), "{}", got.stdout);
}

/// The gate's shape (feature 449 T92): a binary crate `g` whose directory holds its crates, `g/crates/low` and `g/crates/mid`, the binary
/// building from `mid` and `mid` from `low`.
fn nested_crates() -> (TempDir, PathBuf, PathBuf, PathBuf) {
    let root = scratch("rustc-nested");
    let make = |dir: &str, manifest: &str, lib: &str| {
        std::fs::create_dir_all(root.join(format!("rust/{dir}/src"))).unwrap();
        std::fs::write(root.join(format!("rust/{dir}/Cargo.toml")), manifest).unwrap();
        std::fs::write(root.join(format!("rust/{dir}/src/lib.rs")), lib).unwrap();
    };
    make(
        "g",
        "[package]\nname = \"g\"\n[dependencies]\nmid = { path = \"crates/mid\" }\n",
        "fn main() { mid_only(); }\n",
    );
    make(
        "g/crates/mid",
        "[package]\nname = \"g_mid\"\n[dependencies]\nlow = { path = \"../low\" }\n",
        "pub fn mid_only() { low_used(); }\n",
    );
    make(
        "g/crates/low",
        "[package]\nname = \"g_low\"\n",
        "pub fn low_used() {}\npub fn low_dead() {}\n",
    );
    std::fs::write(root.join("rust/Cargo.toml"), "[workspace]\n").unwrap();
    let m = |d: &str| root.join(format!("rust/{d}/Cargo.toml"));
    let (g, mid, low) = (m("g"), m("g/crates/mid"), m("g/crates/low"));
    (root, g, mid, low)
}

#[test]
fn a_nested_crate_owns_its_files_and_a_dependency_s_dependency_moves_the_key() {
    let (root, g, mid, low) = nested_crates();
    let all = [g.clone(), mid.clone(), low.clone()];
    let base = ids(&[
        ("rust/g/src/lib.rs", "1"),
        ("rust/g/crates/mid/src/lib.rs", "2"),
        ("rust/g/crates/low/src/lib.rs", "3"),
    ]);
    let moved = |path: &str| {
        let mut m = base.clone();
        m.insert(path.to_owned(), "9".to_owned());
        m
    };
    for (cmd, reads) in [("lint", Reads::Source), ("cover", Reads::Tests)] {
        let key = |manifest: &Path, ids: &BTreeMap<String, String>| {
            verdict_key(&root, manifest, cmd, reads, &all, ids, "c")
        };
        // the binary moves with low, which it builds from only through mid
        assert_ne!(
            key(&g, &base),
            key(&g, &moved("rust/g/crates/low/src/lib.rs"))
        );
        // low's own edit moves low's key, though the binary's directory holds it
        assert_ne!(
            key(&low, &base),
            key(&low, &moved("rust/g/crates/low/src/lib.rs"))
        );
        // and the binary's own file does not move low's
        assert_eq!(key(&low, &base), key(&low, &moved("rust/g/src/lib.rs")));
        assert_eq!(key(&mid, &base), key(&mid, &moved("rust/g/src/lib.rs")));
    }
    // the dead check counts calls across the whole family (T100): low's dead key moves with the binary's file, which can drop the last
    // call to a low function; a file outside the family moves nothing
    let dead = |ids: &BTreeMap<String, String>| {
        verdict_key(&root, &low, "dead", Reads::Source, &all, ids, "c")
    };
    assert_ne!(dead(&base), dead(&moved("rust/g/src/lib.rs")));
    assert_ne!(dead(&base), dead(&moved("rust/g/crates/mid/src/lib.rs")));
    assert_eq!(dead(&base), dead(&moved("rust/other/src/lib.rs")));
}

#[test]
fn a_nested_crate_s_lines_and_calls_are_its_own_and_the_family_shares_one_coverage_build() {
    let (root, g, mid, low) = nested_crates();
    assert_eq!(dead_public(&low), ["low_dead"]);
    assert!(dead_public(&mid).is_empty());
    assert_eq!(own_libs(&low), "libg_low-");
    assert_eq!(own_libs(&root.join("rust/Cargo.toml")), "libl7r_");
    let world = world_with(&root, LCOV_CARGO);
    assert_eq!(super::cover_dir(&world, &low), world.target.join("cover-g"));
    assert_eq!(super::cover_dir(&world, &g), world.target.join("cover-g"));
    let canon = |p: &str| std::fs::canonicalize(root.join(p)).unwrap();
    std::fs::write(
        world.target.join("lcov"),
        format!(
            "SF:{}\nDA:1,0\nend_of_record\nSF:{}\nDA:2,0\nend_of_record\n",
            canon("rust/g/src/lib.rs").display(),
            canon("rust/g/crates/low/src/lib.rs").display()
        ),
    )
    .unwrap();
    let got = uncovered(&world, &g, &world.target.join("w"));
    assert_eq!(
        got.keys().cloned().collect::<Vec<_>>(),
        [canon("rust/g/src/lib.rs").display().to_string()]
    );
    let got = uncovered(&world, &low, &world.target.join("w2"));
    assert_eq!(
        got.keys().cloned().collect::<Vec<_>>(),
        [canon("rust/g/crates/low/src/lib.rs").display().to_string()]
    );
}

/// `two_crates` in a repository, so a kept result has a git directory to live in.
fn kept_crates() -> (TempDir, PathBuf, PathBuf) {
    let (root, a, b) = two_crates();
    assert!(Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    (root, a, b)
}

#[test]
fn a_manifest_declares_what_its_tests_read_and_an_undeclared_reader_is_refused() {
    let (root, a, b) = kept_crates();
    assert!(declared_reads(&a).is_empty());
    std::fs::write(
        &a,
        "[package]\nname = \"a\"\n\n[package.metadata.l7r]\n# why\nreads = [\n  \"scripts/\",\n  \"Makefile\",\n]\n\n[dependencies]\nx = \"1\"\n",
    )
    .unwrap();
    assert_eq!(declared_reads(&a), ["scripts/", "Makefile"]);
    std::fs::write(
        root.join("rust/b/src/lib.rs"),
        "fn f() { let _ = env!(\"CARGO_MANIFEST_DIR\"); }\n",
    )
    .unwrap();
    let both = [a.clone(), b.clone()];
    assert_eq!(undeclared(&both), [&b]);
    let world = world_with(&root, "exit 0");
    for cmd in ["test", "test-counters", "cover"] {
        let refused = answer(&world, cmd, &[], false);
        assert_eq!(refused.code, 1);
        assert_eq!(refused.stderr, "rust-checks: these crates' sources name the tree outside the crate (CARGO_MANIFEST_DIR, top(), toplevel()) but their Cargo.toml declares nothing their tests read, so a kept result could stand over a tree the tests no longer pass on:\n  rust/b/\nadd `[package.metadata.l7r]` with `reads = [\"<path>/\", ...]` (\".\" the whole tree) to each Cargo.toml\n");
    }
    assert!(calls(&world).is_empty(), "refused before any cargo");
    // lint reads no tree
    assert_eq!(answer(&world, "lint", &[], false).code, 0);
    std::fs::write(&b, "[package]\n[package.metadata.l7r]\nreads = [\".\"]\n").unwrap();
    assert!(undeclared(&both).is_empty());
}

/// A cargo whose test build names one executable, `exe` beside it, and fails when `nobuild` is there; every other call passes.
const BINARY_CARGO: &str = r#"case "$1 $2" in
  "test --no-run") [ -f "$(dirname "$0")/nobuild" ] && exit 1; echo '{"executable":"'"$(dirname "$0")"'/exe"}';;
  "test --quiet") echo 'test result: ok. 1 passed';;
esac
exit 0"#;

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

/// Coverage instruments the workspace's crates only (T100): the coverage flags leave RUSTFLAGS, the rest stays for every crate, and a
/// wrapper cargo calls for the workspace's crates alone adds them; written once, and left be while its text is the same; no RUSTFLAGS,
/// nothing done.
#[test]
fn coverage_instruments_the_workspace_s_crates_only() {
    let dir = scratch("rustc-cover-wrapper");
    let script = dir.join("instrument.sh");
    let lld = "-C link-arg=-fuse-ld=lld";
    let shown = || {
        BTreeMap::from([(
            "RUSTFLAGS".to_owned(),
            format!("{lld} -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target"),
        )])
    };
    let mut env = shown();
    workspace_only(&mut env, &script);
    assert_eq!(env["RUSTFLAGS"], lld);
    assert_eq!(env["RUSTC_WORKSPACE_WRAPPER"], script.display().to_string());
    let text = std::fs::read_to_string(&script).unwrap();
    assert_eq!(
        text,
        "#!/bin/sh\nexec \"$@\" -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target\n"
    );
    let ran = Command::new(&script)
        .args(["echo", "rustc"])
        .output()
        .unwrap();
    assert_eq!(
        String::from_utf8_lossy(&ran.stdout),
        "rustc -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target\n"
    );
    let before = std::fs::metadata(&script).unwrap().modified().unwrap();
    std::thread::sleep(std::time::Duration::from_millis(20));
    workspace_only(&mut shown(), &script);
    let after = std::fs::metadata(&script).unwrap().modified().unwrap();
    assert_eq!(after, before, "not written again");
    let mut none = BTreeMap::new();
    workspace_only(&mut none, &script);
    assert!(none.is_empty());
}
