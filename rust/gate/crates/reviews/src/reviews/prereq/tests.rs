//! The prerequisites and the verdict record on scratch repositories, the generation cache and the gate stubbed (`tools`).

use std::path::Path;

use serde_json::{json, Value};

use super::super::tests::{map, put, repo, sheet};
use super::*;

const V: &str = ".git/review-verdicts/settlement-review--m.json";

fn run_in(root: &Path, a: &[&str]) -> Reply {
    let mut all: Vec<String> = a.iter().map(|s| (*s).to_owned()).collect();
    all.extend(["--clone".to_owned(), root.to_string_lossy().into_owned()]);
    cli(&all)
}

fn read(root: &Path, rel: &str) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join(rel)).unwrap()).unwrap()
}

fn verdict() -> Value {
    json!({"verdict": "NEEDS-WORK", "engine_key": "abcdef0123456789", "strict": true, "findings": [{"id": "F1"}, {"id": "F2"}, "junk"]})
}

#[test]
fn a_verdict_record_is_the_reviews_last_act() {
    let r = repo("verdict");
    map(&r, "pool", "m", &["well"]);
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "k123"}"#,
    );
    put(&r, ".git/f.json", r#"[{"what": "a"}, {"id": "X9"}, 3]"#);
    let f = r.join(".git/f.json").to_string_lossy().into_owned();
    put(&r, ".git/green", "");
    let said = run_in(
        &r,
        &[
            "verdict",
            "--unit",
            "settlement-review--m",
            "--verdict",
            "PASS",
            "--findings-file",
            &f,
        ],
    );
    assert_eq!(
        said.stdout,
        "recorded PASS for settlement-review--m (engine key k123, gate green)\n"
    );
    let rec = read(&r, V);
    assert_eq!(
        rec["findings"],
        json!([{"what": "a", "id": "F1"}, {"id": "X9"}])
    );
    assert_eq!(rec["content_key"].as_str().unwrap().len(), 16);
    // red: recorded NOT-REVIEWABLE, carrying the prior verdict's findings
    std::fs::remove_file(r.join(".git/green")).unwrap();
    put(&r, ".git/live", "123 make done\n\n");
    let said = run_in(
        &r,
        &[
            "verdict",
            "--map",
            "settlement-review--m",
            "--verdict",
            "PASS",
        ],
    );
    assert!(said.stdout.ends_with("gate running)\n"));
    std::fs::remove_file(r.join(".git/live")).unwrap();
    put(&r, ".git/pairing-state.json", "[]");
    let said = run_in(
        &r,
        &[
            "verdict",
            "--map",
            "settlement-review--m",
            "--verdict",
            "NEEDS-WORK",
        ],
    );
    assert_eq!(said.stdout, "recorded NOT-REVIEWABLE for settlement-review--m (engine key NONE - no dispatch recorded, gate red)\n");
    let rec = read(&r, V);
    assert_eq!(
        (rec["concluded"].clone(), rec["carried_from"].clone()),
        (json!("NEEDS-WORK"), json!("k123"))
    );
    let bad = run_in(&r, &["verdict", "--map", "m", "--verdict", "BOGUS"]);
    assert_eq!((bad.code, bad.stdout.as_str()), (1, ""));
    put(&r, ".git/obj.json", "{}");
    let obj = r.join(".git/obj.json").to_string_lossy().into_owned();
    let notlist = run_in(
        &r,
        &[
            "verdict",
            "--map",
            "m",
            "--verdict",
            "PASS",
            "--findings-file",
            &obj,
        ],
    );
    assert_eq!(
        (notlist.code, notlist.stdout.as_str()),
        (
            2,
            "--findings-file must hold a JSON list of {id, severity, what}\n"
        )
    );
}

