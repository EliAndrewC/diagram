//! One pass on fixtures: real git repositories, the registry's pid this process, tmux a recording `sh` script.
//! (`tests/hooks/test-stall-watchdog-hooks.sh`, replayed through the shim, is the verdict.)

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    asking_gm, clone_of, host_pane, human, in_retry_wait, input_empty, judge, live_sessions, now,
    resume_command, run_pass, unfinished, Paths,
};
use crate::shared::tool::ask;

fn git(dir: &Path, args: &[&str]) {
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
    assert!(ask(Path::new("/"), "git", &all, "").ok());
}

struct World {
    root: PathBuf,
    clone: PathBuf,
    p: Paths,
}

/// A mirror on main, a clone of it, an empty registry and projects, a fake tmux and a fake `finished-run-hooks.sh`.
fn world(tag: &str) -> World {
    let root = std::env::temp_dir().join(format!("l7r-guard-pass-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&root);
    let (mirror, clone) = (root.join("mirror"), root.join("clone"));
    for d in [
        &mirror,
        &root.join("sessions"),
        &root.join("projects/p"),
        &root.join("map"),
        &root.join("tree/scripts/hooks"),
    ] {
        std::fs::create_dir_all(d).unwrap();
    }
    git(&mirror, &["init", "-q", "-b", "main"]);
    git(&mirror, &["commit", "-q", "--allow-empty", "-m", "one"]);
    let (from, to) = (mirror.to_string_lossy(), clone.to_string_lossy());
    assert!(ask(Path::new("/"), "git", &["clone", "-q", &from, &to], "").ok());
    let base = root.display().to_string();
    std::fs::write(root.join("tmux"), format!("case \"$1\" in display) touch {base}/tty-$4; echo {base}/tty-$4 ;; capture-pane) cat {base}/screen 2>/dev/null ;; send-keys) echo \"$*\" >> {base}/sent ;; esac\n")).unwrap();
    let r = root.clone();
    let mut p = Paths::from_env(&|_| None);
    p.sessions = r.join("sessions");
    p.projects = r.join("projects");
    p.state = r.join("state");
    p.clones = r.join("map");
    p.mirror = r.join("mirror");
    p.tmux = vec![
        "sh".to_owned(),
        r.join("tmux").to_string_lossy().into_owned(),
    ];
    World { root, clone, p }
}

impl World {
    /// A live registry entry (this process's pid), claimed by the clone, last active `age` seconds ago.
    fn session(&self, sid: &str, extra: &Value, age: u64) -> Value {
        let mut e = json!({"pid": std::process::id(), "sessionId": sid, "name": format!("name-{sid}"), "kind": "interactive", "status": "idle"});
        for (k, v) in extra.as_object().unwrap() {
            e[k.as_str()] = v.clone();
        }
        std::fs::write(self.p.sessions.join(format!("{sid}.json")), e.to_string()).unwrap();
        std::fs::write(
            self.p.clones.join(sid),
            self.clone.to_string_lossy().as_bytes(),
        )
        .unwrap();
        let t = self.root.join(format!("projects/p/{sid}.jsonl"));
        std::fs::write(
            &t,
            "{\"type\":\"assistant\",\"message\":{\"content\":[]}}\n",
        )
        .unwrap();
        let f = std::fs::File::options().write(true).open(&t).unwrap();
        f.set_modified(std::time::SystemTime::now() - std::time::Duration::from_secs(age))
            .unwrap();
        e
    }

    fn dirty(&self) {
        std::fs::write(self.clone.join("work.txt"), "x").unwrap();
    }

    fn screen(&self, input: &str) {
        let rule = "─".repeat(20);
        std::fs::write(
            self.root.join("screen"),
            format!("out\n{rule}\n{input}\n{rule}\nstatus\n"),
        )
        .unwrap();
    }

    fn sent(&self) -> String {
        std::fs::read_to_string(self.root.join("sent")).unwrap_or_default()
    }
}

#[test]
fn the_paths_come_from_the_environment() {
    let p = Paths::from_env(&|k| match k {
        "HOME" => Some("/h".to_owned()),
        "STALL_AFTER" => Some("5".to_owned()),
        "STALL_DRYRUN" => Some("1".to_owned()),
        "STALL_MIRROR" => Some("/m".to_owned()),
        _ => None,
    });
    assert!(
        p.sessions == Path::new("/h/.claude/sessions")
            && p.mirror == Path::new("/m")
            && p.proc == Path::new("/proc")
            && p.dry
    );
    assert!((p.stall_after - 5.0).abs() < 1e-9 && p.tmux == ["tmux"]);
    assert_eq!(human(7200), "2h00m");
    assert_eq!(human(600), "10m");
}

#[test]
fn only_a_live_registry_entry_counts() {
    let w = world("live");
    w.session("here", &json!({}), 0);
    let dir = &w.p.sessions;
    std::fs::write(
        dir.join("dead.json"),
        json!({"pid": 2_147_483_000u32, "sessionId": "d"}).to_string(),
    )
    .unwrap();
    std::fs::write(
        dir.join("text.json"),
        json!({"pid": "not-a-pid", "sessionId": "t"}).to_string(),
    )
    .unwrap();
    std::fs::write(
        dir.join("noid.json"),
        json!({"pid": std::process::id()}).to_string(),
    )
    .unwrap();
    std::fs::write(dir.join("list.json"), "[1]").unwrap();
    std::fs::write(dir.join("bad.json"), "{").unwrap();
    std::fs::write(dir.join("note.txt"), "").unwrap();
    std::fs::write(dir.join(".hidden.json"), "{}").unwrap();
    assert_eq!(
        live_sessions(&w.p)
            .iter()
            .map(|e| e["sessionId"].as_str().unwrap().to_owned())
            .collect::<Vec<_>>(),
        ["here"]
    );
}

#[test]
fn a_pending_question_is_read_from_the_transcripts_end() {
    let w = world("ask");
    let t = w.root.join("t.jsonl");
    let say = |body: &str| {
        std::fs::write(&t, body).unwrap();
        asking_gm(&t)
    };
    let ask_rec = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "AskUserQuestion"}]}});
    assert!(say(&format!(
        "{ask_rec}\n{{bad\n{}\n",
        json!({"type": "system"})
    )));
    assert!(!say(&format!(
        "{ask_rec}\n{}\n",
        json!({"type": "user", "message": {"content": "answer"}})
    )));
    assert!(!say(&format!(
        "{}\n",
        json!({"type": "assistant", "message": {"content": "text"}})
    )));
    assert!(!say(&format!(
        "{}\n",
        json!({"type": "assistant", "message": "not an object"})
    )));
    assert!(!asking_gm(&w.root.join("missing")));
}

