//! The decider over a real tree (`tests/hooks/test-conflict-marker-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::json;

use super::{
    assignments, conflicted, decide, declares_exemption, expand, has_conflict, judge, staged_by,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn triple() -> String {
    format!(
        "{} HEAD\nmine\n{}\ntheirs\n{} other\n",
        "<".repeat(7),
        "=".repeat(7),
        ">".repeat(7)
    )
}

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
    assert!(ask(Path::new("/"), "git", &all, "").ok());
}

/// A repository with a tracked file, committed clean.
fn repo(tag: &str) -> String {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-conflict-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join("sub")).unwrap();
    let at = d.canonicalize().unwrap().to_string_lossy().into_owned();
    git(&at, &["init", "-q", "-b", "main"]);
    std::fs::write(d.join("a.md"), "base\n").unwrap();
    std::fs::write(d.join("sub/ok.md"), "clean\n").unwrap();
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "one"]);
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
fn only_the_triple_in_order_at_column_zero_is_a_conflict() {
    let t = triple();
    let (open, mid, close) = ("<".repeat(7), "=".repeat(7), ">".repeat(7));
    assert!(has_conflict(&t) && has_conflict(&format!("doc\n\n```\n{t}```\n")));
    assert!(
        !has_conflict(&format!("A heading\n{mid}\n\ntext\n"))
            && !has_conflict(&format!("{open} is what git writes\n"))
    );
    let indented = t
        .lines()
        .map(|l| format!("    {l}"))
        .collect::<Vec<_>>()
        .join("\n");
    assert!(!has_conflict(&indented) && !has_conflict(&format!("{close} x\n{mid}\n{open} y\n")));
}

#[test]
fn a_file_exempts_itself_only_with_a_real_declaration_near_its_top() {
    let t = triple();
    assert!(!has_conflict(&format!(
        "CONFLICT_MARKERS_OK: this doc must show one\n{t}"
    )));
    assert!(!has_conflict(&format!(
        "# CONFLICT_MARKERS_OK: a fixture that must hold one\n{t}"
    )));
    assert!(has_conflict(&format!("CONFLICT_MARKERS_OK: x\n{t}")));
    assert!(has_conflict(&format!(
        "a doc saying to put `CONFLICT_MARKERS_OK: <reason>` here\n{t}"
    )));
    assert!(has_conflict(&format!(
        "CONFLICT_MARKERS_OK: <reason> goes here\n{t}"
    )));
    assert!(has_conflict(&format!(
        "{}CONFLICT_MARKERS_OK: too far down to count\n{t}",
        "\n".repeat(40)
    )));
    assert!(!declares_exemption("nothing here"));
}

#[test]
fn a_commands_assignments_expand_into_its_paths() {
    let vars = assignments("CL=/x; D=\"/y\" git add ; CL=/z");
    assert_eq!(
        vars,
        [
            ("CL".to_owned(), "/z".to_owned()),
            ("D".to_owned(), "/y".to_owned())
        ]
    );
    assert_eq!(expand("$CL/a ${D}/b $E", &vars), "/z/a /y/b $E");
}

#[test]
fn git_is_asked_what_would_be_staged() {
    let at = repo("add");
    std::fs::write(format!("{at}/a.md"), triple()).unwrap();
    assert!(refused(&run("git add -A", &at), "a.md"));
    assert!(refused(
        &run(&format!("CL={at}; git -C $CL add -A"), "/"),
        "still carries a merge conflict"
    ));
    assert!(refused(&run("cd sub; git -C .. add -A", &at), "a.md"));
    assert!(run("git add sub/ok.md", &at).is_empty());
    assert!(run("cd sub && git add .", &at).is_empty());
    git(&at, &["add", "a.md"]);
    std::fs::write(format!("{at}/b.md"), triple()).unwrap();
    git(&at, &["add", "b.md"]);
    let got = run("git commit -m \"a.md named here\" && echo done", &at);
    assert!(refused(&got, "a.md") && refused(&got, "b.md"));
}

#[test]
fn a_commit_is_judged_by_what_it_carries() {
    let at = repo("commit");
    assert!(run("git commit -m clean", &at).is_empty());
    assert!(staged_by("git commit -m 'a.md' --author 'x'", &at).is_empty());
    std::fs::write(format!("{at}/a.md"), triple()).unwrap();
    assert!(run("git commit -m x", &at).is_empty());
    assert!(refused(&run("git commit -am wip", &at), "a.md"));
    assert!(refused(&run("git commit --all -m wip", &at), "a.md"));
    assert!(refused(&run("git commit -m wip -- a.md", &at), "a.md"));
    assert!(run("git commit -m wip -- sub/ok.md", &at).is_empty());
}

#[test]
fn only_a_real_add_or_commit_is_read() {
    let at = repo("shapes");
    assert!(staged_by("git -C /somewhere", &at).is_empty());
    assert!(run("echo add; git add sub/ok.md", &at).is_empty());
    std::fs::remove_file(format!("{at}/sub/ok.md")).unwrap();
    assert!(run("git add -A", &at).is_empty());
    for cmd in [
        "",
        "ls",
        "echo git add",
        "git -C",
        "git status add",
        "echo 'git add",
    ] {
        assert!(run(cmd, &at).is_empty(), "{cmd}");
    }
    assert!(staged_by("git -c a=b add missing.md", &at).is_empty());
    assert!(staged_by("git -C /no/such/repo add -A", &at).is_empty());
    assert!(conflicted(
        &["/no/such/file".to_owned(), at.clone()]
            .into_iter()
            .collect()
    )
    .is_empty());
}

#[test]
fn the_escape_needs_a_reason_and_the_entry_reads_the_cwd() {
    let at = repo("esc");
    std::fs::write(format!("{at}/a.md"), triple()).unwrap();
    assert!(run(
        "git add -A  # CONFLICT_MARKERS_OK: a fixture holding one",
        &at
    )
    .is_empty());
    assert!(refused(
        &run("git add -A  # CONFLICT_MARKERS_OK", &at),
        "with no reason"
    ));
    let one = run("git add a.md", &at);
    assert!(refused(&one, "BLOCKED: this would stage"));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": "echo hi"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
