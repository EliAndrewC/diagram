//! The budget and review check over a fixture corpus (451 T170): an unreviewed change fires, a reviewed or baselined one passes, a
//! fixture's paths, ids and numbers do not move a key.

use std::path::Path;

use serde_json::json;

use super::{cli, corpus, record, NOTICE_BUDGET, REFUSE_BUDGET};
use crate::shared::tempdir::TempDir;

fn put(dir: &Path, name: &str, lines: &[(&str, &str, String)]) {
    std::fs::create_dir_all(dir).unwrap();
    let text: String = lines
        .iter()
        .map(|(g, k, t)| {
            json!({"guard": g, "kind": k, "event": "PreToolUse", "text": t}).to_string() + "\n"
        })
        .collect();
    std::fs::write(dir.join(name), text).unwrap();
}

fn run(args: &[&str]) -> crate::protocol::Reply {
    cli(&args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>())
}

#[test]
fn a_fixtures_paths_ids_and_numbers_do_not_move_a_wording_and_its_longest_rendering_is_kept() {
    let d = TempDir::new("messages-corpus");
    let c = d.join("c");
    put(
        &c,
        "a.jsonl",
        &[
            ("g-hooks", "refuse", "BLOCKED: /tmp/tmp.Ab3/x.log is 12 s old, pid 4005496, \x1b[1mdeadbeef12\x1b[0m".to_owned()),
            ("g-hooks", "refuse", "BLOCKED:  /home/agent/.claude/jobs/c6/tmp/long-name.log is 3 s old, pid 7, cafe0123".to_owned()),
            ("g-hooks", "notice", "BLOCKED: /tmp/x is 1 s old, pid 1, abcdef0".to_owned()),
            ("g-hooks", "notice", "   ".to_owned()),
        ],
    );
    std::fs::write(c.join("b.jsonl"), "not json\n").unwrap();
    std::fs::write(c.join("ignored.txt"), "{}").unwrap();
    let got = corpus(&c);
    assert_eq!(got.len(), 2, "{got:?}");
    let refuse = got.values().find(|m| m.kind == "refuse").unwrap();
    assert!(refuse.text.contains("long-name.log"));
    assert_eq!(refuse.chars, refuse.text.chars().count());
    assert!(corpus(&d.join("none")).is_empty());
    // the record's head is the wording as keyed: a suite's temporary paths, pids and ids never reach it
    let rec = d.join("r.tsv");
    let (cs, rs) = (
        c.to_string_lossy().into_owned(),
        rec.to_string_lossy().into_owned(),
    );
    assert_eq!(run(&["baseline", &cs, &rs, "x"]).code, 0);
    let heads: Vec<String> = record(&rec).into_values().map(|r| r.head).collect();
    assert_eq!(heads, ["BLOCKED: <path> is N s old, pid N, N"; 2]);
    // ...and never ends inside a code span, which would pair with the next row's backticks
    let c2 = d.join("c2");
    put(
        &c2,
        "a.jsonl",
        &[(
            "g-hooks",
            "refuse",
            "BLOCKED: one two three four five six seven eight nine ten `make x` now".to_owned(),
        )],
    );
    let rec2 = d.join("r2.tsv");
    assert_eq!(
        run(&[
            "baseline",
            &c2.to_string_lossy(),
            &rec2.to_string_lossy(),
            "x"
        ])
        .code,
        0
    );
    let cut: Vec<String> = record(&rec2).into_values().map(|r| r.head).collect();
    assert_eq!(
        cut,
        ["BLOCKED: one two three four five six seven eight nine ten"]
    );
}