#[test]
fn the_clone_is_the_claim_else_the_cwds_and_never_the_mirror() {
    let w = world("clone");
    let e = json!({"sessionId": "none", "cwd": w.clone.to_string_lossy()});
    assert_eq!(
        clone_of(&w.p, &e),
        w.clone.canonicalize().unwrap().to_string_lossy()
    );
    assert_eq!(clone_of(&w.p, &json!({"sessionId": "none"})), "");
    let m = json!({"sessionId": "none", "cwd": w.p.mirror.to_string_lossy()});
    assert_eq!(clone_of(&w.p, &m), "");
    std::fs::write(w.p.clones.join("c"), "/claimed\n").unwrap();
    assert_eq!(clone_of(&w.p, &json!({"sessionId": "c"})), "/claimed");
}

#[test]
fn unfinished_work_is_named() {
    let w = world("work");
    let c = w.clone.to_string_lossy().into_owned();
    assert_eq!(unfinished(&w.p, &c), "");
    w.dirty();
    git(&w.clone, &["add", "."]);
    git(&w.clone, &["commit", "-q", "-m", "x"]);
    assert_eq!(unfinished(&w.p, &c), "commits not on main");
    w.dirty();
    std::fs::write(w.clone.join("more"), "").unwrap();
    let fake = w.root.join("proc/500");
    std::fs::create_dir_all(&fake).unwrap();
    std::fs::write(fake.join("comm"), "make\n").unwrap();
    std::fs::write(fake.join("cmdline"), "make\0done\0").unwrap();
    std::os::unix::fs::symlink(&w.clone, fake.join("cwd")).unwrap();
    let w = World {
        p: Paths {
            proc: w.root.join("proc"),
            ..w.p
        },
        ..w
    };
    assert_eq!(
        unfinished(&w.p, &c),
        "uncommitted changes, commits not on main, a live make"
    );
}

