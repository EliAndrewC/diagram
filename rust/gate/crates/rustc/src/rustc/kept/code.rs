//! A Rust file's code (feature 449 T112; the GM 2026-11-11): its text with its plain comments taken out, what a crate's lint, tests and
//! coverage key a `.rs` file by, so a comment-only edit moves none of them. A doc comment (`///`, `//!`, `/** */`, `/*! */`) stays:
//! clippy lints it and rustdoc runs its code. A line a removed comment leaves empty goes; every other line, blank ones too, stays as it
//! was, so an edit of a line's code or of the blank lines a lint reads still moves the key. Clippy's `too_many_lines` counts no comment
//! line (observed 2026-11-11, method: 98 code lines and 10 comment lines drew no warning, 102 code lines did).
//!
//! THE VIEWS ARE KEYED BY THIS CODE (feature 451 T434): a kept view (`View`, built here and nowhere else - its fields are private to
//! this file) is a function of a file's path and text computed by this file and by the files `SOURCES` names, compiled in, and of the
//! Unicode tables std's `char` methods read (`char::UNICODE_VERSION`). The cache's stamp is their hash (`stamp`), so an edit of any of
//! them throws the kept views away and no other rebuild of `l7r-rust` does. Keyed by the whole binary, every rebuild - an edit of
//! `rust/guard/shared`, `core`, `tree` or `rustc` - read and hashed all 1,504 Rust files again, 1.9 s at load 12 (measured 2026-11-27,
//! `dev/measurements/2026-11-27/checks-start/`). The test `the_views_reach_nothing_outside_their_hashed_sources` holds every file
//! `SOURCES` names to reaching only std and the other files it names: no `super`, `crate` or other crate's path, no module file, no
//! cfg but the test module's, no compiled-in file outside the set.

use l7r_shared::sha256;

/// The files the views are computed from, compiled in, by their paths from the tree's root.
const SOURCES: [(&str, &str); 2] = [
    (
        "rust/gate/crates/rustc/src/rustc/kept/code.rs",
        include_str!("code.rs"),
    ),
    (
        "rust/guard/shared/src/sha256.rs",
        include_str!("../../../../../../guard/shared/src/sha256.rs"),
    ),
];

/// The views cache's first line: the hash of the code that computes a view (`SOURCES`) and of the Unicode version its `char` methods
/// read. A cache whose first line is another is thrown away whole.
pub(super) fn stamp() -> String {
    stamp_of(&SOURCES, char::UNICODE_VERSION)
}

fn stamp_of(sources: &[(&str, &str)], unicode: (u8, u8, u8)) -> String {
    let mut all = format!("unicode {unicode:?}\n").into_bytes();
    for (path, text) in sources {
        all.extend(format!("{path} {}\n", text.len()).into_bytes());
        all.extend(text.as_bytes());
    }
    format!("l7r-rust views {}", sha256::hex(&all))
}

/// One Rust file's views: its code id, its interface id and the files it compiles in. Built only by `View::of` and read back only by
/// `View::parse`, both here, so what a kept line holds is computed by the hashed code alone.
#[derive(Clone, PartialEq, Debug)]
pub(super) struct View {
    code: String,
    interface: String,
    includes: Vec<String>,
}

impl View {
    /// The views of the file at `path` (from the root) whose text is `text`.
    pub(super) fn of(path: &str, text: &str) -> Self {
        View {
            code: format!("code:{}", sha256::hex(code_text(text).as_bytes())),
            interface: format!("interface:{}", sha256::hex(interface_text(text).as_bytes())),
            includes: included(path, text),
        }
    }

    pub(super) fn code(&self) -> &str {
        &self.code
    }

    pub(super) fn interface(&self) -> &str {
        &self.interface
    }

    pub(super) fn includes(&self) -> &[String] {
        &self.includes
    }

