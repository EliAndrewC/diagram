//! A command's quoted strings as the walk reads them (`_quotes_to_paths`): a plain body kept as the word it is, any other held as
//! the one word its quotes make, its splitting characters stood in (451 T83), a `python3 -c` program carried out beside the text;
//! moved out of `tree.rs` by 451 T83 (file-scale).
use std::fmt::Write as _;

use super::python::{Program, PYTHON_C_BEFORE};
use crate::shape::quoted_spans;

/// A quoted body that is one plain word - no whitespace and none of `;|&()<>` or a backquote - read without the pattern it was
/// (`PLAIN_QUOTE_BODY`, 451 T97): its `\s` is Unicode's `White_Space`, as `char::is_whitespace` is (`tests/builds.rs` holds the two
/// equal on every character to U+3100 and U+FEFF).
pub(super) fn plain_quote_body(body: &str) -> bool {
    !body.contains(splits)
}

/// A character the walk splits a text at - a blank or one of `;|&()<>` and a backquote - which a plain quoted body holds none of.
fn splits(c: char) -> bool {
    c.is_whitespace() || ";|&()<>`".contains(c)
}

/// Where the stand-ins of a held quoted word begin (451 T83): a character `c` of a quoted body the walk would split at or read as a
/// brace, and each quote of the pair, travels the walk as `HELD + c`, a private-use character (U+F0000 up: no command a session
/// types holds one, and `c` is at most U+3000, so every stand-in is one of plane 15's), which no segment, word, redirect, brace or
/// continued-line rule reads.
const HELD: u32 = 0xF_0000;

/// A character a held word hides from the walk: one it splits at, and a brace, which `segments` reads to its close (`${`) or as a
/// group (451 T83: a held `'... "\${#passed'` read the rest of the command as one word, its `cp` into the clone unseen).
pub(super) fn hides(c: char) -> bool {
    splits(c) || c == '{' || c == '}'
}

/// The stand-in of a character a held word hides from the walk.
pub(super) fn stand_in(c: char) -> char {
    char::from_u32(HELD + u32::from(c)).unwrap_or(c)
}

/// The character a stand-in hides, None for any other character.
fn stood_for(c: char) -> Option<char> {
    let hidden = char::from_u32(u32::from(c).checked_sub(HELD)?)?;
    (hides(hidden) || hidden == '"' || hidden == '\'').then_some(hidden)
}

/// Whether a quoted body's parentheses and backquotes pair within it (451 T83). One that does not is a piece of a substitution whose
/// nested quotes the scan pairs flat - `"$(dirname "$F")"` is read as `"$(dirname "`, `$F` and `")"` - and the command's other
/// spans are then read across it too, so no body of that command is held: each is read as before (`quotes_to_paths`).
pub(super) fn pairs_within(body: &str) -> bool {
    let mut depth = 0_usize;
    for c in body.chars() {
        if c == '(' {
            depth += 1;
        } else if c == ')' {
            let Some(d) = depth.checked_sub(1) else {
                return false;
            };
            depth = d;
        }
    }
    depth == 0 && body.matches('`').count() % 2 == 0
}

/// Where the `$(...)` opening at `at` of a double-quoted body closes, where it holds no quote and no backquote: the walk reads it as
/// the substitution it is, as it reads one outside quotes (`mkdir -p "$(dirname $F)"` makes F's directory, 451 T79's `dir_base`).
/// A `$((` is arithmetic, no substitution: read as one, `"$((a > b))"` was a write of `b`.
fn substitution_end(chars: &[char], at: usize) -> Option<usize> {
    if chars.get(at..at + 2) != Some(&['$', '('][..]) || chars.get(at + 2) == Some(&'(') {
        return None;
    }
    let mut depth = 0_usize;
    for (k, &c) in chars.iter().enumerate().skip(at + 1) {
        match c {
            '(' => depth += 1,
            ')' if depth == 1 => return Some(k),
            ')' => depth -= 1,
            '"' | '\'' | '`' => return None,
            _ => {}
        }
    }
    None
}

/// A quoted body that is no plain word as the ONE word its quotes make (451 T83): its quotes and the characters it hides stood in,
/// a double-quoted body's plain `$(...)` left for the walk. Blanked to an empty pair before, it left a file tool's destination read
/// from the word before it (`cp /tmp/a "/diagram/x y"` a write of `/tmp/a`) and a redirect's place unknown (`echo x >
/// "/diagram/a b"` where the shell stood). A `$(...)` holding a quote is hidden whole, and every `$(` after it in the body, so the
/// scan stays one pass. A backslash in double quotes escapes the character after it: `\$(` is a dollar and a parenthesis, no
/// substitution (bx#57058's `"... Y='\$(touch $W/out/RAN5)' ..."`, a probe's marker that the touch never runs), `\\$(` one.
pub(super) fn held(quote: char, body: &str) -> String {
    let chars: Vec<char> = body.chars().collect();
    let (mut word, mut at, mut reads_subs) =
        (String::with_capacity(body.len() + 8), 0, quote == '"');
    word.push(stand_in(quote));
    while at < chars.len() {
        if quote == '"' && chars[at] == '\\' {
            for &c in chars.get(at..at + 2).unwrap_or(&chars[at..]) {
                word.push(if hides(c) { stand_in(c) } else { c });
            }
            at += 2;
            continue;
        }
        let end = if reads_subs && chars[at] == '$' {
            substitution_end(&chars, at)
        } else {
            None
        };
        if let Some(end) = end {
            word.extend(&chars[at..=end]);
            at = end + 1;
            continue;
        }
        // a `$(...)` holding a quote ends the reading of substitutions; an arithmetic `$((` is hidden and the reading goes on
        reads_subs &=
            chars.get(at..at + 2) != Some(&['$', '('][..]) || chars.get(at + 2) == Some(&'(');
        word.push(if hides(chars[at]) {
            stand_in(chars[at])
        } else {
            chars[at]
        });
        at += 1;
    }
    word.push(stand_in(quote));
    word
}

