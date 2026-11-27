//! The start through the lane tree's launcher (feature 461 T51): a stale `l7r-gate` is built before the detached spawn, so a build
//! longer than the start's wait never reads as "holds no lock"; a build that fails starts nothing and says why.

use std::path::{Path, PathBuf};

use serde_json::json;
use std::time::Duration;

use l7r_gate_core::ci::fixtures::repo;

use super::{holder, start, stop};

/// The start's wait in these tests (461 T58): 0.3 s was red 2 of 30 whole-crate runs ten at once (2026-11-27), and with the fake's
/// spawn slowed 0.5 s, 10 of 10. Measured 2026-11-27 (the lane test binary 6x10 at once, load 31 to 86 on 22 cores, the start's
/// wait timed): a spawn to the lock took 0.066 s at the median and 0.749 s at the most of 419 starts that came up, so 3.0 s holds
/// that worst plus the fake's 0.5 s near 2.4 times; a lock seen ends the wait at once, so it costs a green run nothing.
const WAIT_S: f64 = 3.0;

/// A stand-in for `scripts/gates/l7r-gate.sh`: with `L7R_GATE_PRINT_FRESH` it "builds" - 3.5 s where `<it>.stale` exists, a line
/// in `<it>.builds` - and prints its path, or fails as cargo does where `<it>.fail` exists; without it, it runs as the runner (the
/// same build first where still stale), taking the lock and holding it after a slow spawn of 0.5 s, as a loaded machine's (see [`WAIT_S`]).
/// Every start of it gets [`WAIT_S`], which the build outlasts.
fn fake_launcher(dir: &Path) -> PathBuf {
    let gates = dir.join("gates");
    std::fs::create_dir_all(&gates).unwrap();
    let exe = gates.join("l7r-gate.sh");
    l7r_gate_core::write_executable(
        &exe,
        "#!/bin/sh\n\
         if [ -n \"$L7R_GATE_PRINT_FRESH\" ]; then\n\
           [ -e \"$0.fail\" ] && { echo 'error[E0425]: cannot find value `x`' >&2; exit 1; }\n\
           [ -e \"$0.stale\" ] && { sleep 3.5; rm -f \"$0.stale\"; echo built >> \"$0.builds\"; }\n\
           echo \"$0\"; exit 0\n\
         fi\n\
         [ -e \"$0.stale\" ] && { sleep 3.5; rm -f \"$0.stale\"; }\n\
         sleep 0.5\n\
         exec 9<>\"$3/l7r-lane/lane.lock\"\nflock -w 1 9 || exit 0\necho $$ > \"$3/l7r-lane/lane.lock\"\nexec sleep 30\n",
    );
    exe
}

