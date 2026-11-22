//! A plan read for its sections (moved from `rust/gate/src/plan/sections.rs` by feature 449 T86, so the guards' plan hold reads them in-process): each task's section and each block.

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
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
    section_spans(plan)
        .into_iter()
        .map(|(t, spans)| (t, spans.iter().map(|(a, b)| &plan[*a..*b]).collect()))
        .collect()
}

/// The places a task's section stands in `plan`, as byte spans in document order: its spans with adjacent ones joined, so one place
/// for a section that stands whole and one a run for a section whose own headings stand apart (451 T80: the plan hold's write-back
/// restores each place; the joined section stands nowhere in the plan).
#[must_use]
pub fn section_places(plan: &str, task: &str) -> Vec<(usize, usize)> {
    let spans = section_spans(plan)
        .into_iter()
        .find(|(t, _)| t == task)
        .map(|(_, s)| s)
        .unwrap_or_default();
    let mut places: Vec<(usize, usize)> = Vec::new();
    for (a, b) in spans {
        match places.last_mut() {
            Some(last) if last.1 == a => last.1 = b,
            _ => places.push((a, b)),
        }
    }
    places
}

/// [`ordered_sections`] as byte spans: a mentioned task's one heading, or each of a task's own headings not inside another.
fn section_spans(plan: &str) -> Vec<(String, Vec<(usize, usize)>)> {
    let heads: Vec<(usize, usize, &str)> = HEAD
        .captures_iter(plan)
        .map_while(Result::ok)
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
    let mut mentioned: Vec<(String, Vec<(usize, usize)>)> = Vec::new();
    for (i, (at, level, title)) in heads.iter().enumerate() {
        let ids: Vec<&str> = TASK_ID
            .find_iter(title)
            .map_while(Result::ok)
            .map(|m| m.as_str())
            .collect();
        let end = heads[i + 1..]
            .iter()
            .find(|(_, lv, _)| lv <= level)
            .map_or(plan.len(), |(a, ..)| *a);
        let own_of = leading_tasks(title.trim());
        for t in ids {
            if own_of.contains(&t) {
                let at_own = own.iter().position(|(k, _)| k == t).unwrap_or_else(|| {
                    own.push((t.to_owned(), Vec::new()));
                    own.len() - 1
                });
                let spans = &mut own[at_own].1;
                if !spans.iter().any(|(a, b)| a <= at && end <= *b) {
                    spans.push((*at, end));
                }
            } else if !mentioned.iter().any(|(k, _)| k == t) {
                mentioned.push((t.to_owned(), vec![(*at, end)]));
            }
        }
    }
    for (t, spans) in own {
        match mentioned.iter_mut().find(|(k, _)| *k == t) {
            Some(slot) => slot.1 = spans,
            None => mentioned.push((t, spans)),
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

/// A bundle's heading (451 T141): a list of task ids, then its marker - `(bundle)`, or the Approach, part B or performance checklist
/// headings the section's template writes. A list followed by anything else (feature 405's `## T17, T16, T27 - ...`) is not one.
static BUNDLE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^(T\d+[a-z]?(?:,\s*T\d+[a-z]?)+)\s+(?:\(bundle\)|Approach\b|part B\b|Performance checklist\b)",
    )
});

/// The tasks whose own heading `title` is: a bundle's every listed id (451 T141), else the id it opens with, else none.
#[must_use]
pub fn leading_tasks(title: &str) -> Vec<&str> {
    let listed = BUNDLE
        .captures(title)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str());
    match listed {
        Some(list) => list.split(',').map(str::trim).collect(),
        None => leading_task(title).into_iter().collect(),
    }
}

/// (key, text, offset) of every block (D60, FR-043): each heading line to the next heading, and the text before the first as `preamble`.
#[must_use]
pub fn blocks(plan: &str) -> Vec<(String, String, usize)> {
    let heads: Vec<(usize, &str)> = ANY_HEAD
        .find_iter(plan)
        .map_while(Result::ok)
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
    use super::{
        blocks, leading_task, leading_tasks, ordered_sections, section_places, task_sections,
    };

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

    /// A task's section as the places it stands (451 T80): one place where its headings stand together, one a run where they stand
    /// apart, the mentioning heading for a task with no own heading, none for a task the plan does not name.
    #[test]
    fn a_section_reads_as_the_places_it_stands() {
        let plan = "# plan\n\n## T01 the bath\n\nbody\n\n### T01 Approach\n\nmore\n\n## About T02\n\nx\n\n## T03 the well\n\ny\n\n## T01 part B\n\nz\n";
        let at = |s: &str| plan.find(s).unwrap();
        let split = section_places(plan, "T01");
        let want = vec![
            (at("## T01 the bath"), at("## About")),
            (at("## T01 part B"), plan.len()),
        ];
        assert_eq!(split, want);
        let joined: String = split.iter().map(|(a, b)| &plan[*a..*b]).collect();
        let section = task_sections(plan)["T01"].clone();
        assert_eq!(joined, section);
        let whole = section_places(plan, "T03");
        let one = vec![(at("## T03"), at("## T01 part B"))];
        assert_eq!(whole, one);
        let mention = section_places(plan, "T02");
        let heading = vec![(at("## About T02"), at("## T03"))];
        assert_eq!(mention, heading);
        let none = section_places(plan, "T09");
        assert!(none.is_empty());
    }

    /// A bundle's headings (451 T141): `### Ta, Tb, Tc (bundle)` and its Approach, owned by every task they list, so each reads the one
    /// section byte for byte; a list heading without the marker (feature 405's `## T17, T16, T27 - ...`) stays its first task's own.
    #[test]
    fn a_bundle_heading_is_each_listed_task_s_own() {
        let plan = "# plan\n\n### T05, T06, T07 (bundle)\n\nthe table\n\n### T05, T06, T07 Approach (checklist part A)\n\n1. x\n\n### T08 the next\n\ny\n";
        let sections = task_sections(plan);
        let want = plan[plan.find("### T05").unwrap()..plan.find("### T08").unwrap()].to_owned();
        assert_eq!(sections["T05"], want);
        assert_eq!(sections["T06"], want);
        assert_eq!(sections["T07"], want);
        let members = leading_tasks("T05, T06, T07 (bundle)");
        assert_eq!(members, ["T05", "T06", "T07"]);
        let approach = leading_tasks("T05, T06 Approach (checklist part A)");
        assert_eq!(approach, ["T05", "T06"]);
        let old = "# plan\n\n## T17, T16, T27 - three claims\n\nx\n\n## T16 its own\n\ny\n";
        let old_sections = task_sections(old);
        assert_eq!(old_sections["T16"], "## T16 its own\n\ny\n");
        assert!(old_sections["T17"].starts_with("## T17, T16"));
        let not = leading_tasks("T17, T16, T27 - three claims");
        assert_eq!(not, ["T17"]);
        let none = leading_tasks("the T5");
        assert!(none.is_empty());
    }
}
