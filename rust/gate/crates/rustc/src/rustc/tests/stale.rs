//! A test build whose link fails on a mixed incremental session (feature 451 T336): the named crates' incremental directories
//! and the named builds' fingerprints are dropped under cargo's lock and the build asked once more, a `link-heal` phase line
//! written; any other failure, and a link that names nothing of the tree, come back as they are; never a third build.

use std::path::Path;

use super::phases::phases;
use super::{calls, two_crates, world_with};
use crate::rustc::stale::{healed, LOCK_S, STEP};
use crate::rustc::{stepped, Ran, Told};

fn ran(code: i32, stderr: &str) -> Ran {
    Ran {
        code,
        stdout: String::new(),
        stderr: stderr.to_owned(),
    }
}

/// A build directory with one crate's two incremental directories, a dependency's, another crate's, and each build's fingerprint.
pub(super) fn cache(profile: &Path) {
    for dir in [
        "incremental/k-aaa/s-1-working",
        "incremental/k-bbb/s-2-done",
        "incremental/dep-ccc/s-3-done",
        "incremental/other-ddd/s-4-done",
        ".fingerprint/k-0123456789abcdef",
        ".fingerprint/dep-name-fedcba9876543210",
        ".fingerprint/other-1111111111111111",
        "deps",
    ] {
        std::fs::create_dir_all(profile.join(dir)).unwrap();
    }
}

/// The linker's words: a unit of the crate by its path, and a unit of a dependency as a member of its rlib.
pub(super) fn link_error(profile: &Path) -> String {
    let deps = profile.join("deps");
    format!(
        "error: linking with `cc` failed: exit status: 1\n  = note: rust-lld: error: undefined hidden symbol: anon.1.llvm.2\n          >>> referenced by u1\n          >>>               {0}/k-0123456789abcdef.u1.rcgu.o:(k::f)\n          >>> referenced by u2\n          >>>               {0}/libdep-fedcba9876543210.rlib(dep-fedcba9876543210.u2.rcgu.o):(dep::g)\n",
        deps.display()
    )
}

/// A fake cargo whose first `n` test builds fail as the linker does, in the words of `link-error` beside it.
fn failing(n: usize) -> String {
    format!("d=$(dirname \"$0\")\nif [ \"$1\" = test ] && [ \"$(grep -c '^test' \"$d/calls\")\" -le {n} ]; then cat \"$d/link-error\" >&2; exit 101; fi\nexit 0")
}

fn heals(root: &Path) -> Vec<i64> {
    phases(root)
        .iter()
        .filter(|l| l["step"] == STEP)
        .map(|l| l["code"].as_i64().unwrap())
        .collect()
}

#[test]
fn a_link_on_a_mixed_session_drops_the_named_crates_sessions_and_builds_once_more() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, &failing(1));
    let profile = world.target.join("debug");
    cache(&profile);
    std::fs::write(world.target.join("link-error"), link_error(&profile)).unwrap();
    let done = stepped(&world, "test", &a, false, (false, &Told::wide()), None);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let builds = |w: &crate::rustc::World| {
        calls(w)
            .iter()
            .filter(|c| c.starts_with("test --no-run"))
            .count()
    };
    assert_eq!(builds(&world), 2);
    // every incremental directory of each named crate and each named build's fingerprint are gone; every other stands
    let left = |p: &str| profile.join(p).exists();
    assert!(!left("incremental/k-aaa") && !left("incremental/k-bbb"));
    assert!(!left("incremental/dep-ccc"));
    assert!(!left(".fingerprint/k-0123456789abcdef"));
    assert!(!left(".fingerprint/dep-name-fedcba9876543210"));
    assert!(left("incremental/other-ddd") && left(".fingerprint/other-1111111111111111"));
    // the heal is one phase line of its own, with the second build's code, inside the build's
    assert_eq!(heals(&root), [0]);
    // what it says of a heal that linked (said on the gate's stderr by `built`; the run that follows keeps no build's words)
    cache(&profile);
    let first = ran(101, &link_error(&profile));
    let linked = healed(&world, &a, first, LOCK_S, &mut || ran(0, "")).stderr;
    let dropped = "l7r-gate rust: the link failed on a mixed incremental session (rust-lld: undefined hidden symbol) - a build of this crate was killed while rustc compiled it (feature 451 T336); dropped incremental/dep-ccc, incremental/k-aaa, incremental/k-bbb, .fingerprint/dep-name-fedcba9876543210, .fingerprint/k-0123456789abcdef and built again: linked\n";
    assert_eq!(linked, dropped);
    assert_eq!(heals(&root), [0, 0]);
}

