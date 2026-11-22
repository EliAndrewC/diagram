//! A command split at its separators into the pieces the walk reads (`_segments`): segments, subshells and the `$(...)` inside
//! a word; moved out of `tree.rs` by 451 T83 (file-scale).
use std::fmt::Write as _;

use super::quoted::{hides, stand_in};

/// One piece of a command split at its separators: a segment, or a subshell's opening or closing (`_segments`).
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Piece {
    /// A segment, and whether a pipe feeds it the stdout of the segment before (451 T42: `cat <<'PY' | python3`).
    Seg(String, bool),
    Push,
    Pop,
    /// A `$(...)` inside a word, walked before its word's command as a subshell, its segments feeding no pipe outside it (451 T79).
    SubPush,
    SubPop,
}

/// Whether a substitution's text is `pwd`: where the shell stands (451 T79).
fn is_pwd(inner: &str) -> bool {
    matches!(inner.trim(), "pwd" | "pwd -P" | "pwd -L")
}

/// The length of a `` `pwd` `` that `rest` opens with and its word goes on past only into a path (`/`), else None (451 T79).
fn tick_pwd(rest: &[char]) -> Option<usize> {
    let close = rest.iter().skip(1).position(|c| *c == '`')? + 1;
    let inner: String = rest[1..close].iter().collect();
    (is_pwd(&inner) && word_goes_on_as_path(rest, close + 1)).then_some(close + 1)
}

/// Whether the word ends at `at` or goes on into a path: `$(pwd)/f` and `$(pwd)` name the shell's place, `$(pwd)x` does not.
fn word_goes_on_as_path(chars: &[char], at: usize) -> bool {
    chars
        .get(at)
        .is_none_or(|c| *c == '/' || c.is_whitespace() || "\"';|&)".contains(*c))
}

/// Whether a `{` or `}` is a brace group's - a word of its own, a `{` followed by a blank - and not a brace expansion inside a word
/// (`/tmp/{a,b}`), whose split cut a copy's destination off its command (451 T79: `cp /tmp/{a,b} /diagram/x` from `/tmp` passed).
fn brace_group(chars: &[char], i: usize, buf: &str) -> bool {
    let own_word = buf.trim().is_empty() || buf.ends_with(char::is_whitespace);
    own_word
        && chars
            .get(i + 1)
            .is_none_or(|c| c.is_whitespace() || (chars[i] == '}' && ";|&)".contains(*c)))
}

/// Where an arithmetic opens at `i`, a `$((` or a `((` where a command stands: the index of its first `(` (451 T83). Read as a
/// substitution or two subshells, `$((o>200?o-200:1))` was a write of `200?o-200:1` (ux#1441, in the clone) and `(( n > 3 ))` one
/// of `3`. As bash 5.3 reads it (probed 2026-11-21): one whose inner parenthesis closes before its outer is subshells,
/// `((cd x && touch a) && touch b)` making both, and any other arithmetic, `((cd x; touch a))` making none.
fn arithmetic(chars: &[char], i: usize, buf: &str) -> Option<usize> {
    let open = match chars.get(i) {
        Some('$') => i + 1,
        Some('(') => i,
        _ => return None,
    };
    if chars.get(open..open + 2) != Some(&['(', '('][..]) {
        return None;
    }
    let command = buf.trim();
    let at_command = matches!(
        command,
        "" | "!" | "for" | "if" | "elif" | "then" | "else" | "do" | "while" | "until"
    );
    let pairs = closing(chars, open + 1) + 1 == closing(chars, open);
    ((open > i || at_command) && pairs).then_some(open)
}

/// The index of the bracket that closes the one at `open` (`(` or `{`), its nesting counted; the text's length where none does.
fn closing(chars: &[char], open: usize) -> usize {
    let (o, c) = (chars[open], if chars[open] == '(' { ')' } else { '}' });
    let mut depth = 0;
    for (k, &ch) in chars.iter().enumerate().skip(open) {
        depth += i32::from(ch == o) - i32::from(ch == c);
        if depth == 0 {
            return k;
        }
    }
    chars.len()
}

