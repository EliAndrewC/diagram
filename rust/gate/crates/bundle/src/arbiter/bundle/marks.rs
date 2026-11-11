//! A round's findings and how each stands to the rounds before it (from `arbiter_bundle.py`, feature 375): NEW, REPEATED (an earlier round raised it) or REVERSING (its EDIT undoes an earlier round's), what the arbiter's bundle and a record check's earlier rounds (feature 393) both mark.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::verdict_of;
use l7r_guard::shared::checks::reply;
use l7r_guard::shared::py_text::{is_space, strip};
use serde_json::Value;

use crate::difflib::{opcodes, Tag};
use crate::record::bundle::{findall, head, hit, py_repr, pyre, split_on};
use crate::record::py_lines;
use crate::record::repo::read_text;

static NUMBERED_START: LazyLock<Regex> = LazyLock::new(|| pyre(r"^\s{0,3}(?:\*\*)?\d+[.)]\s+\S"));
static TOP_START: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"^(?:[-*]\s+\S|\*\*[A-Z][^*]{2,}\*\*|(?:FIX|NOTE)\s+M\d+\b)"));
static MRULE: LazyLock<Regex> = LazyLock::new(|| pyre(r"\bM\d+(?:\.\d+)?\b"));
static NOT_FINDING: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r"(?i)^(?:`?/tmp/l7r-check\S*`?\s*$|`?\S*MANIFEST\.md`?\s*$|(?:\*\*)?(?:ok|pass|passes|clean|confirmed|dismissed|ordinary english)\b)",
    )
});
static QUOTED: LazyLock<Regex> = LazyLock::new(|| {
    pyre("[\"\u{201c}'\u{2018}\u{300c}]([^\"\u{201d}'\u{2019}\u{300d}\n]{12,})[\"\u{201d}'\u{2019}\u{300d}]")
});
static PAGE_REF: LazyLock<Regex> = LazyLock::new(|| pyre(r"\b(\d{4})(?=[-.\s,;:)]|$)"));
static CODE: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r"\b(?:D\d+|FR-\d+|SC-\d+|ACCURACY|REFERENCES|GAPS|COVERAGE|TRUTH|LINKS|VOCABULARY|SESSION NOTE|HISTORY)\b",
    )
});
static UNRECORDED: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r"(?i)no page (?:holds|gives|says|records)|needs new research|not recorded|unrecorded|no source gives",
    )
});
static MARKER: LazyLock<Regex> = LazyLock::new(|| pyre(r"^(?:(?:\*\*)?\d+[.)]\s+|[-*]\s+)"));
static SENTENCES: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?<=[.;])\s+|\n"));
const STOP: [&str; 26] = [
    "the", "a", "an", "of", "to", "in", "on", "and", "or", "is", "are", "was", "were", "it", "its",
    "this", "that", "with", "as", "by", "for", "from", "be", "at", "not", "no",
];

/// `" ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())`.
#[must_use]
pub fn words(text: &str) -> String {
    let lowered: String = text
        .to_lowercase()
        .chars()
        .map(|c| {
            if c.is_ascii_lowercase() || c.is_ascii_digit() {
                c
            } else {
                ' '
            }
        })
        .collect();
    lowered
        .split(' ')
        .filter(|w| !w.is_empty())
        .collect::<Vec<_>>()
        .join(" ")
}

/// A reply's findings, each WHOLE - its first line with its continuation lines and sub-bullets (`findings_of`).
pub fn findings_of(reply_text: &str) -> Vec<String> {
    let lines = py_lines(reply_text);
    let numbered = lines.iter().any(|ln| hit(&NUMBERED_START, ln));
    let mut out: Vec<Vec<String>> = Vec::new();
    let mut open = false;
    for ln in lines {
        let s = strip(ln);
        let starts = if numbered {
            hit(&NUMBERED_START, ln)
        } else {
            hit(&TOP_START, ln)
        };
        if starts {
            out.push(vec![s.to_owned()]);
            open = true;
        } else if s.is_empty() || s.starts_with('#') {
            open = false;
        } else if open
            && (ln.chars().next().is_some_and(is_space) || s.starts_with(['-', '*', '>']))
        {
            if let Some(last) = out.last_mut() {
                last.push(s.to_owned());
            }
        } else {
            open = false;
        }
    }
    out.iter()
        .map(|item| MARKER.replace(&item.join(" "), "").into_owned())
        .filter(|f| f.chars().count() >= 12 && !hit(&NOT_FINDING, f))
        .collect()
}

fn content(text: &str) -> HashSet<String> {
    words(text)
        .split(' ')
        .filter(|w| w.chars().count() > 3 && !STOP.contains(w))
        .map(str::to_owned)
        .collect()
}

