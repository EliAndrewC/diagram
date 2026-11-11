//! The sweep on a fixture tree: a root, its projects' transcripts, a state directory, and the clock set four days ahead so whatever
//! the test does not freshen is idle.

use std::fs::File;
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::time::{Duration, SystemTime};

use serde_json::json;

use super::sweep::{plan, remove, Item};
use super::{cli, decide, judge, size, with, Config};
use crate::protocol::Event;
use crate::shared::session::Session;
use crate::shared::tool::flock;

const DAY: u64 = 86_400;

fn now() -> SystemTime {
    SystemTime::now() + Duration::from_secs(4 * DAY)
}

fn world(tag: &str) -> (PathBuf, Config) {
    crate::shared::log::quiet();
    let base = std::env::temp_dir().join(format!("l7r-guard-sweep-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&base);
    for d in ["root", "projects", "elsewhere", "sessions"] {
        std::fs::create_dir_all(base.join(d)).unwrap();
    }
    let mut c = Config::from_env(&|_| None, 4242);
    c.root = base.join("root");
    c.projects = base.join("projects");
    c.sessions = base.join("sessions");
    c.state = base.join("state");
    c.exe = PathBuf::from("/bin/true");
    c.keep = "current".to_owned();
    (base, c)
}

fn put(path: &Path, fresh: bool) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, "x").unwrap();
    if fresh {
        File::options()
            .write(true)
            .open(path)
            .unwrap()
            .set_modified(now())
            .unwrap();
    }
}

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn names(items: &[Item], c: &Config) -> Vec<String> {
    let root = std::fs::canonicalize(&c.root).unwrap();
    let mut v: Vec<String> = items
        .iter()
        .map(|i| {
            i.path
                .strip_prefix(&root)
                .unwrap()
                .to_string_lossy()
                .into_owned()
        })
        .collect();
    v.sort();
    v
}

fn hold(cwd: &Path, out: Option<&Path>) -> Child {
    Command::new("sleep")
        .arg("60")
        .current_dir(cwd)
        .stdin(Stdio::null())
        .stdout(out.map_or(Stdio::null(), |p| Stdio::from(File::create(p).unwrap())))
        .spawn()
        .unwrap()
}

/// The fixture every judgment is read from: one entry per rule.
fn plant(base: &Path, c: &Config) {
    let (r, p) = (&c.root, &c.projects);
    put(&r.join("-proj/idle/scratchpad/a"), false);
    put(&p.join("-proj/idle.jsonl"), false);
    // its transcript and scratch idle, but Claude Code records it running under this very process: kept; and a record whose pid was
    // reused (the start time differs) keeps nothing, so `idle` above still goes
    put(&r.join("-proj/running/scratchpad/a"), false);
    put(&p.join("-proj/running.jsonl"), false);
    let me = std::process::id();
    let stat = std::fs::read_to_string(format!("/proc/{me}/stat")).unwrap();
    let since = stat
        .rsplit_once(") ")
        .unwrap()
        .1
        .split_whitespace()
        .nth(19)
        .unwrap()
        .to_owned();
    let record = |file: &str, id: &str, start: &str| {
        let v = json!({ "pid": me, "sessionId": id, "procStart": start });
        std::fs::write(c.sessions.join(file), v.to_string()).unwrap();
    };
    record("1.json", "running", &since);
    record("2.json", "idle", "1");
    std::fs::write(c.sessions.join("3.json"), "not json").unwrap();
    let gone = json!({ "pid": 4_000_000_000_u64, "sessionId": "orphan-old", "procStart": "1" });
    std::fs::write(c.sessions.join("5.json"), gone.to_string()).unwrap();
    std::fs::write(c.sessions.join("4.key"), "x").unwrap();
    // its transcript idle, but a subagent wrote into its scratch since: kept
    put(&r.join("-proj/agent-wrote/scratchpad/fresh"), true);
    put(&p.join("-proj/agent-wrote.jsonl"), false);
    put(&r.join("-proj/recent/scratchpad/a"), false);
    put(&p.join("-proj/recent.jsonl"), true);
    put(&r.join("-proj/current/scratchpad/a"), false);
    put(&r.join("-proj/orphan-old/tasks/t.output"), false);
    put(&r.join("-proj/orphan-new/tasks/t.output"), true);
    put(&r.join("-proj/cwd-held/scratchpad/a"), false);
    put(&r.join("-proj/fd-held/tasks/b"), false);
    put(&r.join("old.log"), false);
    put(&r.join("-not-a-dir"), false);
    put(&r.join("trials/deep/x/y"), false);
    put(&r.join("w38/deep/fresh"), true);
    put(&r.join("locked/inner/a"), false);
    std::fs::set_permissions(
        r.join("locked/inner"),
        std::fs::Permissions::from_mode(0o000),
    )
    .unwrap();
    put(&base.join("elsewhere/precious"), false);
    std::os::unix::fs::symlink(base.join("elsewhere"), r.join("link-out")).unwrap();
    std::os::unix::fs::symlink(base.join("elsewhere"), r.join("trials/link-in")).unwrap();
    std::os::unix::fs::symlink(base.join("elsewhere"), r.join("-proj/link-session")).unwrap();
}

