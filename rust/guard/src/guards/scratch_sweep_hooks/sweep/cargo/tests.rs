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
    built_from(k, &k.join("gone-scratch"), &k.join("no/such/tree"), 9);
    put(k, &k.join("fresh-scratch/debug/x"), 0);
    // eighteen old variants of one crate in a store: the oldest two go, sixteen kept (451 T158); five fresh ones of another: none
    for (i, d) in (10..28).enumerate() {
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
    for (i, d) in (10..27).enumerate() {
        dir(
            k,
            &k.join(format!(
                "live-clone/cover-gate/target/debug/incremental/l7r_fixture-h{i}"
            )),
            d,
        );
    }
    // a store deeper than five is not looked for, and a symlink is not followed
    for i in 0..18 {
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
    let got = plan(&c, cutoff(), &[], within());
    assert_eq!(
        names(&got, &c),
        [
            "diagram/debug/deps/libserde-h16.rlib",
            "diagram/debug/deps/libserde-h17.rlib",
            "gone-scratch",
            "live-clone/cover-gate/target/debug/incremental/l7r_fixture-h16",
        ]
    );
    // no build directory is removed whole where the clones cannot be listed, and no cache is no sweep
    let mut blind = Config::from_env(&|_| None, 4242);
    blind.cargo = c.cargo.clone();
    blind.clones = c.clones.join("missing");
    blind.mirror = c.mirror.clone();
    assert!(!names(&plan(&blind, cutoff(), &[], within()), &c).contains(&"gone-scratch".to_owned()));
    blind.cargo = c.cargo.join("a-file");
    assert!(plan(&blind, cutoff(), &[], within()).is_empty());
}

/// What at the cache's root is no build directory goes once idle (451 T523): a loose file (444 T17's `fixture-*.profraw`,
/// `fixture.profdata`, cargo's `.rustc_info.json` of a run that used the root as its target), and a shell that holds nothing but
/// cargo's two markers (`tree/`, its profile evicted) - whatever its name, `tree` and `main-tree` no longer built into; never the
/// root's `CACHEDIR.TAG`, a fresh one, a held one, a live tree's shell, or a directory with anything else in it.
#[test]
fn what_at_the_root_is_no_build_directory_goes_once_idle() {
    let (_base, c) = world();
    let k = &c.cargo;
    for f in [
        "fixture-1-2_3.profraw",
        "fixture.profdata",
        ".rustc_info.json",
        "CACHEDIR.TAG",
    ] {
        put(k, &k.join(f), 9);
    }
    put(k, &k.join("fresh.profraw"), 0);
    put(k, &k.join("held.profraw"), 9);
    for shell in ["tree", "main-tree", "old-shell", "live-clone", "held-shell"] {
        put(k, &k.join(shell).join(".rustc_info.json"), 9);
        put(k, &k.join(shell).join("CACHEDIR.TAG"), 9);
    }
    dir(k, &k.join("empty-shell"), 9);
    put(k, &k.join("fresh-shell/CACHEDIR.TAG"), 0);
    // the guard's kept binary beside the markers is no shell (`diagram-research/`, no profile, no dep-info)
    put(k, &k.join("kept-binary/CACHEDIR.TAG"), 9);
    put(k, &k.join("kept-binary/l7r-guard.good"), 9);
    // a model trial's arm, its checkout under its own name and gone: proven dead by its dep-info
    put(k, &k.join("tree/debug/x"), 9);
    built_from(k, &k.join("tree"), &k.join("no/such/arm/tree"), 9);
    let held = [k.join("held.profraw"), k.join("held-shell/CACHEDIR.TAG")];
    let got = plan(&c, cutoff(), &held, within());
    assert_eq!(
        names(&got, &c),
        [
            ".rustc_info.json",
            "empty-shell",
            "fixture-1-2_3.profraw",
            "fixture.profdata",
            "main-tree",
            "old-shell",
            "tree",
        ]
    );
}

/// A build directory's top dep-info, `<target>/<profile>/<bin>.d`, naming the tree it was built from, `days` old.
fn built_from(top: &Path, target: &Path, tree: &Path, days: u64) {
    let d = target.join("tool/l7r-gate.d");
    put(top, &d, days);
    std::fs::write(
        &d,
        format!(
            // a path outside any tree and a relative one name no tree
            "{}: {}/rust/gate/src/main.rs {}/rust/Cargo.toml /usr/include/x.h rel/rust/a.rs\n",
            target.join("tool/l7r-gate").display(),
            tree.display(),
            tree.display()
        ),
    )
    .unwrap();
    age(top, &d, days);
}

#[test]
fn a_target_is_taken_whole_only_once_proven_dead() {
    let (base, c) = world();
    let k = c.cargo.clone();
    let living = base.join("scratch/t94/rc");
    std::fs::create_dir_all(living.join("rust")).unwrap();
    // rc (2026-11-22's dry run): a scratch clone's checks target, its run record empty, its tree still on disk - kept
    for f in ["rust-checks-run.lock", "debug/x", "cover-gate/x"] {
        put(&k, &k.join("rc").join(f), 9);
    }
    std::fs::write(k.join("rc/rust-checks-run.json"), r#"{"members":[]}"#).unwrap();
    age(&k, &k.join("rc/rust-checks-run.json"), 9);
    built_from(&k, &k.join("rc"), &living, 9);
    // names a current code path builds into, their last tree gone: the hooks suites' and the review snapshot's `clone`, a clone's
    // landing worktrees - kept; the model trial's `tree` and `main-tree`, built into by no code since 451 T523 - taken
    let gone = base.join("nowhere");
    for name in [
        "clone",
        "tree",
        "main-tree",
        "live-clone-land",
        "live-clone-tooling",
    ] {
        built_from(
            &k,
            &k.join(name),
            &gone.join(".git/review-snapshot/u").join(name),
            9,
        );
    }
    // no dep-info to read: it cannot be proven dead - kept
    put(&k, &k.join("unknown/debug/x"), 9);
    // head: its one tree gone and no code path names it - taken
    built_from(&k, &k.join("head"), &gone.join("t235/head"), 9);
    // a trial worktree removed by hand just after its build (451 T246's point 2): its build directory goes at the next sweep with no
    // idle wait - keyed to its tree's existence, not its age
    built_from(&k, &k.join("trial-wt"), &gone.join("t300/trial-wt"), 0);
    assert_eq!(
        names(&plan(&c, cutoff(), &[], within()), &c),
        ["head", "main-tree", "tree", "trial-wt"]
    );
}

#[test]
fn an_entry_whose_age_cannot_be_read_is_kept() {
    use std::os::unix::fs::PermissionsExt;
    let (_base, c) = world();
    let k = &c.cargo;
    let store = k.join("live-clone/debug/incremental");
    for i in 0..18 {
        dir(k, &store.join(format!("c-h{i}/s")), 20);
    }
    let locked = store.join("c-h0/s");
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o000)).unwrap();
    age(k, &store.join("c-h0"), 20);
    let got = names(&plan(&c, cutoff(), &[], within()), &c);
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

#[test]
fn a_registered_worktree_s_name_and_the_tooling_landing_s_are_live_and_a_used_target_is_kept_whole()
{
    let (base, mut c) = world();
    let k = c.cargo.clone();
    // a worktree of the clone made in scratch (`/tmp/t33/wt`): its name's build directory is live; one whose tree is gone is not, nor
    // an admin directory with no gitdir
    let scratch = base.join("scratch/t33/wt");
    std::fs::create_dir_all(&scratch).unwrap();
    let admin = c.clones.join("live-clone/.git/worktrees");
    std::fs::create_dir_all(admin.join("wt")).unwrap();
    std::fs::write(
        admin.join("wt/gitdir"),
        format!("{}/.git\n", scratch.display()),
    )
    .unwrap();
    std::fs::create_dir_all(admin.join("gone")).unwrap();
    std::fs::write(
        admin.join("gone/gitdir"),
        format!("{}/.git\n", base.join("nowhere/old").display()),
    )
    .unwrap();
    std::fs::create_dir_all(admin.join("bare")).unwrap();
    for name in [
        "wt",
        "old",
        "live-clone-land-tooling",
        "held",
        "running",
        "ran",
    ] {
        put(&k, &k.join(format!("{name}/debug/x")), 9);
        built_from(&k, &k.join(name), &base.join("nowhere").join(name), 9);
    }
    // held: a live process's path under it; running: a run record naming this very process; ran: one naming a process gone, deeper
    let me = std::process::id();
    let start = super::started(&c.proc, u64::from(me)).unwrap();
    std::fs::write(
        k.join("running/debug/rust-checks-run.json"),
        serde_json::json!({"members": [{"pid": 0}, {"pid": me, "start": start}]}).to_string(),
    )
    .unwrap();
    std::fs::create_dir_all(k.join("ran/a/b")).unwrap();
    std::fs::write(
        k.join("ran/a/b/rust-checks-run.json"),
        serde_json::json!({"members": [{"pid": me, "start": start + 1}]}).to_string(),
    )
    .unwrap();
    age(&k, &k.join("ran/a/b/rust-checks-run.json"), 9);
    let held = [k.join("held/debug/.cargo-lock")];
    let got = names(&plan(&c, cutoff(), &held, within()), &c);
    assert_eq!(got, ["old", "ran"]);
    assert_eq!(super::worktrees(&c).len(), 1);
    assert!(super::started(&c.proc, 4_000_000_000).is_none());
    // the mirror's own worktrees count too
    c.mirror = base.join("mirror");
    std::fs::create_dir_all(c.mirror.join(".git/worktrees/x")).unwrap();
    std::fs::write(
        c.mirror.join(".git/worktrees/x/gitdir"),
        format!("{}/.git", base.join("scratch/t33").display()),
    )
    .unwrap();
    assert_eq!(super::worktrees(&c).len(), 2);
}

/// Within the budget: no live tree's profile asked for (451 T245).
fn within() -> super::Budget {
    super::Budget {
        need: 0,
        idle: SystemTime::now(),
    }
}

#[test]
fn past_the_budget_a_profile_taken_whole_lists_none_of_its_variants() {
    let (_base, c) = world();
    let k = &c.cargo;
    // eighteen old variants in a live clone's coverage profile, and in its debug profile, built today
    for (i, d) in (10..28).enumerate() {
        put(
            k,
            &k.join(format!("live-clone/cover-gate/deps/liba-h{i}.rlib")),
            d,
        );
    }
    for i in 0..18 {
        put(
            k,
            &k.join(format!("live-clone/debug/deps/libb-h{i}.rlib")),
            0,
        );
    }
    let all = super::Budget {
        need: u64::MAX,
        idle: SystemTime::now() - Duration::from_secs(DAY),
    };
    let got = names(&plan(&c, SystemTime::now(), &[], all), &c);
    // the idle profile whole, none of its variants beside it; the fresh profile kept, its variants past sixteen pruned
    assert!(got.contains(&"live-clone/cover-gate".to_owned()), "{got:?}");
    let inside = got.iter().any(|n| n.starts_with("live-clone/cover-gate/"));
    assert!(!inside, "{got:?}");
    assert_eq!(
        got.iter()
            .filter(|n| n.starts_with("live-clone/debug/deps/"))
            .count(),
        2
    );
}