fn set_of(pattern: &Regex, text: &str, g: usize) -> HashSet<String> {
    findall(pattern, text, g).into_iter().collect()
}

fn quotes(text: &str) -> HashSet<String> {
    findall(&QUOTED, text, 1).iter().map(|q| words(q)).collect()
}

#[expect(clippy::cast_precision_loss, reason = "word counts")]
fn overlap(a: &HashSet<String>, b: &HashSet<String>) -> f64 {
    a.intersection(b).count() as f64 / a.union(b).count().max(1) as f64
}

/// Whether finding `f` re-raises an earlier one (`_repeats`).
fn repeats(f: &str, earlier: &[String]) -> bool {
    let (w, q, pages, codes, mine) = (
        words(f),
        quotes(f),
        set_of(&PAGE_REF, f, 1),
        set_of(&CODE, f, 0),
        content(f),
    );
    let rules = set_of(&MRULE, f, 0);
    earlier.iter().any(|e| {
        if w == words(e) || !q.is_disjoint(&quotes(e)) {
            return true;
        }
        let share = overlap(&mine, &content(e));
        (!pages.is_disjoint(&set_of(&PAGE_REF, e, 1))
            && (!codes.is_disjoint(&set_of(&CODE, e, 0)) || share >= 0.35))
            || (!rules.is_disjoint(&set_of(&MRULE, e, 0)) && share >= 0.25)
    })
}

/// The words `n` adds to `o` when it keeps every word of `o` in order, else None (`_insertion`).
fn insertion(o: &str, n: &str) -> Option<String> {
    let (wa, wb) = (words(o), words(n));
    let a: Vec<&str> = wa.split(' ').filter(|w| !w.is_empty()).collect();
    let b: Vec<&str> = wb.split(' ').filter(|w| !w.is_empty()).collect();
    let ops = opcodes(&a, &b);
    if a.is_empty()
        || ops
            .iter()
            .any(|op| matches!(op.0, Tag::Delete | Tag::Replace))
    {
        return None;
    }
    Some(
        ops.iter()
            .filter(|op| op.0 == Tag::Insert)
            .flat_map(|op| b[op.3..op.4].iter().copied())
            .collect::<Vec<_>>()
            .join(" "),
    )
}

fn trigrams(text: &str) -> HashSet<Vec<String>> {
    let w: Vec<String> = words(text)
        .split(' ')
        .filter(|x| x.chars().count() > 3 && !STOP.contains(x))
        .map(str::to_owned)
        .collect();
    w.windows(3).map(<[String]>::to_vec).collect()
}

/// An EDIT that adds back words an earlier EDIT deleted (`_near_reversal`).
fn near_reversal(o: &str, n: &str, earlier: &[(String, String)]) -> bool {
    if let Some(inserted) = insertion(o, n) {
        let tail = trigrams(&inserted);
        return earlier.iter().any(|(eo, en)| {
            let gone: HashSet<Vec<String>> =
                trigrams(eo).difference(&trigrams(en)).cloned().collect();
            !tail.is_disjoint(&gone)
        });
    }
    let added: HashSet<String> = content(n).difference(&content(o)).cloned().collect();
    earlier.iter().any(|(eo, en)| {
        let gone: HashSet<String> = content(eo).difference(&content(en)).cloned().collect();
        added.intersection(&gone).count() >= 2
    })
}

/// Each round's findings, `(mark, finding)` (`mark_rounds`); `others` are other checks' EDITs on the subject.
pub fn mark_rounds(replies: &[String], others: &[(String, String)]) -> Vec<Vec<(String, String)>> {
    let mut seen: Vec<String> = Vec::new();
    let mut edits: Vec<(String, String)> = others.to_vec();
    let mut out = Vec::new();
    for r in replies {
        let blocks: Vec<(String, String)> = reply::blocks(r)
            .into_iter()
            .map(|(_, o, n)| (o, n))
            .collect();
        let mut marked = Vec::new();
        if verdict_of(r) != "clean" {
            for f in findings_of(r) {
                let mark = if repeats(&f, &seen) {
                    "REPEATED"
                } else {
                    "NEW"
                };
                marked.push((mark.to_owned(), f.clone()));
                seen.push(f);
            }
        }
        seen.extend(
            split_on(&SENTENCES, r)
                .into_iter()
                .filter(|s| hit(&UNRECORDED, s))
                .map(str::to_owned),
        );
        for (o, n) in &blocks {
            if edits.iter().any(|(eo, en)| eo == n && en == o) {
                marked.push((
                    "REVERSING".to_owned(),
                    format!(
                        "EDIT {} -> {} undoes an earlier round's fix",
                        py_repr(o),
                        py_repr(n)
                    ),
                ));
            } else if near_reversal(o, n, &edits) {
                marked.push((
                    "REVERSING".to_owned(),
                    format!(
                        "EDIT {} -> {} adds back words an earlier fix took out",
                        py_repr(o),
                        py_repr(n)
                    ),
                ));
            }
        }
        edits.extend(blocks);
        out.push(marked);
    }
    out
}

