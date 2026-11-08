//! The decider on the suite's shapes, in a real repository (`tests/hooks/test-discard-hooks.sh`, replayed through the shim, is the verdict).

use std::path::PathBuf;

use serde_json::json;

use super::{decide, dirty, judge, shlex};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn git(dir: &str, args: &[&str]) {
    let all: Vec<&str> = [
        "-C",
        dir,
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
    assert!(ask(std::path::Path::new("/"), "git", &all, "").ok());
}

/// A repository with one committed file left modified and one clean.
fn repo(tag: &str) -> String {
    crate::shared::log::quiet();
    let d: PathBuf =
        std::env::temp_dir().join(format!("l7r-guard-discard-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join("sub")).unwrap();
    let at = d.to_string_lossy().into_owned();
    git(&at, &["init", "-q", "-b", "main"]);
    for f in ["dirty.py", "clean.py", "sub/deep.py"] {
        std::fs::write(d.join(f), "a\n").unwrap();
    }
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "one"]);
    std::fs::write(d.join("dirty.py"), "b\n").unwrap();
    at
}

fn run(cmd: &str, at: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": cmd}}),
    };
    judge(&e, &Session::from_input(&e.input), at)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_command_is_split_as_shlex_splits_it() {
    let words = |s: &str| shlex(s).unwrap();
    assert_eq!(
        words("git  checkout -- 'a b' \"c\\\"d\\x\" e\\ f # note"),
        ["git", "checkout", "--", "a b", "c\"d\\x", "e f"]
    );
    assert_eq!(words("a#b c"), ["a"]);
    assert_eq!(words("'' x"), ["", "x"]);
    assert_eq!(shlex("it's"), None);
    assert_eq!(words(""), Vec::<String>::new());
}

#[test]
fn every_spelling_that_discards_a_modified_file_is_refused() {
    let at = repo("block");
    for cmd in [
        "git checkout -- dirty.py",
        "git checkout dirty.py",
        "git checkout HEAD -- dirty.py",
        "git checkout HEAD dirty.py",
        "git restore dirty.py",
        "git restore --worktree dirty.py",
        "git checkout -- .",
        "echo x && git checkout -- dirty.py",
        "git checkout abcdef1 dirty.py",
    ] {
        assert!(refused(&run(cmd, &at), "dirty.py"), "{cmd}");
    }
    assert!(refused(
        &run(&format!("git -C {at} -c a=b checkout -- dirty.py"), "/"),
        "throw away UNCOMMITTED"
    ));
    assert_eq!(
        dirty("git checkout -- dirty.py; git restore dirty.py", &at),
        ["dirty.py"]
    );
}

#[test]
fn what_discards_nothing_passes() {
    let at = repo("allow");
    for cmd in [
        "",
        "ls",
        "git checkout main",
        "git checkout -b x",
        "git checkout -- clean.py",
        "git restore --staged dirty.py",
        "git log",
        "git",
        "git -C",
        "git -C /somewhere",
        "git status && echo git checkout",
    ] {
        assert!(run(cmd, &at).is_empty(), "{cmd}");
    }
}

#[test]
fn an_unclosed_quote_falls_back_to_whitespace() {
    let at = repo("quote");
    assert!(refused(
        &run("git checkout -- dirty.py 'x", &at),
        "dirty.py"
    ));
    std::fs::write(format!("{at}/new.txt"), "").unwrap();
    assert!(run("git checkout -- new.txt", &at).is_empty());
}

#[test]
fn a_side_of_a_merge_is_resolution_only_during_a_merge() {
    let at = repo("merge");
    assert!(refused(
        &run("git checkout --ours -- dirty.py", &at),
        "dirty.py"
    ));
    std::fs::write(format!("{at}/.git/MERGE_HEAD"), "x").unwrap();
    assert!(run("git checkout --ours -- dirty.py", &at).is_empty());
    assert!(run("git restore --theirs dirty.py", &at).is_empty());
    assert!(refused(&run("git checkout -- dirty.py", &at), "dirty.py"));
    assert!(run("git checkout --ours -- dirty.py", "/no/such/repo").is_empty());
}

#[test]
fn the_escape_needs_a_reason_and_the_entry_reads_the_cwd() {
    let at = repo("esc");
    assert!(run(
        "git checkout -- dirty.py  # DISCARD_OK: reverting my own test edit",
        &at
    )
    .is_empty());
    assert!(refused(
        &run("git checkout -- dirty.py  # DISCARD_OK", &at),
        "with no reason"
    ));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": "echo hi"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
