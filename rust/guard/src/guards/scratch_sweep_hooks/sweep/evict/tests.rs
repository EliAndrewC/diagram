//! The budget's eviction on a fixture: a cargo root whose build directories are a clone's whose HEAD moved an hour ago (active), a
//! clone's idle two days, the mirror's, a landing tree's with no tree on disk, and one a live process holds - every profile aged by hand.

use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::choose;
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

const HOUR: u64 = 3600;

/// Write `size` bytes at `path`, it and its parents up to `top` set `h` hours ago.
fn put(top: &Path, path: &Path, size: usize, h: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, vec![b'x'; size]).unwrap();
    let when = SystemTime::now() - Duration::from_secs(h * HOUR);
    let mut at = Some(path);
    while let Some(p) = at {
        File::open(p).unwrap().set_modified(when).unwrap();
        if p == top {
            break;
        }
        at = p.parent();
    }
}

/// A clone `<clones>/<name>` whose HEAD log moved `h` hours ago.
fn clone(c: &Config, name: &str, h: u64) {
    let log = c.clones.join(name).join(".git/logs/HEAD");
    put(&c.clones, &log, 10, h);
}

fn world() -> (TempDir, Config) {
    let base = TempDir::new("guard-sweep-evict");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("cargo");
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    c.proc = base.join("proc");
    std::fs::create_dir_all(c.proc.join("1")).unwrap();
    let k = c.cargo.clone();
    clone(&c, "busy", 1);
    clone(&c, "idle", 48);
    // a worktree's `.git` file names its administrative directory, whose HEAD log moved two days ago
    let admin = base.join("admin/wt");
    put(&base, &admin.join("logs/HEAD"), 10, 48);
    std::fs::create_dir_all(c.clones.join("wt")).unwrap();
    std::fs::write(
        c.clones.join("wt/.git"),
        format!("gitdir: {}\n", admin.display()),
    )
    .unwrap();
    for (path, size, h) in [
        ("busy/cover-gate/x", 40_000, 30),
        ("busy/debug/x", 40_000, 1),
        ("idle/cover-gate/x", 40_000, 20),
        ("idle/debug/x", 40_000, 40),
        ("idle/l7r-guard.good", 40_000, 90),
        ("diagram/debug/x", 40_000, 90),
        ("busy-land/debug/x", 40_000, 30),
        ("wt/debug/x", 40_000, 25),
        ("held/debug/x", 40_000, 90),
    ] {
        put(&k, &k.join(path), size, h);
    }
    (base, c)
}

fn names(found: &[(PathBuf, &str)], c: &Config) -> Vec<String> {
    found
        .iter()
        .map(|(p, _)| p.strip_prefix(&c.cargo).unwrap().display().to_string())
        .collect()
}

fn cutoff() -> SystemTime {
    SystemTime::now() - Duration::from_secs(12 * HOUR)
}

#[test]
fn past_the_budget_idle_trees_profiles_go_least_recently_built_first_then_an_active_tree_s() {
    let (_base, c) = world();
    let held = vec![c.cargo.join("held/debug/x")];
    // everything it may take: idle trees' profiles oldest first, then the active tree's idle one; never the mirror's, a held one, a
    // profile built within the knob, or a build directory's own file
    let all = choose(&c, u64::MAX, cutoff(), &held);
    assert_eq!(
        names(&all, &c),
        [
            "idle/debug",
            "busy-land/debug",
            "wt/debug",
            "idle/cover-gate",
            "busy/cover-gate",
        ]
    );
    assert!(all[0].1.contains("an idle tree's profile"));
    assert!(all[4].1.contains("an active tree's profile"));
    // it stops once the need is met: one profile of 40 kB frees 40 kB
    assert_eq!(names(&choose(&c, 1, cutoff(), &held), &c), ["idle/debug"]);
    assert_eq!(
        names(&choose(&c, 50_000, cutoff(), &held), &c),
        ["idle/debug", "busy-land/debug"]
    );
    // within the budget, nothing
    assert!(choose(&c, 0, cutoff(), &held).is_empty());
}

#[test]
fn a_tree_a_live_process_works_in_is_active_however_old_its_head() {
    let (_base, c) = world();
    let held = vec![c.clones.join("idle/src"), c.cargo.join("held/debug/x")];
    let all = names(&choose(&c, u64::MAX, cutoff(), &held), &c);
    // the idle clone, its cwd held, ranks after the trees no one is in
    assert_eq!(all.last().map(String::as_str), Some("idle/cover-gate"));
    assert_eq!(all[0], "busy-land/debug");
}

/// A builder pool tree's build directory is never the budget's (451 T285): free, it is idle, and its cache is what the pool keeps.
#[test]
fn a_pool_tree_s_profiles_are_never_taken() {
    let (_base, c) = world();
    let before = names(&choose(&c, u64::MAX, cutoff(), &[]), &c);
    assert!(before.iter().any(|n| n.starts_with("idle/")), "{before:?}");
    let tree = crate::shared::builder_pool::Tree {
        tree: c.clones.join("idle"),
        feature: String::new(),
        tasks: Vec::new(),
        since: String::new(),
    };
    crate::shared::builder_pool::write(&c.clones.join("busy/.git"), &[tree]).unwrap();
    let after = names(&choose(&c, u64::MAX, cutoff(), &[]), &c);
    let idle = after.iter().filter(|n| n.starts_with("idle/")).count();
    assert!(idle == 0 && !after.is_empty(), "{after:?}");
}

