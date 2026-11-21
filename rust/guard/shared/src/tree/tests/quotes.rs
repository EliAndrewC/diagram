//! 451 T112: a quoted string read in time by the walk. `QUOTED` (`(?s)(["'])((?:\\.|(?!\1).)*)\1`) took a backslash and the
//! character after it, or the backslash alone, so a quote no later quote closes, followed by n backslashes, cost its backtracking
//! search 2^n tries: `<a write>; echo it's` and forty escapes, the write each guard reads, held the house style guard, main-tree,
//! gm-tree, make-only, readme, gate-write (while a `make done` ran) and the event log's end past 10 s, killed (measured 2026-11-21,
//! the T112 plan section). The command is walked here in a process of its own - this test run again as that process - under a deadline.

use super::super::{plain_quote_body, quotes_to_paths, walk, PYTHON_C_BEFORE};
use super::answers_in_time;

/// The variable that makes a child run walk the command.
const CHILD: &str = "L7R_TREE_QUOTE_IN_TIME";

/// A write, then a quote no later quote closes and forty escapes: 2^40 tries for the backtracking search.
fn unclosed() -> String {
    format!("echo hi > f.md; echo it's {}", "\\n".repeat(40))
}

#[test]
fn a_quote_no_later_quote_closes_is_walked_in_time() {
    if std::env::var_os(CHILD).is_some() {
        let w = walk(&unclosed(), Some("/w"), "", "/home/u");
        let paths: Vec<_> = w.targets.iter().map(|t| t.path.clone()).collect();
        println!("T112 walked {paths:?}");
        return;
    }
    let name = "tree::tests::quotes::a_quote_no_later_quote_closes_is_walked_in_time";
    let (passed, said) = answers_in_time(name, CHILD, 10);
    assert!(passed, "the walk did not answer in 10 s: {said}");
    let walked = said.contains(r#"T112 walked [Some("/w/f.md")]"#);
    assert!(walked, "{said}");
}

/// What `quotes_to_paths` made of a command with `QUOTED`, the pattern it replaced, built here: its replacement as it stood.
fn by_the_pattern(pattern: &fancy_regex::Regex, cmd: &str) -> (String, Vec<(char, String)>) {
    let mut programs = Vec::new();
    let text = pattern
        .replace_all(cmd, |c: &fancy_regex::Captures| {
            let body = c.get(2).map_or("", |m| m.as_str());
            let quote = c.get(1).map_or("", |m| m.as_str());
            let at = c.get(0).map_or(0, |m| m.start());
            if PYTHON_C_BEFORE.is_match(&cmd[..at]) {
                programs.push((quote.chars().next().unwrap_or('"'), body.to_owned()));
                format!("__py_c_{}__", programs.len() - 1)
            } else if !body.is_empty() && plain_quote_body(body) {
                body.to_owned()
            } else {
                quote.repeat(2)
            }
        })
        .into_owned();
    (text, programs)
}

/// The scan's reading is the pattern's on every text of up to 6 pieces over a double and a single quote, a backslash, a letter, a
/// newline (a body that is no plain word), a character of two bytes and a `python3 -c ` (a program carried out), and on the empty
/// text: the text it leaves and the programs it carries out.
#[test]
fn the_scan_reads_each_quoted_string_as_the_pattern_read_it() {
    let pattern = crate::regex::build(r#"(?s)(["'])((?:\\.|(?!\1).)*)\1"#).unwrap();
    let pieces = ["\"", "'", "\\", "a", "\n", "é", "python3 -c "];
    let mut texts = vec![String::new()];
    let mut longest = vec![String::new()];
    for _ in 0..6 {
        longest = longest
            .iter()
            .flat_map(|t| pieces.map(|p| format!("{t}{p}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let (scan, old) = (
            quotes_to_paths(text, Vec::new()),
            by_the_pattern(&pattern, text),
        );
        assert_eq!(scan, old, "{text:?}");
    }
}
