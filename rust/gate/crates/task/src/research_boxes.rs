//! A ticked `research: physical` task carries its research boxes ticked (constitution v2.12.0, GM 2026-08-27) - the port of
//! `tests/test_task_research_boxes.py` by feature 449 T131, with the tick whose box rule it checks (FR-001b: a kept test goes with the
//! piece it tests).
//!
//! THE REQUIREMENT IS A SHAPE, NOT A MEMORY. *"anytime we have a documented requirement that requires that we remember to do something,
//! then there is always a chance that it will be skipped."* So every spec-kit task says `research: rendering | physical | procedure`, and a
//! `physical` task - one about how a place was built, farmed, planted, bounded or lived in - carries `research pass`, `source-reader
//! confirmed`, `recorded and cited`; from feature 194 a fourth, `quote-check confirmed` (GM 2026-09-06, "quote what you cite"); from 211
//! a fifth, `source-applicability confirmed` (GM 2026-09-07). This reads every `specs/*/tasks.md` and fails when a task marked `[x]` and
//! `research: physical` has a box unticked or missing. Entries without a `research:` line are older than the rule and are not judged; the
//! rule binds from the day it was made, and each later box from its own feature, older task files being history.

use std::path::{Path, PathBuf};

use crate::tick::text::re;

const BOXES: [&str; 3] = [
    "research pass",
    "source-reader confirmed",
    "recorded and cited",
];
const QUOTE_BOX: &str = "quote-check confirmed";
const QUOTE_BOX_FROM: u32 = 194;
const APPLICABILITY_BOX: &str = "source-applicability confirmed";
const APPLICABILITY_BOX_FROM: u32 = 211;

/// `(task id, ticked, the entry's body up to the next task or heading)`.
fn entries(text: &str) -> Vec<(String, bool, String)> {
    let task = re(r"(?m)^- \[(?P<tick>[ x])\] (?P<id>T\d+)\b");
    let head = re(r"(?m)^## ");
    let starts: Vec<_> = task.captures_iter(text).flatten().collect();
    let mut out = Vec::new();
    for (k, m) in starts.iter().enumerate() {
        let at = m.get(0).map_or(0, |g| g.start());
        let end = starts
            .get(k + 1)
            .and_then(|n| n.get(0))
            .map_or(text.len(), |g| g.start());
        let mut body = &text[at..end];
        if let Some(h) = head.find(&body[1..]).ok().flatten() {
            body = &body[..=h.start()];
        }
        out.push((
            m.name("id").map_or("", |g| g.as_str()).to_owned(),
            m.name("tick").is_some_and(|g| g.as_str() == "x"),
            body.to_owned(),
        ));
    }
    out
}

/// Every ticked `research: physical` task whose boxes are not all ticked - three, four from feature 194, five from 211.
/// Each named after `at` (the file, in the test over the tree).
fn violations(text: &str, feature: u32, at: &str) -> Vec<String> {
    let kind = re(r"(?m)^\s+research:\s*(\w+)");
    let mut boxes: Vec<&str> = BOXES.to_vec();
    if feature >= QUOTE_BOX_FROM {
        boxes.push(QUOTE_BOX);
    }
    if feature >= APPLICABILITY_BOX_FROM {
        boxes.push(APPLICABILITY_BOX);
    }
    let mut bad = Vec::new();
    for (id, ticked, body) in entries(text) {
        let physical = kind
            .captures(&body)
            .ok()
            .flatten()
            .and_then(|c| c.get(1))
            .is_some_and(|g| g.as_str() == "physical");
        if !physical || !ticked {
            continue;
        }
        for b in &boxes {
            if !body.contains(&format!("- [x] {b}")) {
                bad.push(format!("{at}{id}: `{b}` not ticked"));
            }
        }
    }
    bad
}

fn top() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..")
}

#[test]
fn every_ticked_physical_task_has_its_research_boxes_ticked() {
    let specs = top().join("specs");
    let mut files: Vec<PathBuf> = std::fs::read_dir(&specs)
        .unwrap()
        .flatten()
        .map(|e| e.path().join("tasks.md"))
        .filter(|p| p.is_file())
        .collect();
    files.sort();
    // no specs/*/tasks.md found: the repo root resolved wrong
    assert!(!files.is_empty());
    let mut bad = Vec::new();
    for f in &files {
        let dir = f
            .parent()
            .unwrap()
            .file_name()
            .unwrap()
            .to_string_lossy()
            .into_owned();
        let n: u32 = dir.split('-').next().unwrap().parse().unwrap();
        bad.extend(violations(
            &std::fs::read_to_string(f).unwrap(),
            n,
            &format!("specs/{dir}/tasks.md "),
        ));
    }
    // a ticked physical task owes its research boxes (constitution v2.12.0): each named in the failure
    assert_eq!(bad, Vec::<String>::new());
}

#[test]
fn the_rule_fires_on_a_ticked_physical_task_with_an_open_box() {
    let text = "- [x] T01 **x**\n      research: physical\n      - [x] research pass  - [ ] source-reader confirmed  - [x] recorded and cited\n";
    assert_eq!(
        violations(text, 0, ""),
        vec!["T01: `source-reader confirmed` not ticked"]
    );
    assert!(violations(&text.replace("[ ] source", "[x] source"), 0, "").is_empty());
    // an OPEN task may still owe its boxes
    assert!(violations(&text.replace("- [x] T01", "- [ ] T01"), 0, "").is_empty());
    let rendering = text.replace("physical", "rendering").replace(
        "- [x] research pass  - [ ] source-reader confirmed  - [x] recorded and cited",
        "",
    );
    assert!(violations(&rendering, 0, "").is_empty());
    // a heading ends the entry: a box below it is not the task's
    let headed = "- [x] T01 **x**\n      research: physical\n## Next\n      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited\n";
    assert_eq!(violations(headed, 0, "").len(), 3);
}

#[test]
fn the_fourth_and_fifth_boxes_bind_from_their_features() {
    let four = "- [x] T01 **x**\n      research: physical\n      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed\n";
    assert!(violations(four, 210, "").is_empty());
    assert_eq!(
        violations(four, 211, ""),
        vec!["T01: `source-applicability confirmed` not ticked"]
    );
    assert!(violations(
        &format!("{four}      - [x] source-applicability confirmed\n"),
        211,
        ""
    )
    .is_empty());
    assert!(violations(&four.replace("  - [x] quote-check confirmed", ""), 193, "").is_empty());
}
