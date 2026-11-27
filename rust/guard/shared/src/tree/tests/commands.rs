//! 451 T417: `commands`, every simple command a command runs as the walk splits it - the context cap's wrap-up band asks each one.

use crate::spelled::program_of;
use crate::tree::{command_head, commands};

fn programs(cmd: &str) -> Vec<String> {
    commands(cmd)
        .iter()
        .map(|c| program_of(&command_head(c)).to_owned())
        .collect()
}

#[test]
fn every_command_is_listed_and_no_quoted_or_heredoc_text_is_one() {
    assert_eq!(
        programs("cd /t && export A=1 B=2 && L7R_X=1 make decide F=451 T=T1 2>&1 | tail -5; git -C /t status"),
        ["cd", "export", "make", "tail", "git"]
    );
    // a quoted command, a heredoc's body: no command of their own
    assert_eq!(programs("echo \"make decide; rm -rf x\""), ["echo"]);
    assert_eq!(
        programs("cat > /tmp/x <<'EOF'\nmake decide\nrm -rf y\nEOF\nmake quick"),
        ["cat", "make"]
    );
    // a subshell's and a substitution's commands are listed, a substitution in double quotes too (bash runs it), before its word's
    assert_eq!(
        programs("(cd /t && make decide) && make task-add TITLE=\"$(rm -rf z)\""),
        ["cd", "make", "rm", "make"]
    );
    assert_eq!(programs("make task-add TITLE=$(rm -rf z)"), ["rm", "make"]);
    assert!(commands("").is_empty());
}

#[test]
fn a_command_is_shown_as_it_was_written() {
    let c = commands("echo \"make decide\" 'a;b'");
    assert_eq!(c.len(), 1);
    assert_eq!(crate::tree::shown(&c[0]), "echo \"make decide\" 'a;b'");
    assert_eq!(crate::tree::shown("ls"), "ls");
}

#[test]
fn a_redirect_is_marked_apart_from_its_programs_own_write() {
    let marks = |cmd: &str| -> Vec<(Option<String>, bool)> {
        crate::tree::walk(cmd, Some("/t"), "", "/h")
            .targets
            .into_iter()
            .map(|t| (t.path, t.redirect))
            .collect()
    };
    // 451 T427: `make`'s write where it stands is no redirect; its `> f` is
    assert_eq!(
        marks("make decide > a.rs 2>&1; git -C /t/y commit -m x >> /tmp/l"),
        [
            (Some("/t".to_owned()), false),
            (Some("/t/a.rs".to_owned()), true),
            (Some("/t/y".to_owned()), false),
            (Some("/tmp/l".to_owned()), true),
        ]
    );
}
