//! The decider on the suite's shapes (`tests/hooks/test-clone-sync-hooks.sh`, replayed through the shim, is the verdict). Each world
//! is a mirror with one commit and a clone of it, copied from one template by one `cp -a` so a test starts no `git clone` and this
//! process never holds a world's script open for writing (451 T263, at `copy`); the tree's tools are `sh` fakes, steered by marker files.

use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use serde_json::{json, Value};

use super::{
    both, decide, forbidden, forked_from, judge, notes, parked_by, sid_is_live, tail, Ctx,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::{ask, Said};

fn git(dir: &Path, args: &[&str]) -> Said {
    let d = dir.to_string_lossy();
    let all: Vec<&str> = [
        "-C",
        d.as_ref(),
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
    ]
    .into_iter()
    .chain(args.iter().copied())
    .collect();
    ask(Path::new("/"), "git", &all, "")
}

fn script(p: &Path, body: &str) {
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    crate::guards::write_executable(p, &format!("#!/bin/sh\n{body}\n"));
}

/// `from`'s contents copied into `to` by one `cp -a`, a child of its own, never by this process.
///
/// WHY (451 T263): the copy was `std::fs::copy` a file, which holds each destination open for writing in THIS process while it is
/// written. A thread that forks in another test copies every open descriptor until its child execs (`write_executable`'s hazard), so a
/// child forked during the copy of `scripts/sync-with-main.sh` and slow to its exec still held the script open for writing when the hook
/// ran it: the run failed with "Text file busy", `ask` gave code -1 and no output, and the mid-task notice ended `mirror refresh FAILED: `
/// with nothing after it, where the test read `mirror refreshed from GitHub main` (once in 449/451's landing gate, 2026-11-26; forced red
/// that day by a `sleep` child handed the copied script open for append). `cp` holds the only descriptors that write a world's files,
/// and it has exited by the time this returns. Do not copy a world's scripts in-process again.
fn copy(from: &Path, to: &Path) {
    let done = std::process::Command::new("cp")
        .arg("-a")
        .arg(from.join("."))
        .arg(to)
        .status();
    assert!(done.unwrap().success());
}

/// The template, made once: `diagram` (one commit, `origin/main` at it) and its clone `.clones/mine`, the fakes beside them.
fn template() -> &'static PathBuf {
    static T: OnceLock<PathBuf> = OnceLock::new();
    T.get_or_init(|| {
        // one template for the process, in its shared directory (`beside_binary`): a static is never dropped to remove a `TempDir`, so it
        // goes with the run's own temp directory (feature 449 T101)
        let root = crate::shared::tempdir::beside_binary("guard-cs-template");
        let main = root.join("diagram");
        std::fs::create_dir_all(&main).unwrap();
        std::fs::write(main.join(".gitignore"), ".clones/\n").unwrap();
        git(&main, &["init", "-q", "-b", "main"]);
        git(&main, &["add", ".gitignore"]);
        git(&main, &["commit", "-q", "-m", "one"]);
        git(&main, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
        let clone = main.join(".clones/mine");
        let (m, c) = (main.to_string_lossy(), clone.to_string_lossy());
        assert!(ask(Path::new("/"), "git", &["clone", "-q", &m, &c], "").ok());
        // `.claude/settings.local.json`: git ignores it in the real repository, and the hook writes it on every prompt
        std::fs::write(clone.join(".git/info/exclude"), "scripts/\n.making\n.claude/settings.local.json\n").unwrap();
        // the clone's sync: its output, its exit from `.git/sync-rc`, a fast-forward when `.git/sync-ff` is there
        script(
            &clone.join("scripts/sync-with-main.sh"),
            "echo 'sync-with-main: NOTE kept'; echo said >&2\n[ -f .git/sync-ff ] && git fetch -q origin && git merge -q --ff-only FETCH_HEAD\nexit $(cat .git/sync-rc 2>/dev/null || echo 0)",
        );
        let tree = root.join("tree");
        script(&tree.join("scripts/gates/l7r-gate.sh"), "[ -f .making ]");
        script(&tree.join("scripts/reviews/layout_carry.sh"), "echo carried");
        root
    })
}

/// A world of its own, copied from the template.
struct World {
    main: PathBuf,
    clone: PathBuf,
    tree: PathBuf,
    sessions: PathBuf,
    _root: crate::shared::tempdir::TempDir,
}

impl World {
    fn new(tag: &str) -> Self {
        crate::shared::log::quiet();
        let root = crate::shared::tempdir::TempDir::new(&format!("guard-cs-{tag}"));
        copy(template(), &root);
        let main = root.join("diagram");
        let sessions = root.join("sessions");
        std::fs::create_dir_all(&sessions).unwrap();
        let clone = main.join(".clones/mine");
        git(
            &clone,
            &["remote", "set-url", "origin", &main.to_string_lossy()],
        );
        Self {
            clone,
            tree: root.join("tree"),
            main,
            sessions,
            _root: root,
        }
    }

    /// Main moves on a commit the clone does not have; `origin` follows unless the commit is a stray.
    fn advance(&self, file: &str, stray: bool) {
        std::fs::create_dir_all(self.main.join(file).parent().unwrap()).unwrap();
        std::fs::write(self.main.join(file), "x").unwrap();
        git(&self.main, &["add", file]);
        git(&self.main, &["commit", "-q", "-m", "two"]);
        if !stray {
            git(
                &self.main,
                &["update-ref", "refs/remotes/origin/main", "HEAD"],
            );
        }
        git(&self.clone, &["fetch", "-q", "origin"]);
    }

    /// Main moves on one commit per file, `origin` following, the clone fetching once (feature 449 T167: a fetch a commit was the
    /// test's time against FR-008's tenth of a second).
    fn advance_all(&self, files: &[&str]) {
        for file in files {
            std::fs::create_dir_all(self.main.join(file).parent().unwrap()).unwrap();
            std::fs::write(self.main.join(file), "x").unwrap();
            git(&self.main, &["add", file]);
            git(&self.main, &["commit", "-q", "-m", file]);
        }
        git(
            &self.main,
            &["update-ref", "refs/remotes/origin/main", "HEAD"],
        );
        git(&self.clone, &["fetch", "-q", "origin"]);
    }

    fn claim(&self, sid: &str, clone: &Path) {
        let map = self.main.join(".clones/.session-clones");
        std::fs::create_dir_all(&map).unwrap();
        std::fs::write(map.join(sid), clone.to_string_lossy().as_bytes()).unwrap();
    }

    /// A transcript whose last `/rename` names the session `title`.
    fn titled(&self, title: &str) -> String {
        let t = self.sessions.join(format!("{title}.jsonl"));
        std::fs::write(
            &t,
            json!({"type": "custom-title", "customTitle": title}).to_string(),
        )
        .unwrap();
        t.to_string_lossy().into_owned()
    }

    fn session(&self, input: &Value) -> Session {
        let (m, s) = (
            self.main.to_string_lossy().into_owned(),
            self.sessions.to_string_lossy().into_owned(),
        );
        Session::with_env(input, |k| match k {
            "CLONE_MAIN" => Some(m.clone()),
            "CLONE_SESSIONS_DIR" => Some(s.clone()),
            _ => None,
        })
    }

    fn run(&self, name: &str, input: Value) -> Vec<Answer> {
        let session = self.session(&input);
        let event = Event {
            name: name.to_owned(),
            input,
        };
        judge(&Ctx {
            event: &event,
            session: &session,
            main: self.main.clone(),
            tree: self.tree.clone(),
            solo_forced: Some(
                if self.tree.join("scripts/hooks/lib/solo").exists() {
                    "1"
                } else {
                    "0"
                }
                .to_owned(),
            ),
        })
    }

    fn edit(&self, sid: &str, transcript: &str, path: &Path) -> Vec<Answer> {
        self.run(
            "PreToolUse",
            json!({"session_id": sid, "transcript_path": transcript, "tool_name": "Write", "tool_input": {"file_path": path.to_string_lossy()}}),
        )
    }

    fn prompt(&self, sid: &str, transcript: &str) -> String {
        let got = self.run(
            "UserPromptSubmit",
            json!({"session_id": sid, "transcript_path": transcript}),
        );
        if let [Answer::Print(s)] = &got[..] {
            s.clone()
        } else {
            assert!(got.is_empty());
            String::new()
        }
    }
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(w)] if w.contains(words))
}

