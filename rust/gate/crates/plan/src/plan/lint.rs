//! What `make decide` refuses before a plan section reaches its review (feature 385 T84 and T86; feature 449 T066, from `plan_lint.py`).
//! The evening of 2026-10-18 sent 42 plan reviews, and four came back unreviewable for what a script can see first.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use super::sections::re;
use crate::checks::{figure_pattern, one_shot_pattern};

const RED_EXIT_HINT: &str = "Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.";

static GM: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bthe GM(?:'s)?\b"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z0-9]+"));
static CODE_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static ITEM4: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^4\. \*\*.*?(?=^\d+\. \*\*|^#|\z)"));
static SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"`([^`\n]*)`"));
static NOT_A_FIGURE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\b\d{4}-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?\b|\b\d\d:\d\d(?::\d\d)?Z?\b|\b(?:FR|SC)-\d+[a-z]?\b|\b[TDA]\d+[a-z]?\b|\b0\d{3}\b",
    )
});
static NAMED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(?:round|rounds|seed|seeds|hour|amendment|item|items|change|wave|batch|step|task|feature|proposal|part|tier|version|line|group)\s+\d+(?:\s*(?:-|and|to)\s*\d+)?\b",
    )
});
static LABEL: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?is)(?=.*\bmeasured\b)(?=.*\b20\d\d-\d\d-\d\d\b)(?=.*\()|\bm:[\w.-]+"));
static COMMAND_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"/|::|=|\bmake "));
static SPLIT4: LazyLock<Regex> = LazyLock::new(|| re(r"(?<=\.)\s+|\n(?=\S)"));
static LEAD4: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*4\."));
static BARE_FIGURE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w-])\d[\d,.]*(?![\w-])"));
static FENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^```.*?^```"));
static SPLIT_UNIT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<=[.;])\s+|\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))"));
/// A decided figure's labels (root CLAUDE.md, "every rendering decision is labeled"), and a source's verdict in a research-record plan.
static DECISION_LABEL: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\b(?:GUESS|CONVENTION|DEVIATION|UNRESEARCHED|ACCURATE|HISTORICALLY ACCURATE|ATTESTED|SILENT)\b|this project's arithmetic|research/questions/|\bknob\b|\bR\d+\b",
    )
});
/// A rule stated as a figure, which measures nothing: the coverage floor.
static RULE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\b100\s*%\s+(?:code\s+|line\s+)?coverage\b"));
static APPROACH_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^### (T\d+[a-z]?) Approach\b.*$"));
static NEXT_23: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,3} "));
static ITEM6: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^6\.\s.*?(?=^\d+\.\s|\z)"));
static OPEN_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[ \] (T\d+[a-z]?)\b"));

fn folded(text: &str) -> String {
    let lower = text.to_lowercase();
    let words: Vec<&str> = WORD
        .find_iter(&lower)
        .flatten()
        .map(|m| m.as_str())
        .collect();
    format!(" {} ", words.join(" "))
}

fn split_on<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    let mut out = Vec::new();
    let mut at = 0;
    for gap in pattern.find_iter(text).flatten() {
        out.push(&text[at..gap.start()]);
        at = gap.end();
    }
    out.push(&text[at..]);
    out
}

/// Each double-quoted span that follows "the GM" within the same sentence; a code span names words, it quotes no one.
fn gm_quotes(section: &str) -> Vec<String> {
    let masked = CODE_SPAN
        .replace_all(section, |c: &Captures<'_>| " ".repeat(c[0].len()))
        .into_owned();
    let bytes = masked.as_bytes();
    let mut out: Vec<String> = Vec::new();
    for m in GM.find_iter(&masked).flatten() {
        let line_start = masked[..m.start()].rfind('\n').map_or(0, |p| p + 1);
        if masked[line_start..m.start()].matches('"').count() % 2 == 1 {
            continue;
        }
        let (mut i, mut quoting, mut start) = (m.end(), false, 0);
        while i < bytes.len() {
            let next = bytes.get(i + 1).copied();
            let ch = bytes[i];
            if ch == b'"' {
                if quoting && !out.iter().any(|q| q == &section[start..i]) {
                    out.push(section[start..i].to_owned());
                }
                start = i + 1;
                quoting = !quoting;
            } else if !quoting
                && ((ch == b'\n' && matches!(next, Some(b'\n') | None))
                    || (matches!(ch, b'.' | b'!' | b'?')
                        && matches!(next, Some(b' ' | b'\n') | None)))
            {
                break;
            }
            i += 1;
        }
    }
    out
}

/// The GM quotes whose words, folded, are not a run in the request folded the same way (D105) - every length, no escape.
fn gm_quotes_missing(section: &str, request: &str) -> Vec<String> {
    let req = folded(request);
    gm_quotes(section)
        .into_iter()
        .filter(|q| {
            let pieces = q.split("...").flat_map(|p| p.split('\u{2026}'));
            !folded(q).trim().is_empty()
                && !pieces
                    .filter(|p| !folded(p).trim().is_empty())
                    .all(|p| req.contains(&folded(p)))
        })
        .collect()
}

/// The first figure Approach item 4 states whose own sentence carries no label, or "" (feature 385 T86).
fn unlabeled_figure(section: &str) -> String {
    let Ok(Some(item)) = ITEM4.find(section) else {
        return String::new();
    };
    let spaced = SPAN
        .replace_all(item.as_str(), |c: &Captures<'_>| {
            if COMMAND_SPAN.is_match(&c[1]).unwrap_or(false) {
                " ".to_owned()
            } else {
                c[1].to_owned()
            }
        })
        .into_owned();
    for sentence in split_on(&SPLIT4, &spaced) {
        let lead = LEAD4.replace(sentence, " ");
        let bare = NOT_A_FIGURE.replace_all(&lead, " ");
        let bare = NAMED.replace_all(&bare, " ");
        if BARE_FIGURE.is_match(&bare).unwrap_or(false)
            && !LABEL.is_match(sentence).unwrap_or(false)
        {
            return sentence.trim().chars().take(160).collect();
        }
    }
    String::new()
}

