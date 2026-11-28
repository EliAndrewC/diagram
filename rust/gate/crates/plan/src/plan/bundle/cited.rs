//! What a plan review's blocks cite, and where each id's text is found (moved out of `bundle.rs` by 461 T68, which added the reader
//! of a task's own section): the ids named as this feature's, as another feature's or task's, and as another source's.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::{Map, Value};

use super::super::sections::{re, task_sections};
use super::section::{is_task, section_ids_out};
use super::{
    expand_ranges, paragraphs, plans_of, read, requirements, DECISION, IDS, NAMED, QUALIFIED,
};

/// The names whose possessive is the reviewed feature's own (read 2026-11-20 over every `specs/*/plan.md`, `plan-done.md` and
/// `spec.md`: "the spec's", "plan.md's", "the GM's", "the amendment's", "this feature's", "T31's" name the feature's own documents;
/// "house style's" and "the claims gate's" name another's; 250's "every page's FR-002 list" is its own). `feature` is own after any
/// word ("this feature's", "the reviewed feature's"): another feature is named by its number. A name misread as another's costs a NOT FOUND line, never a wrong text.
const OWN_NAMES: [&str; 19] = [
    "spec",
    "spec.md",
    "plan",
    "plan.md",
    "plan-done.md",
    "tasks.md",
    "request",
    "request.md",
    "research.md",
    "gm",
    "amendment",
    "reopening",
    "review",
    "session",
    "task",
    "section",
    "block",
    "page",
    "feature",
];

/// A decision a task section writes for itself, indented or not, its `T<n>-` label optional (`  - **D3. The sampler names itself.**`,
/// `- **T306-D2, ...**`): what a block defines, and what another task's section is read for (461 T68).
pub(super) static SECTION_DECISION: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?m)^[ \t]*(?:#{2,4} |- \*\*|\*\*|- (?=D\d+[a-z]? - ))(?:T\d+[a-z]?-)?(D\d+[a-z]?)(?: - |\*\*|\.|,| |$)",
    )
});
/// The task a qualified run names before it, `451 T274's D3` (461 T68).
static RUN_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"\b(T\d+[a-z]?)'s\s"));

/// The line a cited id stands on when it is not found where it is named.
fn not_found(rid: &str, why: &str) -> String {
    format!("- **{rid}**: NOT FOUND - {why}; the bundle has only the blocks' own words of it.\n")
}

/// `rid`'s text in a feature's directory: a decision from its plans, else its spec (feature 204 keeps its decisions in `spec.md`); a
/// requirement from its spec, else its plans.
fn lookup(dir: &Path, rid: &str) -> Option<String> {
    let (plans, spec) = (plans_of(dir), read(&dir.join("spec.md")));
    let found = |texts: [&str; 2], decision: bool| {
        texts.into_iter().find_map(|t| {
            let map = if decision {
                paragraphs(t, &DECISION)
            } else {
                requirements(t)
            };
            map.get(rid).and_then(Value::as_str).map(str::to_owned)
        })
    };
    if rid.starts_with('D') {
        found([&plans, &spec], true)
    } else {
        found([&spec, &plans], false)
    }
}

/// `rid` as `task`'s section in a feature's directory writes it (plan.md, then plan-done.md and its archive), or the line saying where it
/// is not: never the feature's plan-level decision of that name (461 T68).
fn in_task(dir: &Path, task: &str, rid: &str) -> String {
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    let Some(section) = task_sections(&plans_of(dir)).remove(task) else {
        return not_found(
            rid,
            &format!("specs/{name} has no {task} section in its plan.md or plan-done.md"),
        );
    };
    paragraphs(&section, &SECTION_DECISION)
        .get(rid)
        .and_then(Value::as_str)
        .map_or_else(
            || {
                not_found(
                    rid,
                    &format!("{task}'s section in specs/{name} holds no {rid}"),
                )
            },
            str::to_owned,
        )
}

/// Each (feature, id) another feature's requirement or decision, from that feature's one directory, under a line naming it; one not
/// found there, or a feature with no one directory, is named as not found (451 T46: it was dropped without a word).
fn foreign(spec_dir: &Path, others: &[(String, String)]) -> Vec<String> {
    let parent = spec_dir.parent().unwrap_or(Path::new("."));
    let mut out = Vec::new();
    for (whose, rid) in others {
        // `451 T274`: that task's section of feature 451 (461 T68)
        let (no, task) = whose
            .split_once(' ')
            .map_or((whose.as_str(), None), |(n, t)| (n, Some(t)));
        let prefix = format!("{no}-");
        let hits: Vec<PathBuf> = std::fs::read_dir(parent)
            .into_iter()
            .flatten()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix) && e.path().is_dir())
            .map(|e| e.path())
            .collect();
        let text = match (hits.as_slice(), task) {
            ([], _) => not_found(rid, &format!("feature {no} has no directory under specs/")),
            ([hit], Some(t)) => in_task(hit, t, rid),
            ([hit], None) => lookup(hit, rid).unwrap_or_else(|| {
                let name = hit.file_name().unwrap_or_default().to_string_lossy();
                not_found(
                    rid,
                    &format!("specs/{name} holds no {rid} in its spec.md, plan.md or plan-done.md"),
                )
            }),
            (many, _) => not_found(
                rid,
                &format!("feature {no} has {} directories under specs/", many.len()),
            ),
        };
        out.push(format!("<!-- feature {whose} -->\n{text}"));
    }
    out
}