fn told(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Notice(w)] if w.contains(words))
}

#[test]
fn an_edit_outside_a_clone_or_into_a_dirty_one_is_let_through() {
    let w = World::new("through");
    let me = w.titled("mine");
    assert!(w.edit("s", &me, &w.main.join("a.txt")).is_empty());
    assert!(w.edit("s", &me, &w.main.join(".clones/mine/")).is_empty());
    assert!(w
        .edit("s", &me, &w.main.join(".clones/ghost/a.txt"))
        .is_empty());
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    assert!(w.edit("s", &me, &w.clone.join("a.txt")).is_empty());
    let claimed = std::fs::read_to_string(w.main.join(".clones/.session-clones/s")).unwrap();
    assert_eq!(claimed, w.clone.to_string_lossy());
}

#[test]
fn a_forbidden_name_or_another_sessions_clone_is_refused() {
    let w = World::new("names");
    let a = w.clone.join("a.txt");
    assert!(refused(
        &w.edit("s", &w.titled("gm-assistant"), &a),
        "has no distinct name"
    ));
    let gm = w.main.join(".clones/gm-assistant");
    std::fs::create_dir_all(gm.join(".git")).unwrap();
    assert!(refused(&w.edit("s", "", &gm.join("a.txt")), "is a FORBIDDEN clone name (a repository's name, not a session). Work in .clones/<your-session-name>."));
    assert!(refused(
        &w.edit("s", &w.titled("other"), &gm.join("a.txt")),
        "(this session resolves to"
    ));
    assert!(refused(
        &w.edit("s", &w.titled("other"), &a),
        "this session's clone is"
    ));
    assert!(forbidden(&w.main, &w.main) && !forbidden(&w.clone, &w.main));
}

