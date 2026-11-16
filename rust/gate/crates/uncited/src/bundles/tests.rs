//! The filter's bundles and its verdicts (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record).

use serde_json::json;

use super::*;
use crate::testkit::{long, W};

fn contracts(w: &W) -> Contracts {
    w.put(
        ".claude/agents/source-filter.md",
        "---\nname: source-filter\n---\n\n  The contract.\n",
    );
    w.put(
        "specs/312-uncited-source-catalog/writeup-contract.md",
        "# Write-ups\n",
    );
    Contracts {
        tree: w.root().to_path_buf(),
    }
}

#[test]
fn pages_split_into_parts_and_bundles() {
    assert_eq!(title_of("\n  \n  The title line  \nmore"), "The title line");
    assert_eq!(title_of(" \n"), "(no text)");
    assert_eq!(title_of(&"t".repeat(200)).chars().count(), 120);
    assert_eq!(split("a\nb\n", 0), ["a\nb\n"]);
    assert!(split("", 0).is_empty());
    // lines grouped up to the token limit
    assert_eq!(split("aaaa\nbbbb\ncccc\n", 2), ["aaaa\nbbbb\n", "cccc\n"]);
    // one enormous line cut in pieces, by tokens and by characters
    let parts = split(&"x".repeat(100), 10);
    assert_eq!(
        parts.iter().map(String::len).collect::<Vec<_>>(),
        [40, 40, 20]
    );
    let wide = "y".repeat(PART_CHARS + 10);
    assert_eq!(
        split(&wide, 1_000_000)
            .iter()
            .map(String::len)
            .collect::<Vec<_>>(),
        [PART_CHARS, 10]
    );
    let cjk = "日".repeat(30);
    assert_eq!(split(&cjk, 10).len(), 3);
    assert_eq!(
        split(&format!("{}\nshort\n", "z".repeat(PART_CHARS)), 1_000_000),
        ["z".repeat(PART_CHARS), "\nshort\n".to_owned()]
    );
    let pages = vec![
        ("a".to_owned(), "x".repeat(100_000)),
        ("b".to_owned(), "y".repeat(100_000)),
        ("big".to_owned(), "z".repeat(BUNDLE_CHARS + 1)),
        ("c".to_owned(), "日".repeat(BUNDLE_TOKENS + 1)),
        ("d".to_owned(), "w".to_owned()),
    ];
    let grouped = groups(pages);
    let g: Vec<Vec<&str>> = grouped
        .iter()
        .map(|b| b.iter().map(|(u, _)| u.as_str()).collect())
        .collect();
    assert_eq!(g, [vec!["a"], vec!["big"], vec!["c"], vec!["b", "d"]]);
    assert_eq!(
        (commas(0), commas(999), commas(1000), commas(1_234_567)),
        ("0".into(), "999".into(), "1,000".into(), "1,234,567".into())
    );
    assert_eq!(
        (padded(3, 4), padded(-2, 4), padded(12345, 4)),
        ("0003".into(), "-002".into(), "12345".into())
    );
}

#[test]
fn a_contract_without_its_frontmatter() {
    let w = W::new("bundles-contract");
    let c = contracts(&w);
    assert_eq!(c.body().unwrap(), "The contract.\n");
    w.put(".claude/agents/source-filter.md", "no frontmatter\n");
    assert_eq!(c.body().unwrap(), "no frontmatter\n");
    w.put(".claude/agents/source-filter.md", "---\nunclosed\n");
    assert_eq!(c.body().unwrap_err().kind, "IndexError");
    std::fs::remove_file(w.root().join(".claude/agents/source-filter.md")).unwrap();
    assert!(c.body().is_err());
}

