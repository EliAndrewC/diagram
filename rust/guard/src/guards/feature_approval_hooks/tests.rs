//! The decider over a real tree and a fixture transcript (`tests/hooks/test-feature-approval-hooks.sh`, replayed through the shim, is the
//! verdict).

use std::path::Path;

use serde_json::json;

use super::{decide, is_new, judge, judge_staging, problem, standing, why};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

const QUOTE: &str = "please file the widget cache";

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

fn spec(root: &str, feature: &str, text: &str) {
    let d = format!("{root}/specs/{feature}");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(format!("{d}/spec.md"), text).unwrap();
}

fn line(words: &str) -> String {
    format!("# x\n\n**Approved**: the GM, 2026-11-08, \"{words}\"\n")
}

/// A repository holding feature 376 and 377, and a transcript of what the GM typed.
fn repo(tag: &str) -> (String, String) {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-approval-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    let at = d.canonicalize().unwrap().to_string_lossy().into_owned();
    git(&at, &["init", "-q", "-b", "main"]);
    spec(&at, "376-older", "# 376\n");
    spec(&at, "377-held", "# 377\n");
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "one"]);
    let transcript = format!("{at}/.git/t.jsonl");
    let typed = json!({"type": "user", "origin": {"kind": "human"}, "promptSource": "typed", "message": {"content": format!("Yes, {QUOTE} now")}});
    std::fs::write(&transcript, typed.to_string()).unwrap();
    (at, transcript)
}

fn run(cmd: &str, at: &str, transcript: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "transcript_path": transcript, "tool_input": {"command": cmd}}),
    };
    judge(&e, &Session::from_input(&e.input), at)
}

fn commit(at: &str, message: &str) {
    git(at, &["add", "."]);
    git(at, &["commit", "-q", "-m", message]);
}

fn run_push(at: &str, transcript: &str) -> Vec<Answer> {
    run("scripts/sync-with-main.sh done", at, transcript)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn an_approval_needs_its_line_three_words_and_the_gms_own_message() {
    let said = [format!("yes, {QUOTE} now")];
    assert_eq!(problem("# no line\n", &said), "no-line");
    assert_eq!(problem(&line("ok go"), &said), "short");
    assert_eq!(
        problem(&line("something he never wrote"), &said),
        "not-found"
    );
    assert_eq!(problem(&line(QUOTE), &said), "");
}

#[test]
fn every_reason_has_its_words() {
    for (kind, words) in [
        ("no-line", "no approval line"),
        ("short", "under three words"),
        ("not-found", "in no message"),
        ("reopened", "closed before"),
        ("reopened-not-found", "reopened and left open"),
        ("hidden-open", "an unticked task added"),
        (
            "hidden-open-not-found",
            "a task added under a closed status",
        ),
        ("other-kind", "other-kind"),
    ] {
        assert!(why(kind, "p").contains(words), "{kind}");
    }
}

#[test]
fn a_new_feature_is_refused_without_an_approval() {
    let (at, tr) = repo("new");
    spec(&at, "380-widget", "# 380\n");
    let got = run("git add specs/380-widget/spec.md", &at, &tr);
    assert!(
        refused(&got, "specs/380-widget/spec.md: no approval line")
            && refused(&got, "There is no escape variable")
    );
    assert!(refused(&got, "This command itself touches a spec.md"));
    spec(&at, "380-widget", &line("something he never wrote"));
    let not_found = run("git add -A", &at, &tr);
    assert!(
        refused(&not_found, "in no message the GM wrote") && refused(&not_found, "standing words")
    );
    spec(&at, "380-widget", &line(QUOTE));
    assert!(run("git add -A", &at, &tr).is_empty());
}

#[test]
fn only_a_new_feature_at_or_above_the_first_number_is_judged() {
    let (at, tr) = repo("old");
    spec(&at, "370-older", "# 370\n");
    assert!(run("git add -A", &at, &tr).is_empty());
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "two"]);
    spec(&at, "377-held", "# changed\n");
    assert!(run("git add -A", &at, &tr).is_empty());
    assert!(run("ls", &at, &tr).is_empty());
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&none, &Session::from_input(&none.input)).is_empty());
    let no_cmd = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "note": "git add"}),
    };
    assert!(decide(&no_cmd, &Session::from_input(&no_cmd.input)).is_empty());
}

#[test]
fn a_commit_is_read_from_the_index_unless_it_takes_the_tree() {
    let (at, _) = repo("index");
    spec(&at, "381-index", &line(QUOTE));
    git(&at, &["add", "."]);
    std::fs::write(format!("{at}/specs/381-index/spec.md"), "# no line now\n").unwrap();
    let said = [format!("yes, {QUOTE}")];
    assert!(judge_staging("git commit -m x", &at, &said).is_empty());
    assert_eq!(
        judge_staging("git commit -a -m x", &at, &said)[0].0,
        "no-line"
    );
    assert!(judge_staging("git commit -m x", "/no/such/dir", &said).is_empty());
}

#[test]
fn a_rename_a_renumber_and_a_copy() {
    let (at, _) = repo("rename");
    assert!(!is_new(&at, "specs/377-held/spec.md", "held"));
    assert!(is_new(&at, "specs/390-new/spec.md", "new"));
    assert!(is_new(&at, "specs/391-held/spec.md", "held"));
    git(&at, &["rm", "-q", "--cached", "specs/377-held/spec.md"]);
    assert!(!is_new(&at, "specs/393-held/spec.md", "held"));
    git(&at, &["add", "specs/377-held/spec.md"]);
    std::fs::rename(
        format!("{at}/specs/377-held"),
        format!("{at}/specs/392-held"),
    )
    .unwrap();
    assert!(!is_new(&at, "specs/392-held/spec.md", "held"));
    git(&at, &["add", "-A"]);
    assert!(!is_new(&at, "specs/392-held/spec.md", "held"));
}

