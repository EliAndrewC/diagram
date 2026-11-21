//! A footnote that quotes several passages, shown as a list (`record/passages.py`, feature 292; ported by feature 449 T144). The notes a
//! session writes do not change; the assembly writes `<span class="pass">` per passage inside `<span class="passages">` and keeps every
//! separator it replaces in a hidden `<span class="sep">`, so the page's text, tags stripped, is exactly what it was. A split is made only
//! at depth zero and only where the next thing is a passage.

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_shared::py_text::is_space;

use crate::re;

static KEY_HEAD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"^([\t-\r\x1c-\x1f \x85\xa0\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}]*<a href="[^"]*"(?: [^>]*)?><code>[a-z0-9][a-z0-9-]*</code></a>)( - )"#,
    )
});
const STARTS: [&str; 4] = ["\u{300c}", "\"", "\u{201c}", "<a href="];
static NOTE: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)(<li data-note="[^"]+">)(.*?)(</li>)"#));

/// (index, kind) of each `;`, `/` and `:` at depth zero; a tag, a comment and a collapsed original are each one unit, and an unclosed
/// one ends the scan.
fn depth0_marks(text: &str) -> Vec<(usize, char)> {
    let mut marks = Vec::new();
    let (mut depth, mut in_quote, mut i) = (0_i32, false, 0);
    while let Some(c) = text[i..].chars().next() {
        if c == '<' {
            let closer = if text[i..].starts_with("<span class=\"orig\">") {
                "</span>"
            } else if text[i..].starts_with("<!--") {
                "-->"
            } else {
                ">"
            };
            match text[i + 1..].find(closer) {
                Some(n) => i = i + 1 + n + closer.len(),
                None => break,
            }
            continue;
        }
        match c {
            '\u{300c}' | '(' | '\u{ff08}' => depth += 1,
            '\u{300d}' | ')' | '\u{ff09}' if depth > 0 => depth -= 1,
            '"' => in_quote = !in_quote,
            ';' | ':' | '/' if depth == 0 && !in_quote => marks.push((i, c)),
            _ => {}
        }
        i += c.len_utf8();
    }
    marks
}

/// Where a passage starts after the separator at `at`, or None when what follows is not a passage.
fn next_is_passage(text: &str, at: usize) -> Option<usize> {
    let j = at + 1 + text[at + 1..].bytes().take_while(|b| *b == b' ').count();
    STARTS.iter().any(|s| text[j..].starts_with(s)).then_some(j)
}

/// One note's body with its passages as a list, when it quotes more than one; unchanged otherwise.
#[must_use]
pub fn bulleted(body: &str) -> String {
    let Some(head) = KEY_HEAD.captures(body).ok().flatten() else {
        return body.to_owned();
    };
    let rest = &body[head.get(0).map_or(0, |m| m.end())..];
    let mut cuts: Vec<(usize, usize, char)> = Vec::new();
    for (at, kind) in depth0_marks(rest) {
        if let Some(start) = next_is_passage(rest, at) {
            let end = if kind == ':' {
                at + 1
            } else {
                rest[..at].trim_end_matches(' ').len()
            };
            cuts.push((end, start, kind));
        }
    }
    if cuts.is_empty() {
        return body.to_owned();
    }
    let (mut pieces, mut seps, mut kinds, mut last) = (Vec::new(), Vec::new(), Vec::new(), 0);
    for (end, start, kind) in &cuts {
        pieces.push(&rest[last..*end]);
        seps.push(&rest[*end..*start]);
        kinds.push(*kind);
        last = *start;
    }
    let tail = &rest[last..];
    let kept = tail.trim_end_matches(is_space);
    let trailing = &tail[kept.len()..];
    pieces.push(kept);
    let mut nested = false;
    let mut out = format!(
        r#"{}<span class="sep">{}</span><span class="passages">"#,
        &head[1], &head[2]
    );
    for (n, piece) in pieces.iter().enumerate() {
        let cls = if nested { "pass sub" } else { "pass" };
        let _ = write!(out, r#"<span class="{cls}">{piece}</span>"#);
        if let Some(sep) = seps.get(n) {
            let _ = write!(out, r#"<span class="sep">{sep}</span>"#);
            nested = nested || kinds[n] == ':';
        }
    }
    out.push_str("</span>");
    out.push_str(trailing);
    out
}

/// Every note of a notes file, each with its passages listed when it has several.
#[must_use]
pub fn bulleted_notes(notes_html: &str) -> String {
    NOTE.replace_all(notes_html, |m: &Captures| {
        format!("{}{}{}", &m[1], bulleted(&m[2]), &m[3])
    })
    .into_owned()
}

#[cfg(test)]
mod tests;
