//! The pre-warm of a pool tree (feature 451 T316): the test builds of the crates the commits since a handout moved, asked as a real
//! run asks them; ended by a real run in its tree and starting nothing while no slot is spare, each only once the build in flight
//! is done - a build is never cut (feature 451 T336) - never in the slots' queue, off at `L7R_PREWARM=0`, one a tree, and exit 0
//! whatever cargo said.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, Instant};

use super::phases::phases;
use super::runlock::{me, stage};
use super::{calls, kept_crates, world_with, World};
use crate::checks::scratch;
use crate::rustc::prewarm::{run, Knobs, STEP};
use crate::rustc::runlock::RECORD;
use crate::rustc::slot::{spare, take, Slots};
use l7r_shared::tempdir::TempDir;

fn git(root: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    assert!(out.status.success(), "git {args:?}");
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

/// Two crates in a repository, `b` building on `a`, committed; then `edited`'s library changed and committed. The first commit comes
/// back: what a handout would name as `--since`.
fn moved_tree(edited: &str) -> (TempDir, String) {
    let (root, _, b) = kept_crates();
    std::fs::write(&b, "[package]\n[dependencies]\na = { path = \"../a\" }\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "one"]);
    let since = git(&root, &["rev-parse", "HEAD"]);
    std::fs::write(root.join(format!("rust/{edited}/src/lib.rs")), "//! y\n").unwrap();
    std::fs::write(root.join("notes.md"), "a note\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "two"]);
    (root, since)
}

fn knobs(ceiling_ms: u64) -> Knobs {
    Knobs {
        poll: Duration::from_millis(10),
        ceiling: Duration::from_millis(ceiling_ms),
        proc_root: PathBuf::from("/proc"),
        lock_s: 30.0,
    }
}

fn since(commit: &str) -> Vec<String> {
    vec!["--since".to_owned(), commit.to_owned()]
}

/// The builds asked of the fake cargo (its `--version`, which a key reads, left out).
fn builds(world: &World) -> Vec<String> {
    let all = calls(world);
    all.into_iter().filter(|c| c.starts_with("test")).collect()
}

/// The fake cargo's calls so far, waited for until there are `n` (a bound no load reaches).
fn until_calls(world: &World, n: usize) {
    let began = Instant::now();
    while builds(world).len() < n {
        assert!(began.elapsed().as_secs() < 60);
        std::thread::sleep(Duration::from_millis(5));
    }
}

/// The codes of the tree's `prewarm` phase lines.
fn codes(root: &Path) -> Vec<i64> {
    phases(root)
        .iter()
        .filter(|l| l["step"] == STEP)
        .map(|l| l["code"].as_i64().unwrap())
        .collect()
}

/// A fake cargo that stays in a build for as long as `slow` lies beside it.
const SLOW: &str =
    "[ \"$1\" = test ] && while [ -f \"$(dirname \"$0\")/slow\" ]; do sleep 0.05; done\nexit 0";

#[test]
fn the_moved_crates_test_builds_are_asked_as_a_real_run_asks_them_a_crate_before_its_dependents() {
    // only `b` moved: `a`, which builds from nothing of it, is left alone
    let (root, from) = moved_tree("b");
    let world = world_with(&root, "exit 0");
    let done = run(&world, &since(&from), &knobs(60_000));
    assert_eq!(done.code, 0);
    assert!(
        done.stdout.starts_with(&format!(
            "prewarm: 1 crate(s) whose build moved since {from}\n"
        )),
        "{}",
        done.stdout
    );
    assert!(done
        .stdout
        .contains("prewarm: rust/b - its test build is warm ("));
    let b = root.join("rust/b/Cargo.toml");
    let asked = format!("test --no-run --quiet --manifest-path {}", b.display());
    assert_eq!(builds(&world), [asked.clone()]);
    // one phase line a build, its step and crate named: never a `build`, which the readers book as the task's compile
    let lines = phases(&root);
    assert_eq!(lines.len(), 1, "{lines:?}");
    assert_eq!(
        (&lines[0]["step"], &lines[0]["crates"][0], &lines[0]["code"]),
        (&STEP.into(), &"rust/b".into(), &0.into())
    );
    // `a` moved: `b` builds from it, so both, `a` first
    let (root, from) = moved_tree("a");
    let world = world_with(&root, "exit 0");
    let done = run(&world, &since(&from), &knobs(60_000));
    let a = root.join("rust/a/Cargo.toml");
    assert!(done.stdout.starts_with("prewarm: 2 crate(s)"));
    assert_eq!(
        builds(&world),
        [
            format!("test --no-run --quiet --manifest-path {}", a.display()),
            format!(
                "test --no-run --quiet --manifest-path {}",
                root.join("rust/b/Cargo.toml").display()
            )
        ]
    );
}

/// The pre-warm's build in flight has gone on for a while with nothing written of it: no phase line, so no cut.
fn still_building(root: &Path) {
    std::thread::sleep(Duration::from_millis(150));
    assert!(codes(root).is_empty(), "{:?}", codes(root));
}

#[test]
fn a_real_run_in_its_tree_ends_it_once_the_build_in_flight_is_done() {
    let (root, from) = moved_tree("a");
    let world = world_with(&root, SLOW);
    std::fs::write(world.target.join("slow"), "").unwrap();
    let done = std::thread::scope(|s| {
        let going = s.spawn(|| run(&world, &since(&from), &knobs(600_000)));
        // cargo is in the first crate's build when a run of the checks joins the tree's record: the build is not cut (a rustc
        // killed mid-write leaves a session no later build links from, feature 451 T336)
        until_calls(&world, 1);
        stage(&world.target, 4242, me().start);
        still_building(&root);
        std::fs::remove_file(world.target.join("slow")).unwrap();
        going.join().unwrap()
    });
    assert_eq!(done.code, 0);
    let said = &done.stdout;
    let after = " s of it finishing after a run started, no slot was spare or the ceiling passed)\nprewarm: a run of the checks started in this tree and has the build from here - 1 crate(s) left to it\n";
    assert!(
        said.contains("prewarm: rust/a - its test build is warm ("),
        "{said}"
    );
    assert!(said.contains(after), "{said}");
    // the build ended as cargo ended it, and the second crate was never asked
    assert_eq!(builds(&world).len(), 1);
    assert_eq!(codes(&root), [0]);
    // and one started while a run is at work asks cargo nothing
    let again = run(&world, &since(&from), &knobs(600_000));
    let said = again.stdout;
    assert!(said.contains("2 crate(s) left to it"), "{said}");
    assert_eq!(builds(&world).len(), 1);
    std::fs::remove_file(world.target.join(RECORD)).unwrap();
}

#[test]
fn it_starts_a_crate_only_while_a_slot_is_spare_and_never_cuts_the_one_in_flight() {
    let (root, from) = moved_tree("a");
    let mut world = world_with(&root, SLOW);
    let slots = scratch("prewarm-slots");
    world.slots = Slots::at(slots.to_path_buf(), 2);
    std::fs::write(world.target.join("slow"), "").unwrap();
    let done = std::thread::scope(|s| {
        let going = s.spawn(|| run(&world, &since(&from), &knobs(600_000)));
        until_calls(&world, 1);
        // it holds one slot, signed as a pre-warm, with the other spare
        let signed = std::fs::read_to_string(slots.join("slot-0")).unwrap();
        assert!(
            signed.contains("pre-warm): cargo test --no-run"),
            "{signed}"
        );
        // a real compile takes the last slot: the build in flight goes on, its slot held, and ends as cargo ends it
        let real = take(&world.slots, "a real run\n", &mut |_| {});
        assert!(real.hold.is_some() && real.waited.is_none());
        still_building(&root);
        assert!(!spare(&world.slots));
        std::fs::remove_file(world.target.join("slow")).unwrap();
        let began = Instant::now();
        while codes(&root).is_empty() {
            assert!(began.elapsed().as_secs() < 60);
            std::thread::sleep(Duration::from_millis(5));
        }
        // and while that compile lasts the next crate is not asked
        std::thread::sleep(Duration::from_millis(100));
        assert_eq!(builds(&world).len(), 1);
        drop(real);
        going.join().unwrap()
    });
    let said = done.stdout;
    let after = " s of it finishing after a run started, no slot was spare or the ceiling passed)\nprewarm: rust/b - its test build is warm (";
    assert!(
        said.contains(after) && !said.contains("cut short"),
        "{said}"
    );
    assert_eq!(builds(&world).len(), 2);
    assert_eq!(codes(&root), [0, 0]);
}

#[test]
fn the_ceiling_passing_mid_build_ends_it_after_that_build() {
    let (root, from) = moved_tree("a");
    let world = world_with(&root, SLOW);
    std::fs::write(world.target.join("slow"), "").unwrap();
    let done = std::thread::scope(|s| {
        let going = s.spawn(|| run(&world, &since(&from), &knobs(50)));
        until_calls(&world, 1);
        still_building(&root);
        std::fs::remove_file(world.target.join("slow")).unwrap();
        going.join().unwrap()
    });
    let said = done.stdout;
    let stopped =
        "prewarm: stopped at its ceiling of 0 s (L7R_PREWARM_CEILING) - 1 crate(s) not built";
    assert!(
        said.contains("prewarm: rust/a - its test build is warm ("),
        "{said}"
    );
    assert!(said.contains(stopped), "{said}");
    assert_eq!((builds(&world).len(), codes(&root)), (1, vec![0]));
}

#[test]
fn it_never_waits_in_the_slots_queue_and_stops_at_its_ceiling() {
    let (root, from) = moved_tree("b");
    let mut world = world_with(&root, "exit 0");
    let slots = scratch("prewarm-held");
    // one slot on the machine: one is never spare beside the pre-warm's own, so it builds nothing and holds nothing
    world.slots = Slots::at(slots.to_path_buf(), 1);
    let done = run(&world, &since(&from), &knobs(50));
    assert_eq!(done.code, 0);
    let said = done.stdout;
    assert!(
        said.contains(
            "prewarm: stopped at its ceiling of 0 s (L7R_PREWARM_CEILING) - 1 crate(s) not built"
        ),
        "{said}"
    );
    assert!(builds(&world).is_empty() && spare(&world.slots));
    // two, one held by a real compile: the same
    world.slots = Slots::at(slots.to_path_buf(), 2);
    let real = take(&world.slots, "a real run\n", &mut |_| {});
    let held = run(&world, &since(&from), &knobs(50));
    assert!(held.stdout.contains("stopped at its ceiling") && builds(&world).is_empty());
    drop(real);
}

#[test]
fn it_is_off_at_the_knob_one_a_tree_and_a_crate_that_does_not_build_fails_nothing() {
    let (root, from) = moved_tree("a");
    let mut world = world_with(&root, "exit 1");
    assert_eq!(run(&world, &[], &knobs(1000)).code, 2);
    let wrong = run(&world, &["--from".to_owned(), from.clone()], &knobs(1000));
    assert_eq!(
        (wrong.code, wrong.stdout.as_str()),
        (2, "usage: l7r-gate rust prewarm --since <commit>\n")
    );
    // another pre-warm of the tree at work: nothing started
    let one = l7r_shared::tool::flock_within(&world.target.join("prewarm.lock"), 30.0).unwrap();
    assert!(one.is_some());
    let hasty = Knobs {
        lock_s: 0.0,
        ..knobs(1000)
    };
    let second = run(&world, &since(&from), &hasty);
    assert_eq!(
        (second.code, second.stdout.as_str()),
        (
            0,
            "prewarm: another pre-warm of this tree is at work - nothing started\n"
        )
    );
    drop(one);
    // a build that fails is said and the next crate is still built; the exit is 0
    let failed = run(&world, &since(&from), &knobs(60_000));
    assert_eq!(failed.code, 0);
    assert!(failed.stdout.contains("prewarm: rust/a - cargo test --no-run exited 1; left to the builder's own run, which says why\nprewarm: rust/b - cargo test --no-run exited 1"), "{}", failed.stdout);
    assert_eq!(codes(&root), [1, 1]);
    // a cargo that cannot start is the same
    let cargo = std::mem::replace(&mut world.cargo, "/nonexistent/cargo".to_owned());
    let none = run(&world, &since(&from), &knobs(60_000));
    assert!(none
        .stdout
        .contains("rust/a - cargo test --no-run exited 127"));
    world.cargo = cargo;
    // off: cargo asked nothing more
    let before = builds(&world).len();
    world.root = l7r_shared::env::Rooted::with(
        &*root,
        &[("L7R_PREWARM", "0"), ("L7R_PREWARM_CEILING", "7")],
    );
    let off = run(&world, &since(&from), &knobs(60_000));
    assert_eq!(
        (off.code, off.stdout.as_str()),
        (0, "prewarm: off (L7R_PREWARM=0)\n")
    );
    assert_eq!(builds(&world).len(), before);
    // the ceiling is a knob in seconds, fifteen minutes where unset
    assert_eq!(Knobs::of(&world).ceiling, Duration::from_secs(7));
    world.root = l7r_shared::env::Rooted::with(&*root, &[]);
    assert_eq!(Knobs::of(&world).ceiling, Duration::from_secs(900));
    // the command line: no run lock taken, a usage error its own
    let usage = crate::rustc::cli(&[STEP.to_owned()]);
    assert_eq!(usage.code, 2);
}
