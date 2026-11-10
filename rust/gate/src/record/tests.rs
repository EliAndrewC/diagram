//! Each tool on a scratch tree, and every refusal.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{canon, canon_files, cli, close_rows, found, money, py_lines};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn lines_split_as_python_splits_them() {
    assert_eq!(
        py_lines("a\nb\r\nc\rd\u{c}e\u{2028}f\n"),
        ["a", "b", "c", "d", "e", "f"]
    );
    assert_eq!(py_lines("no end"), ["no end"]);
    assert!(py_lines("").is_empty());
}

fn canon_tree(tag: &str) -> Vec<PathBuf> {
    let a = crate::checks::scratch(tag);
    std::fs::create_dir_all(a.join("deep")).unwrap();
    std::fs::write(
        a.join("z.md"),
        "# Roads\nthe imperial ROAD runs north\nnothing here\n",
    )
    .unwrap();
    std::fs::write(a.join("deep/a.txt"), format!("road {}\n", "x".repeat(500))).unwrap();
    std::fs::write(a.join("CLAUDE.md"), "road\n").unwrap();
    std::fs::write(a.join("b.json"), "road\n").unwrap();
    vec![a, PathBuf::from("/nonexistent/x")]
}

#[test]
fn every_term_is_answered_with_its_heading_and_a_miss_says_so() {
    let roots = canon_tree("rec-canon");
    let got = canon(&words(&["road | merchant share|"]), &roots);
    assert_eq!(got.code, 0);
    let root = roots[0].display();
    assert!(
        got.stdout.starts_with(&format!(
            "== road: 3 hit(s)\n  {root}/deep/a.txt:1 [] road "
        )),
        "{}",
        got.stdout
    );
    assert!(got.stdout.contains("...\n"));
    assert!(got.stdout.contains(&format!(
        "  {root}/z.md:2 [Roads] the imperial ROAD runs north\n"
    )));
    assert!(got.stdout.ends_with("== merchant share: 0 hit(s)\n"));
}

#[test]
fn a_term_past_the_cap_shows_the_first_fifteen() {
    let a = crate::checks::scratch("rec-cap");
    std::fs::write(a.join("n.md"), "road\n".repeat(20)).unwrap();
    let got = canon(&words(&["road"]), &[a]);
    assert!(got
        .stdout
        .starts_with("== road: 20 hit(s), the first 15 shown\n"));
    assert_eq!(got.stdout.lines().count(), 16);
}

#[test]
fn the_canon_is_each_roots_files_in_path_order() {
    let roots = canon_tree("rec-files");
    let names: Vec<String> = canon_files(&roots)
        .iter()
        .map(|p| p.strip_prefix(&roots[0]).unwrap().display().to_string())
        .collect();
    assert_eq!(names, ["deep/a.txt", "z.md"]);
}

#[test]
fn no_term_is_refused() {
    assert_eq!(canon(&[], &[]).code, 2);
    assert_eq!(canon(&words(&[" | "]), &[]).code, 2);
}

fn money_tree(tag: &str, held: Option<&str>) -> (PathBuf, PathBuf) {
    let root = crate::checks::scratch(tag);
    std::fs::create_dir_all(root.join("research/assets")).unwrap();
    if let Some(text) = held {
        std::fs::write(root.join("research/assets/money-conversions.json"), text).unwrap();
    }
    let source = root.join("source.json");
    std::fs::write(&source, "fresh").unwrap();
    (root, source)
}

#[test]
fn the_copy_is_refreshed_checked_and_reported() {
    let (root, source) = money_tree("rec-money", Some("old"));
    let check = words(&["--check"]);
    let got = money(&check, &source, &root);
    assert!(got.code == 1 && got.stderr.contains("run `make money-conversions`"));
    let got = money(&[], &source, &root);
    assert!(got.code == 0 && got.stdout.contains("refreshed from"));
    assert_eq!(
        std::fs::read_to_string(root.join("research/assets/money-conversions.json")).unwrap(),
        "fresh"
    );
    assert!(money(&check, &source, &root)
        .stdout
        .ends_with("is current\n"));
    let (blank, source) = money_tree("rec-money-new", None);
    assert_eq!(money(&[], &source, &blank).code, 0);
    let got = money(&[], Path::new("/nonexistent/s"), &blank);
    assert!(got.code == 0 && got.stdout.contains("nothing to compare"));
    assert_eq!(money(&[], &source, Path::new("/nonexistent/r")).code, 1);
}

fn rows() -> Vec<Value> {
    vec![
        json!({"check": "c", "file": "f", "finding": "one"}),
        json!({"finding": "two", "status": "filed"}),
        json!({"check": "d", "finding": "three"}),
    ]
}

const WHY: &str = "no longer holds: measured against the current file";

#[test]
fn a_row_is_filed_or_settled_and_keeps_its_fields() {
    let mut r = rows();
    assert_eq!(close_rows(&mut r, &[1], "T61", "", "W"), Ok(1));
    assert_eq!(
        r[0],
        json!({"check": "c", "file": "f", "finding": "one", "status": "filed", "task": "T61", "closed_utc": "W"})
    );
    assert_eq!(close_rows(&mut r, &[3], "", WHY, "W"), Ok(1));
    assert_eq!(r[2]["status"], "settled");
    assert_eq!(r[2]["why"], WHY);
    let mut r = rows();
    assert_eq!(close_rows(&mut r, &[1, 3], "385 T12", "", "W"), Ok(2));
}