/// The first sentence anywhere in the section stating a figure with a unit and carrying no label, or "" (feature 430 T05, D5).
fn unlabeled_unit_figure(section: &str) -> String {
    let text = FENCE.replace_all(section, " ").into_owned();
    for sentence in split_on(&SPLIT_UNIT, &text) {
        let bare = SPAN.replace_all(sentence, " ");
        let bare = NOT_A_FIGURE.replace_all(&bare, " ");
        let bare = RULE.replace_all(&bare, " ");
        let labeled = [&*LABEL, one_shot_pattern(), &*DECISION_LABEL]
            .iter()
            .any(|p| p.is_match(sentence).unwrap_or(false));
        if figure_pattern().is_match(&bare).unwrap_or(false) && !labeled {
            return sentence
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
                .chars()
                .take(160)
                .collect();
        }
    }
    String::new()
}

/// The task whose approach block's item 6 routes no red result through `make arbiter-ask` (D35's wording), or "".
fn missing_red_exit(section: &str) -> String {
    for c in APPROACH_HEAD.captures_iter(section).flatten() {
        let rest = &section[c.get(0).map_or(0, |g| g.end())..];
        let block = NEXT_23
            .find(rest)
            .ok()
            .flatten()
            .map_or(rest, |n| &rest[..n.start()]);
        let routed = ITEM6.find(block).ok().flatten().is_some_and(|m| {
            m.as_str().contains("make arbiter-ask") || m.as_str().contains("make budget-change")
        });
        if !routed {
            return c[1].to_owned();
        }
    }
    String::new()
}

/// In a plan whose tasks owe approach blocks, each open task with no `### Txx Approach` block in the plan or plan-done.md (D5).
fn tasks_without_approach(spec_dir: &Path, plan: &str) -> Vec<String> {
    let done = std::fs::read_to_string(spec_dir.join("plan-done.md")).unwrap_or_default();
    let joined = format!("{plan}\n{done}");
    let any = APPROACH_HEAD
        .is_match(&format!("{plan}{done}"))
        .unwrap_or(false);
    if !plan.contains("**Approach checklist**:") && !any {
        return Vec::new();
    }
    let tasks = std::fs::read_to_string(spec_dir.join("tasks.md")).unwrap_or_default();
    let have: Vec<String> = APPROACH_HEAD
        .captures_iter(&joined)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    OPEN_TASK
        .captures_iter(&tasks)
        .flatten()
        .map(|c| c[1].to_owned())
        .filter(|t| !have.contains(t))
        .collect()
}

/// Why `make decide` refuses this section, or "".
pub(super) fn refusal(spec_dir: &Path, section: &str) -> String {
    let req = std::fs::read_to_string(spec_dir.join("request.md")).unwrap_or_default();
    let missing = gm_quotes_missing(section, &req);
    if !missing.is_empty() {
        let shown: Vec<String> = missing
            .iter()
            .map(|q| format!("\"{}\"", q.trim().chars().take(160).collect::<String>()))
            .collect();
        return format!("the section quotes the GM with words request.md does not hold - add the GM's words to request.md verbatim, or correct the quote (feature 385 T84):\n  {}", shown.join("\n  "));
    }
    let fig = unlabeled_figure(section);
    if !fig.is_empty() {
        return format!("Approach item 4 states a figure whose sentence carries no `measured <YYYY-MM-DD> (<method>)` or `m:<key>` - label it where it stands (feature 385 T86):\n  {fig}");
    }
    let fig = unlabeled_unit_figure(section);
    if !fig.is_empty() {
        return format!("a figure with a unit whose sentence carries no label - a measurement `measured <YYYY-MM-DD> (<method>)`, `observed <YYYY-MM-DD>, method: ...` or `m:<key>`; a decided size its research label (GUESS, CONVENTION, ...), its page or its knob - label it where it stands (feature 430 D5):\n  {fig}");
    }
    let task = missing_red_exit(section);
    if !task.is_empty() {
        return format!("{task}'s approach item 6 routes no red result through `make arbiter-ask` - give it D35's red exit, as `make task-add`'s template words it (feature 430 D5):\n  {RED_EXIT_HINT}");
    }
    String::new()
}

/// Why `make plan-delta` writes no bundle, or "" (feature 430 T05, D5: a plan review is never dispatched on what a script can see).
pub(super) fn plan_refusal(spec_dir: &Path, plan: &str, bodies: &[String]) -> String {
    for body in bodies {
        let why = refusal(spec_dir, body);
        if !why.is_empty() {
            return why;
        }
    }
    let missing = tasks_without_approach(spec_dir, plan);
    if missing.is_empty() {
        return String::new();
    }
    format!("open tasks with no `### Txx Approach (checklist part A)` block in the plan - write one for each, `make task-add`'s template has the form (feature 430 D5):\n  {}", missing.join(", "))
}

#[cfg(test)]
mod tests;