/// What one block names: its ids named as another feature's `(feature, id)` (by its number before them or in a clause after them, 451
/// T48), as another source's `(its name, id)`, the ids it names as
/// this feature's in so many words, and its text with every other feature's and source's ids taken out (its ranges written out).
pub(super) struct Named {
    others: Vec<(String, String)>,
    sources: Vec<(String, String)>,
    own: BTreeSet<String>,
    pub(super) bare: String,
}

pub(super) fn ids_in(text: &str) -> Vec<String> {
    IDS.captures_iter(text)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect()
}

/// A clause after a run of ids that names another source ("in 451's sections", "of feature 999"): the run's last part is its, not the
/// number's (451 T46 round 2: "449 T233's FR-023 and FR-024, and D5 and D11 in 451's sections" carried 449's D5); a clause naming a
/// feature by its number, group 1, makes that part that feature's (451 T48), one naming a source by another name leaves it bare.
static ANOTHER: LazyLock<Regex> = LazyLock::new(|| {
    re(r"^\s+(?:in|of|from)\s+(?:(?:[Ff]eature\s+)?(\d{3})\b|(?:the\s+)?[A-Za-z][\w.-]*'s)")
});

/// The feature a clause after a run of ids names by its number ("of feature 134", "in 451's sections"; 451 T48), if it names one.
fn clause_feature(after: &str) -> Option<&str> {
    ANOTHER
        .captures(after)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str())
}

impl Named {
    /// The ids in `text` read as feature `no`'s: this feature's kept in the text, to be carried; another's taken out of it. A decision
    /// a `task` names is that task's section's, whichever feature's, so it is taken out as another's under `<no> <task>` (461 T68).
    fn claim(&mut self, no: &str, own_no: &str, task: Option<&str>, text: &str) -> String {
        let (tasked, ids): (Vec<String>, Vec<String>) = ids_in(text)
            .into_iter()
            .partition(|i| task.is_some() && i.starts_with('D'));
        if let Some(t) = task.filter(|_| !tasked.is_empty()) {
            self.others
                .extend(tasked.into_iter().map(|i| (format!("{no} {t}"), i)));
            return self.claim(no, own_no, None, &ids.join(", "));
        }
        if no == own_no {
            self.own.extend(ids);
            text.to_owned()
        } else {
            self.others
                .extend(ids.into_iter().map(|i| (no.to_owned(), i)));
            String::new()
        }
    }
}

/// (the part of a run of ids its number names, the rest, left to be read as written): the whole run, unless the text after it opens a
/// clause naming another source - then the run stops at its last comma, or before its last id when it has no comma.
fn own_run<'a>(run: &'a str, after: &str) -> (&'a str, &'a str) {
    if !ANOTHER.is_match(after).unwrap_or(false) {
        return (run, "");
    }
    let cut = run.rfind(',').or_else(|| {
        IDS.find_iter(run)
            .map_while(Result::ok)
            .last()
            .map(|m| m.start())
            .filter(|&s| s > 0)
    });
    cut.map_or((run, ""), |at| (&run[..at], &run[at..]))
}

/// What `body` names; `owners` the labeled task sections it stands in (`labeled_owners`), where a bare decision is the section's own.
pub(super) fn named(body: &str, own_no: &str, owners: &[String]) -> Named {
    let mut n = Named {
        others: Vec::new(),
        sources: Vec::new(),
        own: BTreeSet::new(),
        bare: String::new(),
    };
    let expanded = expand_ranges(body);
    let expanded = if owners.is_empty() {
        expanded
    } else {
        section_ids_out(&expanded)
    };
    let numbered = QUALIFIED.replace_all(&expanded, |c: &Captures<'_>| {
        let after = &expanded[c.get(0).map_or(0, |g| g.end())..];
        let clause = clause_feature(after);
        if let Some(run) = c.get(3) {
            return n.claim(clause.unwrap_or(own_no), own_no, None, run.as_str());
        }
        // the number's part of the run is its; the part a clause naming a feature takes, that feature's (451 T48); a clause naming the
        // run's own number cuts nothing, so a task the run names keeps all of it ("451 T274's D3, D13 and D5 from 451's plan-done.md", 461 T68)
        let (run, left) = if clause == Some(&c[1]) {
            (&c[2], "")
        } else {
            own_run(&c[2], after)
        };
        let left = clause.map_or_else(|| left.to_owned(), |no| n.claim(no, own_no, None, left));
        let (whole, run_at) = (
            c.get(0).map_or(0, |g| g.start()),
            c.get(2).map_or(0, |g| g.start()),
        );
        let task = RUN_TASK
            .captures(&expanded[whole..run_at])
            .ok()
            .flatten()
            .and_then(|t| t.get(1))
            .map(|t| t.as_str().to_owned());
        n.claim(&c[1], own_no, task.as_deref(), run) + &left
    });
    n.bare = NAMED
        .replace_all(&numbered, |c: &Captures<'_>| {
            let before = c.get(1).map_or("", |g| g.as_str());
            let word = c[2].to_lowercase();
            if is_task(&word) {
                // a task's decision is its section's in this feature's plans, its requirement the spec's (461 T68)
                return n.claim(own_no, own_no, Some(&c[2]), &c[3]);
            }
            let is_own = OWN_NAMES.contains(&word.as_str()) || IDS.is_match(&c[2]).unwrap_or(false);
            let ids = ids_in(&c[3]);
            if is_own {
                n.own.extend(ids);
                return c[0].to_owned();
            }
            let article =
                ["the", "this", "a", "an", "our"].contains(&before.to_lowercase().as_str());
            let name = if before.is_empty() || article {
                c[2].to_owned()
            } else {
                format!("{before} {}", &c[2])
            };
            n.sources.extend(ids.into_iter().map(|i| (name.clone(), i)));
            String::new()
        })
        .into_owned();
    n
}

