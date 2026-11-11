//! A claim and its grammar, read from a docstring's or a doc comment's `Research:` section (feature 316; `l7r/diagram/tools/claims.py`'s
//! `parse_claim`, `section_lines` and `claims_of`, ported by feature 449 T82): a claim is one line, `<label> - <backing>[: <account>]`.

use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::shared::py_text::{collapse, is_space, strip};

use crate::record::units::re;

/// The classes a backing may name besides question files (spec FR-001).
pub const CLASSES: [&str; 6] = [
    "GUESS",
    "UNRESEARCHED",
    "CONVENTION",
    "DEVIATION",
    "CANON",
    "NONE",
];

/// What every refusal prints, so the fix is in the message (the project's guard doctrine).
pub const GRAMMAR: &str = "a claim is one line of a `Research:` docstring section: `<label> - <backing>[: <what the code does>]`, the backing being question files (`research/questions/NNNN-<id>.html` or `.drawing.html`, comma-separated), `GUESS [<drawing page>]` (searched, silent; the `.drawing.html` that records the guess), `UNRESEARCHED` (not yet searched), `CONVENTION`, `DEVIATION <question file>`, `CANON` (the GM's setting canon or ruling), or `NONE` (no physical decision); one claim may sit on the header line (`Research: <label> - <backing>`); a constant's claim is a string literal directly after its assignment; a module's claims are inherited by its units that carry none";

/// A question file, as a claim names it (feature 303's flat directory).
pub static POINTER: LazyLock<Regex> =
    LazyLock::new(|| re(r"research/questions/(\d{4})-([a-z0-9-]+?)(\.drawing)?\.html"));
static POINTER_WHOLE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\A(?:research/questions/(\d{4})-([a-z0-9-]+?)(\.drawing)?\.html)\z"));
static SECTION_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"\AResearch:(.*)\z"));

/// One claim: what is decided, what backs it, and an optional account of what the code does.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Claim {
    pub label: String,
    /// One of [`CLASSES`], or `POINTER`.
    pub backing: String,
    pub pointers: Vec<String>,
    pub account: String,
    pub line: String,
}

impl Claim {
    /// The claim line as it enters a fingerprint: whitespace collapsed, each pointer reduced to its heading id.
    pub fn normalized(&self) -> String {
        POINTER
            .replace_all(&collapse(&self.line), |c: &Captures| {
                format!("{}{}", &c[2], c.get(3).map_or("", |m| m.as_str()))
            })
            .into_owned()
    }
}

/// `str.partition(sep)`: (before, whether found, after).
pub fn partition<'a>(text: &'a str, sep: &str) -> (&'a str, bool, &'a str) {
    text.split_once(sep)
        .map_or((text, false, ""), |(a, b)| (a, true, b))
}

fn whole(p: &str) -> Option<bool> {
    POINTER_WHOLE
        .captures(p)
        .ok()
        .flatten()
        .map(|c| c.get(3).is_some())
}

/// One claim line, or the error naming what is wrong.
pub fn parse_claim(line: &str) -> Result<Claim, String> {
    let text = collapse(line);
    let (label, sep, rest) = partition(&text, " - ");
    if !sep || strip(label).is_empty() || strip(rest).is_empty() {
        return Err(format!("`{text}` has no `<label> - <backing>`"));
    }
    let (backing, _, account) = partition(rest, ": ");
    let backing = strip(backing);
    let head = backing.split(' ').next().unwrap_or_default();
    let claim = |backing: &str, pointers: Vec<String>| Claim {
        label: strip(label).to_owned(),
        backing: backing.to_owned(),
        pointers,
        account: strip(account).to_owned(),
        line: text.clone(),
    };
    if head == "GUESS" && backing != head {
        let parts: Vec<String> = backing["GUESS".len()..]
            .split(',')
            .map(|p| strip(p).to_owned())
            .collect();
        if !parts.iter().all(|p| whole(p) == Some(true)) {
            return Err(format!("`{text}`: `GUESS` names the drawing page that records it (`...drawing.html`), or nothing"));
        }
        return Ok(claim("GUESS", parts));
    }
    if CLASSES.contains(&head) && head != "DEVIATION" {
        if backing != head {
            return Err(format!("`{text}`: `{head}` takes no pointer"));
        }
        return Ok(claim(head, Vec::new()));
    }
    let (kind, tail) = if head == "DEVIATION" {
        ("DEVIATION", strip(&backing["DEVIATION".len()..]))
    } else {
        ("POINTER", backing)
    };
    let parts: Vec<String> = tail.split(',').map(|p| strip(p).to_owned()).collect();
    if tail.is_empty() || !parts.iter().all(|p| whole(p).is_some()) {
        return Err(format!(
            "`{text}`: the backing `{backing}` is not question files or a class"
        ));
    }
    Ok(claim(kind, parts))
}