#[test]
fn a_finding_is_accepted_with_a_reason_for_its_round() {
    let r = repo("accept");
    let acc = |finding: &str, reason: &str| {
        run_in(
            &r,
            &[
                "accept",
                "--map",
                "settlement-review--m",
                "--finding",
                finding,
                "--reason",
                reason,
            ],
        )
    };
    assert_eq!(acc("F1", "short").stdout, "an acceptance needs a REASON of at least two words and eight characters - it is what a later audit reads\n");
    assert_eq!(
        acc("F1", "left on purpose").stdout,
        "settlement-review--m's last verdict raised no finding 'F1' (it raised: none)\n"
    );
    put(&r, V, &verdict().to_string());
    assert_eq!(acc("F9", "left on purpose").code, 1);
    put(
        &r,
        ".git/review-dispositions/settlement-review--m.json",
        r#"{"accepted": [{"finding": "F1", "round": "abcdef012345", "reason": "old"}, {"finding": "F2", "round": "zz", "reason": "x y"}, 5]}"#,
    );
    let ok = acc("F1", " left on purpose ");
    assert_eq!(
        (ok.code, ok.stdout.as_str()),
        (0, "accepted F1 on settlement-review--m\n")
    );
    assert_eq!(
        read(&r, ".git/review-dispositions/settlement-review--m.json")["accepted"],
        json!([{"finding": "F2", "round": "zz", "reason": "x y"}, {"finding": "F1", "round": "abcdef012345", "reason": "left on purpose"}])
    );
    // a NOT-REVIEWABLE verdict's own findings, where a red gate downgraded a concluded review
    put(
        &r,
        V,
        r#"{"verdict": "NOT-REVIEWABLE", "carried_from": "fedcba9876543210", "carried": [{"id": "F3"}], "concluded": "PASS", "findings": [{"id": "F4"}]}"#,
    );
    assert_eq!(acc("F4", "left on purpose").code, 0);
    assert_eq!(
        read(&r, ".git/review-dispositions/settlement-review--m.json")["accepted"][2]["round"],
        json!("fedcba987654")
    );
}

#[test]
fn a_verdict_with_no_findings_owes_no_record() {
    let r = repo("nofindings");
    put(
        &r,
        V,
        r#"{"verdict": "PASS", "engine_key": "K", "findings": []}"#,
    );
    assert!(unverified_findings(&r, "settlement-review--m", &[]).is_empty());
    assert_eq!(answers_hint(&r, "settlement-review--m"), "");
}

