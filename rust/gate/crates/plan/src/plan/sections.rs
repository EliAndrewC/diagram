//! A plan read for its review (feature 449 T066, from `plan_sections.py`): each task's section and each block of a plan, their digests,
//! a typo told from a change, and which blocks decide nothing.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::plan_text::HEAD;
pub(super) use l7r_guard::shared::plan_text::{
    blocks, leading_task, ordered_sections, task_sections, TASK_ID,
};
use l7r_guard::shared::sha256;

/// Words a "typo" may never touch (feature 375 FR-005(b), plan D6): a number, a quantity, a negation or a quantifier changes a
/// decision however few letters it moves - "two" -> "ten", "all" -> "any", "must" -> "may".
const GUARDED: [&str; 74] = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "hundred",
    "thousand",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "half",
    "twice",
    "once",
    "double",
    "triple",
    "not",
    "no",
    "never",
    "none",
    "except",
    "unless",
    "only",
    "all",
    "any",
    "each",
    "every",
    "some",
    "few",
    "many",
    "most",
    "more",
    "less",
    "fewer",
    "may",
    "must",
    "should",
    "shall",
    "can",
    "cannot",
    "before",
    "after",
    "above",
    "below",
    "over",
    "under",
    "min",
    "max",
    "least",
];
/// How many words a typo-scale edit may change in the whole plan.
const TYPO_WORDS: usize = 3;

pub(super) fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[A-Za-z0-9]+"));
/// The line `make plan-archive` leaves where finished sections were (FR-044): out of every digest, so it owes no review.
pub(super) static ARCHIVE_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^<!-- plan-archive: [^\n]*? -->\n?"));
pub(super) static PART_B: LazyLock<Regex> = LazyLock::new(|| re(r"^### T\d+[a-z]?\s+part B \("));
static DEFINED: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\*\*(D\d+[a-z]?) - "));
static APPROACH: LazyLock<Regex> = LazyLock::new(|| re(r"^### T\d+[a-z]?\s+Approach\b"));
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(\d+)\.\s+\*\*[^*]*\*\*[ \t]*"));
/// The ids an approach answer may name and nothing else: decisions, requirements, criteria, research, tasks, a feature, a date.
static IDS: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\bD\d+[a-z]?\b|\bFR-\d+[a-z]?\b|\bSC-\d+\b|\bR\d+\b|\bT\d+[a-z]?\b|\bfeature \d{3}\b|\b\d{4}-\d\d-\d\d\b",
    )
});
static DECISION_ID: LazyLock<Regex> = LazyLock::new(|| re(r"\bD\d+[a-z]?\b"));
static FILLER: LazyLock<Regex> = LazyLock::new(|| re(r"(?:\s|[,;.:]|\band\b)+"));
static LANDS_OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\*\*Lands open\*\*:.*$"));
static BARE_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"\bT\d+[a-z]?\b"));
static REPEAT: LazyLock<Regex> = LazyLock::new(|| re(r"#\d+$"));
static PARENTHETICAL: LazyLock<Regex> = LazyLock::new(|| re(r"\s*\([^()]*\)\s*$"));
static DECISIONS_BLOCK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^#{3,4}\s+T\d+[a-z]?\s+Decisions\s*$"));
static NEXT_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s"));
static DECISION_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\*\*D\d+[a-z]?\s+-\s"));

pub(super) fn digest(data: &[u8]) -> String {
    sha256::hex(data)
}

pub(super) fn strip_archive(text: &str) -> String {
    ARCHIVE_LINE.replace_all(text, "").into_owned()
}

pub(super) fn block_digest(text: &str) -> String {
    digest(strip_archive(text).as_bytes())
}

/// The Damerau-Levenshtein distance of two short words (a transposition is one edit).
fn distance(a: &str, b: &str) -> usize {
    let (a, b): (Vec<char>, Vec<char>) = (a.chars().collect(), b.chars().collect());
    let mut prev2: Vec<usize> = Vec::new();
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    for i in 1..=a.len() {
        let mut cur = vec![i];
        for j in 1..=b.len() {
            let mut best = (prev[j] + 1)
                .min(cur[j - 1] + 1)
                .min(prev[j - 1] + usize::from(a[i - 1] != b[j - 1]));
            if i > 1 && j > 1 && a[i - 1] == b[j - 2] && a[i - 2] == b[j - 1] {
                best = best.min(prev2[j - 2] + 1);
            }
            cur.push(best);
        }
        prev2 = std::mem::replace(&mut prev, cur);
    }
    prev[b.len()]
}

