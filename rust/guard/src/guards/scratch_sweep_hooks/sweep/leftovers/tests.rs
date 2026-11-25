//! The per-clone leftovers on a fixture: a mirror and a clone with their git directories and generation caches, a worktree whose
//! `.git` is a file, every entry's age set by hand up to the fixture's root.

use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{dead_stores, git_dirs, landed, number, snapshots};
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

const DAY: u64 = 86_400;

/// Write `path`, and set it and every directory from it up to `top` to `days` days ago.
fn put(top: &Path, path: &Path, days: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, "x").unwrap();
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
    let base = TempDir::new("guard-sweep-leftovers");
    let mut c = Config::from_env(&|_| None, 4242);
    c.mirror = base.join("diagram");
    c.clones = base.join("diagram/.clones");
    std::fs::create_dir_all(c.clones.join("clone/.git")).unwrap();
    std::fs::create_dir_all(c.mirror.join(".git")).unwrap();
    // a worktree: its `.git` a file, its scratch in its clone's
    std::fs::create_dir_all(c.clones.join("wt")).unwrap();
    std::fs::write(
        c.clones.join("wt/.git"),
        "gitdir: ../clone/.git/worktrees/wt\n",
    )
    .unwrap();
    (base, c)
}

fn ago(days: u64) -> SystemTime {
    SystemTime::now() - Duration::from_secs(days * DAY)
}

fn names(found: &[(PathBuf, &str)], top: &Path) -> Vec<String> {
    let mut v: Vec<String> = found
        .iter()
        .map(|(p, _)| p.strip_prefix(top).unwrap().display().to_string())
        .collect();
    v.sort();
    v
}

#[test]
fn a_snapshot_goes_idle_a_week_unless_the_review_tree_took_it() {
    let (base, c) = world();
    let top = &*base;
    let clone = c.clones.join("clone/.git/review-snapshot");
    put(top, &clone.join("building-review--old/dispatch.md"), 8);
    put(top, &clone.join("building-review--fresh/dispatch.md"), 1);
    // the review tree's: its copy keys the unit's content key after its review (`tree::of_unit`), kept whatever its age
    put(top, &clone.join("glyph-check--tree/tree.json"), 30);
    put(
        top,
        &c.mirror
            .join(".git/review-snapshot/size-audit--old/clone/x.svg"),
        9,
    );
    // a loose file in the snapshots' directory is no snapshot
    put(top, &clone.join("stray.txt"), 30);
    assert_eq!(
        names(&snapshots(&c, ago(7)), top),
        [
            "diagram/.clones/clone/.git/review-snapshot/building-review--old",
            "diagram/.git/review-snapshot/size-audit--old"
        ]
    );
    // the worktree's .git is a file: no git directory of its own
    let gits = git_dirs(&c).len();
    assert_eq!(gits, 2);
}

#[test]
fn a_dead_store_of_the_generation_cache_goes_idle_and_the_live_one_never() {
    let (base, c) = world();
    let top = &*base;
    put(top, &c.clones.join("clone/.gencache/rolls/ab/x.json"), 18);
    put(top, &c.clones.join("clone/.gencache/rust/reads.tsv"), 40);
    put(top, &c.clones.join("clone/.gencache/ast-426/x"), 1);
    put(top, &c.clones.join("wt/.gencache/h10/x"), 30);
    put(top, &c.mirror.join(".gencache/rust/entries/x"), 40);
    assert_eq!(
        names(&dead_stores(&c, ago(3)), top),
        [
            "diagram/.clones/clone/.gencache/rolls",
            "diagram/.clones/wt/.gencache/h10"
        ]
    );
}

#[test]
fn a_landing_takes_its_tasks_directories_in_the_git_directory_and_never_a_note_or_a_log() {
    let (base, c) = world();
    let top = &*base;
    let git = c.clones.join("clone/.git");
    for f in [
        "t204/tree/a.rs",
        "t204-land.log",
        "t2040/x",
        "t31-parked/x",
        "tmp.x/y",
        "l7r-handoffs/T204-scratch/run.sh",
        "l7r-handoffs/T204-a1b2c3.md",
        "l7r-handoffs/T2041-scratch/x",
        "l7r-handoffs/T31-scripts/x",
        "l7r-handoffs/probe/x",
    ] {
        put(top, &git.join(f), 0);
    }
    assert_eq!(
        names(&landed(&git, &[204, 31]), &git),
        [
            "l7r-handoffs/T204-scratch",
            "l7r-handoffs/T31-scripts",
            "t204",
            "t31-parked"
        ]
    );
    assert!(landed(&git, &[]).is_empty());
    assert!(landed(&base.join("no-such"), &[204]).is_empty());
    assert_eq!(number("t31-parked", 't'), Some(31));
    assert_eq!(number("T432-scratch", 'T'), Some(432));
    assert_eq!(number("tmp.x", 't'), None);
    assert_eq!(number("probe", 'T'), None);
}
