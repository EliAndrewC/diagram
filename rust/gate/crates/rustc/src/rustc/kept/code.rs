//! A Rust file's code (feature 449 T112; the GM 2026-11-11): its text with its plain comments taken out, what a crate's lint, tests and
//! coverage key a `.rs` file by, so a comment-only edit moves none of them. A doc comment (`///`, `//!`, `/** */`, `/*! */`) stays:
//! clippy lints it and rustdoc runs its code. A line a removed comment leaves empty goes; every other line, blank ones too, stays as it
//! was, so an edit of a line's code or of the blank lines a lint reads still moves the key. Clippy's `too_many_lines` counts no comment
//! line (observed 2026-11-11, method: 98 code lines and 10 comment lines drew no warning, 102 code lines did).

/// The text with its plain comments removed, string, raw string, byte and char literals read as such (a `//` inside one is no comment).
pub(super) fn code_text(text: &str) -> String {
    let chars: Vec<char> = text.chars().collect();
    let mut out = String::with_capacity(text.len());
    let mut line = String::new();
    let mut cut = false;
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        let next = chars.get(i + 1).copied();
        if c == '\n' {
            end_line(&mut out, &mut line, &mut cut, true);
            i += 1;
        } else if c == '/' && next == Some('/') {
            let doc = matches!(chars.get(i + 2), Some('!'))
                || (chars.get(i + 2) == Some(&'/') && chars.get(i + 3) != Some(&'/'));
            let end = chars[i..]
                .iter()
                .position(|&x| x == '\n')
                .map_or(chars.len(), |p| i + p);
            if doc {
                line.extend(&chars[i..end]);
            } else {
                cut = true;
            }
            i = end;
        } else if c == '/' && next == Some('*') {
            i = block(&chars, i, &mut out, &mut line, &mut cut);
        } else if c == '"' || raw_start(&chars, i) {
            let end = literal_end(&chars, i);
            line.extend(&chars[i..end]);
            i = end;
        } else if c == '\'' {
            let end = char_end(&chars, i);
            line.extend(&chars[i..end]);
            i = end;
        } else {
            line.push(c);
            i += 1;
        }
    }
    end_line(&mut out, &mut line, &mut cut, false);
    out
}

/// End a line: a line a removed comment left empty goes, one it shortened loses its trailing space, any other stays as it was.
fn end_line(out: &mut String, line: &mut String, cut: &mut bool, newline: bool) {
    let kept = if *cut { line.trim_end() } else { line.as_str() };
    if !(*cut && kept.trim().is_empty()) {
        out.push_str(kept);
        if newline {
            out.push('\n');
        }
    }
    line.clear();
    *cut = false;
}

/// A block comment from `at` (nested, as Rust's are): a doc block copied, a plain one removed line by line; where it ends.
fn block(chars: &[char], at: usize, out: &mut String, line: &mut String, cut: &mut bool) -> usize {
    let third = chars.get(at + 2).copied();
    let doc =
        third == Some('!') || (third == Some('*') && !matches!(chars.get(at + 3), Some('*' | '/')));
    let mut depth = 0;
    let mut i = at;
    while i < chars.len() {
        let pair = (chars[i], chars.get(i + 1).copied());
        let step = if pair == ('/', Some('*')) {
            depth += 1;
            2
        } else if pair == ('*', Some('/')) {
            depth -= 1;
            2
        } else {
            1
        };
        if doc {
            line.extend(&chars[i..i + step]);
        } else if chars[i] == '\n' {
            *cut = true;
            end_line(out, line, cut, true);
        }
        i += step;
        if depth == 0 {
            break;
        }
    }
    *cut |= !doc;
    i
}

/// Is `at` the `r` of a raw string (`r"`, `r#"`, `br"`, `cr"`), not a name ending in r?
fn raw_start(chars: &[char], at: usize) -> bool {
    let ident = |c: char| c.is_alphanumeric() || c == '_';
    let before = at.checked_sub(1).map(|b| chars[b]);
    let prefix_ok = match before {
        Some('b' | 'c') => !at.checked_sub(2).is_some_and(|b| ident(chars[b])),
        Some(p) => !ident(p),
        None => true,
    };
    let hashes = chars[at + 1..].iter().take_while(|&&c| c == '#').count();
    chars[at] == 'r' && prefix_ok && chars.get(at + 1 + hashes) == Some(&'"')
}

/// Where a string literal from `at` ends: a plain one at its unescaped quote, a raw one at its quote and as many `#` as it opened with.
fn literal_end(chars: &[char], at: usize) -> usize {
    if chars[at] == '"' {
        let mut i = at + 1;
        while i < chars.len() && chars[i] != '"' {
            i += if chars[i] == '\\' { 2 } else { 1 };
        }
        return (i + 1).min(chars.len());
    }
    let hashes = chars[at + 1..].iter().take_while(|&&c| c == '#').count();
    let close: Vec<char> = std::iter::once('"')
        .chain(std::iter::repeat_n('#', hashes))
        .collect();
    let body = at + 2 + hashes;
    chars[body.min(chars.len())..]
        .windows(close.len())
        .position(|w| w == close.as_slice())
        .map_or(chars.len(), |p| body + p + close.len())
}

/// Where a `'` from `at` ends: a char literal (`'x'`, `'\n'`, `'\''`) at its closing quote, a lifetime or label after the quote alone.
fn char_end(chars: &[char], at: usize) -> usize {
    if chars.get(at + 1) == Some(&'\\') {
        let close = chars[at + 3..].iter().position(|&c| c == '\'');
        return close.map_or(chars.len(), |p| at + 3 + p + 1);
    }
    if chars.get(at + 2) == Some(&'\'') {
        return at + 3;
    }
    at + 1
}

#[cfg(test)]
mod tests;
