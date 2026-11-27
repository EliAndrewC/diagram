//! THE LANE'S TREE (feature 461 T13, plan D1): `<clone>-land` adopted under the reserved holder `lane`, which no handout takes and the
//! pool's cap does not count, and brought to `origin/main` at a batch's start by land-alone's step 4 rule.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{commit, git, put};

use super::{env, pool_of, words, world};
use crate::builder_tree::run;

fn worktree(root: &Path, tree: &Path) {
    git(
        root,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &tree.to_string_lossy(),
            "HEAD",
        ],
    );
}

fn picking(tree: &Path) -> bool {
    crate::git(tree, &["rev-parse", "-q", "--verify", "CHERRY_PICK_HEAD"]).0 == Some(0)
}

fn registry(root: &Path) -> String {
    std::fs::read_to_string(root.join(".git/builder-pool.json")).unwrap_or_default()
}

#[test]
fn the_lane_s_tree_is_adopted_under_a_holder_no_handout_takes_and_the_cap_does_not_count() {
    let (dir, root) = world("pool-lane");
    let e = env(&dir);
    let land = dir.join("repo-land");
    let land_text = land.to_string_lossy().into_owned();
    worktree(&root, &land);
    let adopted = run(&words(&["adopt", &land_text]), &root, &e);
    assert_eq!(adopted.code, 0, "{}", adopted.stderr);
    assert_eq!(adopted.stdout, format!("builder-tree-adopt: {land_text} joins the pool as the lane's tree, held by lane: no handout takes it and the cap (L7R_BUILDER_POOL) does not count it, its build cache as it is\n"));
    assert!(registry(&root).contains("\"lane\""));
    // the builders' reading of the registry leaves the lane out: the queue, the idle rule and the sampler count builders
    assert!(pool_of(&root).is_empty());
    assert!(run(&words(&["adopt", &land_text]), &root, &e)
        .stderr
        .contains("already in the pool"));
    // the cap of 2 is two builders' trees, the lane's beside them
    let b1 = run(&words(&["take", "T01", "9001"]), &root, &e);
    assert_eq!(b1.stdout, format!("{}\n", dir.join("repo-b1").display()));
    assert!(b1.stderr.contains("(1 of 2 now)"), "{}", b1.stderr);
    let b2 = run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(b2.stdout, format!("{}\n", dir.join("repo-b2").display()));
    let full = run(&words(&["take", "T03", "9001"]), &root, &e);
    assert!(
        full.code == 2 && full.stderr.contains("at its cap of 2"),
        "{}",
        full.stderr
    );
    assert!(!full.stderr.contains("repo-land"), "{}", full.stderr);
    // the holder's word is reserved: no take, release or adoption names it
    for asked in [
        &["take", "lane", "9001"][..],
        &["release", "lane"],
        &["landed", "9001", "lane"],
        &[
            "adopt",
            &dir.join("repo-t1").to_string_lossy(),
            "T01,lane",
            "9001",
        ],
    ] {
        let said = run(&words(asked), &root, &e);
        assert!(
            said.stderr
                .contains("`lane` is the landing lane's reserved holder"),
            "{asked:?}: {}",
            said.stderr
        );
        assert_eq!(said.code, i32::from(asked[0] != "landed") * 2, "{asked:?}");
    }
    assert!(registry(&root).contains("\"lane\""));
    let listed = run(&words(&["list"]), &root, &e);
    assert!(
        listed
            .stdout
            .starts_with("builder-trees: 2 of 2 (the cap, L7R_BUILDER_POOL), and the lane's tree"),
        "{}",
        listed.stdout
    );
    assert!(
        listed
            .stdout
            .contains("repo-land  lane  since 2026-11-26T12:00:00Z"),
        "{}",
        listed.stdout
    );
    // a freed builder's tree is the next handout, never the lane's
    assert_eq!(run(&words(&["release", "T01", "9001"]), &root, &e).code, 0);
    let next = run(&words(&["take", "T04", "9001"]), &root, &e);
    assert_eq!(next.stdout, b1.stdout);
    // gone from disk: the drop and the adoption to run
    std::fs::remove_dir_all(&land).unwrap();
    git(&root, &["worktree", "prune"]);
    let gone = run(&words(&["lane"]), &root, &e);
    assert!(
        gone.code == 2 && gone.stderr.contains("is gone from disk"),
        "{}",
        gone.stderr
    );
}