#[test]
fn the_sets_pages_bundled_by_host() {
    let w = W::new("bundles-bundle");
    let c = contracts(&w);
    w.page("https://b.org/2", &long("Second page", 10), "fetch");
    w.page("https://a.org/1", &long("First page", 10000), "fetch");
    w.page("https://a.org/blank", "  \n", "fetch");
    let urls: Vec<String> = [
        "https://b.org/2",
        "https://a.org/1",
        "https://a.org/blank",
        "https://none.org/x",
    ]
    .iter()
    .map(|u| (*u).to_owned())
    .collect();
    let out = w.root().join("out");
    let dirs = bundle(w.root(), &urls, &out, 7, &c).unwrap();
    assert_eq!(dirs, [out.join("312-filter-0007")]);
    let d = &dirs[0];
    assert_eq!(
        std::fs::read_to_string(d.join("ids.json")).unwrap(),
        "{\n \"p00001\": \"https://a.org/1\",\n \"p00002\": \"https://b.org/2\"\n}"
    );
    let manifest = std::fs::read_to_string(d.join("MANIFEST.md")).unwrap();
    assert!(manifest.starts_with(&manifest_head("312-filter-0007", 2)));
    assert!(manifest.contains("## p00001\n\n- url: https://a.org/1\n- title: First page\n- size: 88,901 characters, about 22,225 tokens\n- files: p00001.part1.txt, p00001.part2.txt, p00001.part3.txt\n\n"), "{manifest}");
    assert!(manifest.ends_with("- files: p00002.txt\n\n"));
    assert_eq!(
        std::fs::read_to_string(d.join("CONTRACT.md")).unwrap(),
        "The contract.\n"
    );
    assert!(d.join("p00001.part3.txt").is_file() && d.join("p00002.txt").is_file());
    assert_eq!(
        bundle(w.root(), &["https://[bad/x".to_owned()], &out, 1, &c).unwrap(),
        Vec::<std::path::PathBuf>::new()
    );
    // a saved page whose URL will not split (written as the import once saved it: the cache's writer checks the host first)
    let bad = l7r_gate_research::pages::entry_dir(w.home(), "https://[bad/y");
    std::fs::create_dir_all(&bad).unwrap();
    std::fs::write(
        bad.join("meta.json"),
        r#"{"fetched": "2026-01-01T00:00:00+00:00"}"#,
    )
    .unwrap();
    std::fs::write(bad.join("text.txt"), "x").unwrap();
    assert_eq!(
        bundle(w.root(), &["https://[bad/y".to_owned()], &out, 1, &c)
            .unwrap_err()
            .kind,
        "ValueError"
    );
    w.page("http://[::1]/x", "text", "fetch");
    assert_eq!(
        bundle(w.root(), &["http://[::1]/x".to_owned()], &out, 1, &c)
            .unwrap()
            .len(),
        1
    );
    std::fs::write(
        w.root().join("out/312-filter-0020"),
        "a file where the bundle goes",
    )
    .unwrap();
    assert!(bundle(w.root(), &["https://b.org/2".to_owned()], &out, 20, &c).is_err());
}

fn verdicts(w: &W, ids: &serde_json::Value, lines: &[&str]) -> std::path::PathBuf {
    let d = w.root().join("out/b");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("ids.json"), ids.to_string()).unwrap();
    std::fs::write(d.join("verdicts.jsonl"), lines.join("\n")).unwrap();
    d
}