#[test]
fn a_close_that_breaks_a_rule_is_refused_and_changes_nothing() {
    let mut r = rows();
    let mut wrong = |n: &[usize], t: &str, w: &str| close_rows(&mut r, n, t, w, "W").unwrap_err();
    assert!(wrong(&[1], "", "").starts_with("one of"));
    assert!(wrong(&[1], "T1", WHY).starts_with("one of"));
    assert!(wrong(&[], "T1", "").starts_with("no rows named"));
    assert!(wrong(&[1], "T", "").contains("names a task id"));
    assert!(wrong(&[1], "406 T1", "").contains("names a task id"));
    assert!(wrong(&[1], "", "no longer holds, short").starts_with("--why"));
    assert!(wrong(&[1], "", "still holds but we will not file it today").starts_with("--why"));
    assert!(wrong(&[9], "T1", "").starts_with("no row 9"));
    assert!(wrong(&[0], "T1", "").starts_with("no row 0"));
    assert_eq!(wrong(&[2], "T1", ""), "row 2 is already filed");
    assert_eq!(r, rows());
}

fn feature(tag: &str) -> (PathBuf, String) {
    let dir = crate::checks::scratch(tag);
    let body: String = rows().iter().map(|r| format!("{r}\n")).collect();
    std::fs::write(dir.join("found.jsonl"), body + "\n").unwrap();
    let name = dir.display().to_string();
    (dir, name)
}

#[test]
fn the_list_numbers_open_rows_in_file_order() {
    let (dir, name) = feature("rec-list");
    let got = found(&words(&["list", "--feature", &name]));
    let path = dir.join("found.jsonl");
    assert_eq!(
        got.stdout,
        format!(
            "  1  c  f  one\n  3  d  ?  three\nfound: 2 open of 3 row(s) in {}\n",
            path.display()
        )
    );
}

#[test]
fn close_writes_the_rows_back_as_json_dumps_writes_them() {
    let (dir, name) = feature("rec-close");
    let got = found(&words(&[
        "close",
        "--feature",
        &name,
        "--rows",
        "1, 3",
        "--task",
        "T7",
    ]));
    assert!(
        got.code == 0 && got.stdout.starts_with("found: 2 row(s) filed as T7 in "),
        "{}",
        got.stderr
    );
    let text = std::fs::read_to_string(dir.join("found.jsonl")).unwrap();
    assert!(text.starts_with("{\"check\": \"c\", \"file\": \"f\""));
    assert_eq!(text.lines().count(), 3);
    let (_, name) = feature("rec-settle");
    let got = found(&words(&[
        "close",
        "--feature",
        &name,
        "--rows",
        "1",
        "--why",
        WHY,
    ]));
    assert!(got.stdout.starts_with("found: 1 row(s) settled in "));
}

#[test]
fn found_refuses_what_it_cannot_do() {
    let (dir, name) = feature("rec-bad");
    assert_eq!(found(&[]).code, 2);
    assert_eq!(found(&words(&["list"])).code, 2);
    let got = found(&words(&[
        "close",
        "--feature",
        &name,
        "--rows",
        "x",
        "--task",
        "T1",
    ]));
    assert!(got.code == 2 && got.stderr.contains("not x"));
    let got = found(&words(&["close", "--feature", &name, "--rows", "1"]));
    assert!(got.code == 2 && got.stderr.starts_with("found: refused - one of"));
    std::fs::write(dir.join("found.jsonl"), "{\n").unwrap();
    assert_eq!(found(&words(&["list", "--feature", &name])).code, 1);
    let none = crate::checks::scratch("rec-none")
        .join("x")
        .display()
        .to_string();
    assert!(found(&words(&["list", "--feature", &none]))
        .stdout
        .starts_with("found: 0 open of 0"));
    assert_eq!(
        found(&words(&[
            "close",
            "--feature",
            &none,
            "--rows",
            "1",
            "--task",
            "T1"
        ]))
        .code,
        2
    );
    let locked = crate::checks::scratch("rec-locked");
    std::fs::create_dir(locked.join("found.jsonl")).unwrap();
    assert!(found(&words(&[
        "list",
        "--feature",
        &locked.display().to_string()
    ]))
    .stdout
    .contains("0 open"));
}

#[test]
fn a_write_that_fails_says_so() {
    let (dir, name) = feature("rec-nowrite");
    let path = dir.join("found.jsonl");
    let mut perms = std::fs::metadata(&path).unwrap().permissions();
    std::os::unix::fs::PermissionsExt::set_mode(&mut perms, 0o444);
    std::fs::set_permissions(&path, perms).unwrap();
    assert_eq!(
        found(&words(&[
            "close",
            "--feature",
            &name,
            "--rows",
            "1",
            "--task",
            "T1"
        ]))
        .code,
        1
    );
}

#[test]
fn the_command_line_routes_each_verb() {
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(cli(&words(&["frob"])).code, 2);
    assert_eq!(cli(&words(&["canon"])).code, 2);
    assert_eq!(cli(&words(&["found"])).code, 2);
    assert_eq!(cli(&words(&["canon", "zzz-no-such-term"])).code, 0);
    assert!([0, 1].contains(&cli(&words(&["money-conversions", "--check"])).code));
}