#[test]
fn a_second_failed_link_is_the_builds_answer_and_no_third_build_is_asked() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, &failing(9));
    let profile = world.target.join("debug");
    cache(&profile);
    std::fs::write(world.target.join("link-error"), link_error(&profile)).unwrap();
    let done = stepped(&world, "test", &a, false, (false, &Told::wide()), None);
    assert_eq!(done.code, 101);
    assert_eq!(calls(&world).len(), 2, "{:?}", calls(&world));
    let twice = " and built again: that build failed too, in cargo's words below\nerror: linking with `cc` failed";
    assert!(done.stderr.contains(twice), "{}", done.stderr);
    assert_eq!(heals(&root), [101]);
}

#[test]
fn any_other_result_and_a_link_that_names_nothing_of_the_tree_come_back_unbuilt() {
    let (root, a, _) = two_crates();
    let world = world_with(&root, "exit 0");
    let profile = world.target.join("debug");
    cache(&profile);
    let mut never = || -> Ran { panic!("built again") };
    // a green build, and a red one that is not this
    assert_eq!(healed(&world, &a, ran(0, ""), LOCK_S, &mut never).code, 0);
    let plain = healed(
        &world,
        &a,
        ran(101, "error[E0425]: no\n"),
        LOCK_S,
        &mut never,
    );
    assert_eq!(plain.stderr, "error[E0425]: no\n");
    // the linker's words with no unit named, with a unit of another tree's target directory, and with a crate that has a
    // fingerprint and no incremental directory (the fingerprint alone dropped would build from the same session): nothing
    // dropped, the repair named
    let bare = link_error(&profile)
        .replace("/k-0123", "/lone-0123")
        .replace("dep-fedc", "lone-fedc");
    std::fs::create_dir_all(profile.join(".fingerprint/lone-0123456789abcdef")).unwrap();
    for words in [
        "rust-lld: error: undefined hidden symbol: x\n".to_owned(),
        link_error(Path::new("/elsewhere/target/debug")),
        bare,
    ] {
        let said = healed(&world, &a, ran(101, &words), LOCK_S, &mut never);
        assert_eq!(said.code, 101);
        assert!(said.stderr.contains("; nothing was dropped (the linker names no crate with an incremental directory under this tree's target directory, or another cargo held the build directory for 120 s). The repair: remove the crate's directories under <target>/debug/incremental/ (<crate>-*) and run again. The link's own words:\n"), "{}", said.stderr);
        assert!(said.stderr.ends_with(&words));
        assert!(profile.join("incremental/k-bbb").exists());
        assert!(profile.join(".fingerprint/lone-0123456789abcdef").exists());
    }
    // another cargo holds the build directory: nothing is dropped under it; an overridden target directory is the one read
    let mut world = world;
    world.target_override = Some(world.target.display().to_string());
    let held = l7r_shared::tool::flock_within(&profile.join(".cargo-lock"), 30.0).unwrap();
    assert!(held.is_some());
    let waited = healed(&world, &a, ran(101, &link_error(&profile)), 0.0, &mut never);
    let said = waited.stderr;
    assert!(
        said.contains("; nothing was dropped (") && said.contains(" for 0 s)"),
        "{said}"
    );
    assert!(profile.join("incremental/k-bbb").exists());
    assert!(heals(&root).is_empty());
}
