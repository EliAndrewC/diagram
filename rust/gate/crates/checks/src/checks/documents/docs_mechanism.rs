//! The operative documents must describe the coverage mechanism the tree ACTUALLY has - the port of
//! `tests/tooling/test_docs_match_the_mechanism.py` by feature 449 T133, `ask:449-phase3-remainder` Q3.
//!
//! WHY THIS EXISTS, and it is not a style rule. Feature 174 spent SIX consecutive `spec-fidelity` rounds on one failure: an item settled
//! in the spec while a sentence asserting the old state stood in a document a session reads before acting. Two of them were ACTIVELY
//! WRONG - `CLAUDE.md` and the settlements index each told a reader the floor is `fail_under = 100` in `[tool.coverage.report]`, and a
//! session acting on that would put it where `pytest-cov` reads it: the global floor would then fire on every partial run and the
//! deliberate ordering - the floor runs LAST, so a run's own failures are reported before the coverage table - would be destroyed. Twelve
//! rounds of prose review did not end the class; the check does, because it asks the CONFIG rather than the prose.

use std::path::Path;

use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::{files_under, re, read, rel, root};

/// The files a session reads before it acts. A doc not listed here is free to be a historical record; these are the ones that instruct.
const OPERATIVE: [&str; 9] = [
    "CLAUDE.md",
    ".specify/memory/constitution.md",
    ".specify/templates/plan-template.md",
    "docs/efficiency-tooling.md",
    "l7r/diagram/CLAUDE.md",
    "docs/usage.md",
    "tests/CLAUDE.md",
    "dev/gate.md",
    "docs/migration-plan.md",
];

/// A moved or renamed document must be re-pointed here, not silently skipped (feature 329: the usage document moved and the list went
/// on naming the old file, so its check quietly checked nothing).
fn missing(root: &Path) -> Vec<String> {
    OPERATIVE
        .iter()
        .filter(|p| !root.join(p).is_file())
        .map(|p| format!("OPERATIVE names {p}, which does not exist - re-point the list in rust/gate/crates/checks/src/checks/documents/docs_mechanism.rs"))
        .collect()
}

/// Whether `pyproject.toml` sets `fail_under` in `tool.coverage.report`, by its table header and dotted keys, or an inline table. A
/// line scan, not a TOML parser (the workspace has none): it reads the forms TOML allows for the key, outside comments.
fn sets_fail_under(pyproject: &str) -> bool {
    const KEY: &str = "tool.coverage.report.fail_under";
    let bare = |s: &str| {
        s.chars()
            .filter(|c| !matches!(c, '"' | '\'' | ' ' | '\t'))
            .collect::<String>()
    };
    let mut table = String::new();
    for line in splitlines(pyproject) {
        let t = strip(line);
        if t.starts_with('[') {
            table = bare(t.trim_matches(['[', ']']));
        } else if let Some((key, value)) = t.split_once('=').filter(|_| !t.starts_with('#')) {
            let full = [table.as_str(), &bare(key)]
                .iter()
                .filter(|s| !s.is_empty())
                .copied()
                .collect::<Vec<_>>()
                .join(".");
            if full == KEY
                || (KEY.starts_with(&format!("{full}.")) && bare(value).contains("fail_under="))
            {
                return true;
            }
        }
    }
    false
}

/// `lines[i-2..=i+2]` lowercased: the negation is regularly on the wrapped line before or after (measured: the constitution's own
/// clause 5 wraps "deliberately omits" onto the next line).
fn window(lines: &[&str], at: usize) -> String {
    lines[at.saturating_sub(2)..(at + 3).min(lines.len())]
        .join(" ")
        .to_lowercase()
}

fn shown(line: &str, n: usize) -> String {
    strip(line).chars().take(n).collect()
}

/// `fail_under` is deliberately NOT in `[tool.coverage.report]` - the floor is a command-line flag in the Makefile so it runs last and
/// so partial runs do not trip it. A document naming the config key is not describing the mechanism, it is prescribing a change that
/// would break it.
fn prescribed(root: &Path) -> Vec<String> {
    if sets_fail_under(&read(&root.join("pyproject.toml"))) {
        return vec!["pyproject.toml sets `fail_under` in [tool.coverage.report] after all - the floor is the Makefile's `coverage report --fail-under=100`; remove the key, or revisit this check and the docs together".to_owned()];
    }
    let names = re(
        r"\[tool\.coverage\.report\][^\n]*fail_under|fail_under[^\n]*\[tool\.coverage\.report\]|`fail_under = 100` in the config",
    );
    let excused = re(r"\bnot\b|never|omits|deliberately|used to|no longer|would break|forbid");
    let mut bad = Vec::new();
    for p in OPERATIVE
        .iter()
        .map(|p| root.join(p))
        .filter(|p| p.is_file())
    {
        let text = read(&p);
        let lines = splitlines(&text);
        for (at, line) in lines.iter().enumerate() {
            if names.is_match(line).unwrap_or(false)
                && !excused.is_match(&window(&lines, at)).unwrap_or(false)
            {
                bad.push(format!("{}:{}: {} - this PRESCRIBES a coverage config key that is not set; the floor is `coverage report --fail-under=100` in the Makefile: describe that", rel(&p, root), at + 1, shown(line, 90)));
            }
        }
    }
    bad
}

