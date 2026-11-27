//! The decider on the shapes of its rules (`tests/hooks/test-repo-safety-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::json;

use super::{decide, verdict};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn v(cmd: &str) -> Option<&'static str> {
    verdict(cmd, false)
}

#[test]
fn a_force_push_is_refused_however_it_is_prefixed() {
    for cmd in [
        "git push --force origin main",
        "git push -f origin main",
        "git push --force-with-lease",
        "git --force push",
        "FOO=\"bar\" git push --force origin main",
        "timeout 5 env A=b git push -f",
        "ls && git push -f",
    ] {
        assert_eq!(v(cmd), Some("force-push"), "{cmd}");
    }
}

#[test]
fn a_history_rewrite_is_refused_and_the_flag_forbidding_it_is_not() {
    for cmd in [
        "git rebase main",
        "git -C x rebase main",
        "git pull --rebase origin main",
        "git merge --squash x",
        "git commit --amend",
    ] {
        assert_eq!(v(cmd), Some("history-rewrite"), "{cmd}");
    }
    assert_eq!(v("git pull --no-rebase origin main"), None);
    // its abort rewrites nothing (451 T292: the landing's refusal of a rebase in progress prints it) - alone, never with more after it
    assert_eq!(v("git -C x rebase --abort"), None);
    // ...and every other command that refusal prints (`rust/gate/crates/land/src/land/unfinished.rs`) is no rewrite
    for cmd in [
        "git -C x am --abort",
        "git -C x -c core.editor=true cherry-pick --continue",
        "git -C x -c core.editor=true merge --continue",
        "git -C x -c core.editor=true revert --continue",
        "git -C x cherry-pick --abort",
        "git -C x add -- a b",
        "git -C x restore --staged -- a",
    ] {
        assert_eq!(v(cmd), None, "{cmd}");
    }
    assert_eq!(v("git rebase --abort && git push"), None);
    for cmd in [
        "git rebase --abort main",
        "git rebase --abort; git rebase main",
        "git rebase --continue",
    ] {
        assert_eq!(v(cmd), Some("history-rewrite"), "{cmd}");
    }
}

#[test]
fn a_git_write_at_the_mount_is_refused_a_read_is_not_and_the_escape_lifts_it() {
    assert_eq!(v("git -C /host-l7r-repo commit -a"), Some("host-git-write"));
    assert_eq!(
        v("cd /host-l7r-repo/setting && git add x"),
        Some("host-git-write")
    );
    assert_eq!(v("git -C /host-l7r-repo log"), None);
    assert_eq!(verdict("git -C /host-l7r-repo commit -a", true), None);
    assert_eq!(verdict("git push -f", true), Some("force-push"));
}

#[test]
fn payload_is_not_a_command() {
    assert_eq!(v("git commit -m \"never git push --force\""), None);
    assert_eq!(v("git commit -m 'no git commit --amend'"), None);
    assert_eq!(v("cat <<'EOF'\ngit push --force\nEOF"), None);
    assert_eq!(v(""), None);
}

#[test]
fn an_escape_is_recorded_with_its_reason() {
    crate::shared::log::quiet();
    let why = "a read misdetected, unique to this firing record test";
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": format!("git -C /host-l7r-repo add x  # HOST_GIT_OK: {why}")}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
    let dir = std::env::var("GUARD_LOG_DIR").unwrap();
    let recorded = std::fs::read_dir(dir).unwrap().flatten().any(|f| {
        let text = std::fs::read_to_string(f.path()).unwrap_or_default();
        text.contains(why) && text.contains("host-git-ok") && text.contains("escaped")
    });
    assert!(recorded);
}

#[test]
fn the_refusals_and_the_escape() {
    crate::shared::log::quiet();
    let run = |cmd: &str| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Bash", "tool_input": {"command": cmd}}),
        };
        decide(&e, &Session::from_input(&e.input))
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    assert!(refused(&run("git push -f"), "BLOCKED: git push --force."));
    assert!(refused(&run("git rebase x"), "BLOCKED: a history rewrite"));
    assert!(refused(
        &run("git -C /host-l7r-repo add x"),
        "BLOCKED: a git write against"
    ));
    assert!(
        run("git -C /host-l7r-repo add x  # HOST_GIT_OK: a read misdetected by the guard")
            .is_empty()
    );
    assert!(refused(
        &run("git -C /host-l7r-repo add x  # HOST_GIT_OK"),
        "with no reason"
    ));
    assert!(run("ls").is_empty());
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({}),
    };
    assert!(decide(&bare, &Session::from_input(&bare.input)).is_empty());
}

/// 451 T295: git spelled by its path, behind a `\` or a wrapper is git; a program whose name only ends in git is not.
#[test]
fn git_is_read_however_it_is_spelled() {
    for s in [
        "/usr/bin/",
        "\\",
        "command ",
        "env ",
        "/usr/bin/env ",
        "sudo /usr/bin/",
        "exec ",
        "sudo -u x ",
        "env -i A=1 ",
        "A=1 nice ",
        "xargs -0 ",
        "xargs -I {} ",
    ] {
        for (rest, rule) in [
            ("git push --force origin main", "force-push"),
            ("git --force push", "force-push"),
            ("git rebase main", "history-rewrite"),
            ("git -C /x pull --rebase", "history-rewrite"),
            ("git merge --squash b", "history-rewrite"),
            ("git commit --amend", "history-rewrite"),
            ("git -C /host-l7r-repo commit -a", "host-git-write"),
        ] {
            assert_eq!(v(&format!("{s}{rest}")), Some(rule), "{s}{rest}");
            assert_eq!(v(&format!("ls && {s}{rest}")), Some(rule), "{s}{rest}");
        }
    }
    for cmd in [
        "/tmp/mygit rebase main",
        "legit commit --amend",
        "/tmp/git/run push --force",
        "echo /usr/bin/git rebase main",
    ] {
        assert_eq!(v(cmd), None, "{cmd}");
    }
}

/// 451 T453: a quoted git is git (`"git" push -f` was blanked as a payload and passed); a quoted word that is no command stays one.
#[test]
fn a_quoted_git_is_read_as_git() {
    for (cmd, rule) in [
        ("\"git\" push --force origin main", "force-push"),
        ("'git' rebase main", "history-rewrite"),
        ("ls && \"/usr/bin/git\" commit --amend", "history-rewrite"),
    ] {
        assert_eq!(v(cmd), Some(rule), "{cmd}");
    }
    for cmd in [
        "echo \"git\" push --force",
        "FOO=\"git\" push -f",
        "git commit -m \"git push --force\"",
        "git log --grep \"rebase\"",
    ] {
        assert_eq!(v(cmd), None, "{cmd}");
    }
}
