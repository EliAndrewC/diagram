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

/// Where each redirect of `cmd` lands, standing in `/t`.
fn redirected(cmd: &str) -> Vec<Option<String>> {
    crate::tree::walk(cmd, Some("/t"), "", "/h")
        .targets
        .into_iter()
        .filter(|t| t.redirect)
        .map(|t| t.path)
        .collect()
}

fn at(paths: &[&str]) -> Vec<Option<String>> {
    paths.iter().map(|p| Some((*p).to_owned())).collect()
}

#[test]
fn a_redirect_spelled_with_an_ampersand_writes_its_file_unless_an_fd_follows() {
    // 451 T433: `>& FILE` and `>&FILE` send both streams to FILE, as `&>` does; `>&2.log` is a file, its word no fd (measured
    // 2026-11-27 under bash: `echo w >&2.log` made `2.log`, `echo z >& 2` made nothing)
    assert_eq!(
        redirected("tail -n 0 x >& rust/a.rs"),
        at(&["/t/rust/a.rs"])
    );
    assert_eq!(redirected("tail -n 0 x >&rust/a.rs"), at(&["/t/rust/a.rs"]));
    assert_eq!(redirected("echo w >&2.log"), at(&["/t/2.log"]));
    assert_eq!(redirected("echo w 1>&/d/x.rs"), at(&["/d/x.rs"]));
    // `&>` and `&>>` in their command's segment, not cut off by the `&` as a job's end
    let walked = crate::tree::walk("echo v &> f6; echo u &>> f7", Some("/t"), "", "/h");
    let heads: Vec<(Option<String>, String)> = walked
        .targets
        .into_iter()
        .map(|t| (t.path, t.head))
        .collect();
    assert_eq!(
        heads,
        [
            (Some("/t/f6".to_owned()), "echo v &> f6".to_owned()),
            (Some("/t/f7".to_owned()), "echo u &>> f7".to_owned())
        ]
    );
    // an fd, a closed or moved fd (`>&-x` closes it, `x` an argument: measured the same way), and /dev/null are no file written
    for cmd in [
        "echo z >&2",
        "echo z >& 2",
        "echo z 1>&2",
        "echo z >&-",
        "echo z >&-x",
        "echo z 3>&1-",
        "echo z >&2;",
        "echo z >&2|cat",
        "echo z >&/dev/null",
        "echo z >& /dev/null",
        "echo z &>/dev/null",
        "echo z &>> /dev/null",
        "make x 2>&1 | tail",
    ] {
        assert!(redirected(cmd).is_empty(), "{cmd}");
    }
}

#[test]
fn a_cds_redirect_lands_where_the_shell_stood_before_it_moved() {
    // 451 T436: bash opens a builtin's redirects before it runs, `$PWD` expanded there too (measured 2026-11-27: `cd b > out1`
    // and `cd b > $PWD/out2` standing in `a` each made `a/...`, nothing in `b`)
    assert_eq!(redirected("cd /u > out1"), at(&["/t/out1"]));
    assert_eq!(
        redirected("cd /u > $PWD/out2 && echo x > y"),
        at(&["/t/out2", "/u/y"])
    );
    assert_eq!(redirected("cd /u > /diagram/x.rs"), at(&["/diagram/x.rs"]));
    assert_eq!(
        redirected("cd /v &> n; pushd /u >> l; popd > m"),
        at(&["/t/n", "/v/l", "/u/m"])
    );
    assert_eq!(redirected("cd /u >& /diagram/x.rs"), at(&["/diagram/x.rs"]));
    let walked = crate::tree::walk("cd /diagram/x > /tmp/l", Some("/t"), "/diagram", "/h");
    let placed: Vec<(&str, bool)> = walked
        .targets
        .iter()
        .map(|t| (t.class, t.redirect))
        .collect();
    assert_eq!(
        (placed, walked.final_dir.as_deref()),
        (vec![("elsewhere", true)], Some("/diagram/x"))
    );
}
