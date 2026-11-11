//! The crate checks, over a fake cargo.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    answer, check, content_ids, crates, dead_public, dispatch, features_but, kept_reads,
    lcov_missed, own_libs, parse, relative, run, tail, uncovered, verdict_key, Reads, World,
};
use crate::checks::scratch;

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

fn world_with(root: &Path, body: &str) -> World {
    let target = scratch("rustc-target");
    World {
        root: root.to_owned(),
        cargo: fake_cargo(&target, body),
        path_dir: target.clone(),
        target_override: None,
        no_reuse: false,
        hamlet_features: String::new(),
        hamlet_args: String::new(),
        hamlet_spec: "spec.json".to_owned(),
        cover_work: None,
        target,
    }
}

fn calls(world: &World) -> Vec<String> {
    std::fs::read_to_string(world.target.join("calls"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

fn two_crates() -> (PathBuf, PathBuf, PathBuf) {
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
    let tree = key("cover", Reads::Tree, &[], "cargo 1");
    assert_ne!(
        tree,
        key("cover", Reads::Tree, &[("Makefile", "9")], "cargo 1")
    );
    assert_eq!(
        tree,
        key("cover", Reads::Tree, &[("rust/b/src/l.rs", "9")], "cargo 1")
    );
    assert_eq!(
        tree,
        key(
            "cover",
            Reads::Tree,
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
    for (cmd, reads) in [("lint", Reads::Source), ("cover", Reads::Tree)] {
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
    let full = World {
        no_reuse: true,
        ..world
    };
    assert_eq!(answer(&full, "lint", &[], false).code, 0);
    assert_eq!(clippy(&full), before + 3, "a full run runs everything");
}

#[test]
fn no_crate_is_no_work_and_a_named_crate_is_not_kept() {
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
    assert!(calls(&world).is_empty());
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
    let world = World {
        hamlet_features: "counters".to_owned(),
        hamlet_args: "--budget x".to_owned(),
        target_override: Some("/t".to_owned()),
        ..world_with(&root, "echo \"$CARGO_TARGET_DIR\"\nexit 0")
    };
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
    let world = World {
        cover_work: Some(shared.clone()),
        ..world_with(&root, LCOV_CARGO)
    };
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
            && kept_reads("cover") == Some(Reads::Tree)
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

/// FR-008's one end-to-end test: the real cargo over the fixture crate, every other test here standing a fake cargo in its place.
#[test]
fn the_real_cargo_tests_a_real_crate() {
    let root = scratch("rustc-real");
    let fixture = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../tests/fixtures/rust/fixture");
    let crate_dir = root.join("rust/fixture");
    std::fs::create_dir_all(crate_dir.join("src")).unwrap();
    for name in ["Cargo.toml", "rust-toolchain.toml", "src/lib.rs"] {
        std::fs::copy(fixture.join(name), crate_dir.join(name)).unwrap();
    }
    let target = scratch("rustc-real-target");
    let world = World {
        root,
        cargo: "cargo".to_owned(),
        path_dir: target.clone(),
        target_override: None,
        no_reuse: true,
        hamlet_features: String::new(),
        hamlet_args: String::new(),
        hamlet_spec: "spec.json".to_owned(),
        cover_work: None,
        target,
    };
    let got = answer(&world, "test", &[], false);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    assert!(got.stdout.contains("test result: ok"), "{}", got.stdout);
}

/// The gate's shape (feature 449 T92): a binary crate `g` whose directory holds its crates, `g/crates/low` and `g/crates/mid`, the binary
/// building from `mid` and `mid` from `low`.
fn nested_crates() -> (PathBuf, PathBuf, PathBuf, PathBuf) {
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
    (root.clone(), m("g"), m("g/crates/mid"), m("g/crates/low"))
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
    for (cmd, reads) in [("lint", Reads::Source), ("cover", Reads::Tree)] {
        let key = |manifest: &Path, ids: &BTreeMap<String, String>| {
            verdict_key(&root, manifest, cmd, reads, &all, ids, "c")
        };
        // the binary moves with low, which it builds from only through mid
        assert_ne!(key(&g, &base), key(&g, &moved("rust/g/crates/low/src/lib.rs")));
        // low's own edit moves low's key, though the binary's directory holds it
        assert_ne!(key(&low, &base), key(&low, &moved("rust/g/crates/low/src/lib.rs")));
        // and the binary's own file does not move low's
        assert_eq!(key(&low, &base), key(&low, &moved("rust/g/src/lib.rs")));
        assert_eq!(key(&mid, &base), key(&mid, &moved("rust/g/src/lib.rs")));
    }
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
