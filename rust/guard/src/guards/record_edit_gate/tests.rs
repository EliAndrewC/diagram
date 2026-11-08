//! The gate over a fixture clone, the shell guard stubbed (`tests/hooks/test-record-edit-hooks.sh` drives the real one).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge, mode_for};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn world(tag: &str, guard: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("l7r-guard-regate-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join("scripts/hooks")).unwrap();
    std::fs::write(d.join("scripts/hooks/record-edit-hooks.sh"), guard).unwrap();
    d.canonicalize().unwrap()
}

fn event(tool: &str, input: &Value, at: &Path) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    }
}

#[test]
fn a_plain_call_concerns_nothing_and_a_record_call_does() {
    let d = world("modes", "");
    let bash = |c: &str| mode_for(&event("Bash", &json!({"command": c}), &d), &d);
    let edit = |p: &str| mode_for(&event("Edit", &json!({"file_path": p}), &d), &d);
    assert_eq!(bash("ls"), None);
    assert_eq!(bash("make quick"), None);
    assert_eq!(bash("make done"), Some("pretool-bash"));
    assert_eq!(bash("FULL=1 make -s done"), Some("pretool-bash"));
    assert_eq!(bash("make apply-edits FROM=x"), Some("pretool-bash"));
    assert_eq!(edit("/r/notes.md"), None);
    assert_eq!(edit("/r/rust/guard/src/a.rs"), None);
    assert_eq!(edit("/r/research/site/q/x.html"), Some("pretool"));
    assert_eq!(edit("research/site/a.html"), Some("pretool"));
    assert_eq!(
        edit("/r/l7r/diagram/interactive/assets/modals/sheet/bath.md"),
        Some("pretool")
    );
    assert_eq!(
        edit("/r/l7r/diagram/interactive/assets/glossary.json"),
        Some("pretool")
    );
    std::fs::write(d.join(".git/checks-open.json"), r#"{"dispatches": {}}"#).unwrap();
    assert_eq!(bash("ls"), None);
    std::fs::write(
        d.join(".git/checks-open.json"),
        "{\n \"plan_holds\": {},\n \"x\": 1\n}",
    )
    .unwrap();
    assert_eq!(bash("ls"), None, "the key stays, empty, after every hold");
    std::fs::write(
        d.join(".git/checks-open.json"),
        r#"{"plan_holds": {}, "plan_snaps": {"a": "the state's \"plan_holds\": {\"t\": 1}"}}"#,
    )
    .unwrap();
    assert_eq!(bash("ls"), None);
    std::fs::write(
        d.join(".git/checks-open.json"),
        r#"{"plan_holds": {"t": {}}}"#,
    )
    .unwrap();
    assert_eq!(bash("ls"), Some("pretool-bash"));
    assert_eq!(edit("/r/notes.md"), None);
    assert_eq!(edit("/r/specs/449-x/plan.md"), Some("pretool"));
}

#[test]
fn a_worktree_is_resolved_and_no_repository_holds_nothing() {
    let d = world("worktree", "");
    let main_git = d.join("main.git");
    std::fs::create_dir_all(main_git.join("worktrees/w")).unwrap();
    std::fs::write(main_git.join("worktrees/w/commondir"), "../..\n").unwrap();
    std::fs::remove_dir_all(d.join(".git")).unwrap();
    std::fs::write(
        d.join(".git"),
        format!("gitdir: {}\n", main_git.join("worktrees/w").display()),
    )
    .unwrap();
    let ls = event("Bash", &json!({"command": "ls"}), &d);
    assert_eq!(mode_for(&ls, &d), None);
    std::fs::write(
        main_git.join("checks-open.json"),
        r#"{"plan_holds": {"t": {}}}"#,
    )
    .unwrap();
    assert_eq!(mode_for(&ls, &d), Some("pretool-bash"));
    std::fs::write(d.join(".git"), format!("gitdir: {}\n", main_git.display())).unwrap();
    assert_eq!(mode_for(&ls, &d), Some("pretool-bash"));
    std::fs::write(d.join(".git"), "not a gitdir line").unwrap();
    assert_eq!(mode_for(&ls, &d), None);
    assert_eq!(mode_for(&ls, Path::new("/")), None);
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit"}),
    };
    assert_eq!(mode_for(&bare, Path::new("/")), None);
}

#[test]
fn the_shell_guards_reply_becomes_the_answers() {
    let refuse = world(
        "refuse",
        "cat >/dev/null; echo frozen while checked >&2; exit 2\n",
    );
    let page = json!({"file_path": "/r/research/site/q/x.html"});
    let e = event("Edit", &page, &refuse);
    assert!(
        matches!(&judge(&e, &refuse, &refuse)[..], [Answer::Refuse(t)] if t == "frozen while checked")
    );
    let rewrite = world(
        "rewrite",
        r#"cat >/dev/null; echo '{"hookSpecificOutput": {"updatedInput": {"file_path": "moved"}, "additionalContext": "moved it"}}'"#,
    );
    let e = event("Edit", &page, &rewrite);
    assert!(
        matches!(&judge(&e, &rewrite, &rewrite)[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["file_path"] == "moved" && n == "moved it")
    );
    let quiet = world("quiet", "cat >/dev/null\n");
    let e = event("Edit", &page, &quiet);
    assert!(judge(&e, &quiet, &quiet).is_empty());
    let plain = event("Bash", &json!({"command": "ls"}), &quiet);
    assert!(judge(&plain, &quiet, &quiet).is_empty());
    let unstarted = world("unstarted", "touch \"$(dirname \"$0\")/started\"\n");
    let plain = event("Bash", &json!({"command": "ls"}), &unstarted);
    assert!(judge(&plain, &unstarted, &unstarted).is_empty());
    assert!(!unstarted.join("scripts/hooks/started").exists());
    let cwdless = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(judge(&cwdless, &quiet, &quiet).is_empty());
    assert!(decide(&plain, &Session::from_input(&plain.input)).is_empty());
}