/// The runner a start may have left, stopped whatever the start said (on the old code it comes up after the start gave up).
fn reap(common: &Path) {
    for _ in 0..150 {
        if holder(common).is_some() {
            break;
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    let _ = stop(common, true, 5.0);
}

#[test]
fn a_stale_launcher_is_built_before_the_spawn_so_a_long_build_is_no_failed_start() {
    let dir = repo("lane-start-build");
    let common = dir.path().join(".git");
    let exe = fake_launcher(dir.path());
    std::fs::write(exe.with_extension("sh.stale"), "").unwrap();
    // the build (3.5 s) outlasts the wait (WAIT_S), as the lane tree's rebuild outlasts START_WAIT_S
    let started = start(&common, &exe, "setsid", WAIT_S);
    let pid = holder(&common);
    reap(&common);
    assert_eq!(started.stderr, "");
    assert_eq!(started.code, 0);
    assert_eq!(
        started.stdout,
        format!("lane: the runner started (pid {})\n", pid.unwrap())
    );
    assert_eq!(
        std::fs::read_to_string(exe.with_extension("sh.builds")).unwrap(),
        "built\n"
    );
}

#[test]
fn a_build_that_fails_or_a_launcher_that_cannot_run_starts_nothing_and_says_why() {
    let dir = repo("lane-start-build-fails");
    let common = dir.path().join(".git");
    let exe = fake_launcher(dir.path());
    std::fs::write(exe.with_extension("sh.fail"), "").unwrap();
    let failed = start(&common, &exe, "setsid", WAIT_S);
    reap(&common);
    assert_eq!(failed.code, 1);
    let said = failed.stderr.as_str();
    assert!(said.contains("could not be built (exit 1)"));
    assert!(said.contains("error[E0425]: cannot find value `x`"));
    assert!(!super::lock_path(&common).exists());
    let gone = dir.path().join("nowhere/l7r-gate.sh");
    let missing = start(&common, &gone, "setsid", WAIT_S);
    assert_eq!(missing.code, 1);
    let named = format!("lane: {}: ", gone.display());
    assert!(missing.stderr.starts_with(&named));
    assert!(!super::lock_path(&common).exists());
}

/// 461 T55's stand-in for the lane tree's `scripts/gates/l7r-gate.sh`, committed in the world: like cargo, it fails on a conflict's
/// markers in a `rust/` file - in both of its modes, as the real launcher builds where stale whether printing or running - else prints
/// its path (`L7R_GATE_PRINT_FRESH`) or runs as the runner, taking the lock and holding it.
const BUILDS_FROM_RUST: &str = "#!/bin/sh\n\
    t=\"$(cd \"$(dirname \"$0\")/../..\" && pwd)\"\n\
    grep -rqs '^<<<<<<<' \"$t/rust\" && { echo 'error: this file contains an unclosed delimiter' >&2; exit 1; }\n\
    [ -n \"$L7R_GATE_PRINT_FRESH\" ] && { echo \"$0\"; exit 0; }\n\
    exec 9<>\"$3/l7r-lane/lane.lock\"\nflock -w 1 9 || exit 0\necho $$ > \"$3/l7r-lane/lane.lock\"\nexec sleep 30\n";

/// A clone, its bare `origin`, and the lane's tree in the pool's registry at `origin/main`, whose `rust/x.rs` a hand-in's commit
/// (the returned sha) changed another way: picked onto the tree it stops in conflict, as a stopped carry leaves it.
struct Stopped {
    _dir: l7r_shared::tempdir::TempDir,
    clone: PathBuf,
    common: PathBuf,
    land: PathBuf,
    theirs: String,
}

fn stopped_world(tag: &str) -> Stopped {
    use l7r_gate_core::ci::fixtures::{git, put, scratch};
    let dir = scratch(tag);
    let (origin, clone) = (dir.path().join("origin.git"), dir.path().join("repo"));
    std::fs::create_dir_all(&clone).unwrap();
    git(
        dir.path(),
        &[
            "init",
            "-q",
            "--bare",
            "-b",
            "main",
            &origin.to_string_lossy(),
        ],
    );
    git(&clone, &["init", "-q", "-b", "main"]);
    git(&clone, &["config", "user.email", "t@t"]);
    git(&clone, &["config", "user.name", "t"]);
    git(
        &clone,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    let script = clone.join("scripts/gates/l7r-gate.sh");
    std::fs::create_dir_all(script.parent().unwrap()).unwrap();
    l7r_gate_core::write_executable(&script, BUILDS_FROM_RUST);
    put(&clone, "rust/x.rs", "base\n");
    git(&clone, &["add", "-A"]);
    git(&clone, &["commit", "-qm", "the world"]);
    let base = git(&clone, &["rev-parse", "HEAD"]);
    put(&clone, "rust/x.rs", "theirs\n");
    git(&clone, &["commit", "-qam", "461 T01: the hand-in"]);
    let theirs = git(&clone, &["rev-parse", "HEAD"]);
    git(&clone, &["update-ref", "refs/l7r/done/461-T01", &theirs]);
    git(&clone, &["reset", "-q", "--hard", &base]);
    put(&clone, "rust/x.rs", "ours\n");
    git(&clone, &["commit", "-qam", "main moved"]);
    git(&clone, &["push", "-q", "origin", "main"]);
    git(&clone, &["fetch", "-q", "origin"]);
    let land = dir.path().join("repo-land");
    git(
        &clone,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &land.to_string_lossy(),
            "origin/main",
        ],
    );
    let common = clone.join(".git");
    let held = l7r_shared::builder_pool::Tree {
        tree: land.clone(),
        feature: String::new(),
        tasks: vec![l7r_shared::builder_pool::LANE.to_owned()],
        since: "2026-11-28T00:00:00Z".to_owned(),
    };
    l7r_shared::builder_pool::write(&common, &[held]).unwrap();
    let w = Stopped {
        _dir: dir,
        clone,
        common,
        land,
        theirs,
    };
    w.pick();
    w
}

impl Stopped {
    /// The hand-in picked onto the lane's tree: it stops in conflict, the pick left in progress.
    fn pick(&self) {
        let done = std::process::Command::new("git")
            .arg("-C")
            .arg(&self.land)
            .args(["cherry-pick", &self.theirs])
            .output()
            .unwrap();
        assert!(!done.status.success());
        assert!(self.picking());
    }

    fn picking(&self) -> bool {
        std::process::Command::new("git")
            .arg("-C")
            .arg(&self.land)
            .args(["rev-parse", "-q", "--verify", "CHERRY_PICK_HEAD"])
            .output()
            .unwrap()
            .status
            .success()
    }

    /// The lane's log as a runner whose carry stopped leaves it: the batch, its stopped `carry`, the runner's `stop` (no batch).
    fn stopped_carry(&self) {
        let lines = [
            ("batch", json!({"batch": "461-1", "changes": [self.theirs]})),
            (
                "carry",
                json!({"batch": "461-1", "code": 2, "conflict": ["rust/x.rs"]}),
            ),
            (
                "stop",
                json!({"pid": 1, "why": "error: lane: batch 461-1: the carry stopped"}),
            ),
        ];
        for (event, fields) in lines {
            crate::log::append(&self.common, "2026-11-28T01:00:00Z", event, &fields).unwrap();
        }
    }

    fn start(&self) -> l7r_gate_core::Reply {
        let exe = super::runner_exe(&self.common, Path::new("/nowhere/l7r-gate"));
        assert_eq!(exe, self.land.join("scripts/gates/l7r-gate.sh"));
        start(&self.common, &exe, "setsid", WAIT_S)
    }
}

#[test]
fn a_stopped_carry_s_conflict_in_the_lane_s_tree_is_reset_away_before_the_build_so_the_runner_starts_to_resume_it(
) {
    let w = stopped_world("lane-start-stopped-carry");
    w.stopped_carry();
    let started = w.start();
    let pid = holder(&w.common);
    reap(&w.common);
    assert_eq!(started.stderr, "");
    assert_eq!(started.code, 0);
    assert_eq!(
        started.stdout,
        format!(
            "lane: the lane's tree {} held batch 461-1's stopped carry (a cherry-pick in progress): brought to origin/main before the build, as the runner's resume brings it\nlane: the runner started (pid {})\n",
            w.land.display(),
            pid.unwrap()
        )
    );
    assert!(!w.picking());
    assert_eq!(
        std::fs::read_to_string(w.land.join("rust/x.rs")).unwrap(),
        "ours\n"
    );
}

#[test]
fn a_pick_in_progress_with_no_stopped_carry_open_is_left_as_it_is_and_the_build_says_why() {
    let w = stopped_world("lane-start-pick-not-the-lane-s");
    // a batch whose carry ended 0 is no stopped carry: the pick in the tree is not the lane's, and the start leaves it
    crate::log::append(
        &w.common,
        "t",
        "batch",
        &json!({"batch": "461-1", "changes": [w.theirs]}),
    )
    .unwrap();
    crate::log::append(
        &w.common,
        "t",
        "carry",
        &json!({"batch": "461-1", "code": 0, "conflict": []}),
    )
    .unwrap();
    let left = w.start();
    reap(&w.common);
    assert_eq!(left.code, 1);
    assert!(left.stderr.contains("could not be built (exit 1)"));
    assert!(left.stderr.contains("unclosed delimiter"));
    assert!(w.picking());
}

#[test]
fn a_reset_that_fails_starts_nothing_and_says_both_why() {
    let w = stopped_world("lane-start-reset-fails");
    w.stopped_carry();
    l7r_gate_core::ci::fixtures::git(
        &w.clone,
        &["remote", "set-url", "origin", "/nowhere/origin.git"],
    );
    let failed = w.start();
    reap(&w.common);
    assert_eq!(failed.code, 1);
    assert!(failed
        .stderr
        .starts_with("builder-tree lane: the lane's tree "));
    assert!(failed
        .stderr
        .contains("could not be brought to origin/main"));
    assert!(failed.stderr.contains("could not be built (exit 1)"));
    assert!(w.picking());
}