#[test]
fn an_unreviewed_change_fires_and_a_reviewed_or_baselined_wording_passes() {
    let d = TempDir::new("messages-check");
    let (c, rec) = (d.join("c"), d.join("guard-messages.tsv"));
    let (cs, rs) = (
        c.to_string_lossy().into_owned(),
        rec.to_string_lossy().into_owned(),
    );
    // nothing rendered is a failure, never a pass
    let none = run(&["check", &cs, &rs]);
    assert!(none.code == 1 && none.stderr.contains("HOOKS_ALL=1"));
    put(
        &c,
        "s.jsonl",
        &[("g-hooks", "refuse", "BLOCKED: no. Fix: make x".to_owned())],
    );
    assert!(run(&["baseline", &cs, &rs, "before T170"])
        .stdout
        .contains("1 wordings baselined"));
    let rows = record(&rec);
    let (k0, r0) = rows.iter().next().unwrap();
    assert!(
        r0.verdict == "BASELINE"
            && r0.by == "unreviewed - before T170"
            && r0.head == "BLOCKED: no. Fix: make x"
    );
    assert_eq!(run(&["check", &cs, &rs]).code, 0);
    // a second baseline is refused: a later wording is reviewed
    assert!(run(&["baseline", &cs, &rs, "again"])
        .stderr
        .contains("already holds the baseline"));
    // THE PROOF: the same guard's message changed, with no recorded PASS, fails, printing the message, its length, budget and fix
    put(
        &c,
        "s.jsonl",
        &[(
            "g-hooks",
            "refuse",
            "BLOCKED: no, not that. Fix: make x".to_owned(),
        )],
    );
    let changed = run(&["check", &cs, &rs]);
    assert_eq!(changed.code, 1);
    assert!(
        changed
            .stderr
            .contains("GUARD MESSAGE NEW OR CHANGED, NOT REVIEWED: g-hooks refuse")
            && changed
                .stderr
                .contains("  | BLOCKED: no, not that. Fix: make x")
            && changed
                .stderr
                .contains(&format!("34 characters, budget {REFUSE_BUDGET}"))
            && changed.stderr.contains("make guard-messages KEY=")
            && changed.stderr.contains("1 of 1 wordings"),
        "{}",
        changed.stderr
    );
    // the owed bundle names the unit and the wording it replaced
    let bundle = d.join("bundle.md");
    let owed = run(&["owed", &cs, &rs, &bundle.to_string_lossy()]);
    assert!(owed.stdout.contains("message-check:") && owed.stdout.contains("1 unit(s)"));
    let b = std::fs::read_to_string(&bundle).unwrap();
    assert!(b.contains("BLOCKED: no, not that.") && b.contains("- BLOCKED: no. Fix: make x"));
    assert!(run(&[
        "owed",
        &cs,
        &rs,
        &d.join("no/such/dir/b.md").to_string_lossy()
    ])
    .stderr
    .contains("cannot write"));
    let k = owed
        .stdout
        .split(['\n', ' '])
        .find_map(|w| w.strip_prefix("message-check:"))
        .unwrap()
        .to_owned();
    assert_ne!(&k, k0);
    // a FAIL stays a failure; a PASS passes
    assert!(run(&["verdict", &cs, &rs, &k, "FAIL", "agent-1"])
        .stdout
        .contains("recorded FAIL"));
    assert!(run(&["check", &cs, &rs])
        .stderr
        .contains("FAILED ITS REVIEW"));
    assert!(run(&["verdict", &cs, &rs, &k, "PASS", " "])
        .stderr
        .contains("BY= names"));
    assert!(run(&["verdict", &cs, &rs, "0000", "PASS", "a"])
        .stderr
        .contains("no message rendered has key 0000"));
    assert_eq!(run(&["verdict", &cs, &rs, &k, "PASS", "agent-2"]).code, 0);
    let ok = run(&["check", &cs, &rs]);
    assert!(
        ok.code == 0 && ok.stdout.contains("1 wordings"),
        "{}",
        ok.stderr
    );
    assert_eq!(
        run(&["owed", &cs, &rs, &bundle.to_string_lossy()]).stdout,
        "guard-messages: nothing owed\n"
    );
}