    /// The kept line, `<at>\t<code id>\t<interface id>[\t<included>...]`, `at` the file's `<path> <blob id>`.
    pub(super) fn line(&self, at: &str) -> String {
        format!(
            "{at}\t{}\t{}\t{}\n",
            self.code,
            self.interface,
            self.includes.join("\t")
        )
    }

    /// A kept line read back: its `<path> <blob id>` and its views.
    pub(super) fn parse(line: &str) -> Option<(String, Self)> {
        let mut parts = line.split('\t');
        let at = parts.next()?.to_owned();
        let code = parts.next()?.to_owned();
        let interface = parts.next()?.to_owned();
        let includes = parts.filter(|s| !s.is_empty()).map(str::to_owned).collect();
        Some((
            at,
            View {
                code,
                interface,
                includes,
            },
        ))
    }
}

/// The paths a Rust file at `path` (from the root) compiles in - each string a compiling-in macro opens with, on one line - resolved
/// from its directory. A path is on one line: a string that only names the macro (`core`'s reader of these lines) once ran to the
/// next quote, lines and all, and the kept views, a line a file, gave that "path" back cut short, so a key moved after each rebuild
/// (feature 451 T347). Read by hand, not by a pattern, so the views reach no regex crate (451 T434).
fn included(path: &str, text: &str) -> Vec<String> {
    let chars: Vec<char> = text.chars().collect();
    let dir: Vec<&str> = path.split('/').collect();
    let mut found = Vec::new();
    let mut i = 0;
    while i < chars.len() {
        if let Some((name, end)) = include_at(&chars, i) {
            let mut at: Vec<&str> = dir[..dir.len() - 1].to_vec();
            for part in name.split('/') {
                match part {
                    ".." => drop(at.pop()),
                    "." => {}
                    p => at.push(p),
                }
            }
            found.push(at.join("/"));
            i = end;
        } else {
            i += 1;
        }
    }
    found
}

/// A compiling-in macro's path at `at` - the word `include`, `include_str` or `include_bytes`, then `!`, `(` and a string of one line
/// or more characters, spaces allowed between - and one past its closing quote.
fn include_at(chars: &[char], at: usize) -> Option<(String, usize)> {
    let starts = |i: usize, w: &str| {
        chars[i.min(chars.len())..]
            .iter()
            .copied()
            .take(w.len())
            .eq(w.chars())
    };
    if at.checked_sub(1).is_some_and(|b| ident(chars[b])) || !starts(at, "include") {
        return None;
    }
    let mut i = at + "include".len();
    if starts(i, "_str") {
        i += "_str".len();
    } else if starts(i, "_bytes") {
        i += "_bytes".len();
    }
    let skip = |mut i: usize| {
        while chars.get(i).is_some_and(|c| c.is_whitespace()) {
            i += 1;
        }
        i
    };
    if chars.get(i) != Some(&'!') {
        return None;
    }
    i = skip(i + 1);
    if chars.get(i) != Some(&'(') {
        return None;
    }
    i = skip(i + 1);
    if chars.get(i) != Some(&'"') {
        return None;
    }
    let body = i + 1;
    let len = chars[body..]
        .iter()
        .position(|&c| c == '"' || c == '\n')
        .filter(|&n| n > 0 && chars[body + n] == '"')?;
    Some((chars[body..body + len].iter().collect(), body + len + 1))
}

