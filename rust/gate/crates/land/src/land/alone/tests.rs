//! A task landing alone (feature 451 T88): work uncommitted in the clone sends the whole landing to `scripts/land-alone.sh` - nothing of
//! it runs in the clone, and its `end` line is the worktree's landing's, but where the script refused before that ran; the landing
//! worktree's own run (`L7R_LAND_ALONE`) lands as before, its uncommitted-work refusal standing.

use std::path::Path;
use std::time::SystemTime;

use l7r_gate_core::ci::fixtures::put;
use serde_json::Value;

use super::super::tests::{fx, Fx, NOTE};
use super::{INNER, REFUSED_FIRST, SCRIPT};

/// The landing's `end` lines in the tree's event logs.
fn ends(root: &Path) -> Vec<Value> {
    std::fs::read_dir(root.join(".git/l7r-events"))
        .into_iter()
        .flatten()
        .flatten()
        .flat_map(|e| {
            std::fs::read_to_string(e.path())
                .unwrap_or_default()
                .lines()
                .filter_map(|l| serde_json::from_str::<Value>(l).ok())
                .collect::<Vec<_>>()
        })
        .filter(|v| v["ev"] == "Phase" && v["src"] == "land" && v["step"] == "end")
        .collect()
}

/// A landing of T1 by its whole door, its `end` written.
fn landing(fx: &Fx) -> Result<i32, String> {
    fx.land.landing(
        &fx.root.join("specs/449-x"),
        &["T1".to_owned()],
        NOTE,
        SystemTime::now(),
    )
}

#[test]
fn work_uncommitted_in_the_clone_lands_the_task_alone() {
    for (rc, code) in [(0, 0), (3, 3), (1, 1), (4, 4), (REFUSED_FIRST, 2)] {
        let fx = fx(&format!("land-alone-{rc}"));
        // the alone script is the stub, its line logged and answered
        std::fs::hard_link(
            fx.dir.join("tree/scripts/gates/l7r-gate.sh"),
            fx.dir.join("tree/scripts").join(SCRIPT),
        )
        .unwrap();
        put(&fx.root, "rust/other/half_done.rs", "another task's work");
        fx.answer("land-alone.sh 449-x T1", "rc", &rc.to_string());
        assert_eq!(landing(&fx), Ok(code));
        // nothing else ran in the clone
        assert_eq!(fx.log(), "land-alone.sh 449-x T1\n");
        assert!(fx.said().0.contains(
            "land: other work is uncommitted in the clone - T1 lands alone, its commit gated in the landing worktree (451 T88)"
        ));
        // the worktree's landing wrote its own `end` (here a stub's, none); a refusal before it ran is the clone's to write
        let ends = ends(&fx.root);
        if rc == REFUSED_FIRST {
            assert_eq!(ends.len(), 1, "{ends:?}");
            assert_eq!(ends[0]["code"], 2);
            assert_eq!(ends[0]["landed"], false);
        } else {
            assert!(ends.is_empty(), "{ends:?}");
        }
    }
}

#[test]
fn the_landing_worktree_s_own_run_is_never_sent_alone_again() {
    let mut fx = fx("land-alone-inner");
    fx.land.root = l7r_shared::env::Rooted::with(fx.root.clone(), &[(INNER, "1")]);
    put(&fx.root, "untracked.txt", "x");
    assert_eq!(landing(&fx), Ok(2));
    assert!(fx
        .said()
        .1
        .contains("uncommitted changes - commit them first"));
    assert!(!fx.log().contains("land-alone.sh"));
    assert_eq!(ends(&fx.root).len(), 1);
}

/// `scripts/land-alone.sh` itself, from the tree this crate is built in (its `Cargo.toml` declares the read).
fn script() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../scripts/land-alone.sh")
}