#[test]
fn a_retry_wait_exempts_only_a_live_current_queue() {
    let mut w = world("retry");
    let dir = w.clone.join(".git/page-sessions");
    std::fs::create_dir_all(&dir).unwrap();
    let log = dir.join("run-a.log");
    std::fs::write(
        &log,
        "started s x\nfailed s rc=1 - waiting 15 min (reset), then resuming\n\n",
    )
    .unwrap();
    std::fs::write(dir.join("other.txt"), "").unwrap();
    let c = w.clone.to_string_lossy().into_owned();
    let proc = w.root.join("proc");
    let at = proc.join("4242");
    std::fs::create_dir_all(&at).unwrap();
    std::fs::create_dir_all(proc.join("self")).unwrap();
    w.p.proc = proc;
    let t = now();
    assert!(!in_retry_wait(&w.p, &c, "s", t));
    let argv = format!(
        "python3\0page_session_runner.py\0--work\0{}\0",
        log.display()
    );
    std::fs::write(at.join("cmdline"), argv).unwrap();
    assert!(in_retry_wait(&w.p, &c, "s", t));
    assert!(!in_retry_wait(&w.p, &c, "other", t));
    assert!(!in_retry_wait(&w.p, &c, "s", t + 3600.0));
    std::fs::write(&log, "started s x\nsome other line\n").unwrap();
    assert!(!in_retry_wait(&w.p, &c, "s", t));
}

#[test]
fn a_stall_lands_on_its_own_pane_else_its_hosts() {
    let mut w = world("host");
    let c = w.clone.to_string_lossy().into_owned();
    let own = json!({"tmux": "@1.%3"});
    assert_eq!(host_pane(&w.p, &own, &[], &c), ("%3".to_owned(), true));
    let host = json!({"sessionId": "disp", "tmux": "@1.%9"});
    let parker = json!({"sessionId": "park", "tmux": "@1.%8", "parkedJobId": "job"});
    let at = w.root.join("proc/77");
    std::fs::create_dir_all(&at).unwrap();
    std::fs::write(at.join("environ"), "A=1\0L7R_DISPATCHER=disp\0").unwrap();
    w.p.proc = w.root.join("proc");
    let headless = json!({"sessionId": "h", "pid": 77});
    let regs = [host, parker.clone()];
    assert_eq!(
        host_pane(&w.p, &headless, &regs, &c),
        ("%9".to_owned(), false)
    );
    let bg = json!({"sessionId": "b", "jobId": "job", "pid": "78"});
    assert_eq!(host_pane(&w.p, &bg, &regs, &c), ("%8".to_owned(), false));
    std::fs::write(w.p.clones.join("near"), &c).unwrap();
    let near = json!({"sessionId": "near", "kind": "interactive", "tmux": "@1.%7"});
    let lone = json!({"sessionId": "l"});
    assert_eq!(
        host_pane(&w.p, &lone, &[near], &c),
        ("%7".to_owned(), false)
    );
    assert_eq!(
        host_pane(&w.p, &lone, &[parker], &c),
        (String::new(), false)
    );
}

#[test]
fn what_is_not_a_stall() {
    let w = world("not");
    let e = w.session("s", &json!({}), 7200);
    let t = now();
    assert!(judge(&w.p, &json!({"sessionId": "never"}), t).is_none());
    assert!(judge(&w.p, &e, t).is_none());
    w.dirty();
    assert_eq!(
        judge(&w.p, &e, t).map(|s| s.what).as_deref(),
        Some("uncommitted changes")
    );
    assert!(judge(&w.p, &json!({"sessionId": "s", "status": "waiting"}), t).is_none());
    assert!(judge(&w.p, &e, t - 7000.0).is_none());
    let ask_rec = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "AskUserQuestion"}]}});
    std::fs::write(w.root.join("projects/p/s.jsonl"), format!("{ask_rec}\n")).unwrap();
    assert!(judge(&w.p, &e, now() + 7200.0).is_none());
    std::fs::write(w.root.join("projects/p/s.jsonl"), "{}\n").unwrap();
    std::fs::remove_file(w.p.clones.join("s")).unwrap();
    assert!(judge(&w.p, &json!({"sessionId": "s", "cwd": "/"}), now() + 7200.0).is_none());
    std::fs::create_dir_all(w.root.join("projects/p/q/subagents")).unwrap();
    std::fs::write(w.root.join("projects/p/q/subagents/agent-1.jsonl"), "").unwrap();
    std::fs::write(w.root.join("projects/p/q/subagents/note.txt"), "").unwrap();
    std::fs::write(w.root.join("projects/p/q.jsonl"), "").unwrap();
    assert!(judge(&w.p, &json!({"sessionId": "q"}), now()).is_none());
}