#[test]
fn a_review_is_recorded_only_at_its_engine_key() {
    let r = repo("recorded");
    let rec = |maps: &str, key: &str| run_in(&r, &["recorded", "--maps", maps, "--key", key]).code;
    assert_eq!(rec("settlement-review--m", "K"), 1);
    put(
        &r,
        V,
        &json!({"verdict": "PASS", "engine_key": "K"}).to_string(),
    );
    assert_eq!(rec("settlement-review--m", "K"), 0);
    assert_eq!(rec("settlement-review--m", "J"), 1);
    assert_eq!(rec("", "K"), 1);
    assert_eq!(rec("settlement-review--m", ""), 1);
    put(&r, V, r#"{"verdict": "NOT-REVIEWABLE", "engine_key": "K"}"#);
    assert_eq!(rec("settlement-review--m", "K"), 1);
    put(&r, V, r#"{"verdict": "MAYBE"}"#);
    assert_eq!(rec("settlement-review--m", "K"), 1);
}

#[test]
fn a_dispatch_names_its_units_else_its_maps() {
    let r = repo("named");
    map(&r, "pool", "inashiro", &[]);
    map(&r, "pool", "m", &[]);
    let named = |prompt: &str, maps: &[&str]| {
        put(&r, ".git/p.md", prompt);
        let mut a = vec!["named", "--prompt-file"];
        let p = r.join(".git/p.md").to_string_lossy().into_owned();
        a.push(&p);
        a.extend_from_slice(maps);
        run_in(&r, &a).stdout
    };
    assert_eq!(named("UNIT: glyph-check--b-c\n.git/review-snapshot/size-audit--x-y/clone UNIT:settlement-review--a", &[]), "glyph-check--b-c\nsettlement-review--a\nsize-audit--x-y\n");
    assert_eq!(named("look at review-snapshot/m and inashiro", &[]), "m\n");
    assert_eq!(named("review INASHIRO and m-x, not mm", &[]), "inashiro\n");
    assert_eq!(named("aa and bb-c", &["--maps", "aa bb"]), "aa\n");
    let missing = run_in(&r, &["named", "--prompt-file", "/no/such/file"]);
    assert_eq!((missing.code, missing.stdout.as_str()), (1, ""));
}

#[test]
fn the_content_key_is_the_sheets_drawing_and_notes() {
    let r = repo("ck");
    assert_eq!(content_key(&r, ""), "");
    assert_eq!(content_key(&r, "s"), "");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    let first = content_key(&r, "s");
    assert_eq!(first.len(), 16);
    put(
        &r,
        "legacy-hand-authored-pool/compounds/s/s.notes.md",
        "notes\n",
    );
    assert_ne!(content_key(&r, "s"), first);
    assert_eq!(
        run_in(&r, &["content-key", "--map", "building-review--s"])
            .stdout
            .len(),
        17
    );
    assert_eq!(run_in(&r, &["content-key", "--unit", "nope"]).stdout, "\n");
}

#[test]
fn the_paired_gate_is_green_running_or_red() {
    let r = repo("gate");
    assert_eq!(run_in(&r, &["gate-state"]).stdout, "red\n");
    put(&r, ".git/live", "9 make verify\n");
    assert_eq!(run_in(&r, &["gate-state"]).stdout, "running\n");
    put(&r, ".git/live", "9 make quick\n");
    assert_eq!(run_in(&r, &["gate-state"]).stdout, "red\n");
    put(&r, ".git/green", "");
    assert_eq!(run_in(&r, &["gate-state"]).stdout, "green\n");
}

#[test]
fn a_check_names_every_unmet_prerequisite() {
    let r = repo("check");
    map(&r, "pool", "m", &["well"]);
    for ext in [".svg", ".png", ".html"] {
        put(&r, &format!("pool/hamlets/m/m{ext}"), "x");
    }
    put(&r, V, &json!({"verdict": "NEEDS-WORK", "engine_key": "abcdef0123456789", "strict": true, "findings": [{"id": "F1"}, {"id": "F2"}, {"id": "F3"}]}).to_string());
    put(&r, "specs/900-x/measurements.json", &json!({
        "t89-a": {"value": 42.5, "verifies": "F1", "subject": "settlement-review--m", "quantity": "q", "source": "s", "answers": "abcdef0123456789"},
        "t89-weak": {"value": 1, "verifies": "F3", "subject": "settlement-review--m", "quantity": "q", "source": "s", "answers": "short"},
        "t89-b": {"value": "1,234 px"},
        "not-an-entry": 5
    }).to_string());
    put(&r, "specs/901-y/measurements.json", "[1]");
    put(
        &r,
        ".git/review-dispositions/settlement-review--m.json",
        r#"{"accepted": [{"finding": "F2", "round": "abcdef012345", "reason": "left on purpose"}]}"#,
    );
    put(&r, ".git/p.md", "UNIT: settlement-review--m\n\nThe belt is 42.5 px wide (m:t89-a) and 1,234 px long.\n\nIt took 17 s, observed 2026-11-11, method: a stopwatch.\n\nIt costs 9 s `and 3 s named`.\n");
    let p = r.join(".git/p.md").to_string_lossy().into_owned();
    let check = |extra: &[&str]| {
        let mut a = vec!["check", "--prompt-file", &p];
        a.extend_from_slice(extra);
        run_in(&r, &a)
    };
    let said = check(&["--maps", "settlement-review--m"]);
    assert_eq!(said.code, 1);
    assert_eq!(
        said.stdout,
        "FR-003 settlement-review--m: finding(s) F3 from its last review have no record verifying them - add a measurements.json entry with \
         \"verifies\", \"subject\": \"settlement-review--m\" and \"answers\": \"abcdef012345\", or `make review-accept MAP=settlement-review--m FINDING=<id> REASON=\"...\"` for one deliberately left\n\
         FR-004 this is a review of FIXES, and the gate is not green for this engine key - run `make done` first\n\
         FR-006 figure(s) quoted with no record behind them: 1,234 px; 9 s - cite the `m:` key or record it\n"
    );
    // the map stale, a snapshot named, a missing render, a snapshot of an older map, no generator
    put(&r, "pool/hamlets/m/m.gen.py.stale", "");
    put(&r, ".git/p.md", "x");
    let stale = check(&["--maps", "m", "--gate-green", "yes"]);
    assert!(
        stale
            .stdout
            .contains("FR-005 m: its generation key has moved"),
        "{}",
        stale.stdout
    );
    std::fs::remove_file(r.join("pool/hamlets/m/m.gen.py.stale")).unwrap();
    put(&r, ".git/p.md", "review .git/review-snapshot/m");
    assert!(check(&["--maps", "m"])
        .stdout
        .contains("the review snapshot the dispatch names lacks .json .svg .png .html"));
    for ext in [".json", ".svg", ".png", ".html"] {
        put(&r, &format!(".git/review-snapshot/m/clone/m{ext}"), "old");
    }
    assert!(check(&["--maps", "m"])
        .stdout
        .contains("is of an older map than the pool's"));
    put(&r, ".git/p.md", "x");
    std::fs::remove_file(r.join("pool/hamlets/m/m.png")).unwrap();
    assert!(check(&["--maps", "m"])
        .stdout
        .contains("its pool folder lacks .png"));
    assert!(check(&["--maps", "nosuch"])
        .stdout
        .contains("nosuch: no pool generator by that name"));
    put(&r, "pool/hamlets/m/m.png", "x");
    let clean = check(&["--maps", "m"]);
    assert_eq!((clean.code, clean.stdout.as_str()), (0, ""));
    // a Mode A sheet has no manifest to miss; a unit names the map it is reviewed on
    sheet(&r, "pool", "s", &["gate"]);
    put(&r, "pool/compounds/s/s.gen.py", "#\n");
    for ext in [".png", ".html"] {
        put(&r, &format!("pool/compounds/s/s{ext}"), "x");
    }
    put(&r, ".git/p.md", "x .git/review-snapshot/building-review--s");
    assert!(check(&["--maps", "building-review--s"])
        .stdout
        .contains("FR-005 s: the review snapshot the dispatch names lacks .svg .png .html"));
    // the generation cache's runner failing, and the figure pattern's, fail the check
    put(&r, "pool/hamlets/m/m.gen.py.broken", "");
    let broken = check(&["--maps", "m"]);
    assert_eq!((broken.code, broken.stdout.as_str()), (1, ""));
    std::fs::remove_file(r.join("pool/hamlets/m/m.gen.py.broken")).unwrap();
    put(&r, ".git/no-pattern", "");
    assert_eq!(check(&["--maps", ""]).code, 1);
    assert_eq!(check(&["--maps", ""]).stdout, "");
}

#[test]
fn the_command_line_reads_as_argparse_did() {
    assert_eq!(
        cli(&["nope".to_owned(), "--clone".to_owned(), ".".to_owned()]).code,
        2
    );
    assert_eq!(cli(&["named".to_owned()]).code, 2);
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(
        cli(&[
            "check".to_owned(),
            "--clone".to_owned(),
            ".".to_owned(),
            "--gate-green".to_owned(),
            "maybe".to_owned()
        ])
        .code,
        2
    );
    assert_eq!(
        cli(&[
            "check".to_owned(),
            "--clone".to_owned(),
            ".".to_owned(),
            "--prompt-file".to_owned(),
            "/no/such".to_owned()
        ])
        .code,
        1
    );
    assert_eq!(
        cli(&[
            "check".to_owned(),
            "--clone".to_owned(),
            ".".to_owned(),
            "extra".to_owned()
        ])
        .code,
        2
    );
}

#[test]
fn the_figure_pattern_is_the_spec_lints() {
    let r = repo("pattern");
    let re = figure_pattern(&r).unwrap();
    assert!(re.is_match("12 px").unwrap() && !re.is_match("12 pxs").unwrap());
    let none = super::super::tests::dir("nopattern");
    assert!(figure_pattern(&none).is_err());
    put(&none, "scripts/gates/l7r-gate.sh", "#!/bin/sh\necho '('\n");
    super::super::tests::sh(&none, "chmod +x scripts/gates/l7r-gate.sh");
    assert!(figure_pattern(&none).is_err());
}