/// The command split at its separators. A word stays whole (451 T79, found by T50 2026-11-21): a `${...}` and a brace expansion
/// keep their braces, which a brace group's `{` and `}` do not, and a `$(...)` inside a word is walked as a subshell before the word's command - its text
/// the n-th of `subs`, `$__sub_<n>__` standing in its place, a word the walk cannot resolve (a `$(mktemp ...)` aside, which
/// `mktemp_words` places; a `$(pwd)` or `` `pwd` `` is `.`, where the shell stands) - where before both split the word, its pieces
/// read as commands of their own (and `` `pwd`/f `` read as a word nothing is known of, 451 T79's probe of 2026-11-21).
pub(super) fn segments(text: &str, subs: &mut Vec<String>) -> Vec<Piece> {
    let chars: Vec<char> = text.chars().collect();
    let (mut out, mut buf, mut i, mut piped) = (Vec::new(), String::new(), 0, false);
    let mut pending = Vec::new();
    let flush = |buf: &mut String, out: &mut Vec<Piece>, pending: &mut Vec<Piece>, piped: bool| {
        out.append(pending);
        let seg = buf.trim().to_owned();
        buf.clear();
        if !seg.is_empty() {
            out.push(Piece::Seg(seg, piped));
        }
    };
    let mut arith = 0_usize;
    while i < chars.len() {
        let ch = chars[i];
        let next = chars.get(i + 1).copied();
        let sub = ch == '$' && next == Some('(') && chars.get(i + 2) != Some(&'(');
        if arith > 0 && !sub {
            // within an arithmetic: its operators no separator, group or redirect, a `$(...)` in it still a substitution
            match ch {
                '(' => arith += 1,
                ')' => arith -= 1,
                _ => {}
            }
            buf.push(if hides(ch) { stand_in(ch) } else { ch });
            i += 1;
        } else if let Some(open) = arithmetic(&chars, i, &buf) {
            buf.extend(&chars[i..open]);
            buf.extend([stand_in('('), stand_in('(')]);
            arith = 2;
            i = open + 2;
        } else if (ch == '&' && next == Some('&')) || (ch == '|' && next == Some('|')) {
            flush(&mut buf, &mut out, &mut pending, piped);
            piped = false;
            i += 2;
        } else if ch == '$' && next == Some('(') {
            let end = closing(&chars, i + 1);
            let inner: String = chars[i + 2..end].iter().collect();
            pending.push(Piece::SubPush);
            pending.extend(segments(&inner, subs));
            pending.push(Piece::SubPop);
            if is_pwd(&inner) && word_goes_on_as_path(&chars, end + 1) {
                buf.push('.');
            } else {
                let _ = write!(buf, "$__sub_{}__", subs.len());
            }
            subs.push(inner);
            i = end + 1;
        } else if let Some(len) = (ch == '`').then(|| tick_pwd(&chars[i..])).flatten() {
            buf.push('.');
            i += len;
        } else if ch == '$' && next == Some('{') {
            let end = closing(&chars, i + 1).min(chars.len() - 1);
            buf.extend(&chars[i..=end]);
            i = end + 1;
        } else if (ch == '|' || ch == '&') && buf.ends_with('>') {
            buf.push(ch); // `>|` and `>&` belong to the redirection, not a separator (feature 429)
            i += 1;
        } else if matches!(ch, ';' | '|' | '&' | '\n') {
            // a pipe at a line's end still feeds the next line's segment
            if !(ch == '\n' && buf.trim().is_empty()) {
                flush(&mut buf, &mut out, &mut pending, piped);
                piped = ch == '|';
            }
            i += 1;
        } else if ch == '(' {
            flush(&mut buf, &mut out, &mut pending, piped);
            out.push(Piece::Push);
            i += 1;
        } else if ch == ')' {
            flush(&mut buf, &mut out, &mut pending, piped);
            out.push(Piece::Pop);
            piped = false;
            i += 1;
        } else if (ch == '{' || ch == '}') && brace_group(&chars, i, &buf) {
            flush(&mut buf, &mut out, &mut pending, piped);
            i += 1;
        } else {
            buf.push(ch);
            i += 1;
        }
    }
    flush(&mut buf, &mut out, &mut pending, piped);
    out
}
