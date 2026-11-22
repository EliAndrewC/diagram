//! The floor, the cache's cleanup and the scratch worktrees on a fixture: a cargo root, a clones directory with one clone and a scratch
//! worktree of it, a stand-in `/proc` (no build running unless a test plants one), and every entry's age set by hand.

use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{cache, floor, free, hours, trees};
use crate::guards::scratch_sweep_hooks::{with, Config};
use crate::shared::tempdir::TempDir;
use crate::shared::tool::flock;

const HOUR: u64 = 3600;

fn now() -> SystemTime {
    SystemTime::now()
}

/// Write `path`, and set it and every directory from it up to `top` to `h` hours ago.
fn put(top: &Path, path: &Path, h: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, vec![b'x'; 8192]).unwrap();
    put_age(top, path, h);
}

/// `<cargo>/<name>/debug/x.d`, `h` hours old, naming a source tree that does not exist.
fn dead(cargo: &Path, name: &str, h: u64) {
    let d = cargo.join(name).join("debug/x.d");
    put(cargo, &d, h);
    std::fs::write(&d, "x: /no/such/tree/rust/a.rs\n").unwrap();
    put_age(cargo, &d, h);
}

fn put_age(top: &Path, path: &Path, h: u64) {
    let when = now() - Duration::from_secs(h * HOUR);
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
    crate::shared::log::quiet();
    let base = TempDir::new("guard-disk");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("cargo");
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    c.state = base.join("state");
    c.proc = base.join("proc");
    std::fs::create_dir_all(c.proc.join("1")).unwrap();
    std::fs::write(c.proc.join("1/comm"), "bash\n").unwrap();
    let k = c.cargo.clone();
    // the clone's, live; a dead tree's, idle a day; a dead tree's, an hour old (kept: under the threshold)
    put(&k, &k.join("live-clone/debug/x"), 30);
    put(&k, &k.join("t42-scratch/debug/deps/liba-1.rlib"), 24);
    put(&k, &k.join("fresh/debug/x"), 1);
    // each dead tree's dep-info names a tree that is gone (a build directory with none cannot be proven dead, 451 T158)
    for (name, h) in [("t42-scratch", 24), ("fresh", 1)] {
        dead(&k, name, h);
    }
    // a scratch worktree of the clone, outside the clones directory, and the clone's own landing worktree inside it
    let scratch = base.join("tmp/t33/wt");
    let land = c.clones.join("live-clone-land");
    let admin = c.clones.join("live-clone/.git/worktrees");
    for (id, tree) in [("wt", &scratch), ("live-clone-land", &land)] {
        std::fs::create_dir_all(tree).unwrap();
        std::fs::create_dir_all(admin.join(id)).unwrap();
        std::fs::write(
            admin.join(id).join("gitdir"),
            format!("{}/.git\n", tree.display()),
        )
        .unwrap();
    }
    (base, c)
}

fn removed(c: &Config, name: &str) -> bool {
    !c.cargo.join(name).exists()
}

#[test]
fn below_the_floor_the_gate_is_refused_naming_the_space_the_targets_the_cleanup_and_the_scratch_trees(
) {
    let (_base, mut c) = world();
    c.floor = 15_000_000_000;
    // above the floor: silent
    let fine = floor(&c, Some(20_000_000_000), now());
    assert_eq!((fine.code, fine.stderr.as_str()), (0, ""));
    // df cannot say: said, not refused
    let blind = floor(&c, None, now());
    assert!(blind.code == 0 && blind.stderr.contains("could not be read"));
    let low = floor(&c, Some(1_234_567_890), now());
    assert_eq!(low.code, 1);
    let e = &low.stderr;
    for want in [
        "REFUSED: 1.2 GB free on the build cache's disk, below the 15.0 GB floor",
        "live-clone  (a live tree's",
        "t42-scratch  (no live tree's: removed whole once idle; idle 24.0 h)",
        "make cache-clean frees 0.0 GB now (1 entries idle 12 h or more",
        "scratch worktree ",
        "worktree remove --force ",
        "DISK_OK=",
    ] {
        assert!(e.contains(want), "{want:?} in {e}");
    }
    // the clone's own landing worktree is not a scratch tree
    assert!(!e.contains("live-clone-land (of"), "{e}");
    // a build running: the cleanup waits, and the refusal says so
    std::fs::create_dir_all(c.proc.join("77")).unwrap();
    std::fs::write(c.proc.join("77/comm"), "rustc\n").unwrap();
    let busy = floor(&c, Some(1), now());
    assert!(busy
        .stderr
        .contains("waits for the build that runs now (77 rustc)"));
}

