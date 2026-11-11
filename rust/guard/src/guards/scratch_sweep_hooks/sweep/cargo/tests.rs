//! The cache's sweep on a fixture: a cargo root, a clones directory, the mirror's name, and every entry's age set by hand.

use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{plan, variant_of};
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

const DAY: u64 = 86_400;

/// Write `path` and set it and every directory from it up to `top` to `days` ago.
fn put(top: &Path, path: &Path, days: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, "x").unwrap();
    age(top, path, days);
}

/// A directory with nothing in it, `days` old, as are its parents up to `top`.
fn dir(top: &Path, path: &Path, days: u64) {
    std::fs::create_dir_all(path).unwrap();
    age(top, path, days);
}

fn age(top: &Path, path: &Path, days: u64) {
    let when = SystemTime::now() - Duration::from_secs(days * DAY);
    let mut at = Some(path);
    while let Some(p) = at {
        File::open(p).unwrap().set_modified(when).unwrap();
        if p == top {
            break;
        }
        at = p.parent();
    }
}

fn world() -> (TempDir, Config) {
    let base = TempDir::new("guard-sweep-cargo");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("cargo");
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    std::fs::create_dir_all(c.clones.join("live-clone")).unwrap();
    (base, c)
}

fn names(found: &[(PathBuf, &str)], c: &Config) -> Vec<String> {
    let mut v: Vec<String> = found
        .iter()
        .map(|(p, _)| p.strip_prefix(&c.cargo).unwrap().display().to_string())
        .collect();
    v.sort();
    v
}

fn cutoff() -> SystemTime {
    SystemTime::now() - Duration::from_secs(3 * DAY)
}

#[test]
fn a_gone_tree_s_build_goes_whole_and_a_live_one_loses_only_old_variants() {
    let (_base, c) = world();
    let k = &c.cargo;
    // the mirror's and a clone's, however old, are kept whole
    put(k, &k.join("diagram/l7r-guard.good"), 30);
    put(k, &k.join("live-clone/debug/x"), 30);
    // a scratch clone's, idle: whole; a fresh one: kept
    put(k, &k.join("gone-scratch/debug/deps/liba-1.rlib"), 9);
    put(k, &k.join("fresh-scratch/debug/x"), 0);
    // six old variants of one crate in a store: the oldest two go; five fresh ones of another: none
    for (i, d) in [10, 11, 12, 13, 14, 15].into_iter().enumerate() {
        put(
            k,
            &k.join(format!("diagram/debug/deps/libserde-h{i}.rlib")),
            d,
        );
    }
    for i in 0..5 {
        put(
            k,
            &k.join(format!("diagram/debug/deps/libfresh-h{i}.rlib")),
            0,
        );
    }
    // incremental and fingerprint entries are directories; a nested coverage target's store is found too
    for (i, d) in [10, 11, 12, 13, 14].into_iter().enumerate() {
        dir(
            k,
            &k.join(format!(
                "live-clone/cover-gate/target/debug/incremental/l7r_fixture-h{i}"
            )),
            d,
        );
    }
    // a store deeper than five is not looked for, and a symlink is not followed
    for i in 0..6 {
        put(
            k,
            &k.join(format!("live-clone/a/b/c/d/e/deps/liby-{i}.rlib")),
            30,
        );
    }
    std::os::unix::fs::symlink(k.join("gone-scratch"), k.join("link")).unwrap();
    std::os::unix::fs::symlink(
        k.join("gone-scratch"),
        k.join("diagram/debug/deps/libz-1.rlib"),
    )
    .unwrap();
    std::fs::write(k.join("a-file"), "x").unwrap();
    let got = plan(&c, cutoff());
    assert_eq!(
        names(&got, &c),
        [
            "diagram/debug/deps/libserde-h4.rlib",
            "diagram/debug/deps/libserde-h5.rlib",
            "gone-scratch",
            "live-clone/cover-gate/target/debug/incremental/l7r_fixture-h4",
        ]
    );
    // no build directory is removed whole where the clones cannot be listed, and no cache is no sweep
    let mut blind = Config::from_env(&|_| None, 4242);
    blind.cargo = c.cargo.clone();
    blind.clones = c.clones.join("missing");
    blind.mirror = c.mirror.clone();
    assert!(!names(&plan(&blind, cutoff()), &c).contains(&"gone-scratch".to_owned()));
    blind.cargo = c.cargo.join("a-file");
    assert!(plan(&blind, cutoff()).is_empty());
}

#[test]
fn an_entry_whose_age_cannot_be_read_is_kept() {
    use std::os::unix::fs::PermissionsExt;
    let (_base, c) = world();
    let k = &c.cargo;
    let store = k.join("live-clone/debug/incremental");
    for i in 0..6 {
        dir(k, &store.join(format!("c-h{i}/s")), 20);
    }
    let locked = store.join("c-h0/s");
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o000)).unwrap();
    age(k, &store.join("c-h0"), 20);
    let got = names(&plan(&c, cutoff()), &c);
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o755)).unwrap();
    assert_eq!(got.len(), 1, "{got:?}");
    assert!(!got.iter().any(|g| g.ends_with("c-h0")), "{got:?}");
}

#[test]
fn a_variant_is_its_name_without_the_hash() {
    assert_eq!(variant_of("libserde-ab12.rlib"), "libserde.rlib");
    assert_eq!(variant_of("serde-ab12.d"), "serde.d");
    assert_eq!(variant_of("l7r_gate-0hjj"), "l7r_gate.");
    assert_eq!(variant_of("plain"), "plain.");
    assert_eq!(variant_of(".hidden"), ".hidden.");
    assert_eq!(variant_of("a-b.x-y"), "a-b.x.");
}