/// A word as the shell reads it where the walk reads a place (451 T83): a held body's characters back and its quotes off.
pub(super) fn unheld(word: &str) -> std::borrow::Cow<'_, str> {
    if !word.chars().any(|c| stood_for(c).is_some()) {
        return std::borrow::Cow::Borrowed(word);
    }
    word.chars()
        .filter_map(|c| match stood_for(c) {
            Some('"' | '\'') => None,
            Some(hidden) => Some(hidden),
            None => Some(c),
        })
        .collect()
}

/// A segment as the guards that read one were shown it before 451 T83: each held word blanked to its empty pair of quotes, so a
/// README's place (`readme_hooks`), a write's tool (make-only, gate-write) and every message judge the text they judged; a
/// stand-in outside a held word, an arithmetic's (`split::arithmetic`), shown as the character it hides.
pub(super) fn blanked(seg: &str) -> std::borrow::Cow<'_, str> {
    if !seg.chars().any(|c| stood_for(c).is_some()) {
        return std::borrow::Cow::Borrowed(seg);
    }
    let (mut text, mut open) = (String::with_capacity(seg.len()), None);
    for c in seg.chars() {
        match (open, stood_for(c)) {
            (None, Some(q @ ('"' | '\''))) => {
                text.push(q);
                text.push(q);
                open = Some(q);
            }
            (None, hidden) => text.push(hidden.unwrap_or(c)),
            (Some(q), Some(hidden)) if hidden == q => open = None,
            (Some(_), _) => {}
        }
    }
    std::borrow::Cow::Owned(text)
}

/// A quoted string kept as its body where it is one plain word (a path), else held as the one word its quotes make (451 T83,
/// `held`), and blanked to an empty pair where it is empty or its parentheses do not pair (`_quotes_to_paths`); a
/// program `python3 -c` runs is carried out beside the text, the word `__py_c_<n>__` standing in its place, so `writes_in` can
/// judge whether it only reads without the program's own `;`, `(` and `|` splitting the walk (451 T31). The strings are shape's
/// `quoted_spans` (451 T112), where the pattern `(?s)(["'])((?:\\.|(?!\1).)*)\1` tried 2^n readings of the n escapes after a quote
/// nothing closes: `<a write>; echo it's` and forty escapes, the write each guard reads, held the house style guard, main-tree,
/// gm-tree, make-only, readme, gate-write and the event log's end past 10 s (measured 2026-11-21, the T112 plan section); a test
/// holds the two equal on every text of up to 6 pieces (`tests/quotes.rs`).
pub(super) fn quotes_to_paths(cmd: &str, mut programs: Vec<Program>) -> (String, Vec<Program>) {
    let (mut text, mut from) = (String::with_capacity(cmd.len()), 0);
    let spans: Vec<(usize, usize, bool)> = quoted_spans(cmd)
        .into_iter()
        .map(|(open, close)| (open, close, PYTHON_C_BEFORE.is_match(&cmd[..open])))
        .collect();
    let hold = spans
        .iter()
        .all(|&(open, close, program)| program || pairs_within(&cmd[open + 1..close]));
    for (open, close, program) in spans {
        let (quote, body) = (&cmd[open..=open], &cmd[open + 1..close]);
        text.push_str(&cmd[from..open]);
        if program {
            programs.push((quote.chars().next().unwrap_or('"'), body.to_owned()));
            let _ = write!(text, "__py_c_{}__", programs.len() - 1);
        } else if body.is_empty() || !(hold || plain_quote_body(body)) {
            // an empty quote stays a word (451 T79: `cd ""` stays where it is, bash's `null directory`, never `cd` home), and a
            // body of a command whose quotes are read across a substitution is blanked, as before 451 T83 (`pairs_within`)
            text.push_str(quote);
            text.push_str(quote);
        } else if plain_quote_body(body) {
            text.push_str(body);
        } else {
            text.push_str(&held(quote.chars().next().unwrap_or('"'), body));
        }
        from = close + 1;
    }
    text.push_str(&cmd[from..]);
    (text, programs)
}

pub(super) fn strip_quote_chars(token: &str) -> &str {
    token.trim_matches(|c| matches!(c, '"' | '\'') || matches!(stood_for(c), Some('"' | '\'')))
}
