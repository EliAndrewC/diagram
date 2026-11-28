//! The report's cut (462 T555) over scratch feature directories. `GUARD_EDIT_OK`: 462 T555 the report split's own tests.

use std::fmt::Write as _;

use super::*;
use crate::tempdir::TempDir;

/// A report past [`BOUND`]: a title, a small section, a large table of three-row runs per task, a small table and a large section with
/// no table.
fn report() -> String {
    let mut t = String::from("# Feature report - 999-scratch\n\n## Where the time went\n\n- a line\n\n## Each task's phases (plan D32)\n\n| task | span |\n|---|---|\n");
    for n in 1..=900 {
        for k in 0..3 {
            let _ = writeln!(t, "| T{n:03} | 06:{k:02}-07:00 {} |", "x".repeat(40));
        }
    }
    t += "\n## Small table\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n## Prose only\n\n";
    t += &"word ".repeat(4000);
    t += "\n";
    t
}

fn scratch(tag: &str) -> (TempDir, std::path::PathBuf) {
    let t = TempDir::new(&format!("report-{tag}"));
    let d = t.join("999-scratch");
    std::fs::create_dir_all(&d).unwrap();
    (t, d)
}

#[test]
fn a_large_report_is_cut_at_its_rows_and_its_index_names_every_part() {
    let text = report();
    let (index, parts) = split("999-scratch", &text).unwrap();
    assert!(index.starts_with("# Feature report - 999-scratch\n\n<!-- report split"));
    assert!(index.contains("Load this file when: you need feature 999's report"));
    assert!(index.contains("## Where the time went\n\n- a line\n") && index.contains("| 1 | 2 |"));
    assert!(index.len() < INLINE);
    // the table's parts and the prose's one
    let table: Vec<&(String, String)> = parts
        .iter()
        .filter(|(p, _)| p.contains("-each-task-s-phases-plan-d32-"))
        .collect();
    assert!(table.len() > 1);
    assert!(parts
        .iter()
        .any(|(p, b)| p == "report/04-prose-only-1.md" && b.starts_with("## Prose only")));
    let mut rows = String::new();
    let mut seen = std::collections::BTreeSet::new();
    for (path, body) in &table {
        assert!(
            body.len() <= BOUND
                && index.contains(&format!("- `{path}` ({} bytes, rows ", body.len()))
        );
        assert!(
            body.starts_with("## Each task's phases (plan D32)\n\n| task | span |\n|---|---|\n")
        );
        let own: Vec<&str> = body.lines().filter(|l| l.starts_with("| T")).collect();
        // a task's three rows stand in one part
        for cell in own.iter().map(|l| first_cell(l)) {
            assert_eq!(own.iter().filter(|l| first_cell(l) == cell).count(), 3);
        }
        for l in &own {
            seen.insert((first_cell(l).to_owned(), path.clone()));
            rows += l;
            rows += "\n";
        }
    }
    let flat: String = text
        .lines()
        .filter(|l| l.starts_with("| T"))
        .flat_map(|l| [l, "\n"])
        .collect();
    assert_eq!(rows, flat);
    let cells: std::collections::BTreeSet<&String> = seen.iter().map(|(c, _)| c).collect();
    assert_eq!(cells.len(), seen.len());
    // a split report, and a small one, are left as they stand
    assert!(split("999-scratch", &index).is_none() && split("999-scratch", "# small\n").is_none());
}

#[test]
fn write_splits_only_where_asked_and_clears_an_earlier_split() {
    let (_t, d) = scratch("write");
    let text = report();
    let written = write(&d, &text, true).unwrap();
    assert!(!written.is_empty() && written.iter().all(|p| d.join(p).is_file()));
    assert!(std::fs::read_to_string(d.join(REPORT))
        .unwrap()
        .contains(MARK));
    // a second split of the index keeps its parts
    let index = std::fs::read_to_string(d.join(REPORT)).unwrap();
    assert_eq!(write(&d, &index, true).unwrap(), Vec::<String>::new());
    assert!(d.join(DIR).is_dir());
    // a whole write (an unsplit feature) removes the parts
    assert_eq!(write(&d, &text, false).unwrap(), Vec::<String>::new());
    assert!(!d.join(DIR).exists());
    assert_eq!(std::fs::read_to_string(d.join(REPORT)).unwrap(), text);
    // a part that cannot be written, and a report that cannot be
    std::fs::write(d.join(DIR), "a file where the directory goes").unwrap();
    let e = write(&d, &text, true).unwrap_err();
    assert!(e.contains("report"), "{e}");
    std::fs::remove_file(d.join(DIR)).unwrap();
    std::fs::remove_file(d.join(REPORT)).unwrap();
    std::fs::create_dir(d.join(REPORT)).unwrap();
    assert!(write(&d, "# small\n", true).is_err());
    assert!(write(&d, &text, true).is_err());
}

#[test]
fn a_section_with_no_rows_under_its_header_is_one_part() {
    let one = rows_cut("## A\n\n| h |\n|---|\n\ntext\n");
    assert_eq!(
        one,
        vec![(
            String::new(),
            String::new(),
            "## A\n\n| h |\n|---|\n\ntext\n".to_owned()
        )]
    );
    assert_eq!(
        slug("## The critical path and what was spent beside it (`make where-time`'s)"),
        "the-critical-path-and-what-was-spent"
    );
}

/// 451's critical path holds eight tables and its decision-log skeleton a task of 120 KB of rows: a later table's part opens with
/// that table's header, and one task's long run is cut between rows.
#[test]
fn every_table_of_a_section_is_cut_and_a_long_run_too() {
    let mut s = String::from("## Many\n\n| a | b |\n|---|---|\n");
    for n in 0..2000 {
        let _ = writeln!(s, "| T{n} | {} |", "x".repeat(30));
    }
    s += "\nbetween\n\n| c | d |\n|---|---|\n";
    for _ in 0..3000 {
        let _ = writeln!(s, "| T9 | {} |", "y".repeat(30));
    }
    let parts = rows_cut(&s);
    assert!(parts
        .iter()
        .all(|p| p.2.len() <= BOUND && p.2.starts_with("## Many\n")));
    let joined: String = parts.iter().map(|p| p.2.as_str()).collect();
    assert_eq!(joined.matches("| T9 | y").count(), 3000);
    assert!(joined.contains("\nbetween\n"));
    let late = parts.last().unwrap();
    assert!(
        late.2
            .starts_with("## Many\n\n| c | d |\n|---|---|\n| T9 |")
            && late.0 == "T9"
            && late.1 == "T9"
    );
    assert!(parts.iter().filter(|p| p.2.contains("| T9 | y")).count() > 1);
}
