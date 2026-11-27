//! The pre-warm of a pool tree (feature 451 T316): the test builds of the crates the commits since a handout moved, asked as a real
//! run asks them; ended by a real run in its tree and starting nothing while no slot is spare, each only once the build in flight
//! is done - a build is never cut (feature 451 T336) - never in the slots' queue, off at `L7R_PREWARM=0`, one a tree, and exit 0
//! whatever cargo said.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, Instant};

use super::alone::{fixture, lane_world, put, since as slot_lines};
use super::lint::{both_held, lint, passes_of, SMALL};
use super::phases::phases;
use super::runlock::{me, stage};
use super::slot::quick;
use super::{answer, calls, kept_crates, world_with, World};
use crate::checks::scratch;
use crate::rustc::kept::alone::DIR;
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

/// Is the one slot under `dir` let go? Asked of a taker that waits, a minute at most: a slot just let go can read held for a moment, a
/// child another test's thread is starting holding a copy of its open file until its exec (`slot.rs`) - so a bare `spare` straight
/// after a pre-warm failed once inside a batch gate's coverage run (451 T424), where a hold never let go still fails here.
fn let_go(dir: &Path) -> bool {
    let slots = Slots {
        ceiling: Duration::from_secs(60),
        ..quick(dir, 1)
    };
    take(&slots, "a later run\n", &mut |_| {}).hold.is_some()
}

/// A fake cargo that stays in a build for as long as `slow` lies beside it - for 30 s at most, so a test that fails before it
/// removes the file ends red instead of holding the suite (it held a batch's checks for 9 minutes on 2026-11-26).
const SLOW: &str =
    "i=0\n[ \"$1\" = test ] && while [ -f \"$(dirname \"$0\")/slow\" ] && [ $i -lt 600 ]; do sleep 0.05; i=$((i+1)); done\nexit 0";

/// `SLOW`'s `slow` file, laid beside it and removed when this drops - by the test where its build should end, or by the unwind of an
/// assertion failed inside a `std::thread::scope`, which drops the scope's locals before the scope joins the pre-warm run. Laid
/// inside the scope's closure, so a red test frees the stand-in within one poll: the old shape, `slow` removed by a line after the
/// assertions, left the joined run waiting on each build's 600 polls (69.9 s for one red at load 17, 451 T454).
struct Slow(PathBuf);

impl Slow {
    fn lay(world: &World) -> Slow {
        let file = world.target.join("slow");
        std::fs::write(&file, "").unwrap();
        Slow(file)
    }
}

