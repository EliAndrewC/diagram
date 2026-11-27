//! A program read by its name through each spelling, and a name that only ends in it left alone.

use super::options;
use super::{before, command_at, name_of, names, program_of, WRAPPER_WORDS};

#[test]
fn a_word_names_its_program_by_its_last_path_part() {
    for w in [
        "git",
        "/usr/bin/git",
        "\\git",
        "\"git\"",
        "'/usr/bin/git'",
        "./git",
        "~/bin/git",
    ] {
        assert!(names(w, "git"), "{w}");
    }
    for w in [
        "/tmp/mygit",
        "legit",
        "git.sh",
        "/tmp/git/run",
        "gitk",
        "",
        ".git",
    ] {
        assert!(!names(w, "git"), "{w}");
    }
    assert_eq!(name_of("/bin/rm"), "rm");
}

#[test]
fn the_command_word_stands_past_assignments_and_wrappers() {
    let at = |cmd: &str| {
        let words: Vec<&str> = cmd.split_whitespace().collect();
        command_at(&words)
    };
    assert_eq!(at("git status"), 0);
    assert_eq!(at("A=1 B=2 git status"), 2);
    assert_eq!(at("sudo /usr/bin/env A=1 command git status"), 4);
    assert_eq!(at("timeout 60 nice git status"), 3);
    assert_eq!(at("/usr/bin/timeout 60 git"), 2);
    // a command of wrappers alone has no command word; a word with `=` that is no assignment is one
    assert_eq!(at("env"), 1);
    assert_eq!(at("timeout"), 1);
    assert_eq!(at("1=2 git"), 0);
    assert_eq!(at("=x git"), 0);
    assert_eq!(at("a-b=c git"), 0);
    assert_eq!(program_of("A=1 exec /usr/bin/git -C /x status"), "git");
    assert_eq!(program_of("timeout 5 \\rm -rf x"), "rm");
    // a wrapper's options, each with its value where it takes one
    assert_eq!(program_of("env -i git status"), "git");
    assert_eq!(program_of("sudo -E -u x /usr/bin/git status"), "git");
    assert_eq!(program_of("env -u A -C /x B=1 nice -n 5 git status"), "git");
    assert_eq!(program_of("timeout -k 5 -s KILL 60 git status"), "git");
    assert_eq!(program_of("exec -a name git status"), "git");
    assert_eq!(program_of("sudo -- git status"), "git");
    assert_eq!(program_of("sudo --user=x git"), "git");
    assert_eq!(program_of("sudo -u"), "");
    assert_eq!(options("env", &["-", "git"]), 0);
    assert_eq!(options("nohup", &["-x", "-n", "git"]), 2);
    // a lookup runs nothing
    assert_eq!(program_of("command -v git"), "command");
    assert_eq!(program_of("A=1 command -V make"), "command");
    assert_eq!(program_of("command -p git status"), "git");
    assert_eq!(program_of("env"), "");
    assert_eq!(program_of(""), "");
}

#[test]
fn the_pattern_texts_read_the_spellings_the_reader_reads() {
    let re = crate::regex::build(&format!(r"^(?:{WRAPPER_WORDS})*{}git\b", before("git"))).unwrap();
    for cmd in [
        "git x",
        "/usr/bin/git x",
        "\\git x",
        "\"git\" x",
        "command git x",
        "/usr/bin/env '/usr/bin/git' x",
        "timeout 60 sudo git x",
        "sudo -E -u x git x",
        "env -i /usr/bin/git x",
        "timeout -k 5 60 nice -n 5 git x",
        "xargs -0 git x",
        "xargs -I {} git x",
        "/usr/bin/xargs -r -n 50 git x",
    ] {
        assert!(re.is_match(cmd).unwrap(), "{cmd}");
    }
    for cmd in [
        "X=/usr/bin/git x",
        "/tmp/mygit x",
        "legit x",
        "echo git x",
        "/tmp/git/run x",
        "git.sh x",
        "/usr/bin/git-lfs x",
    ] {
        assert!(!re.is_match(cmd).unwrap(), "{cmd}");
    }
}

/// 451 T306: `xargs` runs the program after its own options, each with its value where it takes one (`-I {}`, `-n 50`, `-a list`;
/// `-n50` and `--max-args=5` are one word): `printf '%s\0' a b | xargs -0 git add --`, five times in the week's commands, was a
/// write no reader of the command word saw.
#[test]
fn xargs_runs_the_program_after_its_own_options() {
    assert_eq!(program_of("xargs -0 git add --"), "git");
    assert_eq!(program_of("xargs -I {} git show {}"), "git");
    assert_eq!(program_of("xargs -r -n 50 /usr/bin/git log"), "git");
    assert_eq!(program_of("xargs -r -n50 git log"), "git");
    assert_eq!(program_of("xargs --max-args=5 -a list rm -f"), "rm");
    assert_eq!(
        program_of("/usr/bin/xargs -P 4 -L 1 -d , -E x -s 99 git add"),
        "git"
    );
    assert_eq!(program_of("xargs"), "");
}
