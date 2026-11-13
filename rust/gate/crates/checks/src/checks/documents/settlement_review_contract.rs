//! The settlement-review agent's first stage and verdict record, found in its own file (feature 240, SC-006) - the port of
//! `tests/test_settlement_review_contract.py` by feature 449 T133, `ask:449-phase3-remainder` Q3.
//!
//! An agent file is prose, so what a test can prove is that the contract is WRITTEN where the agent reads it, in the order it must run,
//! and that every command it names exists. Whether an agent obeys is the hook's half and the verdict writer's (`make review-verdict`
//! re-reads the gate itself) - D2: each layer the other's backstop. Feature 294 split the old settlement-review into three checks that
//! each write a verdict record: settlement-review, fix-check and glyph-check.

use std::path::Path;

use super::{re, read, root};

const CHECKS: [&str; 3] = ["settlement-review", "fix-check", "glyph-check"];
/// The files the Python test read on import, `perf-audit.md` among them: one gone failed every test.
const READ: [&str; 5] = [
    ".claude/agents/settlement-review.md",
    ".claude/agents/fix-check.md",
    ".claude/agents/glyph-check.md",
    ".claude/agents/perf-audit.md",
    "Makefile",
];

/// The `## <heading>` section of `text`, to the next `## ` heading.
fn section<'t>(heading: &str, text: &'t str) -> Option<&'t str> {
    let m = re(&format!(
        r"(?sm)^## {}.*?(?=^## )",
        fancy_regex::escape(heading)
    ))
    .find(text)
    .ok()??;
    Some(m.as_str())
}

fn absent(name: &str, heading: &str) -> String {
    format!("{name}.md has no '## {heading}' section followed by another - restore the section")
}

/// The texts by name, and a problem for each file that is gone.
fn load(root: &Path) -> (Vec<(String, String)>, Vec<String>) {
    let mut texts = Vec::new();
    let mut bad = Vec::new();
    for path in READ {
        let full = root.join(path);
        if full.is_file() {
            let name = path
                .trim_start_matches(".claude/agents/")
                .trim_end_matches(".md");
            texts.push((name.to_owned(), read(&full)));
        } else {
            bad.push(format!(
                "{path} is gone - the review contract lives there; restore it"
            ));
        }
    }
    (texts, bad)
}

fn text<'a>(texts: &'a [(String, String)], name: &str) -> &'a str {
    texts
        .iter()
        .find(|(n, _)| n == name)
        .map_or("", |(_, t)| t.as_str())
}

fn first_stage_first(texts: &[(String, String)]) -> Vec<String> {
    let mut bad = Vec::new();
    for name in CHECKS {
        let t = text(texts, name);
        let (Some(first), Some(output)) = (t.find("## First stage"), t.find("## Output")) else {
            bad.push(format!(
                "{name}.md needs both '## First stage' and '## Output' - restore them"
            ));
            continue;
        };
        if first > output || t.find("## Inputs").is_some_and(|inputs| first > inputs) {
            bad.push(format!("{name}.md: '## First stage' must come before '## Inputs' and '## Output' - move it up, so it runs before any map is read"));
        }
    }
    bad
}

/// Feature 294 dispatches a check only on a GREEN gate (US6), so the stage reads it once and again before the verdict.
fn paired_gate(texts: &[(String, String)]) -> Vec<String> {
    let mut bad = Vec::new();
    for name in CHECKS {
        let Some(stage) = section("First stage", text(texts, name)) else {
            bad.push(absent(name, "First stage"));
            continue;
        };
        for needle in [
            "make review-paired-gate",
            "`green`",
            "NOT-REVIEWABLE",
            "immediately before",
        ] {
            if !stage.contains(needle) {
                bad.push(format!("{name}.md's First stage lost `{needle}` - it reads the paired gate (`make review-paired-gate`), proceeds only on `green`, else answers NOT-REVIEWABLE, and reads it again immediately before the verdict"));
            }
        }
    }
    bad
}

/// Feature 240's worked example moved with the question it answers: did a fix's record read the thing complained of.
fn canopy_example(texts: &[(String, String)]) -> Vec<String> {
    let Some(judged) = section("What you judge", text(texts, "fix-check")) else {
        return vec![absent("fix-check", "What you judge")];
    };
    ["proxy", "`source`", "CROWNS", "16.3 ft", "R2"]
        .iter()
        .filter(|t| !judged.contains(**t))
        .map(|t| format!("fix-check.md's What you judge lost `{t}` of the canopy's worked example (feature 240) - put it back"))
        .collect()
}

