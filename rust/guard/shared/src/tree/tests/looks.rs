//! 451 T129: the walk's scans whose one look at the character before a match - a lookbehind, a word boundary - is read by hand, so
//! each pattern runs in the regex crate's automaton, not fancy-regex's backtracking machine: each reads what its fancy pattern read,
//! and each pattern is one the regex crate runs.

use std::ops::Range;

use fancy_regex::{Captures, Regex};

use super::super::bind::{printf_v_names, sourced, PRINTF_V, SOURCED};
use super::super::{assignments, joined, mktemp_call, ASSIGN, CONTINUED, MKTEMP};

/// `ASSIGN` as it was, its `(?<!\$)` and `\b` in the pattern.
const OLD_ASSIGN: &str = r#"(?:^|[;&|\n(]|(?<!\$)\{|\b(?:do|then|else)\s)\s*(?:(?:export|local|declare|typeset|readonly)\s+(?:-\w+\s+)*)?([A-Za-z_]\w*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s;&|)]*))"#;
/// `CONTINUED` as it was, its `(?<!\\)` in the pattern.
const OLD_CONTINUED: &str = r"(?<!\\)((?:\\\\)*)\\\n";
/// `bind`'s `SOURCED` as it was, its `\b` in the pattern.
const OLD_SOURCED: &str = r"(?:^|[;&|\n({]|\b(?:do|then|else))\s*(?:source|\.|eval)\s";
/// `bind`'s `PRINTF_V` as it was, its `\b` in the pattern.
const OLD_PRINTF_V: &str = r"\bprintf\s+-v\s+([A-Za-z_]\w*)";
/// `MKTEMP` as it was, its `\b` in the pattern.
const OLD_MKTEMP: &str = r#"^["']?(?:\$\(|`)\s*mktemp\b([^()`\n]*?)\s*(?:\)|`)"#;

/// Every text of up to `n` of `pieces`, the empty one first.
fn texts(pieces: &[&str], n: usize) -> Vec<String> {
    let (mut all, mut longest) = (vec![String::new()], vec![String::new()]);
    for _ in 0..n {
        longest = longest
            .iter()
            .flat_map(|t| pieces.iter().map(move |p| format!("{t}{p}")))
            .collect();
        all.extend(longest.iter().cloned());
    }
    all
}

/// A match's groups' spans, 0 to 4.
fn spans(c: &Captures) -> Vec<Option<Range<usize>>> {
    (0..5).map(|i| c.get(i).map(|m| m.range())).collect()
}

/// `assignments` reads each assignment, every group's span, as the one fancy pattern read it, on every text of up to 5 pieces - a
/// `$`, a `{`, a `do `, a letter, a word character of two bytes, a character of two bytes that is no word character, a separator,
/// an assignment's start and an `export ` - so a match refused and one taken after another are both read; and of up to 4 with a
/// `then ` and an `else ` for the `do `, a double and a single quote for the `$` and the `{`, so every opening's look is refused
/// and each of a value's three forms is read.
#[test]
fn the_assignment_scan_reads_each_assignment_as_the_pattern_read_it() {
    let pattern = crate::regex::build(OLD_ASSIGN).unwrap();
    let wide = texts(&["$", "{", "do ", "x", "é", "²", ";", "A=", "export "], 5);
    let quoted = texts(&["then ", "else ", "x", "é", "²", ";", "A=", "\"", "'"], 4);
    for text in wide.iter().chain(&quoted) {
        let old: Vec<_> = pattern
            .captures_iter(text)
            .map_while(Result::ok)
            .map(|c| spans(&c))
            .collect();
        let scan: Vec<_> = assignments(text).map(|c| spans(&c)).collect();
        assert_eq!(scan, old, "{text:?}");
    }
}

/// `joined` joins each line as the one fancy pattern, its matches replaced by their run of escaped backslashes, joined it, on every
/// text of up to 7 pieces - a backslash, a newline, a letter and a character of two bytes.
#[test]
fn the_continued_line_scan_joins_each_line_as_the_pattern_joined_it() {
    let pattern = crate::regex::build(OLD_CONTINUED).unwrap();
    for text in &texts(&["\\", "\n", "a", "é"], 7) {
        let old = pattern.replace_all(text, "${1}").into_owned();
        let scan = joined(text);
        assert_eq!(scan, old, "{text:?}");
    }
}