impl Drop for Slow {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.0);
    }
}

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
    // one phase line a build - the test build's, then each lint pass's (451 T411) - its step and crate named: never a `build`,
    // which the readers book as the task's compile
    let lines = phases(&root);
    assert_eq!(lines.len(), 3, "{lines:?}");
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
    let done = std::thread::scope(|s| {
        let slow = Slow::lay(&world);
        let going = s.spawn(|| run(&world, &since(&from), &knobs(60_000)));
        // cargo is in the first crate's build when a run of the checks joins the tree's record: the build is not cut (a rustc
        // killed mid-write leaves a session no later build links from, feature 451 T336)
        until_calls(&world, 1);
        stage(&world.target, 4242, me().start);
        still_building(&root);
        drop(slow);
        going.join().unwrap()
    });
    assert_eq!(done.code, 0);
    let said = &done.stdout;
    let after = " s of it finishing after a run started, no slot was spare or the ceiling passed)\nprewarm: a run of the checks started in this tree and has the build from here - 1 crate(s) left to it, and 4 lint pass(es) with them\n";
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
    let done = std::thread::scope(|s| {
        let slow = Slow::lay(&world);
        let going = s.spawn(|| run(&world, &since(&from), &knobs(60_000)));
        until_calls(&world, 1);
        // it holds one slot, signed as a pre-warm, with the other spare
        let signed = std::fs::read_to_string(slots.join("slot-0")).unwrap();
        assert!(
            signed.contains("pre-warm): cargo test --no-run"),
            "{signed}"
        );
        // a real compile takes the last slot: the build in flight goes on, its slot held, and ends as cargo ends it
        let real = take(&world.slots, "a real run\n", &mut |_| {});
        // (it may wait a moment: the pre-warm's own look for a spare slot holds the slot's lock while it looks)
        assert!(real.hold.is_some());
        still_building(&root);
        assert!(!spare(&world.slots));
        drop(slow);
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
    // each crate's test build, then its two lint passes
    assert_eq!(codes(&root), [0; 6]);
}

#[test]
fn the_ceiling_passing_mid_build_ends_it_after_that_build() {
    let (root, from) = moved_tree("a");
    let world = world_with(&root, SLOW);
    let done = std::thread::scope(|s| {
        let slow = Slow::lay(&world);
        let going = s.spawn(|| run(&world, &since(&from), &knobs(50)));
        until_calls(&world, 1);
        still_building(&root);
        drop(slow);
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
    assert!(builds(&world).is_empty() && let_go(&slots));
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
    // and each crate's first lint pass, red, its last (451 T411)
    assert_eq!(codes(&root), [1, 1, 1, 1]);
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

/// `fixture`'s crates committed, then `a`'s code edited and committed: the first commit comes back, as a handout names it.
fn handed_out(root: &Path) -> String {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", "one"]);
    let since = git(root, &["rev-parse", "HEAD"]);
    put(root, "rust/a/src/lib.rs", "pub const A: u8 = 1;\n");
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", "two"]);
    since
}

/// The cargo calls of a world's fake cargo but its `--version`, which a key reads.
fn asked(world: &World) -> Vec<String> {
    let mut all = calls(world);
    all.retain(|c| c != "--version");
    all
}

/// The keys kept under a world's target directory, by name.
fn keys(world: &World) -> Vec<String> {
    let mut names: Vec<String> = std::fs::read_dir(world.target.join(DIR))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    names.sort();
    names
}

/// A builder's first test run of `a`: the telling and lane of its binary key's build (its run's own `cargo test` after it left out).
fn first_test(world: &World, root: &Path) -> Vec<String> {
    let before = phases(root).len();
    assert_eq!(answer(world, "test", &["rust/a".to_owned()], false).code, 0);
    slot_lines(root, before)[..2].to_vec()
}

/// A fake cargo whose test builds fail while `fail-test` lies beside it, and whose clippy calls fail while `fail-clippy` does.
const FAILS: &str = "[ -f \"$(dirname \"$0\")/fail-$1\" ] && exit 101\nexit 0";

#[test]
fn the_pre_warm_keeps_the_keys_a_builders_first_test_build_and_lint_are_told_alone_by() {
    let (root, _) = fixture();
    let from = handed_out(&root);
    let dir = scratch("prewarm-keys");
    let world = lane_world(&root, "exit 0", &dir);
    let done = run(&world, &since(&from), &knobs(60_000));
    let warmed = asked(&world);
    // with both wide slots held, the builder's first test build takes the lane (451 T367) and so does each pass of its first
    // lint (451 T411)
    let _held = both_held(&dir);
    assert_eq!(first_test(&world, &root), SMALL);
    assert_eq!(lint(&world, &root, "one"), (0, passes_of(2, SMALL)));
    // the pre-warm asked the test build, then each pass of the lint in the words the lint asks
    let m = root.join("rust/a/Cargo.toml").display().to_string();
    let lint_of = |pass: &str| format!("clippy --quiet {pass} --manifest-path {m} -- -D warnings");
    assert_eq!(
        warmed,
        [
            format!("test --no-run --quiet --manifest-path {m}"),
            lint_of("--all-targets"),
            lint_of("--all-targets --all-features")
        ]
    );
    let said = &done.stdout;
    assert!(
        said.contains("prewarm: rust/a - its test build is warm ("),
        "{said}"
    );
    assert!(
        said.contains("prewarm: rust/a - its lint pass --all-targets --all-features is warm ("),
        "{said}"
    );
    assert_eq!(codes(&root), [0, 0, 0]);
}

#[test]
fn a_red_build_or_pass_keeps_no_key_and_a_pre_warm_told_alone_leaves_its_key_as_it_was() {
    let (root, _) = fixture();
    let from = handed_out(&root);
    let dir = scratch("prewarm-red");
    let world = lane_world(&root, FAILS, &dir);
    for red in ["fail-test", "fail-clippy"] {
        std::fs::write(world.target.join(red), "").unwrap();
    }
    let done = run(&world, &since(&from), &knobs(60_000));
    let said = &done.stdout;
    let stopped = "prewarm: rust/a - cargo clippy --all-targets exited 101; its later passes left to the builder's own lint, which says why\n";
    assert!(said.contains(stopped), "{said}");
    // a red pass is the lint's last: no later pass is asked, and nothing is kept, nor left beside a key
    assert_eq!(asked(&world).len(), 2);
    assert!(keys(&world).is_empty(), "{:?}", keys(&world));
    for red in ["fail-test", "fail-clippy"] {
        std::fs::remove_file(world.target.join(red)).unwrap();
    }
    run(&world, &since(&from), &knobs(60_000));
    let all = [
        "rust_a-lint--all-targets",
        "rust_a-lint--all-targets--all-features",
        "rust_a-test",
    ];
    assert_eq!(keys(&world), all);
    // a pre-warm told alone builds, and leaves each key as it was: its time is the build's that kept it
    let test_key = world.target.join(DIR).join("rust_a-test");
    let when = std::fs::metadata(&test_key).unwrap().modified().unwrap();
    run(&world, &since(&from), &knobs(60_000));
    assert_eq!(asked(&world).len(), 8);
    assert_eq!(
        std::fs::metadata(&test_key).unwrap().modified().unwrap(),
        when
    );
    assert_eq!(keys(&world), all);
}

#[test]
fn a_crate_that_names_itself_is_warmed_at_all_three_passes_and_the_lint_is_off_at_its_knob() {
    let (root, _) = fixture();
    let itself = format!(
        "{}\n[dev-dependencies]\na = {{ path = \".\", features = [\"kit\"] }}\n",
        super::alone::A_BUILDS_FROM_B
    );
    put(&root, "rust/a/Cargo.toml", &itself);
    let from = handed_out(&root);
    // no lane: each pass is asked, and no key is kept
    let mut world = world_with(&root, "exit 0");
    run(&world, &since(&from), &knobs(60_000));
    let passes: Vec<String> = asked(&world)
        .iter()
        .map(|c| {
            c.split(" --manifest-path")
                .next()
                .unwrap_or_default()
                .to_owned()
        })
        .collect();
    assert_eq!(
        passes[1..],
        [
            "clippy --quiet --all-targets",
            "clippy --quiet --all-targets --all-features",
            "clippy --quiet --lib"
        ]
    );
    assert!(!world.target.join(DIR).exists());
    // `L7R_PREWARM_LINT=0`: the test builds alone
    world.root = l7r_shared::env::Rooted::with(&*root, &[("L7R_PREWARM_LINT", "0")]);
    let off = run(&world, &since(&from), &knobs(60_000));
    assert_eq!(asked(&world).len(), 5);
    assert!(!off.stdout.contains("lint pass"), "{}", off.stdout);
}