/// Where a background agent's transcript lives, by its id.
#[must_use]
pub fn transcripts() -> PathBuf {
    crate::measure::home().join(".claude").join("projects")
}

/// `sorted(TRANSCRIPTS.glob("*/*/subagents/agent-<aid>.jsonl"))`'s first.
#[must_use]
pub fn transcript_of(base: &Path, aid: &str) -> Option<PathBuf> {
    let name = format!("agent-{aid}.jsonl");
    let mut found: Vec<PathBuf> = Vec::new();
    for a in std::fs::read_dir(base).into_iter().flatten().flatten() {
        for b in std::fs::read_dir(a.path()).into_iter().flatten().flatten() {
            let p = b.path().join("subagents").join(&name);
            if p.is_file() {
                found.push(p);
            }
        }
    }
    crate::record::bundle::sort_paths(&mut found);
    found.into_iter().next()
}

/// A round's reply: the one the hook kept, else the last text of the agent's own transcript (`reply_of`).
#[must_use]
pub fn reply_of(v: &Value) -> String {
    reply_in(v, &transcripts())
}

/// [`reply_of`], the transcripts under `base`.
pub fn reply_in(v: &Value, base: &Path) -> String {
    let kept = v
        .get("reply")
        .and_then(Value::as_str)
        .filter(|r| !r.is_empty());
    if let Some(path) = kept.map(Path::new).filter(|p| p.is_file()) {
        return read_text(path).unwrap_or_default();
    }
    let aid = match v.get("aid") {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Null) | None => String::new(),
        Some(other) => other.to_string(),
    };
    if aid.is_empty() {
        return String::new();
    }
    transcript_of(base, &aid)
        .map_or_else(String::new, |t| reply::reply_of(&t.to_string_lossy(), ""))
}

static LINKED: LazyLock<Regex> = LazyLock::new(|| pyre(r"research/questions/[^\s,;]+?\.html"));
static KEYED_LINE: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?m)^(?:Entry|Drawing):(.*)$"));

/// The files a subject's checks read: a question's pages, or a pop-up's file with the pages its Entry: and Drawing: name.
#[must_use]
pub fn subject_files(root: &Path, subject: &str) -> Vec<String> {
    if let Some(q) = subject.strip_prefix("q:") {
        let dir = root.join("research").join("questions");
        let prefix = format!("{q}-");
        let mut found: Vec<String> = std::fs::read_dir(&dir)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .filter(|n| n.starts_with(&prefix))
            .map(|n| format!("research/questions/{n}"))
            .collect();
        found.sort();
        return found;
    }
    if let Some(name) = subject.strip_prefix("modal:") {
        let own = format!("l7r/diagram/interactive/assets/modals/{name}.md");
        let text = read_text(&root.join(&own)).unwrap_or_default();
        let keyed = findall(&KEYED_LINE, &text, 1).join("\n");
        let mut out = vec![own];
        for f in findall(&LINKED, &keyed, 0) {
            if !out.contains(&f) && root.join(&f).is_file() {
                out.push(f);
            }
        }
        return out;
    }
    Vec::new()
}

/// The last answered round's EDIT blocks, each marked applied or not against the files as they stand (`last_edits`).
#[must_use]
pub fn last_edits(root: &Path, reply_text: &str, files: &[String]) -> Vec<String> {
    let text = files
        .iter()
        .filter(|f| root.join(f).is_file())
        .map(|f| read_text(&root.join(f)).unwrap_or_default())
        .collect::<Vec<_>>()
        .join("\n");
    reply::blocks(reply_text)
        .into_iter()
        .map(|(p, o, n)| {
            let done = text.contains(&n) && (!text.contains(&o) || n.contains(&o));
            format!(
                "- {}: {}: {} -> {}",
                if done { "APPLIED" } else { "NOT APPLIED" },
                if p.is_empty() {
                    "(its file)"
                } else {
                    p.as_str()
                },
                py_repr(head(&o, 120)),
                py_repr(head(&n, 120))
            )
        })
        .collect()
}

#[cfg(test)]
mod tests;
