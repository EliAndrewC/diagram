//! A task section's own decisions in the plan review's bundle (451 T438, found by the round-2 plan reviewer of 451 T369, 2026-11-27):
//! in a task section that writes its own decisions `T369-D1`, a bare `D1` is the section's, not the spec's, so the bundle carries no
//! spec text for it; the spec's are cited there as `spec D5`, `plan D5`, `the plan's D6` or `451 D7`.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use super::super::sections::{leading_tasks, re, task_sections};
use super::{named, read, ID, NAMED, QUALIFIED, RUN_ON};

/// A heading line of a block, its title group 1: the task a block stands in is the one its heading leads with (451 T438).
static BLOCK_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4}\s+(.*)$"));
/// A bare decision id, which `section_ids_out` takes out of a labeled task section's text (451 T438).
static BARE_DECISION: LazyLock<Regex> = LazyLock::new(|| re(r"\bD\d+[a-z]?\b"));
/// A run of decisions named as the spec's in so many words, `spec D5`, `plan D5, D6`, `plan.md D7` (451 T438): kept in a labeled task
/// section, where a bare one is the section's own.
static SPEC_RUN: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?<![\w.-])(?:spec|plan)(?:\.md)?\s+{ID}\b{RUN_ON}"
    ))
});
/// The possessives that name a task section's own decisions, not the spec's (451 T438): "the section's D4" in a labeled section.
const SECTION_NAMES: [&str; 3] = ["section", "task", "block"];

/// The tasks a block stands in the section of whose decisions are written `T<n>-D<k>` (451 T438): each task a heading of `body`
/// leads with (`leading_tasks`: a bundle's heading names several), where the block itself or that task's section in `sections` (the
/// plan's) holds such a label. Empty for a block of no task's section and for a section labeling none - an older feature's task
/// section, which defines and cites the plan's own decisions bare (measured 2026-11-27 over every `specs/*/plan.md`: 429 bare ids
/// in unlabeled task sections, 44 in labeled ones, every one of those 44 the section's own or another section's).
pub(super) fn labeled_owners(sections: &BTreeMap<String, String>, body: &str) -> Vec<String> {
    let mut owners: Vec<String> = Vec::new();
    for head in BLOCK_HEAD.captures_iter(body).map_while(Result::ok) {
        for task in leading_tasks(head[1].trim()) {
            let label = format!("{task}-D");
            let labeled = |text: &str| {
                text.match_indices(&label).any(|(at, _)| {
                    text[at + label.len()..].starts_with(|c: char| c.is_ascii_digit())
                        && !text[..at].ends_with(|c: char| c.is_ascii_alphanumeric())
                })
            };
            if !owners.iter().any(|o| o == task)
                && (labeled(body) || sections.get(task).is_some_and(|s| labeled(s)))
            {
                owners.push(task.to_owned());
            }
        }
    }
    owners
}

/// Each block of `under`: the labeled task sections it stands in, by the feature's plan.md (`labeled_owners`, 451 T438), and the
/// decisions its task sections write for themselves there (`pattern`, the bundle's `SECTION_DECISION`): a bare one is its section's
/// own wherever in the section the block stands, an Approach block's D1 its section's other block's (461 T68).
pub(super) fn owners_of(
    spec_dir: &Path,
    under: &[(String, String)],
    pattern: &Regex,
) -> Vec<(Vec<String>, BTreeSet<String>)> {
    let sections = task_sections(&read(&spec_dir.join("plan.md")));
    under
        .iter()
        .map(|(_, body)| {
            let mut defined = BTreeSet::new();
            for head in BLOCK_HEAD.captures_iter(body).map_while(Result::ok) {
                for task in leading_tasks(head[1].trim()) {
                    let section = sections.get(task).map_or("", String::as_str);
                    defined.extend(
                        pattern
                            .captures_iter(section)
                            .map_while(Result::ok)
                            .map(|c| c[1].to_owned()),
                    );
                }
            }
            (labeled_owners(&sections, body), defined)
        })
        .collect()
}

/// Each block of `under` with its text as this feature's ids read it, the amendment it answers read from those alone: "449 FR-023"
/// answers none of 451's (451 T46), nor a labeled section's bare D1 the spec's (451 T438).
pub(super) fn ours(
    feature: &str,
    under: &[(String, String)],
    owners: &[(Vec<String>, BTreeSet<String>)],
) -> Vec<(String, String)> {
    let own_no: String = feature.chars().take(3).collect();
    under
        .iter()
        .zip(owners)
        .map(|((k, b), (owned, _))| (k.clone(), named(b, &own_no, owned).bare))
        .collect()
}

/// A task's name, `t295` or `t12a` lowercased (`named`'s possessive rule reads it too): its possessive decision in a labeled section
/// is that task's own, `T295's D3` its `T295-D3`, never the spec's (451 T467: 451 T306's section wrote "T295's D3 limit", and its
/// bundle carried the spec's D3).
pub(super) fn is_task(word: &str) -> bool {
    let digits = word.strip_prefix('t').unwrap_or("");
    let digits = digits
        .strip_suffix(|c: char| c.is_ascii_lowercase())
        .unwrap_or(digits);
    !digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit())
}

/// `text` (its ranges written out) with each bare decision id taken out, for a block of a labeled task section (`labeled_owners`
/// names it) that writes its own decisions `T369-D1` (451 T438: T369's "(D1)" and "(D3)" were its own T369-D1 and T369-D3, and the bundle carried the spec's).
/// Kept, to be read as before: a run named as the spec's (`spec D5`, `plan D5, D6`), one a feature number names (`451 D7`, which
/// `QUALIFIED` reads, with a task's possessive too, `451 T183's D10`, read from that task's section, 461 T68), and one a possessive names (`the plan's D6`, `house style's D11`) - except the section's own possessives,
/// `the section's D4` and the owner's `T369's D1`, and another task's, `T295's D3`, that task's own decision (451 T467), left out
/// as the section's are: its text is that task's section's, not the spec's. A requirement (`FR-`, `SC-`) is always the spec's and never taken out.
pub(super) fn section_ids_out(text: &str) -> String {
    let spans = |pattern: &Regex| -> Vec<(usize, usize)> {
        pattern
            .find_iter(text)
            .map_while(Result::ok)
            .map(|m| (m.start(), m.end()))
            .collect()
    };
    let mut kept = spans(&SPEC_RUN);
    // a feature's number before a task's possessive, `451 T183's D10`, names that task's own decision, which the bundle now reads from
    // that task's section (461 T68; 451 T467 left it out, there being no reader of a task's section then)
    kept.extend(spans(&QUALIFIED));
    kept.extend(
        NAMED
            .captures_iter(text)
            .map_while(Result::ok)
            .filter(|c| {
                let word = c[2].to_lowercase();
                !SECTION_NAMES.contains(&word.as_str())
            })
            .filter_map(|c| c.get(0).map(|m| (m.start(), m.end()))),
    );
    BARE_DECISION
        .replace_all(text, |c: &Captures<'_>| {
            let at = c.get(0).map_or(0, |m| m.start());
            if kept.iter().any(|&(a, b)| a <= at && at < b) {
                c[0].to_owned()
            } else {
                String::new()
            }
        })
        .into_owned()
}

#[cfg(test)]
mod tests;