#[test]
fn an_issue_filed_for_the_gm_is_approved_by_his_standing_words() {
    let std = "you should treat features that I have asked to be filed as automatic approval";
    let req = "# Request: EliAndrewC/diagram#7\n\n**[gm-assistant]** the body\n";
    assert!(standing(&line(std), req));
    assert!(
        !standing(&line(std), "# Request: other\n**[gm-assistant]**")
            && !standing(&line("other words here"), req)
    );
    let (at, tr) = repo("standing");
    spec(&at, "382-issue", &line(std));
    std::fs::write(format!("{at}/specs/382-issue/request.md"), req).unwrap();
    assert!(run("git add -A", &at, &tr).is_empty());
}

#[test]
fn a_feature_landed_open_or_with_a_hidden_task_is_refused_at_a_push() {
    let (at, tr) = repo("push");
    spec(
        &at,
        "300-closed",
        "# 300\n\n**Status**: Done 2026-10-01 - measured\n",
    );
    spec(&at, "301-open", "# 301\n\n**Status**: Filed\n");
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "base"]);
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    assert!(run_push(&at, &tr).is_empty());
    spec(
        &at,
        "300-closed",
        "# 300\n\n**Status**: Filed - more work\n",
    );
    spec(&at, "301-open", "# 301\n\n**Status**: Filed - edited\n");
    commit(&at, "reopen");
    let got = run_push(&at, &tr);
    assert!(
        refused(&got, "300-closed/spec.md: closed before")
            && refused(&got, "Reopening a feature")
            && !refused(&got, "301-open")
    );
    spec(
        &at,
        "300-closed",
        &format!("**Status**: Filed\n{}", line("words he never wrote")),
    );
    commit(&at, "foreign");
    assert!(refused(&run_push(&at, &tr), "reopened and left open"));
    spec(
        &at,
        "300-closed",
        &format!("**Status**: Filed\n{}", line(QUOTE)),
    );
    commit(&at, "approved");
    assert!(run_push(&at, &tr).is_empty());
}

#[test]
fn a_task_hidden_under_a_closed_status_and_the_gm_review_box() {
    let (at, tr) = repo("hidden");
    spec(&at, "300-closed", "**Status:** Superseded by 400\n");
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "base"]);
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::write(
        format!("{at}/specs/300-closed/tasks.md"),
        "- [ ] T05 hidden\n",
    )
    .unwrap();
    commit(&at, "hide");
    let got = run_push(&at, &tr);
    assert!(
        refused(&got, "an unticked task added")
            && refused(&got, "Adding a task under a closed status")
    );
    spec(
        &at,
        "300-closed",
        &format!("**Status**: Withdrawn\n{}", line("words he never wrote")),
    );
    commit(&at, "foreign");
    assert!(refused(
        &run_push(&at, &tr),
        "a task added under a closed status"
    ));
    std::fs::write(
        format!("{at}/specs/300-closed/tasks.md"),
        "- [ ] GM review (make gm-reviewed F=300)\n",
    )
    .unwrap();
    spec(&at, "300-closed", "**Status**: Done\n");
    commit(&at, "box");
    assert!(run_push(&at, &tr).is_empty());
}

#[test]
fn a_feature_one_gm_box_from_done_stays_settled() {
    let (at, tr) = repo("pending");
    spec(&at, "305-pending", "**Status**: Filed\n");
    std::fs::write(
        format!("{at}/specs/305-pending/tasks.md"),
        "- [x] T01 a\n- [ ] T02 b\n",
    )
    .unwrap();
    std::fs::write(
        format!("{at}/specs/305-pending/gm-review.jsonl"),
        "{\"row\": 1}\n{\"reviewed\": 1}\n\n",
    )
    .unwrap();
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "base"]);
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::write(format!("{at}/specs/305-pending/gm-review.jsonl"), "").unwrap();
    commit(&at, "reviewed");
    assert!(refused(
        &run_push(&at, &tr),
        "305-pending/spec.md: closed before"
    ));
    assert_eq!(
        run(
            &format!("cd {at} && scripts/sync-with-main.sh push"),
            "/",
            &tr
        )
        .len(),
        1
    );
    git(&at, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert!(run_push(&at, &tr).is_empty());
    assert!(run("scripts/sync-with-main.sh done", "/no/such", &tr).is_empty());
    assert!(run("echo sync-with-main.sh", &at, &tr).is_empty());
}

#[test]
fn a_feature_closed_by_every_task_and_one_removed() {
    let (at, tr) = repo("gone");
    spec(&at, "306-gone", "**Status**: Done\n");
    spec(&at, "307-tasks", "**Status**: In progress\n");
    std::fs::write(format!("{at}/specs/307-tasks/tasks.md"), "- [x] T01 a\n").unwrap();
    git(&at, &["add", "."]);
    git(&at, &["commit", "-q", "-m", "base"]);
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::remove_dir_all(format!("{at}/specs/306-gone")).unwrap();
    std::fs::write(
        format!("{at}/specs/307-tasks/tasks.md"),
        "- [x] T01 a\n- [ ] T02 new\n",
    )
    .unwrap();
    commit(&at, "gone");
    assert!(refused(
        &run_push(&at, &tr),
        "307-tasks/spec.md: closed before"
    ));
}
