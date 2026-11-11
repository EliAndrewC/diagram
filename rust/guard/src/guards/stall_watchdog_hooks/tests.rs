//! The guard and its loop (`tests/hooks/test-stall-watchdog-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{cli, decide, judge, run, with, Config};
use crate::protocol::Event;
use crate::shared::session::Session;
use crate::shared::tool::flock;

/// A state directory and a fake library that records each pass and writes to stderr.
fn world(tag: &str) -> (crate::shared::tempdir::TempDir, Config) {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-stall-dog-{tag}"));
    let lib = root.join("tree/scripts/hooks");
    std::fs::create_dir_all(&lib).unwrap();
    let passes = root.join("passes");
    std::fs::write(
        lib.join("l7r-guard.sh"),
        format!(
            "echo x >> {}; echo marked; echo oops >&2\n",
            passes.display()
        ),
    )
    .unwrap();
    let mut c = Config::from_env(&|_| None);
    c.state = root.join("state");
    c.period = 0.0;
    c.passes = Some(2);
    c.tree = root.join("tree");
    c.exe = PathBuf::from("/bin/true");
    c.bash = "bash";
    (root, c)
}

fn event() -> Event {
    Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({}),
    }
}

fn lines(p: &Path) -> usize {
    std::fs::read_to_string(p).map_or(0, |t| t.lines().count())
}

#[test]
fn the_environment_sets_the_paths_and_the_pace() {
    let c = Config::from_env(&|k| match k {
        "HOME" => Some("/h".to_owned()),
        "STALL_PERIOD" => Some("7".to_owned()),
        "STALL_PASSES" | "L7R_SELF_CHECK" => Some("1".to_owned()),
        "L7R_GUARD_TREE" => Some("/t".to_owned()),
        _ => None,
    });
    assert_eq!(
        (
            c.state.as_path(),
            c.period,
            c.passes,
            c.tree.as_path(),
            c.off
        ),
        (
            Path::new("/h/.claude/stall-watchdog"),
            7.0,
            Some(1),
            Path::new("/t"),
            true
        )
    );
    let set = Config::from_env(&|k| (k == "STALL_STATE_DIR").then(|| "/s".to_owned()));
    assert!(
        set.state == Path::new("/s")
            && (set.period - 300.0).abs() < 1e-9
            && !set.off
            && set.tree == Path::new("/diagram")
    );
}

#[test]
fn a_prompt_starts_the_loop_only_when_none_is_alive() {
    let (root, c) = world("prompt");
    let e = event();
    let s = Session::from_input(&e.input);
    assert!(judge(&e, &s, &c).is_empty() && c.state.is_dir());
    std::fs::write(c.state.join("pid"), std::process::id().to_string()).unwrap();
    assert!(judge(&e, &s, &c).is_empty());
    std::fs::write(c.state.join("pid"), "2147483000").unwrap();
    assert!(judge(&e, &s, &c).is_empty());
    let off = Config {
        off: true,
        state: root.join("never"),
        ..c
    };
    assert!(judge(&e, &s, &off).is_empty() && !root.join("never").exists());
    let blocked = Config {
        state: PathBuf::from("/proc/nope/x"),
        ..off
    };
    let on = Config {
        off: false,
        ..blocked
    };
    assert!(judge(&e, &s, &on).is_empty());
}

#[test]
fn the_loop_passes_each_period_and_holds_the_host_to_one() {
    let (root, c) = world("loop");
    assert_eq!(run(&c), 0);
    assert!(lines(&root.join("passes")) == 2 && lines(&c.state.join("errors")) == 2);
    assert_eq!(
        std::fs::read_to_string(c.state.join("pid")).unwrap(),
        std::process::id().to_string()
    );
    let held = std::fs::File::create(c.state.join("lock")).unwrap();
    // a child forked on another test's thread can hold the just-closed lock for an instant, so this waits for it
    assert!((0..500).any(|_| flock(&held, "-n")));
    assert_eq!(run(&c), 0);
    assert_eq!(lines(&root.join("passes")), 2);
    assert!(flock(&held, "-u"));
}

#[test]
fn the_loop_ends_with_its_state_directory_and_fails_without_one() {
    let (root, c) = world("gone");
    std::fs::create_dir_all(&c.state).unwrap();
    std::fs::write(
        root.join("tree/scripts/hooks/l7r-guard.sh"),
        format!("rm -r {}\n", c.state.display()),
    )
    .unwrap();
    assert_eq!(run(&Config { passes: None, ..c }), 0);
    let (_dir, d) = world("noplace");
    assert_eq!(
        run(&Config {
            state: PathBuf::from("/proc/nope/x"),
            ..d
        }),
        1
    );
    let (_dir, e) = world("nolock");
    std::fs::create_dir_all(e.state.join("lock")).unwrap();
    assert_eq!(run(&e), 1);
}

#[test]
fn the_command_line_answers_each_mode() {
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let (root, c) = world("cli");
    std::env::set_var("STALL_SESSIONS_DIR", root.join("no-sessions"));
    std::env::set_var("STALL_STATE_DIR", root.join("once-state"));
    let once = with(&args(&["once"]), &c);
    assert!(once.code == 0 && once.stdout.is_empty());
    assert_eq!(with(&args(&["run"]), &c).code, 0);
    assert_eq!(cli(&args(&[])).code, 2);
    let e = event();
    std::env::set_var("L7R_SELF_CHECK", "1");
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