/// The text of each requirement and decision the blocks cite, and the ids cited bare (another feature's are taken from that feature).
/// An id named with another feature's number or name, or in a clause naming another feature ("FR-010 of feature 134", 451 T48), is
/// never carried from this one; a bare mention of an id the blocks also name as
/// another's carries this feature's text under a line saying it may mean either (451 T46: T42's bare "D5's form" was feature 204's,
/// 417 T37's bare "FR-013 (speed first)" beside "(385 FR-013)" its own), so nothing is withheld and nothing arrives unmarked.
pub(super) fn cited_text(
    spec_dir: &Path,
    feature: &str,
    under: &[(String, String)],
    owners: &[(Vec<String>, BTreeSet<String>)],
    items: &Map<String, Value>,
    decisions: &Map<String, Value>,
) -> (Vec<String>, Vec<String>) {
    let own_no: String = feature.chars().take(3).collect();
    let mut others: Vec<(String, String)> = Vec::new();
    let mut sources: Vec<(String, String)> = Vec::new();
    let mut said_own: BTreeSet<String> = BTreeSet::new();
    let mut cited: Vec<String> = Vec::new();
    let mut defined: BTreeSet<String> = BTreeSet::new();
    for ((_, body), (owned, own_defined)) in under.iter().zip(owners) {
        let n = named(body, &own_no, owned);
        for pair in n.others {
            if !others.contains(&pair) {
                others.push(pair);
            }
        }
        for pair in n.sources {
            if !sources.contains(&pair) {
                sources.push(pair);
            }
        }
        said_own.extend(n.own);
        for id in ids_in(&n.bare) {
            if !cited.contains(&id) && !own_defined.contains(&id) {
                cited.push(id);
            }
        }
        defined.extend(
            SECTION_DECISION
                .captures_iter(body)
                .map_while(Result::ok)
                .map(|c| c[1].to_owned()),
        );
    }
    let elsewhere = |id: &str| -> Vec<String> {
        let numbered = others
            .iter()
            .filter(|(_, i)| i == id)
            .map(|(no, _)| format!("feature {no}'s"));
        let by_name = sources
            .iter()
            .filter(|(_, i)| i == id)
            .map(|(name, _)| format!("{name}'s"));
        numbered.chain(by_name).collect()
    };
    let text_at =
        |map: &Map<String, Value>, id: &str| map.get(id).and_then(Value::as_str).map(str::to_owned);
    let mut parts: Vec<String> = cited
        .iter()
        .filter(|i| !defined.contains(*i))
        .map(|i| {
            // a bare id found nowhere is named so, never dropped without a word (461 T68)
            let Some(text) = text_at(items, i)
                .filter(|t| !t.is_empty())
                .or_else(|| text_at(decisions, i))
            else {
                return not_found(i, &format!("feature {own_no}'s spec.md, plan.md and plan-done.md hold no {i}"));
            };
            let named = elsewhere(i);
            if named.is_empty() || said_own.contains(i) {
                return text;
            }
            format!("<!-- feature {own_no}'s {i}, cited bare; the blocks also name {} {i}, so a bare {i} may mean either -->\n{text}", named.join(" and "))
        })
        .collect();
    parts.extend(foreign(spec_dir, &others));
    parts.extend(sources.iter().map(|(name, rid)| {
        format!(
            "<!-- {name} -->\n{}",
            not_found(rid, &format!("named as {name}'s, not feature {own_no}'s, with no feature number to find it by, so nothing is carried and never this feature's {rid}"))
        )
    }));
    (parts, cited)
}

#[cfg(test)]
mod tests;