#[test]
fn the_input_line_must_be_the_bare_prompt() {
    let w = world("input");
    assert!(!input_empty(&w.p, "%1"));
    w.screen("❯ ");
    assert!(input_empty(&w.p, "%1"));
    w.screen("❯ half a sentence");
    assert!(!input_empty(&w.p, "%1"));
    w.screen("❯\ntwo lines");
    assert!(!input_empty(&w.p, "%1"));
}

#[test]
fn the_resume_command_names_a_page_sessions_brief() {
    let w = world("resume");
    let e = json!({"sessionId": "s", "cwd": "/w"});
    let c = w.clone.to_string_lossy().into_owned();
    assert_eq!(resume_command(&e, &c), "cd /w && claude --resume s");
    assert_eq!(
        resume_command(&json!({"sessionId": "s"}), &c),
        format!("cd {c} && claude --resume s")
    );
    std::fs::create_dir_all(w.clone.join(".git/page-sessions")).unwrap();
    std::fs::write(
        w.clone.join(".git/page-sessions/index.txt"),
        "other b\ns the-brief.md\n",
    )
    .unwrap();
    assert_eq!(
        resume_command(&e, &c),
        "make page-session BRIEF=\"resume:s:the-brief.md\""
    );
}

#[test]
fn a_pass_marks_rings_and_nudges_once_per_stall() {
    let w = world("pass");
    w.dirty();
    w.session("s", &json!({"tmux": "@1.%1"}), 7200);
    w.screen("❯ ");
    let said = run_pass(&w.p, now());
    assert!(
        said.len() == 1
            && said[0].contains("stalled name-s (s) idle 12")
            && said[0].contains("marked %1 (own); nudged")
            && !said[0].contains("resume")
    );
    let tty = std::fs::read_to_string(w.root.join("tty-%1")).unwrap();
    assert!(tty.contains("STALLED 2h00m - name-s\u{7}\u{7}"));
    assert!(
        w.sent()
            .contains("send-keys -t %1 -l watchdog (feature 295)")
            && w.sent().contains("send-keys -t %1 Enter")
    );
    std::fs::remove_file(w.root.join("sent")).unwrap();
    assert_eq!(run_pass(&w.p, now()).len(), 1);
    let tty = std::fs::read_to_string(w.root.join("tty-%1")).unwrap();
    assert!(!tty.ends_with("\u{7}\u{7}") && w.sent().is_empty());
    assert_eq!(
        std::fs::read_to_string(w.p.state.join("log"))
            .unwrap()
            .lines()
            .count(),
        2
    );
}

#[test]
fn a_paneless_stall_is_logged_and_a_dry_run_touches_nothing() {
    let mut w = world("paneless");
    w.dirty();
    w.session("s", &json!({"name": ""}), 7200);
    let said = run_pass(&w.p, now());
    assert!(
        said[0].contains("stalled clone (s)")
            && said[0].contains("no tab, logged only; resume: cd ")
    );
    w.p.dry = true;
    let before = std::fs::read_to_string(w.p.state.join("log")).unwrap();
    assert!(run_pass(&w.p, now())[0].starts_with("would mark  (s) idle 12"));
    assert_eq!(
        std::fs::read_to_string(w.p.state.join("log")).unwrap(),
        before
    );
}

#[test]
fn a_tab_that_cannot_be_found_and_a_host_tab() {
    let w = world("hosttab");
    w.dirty();
    std::fs::write(w.root.join("tmux"), "exit 0\n").unwrap();
    w.session("own", &json!({"tmux": "@1.%2"}), 7200);
    assert!(run_pass(&w.p, now())
        .iter()
        .any(|l| l.contains("stalled name-own (own)") && l.contains("no tab")));
    std::fs::write(
        w.root.join("tmux"),
        format!("touch {0}/tty; echo {0}/tty\n", w.root.display()),
    )
    .unwrap();
    w.session("bg", &json!({"jobId": "j"}), 7200);
    w.session("parker", &json!({"tmux": "@1.%4", "parkedJobId": "j"}), 0);
    assert!(run_pass(&w.p, now())
        .iter()
        .any(|l| l.contains("stalled name-bg (bg)") && l.contains("marked %4 (host)")));
    assert!(run_pass(
        &Paths {
            sessions: w.root.join("none"),
            ..w.p
        },
        now()
    )
    .is_empty());
}