/// `str.expandtabs()`: each tab to the next multiple of eight columns, a line break restarting the count.
pub fn expandtabs(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut col = 0usize;
    for c in text.chars() {
        match c {
            '\t' => {
                let n = 8 - col % 8;
                out.extend(std::iter::repeat_n(' ', n));
                col += n;
            }
            '\n' | '\r' => {
                out.push(c);
                col = 0;
            }
            _ => {
                out.push(c);
                col += 1;
            }
        }
    }
    out
}

/// `str.lstrip()`.
pub fn lstrip(text: &str) -> &str {
    text.trim_start_matches(is_space)
}

fn indent_of(line: &str) -> usize {
    line.chars().count() - lstrip(line).chars().count()
}

fn head_of(line: &str) -> Option<String> {
    SECTION_HEAD
        .captures(line)
        .ok()
        .flatten()
        .map(|c| c[1].to_owned())
}

/// (header index, end index, flat) of the `Research:` section in docstring lines, or None.
fn section_span(lines: &[&str]) -> Option<(usize, usize, bool)> {
    for (i, raw) in lines.iter().enumerate() {
        let Some(own) = head_of(raw) else {
            continue;
        };
        let flat =
            i == 0 && lines.len() > 1 && !strip(lines[1]).is_empty() && !lines[1].starts_with(' ');
        let mut end = i + 1;
        let carried = !strip(&own).is_empty() && !flat;
        while end < lines.len()
            && !strip(lines[end]).is_empty()
            && (flat || lines[end].starts_with(' ') || (carried && !lines[end].contains(" - ")))
        {
            end += 1;
        }
        return Some((i, end, flat));
    }
    None
}

/// The raw claim lines of a docstring's `Research:` section (continuations joined), or None when it has none.
pub fn section_lines(doc: Option<&str>) -> Option<Vec<String>> {
    let doc = doc.filter(|d| !d.is_empty())?;
    let text = expandtabs(doc);
    let lines: Vec<&str> = text.split('\n').collect();
    let (i, end, flat) = section_span(&lines)?;
    let own = head_of(lines[i]).unwrap_or_default();
    let mut out: Vec<String> = if strip(&own).is_empty() {
        Vec::new()
    } else {
        vec![strip(&own).to_owned()]
    };
    let mut base: Option<usize> = None;
    for nxt in &lines[i + 1..end] {
        let indent = indent_of(nxt);
        let joined = |out: &mut Vec<String>| {
            if let Some(last) = out.last_mut() {
                last.push(' ');
                last.push_str(strip(nxt));
            }
        };
        if flat {
            if nxt.contains(" - ") || out.is_empty() {
                out.push(strip(nxt).to_owned());
            } else {
                joined(&mut out);
            }
        } else if !out.is_empty() && !nxt.contains(" - ") {
            joined(&mut out);
        } else if base.is_none_or(|b| indent <= b) {
            base = base.or(Some(indent));
            out.push(strip(nxt).to_owned());
        } else {
            joined(&mut out);
        }
    }
    Some(out)
}

/// (claims, errors) of one docstring; an error is a line that does not parse.
pub fn claims_of(doc: Option<&str>) -> (Vec<Claim>, Vec<String>) {
    let lines = section_lines(doc);
    let (mut claims, mut errors) = (Vec::new(), Vec::new());
    for line in lines.iter().flatten() {
        match parse_claim(line) {
            Ok(c) => claims.push(c),
            Err(e) => errors.push(e),
        }
    }
    if lines.as_ref().is_some_and(Vec::is_empty) {
        errors.push("an empty `Research:` section".to_owned());
    }
    (claims, errors)
}

#[cfg(test)]
mod tests;
