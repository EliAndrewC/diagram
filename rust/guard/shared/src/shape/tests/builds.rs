//! 451 T103: what a command builds of shape's patterns. A hook event is a process of its own and a pattern is built on its first use
//! in it, so every Bash start built the strips' patterns whatever the command held: `HEREDOC`, `QUOTED`, `QUOTED_HEREDOC` and
//! `UNQUOTED_HEREDOC` for 9,646 of T93's 9,646 commands, `INTERPRETER_C` for most (measured 2026-11-21, the T103 plan section's item 4).
//! Each command is stripped here as the guards strip it, in a process of its own - this test run again as that process - and its
//! builds counted by `regex::BUILT`.

use std::process::Command;

use super::super::{executing_backticks, strip_heredocs, strip_quotes};

/// The variable naming the command a child run strips.
const CHILD: &str = "L7R_SHAPE_BUILDS_OF";

/// Each command and the patterns it builds, stripped as `no_poll_hooks` and `make_only_hooks` strip a command
/// (`strip_quotes(&strip_heredocs(cmd))`) and as `shell_check_hooks` reads its backticks (`executing_backticks(cmd, false)`): none
/// for a command with no `<<` and no `-c` before a quote, a redirection, a backtick span and a quoted string among them (a scan reads
/// those); the interpreter's for the quote after a `-c`; the heredoc's and the quoted heredoc's for a heredoc whose delimiter is quoted,
/// its quotes gone with its body.
const BUILDS: [(&str, &[&str]); 6] = [
    ("ls -la docs", &[]),
    ("wc -l < f && sort -u f > g", &[]),
    ("echo `date` | tr a-z A-Z", &[]),
    ("grep -n 'a b' f", &[]),
    ("python3 -c 'print(1)'", &["INTERPRETER_C"]),
    ("cat <<'EOF' > f\nx\nEOF", &["HEREDOC", "QUOTED_HEREDOC"]),
];

/// The name a built pattern goes by in `shape.rs`, read from the start of its own text; another pattern by its text.
fn name(pattern: &str) -> &str {
    [
        ("(?sm)<<-?[ \\t]*", "HEREDOC"),
        ("(?sm)<<-?\\s*(?:'", "QUOTED_HEREDOC"),
        ("(?sm)<<-?\\s*([A-Za-z_]", "UNQUOTED_HEREDOC"),
        ("(?<!\\\\)`", "BACKTICK_SPAN"),
        ("(?:^|[\\s/;&|(])(?:(?:ba", "INTERPRETER_C"),
    ]
    .iter()
    .find(|(start, _)| pattern.starts_with(start))
    .map_or(pattern, |(_, n)| n)
}

#[test]
fn a_command_builds_only_the_strip_patterns_its_text_could_match() {
    if let Some(cmd) = std::env::var_os(CHILD) {
        let cmd = cmd.to_string_lossy();
        let _ = strip_quotes(&strip_heredocs(&cmd));
        let _ = executing_backticks(&cmd, false);
        let built = crate::regex::BUILT.lock().unwrap().clone();
        println!("T103 built {}", serde_json::to_string(&built).unwrap());
        return;
    }
    for (cmd, want) in BUILDS {
        let out = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "shape::tests::builds::a_command_builds_only_the_strip_patterns_its_text_could_match",
                "--nocapture",
            ])
            .env(CHILD, cmd)
            .output()
            .unwrap();
        let said = String::from_utf8_lossy(&out.stdout);
        let built: Vec<String> = said
            .lines()
            .find_map(|l| l.strip_prefix("T103 built "))
            .map_or_else(
                || panic!("{cmd}: the child said {said}"),
                |j| serde_json::from_str(j).unwrap(),
            );
        let names: Vec<&str> = built.iter().map(|p| name(p)).collect();
        assert_eq!(names, want, "{cmd} built {built:#?}");
    }
}
