//! The citation-rule inventory in `docs/research-doctrine.md` names tools that exist (feature 312, FR-005, SC-003) - the port of
//! `tests/test_citation_rule_inventory.py` by feature 449 T133, `ask:449-phase3-remainder` Q3.
//!
//! The GM, 2026-10-02: *"we should definitely make sure that our citation rules are enforced by tooling and not just remembering to do
//! the correct thing."* The inventory lists every citation rule with the tool that holds it; a tool renamed or deleted would leave a rule
//! held by nothing while the table still claimed otherwise. So every file the table names - a script, a hook, an agent contract, a test,
//! an engine module - is checked to exist, and every row names one or says why it is out of scope.

use std::path::{Path, PathBuf};

use l7r_guard::shared::py_text::strip;

use super::{dirs_under, re, read, root};

const DOC: &str = "docs/research-doctrine.md";
const HEADING: &str = "## What enforces each citation rule (feature 312, FR-005)";
const PATH: &str = r"`([A-Za-z0-9_./-]+\.(?:py|sh|md|json|jsonl|rs))(?:::[A-Za-z0-9_]+)?`";

/// Where a bare name in the table may live: the scripts live by purpose since 2026-10-08 (scripts/CLAUDE.md), so every directory under
/// scripts/ is a root a bare name may name.
fn roots(repo: &Path) -> Vec<PathBuf> {
    let mut out = vec![repo.to_path_buf(), repo.join("scripts")];
    let mut under: Vec<PathBuf> = dirs_under(&repo.join("scripts"))
        .into_iter()
        .skip(1)
        .filter(|d| d.file_name().is_some_and(|n| n != "__pycache__"))
        .collect();
    under.sort();
    out.extend(under);
    out.extend(
        [
            "l7r/diagram/interactive",
            "l7r/diagram/interactive/record",
            "research",
            "tests/interactive",
            "tests/hooks",
        ]
        .iter()
        .map(|d| repo.join(d)),
    );
    out
}

/// A row's cells: split at each `|` that no backslash escapes (a cell may hold `make canon TERMS="a\|b"`).
fn cells(line: &str) -> Vec<String> {
    let body = strip(line).trim_matches('|');
    let mut out = Vec::new();
    let mut cell = String::new();
    let mut prev = '\0';
    for c in body.chars() {
        if c == '|' && prev != '\\' {
            out.push(strip(&cell).to_owned());
            cell.clear();
        } else {
            cell.push(c);
        }
        prev = c;
    }
    out.push(strip(&cell).to_owned());
    out
}

/// The numbered rows of the inventory, or None where its heading is gone.
fn rows(doc: &str) -> Option<Vec<Vec<String>>> {
    let start = doc.find(HEADING)?;
    let row = re(r"^\| \d+ \|");
    Some(
        l7r_guard::shared::speckit::splitlines(&doc[start..])
            .into_iter()
            .filter(|l| row.is_match(l).unwrap_or(false))
            .map(cells)
            .collect(),
    )
}

fn tool_cell(row: &[String]) -> &str {
    row.get(3).map_or("", String::as_str)
}

fn missing(repo: &Path, rows: &[Vec<String>]) -> Vec<String> {
    let path = re(PATH);
    let roots = roots(repo);
    let mut out = Vec::new();
    for row in rows {
        for caps in path.captures_iter(tool_cell(row)).flatten() {
            let named = &caps[1];
            // a Python test the table names was deleted by feature 449 FR-001b, readable at the tag `python-tests-before-removal`
            if named.starts_with("tests/") || named.starts_with("test_") {
                continue;
            }
            if !roots.iter().any(|r| r.join(named).exists()) {
                out.push(format!("rule {}: `{named}` does not exist - name the tool that holds the rule now in {DOC}", row[0]));
            }
        }
    }
    out
}

fn bare(rows: &[Vec<String>]) -> Vec<String> {
    let path = re(PATH);
    let mut out = Vec::new();
    if rows.len() < 60 {
        out.push(format!("{DOC}'s inventory has {} numbered rows, fewer than 60 - the table's rows were lost or reformatted", rows.len()));
    }
    out.extend(
        rows.iter()
            .filter(|r| {
                let cell = tool_cell(r);
                !path.is_match(cell).unwrap_or(false) && !cell.contains("out of FR-005's scope") && !cell.contains("private")
            })
            .map(|r| format!("rule {} names no tool - name the file that enforces it, or say it is out of FR-005's scope", r[0])),
    );
    out
}

fn problems(repo: &Path) -> (Vec<String>, Vec<String>) {
    rows(&read(&repo.join(DOC))).map_or_else(
        || {
            let gone = vec![format!("{DOC} has no '{HEADING}' heading - restore it")];
            (gone.clone(), gone)
        },
        |rows| (missing(repo, &rows), bare(&rows)),
    )
}

#[test]
fn every_file_the_inventory_names_exists() {
    assert_eq!(problems(&root()).0, Vec::<String>::new());
}

#[test]
fn every_rule_has_a_tool_or_says_why_not() {
    assert_eq!(problems(&root()).1, Vec::<String>::new());
}

#[test]
fn a_seeded_inventory_is_caught() {
    let dir = crate::checks::scratch("citation-inventory");
    crate::checks::tests::put(&dir, "scripts/gates/held.sh", "");
    crate::checks::tests::put(&dir, "scripts/__pycache__/x.pyc", "");
    let mut doc = format!("# x\n\n{HEADING}\n\n| # | rule | in | by | m |\n");
    doc.push_str("| 1 | a | b | `held.sh`, `tests/test_x.py`, `test_y.py` | yes |\n");
    doc.push_str("| 2 | a\\|b | b | `gone.py::f` | yes |\n");
    doc.push_str("| 3 | a | b | nothing | no |\n| 4 | a | b | out of FR-005's scope | no |\n| 5 | a | b | private | no |\n");
    crate::checks::tests::put(&dir, DOC, &doc);
    let (gone, no_tool) = problems(&dir);
    assert_eq!(
        gone,
        [format!(
            "rule 2: `gone.py` does not exist - name the tool that holds the rule now in {DOC}"
        )]
    );
    assert!(no_tool[0].contains("has 5 numbered rows, fewer than 60"));
    assert_eq!(no_tool[1..], ["rule 3 names no tool - name the file that enforces it, or say it is out of FR-005's scope"]);
    assert_eq!(cells("| 7 | a\\|b |"), ["7", "a\\|b"]);
    crate::checks::tests::put(&dir, DOC, "# no inventory\n");
    let (gone, no_tool) = problems(&dir);
    assert!(gone[0].contains("heading - restore it"));
    assert_eq!(gone, no_tool);
    assert_eq!(tool_cell(&["1".to_owned()]), "");
}