#[test]
fn a_clone_another_live_session_claims_is_refused() {
    let w = World::new("live");
    let mut other = fake(&["claude"]);
    std::fs::write(
        w.sessions.join(format!("{}.json", other.id())),
        json!({"sessionId": "them"}).to_string(),
    )
    .unwrap();
    std::fs::write(
        w.sessions.join("x.json"),
        json!({"sessionId": "nopid"}).to_string(),
    )
    .unwrap();
    std::fs::write(w.sessions.join("bad.json"), "{").unwrap();
    w.claim("them", &w.clone);
    w.claim(".hidden", &w.clone);
    let got = w.edit("s", "", &w.clone.join("a.txt"));
    let _ = other.kill();
    let _ = other.wait();
    assert!(refused(
        &got,
        "already occupied by another live session (them)"
    ));
    assert!(!sid_is_live("nopid", &w.sessions) && !sid_is_live("them", Path::new("/nowhere")));
    assert!(w.edit("", "", &w.clone.join("a.txt")).is_empty());
}

/// A stand-in session: a process running `sh -c 'read _' <args...>`, returned once its own command line shows (a spawned child
/// carries its parent's until it execs: on a loaded host the guard would read "not claude").
///
/// It waits on a pipe this test holds, in the shell itself, and so ends at the test's `kill`, or with the pipe when a test panics
/// before it. Do not make it wait in a `sleep` again (451 T340): `sh -c 'sleep 5; :'` kept the arguments by not exec'ing, so the
/// `sleep` was the shell's child, and a `kill` of the shell left it behind with the test binary's stdout and stderr - nine a run,
/// each holding the gate's read of the run open until its 5 s were up, where the tests end in 2.
fn fake(args: &[&str]) -> std::process::Child {
    let child = std::process::Command::new("sh")
        .args(["-c", "read _"])
        .args(args)
        .stdin(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    let cmdline = format!("/proc/{}/cmdline", child.id());
    let _ = (0..1000).find(|_| {
        std::thread::sleep(std::time::Duration::from_millis(2));
        std::fs::read_to_string(&cmdline).is_ok_and(|c| c.contains("claude"))
    });
    child
}

/// A stand-in session starts no process of its own (451 T340): one that did (`sleep 5; :`, nine a run) left it behind at the kill,
/// holding the test run's output open for 5 s where the tests end in 2.
#[test]
fn a_stand_in_session_starts_no_process_of_its_own() {
    let mut session = fake(&["claude"]);
    let pid = session.id();
    let children = std::fs::read_to_string(format!("/proc/{pid}/task/{pid}/children"));
    let _ = session.kill();
    let _ = session.wait();
    assert_eq!(children.unwrap(), "");
}

#[test]
fn a_forked_background_session_shares_its_launchers_clone() {
    // feature 449 T162: a background job runs as `--fork-session --resume <parent>`; the parent claims the clone and is live
    let w = World::new("forked");
    let mut parent = fake(&["claude"]);
    let mut child = fake(&["claude", "--fork-session", "--resume", "/p/them.jsonl"]);
    let mut stranger = fake(&["claude", "--resume", "/p/them.jsonl"]);
    for (pid, sid) in [
        (parent.id(), "them"),
        (child.id(), "s"),
        (stranger.id(), "t"),
    ] {
        std::fs::write(
            w.sessions.join(format!("{pid}.json")),
            // named for the clone, as a session working in it is
            json!({"sessionId": sid, "name": w.clone.file_name().unwrap().to_string_lossy()})
                .to_string(),
        )
        .unwrap();
    }
    w.claim("them", &w.clone);
    // the stranger first: the forked session's own edit claims the clone for it too
    let not_forked = w.edit("t", "", &w.clone.join("a.txt"));
    let forked = w.edit("s", "", &w.clone.join("a.txt"));
    assert_eq!(forked_from("s", &w.sessions), "them");
    assert_eq!(forked_from("t", &w.sessions), "");
    assert_eq!(forked_from("nobody", &w.sessions), "");
    for p in [&mut parent, &mut child, &mut stranger] {
        let _ = p.kill();
        let _ = p.wait();
    }
    assert!(!refused(&forked, "already occupied"), "{forked:?}");
    assert!(refused(
        &not_forked,
        "already occupied by another live session (them)"
    ));
}

#[test]
fn a_parked_background_job_shares_its_parkers_clone() {
    // feature 451 T62: a job Claude Code runs in the background is `claude bg-spare`, whose command line names no parent; its record
    // is `kind: bg` with a `jobId`, and the live session it was parked from names that job as its own record's `parkedJobId`
    let w = World::new("parked");
    let name = w.clone.file_name().unwrap().to_string_lossy().into_owned();
    let spare = ["claude", "bg-spare", "--bg-spare", "/tmp/x.claim.sock"];
    let mut procs = Vec::new();
    for (args, rec) in [
        // the claimant, which parked job j1; `u` parked j2 and claims nothing; `v`'s job j3 was parked by no one
        (
            &["claude"][..],
            json!({"sessionId": "them", "kind": "interactive", "parkedJobId": "j1"}),
        ),
        (
            &spare[..],
            json!({"sessionId": "s", "kind": "bg", "jobId": "j1"}),
        ),
        (
            &["claude"][..],
            json!({"sessionId": "u", "kind": "interactive", "parkedJobId": "j2"}),
        ),
        (
            &spare[..],
            json!({"sessionId": "t", "kind": "bg", "jobId": "j2"}),
        ),
        (
            &spare[..],
            json!({"sessionId": "v", "kind": "bg", "jobId": "j3"}),
        ),
    ] {
        let p = fake(args);
        let mut rec = rec;
        rec["name"] = json!(name);
        std::fs::write(w.sessions.join(format!("{}.json", p.id())), rec.to_string()).unwrap();
        procs.push(p);
    }
    w.claim("them", &w.clone);
    // the refused first: an edit let through claims the clone for its session too
    let parked_elsewhere = w.edit("t", "", &w.clone.join("a.txt"));
    let parked_by_none = w.edit("v", "", &w.clone.join("a.txt"));
    let parked = w.edit("s", "", &w.clone.join("a.txt"));
    assert_eq!(parked_by("s", &w.sessions), "them");
    assert_eq!(parked_by("t", &w.sessions), "u");
    // no one parked j3; `them` has no job, and an empty job must not match the records that parked nothing
    for sid in ["v", "them", "nobody", ""] {
        assert_eq!(parked_by(sid, &w.sessions), "", "{sid}");
    }
    assert_eq!(parked_by("s", Path::new("/nowhere")), "");
    for p in &mut procs {
        let _ = p.kill();
        let _ = p.wait();
    }
    assert!(!refused(&parked, "already occupied"), "{parked:?}");
    // one line each: a message argument on a line of its own is a line only a failure reaches
    let occupied = "already occupied by another live session (them)";
    for got in [&parked_elsewhere, &parked_by_none] {
        assert!(refused(got, occupied), "{got:?}");
    }
}

/// The transcript reads one Edit of `a.txt` in the clone makes (`Session::reads`).
fn edit_reads(w: &World, transcript: &str) -> u32 {
    let input = json!({"session_id": "s", "transcript_path": transcript, "tool_name": "Edit", "tool_input": {"file_path": w.clone.join("a.txt").to_string_lossy()}});
    let session = w.session(&input);
    let event = Event {
        name: "PreToolUse".to_owned(),
        input,
    };
    let got = judge(&Ctx {
        event: &event,
        session: &session,
        main: w.main.clone(),
        tree: w.tree.clone(),
        solo_forced: Some("0".to_owned()),
    });
    assert!(got.is_empty(), "{got:?}");
    session.reads.get()
}

/// 451 T384: a dirty clone's Edit is let through without the session's name, so it reads no transcript (the name was asked first:
/// one read, the whole transcript where it holds no `/rename`); a clean clone's still asks it, to judge where the edit is routed.
#[test]
fn a_dirty_clones_edit_reads_no_transcript() {
    let w = World::new("lazy-name");
    let me = w.titled("mine");
    assert!(edit_reads(&w, &me) >= 1);
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    assert_eq!(edit_reads(&w, &me), 0);
}

#[test]
fn a_clean_clone_on_main_is_claimed_and_one_behind_a_stray_is_refused() {
    let w = World::new("stray");
    assert!(w.edit("s", "", &w.clone.join("a.txt")).is_empty());
    w.advance("b.txt", true);
    assert!(refused(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "is carrying a commit GitHub main does not have"
    ));
}

#[test]
fn a_clone_behind_under_a_make_or_a_gate_lock_waits() {
    let w = World::new("running");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".making"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "but a make runs in it"
    ));
    std::fs::remove_file(w.clone.join(".making")).unwrap();
    script(
        &w.clone.join("scripts/gates/l7r-gate.sh"),
        "[ -f \"$3/held\" ]",
    );
    std::fs::write(w.clone.join(".git/held"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "but a make runs in it"
    ));
}