/// A shell line in `cwd`, its stdout; it must succeed.
fn sh(cwd: &Path, line: &str) -> String {
    let out = std::process::Command::new("bash")
        .args(["-c", line])
        .current_dir(cwd)
        .env("GIT_AUTHOR_NAME", "t")
        .env("GIT_AUTHOR_EMAIL", "t@t")
        .env("GIT_COMMITTER_NAME", "t")
        .env("GIT_COMMITTER_EMAIL", "t@t")
        .output()
        .unwrap();
    let err = String::from_utf8_lossy(&out.stderr);
    assert!(out.status.success(), "{line}: {err}");
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

const PLAN_TEXT: &str = "### T1 the section the tick moves\n\nT1's words.\n\n### T2 another builder's section\n\nT2's words.\n";

/// A clone of a bare origin, T1's file committed on its last landed tip; the stub `make` the landing worktree runs, which ticks T1
/// (plan.md's first line, tasks.md) and pushes, or exits `$STUB_RC`, logging its arguments and `L7R_LAND_ALONE`.
fn world(tag: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let dir = l7r_gate_core::ci::fixtures::scratch(tag);
    let c = dir.join("c");
    sh(
        &dir,
        "git init -q --bare -b main origin.git && git init -q -b main c",
    );
    put(&c, "specs/451-x/plan.md", PLAN_TEXT);
    put(&c, "specs/451-x/tasks.md", "- [ ] T1 one\n- [ ] T2 two\n");
    put(&c, "src/a.rs", "fn a() {}\n");
    sh(&c, "git add -A && git commit -qm base && git remote add origin ../origin.git && git push -q origin HEAD:main 2>/dev/null");
    put(&c, "src/t1.rs", "fn t1() {}\n");
    sh(&c, "git add src/t1.rs && git commit -qm 'T1 work'");
    put(&c, ".git/rust-checks/lint-land", "a kept result\n");
    put(
        &dir,
        "make",
        "#!/bin/bash\nprintf '%s|%s\\n' \"$L7R_LAND_ALONE\" \"$*\" >> \"$STUB_LOG\"\n[ -e src/other.rs ] && echo 'saw another task' >> \"$STUB_LOG\"\n[ -n \"$STUB_MID\" ] && bash -c \"$STUB_MID\"\n[ \"${STUB_RC:-0}\" = 0 ] || exit \"$STUB_RC\"\nsed -i 's/^### T1 the section the tick moves$/### T1 ticked/' specs/451-x/plan.md\nsed -i 's/^- \\[ \\] T1 one$/- [x] T1 one/' specs/451-x/tasks.md\ngit -c user.name=t -c user.email=t@t commit -qam 'T1 ticked' && git push -q origin HEAD:main 2>/dev/null\n",
    );
    sh(&dir, "chmod +x make && mkdir -p events");
    (dir, c)
}

/// The script run from the clone, as `l7r-gate land` runs it: (its exit, its stdout and stderr together).
fn alone(dir: &Path, c: &Path, env: &[(&str, &str)]) -> (i32, String) {
    let out = std::process::Command::new("bash")
        .arg(script())
        .args(["451-x", "T1"])
        .current_dir(c)
        .env("LAND_ALONE_TREE", dir.join("wt"))
        .env("LAND_ALONE_MAKE", dir.join("make"))
        .env("L7R_EVENTS_DIR", dir.join("events"))
        .env("STUB_LOG", dir.join("stub.log"))
        .env("LAND_NOTE", "checked")
        .envs(env.iter().copied())
        .output()
        .unwrap();
    (
        out.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&out.stdout).into_owned() + &String::from_utf8_lossy(&out.stderr),
    )
}

/// An edit line of the event log: `task`'s builder wrote `rel` of the clone.
fn edited(dir: &Path, c: &Path, task: &str, rel: &str) {
    let line = format!(
        r#"{{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","tool":"Edit","cat":"edit","path":"{}/{rel}","task":"{task}"}}"#,
        c.display()
    );
    let log = dir.join("events/451-x.jsonl");
    let old = std::fs::read_to_string(&log).unwrap_or_default();
    std::fs::write(log, format!("{old}{line}\n")).unwrap();
}

