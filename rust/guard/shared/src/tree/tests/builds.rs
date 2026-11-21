//! 451 T97: what a command builds of the walk's patterns. A hook event is a process of its own and a pattern is built on its first
//! use in it, so every Bash call paid the walk's first builds - 3.2-8.6 ms a first walk against 9-57 us a second (T93, measured
//! 2026-11-21), 10 patterns reached by every command of T93's 9,646 (T97, measured 2026-11-21). Each command is walked here in a
//! process of its own, this test run again as that process, and its builds counted by `regex::BUILT`.

use std::process::Command;

use super::{input, judge, walk_judged};

/// The variable naming the command a child run walks.
const CHILD: &str = "L7R_TREE_BUILDS_OF";

/// Each command and the patterns it builds, walked as the event log's `bash_writes` walks it and as main-tree judges it: none for a
/// command with no `=`, quote, redirection, heredoc or Python, the one redirection pattern for `>`.
const BUILDS: [(&str, usize); 5] = [
    ("ls -la docs", 0),
    ("cd /diagram/.clones/mine && git status --short", 0),
    ("sed -n 1,20p rust/guard/shared/src/tree.rs | head -5", 0),
    ("grep -rn foo docs/ | wc -l", 0),
    ("echo hi > /tmp/x", 1),
];

#[test]
fn a_simple_command_builds_none_of_the_walk_s_patterns() {
    if let Some(cmd) = std::env::var_os(CHILD) {
        let cmd = cmd.to_string_lossy();
        let _ = walk_judged(&cmd, Some("/w"), "", "/home/u");
        let mine = Some("/diagram/.clones/mine");
        let _ = judge(&input(&cmd, "/w"), "/diagram", mine, "/home/u", true);
        let built = crate::regex::BUILT.lock().unwrap().clone();
        println!("T97 built {}", serde_json::to_string(&built).unwrap());
        return;
    }
    for (cmd, want) in BUILDS {
        let out = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "tree::tests::builds::a_simple_command_builds_none_of_the_walk_s_patterns",
                "--nocapture",
            ])
            .env(CHILD, cmd)
            .output()
            .unwrap();
        let said = String::from_utf8_lossy(&out.stdout);
        let built: Vec<String> = said
            .lines()
            .find_map(|l| l.strip_prefix("T97 built "))
            .map_or_else(
                || panic!("{cmd}: the child said {said}"),
                |j| serde_json::from_str(j).unwrap(),
            );
        assert_eq!(built.len(), want, "{cmd} built {built:#?}");
    }
}

/// The plain read of a quoted body answers as the pattern it replaced (`PLAIN_QUOTE_BODY`, built here) on every character to U+3100
/// (every `White_Space` one among them), U+180E (`White_Space` before Unicode 6.3), U+200B and U+FEFF, alone and inside a word, and on
/// the empty body.
#[test]
fn a_plain_quote_body_is_read_as_its_pattern_read_it() {
    let pattern = crate::regex::build(r"^[^\s;|&()<>`\n]*$").unwrap();
    let chars = (0..=0x3100_u32)
        .chain([0x180E, 0x200B, 0xFEFF])
        .filter_map(char::from_u32);
    for c in chars {
        for body in [c.to_string(), format!("a{c}b")] {
            assert_eq!(
                super::super::plain_quote_body(&body),
                pattern.is_match(&body).unwrap(),
                "U+{:04X}",
                u32::from(c)
            );
        }
    }
    assert!(super::super::plain_quote_body(""));
}