#[test]
fn the_verdicts_read_and_every_problem_named() {
    let w = W::new("bundles-verdicts");
    let ids = json!({"p1": "https://a.org/1", "p2": "https://a.org/2", "p3": "https://a.org/3", "p4": "https://a.org/4", "p5": "https://a.org/5"});
    let d = verdicts(&w, &ids, &[
        "not json at all, a line longer than eighty characters is cut at eighty when it is named as a problem here",
        "",
        r#"{"id": "p9"}"#,
        r#"{"id": 5}"#,
        r#"{"verdict": "KEEP"}"#,
        r#"{"id": "p1", "verdict": "MAYBE"}"#,
        r#"{"id": "p1"}"#,
        r#"{"id": "p2", "verdict": "NOT-KEPT"}"#,
        r#"{"id": "p2", "verdict": "NOT-KEPT", "reasons": "off-topic"}"#,
        r#"{"id": "p2", "verdict": "NOT-KEPT", "reasons": ["bogus"]}"#,
        r#"{"id": "p2", "verdict": "NOT-KEPT", "reasons": {"duplicate": 1}}"#,
        r#"{"id": "p3", "verdict": "KEEP"}"#,
        r#"{"id": "p3", "verdict": "NOT-KEPT", "reasons": ["duplicate"]}"#,
    ]);
    let (got, problems) = read_verdicts(&d).unwrap();
    assert_eq!(
        got.iter().map(|(k, _)| k.as_str()).collect::<Vec<_>>(),
        ["p2", "p3"]
    );
    assert_eq!(got[1].1["verdict"], "NOT-KEPT");
    assert_eq!(
        problems,
        [
            "not JSON: not json at all, a line longer than eighty characters is cut at eighty when it i",
            "'p9' is not an id of this bundle",
            "5 is not an id of this bundle",
            "'' is not an id of this bundle",
            "p1: verdict 'MAYBE'",
            "p1: verdict None",
            "p2: NOT-KEPT needs reasons from off-topic, modern-only, unreliable-kind, no-substance, duplicate, unreadable - got None",
            "p2: NOT-KEPT needs reasons from off-topic, modern-only, unreliable-kind, no-substance, duplicate, unreadable - got 'off-topic'",
            "p2: NOT-KEPT needs reasons from off-topic, modern-only, unreliable-kind, no-substance, duplicate, unreadable - got ['bogus']",
            "p1: no verdict",
            "p4: no verdict",
            "p5: no verdict",
        ]
    );
    let refused = apply(w.root(), &d, &mut String::new()).unwrap_err();
    assert!(
        refused
            .message
            .contains(": verdicts refused -\n  not JSON: "),
        "{}",
        refused.message
    );
    assert_eq!(score(&d, &json!({})).unwrap_err().kind, "ValueError");
    for (line, kind) in [
        (r#"{"id": ["x"]}"#, "TypeError"),
        ("[1]", "AttributeError"),
        (
            r#"{"id": "p1", "verdict": "NOT-KEPT", "reasons": 3}"#,
            "TypeError",
        ),
    ] {
        let d = verdicts(&w, &ids, &[line]);
        assert_eq!(read_verdicts(&d).unwrap_err().kind, kind, "{line}");
    }
    let d = verdicts(&w, &json!([1]), &[]);
    assert_eq!(read_verdicts(&d).unwrap_err().kind, "TypeError");
    std::fs::remove_file(d.join("verdicts.jsonl")).unwrap();
    std::fs::write(d.join("ids.json"), "{}").unwrap();
    assert_eq!(read_verdicts(&d).unwrap(), (vec![], vec![]));
}

#[test]
fn apply_writes_the_verdicts_and_score_counts_them() {
    let w = W::new("bundles-apply");
    let ids = json!({"p1": "https://a.org/1", "p2": "https://a.org/2", "p3": "https://a.org/3"});
    let note = "n".repeat(250);
    let p2 = json!({"id": "p2", "verdict": "NOT-KEPT", "reasons": ["off-topic"], "note": note, "propose_block": "spam.org"}).to_string();
    let d = verdicts(
        &w,
        &ids,
        &[
            r#"{"id": "p1", "verdict": "KEEP", "propose_block": ""}"#,
            &p2,
            r#"{"id": "p3", "verdict": "NOT-KEPT", "reasons": ["duplicate"], "note": null, "propose_block": "ads.org"}"#,
        ],
    );
    let mut out = String::new();
    assert_eq!(
        apply(w.root(), &d, &mut out).unwrap(),
        json!({"kept": 1, "not-kept": 2, "proposed": 2})
    );
    assert_eq!(
        out,
        "uncited: b proposes blocking ads.org - for the GM; only the GM adds a domain (FR-001)\nuncited: b proposes blocking spam.org - for the GM; only \
         the GM adds a domain (FR-001)\n"
    );
    let nk = w.read(crate::NOT_KEPT);
    assert!(
        nk.contains(&format!("\"note\": \"{}\"", "n".repeat(200)))
            && nk.contains("\"note\": \"\", \"basis\": \"source-filter\"")
    );
    assert!(w
        .read(KEPT)
        .contains("\"raw\": \"https://a.org/1\", \"basis\": \"source-filter\""));
    assert_eq!(
        score(&d, &json!({"p1": "KEEP", "p2": "KEEP", "p3": "NOT-KEPT"})).unwrap(),
        json!({"KEEP": {"agreed": 1, "total": 2}, "NOT-KEPT": {"agreed": 1, "total": 1}})
    );
    assert_eq!(
        score(&d, &json!({"p1": "MAYBE"})).unwrap_err().message,
        "'MAYBE'"
    );
    assert_eq!(
        score(&d, &json!({"p9": "KEEP"})).unwrap_err().message,
        "'p9'"
    );
    assert_eq!(
        score(&d, &json!([])).unwrap_err().message,
        "'list' object has no attribute 'items'"
    );
    let d = verdicts(
        &w,
        &json!({"p1": "https://grokipedia.com/x"}),
        &[r#"{"id": "p1", "verdict": "KEEP"}"#],
    );
    assert_eq!(
        apply(w.root(), &d, &mut String::new()).unwrap_err().kind,
        "Blocked"
    );
}

#[test]
fn the_drafts_of_the_kept_pages_with_no_entry() {
    let w = W::new("bundles-draft");
    let c = contracts(&w);
    let kept: Vec<serde_json::Value> = (1..=17)
        .map(|i| json!({"url": format!("k.org/{i}"), "raw": format!("https://k.org/{i}")}))
        .chain([
            json!({"url": "k.org/none", "raw": "https://k.org/none"}),
            json!({"url": "w.org/done", "raw": "https://w.org/done"}),
        ])
        .collect();
    w.lines(KEPT, &kept);
    for i in 1..=17 {
        w.page(
            &format!("https://k.org/{i}"),
            &format!("Page {i}\n"),
            "fetch",
        );
    }
    w.uncited("0100-done.html", "<p>https://w.org/done</p>");
    let out = w.root().join("out");
    let dirs = draft_bundles(w.root(), &out, 2, &c).unwrap();
    assert_eq!(
        dirs,
        [out.join("312-draft-0002"), out.join("312-draft-0003")]
    );
    let manifest = std::fs::read_to_string(dirs[0].join("MANIFEST.md")).unwrap();
    assert!(manifest.starts_with(&draft_head("312-draft-0002", 15)));
    assert!(manifest
        .ends_with("## Keys already taken - choose none of these\n\ndone grok l7r-notes src-a\n"),);
    let contract = std::fs::read_to_string(dirs[0].join("CONTRACT.md")).unwrap();
    assert!(contract.starts_with("# Write-ups\n<!-- ") && contract.ends_with("-->\n"),);
    assert!(std::fs::read_to_string(dirs[1].join("ids.json"))
        .unwrap()
        .contains("\"p00016\""));
    std::fs::remove_file(
        w.root()
            .join("specs/312-uncited-source-catalog/writeup-contract.md"),
    )
    .unwrap();
    assert!(draft_bundles(w.root(), &out, 1, &c).is_err());
    w.lines(KEPT, &[json!({"raw": "x"})]);
    assert!(draft_bundles(w.root(), &out, 1, &c).is_err());
    assert!(vocabulary_block(w.root())
        .unwrap()
        .contains("period=modern"));
}