/// 451 T88: T1 lands from the landing worktree, at the clone's HEAD and apart from T2's uncommitted work; the clone takes the landed
/// tip, T2's new file untouched and its plan.md edit merged over the tick's.
#[test]
fn the_script_lands_the_clone_s_head_alone_and_the_clone_takes_the_tip() {
    let (dir, c) = world("alone-lands");
    put(&c, "src/other.rs", "T2's half-done file\n");
    put(
        &c,
        "specs/451-x/plan.md",
        &format!("{PLAN_TEXT}More of T2's words.\n"),
    );
    put(&c, "loose.txt", "a shell write no edit names\n");
    edited(&dir, &c, "T2", "src/other.rs");
    edited(&dir, &c, "T1", "src/t1.rs");
    let (rc, said) = alone(&dir, &c, &[]);
    assert_eq!(rc, 0, "{said}");
    assert_eq!(
        std::fs::read_to_string(dir.join("stub.log")).unwrap(),
        "1|--no-print-directory land F=451-x T=T1 NOTE=checked BOXES= COVER_OK=\n"
    );
    let left = said.contains("left uncommitted in the clone, not landed");
    assert!(left, "{said}");
    let listed = said.contains("loose.txt") && !said.contains("src/other.rs ");
    assert!(listed, "{said}");
    assert!(said.contains("the clone took"), "{said}");
    assert_eq!(
        sh(&c, "git rev-parse HEAD"),
        sh(&dir, "git -C origin.git rev-parse main")
    );
    assert_eq!(
        std::fs::read_to_string(c.join("src/other.rs")).unwrap(),
        "T2's half-done file\n"
    );
    let plan = std::fs::read_to_string(c.join("specs/451-x/plan.md")).unwrap();
    let merged = plan.starts_with("### T1 ticked\n") && plan.ends_with("More of T2's words.\n");
    assert!(merged, "{plan}");
    assert!(std::fs::read_to_string(c.join("specs/451-x/tasks.md"))
        .unwrap()
        .contains("- [x] T1 one"));
    assert_eq!(
        sh(&c, "git status --porcelain -uall"),
        "M specs/451-x/plan.md\n?? loose.txt\n?? src/other.rs"
    );
    let kept = sh(&dir, "git -C wt rev-parse --absolute-git-dir");
    assert!(Path::new(&kept).join("rust-checks/lint-land").is_file());
    // the worktree kept, moved to the next landing's HEAD
    put(&c, "src/t1b.rs", "fn t1b() {}\n");
    sh(&c, "git add src/t1b.rs && git commit -qm 'T1 more'");
    std::fs::remove_file(dir.join("stub.log")).unwrap();
    let (rc, said) = alone(&dir, &c, &[("STUB_RC", "1")]);
    assert_eq!(rc, 1, "{said}");
    assert!(dir.join("wt/src/t1b.rs").is_file());
    let exited = said.contains("the landing in the worktree exited 1");
    assert!(exited, "{said}");
}

/// 451 T88: T1's own edit still uncommitted is refused before anything runs; a landing whose tip conflicts with the clone's uncommitted
/// edit moves nothing; commits the clone made while the landing ran are merged with the tip.
#[test]
fn the_script_refuses_its_own_uncommitted_files_and_moves_nothing_on_a_conflict() {
    let (dir, c) = world("alone-refused");
    put(&c, "src/t1c.rs", "T1's own, uncommitted\n");
    edited(&dir, &c, "T1", "src/t1c.rs");
    let (rc, said) = alone(&dir, &c, &[]);
    assert_eq!(rc, REFUSED_FIRST, "{said}");
    let refused = said.contains("T1's own edits are uncommitted - commit them, then land again");
    assert!(refused, "{said}");
    assert!(said.contains("-- src/t1c.rs"), "{said}");
    assert!(!dir.join("stub.log").exists());
    std::fs::remove_file(c.join("src/t1c.rs")).unwrap();
    // the tick's line and the clone's edit of it conflict: landed, the clone left as it was
    let before = sh(&c, "git rev-parse HEAD");
    let edit = PLAN_TEXT.replace("### T1 the section the tick moves", "### T1 another edit");
    put(&c, "specs/451-x/plan.md", &edit);
    let (rc, said) = alone(&dir, &c, &[]);
    assert_eq!(rc, 4, "{said}");
    assert!(said.contains("conflict"), "{said}");
    assert_eq!(sh(&c, "git rev-parse HEAD"), before);
    assert_eq!(
        std::fs::read_to_string(c.join("specs/451-x/plan.md")).unwrap(),
        edit
    );
    // a commit in the clone while the landing ran: the clone takes a merge of the two
    put(&c, "specs/451-x/plan.md", PLAN_TEXT);
    sh(&c, "git checkout -q -- specs/451-x/plan.md");
    put(&dir, "t2.rs", "fn t2() {}\n");
    let mid = format!("cp {0}/t2.rs {1}/src/t2.rs && git -C {1} add src/t2.rs && git -C {1} -c user.name=t -c user.email=t@t commit -qm 'T2 work'", dir.display(), c.display());
    sh(&c, "git reset -q --hard HEAD && git -C ../origin.git update-ref refs/heads/main $(git rev-parse HEAD~0)");
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 0, "{said}");
    // a merge: HEAD has two parents
    assert_eq!(
        sh(&c, "git rev-list --parents -n1 HEAD").split(' ').count(),
        3
    );
    assert!(c.join("src/t2.rs").is_file());
    assert!(std::fs::read_to_string(c.join("specs/451-x/plan.md"))
        .unwrap()
        .starts_with("### T1 ticked\n"));
}
