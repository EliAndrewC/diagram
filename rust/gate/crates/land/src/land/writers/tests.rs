//! Another writer in the clone (451 T242), on the landing's scratch clone: a writer arriving during the gate is met before the ticks, a
//! tick whose commit fails is put back with nothing staged, and a builder's linked worktree bears on nothing. Each asserts the clone's
//! end state - its status, its index, its tasks.md and its commits - not the landing's words alone.

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_gate_core::write_executable;

use super::super::tests::{fx, has, inner, tool, Fx, NOTE, TASKS};

/// The landing of T1.
fn land(fx: &Fx) -> Result<i32, String> {
    fx.land
        .land(&fx.root.join("specs/449-x"), &["T1".to_owned()], NOTE)
}

/// The clone as the landing left it: `git status --porcelain` (trimmed), the staged names, tasks.md and the commits since origin/main.
fn left(fx: &Fx) -> (String, String, String, String) {
    (
        git(&fx.root, &["status", "--porcelain"]),
        git(&fx.root, &["diff", "--cached", "--name-only"]),
        std::fs::read_to_string(fx.root.join("specs/449-x/tasks.md")).unwrap(),
        fx.subjects(),
    )
}

/// The gate's stamp check (pass 2, after the first pass) runs `sh` in the clone: a writer arriving there.
fn writer_during_the_gate(fx: &Fx, sh: &str) {
    fx.answer(
        &format!("{} stamp --check origin/main", tool("gates/l7r-gate.sh")),
        "sh",
        sh,
    );
}

#[test]
fn a_writer_arriving_during_the_gate_ticks_nothing() {
    // T238's landing, 2026-11-25: the clone clean at the first pass, another writer's file there by the push - the claims wait, which
    // waits for a clean tree, meets it first (a pin: it held before T242), and nothing is ticked or staged
    let fx = fx("writers-mid");
    writer_during_the_gate(&fx, "printf 'x\\n' > foreign.rs\n");
    assert_eq!(land(&fx), Ok(2));
    has(
        &fx.said().1,
        "nothing landed: uncommitted changes: ?? foreign.rs",
    );
    let (status, staged, tasks, subjects) = left(&fx);
    assert_eq!(status, "?? foreign.rs");
    assert_eq!(staged, "");
    assert_eq!(tasks, TASKS);
    assert!(!subjects.contains("ticked"), "{subjects}");
    assert!(!fx.log().contains("sync-with-main.sh"));
}

#[test]
fn a_writer_arriving_after_the_claims_wait_is_refused_before_the_ticks() {
    // the push step itself, a writer's file there since the wait found the tree clean: refused before anything is ticked
    let fx = fx("writers-push-step");
    put(&fx.root, "foreign.rs", "x");
    let d = fx.root.join("specs/449-x");
    assert_eq!(fx.land.tick_and_push(&d, &["T1".to_owned()], NOTE), Ok(2));
    has(&fx.said().1, "land: refused before the ticks - nothing ticked, nothing pushed: uncommitted changes in the clone, not this landing's: ?? foreign.rs");
    let (status, staged, tasks, subjects) = left(&fx);
    assert_eq!(status, "?? foreign.rs");
    assert_eq!(staged, "");
    assert_eq!(tasks, TASKS);
    assert!(!subjects.contains("ticked"), "{subjects}");
    assert!(!fx.log().contains("sync-with-main.sh"));
}

/// A pre-commit hook that refuses a commit holding tasks.md with `said`, `times` times (every time where 0), as a held lock refuses it.
fn refuse_the_tick(fx: &Fx, said: &str, times: u32) {
    let count = fx.dir.join("refusals");
    std::fs::create_dir_all(fx.root.join(".git/hooks")).unwrap();
    write_executable(
        &fx.root.join(".git/hooks/pre-commit"),
        &format!(
            "#!/bin/sh\ngit diff --cached --name-only | grep -q tasks.md || exit 0\nn=$(cat {c} 2>/dev/null || echo 0)\n\
             [ {times} -ne 0 ] && [ \"$n\" -ge {times} ] && exit 0\necho $((n + 1)) > {c}\necho \"{said}\" >&2\nexit 1\n",
            c = count.display()
        ),
    );
}

#[test]
fn a_tick_whose_commit_fails_is_put_back_with_nothing_staged() {
    let fx = fx("writers-commit");
    refuse_the_tick(
        &fx,
        "fatal: Unable to create '.git/index.lock': File exists.",
        0,
    );
    assert_eq!(land(&fx), Ok(2));
    let err = fx.said().1;
    has(&err, "land: the tick's commit failed (git commit: fatal: Unable to create '.git/index.lock': File exists.) - its ticks put back, nothing staged, nothing landed");
    // tried COMMIT_TRIES times, a poll apart, the lock never let go
    assert_eq!(
        std::fs::read_to_string(fx.dir.join("refusals")).unwrap(),
        "3\n"
    );
    let (status, staged, tasks, subjects) = left(&fx);
    assert_eq!((status.as_str(), staged.as_str()), ("", ""));
    assert_eq!(tasks, TASKS);
    assert!(!fx.root.join("specs/449-x/tasks-done.md").exists());
    assert!(!subjects.contains("ticked"), "{subjects}");
    assert!(!fx.log().contains("sync-with-main.sh"));
}

