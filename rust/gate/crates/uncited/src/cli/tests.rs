//! `l7r-gate record uncited ...` (feature 449 T147): each subcommand's lines and refusals through [`cli_with`], on the tests' world.

use l7r_gate_archive::testkit::Fake;
use serde_json::json;

use super::{cli_with, Reach};
use crate::testkit::{long, reserve, starter, Said, W};
use crate::Reply;

fn fake() -> Fake {
    let mut f = Fake::default();
    f.serve(
        "https://a.org/live",
        200,
        "text/plain",
        long("a live page", 200).as_bytes(),
    );
    f
}

fn run(w: &W, args: &[&str]) -> (Reply, Vec<String>) {
    let said = Said::default();
    let start = starter(fake);
    let say = |l: &str| said.say(l);
    let reach = Reach {
        start: &start,
        say: &say,
        reserve: &reserve,
        tree: w.root().to_path_buf(),
    };
    let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    let reply = cli_with(&args, w.root(), &reach);
    (reply, said.all())
}

fn ok(w: &W, args: &[&str]) -> String {
    let (r, _) = run(w, args);
    assert_eq!(r.code, 0, "{args:?}: {}", r.stderr);
    r.stdout
}

#[test]
fn the_refusals_argparse_gave() {
    let w = W::new("cli-refusals");
    for (args, said) in [
        (&[][..], "the following arguments are required: cmd"),
        (&["nope"], "argument cmd: invalid choice: 'nope'"),
        (&["bundle"], "the following arguments are required: out"),
        (&["apply"], "the following arguments are required: dirs"),
        (
            &["score", "d"],
            "the following arguments are required: dir, answers",
        ),
        (&["cite"], "the following arguments are required: key"),
        (
            &["merge", "k"],
            "the following arguments are required: key, into",
        ),
        (
            &["unkeep", "a", "b"],
            "the following arguments are required: url, reasons, note",
        ),
        (&["requeue"], "the following arguments are required: url"),
        (
            &["retire-cited"],
            "the following arguments are required: key, access, note",
        ),
        (
            &["stands", "u"],
            "the following arguments are required: url, note",
        ),
        (
            &["fetch", "--limit", "x"],
            "argument --limit: invalid int value: 'x'",
        ),
        (&["set", "extra"], "unrecognized arguments: extra"),
        (&["dedupe", "--nope"], "unrecognized arguments: --nope"),
    ] {
        let (r, _) = run(&w, args);
        assert_eq!((r.code, r.stdout.as_str()), (2, ""), "{args:?}");
        assert_eq!(
            r.stderr,
            format!("l7r-gate record uncited: error: {said}\n"),
        );
    }
}

#[test]
fn the_set_the_rule_the_report_and_the_fetch() {
    let w = W::new("cli-set");
    w.ledger(&[
        json!({"url": "a.org/live", "raw": "https://a.org/live"}),
        json!({"url": "a.org/search?q=1", "raw": "https://a.org/search?q=1"}),
    ]);
    assert_eq!(
        ok(&w, &["set", "--write", "out.txt"]),
        "uncited: 2 page(s) in the set\n"
    );
    assert_eq!(
        w.read("out.txt"),
        "https://a.org/live\nhttps://a.org/search?q=1\n"
    );
    assert_eq!(ok(&w, &["set"]), "uncited: 2 page(s) in the set\n");
    let (r, said) = run(&w, &["fetch", "--workers", "2", "--limit", "5"]);
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (
            0,
            "uncited: {\"read\": 1, \"unreadable\": 0, \"error\": 0}\n"
        )
    );
    assert_eq!(
        said,
        [
            "uncited: fetching 1 page(s) in up to 2 lane(s)",
            "read                   https://a.org/live"
        ]
    );
    let (_, said) = run(&w, &["fetch"]);
    assert_eq!(said, ["uncited: fetching 0 page(s) in up to 4 lane(s)"]);
    assert_eq!(
        ok(&w, &["rule"]),
        "uncited: the rule - {\"no-substance\": 1, \"duplicate\": 0}\n"
    );
    assert!(ok(&w, &["report"]).starts_with("uncited: 1 page(s) not yet judged (1 with saved text); 0 kept, 1 not kept (no-substance 1); "));
    let (r, _) = run(&w, &["set", "--write", "no/such/dir/x"]);
    assert_eq!((r.code, r.stdout.as_str()), (1, ""));
    assert!(r.stderr.starts_with("FileNotFoundError: "), "{}", r.stderr);
}