#[test]
fn a_batch_s_start_brings_the_lane_s_tree_to_origin_main_over_whatever_it_holds() {
    let (dir, root) = world("pool-lane-main");
    let e = env(&dir);
    let land = dir.join("repo-land");
    // none adopted: the command to adopt it
    let none = run(&words(&["lane"]), &root, &e);
    assert_eq!(none.code, 2);
    assert!(
        none.stderr
            .contains(&format!("make builder-tree-adopt TREE={}", land.display())),
        "{}",
        none.stderr
    );
    worktree(&root, &land);
    assert_eq!(
        run(&words(&["adopt", &land.to_string_lossy()]), &root, &e).code,
        0
    );
    // origin/main moves past what the clone last fetched; the clone's HEAD moves past origin/main
    commit(&root, "scripts/a.py", "x = 2\n");
    git(&root, &["push", "-q", "origin", "HEAD:main"]);
    let tip = git(&root, &["rev-parse", "HEAD"]).trim().to_owned();
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD~1"]);
    commit(&root, "scripts/b.py", "y = 1\n");
    // the lane's tree holds a commit of its own, a cherry-pick stopped on a conflict, an untracked file
    put(&land, "scripts/a.py", "x = 3\n");
    git(&land, &["add", "-A"]);
    git(&land, &["commit", "-qm", "the lane's own"]);
    assert_ne!(crate::git(&land, &["cherry-pick", &tip]).0, Some(0));
    assert!(picking(&land));
    put(&land, "scratch.txt", "left\n");
    let ready = run(&words(&["lane"]), &root, &e);
    assert_eq!(ready.code, 0, "{}", ready.stderr);
    assert_eq!(ready.stdout, format!("{}\n", land.display()));
    assert!(
        ready
            .stderr
            .contains(&format!("at origin/main ({})", &tip[..10])),
        "{}",
        ready.stderr
    );
    assert_eq!(git(&land, &["rev-parse", "HEAD"]).trim(), tip);
    assert_eq!(git(&land, &["status", "--porcelain"]), "");
    assert!(!picking(&land));
    assert!(!land.join("scripts/b.py").exists());
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    assert!(
        log.lines().any(|l| l.contains("\"event\":\"lane\"")),
        "{log}"
    );
}

#[test]
fn the_knob_names_another_tree_and_the_pool_holds_one_lane() {
    let (dir, root) = world("pool-lane-knob");
    let land = dir.join("repo-land");
    let other = dir.join("lane-two");
    worktree(&root, &land);
    worktree(&root, &other);
    let e = super::Env {
        lane_tree: "lane-two".to_owned(),
        ..env(&dir)
    };
    // named by the knob, the landing's worktree is the tool's again
    assert!(run(&words(&["adopt", &land.to_string_lossy()]), &root, &e)
        .stderr
        .contains("is not a builder's worktree"));
    let with = run(
        &words(&["adopt", &other.to_string_lossy(), "T01", "9001"]),
        &root,
        &e,
    );
    assert!(
        with.code == 2
            && with
                .stderr
                .contains("held by lane alone: adopt it with no T="),
        "{}",
        with.stderr
    );
    assert_eq!(
        run(&words(&["adopt", &other.to_string_lossy()]), &root, &e).code,
        0
    );
    // a path the knob names, as well as a name
    let e = super::Env {
        lane_tree: land.to_string_lossy().into_owned(),
        ..e
    };
    let second = run(&words(&["adopt", &land.to_string_lossy()]), &root, &e);
    assert!(
        second.code == 2
            && second.stderr.contains(&format!(
                "the pool holds the lane's tree already ({})",
                other.display()
            )),
        "{}",
        second.stderr
    );
    // the fetch fails: nothing moved, said
    git(
        &root,
        &[
            "remote",
            "set-url",
            "origin",
            &dir.join("nowhere.git").to_string_lossy(),
        ],
    );
    let failed = run(&words(&["lane"]), &root, &e);
    assert!(
        failed.code == 2
            && failed
                .stderr
                .contains("could not be brought to origin/main"),
        "{}",
        failed.stderr
    );
}