#[test]
fn past_its_budget_a_wording_passes_only_on_a_review_that_ruled_every_word_needed() {
    let d = TempDir::new("messages-budget");
    let (c, rec) = (d.join("c"), d.join("r.tsv"));
    let (cs, rs) = (
        c.to_string_lossy().into_owned(),
        rec.to_string_lossy().into_owned(),
    );
    let long = "word ".repeat(NOTICE_BUDGET / 5 + 1);
    put(&c, "s.jsonl", &[("g-hooks", "notice", long.clone())]);
    let new = run(&["check", &cs, &rs]);
    assert!(
        new.stderr.contains("NEW OR CHANGED AND OVER BUDGET")
            && new.stderr.contains(&format!("budget {NOTICE_BUDGET}"))
    );
    let k = super::key("g-hooks", "notice", long.trim());
    assert_eq!(run(&["verdict", &cs, &rs, &k, "PASS", "agent-3"]).code, 0);
    assert!(run(&["check", &cs, &rs])
        .stderr
        .contains("OVER BUDGET: g-hooks notice"));
    assert_eq!(
        run(&[
            "verdict",
            &cs,
            &rs,
            &k,
            "PASS",
            "agent-3",
            "a list of every step"
        ])
        .code,
        0
    );
    assert_eq!(run(&["check", &cs, &rs]).code, 0);
    assert_eq!(record(&rec)[&k].over, "a list of every step");
    // a record that cannot be written is said; a short or extra column row is not a row
    std::fs::write(&rec, "key\tverdict\nshort\trow\n").unwrap();
    assert!(record(&rec).is_empty());
    let dir_rec = d.join("a-dir");
    std::fs::create_dir_all(&dir_rec).unwrap();
    assert!(run(&["baseline", &cs, &dir_rec.to_string_lossy(), "why"])
        .stderr
        .contains("cannot write"));
    let bads: [&[&str]; 5] = [
        &["check"],
        &["check", &cs],
        &["nope", &cs, &rs],
        &["verdict", &cs, &rs, &k, "MAYBE", "a"],
        &["check", &cs, &rs, "extra"],
    ];
    for bad in bads {
        assert_eq!(run(bad).code, 64, "{bad:?}");
    }
}

/// 451 T170, MODE 4's N3: a message that grows with a list is held at its worst case, many items, not at the few its suite renders -
/// static-runs' refusal reached builders at 7,909 characters over 25 crates while its suite rendered 738. Each is within its kind's
/// budget, shows few of its many items, and keeps its fix command and escape.
#[test]
fn every_list_growing_message_at_its_worst_case_is_within_its_budget() {
    let d = TempDir::new("messages-worst");
    let crates: Vec<String> = (1..=super::worst::MANY)
        .map(|i| format!("rust/gate/crates/crate_{i:02}"))
        .collect();
    let said = super::worst::worst(&crates, &d);
    assert_eq!(said.len(), 8);
    for (m, keyed) in &said {
        let budget = if m.kind == "notice" {
            NOTICE_BUDGET
        } else {
            REFUSE_BUDGET
        };
        let (n, text) = (m.chars, &m.text);
        assert!(n <= budget, "{n}: {text}");
        assert_eq!(m.chars, m.text.chars().count());
        if m.guard == "static-runs-hooks" {
            assert!(m.text.contains("crate_40\"\n") && m.text.contains("STATIC_OK"));
            assert!(keyed.contains("CRATE=\"rust/a rust/b rust/c\""));
        } else {
            assert!(m.text.contains(" more: `"), "{}", m.text);
            assert_eq!(&m.text, keyed);
        }
    }
}