#[test]
fn a_commit_a_lock_held_once_is_tried_again_and_lands() {
    let fx = fx("writers-lock-once");
    refuse_the_tick(
        &fx,
        "fatal: Unable to create '.git/index.lock': File exists.",
        1,
    );
    assert_eq!(land(&fx), Ok(0));
    let (status, staged, _, subjects) = left(&fx);
    assert_eq!((status.as_str(), staged.as_str()), ("", ""));
    has(&subjects, "449-x: T1 ticked (make land)");
}

#[test]
fn a_tick_whose_add_fails_is_put_back() {
    // the add names dev/bypass-log, which this clone does not hold: git refuses the whole add
    let fx = fx("writers-add");
    git(&fx.root, &["rm", "-q", "dev/bypass-log/.keep"]);
    git(&fx.root, &["commit", "-qm", "no bypass log"]);
    assert_eq!(land(&fx), Ok(2));
    has(
        &fx.said().1,
        "land: the tick's commit failed (git add: fatal: pathspec 'dev/bypass-log' did not match any files)",
    );
    let (status, staged, tasks, _) = left(&fx);
    assert_eq!((status.as_str(), staged.as_str()), ("", ""));
    assert_eq!(tasks, TASKS);
}

#[test]
fn a_failed_push_whose_revert_another_writer_blocks_leaves_the_tick_committed() {
    // the push refuses, and by then another writer edits the feature's tasks.md: the revert is refused, the tick commit stands - committed,
    // never staged - and the writer's edit is kept
    let fx = fx("writers-push");
    fx.answer(
        &format!("{} done", tool("sync-with-main.sh")),
        "sh",
        "printf 'edit\\n' >> specs/449-x/tasks.md\n",
    );
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "1");
    assert_eq!(land(&fx), Ok(1));
    has(&fx.said().1, "its ticks could NOT be reverted");
    let (status, staged, tasks, subjects) = left(&fx);
    assert_eq!(status, "M specs/449-x/tasks.md"); // unstaged: the index is HEAD's
    assert_eq!(staged, "");
    assert!(tasks.ends_with("edit\n"));
    assert_eq!(
        subjects.lines().next(),
        Some("449-x: T1 ticked (make land)")
    );
}

#[test]
fn the_first_pass_names_the_changes_and_an_open_handoff_naming_the_clone() {
    let mut fx = fx("writers-first");
    inner(&mut fx); // in the clone, uncommitted work sends the landing to land alone (451 T88)
    put(&fx.root, "a.rs", "x");
    let root = fx.root.display().to_string();
    let handoffs = fx.root.join(".git/l7r-handoffs");
    // T2 is open and its handoff names the clone: named
    put(
        &handoffs,
        "T2-a1.md",
        &format!("work in `{root}`, then stop\n"),
    );
    // ...but not one naming a worktree beside the clone, the landing's own task's, a task not open, or a file of no task
    put(&handoffs, "T2-a2.md", &format!("work in {root}-t2/x\n"));
    put(&handoffs, "T1-a3.md", &format!("work in {root}\n"));
    put(&handoffs, "T7-a4.md", &format!("work in {root}\n"));
    put(&handoffs, "notes.md", &format!("work in {root}\n"));
    put(&handoffs, "T2-a5.txt", &format!("work in {root}\n"));
    // ...nor a finished handoff under a name a brief gives (451 T352): a build half's, a bundle's build half's, a done one's
    put(&handoffs, "T2-build.md", &format!("work in {root}\n"));
    put(&handoffs, "T2-T7-build.md", &format!("work in {root}\n"));
    put(
        &handoffs,
        "done-pending-T2.md",
        &format!("work in {root}\n"),
    );
    // ...nor one two days old
    put(&handoffs, "T2-a6.md", &format!("work in {root}\n"));
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(2 * 24 * 3600);
    std::fs::File::options()
        .write(true)
        .open(handoffs.join("T2-a6.md"))
        .unwrap()
        .set_modified(old)
        .unwrap();
    for n in 0..7 {
        put(&fx.root, &format!("b{n}.rs"), "x");
    }
    assert_eq!(land(&fx), Ok(2));
    let err = fx.said().1;
    has(&err, "uncommitted changes in the clone, not this landing's: ?? a.rs; ?? b0.rs; ?? b1.rs; ?? b2.rs; ?? b3.rs; ?? b4.rs and 2 more; an open builder handoff names the clone: ");
    has(
        &err,
        "/T2-a1.md - commit them (or let their writer finish), then land",
    );
    for not in [
        "T2-a2.md",
        "T1-a3.md",
        "T7-a4.md",
        "notes.md",
        "T2-a5.txt",
        "T2-a6.md",
        "T2-build.md",
        "T2-T7-build.md",
        "done-pending-T2.md",
    ] {
        assert!(!err.contains(not), "{not} in:\n{err}");
    }
}

