//! 451 T113: a triple-quoted string read in time. The pattern `readme_hooks` dropped a Python program's triple-quoted text with
//! (`(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''`) took a backslash and the character after it, or the backslash alone, so an
//! opening nothing closes, followed by n backslashes, cost its backtracking search 2^n tries: the guard gave no answer in 10 s on
//! forty (measured 2026-11-21, the T113 plan section). The text is read here in a process of its own - this test run again as that
//! process - under a deadline.

use std::process::Command;
use std::time::{Duration, Instant};

use super::super::triple_quoted_spans;

/// The variable that makes a child run read the text.
const CHILD: &str = "L7R_SHAPE_TRIPLE_IN_TIME";

/// An opening nothing closes, then forty escapes and a lone quote: 2^40 tries for the backtracking search.
fn unclosed() -> String {
    format!("s = '''it {} '", "\\n".repeat(40))
}

#[test]
fn a_triple_quote_nothing_closes_is_read_in_time() {
    if std::env::var_os(CHILD).is_some() {
        println!("T113 read {:?}", triple_quoted_spans(&unclosed()));
        return;
    }
    let mut child = Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "shape::tests::triples::a_triple_quote_nothing_closes_is_read_in_time",
            "--nocapture",
        ])
        .env(CHILD, "1")
        .stdout(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    let deadline = Instant::now() + Duration::from_secs(10);
    let done = loop {
        let status = child.try_wait().unwrap();
        if status.is_some() || Instant::now() > deadline {
            break status;
        }
        std::thread::sleep(Duration::from_millis(20));
    };
    let _ = child.kill();
    let out = child.wait_with_output().unwrap();
    let said = String::from_utf8_lossy(&out.stdout);
    let answered = done.is_some_and(|s| s.success());
    assert!(answered, "the read did not answer in 10 s: {said}");
    assert!(said.contains("T113 read []"), "{said}");
}

/// The scan finds the spans the pattern it replaced (built here) found, on every text of up to 6 pieces of a double quote, three, a
/// single quote, three, a backslash, a letter, a newline and a character of two bytes, and on the empty text (299,593 texts).
#[test]
fn the_scan_finds_the_triple_quoted_strings_the_pattern_found() {
    let pattern =
        crate::regex::build(r#"(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''"#).unwrap();
    let pieces = ["\"", "\"\"\"", "'", "'''", "\\", "a", "\n", "é"];
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
        let found: Vec<(usize, usize)> = pattern
            .find_iter(text)
            .map_while(Result::ok)
            .map(|m| (m.start(), m.end() - 1))
            .collect();
        assert_eq!(triple_quoted_spans(text), found, "{text:?}");
    }
}
