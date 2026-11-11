//! The decider over a real tree with `sh` stand-ins for the review tools (`tests/hooks/test-ledger-hooks.sh`, replayed through the shim, is
//! the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{commit_root, decide, judge, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

const GOOD: &str = "| row |\n";

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

/// A repository with a ledger, and a tree of tools: the lint refuses a ledger holding `SHORT`, the owed report prints a file's words.
fn world(tag: &str) -> (crate::shared::tempdir::TempDir, String, PathBuf) {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-ledger-{tag}"));
    let repo = d.join("repo");
    let tools = d.join("tree/scripts/reviews");
    std::fs::create_dir_all(repo.join("dev")).unwrap();
    std::fs::create_dir_all(&tools).unwrap();
    let at = repo.canonicalize().unwrap().to_string_lossy().into_owned();
    git(&at, &["init", "-q", "-b", "main"]);
    std::fs::write(repo.join("dev/review-ledger.md"), GOOD).unwrap();
    std::fs::write(repo.join("other.md"), "x\n").unwrap();
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "one"]);
    std::fs::write(
        tools.join("ledger_lint.py"),
        "if grep -q SHORT \"$1\"; then echo 'line 7: short'; exit 1; fi\n",
    )
    .unwrap();
    std::fs::write(
        tools.join("ledger_owed.py"),
        format!("cat {}/owed 2>/dev/null\n", d.display()),
    )
    .unwrap();
    std::fs::write(
        tools.join("review_cost.py"),
        "[ \"$2\" = bad ] && exit 1; echo '80 s | 1k in'\n",
    )
    .unwrap();
    let tree = d.join("tree");
    (d, at, tree)
}

fn ctx(at: &str, tree: &Path) -> Ctx {
    Ctx {
        here: PathBuf::from(at),
        tree: tree.to_path_buf(),
        python: "sh",
    }
}

fn run(cmd: &str, at: &str, tree: &Path) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": cmd}}),
    };
    judge(&e, &Session::from_input(&e.input), &ctx(at, tree))
}

fn short(at: &str) {
    std::fs::write(format!("{at}/dev/review-ledger.md"), "SHORT\n").unwrap();
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn the_commit_is_found_among_a_commands_words() {
    assert_eq!(commit_root("git commit -m x").as_deref(), Some("."));
    assert_eq!(
        commit_root("git -C /x -c a=b --no-pager commit").as_deref(),
        Some("/x")
    );
    assert_eq!(commit_root("git status && git -C"), None);
    assert_eq!(commit_root("git -c"), None);
    assert_eq!(commit_root("echo 'git commit"), None);
    assert_eq!(commit_root("grep -n 'git commit' f"), None);
}

#[test]
fn a_staged_short_row_is_refused_and_named() {
    let (_dir, at, tree) = world("short");
    short(&at);
    git(&at, &["add", "dev/review-ledger.md"]);
    let got = run("git commit -m rows", &at, &tree);
    assert!(refused(&got, "line 7: short") && refused(&got, "make review-cost"));
    assert!(refused(
        &run(&format!("git -C {at} commit -m rows"), "/", &tree),
        "row short of a cell"
    ));
}

#[test]
fn what_the_commit_takes_counts_as_staged() {
    let (_dir, at, tree) = world("takes");
    short(&at);
    assert!(run("git commit -m rows", &at, &tree).is_empty());
    assert!(refused(
        &run("git commit -am rows", &at, &tree),
        "row short"
    ));
    assert!(refused(
        &run("git commit --all -m rows", &at, &tree),
        "row short"
    ));
    assert!(refused(
        &run(
            "git add dev/review-ledger.md && git commit -m rows",
            &at,
            &tree
        ),
        "row short"
    ));
    assert!(refused(
        &run("git add dev/ && git commit -m rows", &at, &tree),
        "row short"
    ));
    assert!(run("git add other.md && git commit -m other", &at, &tree).is_empty());
}

#[test]
fn a_row_the_command_appends_is_judged_with_the_ledger() {
    let (_dir, at, tree) = world("append");
    let append =
        "make append FILE=dev/review-ledger.md LINE=\"SHORT\" && git add dev && git commit -m row";
    assert!(refused(&run(append, &at, &tree), "row short"));
    assert!(run(
        "make append FILE=dev/review-ledger.md LINE=\"| ok |\" && git add dev && git commit -m row",
        &at,
        &tree
    )
    .is_empty());
    assert!(run(
        "make append FILE=other.md LINE=\"SHORT\" && git commit -am x",
        &at,
        &tree
    )
    .is_empty());
    assert!(run(
        "make append FILE=dev/review-ledger.md && git commit -m x",
        &at,
        &tree
    )
    .is_empty());
    let agent = "make append FILE=dev/review-ledger.md LINE=\"| SHORT |\" AGENT=a1 && git add dev && git commit -m row";
    assert!(refused(&run(agent, &at, &tree), "row short"));
    let unpriced = "make append FILE=dev/review-ledger.md LINE=\"SHORT\" AGENT=bad && git add dev && git commit -m row";
    assert!(refused(&run(unpriced, &at, &tree), "row short"));
    let open_row = "make append FILE=dev/review-ledger.md LINE=\"SHORT\" AGENT=a1 && git add dev && git commit -m row";
    assert!(refused(&run(open_row, &at, &tree), "row short"));
}

#[test]
fn a_pass_with_no_row_is_reported_never_refused() {
    let (_dir, at, tree) = world("owed");
    std::fs::write(
        tree.parent().unwrap().join("owed"),
        "ledger-owed: 1 check pass",
    )
    .unwrap();
    let got = run("git commit -m other", &at, &tree);
    assert!(matches!(&got[..], [Answer::Notice(t)] if t.contains("ledger-owed")));
}

#[test]
fn the_repositorys_own_tools_come_first_and_nothing_else_is_read() {
    let (_dir, at, tree) = world("own");
    std::fs::create_dir_all(format!("{at}/scripts/reviews")).unwrap();
    std::fs::write(
        format!("{at}/scripts/reviews/ledger_lint.py"),
        "echo own-lint; exit 1\n",
    )
    .unwrap();
    git(&at, &["add", "dev"]);
    short(&at);
    git(&at, &["add", "dev"]);
    assert!(refused(&run("git commit -m rows", &at, &tree), "own-lint"));
    assert!(run("git status", &at, &tree).is_empty());
    assert!(run("echo 'then git commit -m x'", &at, &tree).is_empty());
    assert!(run("git commit -m x", "/", &tree).is_empty());
    std::fs::remove_file(format!("{at}/dev/review-ledger.md")).unwrap();
    assert!(run("git commit -m x", &at, &tree).is_empty());
}

#[test]
fn the_escape_needs_a_reason_and_the_entry_runs() {
    let (_dir, at, tree) = world("esc");
    short(&at);
    git(&at, &["add", "dev"]);
    assert!(run(
        "LEDGER_LINT_OK=\"the row predates it\" git commit -m rows",
        &at,
        &tree
    )
    .is_empty());
    assert!(refused(
        &run("git commit -m rows  # LEDGER_LINT_OK", &at, &tree),
        "with no reason"
    ));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": "echo hi"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