#[test]
fn a_builders_worktree_bears_on_nothing() {
    // today's parallel trial: a builder's linked worktree of the clone, its own work uncommitted, and its handoff naming the worktree
    let fx = fx("writers-worktree");
    let wt = fx.dir.join("repo-t2");
    git(
        &fx.root,
        &["worktree", "add", "-q", "--detach", &wt.to_string_lossy()],
    );
    put(&wt, "specs/449-x/tasks.md", "the builder's edit\n");
    put(&wt, "new.rs", "x");
    put(
        &fx.root.join(".git/l7r-handoffs"),
        "T2-a1.md",
        &format!("work in {}\n", wt.display()),
    );
    assert_eq!(land(&fx), Ok(0));
    has(&fx.said().0, "land: T1 landed and ticked");
    assert_eq!(left(&fx).0, "");
    assert_eq!(
        std::fs::read_to_string(wt.join("specs/449-x/tasks.md")).unwrap(),
        "the builder's edit\n"
    );
}

#[test]
fn the_helpers_read_paths_tasks_and_git_s_words() {
    use std::path::Path;
    assert!(super::names_path("in /c/x.", "/c/x"));
    assert!(super::names_path("/c/x", "/c/x"));
    assert!(super::names_path("at /c/x.\n", "/c/x"));
    assert!(!super::names_path("/c/x.md", "/c/x"));
    assert!(!super::names_path("/c/x_y /c/x-t2", "/c/x"));
    assert_eq!(
        super::handoff_task(Path::new("/h/T12a-x.md")),
        Some("T12a".to_owned())
    );
    for not in [
        "/h/T-x.md",
        "/h/Tx-x.md",
        "/h/T12.md",
        "/h/p3-x.md",
        "/h/T1-x",
        "/h/T12-build.md",
        "/h/T12-T13-build.md",
        "/h/done-pending-T12.md",
    ] {
        assert_eq!(super::handoff_task(Path::new(not)), None, "{not}");
    }
    assert_eq!(
        super::open_tasks("- [ ] T1 a\n  - [ ] T2 b\n- [x] T3 c\n- [ ] note\n"),
        ["T1", "T2"]
    );
    assert_eq!(super::first_line("", "git add", 128), "git add exited 128");
    assert_eq!(super::first_line("a\nb", "git add", 1), "git add: a");
}

/// 451 T537: a split feature (`make archive-split`) - its tick folds the task it archives into a new part, which the tick's commit
/// carries, the flat tail gone; a tick whose commit fails is put back, the new part removed and the index as HEAD holds it.
#[test]
fn a_split_feature_s_tick_carries_its_new_part_and_a_failed_one_is_put_back() {
    for (tag, refused) in [("writers-split", false), ("writers-split-back", true)] {
        let fx = fx(tag);
        let d = fx.root.join("specs/449-x");
        put(&fx.root, "specs/449-x/tasks-done.md", "- [x] T0 before\n");
        l7r_shared::speckit::archive::fold(&d, true).unwrap();
        git(&fx.root, &["add", "-A"]);
        git(&fx.root, &["commit", "-qm", "split"]);
        let index = std::fs::read_to_string(d.join("archive/index.json")).unwrap();
        let part = d.join("archive/tasks-done/002-T1-T1.md");
        if refused {
            refuse_the_tick(&fx, "fatal: the lock", 0);
            assert_eq!(land(&fx), Ok(2));
            let (status, staged, tasks, _) = left(&fx);
            assert_eq!((status.as_str(), staged.as_str()), ("", ""));
            assert_eq!(tasks, TASKS);
            assert_eq!(
                std::fs::read_to_string(d.join("archive/index.json")).unwrap(),
                index
            );
            assert!(!part.exists());
        } else {
            assert_eq!(land(&fx), Ok(0));
            assert_eq!(left(&fx).0, "");
            let shown = git(&fx.root, &["show", "--name-only", "--format=", "HEAD"]);
            has(&shown, "specs/449-x/archive/tasks-done/002-T1-T1.md");
            assert!(part.is_file() && !d.join("tasks-done.md").exists());
        }
    }
}