fn measures_independently(texts: &[(String, String)]) -> Vec<String> {
    match section("First stage", text(texts, "settlement-review")) {
        None => vec![absent("settlement-review", "First stage")],
        Some(s) if !s.contains("right to measure independently") => {
            vec!["settlement-review.md's First stage lost the reviewer's \"right to measure independently\" - put it back".to_owned()]
        }
        Some(_) => Vec::new(),
    }
}

fn verdict_last(texts: &[(String, String)]) -> Vec<String> {
    let tail = |name: &str| {
        let t = text(texts, name);
        t.find("## Output").map_or("", |at| &t[at..])
    };
    let mut bad: Vec<String> = CHECKS
        .iter()
        .filter(|n| !tail(n).contains("make review-verdict UNIT="))
        .map(|n| format!("{n}.md's Output does not write the verdict record - name `make review-verdict UNIT=` there"))
        .collect();
    if !tail("settlement-review")
        .to_lowercase()
        .contains("last act")
    {
        bad.push(
            "settlement-review.md's Output must say the verdict record is the \"last act\""
                .to_owned(),
        );
    }
    for target in ["review-paired-gate", "review-verdict"] {
        if !re(&format!("(?m)^{target}:"))
            .is_match(text(texts, "Makefile"))
            .unwrap_or(false)
        {
            bad.push(format!("the Makefile has no `{target}:` target, which the review contracts name - restore it"));
        }
    }
    bad
}

fn real() -> Vec<(String, String)> {
    let (texts, bad) = load(&root());
    assert_eq!(bad, Vec::<String>::new());
    texts
}

#[test]
fn the_first_stage_runs_before_any_map_is_read() {
    assert_eq!(first_stage_first(&real()), Vec::<String>::new());
}

#[test]
fn the_first_stage_reads_the_paired_gate_and_again_before_the_verdict() {
    assert_eq!(paired_gate(&real()), Vec::<String>::new());
}

#[test]
fn the_fix_check_judges_a_records_source_with_the_canopy_as_its_worked_example() {
    assert_eq!(canopy_example(&real()), Vec::<String>::new());
}

#[test]
fn the_reviewer_keeps_the_right_to_measure_independently() {
    assert_eq!(measures_independently(&real()), Vec::<String>::new());
}

#[test]
fn the_verdict_record_is_the_last_act_and_both_commands_exist() {
    assert_eq!(verdict_last(&real()), Vec::<String>::new());
}

#[test]
fn a_seeded_contract_is_caught() {
    let dir = crate::checks::scratch("review-contract");
    crate::checks::tests::put(
        &dir,
        ".claude/agents/settlement-review.md",
        "## Output\nx\n## First stage\nmake review-paired-gate\n## End\n",
    );
    crate::checks::tests::put(
        &dir,
        ".claude/agents/glyph-check.md",
        "## Inputs\n## First stage\n## Output\n",
    );
    crate::checks::tests::put(&dir, "Makefile", "review-verdict:\n");
    let (texts, gone) = load(&dir);
    assert_eq!(
        gone,
        [
            ".claude/agents/fix-check.md is gone - the review contract lives there; restore it",
            ".claude/agents/perf-audit.md is gone - the review contract lives there; restore it"
        ]
    );
    let order = first_stage_first(&texts);
    assert!(
        order[0].starts_with("settlement-review.md: '## First stage' must come before")
            && order[1].starts_with("fix-check.md needs both")
    );
    assert!(order[2].starts_with("glyph-check.md: '## First stage' must come before"));
    let gate = paired_gate(&texts);
    assert!(
        gate[0].contains("lost ``green``")
            && gate[3].starts_with("fix-check.md has no '## First stage'")
    );
    assert!(gate[4].starts_with("glyph-check.md's First stage lost `make review-paired-gate`"));
    assert_eq!(
        canopy_example(&texts),
        [absent("fix-check", "What you judge")]
    );
    let judged = vec![(
        "fix-check".to_owned(),
        "## What you judge\nproxy `source` CROWNS R2\n## Output\n".to_owned(),
    )];
    assert_eq!(canopy_example(&judged), ["fix-check.md's What you judge lost `16.3 ft` of the canopy's worked example (feature 240) - put it back"]);
    assert!(measures_independently(&texts)[0].contains("right to measure independently"));
    assert_eq!(
        measures_independently(&[]),
        [absent("settlement-review", "First stage")]
    );
    let last = verdict_last(&texts);
    assert_eq!(last.len(), 5, "{last:?}");
    assert!(last[3].contains("\"last act\"") && last[4].contains("`review-paired-gate:`"));
}