/// `sourced` answers as the one fancy pattern's search did, on every text of up to 5 pieces - a `do`, a blank, a `.`, a letter, a
/// word character of two bytes, a character of two bytes that is no word character, a separator and a `{` - and of up to 4 with a
/// `then` and an `else` for the `do`.
#[test]
fn the_sourced_scan_answers_as_the_pattern_answered() {
    let pattern = crate::regex::build(OLD_SOURCED).unwrap();
    let wide = texts(&["do", " ", ".", "x", "é", "²", ";", "{"], 5);
    let words = texts(&["then", "else", " ", ".", "x", "é", "²"], 4);
    for text in wide.iter().chain(&words) {
        let old = pattern.is_match(text).unwrap();
        let scan = sourced(text);
        assert_eq!(scan, old, "{text:?}");
    }
}

/// `mktemp_call` reads each value's `$(mktemp ...)`, both groups' spans, as the one fancy pattern read it, on every text of up to 5
/// pieces - a `$(`, a backquote, a `mktemp`, a letter, a word character of two bytes, a character of two bytes that is no word
/// character, a blank, a `)` and a double quote.
#[test]
fn the_mktemp_scan_reads_each_call_as_the_pattern_read_it() {
    let pattern = crate::regex::build(OLD_MKTEMP).unwrap();
    let pieces = ["$(", "`", "mktemp", "x", "é", "²", " ", ")", "\""];
    for text in &texts(&pieces, 5) {
        let old = pattern.captures(text).unwrap().map(|c| spans(&c));
        let scan = mktemp_call(text).map(|c| spans(&c));
        assert_eq!(scan, old, "{text:?}");
    }
}

/// `printf_v_names` reads each name and where it stands as the one fancy pattern read it, on every text of up to 5 pieces - a
/// `printf`, a ` -v `, a name, a letter, a word character of two bytes, a character of two bytes that is no word character and a
/// separator.
#[test]
fn the_printf_v_scan_reads_each_name_as_the_pattern_read_it() {
    let pattern = crate::regex::build(OLD_PRINTF_V).unwrap();
    for text in &texts(&["printf", " -v ", "n", "x", "é", "²", ";"], 5) {
        let old: Vec<(String, usize)> = pattern
            .captures_iter(text)
            .map_while(Result::ok)
            .filter_map(|c| c.get(1).map(|m| (m.as_str().to_owned(), m.start())))
            .collect();
        let scan = printf_v_names(text);
        assert_eq!(scan, old, "{text:?}");
    }
}

/// The pattern built with a backtracking limit of one step.
fn limited(pattern: &str) -> Regex {
    let mut b = crate::regex::builder(pattern);
    b.backtrack_limit(1);
    b.build().unwrap()
}

/// Each scan's pattern is one the regex crate runs: built with a backtracking limit of one step, it reads a text no error ends,
/// where the fancy pattern it replaced, built so, gives up - fancy-regex's machine counts its steps, the regex crate's automaton
/// has none to count.
#[test]
fn each_hand_read_scan_s_pattern_runs_in_the_regex_crate() {
    let line = "x ${A=1} do B=2; . f printf -v n x \\\\\\\ny ";
    let text = format!("$(mktemp -d /tmp/k.x) {}", line.repeat(20));
    let pairs = [
        (&ASSIGN, OLD_ASSIGN),
        (&CONTINUED, OLD_CONTINUED),
        (&SOURCED, OLD_SOURCED),
        (&PRINTF_V, OLD_PRINTF_V),
        (&MKTEMP, OLD_MKTEMP),
    ];
    for (lazy, old) in pairs {
        let now = lazy.on(&text).unwrap().as_str();
        let (automaton, machine) = (limited(now).captures(&text), limited(old).captures(&text));
        assert!(automaton.is_ok() && machine.is_err(), "{now}");
    }
}
