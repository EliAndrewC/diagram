//! `hm_shell.py`'s selftest and the decider's branches (`tests/hooks/test-shell-check-hooks.sh`, replayed through the shim over the 238-command corpus, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{
    backtick_problem, coauthor_problem, commit_dash_m_problem, commit_dash_m_rewrite, decide,
    judge, parse_error, parse_refusal, segments, verdict,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const OK: &str = "git commit -F - <<'EOF'\n236: x\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\nEOF";

fn here() -> PathBuf {
    PathBuf::from("/")
}

fn co(cmd: &str) -> Option<String> {
    coauthor_problem(cmd, Path::new("/"))
}

#[test]
fn the_parse_uses_the_tools_own_options() {
    assert_eq!(parse_error("echo hi"), None);
    assert!(parse_error("if true; then").is_some());
    assert_eq!(parse_error("shopt -s extglob\nls !(x)"), None);
    assert_eq!(parse_refusal(-1, ""), None);
    assert_eq!(
        parse_refusal(2, "").as_deref(),
        Some("bash refused to parse the command (exit 2)")
    );
    assert_eq!(parse_refusal(2, "bad").as_deref(), Some("bad"));
}

#[test]
fn a_backtick_that_would_run_is_named() {
    assert!(backtick_problem("echo \"use `make quick` first\"").is_some());
    assert!(backtick_problem("cat <<EOF\nsee `make done`\nEOF").is_some());
    assert_eq!(backtick_problem("echo 'use `make quick`'"), None);
    assert_eq!(backtick_problem("cat <<'EOF'\nsee `make done`\nEOF"), None);
    assert_eq!(backtick_problem("x=$(date)"), None);
    let many = backtick_problem("echo \"`a` `b` `c` `d`\"").unwrap();
    assert!(many.ends_with("(and 1 more)"));
}