#[test]
fn a_finished_sessions_scratch_goes_and_everything_live_stays() {
    let (base, mut c) = world("sweep");
    plant(&base, &c);
    let mut cwd = hold(&c.root.join("-proj/cwd-held/scratchpad"), None);
    let mut fd = hold(&base, Some(&c.root.join("-proj/fd-held/tasks/out")));
    std::thread::sleep(Duration::from_millis(200));
    let dry = with(&args(&["dry"]), &mut c, now());
    let gone = [
        "-not-a-dir",
        "-proj/idle",
        "-proj/orphan-old",
        "old.log",
        "trials",
    ];
    assert_eq!(names(&plan(&c, now()), &c), gone);
    assert!(dry.stdout.contains("would remove") && dry.stdout.contains("5 entries"));
    // a dry run removes and stamps nothing
    assert!(c.root.join("trials").exists() && !c.state.join("stamp").exists());
    let swept = with(&args(&["now", "--keep", "current"]), &mut c, now());
    assert!(
        swept.stdout.contains("5 entries") && swept.stdout.contains("removed"),
        "{}",
        swept.stdout
    );
    for g in gone {
        assert!(!c.root.join(g).exists(), "{g} swept");
    }
    for kept in [
        "-proj/recent",
        "-proj/agent-wrote",
        "-proj/running",
        "-proj/current",
        "-proj/orphan-new",
        "-proj/cwd-held",
        "-proj/fd-held",
        "w38",
        "locked",
        "link-out",
    ] {
        assert!(c.root.join(kept).symlink_metadata().is_ok(), "{kept} kept");
    }
    // no symlink followed
    assert!(base.join("elsewhere/precious").exists());
    assert!(c.state.join("stamp").exists());
    let logged = std::fs::read_dir(crate::shared::log::dir())
        .unwrap()
        .flatten()
        .any(|e| {
            std::fs::read_to_string(e.path())
                .is_ok_and(|t| t.contains("scratch-sweep") && t.contains("5 removed"))
        });
    assert!(logged, "the total is on the guard log");
    let _ = (cwd.kill(), fd.kill(), cwd.wait(), fd.wait());
    std::fs::set_permissions(
        c.root.join("locked/inner"),
        std::fs::Permissions::from_mode(0o755),
    )
    .unwrap();
}

