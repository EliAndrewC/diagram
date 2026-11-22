//! The clean scratch worktree's removal on a real repository: a clone with one commit on `main`, its scratch worktrees in a fixture
//! `/tmp`, each aged by hand.

use std::time::{Duration, SystemTime};

use super::fixture::{age, git, worktree};
use super::remove_clean;
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

#[test]
fn a_clean_idle_worktree_on_a_ref_goes_and_every_other_stays() {
    let base = TempDir::new("guard-sweep-trees");
    let mut c = Config::from_env(&|_| None, 4242);
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    let wt = |name: &str| worktree(&c.clones, &base.join("tmp").join(name));
    // clean, idle, HEAD on main: goes
    let clean = wt("t1/clean");
    // an untracked probe: git refuses it
    let probe = wt("t2/probe");
    std::fs::write(probe.join("probe.py"), "x").unwrap();
    // a commit no ref holds: kept
    let unique = wt("t3/unique");
    std::fs::write(unique.join("g"), "y").unwrap();
    git(&unique, &["add", "g"]);
    git(&unique, &["commit", "-qm", "two"]);
    // a live process's path under it: kept
    let held = wt("t4/held");
    // a worktree inside the clones directory is a clone's own landing tree, never scratch
    let landing = worktree(&c.clones, &c.clones.join("git-clone-land"));
    let admin = c.clones.join("git-clone/.git/worktrees");
    for t in [&clean, &probe, &unique, &held, &landing, &admin] {
        age(t, 9);
    }
    // touched lately: kept
    let fresh = wt("t5/fresh");
    let cutoff = SystemTime::now() - Duration::from_secs(86_400);
    let gone = remove_clean(&c, cutoff, &[held.join("x.log")]);
    assert_eq!(gone, [clean.clone()]);
    assert!(!clean.exists());
    for kept in [&probe, &unique, &held, &landing, &fresh] {
        assert!(kept.join("f").exists(), "{}", kept.display());
    }
}