fn words(text: &str) -> Vec<String> {
    let lower = text.to_lowercase();
    WORD.find_iter(&lower)
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// Whether `new` differs from `old` by typos alone (FR-005(b), plan D6): whitespace, re-wrapping, case and punctuation; at most three
/// words replaced, each by a near spelling, none of them a digit or a guarded word; no word added or removed. Anything else adds or
/// changes a decision - the conservative side, since a missed decision is the incident this gate exists for (feature 239).
pub(super) fn typo_only(old: &str, new: &str) -> bool {
    let (a, b) = (words(old), words(new));
    if a.len() != b.len() {
        return false;
    }
    let changed: Vec<(&String, &String)> = a.iter().zip(&b).filter(|(x, y)| x != y).collect();
    changed.len() <= TYPO_WORDS
        && changed.iter().all(|(x, y)| {
            let guarded = GUARDED.contains(&x.as_str()) || GUARDED.contains(&y.as_str());
            let digit = x.chars().chain(y.chars()).any(char::is_numeric);
            let allowed = if x.chars().count().min(y.chars().count()) <= 4 {
                1
            } else {
                2
            };
            !guarded && !digit && distance(x, y) <= allowed
        })
}

/// `old` with one task id renamed to the task a recorded split moved its work to, where that rename is the whole edit (the round
/// arbiter's fix on hour:385-approach-checklist@28). A split is recorded when the new id's heading says it was "found working <task>".
pub(super) fn repointed(old: &str, new: &str, task: &str, plan: &str) -> String {
    let marker = re(&format!(r"found working {}\b", fancy_regex::escape(task)));
    let splits: Vec<String> = task_sections(plan)
        .into_iter()
        .filter(|(t, sec)| {
            t != task
                && marker
                    .is_match(sec.split('\n').next().unwrap_or(""))
                    .unwrap_or(false)
        })
        .map(|(t, _)| t)
        .collect();
    let named: BTreeSet<&str> = TASK_ID
        .find_iter(old)
        .flatten()
        .map(|m| m.as_str())
        .collect();
    for b in &splits {
        for a in named.iter().filter(|a| **a != b && **a != task) {
            let candidate = re(&format!(r"\b{}\b", fancy_regex::escape(a)))
                .replace_all(old, b.as_str())
                .into_owned();
            if typo_only(&candidate, new) {
                return candidate;
            }
        }
    }
    old.to_owned()
}

/// The section without its part B blocks that decide nothing.
pub(super) fn quiet_out(section: &str, plan: &str) -> String {
    let mut out = section.to_owned();
    for (key, body, _) in blocks(section) {
        if decides_nothing(&key, &body, plan, "") {
            out = out.replace(&body, "");
        }
    }
    out
}

fn defined_ids(text: &str) -> BTreeSet<String> {
    DEFINED
        .captures_iter(text)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect()
}

fn decision_ids(text: &str) -> BTreeSet<String> {
    DECISION_ID
        .find_iter(text)
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// `make task-add`'s own wording for items 6 and 9 (feature 430 D5): an answer that is the template's says nothing new. Read from the
/// template itself ([`super::template`], feature 449 T135), where this read `scripts/task-add.py`'s source text from the tree the wrapper
/// named: item 6 is the template's line after its bold label, the red exit in it.
fn template_answers() -> BTreeMap<u32, String> {
    let item6 = super::template::TEMPLATE
        .lines()
        .find(|l| l.starts_with("6."))
        .and_then(|l| l.splitn(3, "**").nth(2))
        .unwrap_or("");
    BTreeMap::from([
        (6, item6.trim().to_owned()),
        (9, "Its tests red without D<n>.".to_owned()),
    ])
}

/// An approach block that matches the template and decides nothing (feature 430 T05, D5): every answer, its ids set aside, is bare or
/// the template's own wording, it holds no number outside those ids, and every `D<n>` it names is defined elsewhere.
fn approach_decides_nothing(body: &str, plan: &str, done: &str) -> bool {
    let marks: Vec<(u32, usize, usize)> = ITEM
        .captures_iter(body)
        .flatten()
        .map(|c| {
            (
                c[1].parse().unwrap_or(0),
                c.get(0).map_or(0, |g| g.start()),
                c.get(0).map_or(0, |g| g.end()),
            )
        })
        .collect();
    if marks.is_empty() {
        return false;
    }
    let template = template_answers();
    let mut own = body.to_owned();
    for (i, (n, _, end)) in marks.iter().enumerate() {
        let stop = marks.get(i + 1).map_or(body.len(), |m| m.1);
        let answer = body[*end..stop]
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ");
        if let Some(wording) = template.get(n) {
            let first = DECISION_ID
                .find(&answer)
                .ok()
                .flatten()
                .map_or("D<n>", |m| m.as_str());
            if answer == wording.replace("D<n>", first) {
                if *n == 6 {
                    own = own.replace(wording, "");
                }
                continue;
            }
        }
        let rest = IDS.replace_all(&answer, " ");
        if rest.chars().any(char::is_numeric) {
            return false;
        }
        let bare = FILLER.replace_all(&rest, " ").trim().to_lowercase();
        if !["", "n/a", "none", "yes", "one landing"].contains(&bare.as_str()) {
            return false;
        }
    }
    decision_ids(&own).is_subset(&defined_ids(&format!("{}{done}", plan.replace(body, ""))))
}

/// A part B block that decides nothing (feature 385 T75, plan D94): item 4 "No", item 5 "Neither", and every `D<n>` defined elsewhere.
/// An approach block is asked its own form.
pub(super) fn decides_nothing(key: &str, body: &str, plan: &str, done: &str) -> bool {
    if APPROACH.is_match(key).unwrap_or(false) {
        return approach_decides_nothing(body, plan, done);
    }
    if !PART_B.is_match(key).unwrap_or(false) {
        return false;
    }
    let answer = |n: u32| -> String {
        re(&format!(r"(?m)^{n}\.\s+\*\*[^*]*\*\*\s*(.*)$"))
            .captures(body)
            .ok()
            .flatten()
            .map_or(String::new(), |c| c[1].trim().to_lowercase())
    };
    re(r"^no\b").is_match(&answer(4)).unwrap_or(false)
        && re(r"^neither\b").is_match(&answer(5)).unwrap_or(false)
        && decision_ids(body).is_subset(&defined_ids(&format!("{}{done}", plan.replace(body, ""))))
}

fn task_tokens(line: &str) -> Vec<&str> {
    BARE_TASK
        .find_iter(line)
        .flatten()
        .map(|m| m.as_str())
        .collect()
}

/// `body` with its `**Lands open**:` line put back as `earlier` had it, where the only change is ids appended in order (feature 385 T74).
pub(super) fn lands_open_appended(earlier: &str, body: &str) -> String {
    let (Ok(Some(was)), Ok(Some(now))) = (LANDS_OPEN.find(earlier), LANDS_OPEN.find(body)) else {
        return body.to_owned();
    };
    let (a, b) = (task_tokens(was.as_str()), task_tokens(now.as_str()));
    let unique = b.iter().collect::<BTreeSet<_>>().len() == b.len();
    if b.len() < a.len() || b[..a.len()] != a[..] || !unique {
        return body.to_owned();
    }
    format!(
        "{}{}{}",
        &body[..now.start()],
        was.as_str(),
        &body[now.end()..]
    )
}

/// A block's heading without its closing parenthetical and without a repeat's `#2` (feature 444 T20, D4).
pub(super) fn stem(key: &str) -> String {
    let bare = REPEAT.replace(key, "");
    PARENTHETICAL.replace(&bare, "").trim().to_owned()
}

/// A block's text below its heading line, archive lines aside (feature 444 T20, D4).
pub(super) fn below_heading(text: &str) -> String {
    strip_archive(text.split_once('\n').map_or("", |(_, rest)| rest))
        .trim()
        .to_owned()
}

/// Does the task section's Decisions block declare wording only, with no decision beside it (feature 385 T118, D137)?
pub(super) fn wording_only(section: &str) -> bool {
    let Ok(Some(m)) = DECISIONS_BLOCK.find(section) else {
        return false;
    };
    let rest = &section[m.end()..];
    let body = NEXT_HEAD
        .find(rest)
        .ok()
        .flatten()
        .map_or(rest, |n| &rest[..n.start()]);
    body.contains("**Wording only.**") && !DECISION_LINE.is_match(body).unwrap_or(true)
}

/// A heading's text, its `#`s and spaces gone.
pub(super) fn heading_text(key: &str) -> String {
    HEAD.replace_all(key, "$2").trim().to_owned()
}

#[cfg(test)]
mod tests;