/// GM 2026-09-02: *"a new tool absolutely should silently owe one hundred percent coverage the day it lands ... for everything."* Four
/// modules carried such a claim in their own docstrings and the first sweep found only three - the fourth said "NOT UNDER THE COVERAGE
/// GATE" where the others said "not under the 100% rule". This asks for the CLAIM in any wording rather than for one phrase.
fn exempt_claims(root: &Path) -> Vec<String> {
    let claim = re(
        r"(?i)not under the (100%|coverage)|NOT UNDER THE COVERAGE|outside the coverage gate|stays outside the coverage|exempt from the (100%|coverage)|owes no (coverage|tests)",
    );
    // a docstring recording that it USED to claim exemption wraps, and the disclaimer is regularly on the line above the quoted claim
    let excused = re(r"used to|no longer|this paragraph|the opposite|was removed|abolished");
    let mut bad = Vec::new();
    for p in files_under(&root.join("l7r"), ".py") {
        let text = read(&p);
        let lines = splitlines(&text);
        for (at, line) in lines.iter().enumerate() {
            if claim.is_match(line).unwrap_or(false)
                && !excused.is_match(&window(&lines, at)).unwrap_or(false)
            {
                bad.push(format!("{}:{}: {} - an engine module claiming it owes no coverage, the opt-in the GM abolished; remove the claim", rel(&p, root), at + 1, shown(line, 80)));
            }
        }
    }
    bad
}

/// The deferral was real until feature 174 and is what the GM's request closed. A document still describing it as current sends a
/// session to `make done FULL=1` for a floor a plain `make done` now enforces - and implies a plain gate can go green below it.
fn deferred(root: &Path) -> Vec<String> {
    let says = re(r"(?i)floors? (are |is )?deferred|deferred to `make done FULL=1`");
    // a line that says it USED to be so, or marks it retired, is the record and is fine
    let record =
        re(r"(?i)retired|had been|used to|was DEFERRED|is what that feature closed|printed");
    let mut bad = Vec::new();
    for p in OPERATIVE
        .iter()
        .map(|p| root.join(p))
        .filter(|p| p.is_file())
    {
        let text = read(&p);
        for (at, line) in splitlines(&text).iter().enumerate() {
            if says.is_match(line).unwrap_or(false) && !record.is_match(line).unwrap_or(false) {
                bad.push(format!("{}:{}: {} - this describes the retired deferral as current; a plain `make done` enforces the floors", rel(&p, root), at + 1, shown(line, 90)));
            }
        }
    }
    bad
}

#[test]
fn every_operative_document_exists() {
    assert_eq!(missing(&root()), Vec::<String>::new());
}

#[test]
fn no_operative_document_names_a_coverage_key_the_config_does_not_set() {
    assert_eq!(prescribed(&root()), Vec::<String>::new());
}

#[test]
fn no_engine_module_claims_exemption_from_the_coverage_rule() {
    assert_eq!(exempt_claims(&root()), Vec::<String>::new());
}

#[test]
fn no_operative_document_says_the_coverage_floors_are_deferred() {
    assert_eq!(deferred(&root()), Vec::<String>::new());
}

#[test]
fn the_config_scan_reads_each_form_of_the_key() {
    assert!(sets_fail_under(
        "[tool.coverage.report]\nfail_under = 100\n"
    ));
    assert!(sets_fail_under(
        "[tool.coverage]\nreport.fail_under = 100\n"
    ));
    assert!(sets_fail_under(
        "[ \"tool\".coverage ]\nreport = { fail_under = 100 }\n"
    ));
    assert!(sets_fail_under("tool.coverage.report.fail_under = 100\n"));
    assert!(!sets_fail_under("[tool.coverage.report]\n# fail_under = 100\nshow_missing = true\n[tool.coverage.run]\nfail_under = 1\n"));
    assert!(!sets_fail_under(
        "[tool.coverage]\nreport = { show_missing = true }\n"
    ));
}

#[test]
fn a_seeded_document_and_module_are_caught() {
    let dir = crate::checks::scratch("docs-mechanism");
    assert_eq!(missing(&dir).len(), 9);
    for p in OPERATIVE {
        crate::checks::tests::put(&dir, p, "");
    }
    assert_eq!(missing(&dir), Vec::<String>::new());
    crate::checks::tests::put(&dir, "CLAUDE.md", "a\nPut `fail_under = 100` in the config.\nb\n\nc\nd\nThe config deliberately omits\n`fail_under = 100` in the config.\nThe floors are deferred to the full run.\nThe floors were retired; deferred to `make done FULL=1` printed.\n");
    crate::checks::tests::put(&dir, "l7r/diagram/x.py", "\"\"\"This module is NOT UNDER THE COVERAGE GATE.\n\n\n\nIt used to say: owes no tests.\"\"\"\n");
    assert_eq!(prescribed(&dir), ["CLAUDE.md:2: Put `fail_under = 100` in the config. - this PRESCRIBES a coverage config key that is not set; the floor is `coverage report --fail-under=100` in the Makefile: describe that"]);
    assert_eq!(exempt_claims(&dir), ["l7r/diagram/x.py:1: \"\"\"This module is NOT UNDER THE COVERAGE GATE. - an engine module claiming it owes no coverage, the opt-in the GM abolished; remove the claim"]);
    assert_eq!(deferred(&dir), ["CLAUDE.md:9: The floors are deferred to the full run. - this describes the retired deferral as current; a plain `make done` enforces the floors"]);
    crate::checks::tests::put(
        &dir,
        "pyproject.toml",
        "[tool.coverage.report]\nfail_under = 100\n",
    );
    assert!(prescribed(&dir)[0].starts_with("pyproject.toml sets `fail_under`"));
}
