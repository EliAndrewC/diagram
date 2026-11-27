//! The prune inside a live build directory on a fixture (451 T515): a cargo root whose build directories hold profiles at one and
//! three levels down, every file's mtime and atime set by hand, and a stand-in `/proc`.

use std::fs::{File, FileTimes};
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{crate_of, kind_of, plan, still_stale, unit_of, WHY};
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

const HOUR: u64 = 3600;

fn ago(h: u64) -> SystemTime {
    SystemTime::now() - Duration::from_secs(h * HOUR)
}

/// Write `path`, built `m` hours ago and last read `a` hours ago.
fn put(path: &Path, m: u64, a: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, "x").unwrap();
    let times = FileTimes::new().set_modified(ago(m)).set_accessed(ago(a));
    File::options()
        .write(true)
        .open(path)
        .unwrap()
        .set_times(times)
        .unwrap();
}

/// Every directory under `root` set 200 hours old, older than any file: a directory's mtime moves only as its files do.
fn settle(root: &Path) {
    for (p, _, m) in crate::guards::scratch_sweep_hooks::sweep::entries(root) {
        if m.is_dir() {
            settle(&p);
            File::open(&p).unwrap().set_modified(ago(200)).unwrap();
        }
    }
}

fn world() -> (TempDir, Config) {
    let base = TempDir::new("guard-sweep-prune");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("cargo");
    c.proc = base.join("proc");
    std::fs::create_dir_all(c.proc.join("1")).unwrap();
    (base, c)
}

/// A profile with `foo` built twice, the old one stale; returns the stale fingerprint.
fn profile(p: &Path) -> PathBuf {
    put(&p.join(".fingerprint/foo-aaaa/lib-foo"), 100, 100);
    put(&p.join(".fingerprint/foo-bbbb/lib-foo"), 1, 1);
    p.join(".fingerprint/foo-aaaa")
}

fn planned(c: &Config, held: &[PathBuf]) -> Vec<PathBuf> {
    settle(&c.cargo);
    found(c, held)
}

/// The plan as it stands, the directories' ages left as they are.
fn found(c: &Config, held: &[PathBuf]) -> Vec<PathBuf> {
    let found = plan(c, held);
    assert!(found.iter().all(|(_, why)| *why == WHY));
    found.into_iter().map(|(p, _)| p).collect()
}

#[test]
fn a_deep_profile_is_found_and_files_beside_profiles_are_passed_over() {
    let (_base, c) = world();
    put(&c.cargo.join("stray.profraw"), 1, 1);
    put(&c.cargo.join("tree/build.log"), 1, 1);
    let deep = profile(&c.cargo.join("tree/cover-gate/target/debug"));
    let top = profile(&c.cargo.join("tree/debug"));
    let mut got = planned(&c, &[]);
    got.sort();
    assert_eq!(got, vec![deep, top]);
}

#[test]
fn a_held_profile_and_a_build_directory_a_live_gate_records_are_skipped_whole() {
    let (_base, c) = world();
    let busy = c.cargo.join("gate-tree");
    profile(&busy.join("debug"));
    std::fs::write(
        c.proc.join("1/stat"),
        format!("1 (l7r-gate) S {}777 0\n", "0 ".repeat(18)),
    )
    .unwrap();
    std::fs::write(
        busy.join("rust-checks-run.json"),
        r#"{"members":[{"pid":1,"start":777}]}"#,
    )
    .unwrap();
    let held = c.cargo.join("held-tree/debug");
    profile(&held);
    let free = profile(&c.cargo.join("held-tree/tool"));
    assert_eq!(planned(&c, &[held.join(".cargo-lock")]), vec![free]);
}

#[test]
fn an_unreadable_entry_is_kept_and_an_empty_profile_takes_nothing() {
    let (_base, c) = world();
    let p = c.cargo.join("tree/debug");
    let stale = profile(&p);
    put(&p.join("incremental/foo-x1/s-1/f"), 100, 100);
    put(&p.join("incremental/foo-x2/s-2/f"), 1, 1);
    let locked = p.join("incremental/foo-x1/s-1");
    std::fs::create_dir_all(c.cargo.join("empty/debug/.fingerprint")).unwrap();
    settle(&c.cargo);
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o000)).unwrap();
    let got = found(&c, &[]);
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o755)).unwrap();
    assert_eq!(got, vec![stale]);
}