#[test]
fn the_bundles_and_the_verdicts() {
    let w = W::new("cli-bundles");
    w.put(".claude/agents/source-filter.md", "the contract\n");
    w.put(
        "specs/312-uncited-source-catalog/writeup-contract.md",
        "# Write-ups\n",
    );
    w.ledger(&[
        json!({"url": "a.org/1", "raw": "https://a.org/1"}),
        json!({"url": "a.org/2", "raw": "https://a.org/2"}),
    ]);
    w.page("https://a.org/1", "page one", "fetch");
    w.page("https://a.org/2", "page two", "fetch");
    assert_eq!(
        ok(&w, &["bundle", "b", "--limit", "1", "--start", "3"]),
        "uncited: 1 bundle(s) under b\n"
    );
    assert_eq!(
        w.read("b/312-filter-0003/ids.json"),
        "{\n \"p00001\": \"https://a.org/1\"\n}"
    );
    assert_eq!(ok(&w, &["bundle", "b2"]), "uncited: 1 bundle(s) under b2\n");
    std::fs::write(
        w.root().join("b/312-filter-0003/verdicts.jsonl"),
        r#"{"id": "p00001", "verdict": "KEEP"}"#,
    )
    .unwrap();
    w.put("labels.json", r#"{"p00001": "KEEP"}"#);
    assert_eq!(
        ok(&w, &["score", "b/312-filter-0003", "labels.json"]),
        "{\"KEEP\": {\"agreed\": 1, \"total\": 1}, \"NOT-KEPT\": {\"agreed\": 0, \"total\": 0}}\n"
    );
    assert_eq!(
        ok(&w, &["apply", "b/312-filter-0003"]),
        "uncited: b/312-filter-0003 - {\"kept\": 1, \"not-kept\": 0, \"proposed\": 0}\n"
    );
    // a page kept twice: the draft's dedupe retires it first
    let mut kept = w.read(crate::KEPT);
    kept.push_str("{\"url\": \"z.org/dup\", \"raw\": \"https://z.org/dup\"}\n{\"url\": \"z.org/dup\", \"raw\": \"https://z.org/dup\"}\n");
    w.put(crate::KEPT, &kept);
    assert_eq!(
        ok(&w, &["draft", "d", "--start", "2"]),
        "uncited: 1 duplicate(s) retired first; 1 draft bundle(s) under d\n"
    );
    let d = w.root().join("d/312-draft-0002");
    std::fs::write(
        d.join("entries.jsonl"),
        json!({"id": "p00001", "key": "new-key", "citation": "(https://a.org/1)", "what": "w", "why": "y", "tags": "period=modern; region=japan; kind=book"})
            .to_string()
            + "\nnot json\n",
    )
    .unwrap();
    let (r, _) = run(&w, &["install", "d/312-draft-0002"]);
    assert_eq!(r.stdout, "uncited: d/312-draft-0002 - {\"written\": 1, \"refused\": 1, \"already\": 0, \"dropped\": 0}\n");
    assert!(
        r.stderr.starts_with("uncited: 312-draft-0002: refused - "),
        "{}",
        r.stderr
    );
    let (r, _) = run(&w, &["apply", "b/312-filter-0003", "b2/312-filter-0001"]);
    assert_eq!(r.code, 1);
    assert!(
        r.stdout.starts_with("uncited: b/312-filter-0003 - ")
            && r.stderr.starts_with("ValueError: "),
        "{}",
        r.stderr
    );
    let (r, _) = run(&w, &["install", "nope"]);
    assert_eq!(
        (r.code, r.stderr.split(':').next()),
        (1, Some("FileNotFoundError"))
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "each entry command and the imported copies, one after another on one world"
)]
fn the_entries_and_the_imported_copies() {
    let w = W::new("cli-entries");
    w.put(
        "research/source-access.json",
        r#"{"states": [{"id": "gone"}], "recorded": {}}"#,
    );
    w.lines(
        crate::KEPT,
        &[
            json!({"url": "k.org/1", "raw": "https://k.org/1"}),
            json!({"url": "k.org/2", "raw": "https://k.org/2"}),
            json!({"url": "k.org/3", "raw": "https://k.org/3"}),
        ],
    );
    w.uncited("0100-k1.html", "<p>https://k.org/1</p>\n<!-- tags: a -->\n");
    w.uncited("0110-k2.html", "<p>https://k.org/2</p>");
    w.put(
        "research/sources/010-works-cited/0500-dead.html",
        "<p>https://dead.org/x</p>",
    );
    assert_eq!(
        ok(&w, &["cite", "k1"]),
        "uncited: k1 moved to research/sources/010-works-cited/0100-k1.html - write its Used for: line (the build refuses the placeholder), \
         then `git add -A` the move\n"
    );
    assert_eq!(ok(&w, &["merge", "k2", "src-a"]), "uncited: k2 retired (0110-k2.html) as a duplicate of src-a; its page is on the not-kept list\n");
    assert_eq!(
        ok(
            &w,
            &["unkeep", "https://k.org/3", "duplicate,off-topic", "why"]
        ),
        "uncited: https://k.org/3 moved to the not-kept list (duplicate,off-topic)\n"
    );
    w.uncited("0120-k4.html", "<p>https://k.org/4</p>");
    w.lines(
        crate::KEPT,
        &[json!({"url": "k.org/4", "raw": "https://k.org/4"})],
    );
    assert_eq!(
        ok(&w, &["requeue", "https://k.org/4"]),
        "uncited: https://k.org/4 requeued - its verdict cleared, its entry k4 retired; `make uncited DO=bundle` judges it again\n"
    );
    assert_eq!(ok(&w, &["requeue", "https://k.org/3"]), "uncited: https://k.org/3 requeued - its verdict cleared; `make uncited DO=bundle` judges it again\n");
    assert_eq!(
        ok(&w, &["retire-cited", "dead", "gone", "read: it is gone"]),
        "uncited: dead left the works cited (0500-dead.html removed), not kept as unreadable (gone), its state recorded\n"
    );
    assert_eq!(
        ok(&w, &["stands", "https://k.org/9", "it stands"]),
        "uncited: https://k.org/9 - its verdict stands (it stands)\n"
    );
    assert_eq!(
        ok(&w, &["copy-verdicts"]),
        "\nuncited: 0 verdict(s) blame a saved copy on a page now read live - read each; requeue a readable one with `make uncited DO=requeue \
         URL=<u>`, or `make uncited DO=stands URL=<u> NOTE=<why>`\n"
    );
    assert_eq!(
        ok(&w, &["dedupe", "--dry"]),
        "\nuncited: 0 duplicate(s) would be retired, 0 similar pair(s) to read\n"
    );
    w.page("https://h.org/k", "x", "fetch");
    w.put(
        "research/sources/010-works-cited/0600-h.html",
        "<p>https://h.org/k?x</p>",
    );
    w.lines(
        crate::KEPT,
        &[
            json!({"url": "h.org/k?x", "raw": "https://h.org/k?x"}),
            json!({"url": "h.org/k?x", "raw": "https://h.org/k?y"}),
        ],
    );
    assert_eq!(
        ok(&w, &["dedupe"]),
        "uncited: duplicate retired - https://h.org/k?x -> h\nuncited: duplicate retired - https://h.org/k?y -> h\nuncited: 2 duplicate(s) retired, 0 similar pair(s) to read\n"
    );
    // a pair only similar, listed to read and never retired
    let nav = "Site navigation: home about contact search\n";
    let body: String = format!(
        "{nav}alpha\n{}\n",
        (0..400)
            .map(|i| format!("alpha{i}"))
            .collect::<Vec<_>>()
            .join(" ")
    );
    let near: String = body
        .split(' ')
        .enumerate()
        .map(|(i, x)| {
            if i % 30 == 0 {
                format!("zq{i}xw")
            } else {
                x.to_owned()
            }
        })
        .collect::<Vec<_>>()
        .join(" ");
    w.put(
        "research/sources/010-works-cited/0700-s-cited.html",
        "<p>https://s.org/c1</p>",
    );
    w.page("https://s.org/c1", &body, "fetch");
    w.page("https://s.org/k", &near, "fetch");
    w.lines(
        crate::KEPT,
        &[json!({"url": "s.org/k", "raw": "https://s.org/k"})],
    );
    let shown = ok(&w, &["dedupe", "--dry"]);
    assert!(shown
        .starts_with("uncited: to read - https://s.org/k ~ s-cited (similar 0.91 - read both;"));
    assert!(
        shown.ends_with("\nuncited: 0 duplicate(s) would be retired, 1 similar pair(s) to read\n")
    );
    let (r, _) = run(&w, &["cite", "src-a"]);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            1,
            "ValueError: no uncited entry for 'src-a' in research/sources/040-uncited-works\n"
        )
    );
    // verify: one imported copy read live, then a sample of judged pages
    w.page(
        "https://a.org/live",
        "an imported copy of the page, word0 word1",
        "import-288",
    );
    w.lines(
        crate::KEPT,
        &[
            json!({"url": "a.org/live", "raw": "https://a.org/live"}),
            json!({"url": "a.org/live", "raw": "https://a.org/live"}),
        ],
    );
    w.lines(
        crate::NOT_KEPT,
        &[
            json!({"url": "a.org/x", "raw": "https://a.org/x", "basis": "source-filter"}),
            json!({"url": "a.org/y", "raw": "https://a.org/y", "basis": "rule"}),
        ],
    );
    let (r, said) = run(
        &w,
        &["verify", "--sample", "5", "--limit", "3", "--workers", "1"],
    );
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (
            0,
            "uncited: {\"same\": 0, \"misfiled\": 1, \"unread\": 0}\n"
        ),
    );
    assert_eq!(
        said,
        [
            "uncited: verifying 1 imported cop(ies) in up to 1 lane(s)",
            "misfiled   https://a.org/live"
        ]
    );
    let (r, said) = run(&w, &["verify", "--all-imported"]);
    assert_eq!(r.code, 0);
    assert_eq!(
        said[0],
        "uncited: verifying 0 imported cop(ies) in up to 3 lane(s)"
    );
    let (r, _) = run(&w, &["verify", "--sample", "-1"]);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            1,
            "ValueError: Sample larger than population or is negative\n"
        )
    );
}

#[test]
fn a_cited_entry_outside_the_root_is_refused() {
    // the record's base moved away from the root (`L7R_ATTEMPTS_ROOT`, the tests' seam): the path is not under the root
    let e = super::relative(std::path::Path::new("/a/b"), std::path::Path::new("/c")).unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        ("ValueError", "'/a/b' is not in the subpath of '/c'")
    );
}