#[test]
fn a_clone_behind_that_cannot_fast_forward_is_refused() {
    let w = World::new("ff");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(refused(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "has a clean tree (a new work unit) but its HEAD is behind main"
    ));
}

#[test]
fn a_clone_behind_is_fast_forwarded() {
    let w = World::new("ff-ok");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".git/sync-ff"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "so main was merged in"
    ));
}

#[test]
fn a_mirror_with_no_head_judges_nothing() {
    let bare = World::new("bare");
    std::fs::remove_dir_all(bare.main.join(".git")).unwrap();
    assert!(bare.edit("s", "", &bare.clone.join("a.txt")).is_empty());
}

#[test]
fn a_dirty_clones_test_run_behind_main_is_told_why() {
    let w = World::new("behind");
    let make = |cmd: &str, tool: &str| {
        w.run(
            "PreToolUse",
            json!({"session_id": "s", "tool_name": tool, "tool_input": {"command": cmd}}),
        )
    };
    assert!(make("make quick", "Bash").is_empty());
    w.claim("s", &w.clone);
    assert!(make("make quick", "Bash").is_empty());
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    assert!(make("make quick", "Bash").is_empty());
    assert!(make("make lines", "Bash").is_empty());
    assert!(make("make quick", "Read").is_empty());
}

