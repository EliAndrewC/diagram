//! The audit on a fixture: every place a temp directory of its own, the disk's size set, and a build cache past its budget.

use std::path::Path;
use std::time::SystemTime;

use super::audit;
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

fn put(path: &Path, size: usize) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, vec![b'x'; size]).unwrap();
}

#[test]
fn the_audit_names_every_place_its_size_owner_age_and_budget_and_the_disk_s_total() {
    crate::shared::log::quiet();
    let base = TempDir::new("guard-disk-audit");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("home/.cache/l7r-cargo-target");
    c.cache_home = base.join("home/.cache");
    c.clones = base.join("diagram/.clones");
    c.mirror = base.join("diagram");
    c.root = base.join("tmp/claude-4242");
    c.tmp = base.join("tmp");
    c.projects = base.join("home/.claude/projects");
    c.guard_log = base.join("home/.claude/guard-log");
    c.state = base.join("state");
    c.proc = base.join("proc");
    std::fs::create_dir_all(c.proc.join("1")).unwrap();
    c.uid = {
        use std::os::unix::fs::MetadataExt;
        std::fs::metadata(&*base).unwrap().uid()
    };
    c.budget = 10_000;
    c.space = Some((10_000_000_000, 1_000_000_000));
    for (p, n) in [
        ("home/.cache/l7r-cargo-target/work/debug/x", 40_000),
        ("home/.cache/l7r-cargo-target/diagram/debug/x", 8_000),
        ("home/.cache/l7r-cargo-target/clone/debug/x", 8_000),
        ("home/.cache/l7r-cargo-target/gone/debug/x", 8_000),
        ("home/.cache/pip/x", 8_000),
        ("diagram/.clones/work/f", 8_000),
        ("diagram/.git/x", 8_000),
        ("tmp/claude-4242/-diagram/sess-1/x", 8_000),
        ("tmp/claude-4242/loose.txt", 100),
        ("tmp/l7r-check/x", 8_000),
        ("tmp/t245/x", 8_000),
        ("home/.claude/projects/-diagram/s.jsonl", 8_000),
        ("home/.claude/guard-log/a.json", 100),
    ] {
        put(&base.join(p), n);
    }
    // a registered worktree of the clone outside the clones directory, building into its basename
    let wt = base.join("tmp/t9/wt");
    std::fs::create_dir_all(&wt).unwrap();
    put(
        &base.join("diagram/.clones/work/.git/worktrees/wt/gitdir"),
        0,
    );
    std::fs::write(
        base.join("diagram/.clones/work/.git/worktrees/wt/gitdir"),
        format!("{}/.git\n", wt.display()),
    )
    .unwrap();
    put(&c.cargo.join("wt/debug/x"), 8_000);
    let out = audit(&c, SystemTime::now()).stdout;
    for want in [
        "OVER by ",
        "the build cache ",
        "/work  (the tree ",
        "/diagram  (the mirror's: the guard's kept binary",
        "/clone  (the hooks suites' and trials' fixture trees",
        "/gone  (no tree of that name on disk",
        "Claude Code's scratch ",
        "(session sess-1;",
        "(loose;",
        "the session transcripts ",
        "the guard log ",
        "/l7r-*",
        "l7r-check  (a suite or a tool",
        "t245  (a builder's scratch",
        "the session clones ",
        "outside the clones",
        "/.git  (the mirror",
        "the rest of ",
        "pip  (cache pip",
        "last written 0.0 h ago",
        "disk: 9.0 GB used of 10.0 GB, 1.0 GB free (10%; the eviction starts below 20%",
        "unaccounted ",
        "now: disk under 20% free (L7R_DISK_FREE_PCT): the eviction ",
    ] {
        assert!(out.contains(want), "{want:?} in\n{out}");
    }
    // the clones are not counted twice, nor the cache, nor the scratch root in the rest of /tmp
    assert!(!out.contains("/.clones  (the mirror"), "{out}");
    assert!(!out.contains("l7r-cargo-target  (cache"), "{out}");
    assert!(!out.contains("claude-4242  (a builder's"), "{out}");
    // the dry run removed nothing
    assert!(c.cargo.join("work/debug").exists());
    c.space = None;
    // the worktree's build directory, alone in the cache, named by its tree
    for t in ["work", "diagram", "clone", "gone"] {
        std::fs::remove_dir_all(c.cargo.join(t)).unwrap();
    }
    let alone = audit(&c, SystemTime::now()).stdout;
    assert!(alone.contains("/wt  (the worktree "), "{alone}");
    c.cargo = base.join("none");
    assert!(audit(&c, SystemTime::now())
        .stdout
        .contains("disk: df could not read"));
}