#[test]
fn a_dash_m_that_needs_a_heredoc_is_named() {
    assert_eq!(
        commit_dash_m_problem("git commit -m \"a plain message\""),
        None
    );
    assert_eq!(
        commit_dash_m_problem("git commit -am 'a plain message'"),
        None
    );
    assert!(
        commit_dash_m_problem("git commit -m \"the pond's own \"center\" thing\"")
            .unwrap()
            .contains("several quoted pieces")
    );
    assert!(commit_dash_m_problem("git commit -m \"one\" -m \"two\"")
        .unwrap()
        .contains("2 separate"));
    assert!(
        commit_dash_m_problem("git commit -m \"line one\nline two\"")
            .unwrap()
            .contains("newline")
    );
    assert!(commit_dash_m_problem("git commit -am \"line one\nline two\"").is_some());
    assert!(commit_dash_m_problem(r#"git commit -m "say \"hi\"""#)
        .unwrap()
        .contains("double quote"));
    assert_eq!(commit_dash_m_problem("echo \"one\" \"two\""), None);
    assert_eq!(commit_dash_m_problem("git log --grep \"a \"b\" c\""), None);
    assert!(
        commit_dash_m_problem("A=b sudo /usr/bin/git --no-pager commit --message=\"a\nb\"")
            .is_some()
    );
    assert!(commit_dash_m_problem("git commit -m\"a\nb\"").is_some());
    assert_eq!(commit_dash_m_problem("A=b"), None);
    assert_eq!(commit_dash_m_problem("git -q"), None);
}

#[test]
fn a_co_author_arrives_by_every_route() {
    assert_eq!(co(OK), None);
    assert!(co(&OK.replace("noreply@", "duplicate@")).is_some());
    assert!(
        co("git commit -m 'x' --trailer 'Co-authored-by: Someone <other@example.com>'").is_some()
    );
    assert!(co("git commit -m 'x' --trailer='Co-authored-by: nobody'")
        .unwrap()
        .contains("'nobody'"));
    assert_eq!(
        co("git commit -F - <<'EOF'\nx\n\nClaude-Session: https://example\nEOF"),
        None
    );
    let dir = crate::shared::tempdir::TempDir::new("guard-shell-msg");
    let f = dir.join("msg");
    std::fs::write(&f, "x\n\nCo-Authored-By: A <a@b.c>\n").unwrap();
    let path = f.to_string_lossy();
    assert!(co(&format!("git commit -F {path}")).is_some());
    assert!(co(&format!("git commit --file={path}")).is_some());
    assert_eq!(co("git commit -F /no/such"), None);
    std::fs::write(&f, "x".repeat(200_000)).unwrap();
    assert_eq!(co(&format!("git commit -F {path}")), None);
}

#[test]
fn an_unambiguous_message_is_rewritten() {
    let rw = commit_dash_m_rewrite("git add x && git commit -q -m \"one\ntwo\" -m 'Co-Authored-By: C <noreply@anthropic.com>' && git log -1");
    assert_eq!(rw.as_deref(), Some("git add x && git commit -q -F - <<'EOF' && git log -1\none\ntwo\n\nCo-Authored-By: C <noreply@anthropic.com>\nEOF"));
    assert_eq!(
        commit_dash_m_rewrite("git commit -am \"a\nb\"").as_deref(),
        Some("git commit -a -F - <<'EOF'\na\nb\nEOF")
    );
    assert_eq!(
        commit_dash_m_rewrite("git commit -m 'say \"hi\"\nEOF'").as_deref(),
        Some("git commit -F - <<'EOF_'\nsay \"hi\"\nEOF\nEOF_")
    );
    assert_eq!(
        commit_dash_m_rewrite("git commit -m \"a\nb\"\necho next").as_deref(),
        Some("git commit -F - <<'EOF'\na\nb\nEOF\necho next")
    );
    assert_eq!(
        commit_dash_m_rewrite("git commit -am 'one\ntwo' -am 'three'").as_deref(),
        Some("git commit -a -F - <<'EOF' -a\none\ntwo\n\nthree\nEOF")
    );
    for refused in [
        "git commit -m \"the pond's own \"center\" thing\"",
        "git commit -m \"costs $5\nnow\"",
        "git commit -m \"a\nb\" && cat <<'X'\nx\nX",
        "git commit -m \"a\nb\"; git commit -m \"c\nd\"",
        "git commit -m \"a\nb\" -F f",
        "git commit -m\"a\nb\"",
        "git commit -m",
        "git commit -q",
        "ls",
        "git commit -m x",
        "git commit -m 'a' -m 'a'",
        "git commit -m '`a`\nb'  'x",
    ] {
        assert_eq!(commit_dash_m_rewrite(refused), None, "{refused}");
    }
}

#[test]
fn words_are_kept_as_written() {
    let segs = segments("a\\ b 'c' \"d\\\"e\" 'open; next");
    assert_eq!(segs[0][0].value, "a b");
    assert_eq!(segs[0][1].raw, "'c'");
    assert_eq!(segs[0][2].value, "d\"e");
    assert_eq!(segs[0][3].value, "open; next");
    assert_eq!(segments(" ; | ").len(), 0);
    assert_eq!(segments("\"unterminated")[0][0].raw, "\"unterminated");
    assert_eq!(segments("x\\")[0][0].value, "x\\");
}

fn run(cmd: &str) -> Vec<Answer> {
    crate::shared::log::quiet();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": cmd, "description": "d"}}),
    };
    judge(&e, &Session::from_input(&e.input), here())
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn the_answers() {
    assert!(refused(&run("if true; then"), "rule \"parse\""));
    assert!(refused(
        &run("echo \"a `b`\""),
        "rule \"executing-backtick\""
    ));
    assert!(refused(
        &run("git commit -m \"a \"b\" c\""),
        "rule \"commit-dash-m\""
    ));
    assert!(refused(
        &run("git commit -m 'x' --trailer 'Co-authored-by: A <a@b.c>'"),
        "rule \"coauthor-address\""
    ));
    assert!(run("echo fine").is_empty());
    assert!(run("").is_empty());
    assert!(run("echo \"a `b`\"  # SHELL_CHECK_OK: quoting a transcript verbatim").is_empty());
    assert!(refused(
        &run("echo \"a `b`\"  # SHELL_CHECK_OK"),
        "with no reason"
    ));
    let got = run("git commit -m 'a\nb'");
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == "git commit -F - <<'EOF'\na\nb\nEOF" && v["description"] == "d" && n.contains("moved from -m"))
    );
    assert!(verdict("echo ok", Path::new("/")).is_none());
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"cwd": "/", "tool_input": {"command": "echo ok"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

#[test]
fn plain_words_need_no_parse_and_a_reserved_word_or_a_quote_still_gets_one() {
    assert!(super::plain_words("ls -la /tmp/a.txt"));
    assert!(super::plain_words("make test-file FILE=tests/x.py"));
    assert!(!super::plain_words("if true"));
    assert!(!super::plain_words("echo 'a'"));
    assert!(!super::plain_words("ls; ls"));
    assert!(!super::plain_words("cat <a"));
    assert!(!super::plain_words("a\nb"));
    let event = crate::protocol::Event {
        name: "PreToolUse".to_owned(),
        input: serde_json::json!({"cwd": "/tmp", "tool_name": "Bash", "tool_input": {"command": "echo 'a'"}}),
    };
    let session = crate::shared::session::Session::from_input(&event.input);
    assert!(super::judge(&event, &session, "/".into()).is_empty());
    let unfinished = crate::protocol::Event {
        name: "PreToolUse".to_owned(),
        input: serde_json::json!({"tool_name": "Bash", "tool_input": {"command": "if true"}}),
    };
    assert!(!super::judge(&unfinished, &session, "/".into()).is_empty());
}
