//! 451 T103: a quoted string read in time. `QUOTED` (`(["'])(?:\\.|(?!\1).)*\1`) took a backslash and the character after it, or the
//! backslash alone, so a quote no later quote closes, followed by n backslashes, cost its backtracking search 2^n tries: a real
//! command of T93's corpus, a heredoc holding `T58's` and some 60 escapes, run in the background, held `no-poll-hooks` past 20 s,
//! killed (`wait::periodic` strips the command's quotes, its heredoc unstripped; measured 2026-11-21, the T103 plan section's Found and
//! left). The text is stripped here in a process of its own - this test run again as that process - under a deadline.

use std::process::Command;
use std::time::{Duration, Instant};

use super::super::strip_quotes;

/// The variable that makes a child run strip the text.
const CHILD: &str = "L7R_SHAPE_QUOTE_IN_TIME";

/// A quote no later quote closes, then forty escapes: 2^40 tries for the backtracking search.
fn unclosed() -> String {
    format!("echo it's {}", "\\n".repeat(40))
}

#[test]
fn a_quote_no_later_quote_closes_is_read_in_time() {
    if std::env::var_os(CHILD).is_some() {
        println!("T103 stripped {}", strip_quotes(&unclosed()));
        return;
    }
    let mut child = Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "shape::tests::quotes::a_quote_no_later_quote_closes_is_read_in_time",
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
    assert!(
        done.is_some_and(|s| s.success()),
        "the strip did not answer in 10 s: {said}"
    );
    assert!(
        said.contains(&format!("T103 stripped {}", unclosed())),
        "{said}"
    );
}

/// The scan finds the spans the pattern it replaced (`QUOTED`, built here) found, on every text to 7 characters over a double and a
/// single quote, a backslash, a letter, a newline and a character of two bytes, and on the empty text.
#[test]
fn the_scan_finds_the_quoted_strings_the_pattern_found() {
    let pattern = crate::regex::build(r#"(?s)(["'])(?:\\.|(?!\1).)*\1"#).unwrap();
    let mut texts = vec![String::new()];
    let mut longest = vec![String::new()];
    for _ in 0..7 {
        longest = longest
            .iter()
            .flat_map(|t| ['"', '\'', '\\', 'a', '\n', 'é'].map(|c| format!("{t}{c}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let found: Vec<(usize, usize)> = pattern
            .find_iter(text)
            .map_while(Result::ok)
            .map(|m| (m.start(), m.end() - 1))
            .collect();
        assert_eq!(super::super::quoted_spans(text), found, "{text:?}");
    }
}