#[test]
fn a_day_passes_between_sweeps_and_one_sweep_holds_the_lock() {
    let (base, mut c) = world("pace");
    put(&c.root.join("old.log"), false);
    let marker = base.join("spawned");
    let exe = base.join("sweeper");
    crate::guards::write_executable(
        &exe,
        &format!("#!/bin/sh\necho \"$@\" > {}\n", marker.display()),
    );
    c.exe = exe;
    let e = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({"session_id": "sid"}),
    };
    assert!(judge(&e, &c, now()).is_empty());
    assert!((0..100).any(|_| {
        std::thread::sleep(Duration::from_millis(50));
        std::fs::read_to_string(&marker).is_ok_and(|t| t.contains("run --keep sid"))
    }));
    std::fs::remove_file(&marker).unwrap();
    let ran = with(&args(&["run"]), &mut c, now());
    assert!(ran.stdout.contains("1 entries") && !c.root.join("old.log").exists());
    put(&c.root.join("old.log"), false);
    assert!(judge(&e, &c, now()).is_empty());
    let again = with(&args(&["run"]), &mut c, now());
    // once a day
    assert!(again.stdout.contains("within the day") && c.root.join("old.log").exists());
    std::thread::sleep(Duration::from_millis(300));
    assert!(!marker.exists(), "a prompt within the day starts nothing");
    let tomorrow = now() + Duration::from_secs(DAY + 1);
    let held = File::create(c.state.join("lock")).unwrap();
    assert!((0..500).any(|_| flock(&held, "-n")));
    let busy = with(&args(&["now"]), &mut c, tomorrow);
    // one sweep at a time
    assert!(busy.stdout.contains("holds the lock") && c.root.join("old.log").exists());
    assert!(flock(&held, "-u"));
    let off = Config {
        off: true,
        ..world("pace-off").1
    };
    assert!(judge(&e, &off, now()).is_empty());
    let back = now() - Duration::from_secs(10 * DAY);
    assert!(c.due(back), "a stamp from the future is a clock set back");
}

#[test]
fn nothing_is_swept_where_the_tree_or_the_process_table_cannot_be_read() {
    let (base, mut c) = world("blind");
    put(&c.root.join("old.log"), false);
    // the running sessions cannot be listed: no session directory is judged, a loose entry still is
    put(&c.root.join("-proj/idle/scratchpad/a"), false);
    c.sessions = base.join("no-sessions");
    assert_eq!(names(&plan(&c, now()), &c), ["old.log"]);
    c.proc = base.join("no-proc");
    assert!(plan(&c, now()).is_empty());
    c.proc = PathBuf::from("/proc");
    c.root = base.join("root/old.log");
    assert!(plan(&c, now()).is_empty());
    let gone = Item {
        path: base.join("never"),
        bytes: 0,
        why: "",
    };
    assert!(!remove(&gone));
    for state in [
        PathBuf::from("/proc/nope/x"),
        base.join("lockdir"),
        base.join("stampdir"),
    ] {
        c.state = state;
        if c.state.ends_with("lockdir") {
            std::fs::create_dir_all(c.state.join("lock")).unwrap();
        }
        if c.state.ends_with("stampdir") {
            std::fs::create_dir_all(c.state.join("stamp")).unwrap();
        }
        assert!(with(&args(&["now"]), &mut c, now())
            .stdout
            .contains("holds the lock"));
    }
}

#[test]
fn the_environment_sets_the_paths_and_the_command_line_its_modes() {
    let c = Config::from_env(
        &|k| match k {
            "HOME" => Some("/h".to_owned()),
            "SCRATCH_SWEEP_DAYS" => Some("0.5".to_owned()),
            "CLAUDE_CODE_SESSION_ID" => Some("me".to_owned()),
            "L7R_SELF_CHECK" => Some("1".to_owned()),
            _ => None,
        },
        1234,
    );
    assert_eq!(
        (
            c.root.as_path(),
            c.projects.as_path(),
            c.state.as_path(),
            c.age,
            c.keep.as_str(),
            c.off
        ),
        (
            Path::new("/tmp/claude-1234"),
            Path::new("/h/.claude/projects"),
            Path::new("/h/.claude/scratch-sweep"),
            Duration::from_secs(DAY / 2),
            "me",
            true
        )
    );
    let set = Config::from_env(
        &|k| match k {
            "SCRATCH_SWEEP_ROOT" => Some("/r".to_owned()),
            "SCRATCH_SWEEP_PROJECTS" => Some("/p".to_owned()),
            "SCRATCH_SWEEP_STATE" => Some("/s".to_owned()),
            "SCRATCH_SWEEP_DAYS" => Some("-1".to_owned()),
            _ => None,
        },
        1,
    );
    assert!(
        set.root == Path::new("/r")
            && set.projects == Path::new("/p")
            && set.state == Path::new("/s")
    );
    assert!(set.age == Duration::from_secs(3 * DAY) && !set.off);
    assert_eq!(cli(&args(&["bogus"])).code, 2);
    assert_eq!(size(12_345_678), "12.3 MB");
    std::env::set_var("L7R_SELF_CHECK", "1");
    let e = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