#[test]
fn the_cleanup_takes_the_idle_dead_targets_alone_and_never_while_a_build_runs_or_another_sweep_holds_the_lock(
) {
    let (_base, mut c) = world();
    let dry = cache(&c, now(), true);
    assert!(
        dry.code == 0 && dry.stdout.contains("would remove") && dry.stdout.contains("t42-scratch")
    );
    assert!(dry.stdout.contains("scratch worktree "));
    assert!(!removed(&c, "t42-scratch"));
    // another sweep holds the lock
    std::fs::create_dir_all(&c.state).unwrap();
    let held = File::create(c.state.join("lock")).unwrap();
    assert!((0..500).any(|_| flock(&held, "-n")));
    let busy = cache(&c, now(), false);
    assert!(
        busy.code == 1 && busy.stderr.contains("holds the lock") && !removed(&c, "t42-scratch")
    );
    assert!(flock(&held, "-u"));
    let ran = cache(&c, now(), false);
    assert_eq!(ran.code, 0, "{}", ran.stderr);
    assert!(ran.stdout.contains("removed ") && removed(&c, "t42-scratch"));
    assert!(!removed(&c, "live-clone") && !removed(&c, "fresh"));
    // HOURS=0: the fresh dead target goes too; but not while a build runs
    c.cache_age = Duration::ZERO;
    std::fs::create_dir_all(c.proc.join("9")).unwrap();
    std::fs::write(c.proc.join("9/comm"), "cargo\n").unwrap();
    let building = cache(&c, now(), false);
    let held_by = building.stderr.contains("a build runs (9 cargo)");
    assert!(building.code == 1 && held_by, "{}", building.stderr);
    assert!(!removed(&c, "fresh"));
    std::fs::remove_dir_all(c.proc.join("9")).unwrap();
    let again = cache(&c, now(), false);
    assert_eq!(again.code, 0, "{}", again.stderr);
    assert!(removed(&c, "fresh") && !removed(&c, "live-clone"));
    // a process table that cannot be read removes nothing
    put(&c.cargo, &c.cargo.join("again/x"), 30);
    dead(&c.cargo, "again", 30);
    let real = c.proc.clone();
    c.proc = real.join("none");
    assert!(cache(&c, now(), false).code == 0 && !removed(&c, "again"));
}

#[test]
fn the_command_line_reaches_each_mode_and_the_knobs_read_from_the_environment() {
    let (_base, mut c) = world();
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<String>>();
    c.floor = 0;
    assert_eq!(with(&args(&["floor"]), &mut c, now()).code, 0);
    let t = with(&args(&["trees"]), &mut c, now());
    assert!(t.code == 0 && t.stdout.lines().count() == 1 && t.stdout.contains("t33/wt"));
    assert!(with(&args(&["cache-dry"]), &mut c, now())
        .stdout
        .contains("would remove"));
    assert_eq!(with(&args(&["cache"]), &mut c, now()).code, 0);
    assert!(removed(&c, "t42-scratch"));
    let knobs = Config::from_env(
        &|k| match k {
            "L7R_DISK_FLOOR_GB" => Some("2.5".to_owned()),
            "L7R_CACHE_IDLE_HOURS" => Some("0.5".to_owned()),
            _ => None,
        },
        1,
    );
    assert_eq!(
        (knobs.floor, knobs.cache_age),
        (2_500_000_000, Duration::from_secs(1800))
    );
    let defaults = Config::from_env(&|k| (k == "L7R_DISK_FLOOR_GB").then(|| "-3".to_owned()), 1);
    assert_eq!(
        (defaults.floor, defaults.cache_age),
        (15_000_000_000, Duration::from_secs(12 * HOUR))
    );
}

#[test]
fn df_reads_a_directory_s_free_space_and_nothing_of_a_missing_one() {
    let (base, _c) = world();
    assert!(free(&base).is_some_and(|f| f > 0));
    assert!(free(&PathBuf::from("/nonexistent/t158")).is_none());
    assert_eq!(hours(now(), now() + Duration::from_secs(HOUR)), "0.0 h");
    let (_b, c) = world();
    assert_eq!(trees(&c, now()).len(), 1);
}

#[test]
fn past_the_budget_the_cleanup_takes_what_is_not_in_use_whatever_its_age() {
    let (_base, mut c) = world();
    assert!(!cache(&c, now(), true).stdout.contains("/fresh "));
    c.budget = 0;
    let dry = cache(&c, now(), true);
    assert!(dry.stdout.contains("cargo/fresh ") && !dry.stdout.contains("cargo/live-clone "));
}

#[test]
fn a_landing_removes_its_tasks_own_scratch_and_says_which_number_it_left() {
    use std::os::unix::fs::MetadataExt;
    let (base, mut c) = world();
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<String>>();
    c.tmp = base.join("tmp");
    c.uid = std::fs::metadata(&c.tmp).unwrap().uid();
    put(&c.tmp, &c.tmp.join("t158/m.py"), 0);
    put(&c.tmp, &c.tmp.join("t160/x"), 0);
    let starts = base.join("starts.jsonl");
    std::fs::write(
        &starts,
        r#"{"feature": "449-rust", "task": "T160", "utc": "2999-01-01T00:00:00Z"}"#,
    )
    .unwrap();
    let s = starts.display().to_string();
    // a clean scratch worktree idle past the scratch threshold: removed at the landing, not only named (451 T158's plan review)
    let tree = crate::guards::scratch_sweep_hooks::sweep::fixture::clean(
        &c.clones,
        &base.join("wt/t7/clean"),
        9,
    );
    let out = with(&args(&["landed", "451", &s, "T158,T160"]), &mut c, now());
    assert_eq!(out.code, 0);
    assert!(out.stdout.contains("removed ") && out.stdout.contains("left /tmp/t160*"));
    assert!(out.stdout.contains("removed the clean scratch worktree") && !tree.exists());
    assert!(!c.tmp.join("t158").exists() && c.tmp.join("t160").exists());
    let none = with(&args(&["landed", "451", &s, "T999"]), &mut c, now());
    assert!(none.code == 0 && none.stdout.is_empty());
    assert_eq!(with(&args(&["landed", "451"]), &mut c, now()).code, 2);
    // where the process table cannot be read, a landing removes nothing
    put(&c.tmp, &c.tmp.join("t161/x"), 0);
    c.proc = base.join("no-proc");
    let blind = with(&args(&["landed", "451", &s, "T161"]), &mut c, now());
    assert!(blind.stdout.is_empty() && c.tmp.join("t161").exists());
}