/// A dirty clone of its own, claimed by session `s`, main moved on by `files`; `make` runs a Bash command there.
fn dirty_behind(tag: &str, files: &[&str]) -> World {
    let w = World::new(tag);
    w.claim("s", &w.clone);
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    w.advance_all(files);
    w
}

fn make_in(w: &World, cmd: &str) -> Vec<Answer> {
    w.run(
        "PreToolUse",
        json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": cmd}}),
    )
}

/// The second half of `a_dirty_clones_test_run_behind_main_is_told_why`, split from it and in two to keep each under FR-008's tenth
/// of a second (feature 449 T167): the clone dirty and main one engine commit on, the run is told its paths are engine paths.
#[test]
fn a_dirty_clones_test_run_behind_main_is_told_its_engine_paths() {
    let w = dirty_behind("behind-engine", &["l7r/x.py"]);
    assert!(told(&make_in(&w, "make quick"), "are ENGINE paths"));
}

/// Main two commits on, one of them engine: `make done` is told both counts (feature 449 T167, split as above).
#[test]
fn a_dirty_clones_done_two_commits_behind_is_told_how_many_are_engine() {
    let w = dirty_behind("behind-two", &["l7r/x.py", "docs/y.md"]);
    let got = make_in(&w, "make done");
    assert!(told(&got, "main has 2 commit(s)") && told(&got, "1 changed file(s) are ENGINE"));
}

