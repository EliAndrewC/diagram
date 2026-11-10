//! A plan read for its sections (moved from `rust/gate/src/plan/sections.rs` by feature 449 T86, so the guards' plan hold reads them in-process): each task's section and each block.

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A heading, its level and its title.
pub static HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(#{2,4})\s+(.*)$"));
pub static TASK_ID: LazyLock<Regex> = LazyLock::new(|| re(r"\b(T\d+[a-z]?)\b"));
static ANY_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s.*$"));

/// `{task id: its section}`: every heading naming a task id, to the next heading at its level or above (feature 375 FR-003(a)). A
/// title that begins with the id is that task's own (feature 385 T56), and every one of its own headings counts (405 T26).
#[must_use]
pub fn task_sections(plan: &str) -> BTreeMap<String, String> {
    ordered_sections(plan).into_iter().collect()
}

/// The sections in the order a reader meets their ids: those a heading only mentions, then each task's own (`archive` moves them so).
#[must_use]
pub fn ordered_sections(plan: &str) -> Vec<(String, String)> {
    let heads: Vec<(usize, usize, &str)> = HEAD
        .captures_iter(plan)
        .flatten()
        .map(|c| {
            let at = c.get(0).map_or(0, |g| g.start());
            (
                at,
                c.get(1).map_or(0, |g| g.as_str().len()),
                c.get(2).map_or("", |g| g.as_str()),
            )
        })
        .collect();
    let mut own: Vec<(String, Vec<(usize, usize)>)> = Vec::new();
    let mut mentioned: Vec<(String, String)> = Vec::new();
    for (i, (at, level, title)) in heads.iter().enumerate() {
        let ids: Vec<&str> = TASK_ID
            .find_iter(title)
            .flatten()
            .map(|m| m.as_str())
            .collect();
        let end = heads[i + 1..]
            .iter()
            .find(|(_, lv, _)| lv <= level)
            .map_or(plan.len(), |(a, ..)| *a);
        let lead = leading_task(title.trim());
        for t in ids {
            if lead == Some(t) {
                let at_own = own.iter().position(|(k, _)| k == t).unwrap_or_else(|| {
                    own.push((t.to_owned(), Vec::new()));
                    own.len() - 1
                });
                let spans = &mut own[at_own].1;
                if !spans.iter().any(|(a, b)| a <= at && end <= *b) {
                    spans.push((*at, end));
                }
            } else if !mentioned.iter().any(|(k, _)| k == t) {
                mentioned.push((t.to_owned(), plan[*at..end].to_owned()));
            }
        }
    }
    for (t, spans) in own {
        let joined: String = spans.iter().map(|(a, b)| &plan[*a..*b]).collect();
        match mentioned.iter_mut().find(|(k, _)| *k == t) {
            Some(slot) => slot.1 = joined,
            None => mentioned.push((t, joined)),
        }
    }
    mentioned
}

/// The task id a title opens with, if it opens with one.
#[must_use]
pub fn leading_task(title: &str) -> Option<&str> {
    TASK_ID
        .find(title)
        .ok()
        .flatten()
        .filter(|m| m.start() == 0)
        .map(|m| m.as_str())
}

/// (key, text, offset) of every block (D60, FR-043): each heading line to the next heading, and the text before the first as `preamble`.
#[must_use]
pub fn blocks(plan: &str) -> Vec<(String, String, usize)> {
    let heads: Vec<(usize, &str)> = ANY_HEAD
        .find_iter(plan)
        .flatten()
        .map(|m| (m.start(), m.as_str()))
        .collect();
    let first = heads.first().map_or(plan.len(), |(a, _)| *a);
    let mut out = vec![("preamble".to_owned(), plan[..first].to_owned(), 0)];
    let mut seen: BTreeMap<&str, usize> = BTreeMap::new();
    for (i, (at, line)) in heads.iter().enumerate() {
        let end = heads.get(i + 1).map_or(plan.len(), |(a, _)| *a);
        let key = line.trim();
        let count = seen.entry(key).or_default();
        *count += 1;
        let shown = if *count == 1 {
            key.to_owned()
        } else {
            format!("{key}#{count}")
        };
        out.push((shown, plan[*at..end].to_owned(), *at));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{blocks, leading_task, ordered_sections, task_sections};

    #[test]
    fn a_plan_reads_as_its_sections_and_blocks() {
        let plan = "# plan\n\n## T01 the bath\n\nbody\n\n### T01 notes\n\nmore\n\n## About T02 and T03\n\nx\n\n## T02 the well\n\ny\n\n## T01 again\n\nz\n\n## T03\n\n## T03\n";
        let sections = task_sections(plan);
        assert!(sections["T01"].contains("the bath"));
        assert!(sections["T01"].contains("### T01 notes") && sections["T01"].contains("T01 again"));
        assert_eq!(sections["T02"], "## T02 the well\n\ny\n\n");
        assert!(sections["T03"].starts_with("## T03"));
        assert_eq!(ordered_sections(plan).len(), 3);
        assert_eq!(leading_task(" T5a stuff".trim()), Some("T5a"));
        assert_eq!(leading_task("the T5"), None);
        let b = blocks(plan);
        assert_eq!((b[0].0.as_str(), b[0].2), ("preamble", 0));
        assert_eq!(b[1].0, "## T01 the bath");
        let keys: Vec<&str> = b.iter().map(|x| x.0.as_str()).collect();
        assert!(keys.contains(&"## T03") && keys.contains(&"## T03#2"));
        assert_eq!(blocks("no heads")[0].1, "no heads");
    }
}
