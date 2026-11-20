//! The deferral's form (feature 451 T17, D15; FR-009): a `**Found and left?**` item that defers a defect states why it is not fixed in
//! this task, the task it is filed as and the open task it lands before, and a fix of a class of defect says how every instance was
//! found. Two of the window's first-round plan-review blocks were deferrals with no order (the spec's User Story 5).
//!
//! An item passes untouched when it says it is fixed in the task (`fixed here`, `fixed in this task`, `before its tick`, `before T<own>
//! lands`) or that it is no defect (`not a defect`, `no wrong outcome`: constitution XIV), and the whole answer when it opens with
//! `none` (the template's `<none - ...>` placeholder among them). Every other item is a deferral and owes its three parts.

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::super::sections::re;
use super::{has_label, shown};

/// The answer: from the bold question to the next bold line, heading, comment or rule.
static ANSWER: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?ms)^\*\*Found and left\?\*\*[ \t]*(.*?)(?=^\*\*[^*\n]+\*\*|^#|^<!--|^---|\z)")
});
static NONE: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)^\s*<?none\b"));
static BULLET: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^[-*] "));
/// Item 12 of an Approach block, the fix (`Before any fix`), to the next numbered item, bold line or heading.
static ITEM12: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?ms)^12\.\s+\*\*Before any fix\.?\*\*.*?(?=^\d+\.\s|^\*\*|^#|\z)"));
static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\s*- \[([ xX])\] (T\d+[a-z]?)\b"));
/// An item fixed in the task. "not fixed here" is a deferral's reason, never a fix.
static FIXED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)(?<!not )(?<!n't )\bfixed (?:here|in this task)\b|\bbefore (?:its|this task's) (?:tick|landing)\b",
    )
});
static NO_DEFECT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\bnot a defect\b|\bno wrong outcome\b"));
/// Why it is not fixed here: the words, then a colon, a dash, a parenthesis or a "because", and two words more.
static REASON: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\bnot fixed (?:here|in this task)\b\s*(?:[:(;,-]|because\b|since\b|as\b)\s*[^\s.]+\s+[^\s.]+",
    )
});
static FILED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\b(?:filed as|added to|folded into)\s+`?(T\d+[a-z]?)\b"));
/// The order and its ids: "lands before T22", "lands before T07, T08 and T14".
static ORDER: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\blands\s+before\s+`?(T\d+[a-z]?`?(?:(?:\s*,\s*(?:and\s+)?|\s+and\s+)`?T\d+[a-z]?`?)*)",
    )
});
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"T\d+[a-z]?"));
/// A class of defect (D15: "every writer", "every form", "every file of a kind", "each of the ...", "all ..."): the nouns a defect's
/// class is named by. "every crate", "every test" and "every suite" name what a tool or a run covers, not a defect's reach - the
/// throwaway replay read T14's "`make format` formats every crate" as a class fix (measured 2026-11-20), so they are left out.
static CLASS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\bevery\s+(?:\w+\s+)?(?:writers?|readers?|forms?|files?|callers?|instances?|cop(?:y|ies)|sites?|guards?)\b|\beach of the\b|\ball (?:of )?the\s+(?:\w+\s+)?(?:writers|readers|forms|files|callers|instances|copies|sites|guards)\b",
    )
});
static OBSERVED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\bobserved\s+20\d\d-\d\d-\d\d\s*,\s*method:"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s+(T\d+[a-z]?)\b"));

/// The feature's task boxes: each id filed in `tasks.md` or `tasks-done.md`, and those an unticked box of `tasks.md` holds.
pub(super) struct Boxes {
    pub(super) filed: BTreeSet<String>,
    pub(super) open: BTreeSet<String>,
}

/// The boxes of `spec_dir`'s `tasks.md` and `tasks-done.md`.
pub(super) fn boxes(spec_dir: &Path) -> Boxes {
    let mut out = Boxes {
        filed: BTreeSet::new(),
        open: BTreeSet::new(),
    };
    for (name, live) in [("tasks.md", true), ("tasks-done.md", false)] {
        let text = std::fs::read_to_string(spec_dir.join(name)).unwrap_or_default();
        for c in BOX.captures_iter(&text).map_while(Result::ok) {
            out.filed.insert(c[2].to_owned());
            if live && &c[1] == " " {
                out.open.insert(c[2].to_owned());
            }
        }
    }
    out
}

/// Each item of each found-and-left answer that is not `none`: (its start, its end, its text) in `section`. An answer's `- ` items
/// each, and its words before the first; an answer with no list, one item.
fn items(section: &str) -> Vec<(usize, usize, &str)> {
    let mut out = Vec::new();
    for c in ANSWER.captures_iter(section).map_while(Result::ok) {
        let Some(body) = c.get(1) else { continue };
        if NONE.is_match(body.as_str()).unwrap_or(false) {
            continue;
        }
        let mut cuts: Vec<usize> = BULLET
            .find_iter(body.as_str())
            .map_while(Result::ok)
            .map(|m| body.start() + m.start())
            .collect();
        cuts.insert(0, body.start());
        cuts.push(body.end());
        for pair in cuts.windows(2) {
            let text = &section[pair[0]..pair[1]];
            let lead = text.len() - text.trim_start().len();
            let trimmed = text.trim();
            if !trimmed.is_empty() {
                let start = pair[0] + lead;
                out.push((start, start + trimmed.len(), trimmed));
            }
        }
    }
    out
}

/// The task id `section`'s first heading opens with, or "".
fn own_id(section: &str) -> String {
    HEADING
        .captures(section)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| c[1].to_owned())
}

/// Whether an item says it is fixed in the task, or no defect.
fn not_deferred(item: &str, own: &str) -> bool {
    let hit = |p: &Regex| p.is_match(item).unwrap_or(false);
    let own_landing = !own.is_empty()
        && item
            .to_lowercase()
            .contains(&format!("before {} lands", own.to_lowercase()));
    hit(&FIXED) || hit(&NO_DEFECT) || own_landing
}

/// A deferral's ids: the ones it is filed as, and the ones it lands before.
fn ids(item: &str) -> (Vec<String>, Vec<String>) {
    let filed = FILED
        .captures_iter(item)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    let order = ORDER
        .captures_iter(item)
        .map_while(Result::ok)
        .flat_map(|c| {
            ID.find_iter(&c[1])
                .map_while(Result::ok)
                .map(|m| m.as_str().to_owned())
                .collect::<Vec<_>>()
        })
        .collect();
    (filed, order)
}

/// The deferrals of `section`: (span, text, filed ids, order ids).
type Deferral<'s> = ((usize, usize), &'s str, Vec<String>, Vec<String>);

fn deferrals(section: &str) -> Vec<Deferral<'_>> {
    let own = own_id(section);
    items(section)
        .into_iter()
        .map(|(a, z, text)| {
            let (filed, order) = ids(text);
            ((a, z), text, filed, order)
        })
        // an item naming a task it is filed as or lands before defers, whatever else it says: a paragraph holding a deferral and a
        // note of no defect is judged as the deferral (449's T226 and T234 read so, measured 2026-11-20, the throwaway replay)
        .filter(|(_, text, filed, order)| {
            !filed.is_empty() || !order.is_empty() || !not_deferred(text, &own)
        })
        .collect()
}

/// Every found-and-left item that defers without its reason, its task id or its order, whose order names its own id, or whose ids
/// name no filed task: (its span, what it lacks and its words) - the timeless half, which `make plan-delta` runs too.
pub(super) fn unformed(section: &str, boxes: &Boxes) -> Vec<((usize, usize), String)> {
    let mut out = Vec::new();
    for (span, text, filed, order) in deferrals(section) {
        let mut lacks: Vec<String> = Vec::new();
        if !REASON.is_match(text).unwrap_or(false) {
            lacks.push("no reason".to_owned());
        }
        if filed.is_empty() {
            lacks.push("no task id".to_owned());
        }
        if order.is_empty() {
            lacks.push("no order".to_owned());
        }
        let mut faults = vec![lacks.join(", ")];
        faults.retain(|f| !f.is_empty());
        if let Some(id) = order.iter().find(|o| filed.contains(o)) {
            faults.push(format!("orders nothing: it lands before its own id {id}"));
        }
        let mut seen = BTreeSet::new();
        for id in filed.iter().chain(&order) {
            if !boxes.filed.contains(id) && seen.insert(id) {
                faults.push(format!("{id} is filed in no tasks.md or tasks-done.md"));
            }
        }
        if !faults.is_empty() {
            out.push((span, format!("[{}] {}", faults.join("; "), shown(text))));
        }
    }
    out
}

/// Every deferral whose task id or "lands before" id names a task filed but not OPEN - `make decide`'s half, judged once, at the
/// decision (D15).
pub(super) fn closed(section: &str, boxes: &Boxes) -> Vec<((usize, usize), String)> {
    let mut out = Vec::new();
    for (span, text, filed, order) in deferrals(section) {
        let shut: BTreeSet<&String> = filed
            .iter()
            .chain(&order)
            .filter(|id| boxes.filed.contains(*id) && !boxes.open.contains(*id))
            .collect();
        if !shut.is_empty() {
            let named: Vec<String> = shut
                .into_iter()
                .map(|id| format!("{id} is not an open task"))
                .collect();
            out.push((span, format!("[{}] {}", named.join("; "), shown(text))));
        }
    }
    out
}

/// Every found-and-left item and item 12 ("Before any fix") naming a class of defect with no `observed <date>, method: ...` line
/// (or a `measured <date> (<method>)` label).
pub(super) fn class_unlabeled(section: &str) -> Vec<((usize, usize), String)> {
    let mut units: Vec<(usize, usize, &str)> = items(section);
    units.extend(ITEM12.find_iter(section).map_while(Result::ok).map(|m| {
        (
            m.start(),
            m.start() + m.as_str().trim_end().len(),
            m.as_str().trim_end(),
        )
    }));
    units
        .into_iter()
        .filter(|(_, _, text)| {
            CLASS.is_match(text).unwrap_or(false)
                && !OBSERVED.is_match(text).unwrap_or(false)
                && !has_label(text)
        })
        .map(|(a, z, text)| ((a, z), shown(text)))
        .collect()
}

#[cfg(test)]
mod tests;