#[test]
fn a_dirty_clones_run_behind_on_docs_alone_is_told_it_is_cheap() {
    let clean = World::new("behind-clean");
    clean.claim("s", &clean.clone);
    std::fs::write(clean.clone.join("wip.txt"), "x").unwrap();
    clean.advance("docs/y.md", false);
    let quick = clean.run(
        "PreToolUse",
        json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}}),
    );
    assert!(told(&quick, "no changed file is an engine path"));
    git(
        &clean.main,
        &["commit", "-q", "--allow-empty", "-m", "unfetched"],
    );
    git(
        &clean.main,
        &["update-ref", "refs/remotes/origin/main", "HEAD"],
    );
    let unfetched = clean.run(
        "PreToolUse",
        json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}}),
    );
    assert!(told(&unfetched, "main has new commit(s)"));
    git(
        &clean.main,
        &["update-ref", "-d", "refs/remotes/origin/main"],
    );
    assert!(clean
        .run(
            "PreToolUse",
            json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}})
        )
        .is_empty());
}

#[test]
fn an_unnamed_session_is_told_once() {
    let w = World::new("unnamed");
    assert!(w.prompt("", "").is_empty());
    assert!(w.prompt("s", "").contains("does not resolve"));
    assert!(w.prompt("s", "").is_empty());
    assert!(w
        .prompt("g", &w.titled("diagram"))
        .contains("resolves to the FORBIDDEN '.clones/diagram'"));
    assert!(w.prompt("n", &w.titled("mine")).is_empty());
    w.claim("gone", &w.main.join(".clones/ghost"));
    assert!(w.prompt("gone", "").is_empty());
}

