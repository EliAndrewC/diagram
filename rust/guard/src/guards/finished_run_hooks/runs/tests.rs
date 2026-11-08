//! What runs and who waits, on the stand-in `/proc` of the guard's tests.

use std::os::unix::fs::PermissionsExt;
use std::path::Path;

use super::super::tests::world;
use super::{files_named, owner, realpath, Root, Status};

#[test]
fn a_path_is_resolved_whether_or_not_it_exists() {
    assert_eq!(
        realpath(Path::new("./no-such-either")),
        Path::new("no-such-either")
    );
    let w = world("real");
    assert_eq!(realpath(&w.clone.join("a/../b/./c")), w.clone.join("b/c"));
    assert_eq!(
        realpath(Path::new("relative-no-such")),
        Path::new("relative-no-such")
    );
    assert_eq!(owner(&w.clone.join("deep/er")), Some(w.clone.clone()));
    assert_eq!(owner(Path::new("/")), None);
}

#[test]
fn a_command_line_names_only_files_through_its_variables() {
    let w = world("named");
    let dir = w.root.join("v");
    std::fs::create_dir_all(&dir).unwrap();
    let (log, tool) = (dir.join("a.log"), dir.join("tool.sh"));
    std::fs::write(&tool, "").unwrap();
    std::fs::set_permissions(&tool, std::fs::Permissions::from_mode(0o755)).unwrap();
    let d = dir.display();
    let found = files_named(&format!("S={d}; L=$S/a.log; until grep -q X ${{L}} $UNKNOWN/x; do {d}/tool.sh {d} /no/such/dir/f; sleep 3; done"), Path::new("/"));
    assert!(found.contains(&log) && found.len() == 1);
    let quoted = files_named(&format!("S=\"{d}\" ; tail $S/q.log"), Path::new("/"));
    assert!(quoted.contains(&dir.join("q.log")));
    let relative = files_named("cat v/r.log", &w.root);
    assert!(relative.contains(&realpath(&w.root.join("v/r.log"))));
}

#[test]
fn a_phase_child_speaks_through_its_root_and_each_status_has_its_line() {
    let w = world("roots");
    let log = w.root.join("run.log");
    std::fs::write(&log, "").unwrap();
    w.add(100, "make", 1, &w.clone, &["make", "done"], Some(&log));
    w.add(101, "make", 100, &w.clone.join("sub"), &["make", "t"], None);
    w.add(102, "bash", 1, &w.clone, &["bash"], None);
    let elsewhere = w.root.join("elsewhere");
    std::fs::create_dir_all(elsewhere.join(".git")).unwrap();
    w.add(103, "make", 1, &elsewhere, &["make", "theirs"], None);
    assert_eq!(w.procs().live_runs(&w.clone).len(), 2);
    let roots = w.procs().judge_runs(&w.clone);
    assert_eq!(roots.len(), 1);
    assert_eq!(
        roots[0].line(),
        format!("100 done unwatched {}", log.display())
    );
    let watched = Root {
        pid: 1,
        target: "t".to_owned(),
        status: Status::Watched(2, "/f".to_owned()),
    };
    assert_eq!(watched.line(), "1 t watched 2 /f");
    assert_eq!(
        Root {
            pid: 1,
            target: "t".to_owned(),
            status: Status::Tracked("o".to_owned())
        }
        .line(),
        "1 t tracked o"
    );
}

#[test]
fn a_run_with_no_output_file_and_a_chain_named_on_an_ancestor() {
    let w = world("chain");
    // a loop on some other file, one whose cwd cannot be read: it watches nothing of this run's
    w.add(
        201,
        "bash",
        1,
        Path::new("/"),
        &[
            "bash",
            "-c",
            "until grep -q X /tmp/other.log; do sleep 1; done",
        ],
        None,
    );
    std::fs::remove_file(w.proc.join("201/cwd")).unwrap();
    w.add(100, "make", 1, &w.clone, &["make", "a"], None);
    assert_eq!(
        w.procs().judge_runs(&w.clone)[0].status,
        Status::Unwatched("(no file)".to_owned())
    );
    let chain = world("chain2");
    let last = chain.root.join("b.log");
    let parent = format!("make a; make b > {}", last.display());
    chain.add(90, "bash", 1, &chain.root, &["bash", "-c", &parent], None);
    chain.add(100, "make", 90, &chain.clone, &["make", "a"], None);
    let waiter = format!("until grep -q DONE {} ; do sleep 3; done", last.display());
    chain.add(
        200,
        "bash",
        1,
        Path::new("/"),
        &["bash", "-c", &waiter],
        None,
    );
    assert_eq!(
        chain.procs().judge_runs(&chain.clone)[0].status,
        Status::Watched(200, last.to_string_lossy().into_owned())
    );
}

#[test]
fn the_hooks_own_tree_is_never_a_waiter_and_a_claude_ancestor_ends_the_chain() {
    let w = world("mine");
    let log = w.root.join("m.log");
    std::fs::write(&log, "").unwrap();
    let cmd = format!("until grep -q X {}; do sleep 1; done", log.display());
    w.add(
        99_999,
        "l7r-guard",
        500,
        Path::new("/"),
        &["l7r-guard"],
        None,
    );
    w.add(500, "bash", 1, Path::new("/"), &["bash", "-c", &cmd], None);
    w.add(100, "make", 1, &w.clone, &["make", "x"], Some(&log));
    assert!(matches!(
        w.procs().judge_runs(&w.clone)[0].status,
        Status::Unwatched(_)
    ));
    assert!(w
        .procs()
        .stale_waiters(&w.root.join("tree"), None)
        .is_empty());
}

#[test]
fn only_a_live_file_of_this_clone_makes_a_waiter_stale() {
    let w = world("waiters");
    let tree = w.root.join("tree");
    let snaps = w.root.join("shell-snapshots");
    std::fs::create_dir_all(&snaps).unwrap();
    let (snap, script, dead) = (
        snaps.join("s.sh"),
        w.root.join("run.sh"),
        w.root.join("dead.log"),
    );
    for f in [&snap, &script, &dead] {
        std::fs::write(f, "").unwrap();
    }
    std::fs::set_permissions(&script, std::fs::Permissions::from_mode(0o755)).unwrap();
    let cmd = format!(
        "source {}; until grep -q X {} {} /gone/x.log {}; do sleep 3; {}; done",
        snap.display(),
        dead.display(),
        dead.display(),
        dead.display(),
        script.display()
    );
    w.add(300, "bash", 1, &w.clone, &["bash", "-c", &cmd], None);
    w.add(
        301,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", "echo hello; sleep 3"],
        None,
    );
    let elsewhere = w.root.join("other");
    std::fs::create_dir_all(elsewhere.join(".git")).unwrap();
    w.add(302, "bash", 1, &elsewhere, &["bash", "-c", &cmd], None);
    let mine = w.procs().stale_waiters(&tree, Some(&w.clone));
    assert_eq!(mine, [format!("300 {}", dead.display())]);
    assert_eq!(w.procs().stale_waiters(&tree, None).len(), 2);
    std::fs::write(tree.join("scripts/hooks/lib/writer-alive.sh"), "exit 0\n").unwrap();
    assert!(w.procs().stale_waiters(&tree, None).is_empty());
}