/// A pool of `trees` written in the clone `busy`'s registry, each `(name, held)` a tree on disk with a debug and a coverage profile
/// built 30 hours ago; the free ones have no tasks.
fn pool(c: &Config, common: &str, trees: &[(&str, bool)]) {
    let k = &c.cargo;
    let list: Vec<_> = trees
        .iter()
        .map(|&(name, held)| {
            std::fs::create_dir_all(c.clones.join(name)).unwrap();
            for p in ["debug/x", "cover-gate/x"] {
                put(k, &k.join(name).join(p), 40_000, 30);
            }
            crate::shared::builder_pool::Tree {
                tree: c.clones.join(name),
                feature: if held {
                    "451".to_owned()
                } else {
                    String::new()
                },
                tasks: if held {
                    vec!["T1".to_owned()]
                } else {
                    Vec::new()
                },
                since: String::new(),
            }
        })
        .collect();
    std::fs::create_dir_all(c.clones.join(common).join(".git")).unwrap();
    crate::shared::builder_pool::write(&c.clones.join(common).join(".git"), &list).unwrap();
}

/// The pool trees whose profiles the budget takes, by tree.
fn taken(c: &Config, held: &[PathBuf], of: &[&str]) -> Vec<String> {
    let all = names(&choose(c, u64::MAX, cutoff(), held), c);
    of.iter()
        .filter(|t| all.iter().any(|n| n.starts_with(&format!("{t}/"))))
        .map(|t| (*t).to_owned())
        .collect()
}

/// 451 T526: a free pool tree past the trees `L7R_BUILDERS` (3) can hand out - a handout takes the first free tree in the registry's
/// order - has its profiles taken, coverage and all; the first three are kept warm.
#[test]
fn a_free_pool_tree_past_the_builder_count_has_its_profiles_taken() {
    let (_base, c) = world();
    pool(
        &c,
        "busy",
        &[("p1", false), ("p2", true), ("p3", false), ("p4", false)],
    );
    assert_eq!(taken(&c, &[], &["p1", "p2", "p3", "p4"]), ["p4"]);
    let all = names(&choose(&c, u64::MAX, cutoff(), &[]), &c);
    assert!(all.contains(&"p4/debug".to_owned()) && all.contains(&"p4/cover-gate".to_owned()));
}

/// Past the count, a held tree and a tree a live process works in are still never taken; at a count of four, the fourth is kept.
#[test]
fn past_the_count_a_held_or_busy_tree_is_kept_and_the_knob_moves_the_line() {
    let (_base, mut c) = world();
    pool(
        &c,
        "busy",
        &[
            ("p1", false),
            ("p2", false),
            ("p3", false),
            ("p4", true),
            ("p5", false),
        ],
    );
    let of = ["p1", "p2", "p3", "p4", "p5"];
    assert_eq!(taken(&c, &[], &of), ["p5"]);
    assert!(taken(&c, &[c.cargo.join("p5/debug/x")], &of).is_empty());
    c.builders = 2;
    assert_eq!(taken(&c, &[], &of), ["p3", "p5"]);
}

/// The landing lane's tree (feature 461 D1) is kept wherever it stands and is not counted, whether its name or its holder marks it;
/// a tree gone from disk is not counted either, since a handout skips it.
#[test]
fn the_lane_s_tree_is_kept_uncounted_and_a_gone_tree_is_not_counted() {
    let (_base, c) = world();
    pool(
        &c,
        "busy",
        &[
            ("busy-land", false),
            ("p1", false),
            ("p2", false),
            ("p3", false),
            ("p4", false),
        ],
    );
    let of = ["busy-land", "p1", "p2", "p3", "p4"];
    assert_eq!(taken(&c, &[], &of), ["p4"]);
    let lane = crate::shared::builder_pool::Tree {
        tree: c.clones.join("p1"),
        feature: "lane".to_owned(),
        tasks: Vec::new(),
        since: String::new(),
    };
    let mut trees = crate::shared::builder_pool::read(&c.clones.join("busy/.git"));
    trees[1] = lane.clone();
    crate::shared::builder_pool::write(&c.clones.join("busy/.git"), &trees).unwrap();
    assert!(taken(&c, &[], &of).is_empty());
    trees[1] = crate::shared::builder_pool::Tree {
        feature: "461".to_owned(),
        tasks: vec!["lane".to_owned()],
        ..lane
    };
    trees[2].tree = c.clones.join("gone");
    crate::shared::builder_pool::write(&c.clones.join("busy/.git"), &trees).unwrap();
    // p2 is now `gone`, off disk: p3 and p4 take the two places it and p1 left, and p2's own cache is no pool tree's
    assert_eq!(taken(&c, &[], &of), ["p2"]);
}

/// Each clone's registry is counted on its own: three kept in each.
#[test]
fn each_clone_s_pool_is_counted_apart() {
    let (_base, c) = world();
    pool(
        &c,
        "busy",
        &[("p1", false), ("p2", false), ("p3", false), ("p4", false)],
    );
    pool(
        &c,
        "idle",
        &[("q1", false), ("q2", false), ("q3", false), ("q4", false)],
    );
    // an entry with no tree's name, first in the order, is passed over and counted for nothing
    let common = c.clones.join("idle/.git");
    let mut trees = crate::shared::builder_pool::read(&common);
    trees.insert(
        0,
        crate::shared::builder_pool::Tree {
            tree: PathBuf::new(),
            ..trees[0].clone()
        },
    );
    crate::shared::builder_pool::write(&common, &trees).unwrap();
    let of = ["p1", "p2", "p3", "p4", "q1", "q2", "q3", "q4"];
    assert_eq!(taken(&c, &[], &of), ["p4", "q4"]);
}