/// The text with its plain comments removed, string, raw string, byte and char literals read as such (a `//` inside one is no comment).
fn code_text(text: &str) -> String {
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

/// A crate's interface as another crate's lint reads it (feature 449 T113; the GM 2026-11-11): its code with the bodies of the
/// functions no other crate can see into replaced by `{}`. A body stays where it can reach another crate: a `const fn`'s (evaluated
/// where it is used) and an `async fn`'s or one with `impl` in its signature (a returned `impl Trait`'s auto traits follow from it), and
/// a body holding an `impl` block or a `macro_rules!`, seen crate-wide. A `macro_rules!` stays whole. Not exact (the plan's design
/// review): a lint that reads another crate's body through the compiler would go unrun until the interface moves. A text the lexer
/// cannot read to its end keeps all its code.
fn interface_text(text: &str) -> String {
    let code = code_text(text);
    let chars: Vec<char> = code.chars().collect();
    let mut out = String::with_capacity(code.len());
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if c == '"' || raw_start(&chars, i) {
            let end = literal_end(&chars, i);
            out.extend(&chars[i..end]);
            i = end;
        } else if c == '\'' {
            let end = char_end(&chars, i);
            out.extend(&chars[i..end]);
            i = end;
        } else if word_at(&chars, i, "macro_rules") {
            let Some(end) = chars[i..]
                .iter()
                .position(|&x| matches!(x, '{' | '(' | '['))
                .and_then(|o| balanced(&chars, i + o))
            else {
                return code;
            };
            out.extend(&chars[i..end]);
            i = end;
        } else if word_at(&chars, i, "fn") && named_after(&chars, i + 2) {
            let Some((open, close)) = body(&chars, i) else {
                return code;
            };
            let head: String = chars[i..open].iter().collect();
            if open == close {
                // a declaration with no body: its `;` is copied next
                out.push_str(&head);
                i = open;
                continue;
            }
            let inner: String = chars[open..close].iter().collect();
            let item = &out[out.rfind(['{', '}', ';']).map_or(0, |p| p + 1)..];
            let visible = has_word(item, "const")
                || has_word(item, "async")
                || has_word(&head, "impl")
                || has_word(&inner, "impl")
                || has_word(&inner, "macro_rules");
            out.push_str(&head);
            out.push_str(if visible { &inner } else { "{}" });
            i = close;
        } else {
            out.push(c);
            i += 1;
        }
    }
    out
}

fn ident(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// Is the word `w` at `at`, whole?
fn word_at(chars: &[char], at: usize, w: &str) -> bool {
    let len = w.chars().count();
    let before = at.checked_sub(1).is_some_and(|b| ident(chars[b]));
    let after = chars.get(at + len).is_some_and(|&c| ident(c));
    !before && !after && chars[at..].iter().take(len).copied().eq(w.chars())
}

fn has_word(text: &str, w: &str) -> bool {
    let chars: Vec<char> = text.chars().collect();
    (0..chars.len()).any(|i| word_at(&chars, i, w))
}

/// Is a name next (a function item, `fn name`), not a function pointer type (`fn(u8)`)?
fn named_after(chars: &[char], at: usize) -> bool {
    let next = chars[at..].iter().find(|c| !c.is_whitespace());
    next.is_some_and(|&c| c.is_alphabetic() || c == '_')
}

/// A function's body from its `fn` at `at`: where its `{` opens and its matching `}` closes (one past it); none for a declaration
/// with no body (`;` first), and none where it never closes.
fn body(chars: &[char], at: usize) -> Option<(usize, usize)> {
    let mut depth = 0i32;
    for (i, &c) in chars.iter().enumerate().skip(at) {
        match c {
            '(' | '[' => depth += 1,
            ')' | ']' => depth -= 1,
            ';' if depth == 0 => return Some((i, i)),
            '{' if depth == 0 => return balanced(chars, i).map(|end| (i, end)),
            _ => {}
        }
    }
    None
}

/// One past the delimiter matching the one at `at`, literals and chars read as such; none where it never closes.
fn balanced(chars: &[char], at: usize) -> Option<usize> {
    let mut depth = 0i32;
    let mut i = at;
    while i < chars.len() {
        let c = chars[i];
        if c == '"' || raw_start(chars, i) {
            i = literal_end(chars, i);
            continue;
        }
        if c == '\'' {
            i = char_end(chars, i);
            continue;
        }
        depth += i32::from(matches!(c, '{' | '(' | '[')) - i32::from(matches!(c, '}' | ')' | ']'));
        i += 1;
        if depth == 0 {
            return Some(i);
        }
    }
    None
}

#[cfg(test)]
mod tests;