#[test]
fn an_unchanged_mid_task_notice_is_said_once_then_in_one_line() {
    // 451 T170: the coordinator's 1,870 prompts each carried the 172-character mid-task notice, measured 2026-11-23
    let w = World::new("midtask-once");
    w.claim("s", &w.clone);
    std::fs::write(w.clone.join("wip.txt"), "mid-task").unwrap();
    let full = w.prompt("s", "");
    assert!(full.contains("has uncommitted work (mid-task) - clone merge skipped; mirror refreshed from GitHub main. Finish and run"), "{full}");
    let again = w.prompt("s", "");
    let first = again.lines().next().unwrap();
    let short = first.starts_with("clone-sync: still mid-task since ")
        && first.ends_with(", merge skipped");
    assert!(short && first.len() < 60, "{again}");
    // another session in the same clone is told in full
    w.claim("t", &w.clone);
    assert!(w.prompt("t", "").contains("Finish and run"));
    // a compaction, a clear or a resume forgets it: the next prompt says it in full
    assert!(w
        .run(
            "SessionStart",
            json!({"session_id": "s", "source": "startup"})
        )
        .is_empty());
    assert!(w.prompt("s", "").contains("clone-sync: still mid-task"));
    assert!(w
        .run(
            "SessionStart",
            json!({"session_id": "s", "source": "compact"})
        )
        .is_empty());
    assert!(w.prompt("s", "").contains("Finish and run"));
    // a failed refresh is said in full, and so is the notice after it
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(w.prompt("s", "").contains("mirror refresh FAILED"));
    std::fs::remove_file(w.clone.join(".git/sync-rc")).unwrap();
    assert!(w.prompt("s", "").contains("Finish and run"));
    // a session with no clone, or an unnamed one, starts with nothing to forget
    assert!(w
        .run(
            "SessionStart",
            json!({"session_id": "nobody", "source": "compact"})
        )
        .is_empty());
    assert!(w
        .run("SessionStart", json!({"source": "compact"}))
        .is_empty());
}

/// A sync script that cannot START is said as that, with the reason the system gave (451 T268): the notice ended `FAILED: ` with
/// nothing after it, the same words a script that ran and failed without output gets. The script is made unstartable with no race:
/// not executable, then missing.
#[test]
fn a_sync_script_that_cannot_start_is_said_with_the_reason() {
    use std::os::unix::fs::PermissionsExt as _;
    let w = World::new("unstartable");
    w.claim("s", &w.clone);
    let script = w.clone.join("scripts/sync-with-main.sh");
    std::fs::set_permissions(&script, std::fs::Permissions::from_mode(0o644)).unwrap();
    std::fs::write(w.clone.join(".making"), "").unwrap();
    // what the notice says after the clone's path and its ` - `
    let after = || {
        let said = w.prompt("s", "");
        said.split_once(" - ").unwrap().1.to_owned()
    };
    assert_eq!(
        after(),
        "clone merge skipped; mirror refresh FAILED: scripts/sync-with-main.sh could not be started (Permission denied (os error 13))"
    );
    std::fs::remove_file(w.clone.join(".making")).unwrap();
    // a script that ran, failed and said nothing says its exit, and one a signal ended that it gave none
    let resolve = "resolve before modifying the repo: scripts/sync-with-main.sh";
    std::fs::remove_file(&script).unwrap();
    self::script(&script, "exit 7");
    assert_eq!(after(), format!("{resolve} exited 7 and said nothing"));
    std::fs::remove_file(&script).unwrap();
    self::script(&script, "kill -9 $$");
    assert_eq!(
        after(),
        format!("{resolve} said nothing and gave no exit code (a signal ended it?)")
    );
    std::fs::remove_file(&script).unwrap();
    let said = w.prompt("s", "");
    assert!(said.starts_with("clone-sync: auto sync-in FAILED in "));
    assert_eq!(
        after(),
        format!("{resolve} could not be started (No such file or directory (os error 2))")
    );
}

