//! The per-clone leftovers on a fixture: a mirror and a clone with their git directories and generation caches, a worktree whose
//! `.git` is a file, every entry's age set by hand up to the fixture's root.

use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{dead_stores, git_dirs, landed, number, open_elsewhere, scratchpad, snapshots};
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

#[test]
fn a_landing_takes_its_tasks_scratch_worlds_in_its_own_session_s_scratchpad_by_whole_number() {
    let (base, mut c) = world();
    let top = &*base;
    c.root = base.join("root");
    c.keep = "sess".to_owned();
    let pad = c.root.join("-diagram--clones-x/sess/scratchpad");
    for f in [
        "t51-a.txt",
        "t515-b/x",
        "t51/x",
        "t51x.log",
        "tmp.y",
        "notes.md",
    ] {
        put(top, &pad.join(f), 0);
    }
    put(top, &c.root.join("-diagram/other/scratchpad/t51-c"), 0);
    // an entry holding a registered worktree's tree stays
    let tree = pad.join("t51-wt/tree");
    std::fs::create_dir_all(tree.parent().unwrap()).unwrap();
    crate::guards::scratch_sweep_hooks::sweep::fixture::worktree(&c.clones, &tree);
    assert_eq!(
        names(&scratchpad(&c, &[51]), &pad),
        ["t51", "t51-a.txt", "t51x.log"]
    );
    assert_eq!(names(&scratchpad(&c, &[515]), &pad), ["t515-b"]);
    assert!(scratchpad(&c, &[]).is_empty());
    c.keep = String::new();
    assert!(scratchpad(&c, &[51]).is_empty());
}

#[test]
fn another_feature_s_start_holds_the_number_while_its_task_is_open_whatever_its_age() {
    let base = TempDir::new("guard-sweep-open-elsewhere");
    let git = base.join("clone/.git");
    std::fs::create_dir_all(&git).unwrap();
    let specs = base.join("clone/specs");
    for (dir, text) in [
        (
            "417-seeds",
            "- [ ] T163 open\n- [x] T164 done\n- [ ] T1650 other\n",
        ),
        ("451-time", "- [ ] T170 ours\n"),
    ] {
        std::fs::create_dir_all(specs.join(dir)).unwrap();
        std::fs::write(specs.join(dir).join("tasks.md"), text).unwrap();
    }
    let starts = git.join("task-starts.jsonl");
    std::fs::write(
        &starts,
        [
            r#"{"feature": "417-seeds", "task": "T163", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"feature": "417-seeds", "task": "T164", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"feature": "417-seeds", "task": "T165", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"feature": "451-time", "task": "T170", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"feature": "999-gone", "task": "T171", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"feature": "417-seeds", "task": "T172", "utc": "2000-01-01T00:00:00Z"}"#,
            r#"{"unstart": {"feature": "417-seeds", "task": "T172"}, "utc": "2000-01-01T00:00:01Z"}"#,
            "not json",
        ]
        .join("\n"),
    )
    .unwrap();
    // open elsewhere: held; ticked elsewhere, a T1650 for a T165, our own feature's, unstarted: not; no tasks.md to read: held
    assert_eq!(
        open_elsewhere(&starts, "451", &[163, 164, 165, 170, 171, 172]),
        [163, 171]
    );
    assert!(open_elsewhere(&base.join("none.jsonl"), "451", &[163]).is_empty());
}

#[test]
fn every_open_number_of_another_feature_holds_whether_started_or_not() {
    let base = TempDir::new("guard-sweep-open-unstarted");
    let git = base.join("clone/.git");
    std::fs::create_dir_all(&git).unwrap();
    let specs = base.join("clone/specs");
    for (dir, file, text) in [
        // 451: its moved boxes ticked in tasks-done.md, one open of its own
        (
            "451-time",
            "tasks-done.md",
            "- [x] T22 Withdrawn 2026-11-27: moved to 462 as 451 T22\n- [x] T40 landed\n",
        ),
        ("451-time", "tasks.md", "- [ ] T537 open\n"),
        // 462: a moved task keeps its 451 id, open here
        (
            "462-backlog",
            "tasks.md",
            "- [ ] T22 (451 T22) moved\n- [X] T23 done\n",
        ),
        // 461: open, never started; an old feature's bold zero-padded id; a box with no id
        (
            "461-lane",
            "tasks.md",
            "- [ ] T50 open\n  - [ ] **T007** old form\n- [ ] GM review\n- [x] T60 done\n",
        ),
    ] {
        std::fs::create_dir_all(specs.join(dir)).unwrap();
        std::fs::write(specs.join(dir).join(file), text).unwrap();
    }
    // no start at all: task-starts.jsonl holds nothing
    let starts = git.join("task-starts.jsonl");
    std::fs::write(&starts, "").unwrap();
    // 451 lands: 461's open T50 and T7 and 462's open T22 hold; ticked T60 and T23, and 451's own, do not
    assert_eq!(
        open_elsewhere(&starts, "451", &[7, 22, 23, 40, 50, 60, 537]),
        [7, 22, 50]
    );
    // 462 lands its moved T22: 451's ticked line moved to it holds nothing; 451's open T537 holds, by name or number
    assert_eq!(open_elsewhere(&starts, "462", &[22, 537]), [537]);
    assert_eq!(open_elsewhere(&starts, "462-backlog", &[22, 537]), [537]);
    // 461 lands: 462's open T22 holds it, whatever 451 ticked
    assert_eq!(open_elsewhere(&starts, "461", &[22, 40, 50]), [22]);
}
