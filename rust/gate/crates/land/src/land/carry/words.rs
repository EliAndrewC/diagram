//! A conflict in PROSE merged by words (451 T300, part 2): the registry rows, help lines and module paragraphs that two tasks
//! each add words to are one very long line each (`rust/gate/CLAUDE.md` averages 885 characters a line), so a line merge calls two
//! separate additions one conflict. Here a hunk's three sides are cut into WORDS - a word is a maximal run of non-whitespace
//! characters, and each run of whitespace between two words, its line ends included, is a token of its own, so the merged text
//! holds every space and line break a side wrote - and each side's changes against the base (`difflib`'s opcodes, the session's
//! hand scripts' own measure, `resolve334.py` and `resolve336.py` of 2026-11-26) are applied together.
//!
//! It never chooses: a change of one side that reaches into the other's (the same base words changed by both, or one's insertion
//! inside what the other replaced) stops; the same change made by both is made once; two insertions at one point are both kept,
//! the clone's first. And it never touches code - the hunk's every line, on all three sides and in the result, is a prose line of
//! its file's kind ([`Prose`]), and a Makefile help line's target and prerequisites (what stands before its `##`) are the same
//! on every side.
//!
//! One side adding WHOLE LINES beside a line the other reworded is the same merge (the added lines are an insertion of words):
//! tried on the two real cases, `scripts/container/builder-brief.md` in T334's carry and a reflowed `//!` paragraph of
//! `rust/gate/crates/task/src/builder_tree.rs` in T336's, the result was the session's commit byte for byte.

use l7r_gate_core::difflib::{opcodes, Tag};

/// The file kinds whose prose is merged by words, by path.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub(super) enum Prose {
    /// A Markdown file: every line.
    Markdown,
    /// A Makefile: a comment line, and a target's line holding its ` ## ` help.
    Makefile,
    /// A Rust source: a line that is wholly a comment (`//`, `///`, `//!`).
    Rust,
}

/// The kind of `path`, where it has one.
pub(super) fn kind(path: &str) -> Option<Prose> {
    let name = path.rsplit('/').next().unwrap_or(path);
    if name == "Makefile" {
        return Some(Prose::Makefile);
    }
    match name.rsplit_once('.').map(|(_, ext)| ext) {
        Some("md") => Some(Prose::Markdown),
        Some("rs") => Some(Prose::Rust),
        _ => None,
    }
}

/// The part of a prose line that is not prose - a help line's target and prerequisites, empty elsewhere - or `None` where the
/// line is no prose line of `kind`.
fn fixed(line: &str, kind: Prose) -> Option<&str> {
    match kind {
        Prose::Markdown => Some(""),
        Prose::Rust => line.trim_start().starts_with("//").then_some(""),
        Prose::Makefile if line.starts_with('#') => Some(""),
        Prose::Makefile if line.starts_with('\t') => None,
        Prose::Makefile => line.split_once(" ## ").map(|(head, _)| head),
    }
}

/// The fixed parts of a side's lines, the empty ones left out - or the first line that is no prose.
fn fixed_parts(text: &str, kind: Prose) -> Result<Vec<&str>, String> {
    let mut parts = Vec::new();
    for line in text.lines() {
        match fixed(line, kind) {
            Some("") => {}
            Some(head) => parts.push(head),
            None => return Err(format!("a line that is not prose: {}", brief(line))),
        }
    }
    Ok(parts)
}

/// A line's opening, short enough for a message.
fn brief(text: &str) -> String {
    let short: String = text.trim().chars().take(60).collect();
    format!("`{short}`")
}

/// `text` as its words and the whitespace runs between them, in order: joined, they are `text`.
pub(super) fn tokens(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    let mut space = None;
    for (at, c) in text.char_indices() {
        if space.is_some_and(|was| was != c.is_whitespace()) {
            out.push(&text[start..at]);
            start = at;
        }
        space = Some(c.is_whitespace());
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

const STRAYED: &str = "the merged words are no longer prose lines of the file";

/// One side's change: the base tokens `from..to` replaced by `with`.
#[derive(PartialEq, Eq)]
struct Edit<'t> {
    from: usize,
    to: usize,
    with: &'t [&'t str],
}

fn edits<'t>(base: &[&str], side: &'t [&'t str]) -> Vec<Edit<'t>> {
    opcodes(base, side)
        .into_iter()
        .filter(|op| op.0 != Tag::Equal)
        .map(|(_, from, to, j1, j2)| Edit {
            from,
            to,
            with: &side[j1..j2],
        })
        .collect()
}

/// The three sides of one hunk merged by words - or why it is left to a hand.
pub(super) fn merged(base: &str, ours: &str, theirs: &str, kind: Prose) -> Result<String, String> {
    let held = fixed_parts(base, kind)?;
    if fixed_parts(ours, kind)? != held || fixed_parts(theirs, kind)? != held {
        return Err("a side changed a help line's target, not only its words".to_owned());
    }
    let (b, o, t) = (tokens(base), tokens(ours), tokens(theirs));
    let mut all = edits(&b, &o);
    // the clone's first where both insert at one point: the sort is stable
    all.extend(edits(&b, &t));
    all.sort_by_key(|e| (e.from, e.to));
    all.dedup();
    let mut out = String::new();
    let mut at = 0;
    for edit in &all {
        if edit.from < at {
            return Err(format!(
                "both sides changed the same words: {}",
                brief(&b[edit.from..at].concat())
            ));
        }
        out += &b[at..edit.from].concat();
        out += &edit.with.concat();
        at = edit.to;
    }
    out += &b[at..].concat();
    // a guard no fixture reaches: every side held the same fixed parts and only words moved, so the result is prose too
    let kept = fixed_parts(&out, kind).is_ok_and(|parts| parts == held);
    kept.then_some(out).ok_or_else(|| STRAYED.to_owned())
}