#[test]
fn a_mid_task_prompt_refreshes_only_the_mirror() {
    let w = World::new("midtask");
    w.claim("s", &w.clone);
    std::fs::create_dir_all(w.clone.join(".specify")).unwrap();
    std::fs::write(w.clone.join(".specify/feature.json"), "{}").unwrap();
    git(&w.clone, &["add", "-f", ".specify/feature.json"]);
    let said = w.prompt("s", "");
    assert!(
        said.contains("feature.json is TRACKED again")
            && said.contains(
                "has uncommitted work (mid-task) - clone merge skipped; mirror refreshed"
            )
            && said.ends_with("sync-with-main: NOTE kept")
    );
    assert!(!w.prompt("s", "").contains("TRACKED"));
    git(&w.clone, &["rm", "-q", "--cached", ".specify/feature.json"]);
    std::fs::remove_dir_all(w.clone.join(".specify")).unwrap();
    std::fs::write(w.clone.join(".making"), "").unwrap();
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(w.prompt("s", "").contains("has a make run going (a gate or a roll) - clone merge skipped; mirror refresh FAILED: said"));
    std::fs::remove_file(w.clone.join(".making")).unwrap();
    std::fs::remove_file(w.clone.join(".git/sync-rc")).unwrap();
    script(
        &w.clone.join("scripts/gates/l7r-gate.sh"),
        "[ -f \"$3/held\" ]",
    );
    std::fs::write(w.clone.join(".git/held"), "").unwrap();
    std::fs::create_dir_all(w.tree.join("scripts/l7r/diagram")).unwrap();
    std::fs::write(w.tree.join("scripts/l7r/diagram/__init__.py"), "").unwrap();
    std::fs::create_dir_all(w.clone.join(".claude/skills/diagram")).unwrap();
    std::fs::write(w.clone.join(".claude/skills/diagram/Makefile"), "").unwrap();
    git(&w.clone, &["add", "-f", ".claude/skills/diagram/Makefile"]);
    let old = w.prompt("s", "");
    assert!(old.contains("has uncommitted work") && old.contains("still on the old layout"));
    git(
        &w.clone,
        &["rm", "-q", "--cached", ".claude/skills/diagram/Makefile"],
    );
    std::fs::remove_dir_all(w.clone.join(".claude")).unwrap();
    assert!(w.prompt("s", "").contains("holds a running gate's lock"));
}

#[test]
fn an_idle_prompt_syncs_the_clone_unless_it_is_the_only_session() {
    let w = World::new("idle");
    w.claim("s", &w.clone);
    assert_eq!(
        w.prompt("s", ""),
        format!(
            "clone-sync: auto-synced {} with main (git)\ncarried\nsync-with-main: NOTE kept",
            w.clone.display()
        )
    );
    // the merge leaves its one usage line in the clone's own repository (feature 449 T129)
    let usage = std::fs::read_to_string(w.clone.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage
        .contains("\"tool\": \"clone-sync-merge\", \"kind\": \"step\", \"outcome\": \"changed\""));
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(w
        .prompt("s", "")
        .ends_with("resolve before modifying the repo: sync-with-main: NOTE kept\nsaid"));
    std::fs::create_dir_all(w.tree.join("scripts/hooks/lib")).unwrap();
    std::fs::write(w.tree.join("scripts/hooks/lib/solo"), "").unwrap();
    assert!(w.prompt("s", "").is_empty());
}

#[test]
fn the_helpers_and_the_entry() {
    assert_eq!(tail("a\nb\nc", 2), "b\nc");
    assert_eq!(
        notes("x\nsync-with-main: WARNING w\nsync-with-main: NOTE n"),
        ["sync-with-main: WARNING w", "sync-with-main: NOTE n"]
    );
    assert_eq!(
        both(&Said {
            code: 0,
            out: String::new(),
            err: "e".into()
        }),
        "e"
    );
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

/// The list is a cache of the Makefile's test targets, not a roster to trust: a name no target bears notices nothing (feature 449 T213
/// found eight such names, five of them pytest's).
#[test]
fn every_test_target_named_is_a_target_of_the_makefile() {
    let makefile =
        std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../Makefile")).unwrap();
    let missing: Vec<&&str> = super::BEHIND_TEST_TARGETS
        .iter()
        .filter(|t| !makefile.lines().any(|l| l.starts_with(&format!("{t}:"))))
        .collect();
    assert_eq!(missing, Vec::<&&str>::new());
}
