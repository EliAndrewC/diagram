//! 451 T295: the walk reads a program by its name however the command spells it - a path (`/usr/bin/git`), a `\` that skips an
//! alias (`\git`), quotes (`"git"`), a wrapper spelled by its path (`/usr/bin/env git`) - where it read git by its bare name alone:
//! `/usr/bin/git worktree add <clones>/x` was no write, so every guard reading the walk passed it (measured 2026-11-26). A program
//! whose name only ends in the one asked for (`/tmp/mygit`) is another program.

use super::{mirror, walk};
use crate::tree::command_head;

type Place = (Option<String>, &'static str, &'static str);

fn writes(cmd: &str, at: &str, m: &str) -> Vec<Place> {
    walk(cmd, Some(at), m, "/home/u")
        .targets
        .into_iter()
        .map(|t| (t.path, t.class, t.how))
        .collect()
}

const SPELLINGS: [&str; 16] = [
    "env -i ",
    "sudo -E -u x ",
    "nice -n 5 /usr/bin/",
    "timeout -k 5 60 ",
    "/usr/bin/",
    "\\",
    "command ",
    "env ",
    "/usr/bin/env ",
    "exec /usr/bin/",
    "sudo \\",
    "timeout 60 /usr/bin/",
    "A=1 /usr/local/bin/",
    // 451 T306: a program `xargs` runs, past its own options and their values
    "xargs -0 ",
    "xargs -I {} ",
    "/usr/bin/xargs -r -n 50 ",
];

#[test]
fn git_spelled_by_a_path_a_backslash_or_behind_a_wrapper_writes_what_git_writes() {
    let (_d, m, c) = mirror("spelled-git");
    for rest in [
        format!("git worktree add {m}/.clones/x HEAD"),
        format!("git -C {m} checkout -- a.py"),
        "git commit -m x".to_owned(),
    ] {
        let bare = writes(&rest, &c, &m);
        assert!(!bare.is_empty(), "{rest}");
        for s in SPELLINGS {
            assert_eq!(writes(&format!("{s}{rest}"), &c, &m), bare, "{s}{rest}");
        }
        let quoted = rest.replacen("git", "\"git\"", 1);
        assert_eq!(writes(&quoted, &c, &m), bare, "{quoted}");
    }
}

#[test]
fn a_file_tool_and_make_are_read_the_same_way() {
    let (_d, m, c) = mirror("spelled-tools");
    for rest in [
        format!("rm -rf {m}/.clones/x"),
        format!("cp /tmp/a {m}/b"),
        format!("sed -i s/a/b/ {m}/b"),
        "make static".to_owned(),
        format!("python3 -c 'open(\"{m}/b\", \"w\")'"),
    ] {
        let bare = writes(&rest, &c, &m);
        assert!(!bare.is_empty(), "{rest}");
        for s in SPELLINGS {
            assert_eq!(writes(&format!("{s}{rest}"), &c, &m), bare, "{s}{rest}");
        }
    }
}

#[test]
fn a_program_whose_name_only_ends_in_git_is_not_git() {
    let (_d, m, c) = mirror("spelled-not");
    for cmd in [
        format!("/tmp/mygit worktree add {m}/.clones/x HEAD"),
        format!("mygit worktree add {m}/.clones/x HEAD"),
        format!("/tmp/git.sh worktree add {m}/.clones/x HEAD"),
        format!("legit worktree add {m}/.clones/x HEAD"),
        format!("/tmp/git/run worktree add {m}/.clones/x HEAD"),
        format!("/tmp/myrm -rf {m}/.clones/x"),
        // a lookup runs nothing
        "command -v git".to_owned(),
        "command -V make".to_owned(),
        format!("command -v rm {m}/.clones/x"),
    ] {
        assert_eq!(writes(&cmd, &c, &m), [], "{cmd}");
    }
}

#[test]
fn a_head_keeps_a_wrapper_spelled_by_its_path() {
    assert_eq!(
        command_head("A=1 /usr/bin/env B=2 /usr/bin/git status"),
        "/usr/bin/env /usr/bin/git status"
    );
    assert_eq!(
        command_head("/usr/bin/timeout 60 A=1 make x"),
        "/usr/bin/timeout 60 make x"
    );
}