#[test]
fn a_unit_spans_its_stores_and_goes_whole_by_its_kind() {
    let (_base, c) = world();
    let p = c.cargo.join("tree/debug");
    for (f, m) in [
        ("deps/libserde-old.rlib", 100),
        ("deps/libserde-old.rmeta", 100),
        ("deps/serde-old.d", 100),
        (".fingerprint/serde-old/lib-serde", 100),
        (".fingerprint/serde-new/lib-serde", 1),
        // a build script's unit is its own kind: its one build kept, old as it is
        (".fingerprint/serde-bs/build-script-build-script-build", 100),
        ("build/serde-bs/build-script-build", 100),
    ] {
        put(&p.join(f), m, m);
    }
    let mut got = planned(&c, &[]);
    got.sort();
    let want: Vec<PathBuf> = [
        ".fingerprint/serde-old",
        "deps/libserde-old.rlib",
        "deps/libserde-old.rmeta",
        "deps/serde-old.d",
    ]
    .iter()
    .map(|f| p.join(f))
    .collect();
    assert_eq!(got, want);
}

#[test]
fn names_read_as_units_crates_and_kinds() {
    assert_eq!(unit_of("libserde-ab12.rlib"), "serde-ab12");
    assert_eq!(unit_of("libl7r_phases-9.so"), "l7r_phases-9");
    assert_eq!(unit_of("l7r_gate-0f.d"), "l7r_gate-0f");
    assert_eq!(unit_of("l7r_gate-0f"), "l7r_gate-0f");
    assert_eq!(unit_of("libc-1.d"), "libc-1");
    assert_eq!(crate_of("l7r_mode_a-07byo"), "l7r_mode_a");
    assert_eq!(crate_of("plain"), "plain");
    let (base, _c) = world();
    let fp = base.join("fp");
    for f in [
        "lib-x.json",
        "dep-lib-x",
        "output-lib-x",
        "invoked.timestamp",
    ] {
        put(&fp.join(f), 1, 1);
    }
    assert_eq!(kind_of(&fp), "");
    put(&fp.join("test-lib-x"), 1, 1);
    put(&fp.join("lib-x"), 1, 1);
    assert_eq!(kind_of(&fp), "lib-x");
}

#[test]
fn at_removal_an_entry_read_since_the_plan_is_kept() {
    let (base, c) = world();
    let f = base.join("deps/libfoo-a.rlib");
    put(&f, 100, 100);
    assert!(still_stale(&c, &f, SystemTime::now()));
    // the knob is floored at 25 h: a knob of 1 h still keeps a file read 2 h ago
    let mut short = c;
    short.stale = Duration::from_secs(HOUR);
    put(&f, 100, 2);
    assert!(!still_stale(&short, &f, SystemTime::now()));
    assert!(!still_stale(&short, &base.join("gone"), SystemTime::now()));
}

#[test]
fn at_removal_a_unit_s_artifact_is_kept_once_a_build_read_its_fingerprint() {
    let (base, c) = world();
    let p = base.join("debug");
    let rlib = p.join("deps/libfoo-a.rlib");
    let script = p.join("build/foo-a/out");
    put(&rlib, 100, 100);
    put(&script, 100, 100);
    // no fingerprint: the artifact judged alone; a stale fingerprint: still stale
    assert!(still_stale(&c, &rlib, SystemTime::now()));
    put(&p.join(".fingerprint/foo-a/lib-foo"), 100, 100);
    settle(&p);
    assert!(still_stale(&c, &rlib, SystemTime::now()));
    // a freshness check reads the fingerprint alone: the rlib and the build script's directory are kept
    put(&p.join(".fingerprint/foo-a/lib-foo"), 100, 0);
    assert!(!still_stale(&c, &rlib, SystemTime::now()));
    assert!(!still_stale(&c, &p.join("build/foo-a"), SystemTime::now()));
}