/// The check holds the worst cases of the tree holding its record - static-runs' over every crate it has - and none outside a repository.
#[test]
fn the_worst_cases_are_checked_in_the_tree_holding_the_record() {
    let d = TempDir::new("messages-tree");
    let git = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&*d)
            .args(args)
            .status()
            .unwrap()
            .success());
    };
    git(&["init", "-q"]);
    std::fs::create_dir_all(d.join("rust/x/src")).unwrap();
    std::fs::write(d.join("rust/x/Cargo.toml"), "[package]\nname = \"x\"\n").unwrap();
    std::fs::write(d.join("rust/x/src/lib.rs"), "").unwrap();
    git(&["add", "."]);
    std::fs::create_dir_all(d.join("dev")).unwrap();
    let (c, r) = (d.join("c"), d.join("dev/guard-messages.tsv"));
    std::fs::create_dir_all(&c).unwrap();
    let (c, r) = (
        c.to_string_lossy().into_owned(),
        r.to_string_lossy().into_owned(),
    );
    let first = run(&["check", &c, &r]);
    assert_eq!(first.code, 1);
    assert!(
        first.stderr.contains("make crate-checks CRATE=\"rust/x\"")
            && first.stderr.contains("8 of 8 wordings"),
        "{}",
        first.stderr
    );
    assert_eq!(run(&["baseline", &c, &r, "a fixture"]).code, 0);
    assert_eq!(run(&["check", &c, &r]).code, 0);
}

/// A stored head names no path (451 T170, at its landing): record-edit's notice rendered with its fixture's edited path, a built
/// page, put a research pointer in the record that the gate's pointer check refused. The key leaves a relative path in the wording,
/// so two such messages keep their two keys; the record's head masks it, and `rehead` re-masks a record written before.
#[test]
fn a_stored_head_masks_a_relative_path_and_its_key_does_not_move() {
    let d = TempDir::new("messages-head-path");
    let (c, rec) = (d.join("c"), d.join("guard-messages.tsv"));
    let (cs, rs) = (
        c.to_string_lossy().into_owned(),
        rec.to_string_lossy().into_owned(),
    );
    // the built page's path assembled, so this file carries no pointer of its own
    let page = concat!("research", "/fields.html");
    put(
        &c,
        "s.jsonl",
        &[
            (
                "g-hooks",
                "notice",
                format!("{page} is assembled from `research/questions/`, never hand-edited"),
            ),
            (
                "g-hooks",
                "notice",
                "docs/usage.md is assembled from `research/questions/`, never hand-edited"
                    .to_owned(),
            ),
            (
                "g-hooks",
                "refuse",
                "BLOCKED: N/N passed, PASS/FAIL, see https://x.org/a/b and ~/.claude/x".to_owned(),
            ),
        ],
    );
    assert_eq!(run(&["baseline", &cs, &rs, "x"]).code, 0);
    let rows = record(&rec);
    let heads: Vec<&str> = rows.values().map(|r| r.head.as_str()).collect();
    assert_eq!(rows.len(), 3, "a relative path stays in the key: {heads:?}");
    let masked = "<path> is assembled from `<path>`, never hand-edited";
    let words = "BLOCKED: N/N passed, PASS/FAIL, see https:/<path> and <path>";
    let (n, kept) = (
        heads.iter().filter(|h| **h == masked).count(),
        heads.contains(&words),
    );
    assert!(n == 2 && kept, "{heads:?}");
    assert!(!std::fs::read_to_string(&rec).unwrap().contains(page));
    // a record written before the mask: `rehead` re-masks its heads and moves no other column
    let text = std::fs::read_to_string(&rec).unwrap();
    let old = text.replacen("<path> is assembled", &format!("{page} is assembled"), 1);
    std::fs::write(&rec, &old).unwrap();
    let said = run(&["rehead", &cs, &rs]);
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (0, "guard-messages: 3 heads written, their paths masked\n")
    );
    let now = std::fs::read_to_string(&rec).unwrap();
    assert_eq!(now, text);
    let cut = |t: &str| {
        t.lines()
            .map(|l| l.rsplit_once('\t').unwrap().0.to_owned())
            .collect::<Vec<_>>()
    };
    assert_eq!(cut(&now), cut(&old));
}
