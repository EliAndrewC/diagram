//! Source tags and the works sections (feature 449 T144; each expected value `source_tags.py`'s on the same record, 2026-11-16).

use std::collections::BTreeSet;

use super::{
    contract_block, home, kind_heading, labels_html, load_sections, load_vocabulary, parse,
    section_heading, strip_marker, synced_contract, takes, Catalog, CONTRACT_CLOSE, CONTRACT_OPEN,
};
use crate::fixture::{put, record};

/// Each broken file and the refusal the Python gave; a "not JSON (" refusal quotes the parser.
const CASES: &[(&str, Option<&str>, &str)] = &[
    ("source-tags.json", None, "SourceTagError: source-tags.json: missing - the record's source vocabulary is a file, and the build will not invent it"),
    ("source-tags.json", Some("x"), "SourceTagError: source-tags.json: not JSON ("),
    ("source-tags.json", Some("{\"period\": []}"), "SourceTagError: source-tags.json: holds exactly period, region, kind and canon"),
    ("source-tags.json", Some("{\"period\": [], \"region\": [], \"kind\": [], \"canon\": {}}"), "SourceTagError: source-tags.json: `period` is a non-empty list, in the order its labels show"),
    ("source-tags.json", Some("{\"period\": [{\"id\": \"A\"}], \"region\": [], \"kind\": [], \"canon\": {}}"), "SourceTagError: source-tags.json period: a value is an object with a lower-case `id`, a `name` and a `description`"),
    ("source-tags.json", Some("{\"period\": [{\"id\": \"a\", \"name\": \"A\", \"description\": \"d\"}, {\"id\": \"a\", \"name\": \"A\", \"description\": \"d\"}], \"region\": [{\"id\": \"r\", \"name\": \"R\", \"description\": \"d\"}], \"kind\": [{\"id\": \"k\", \"name\": \"K\", \"description\": \"d\"}], \"canon\": {\"id\": \"c\", \"name\": \"C\", \"description\": \"d\"}}"), "SourceTagError: source-tags.json: a period value is declared twice"),
    ("source-tags.json", Some("{\"period\": [{\"id\": \"a\", \"name\": \"A\", \"description\": \"d\"}], \"region\": [{\"id\": \"r\", \"name\": \"R\", \"description\": \"d\"}], \"kind\": [{\"id\": \"k\", \"name\": \"K\", \"description\": \"d\"}], \"canon\": {\"id\": \"c\"}}"), "SourceTagError: source-tags.json canon: a value is an object with a lower-case `id`, a `name` and a `description`"),
    ("source-sections.json", None, "SourceTagError: source-sections.json: missing - the record's source sections is a file, and the build will not invent it"),
    ("source-sections.json", Some("{}"), "SourceTagError: source-sections.json: an object with a `sections` list"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"x\"}]}"), "SourceTagError: source-sections.json: a section is an object with a lower-case `id` starting `works-`"),
    ("source-sections.json", Some("{\"sections\": [\"x\"]}"), "SourceTagError: source-sections.json: a section is an object with a lower-case `id` starting `works-`"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"canon\": true}, {\"id\": \"works-a\", \"title\": \"A\"}]}"), "SourceTagError: source-sections.json section `works-a`: the id is used twice"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\"}]}"), "SourceTagError: source-sections.json section `works-a`: no `title`"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"canon\": true, \"takes\": [{\"kind\": \"book\"}]}]}"), "SourceTagError: source-sections.json section `works-a`: a section takes works by clauses, or is the canon section with none - not both, not neither"),
    ("source-sections.json", Some("{\"sections\": []}"), "SourceTagError: source-sections.json: exactly one section is the canon section"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": [{\"hue\": \"x\"}]}]}"), "SourceTagError: source-sections.json section `works-a`: `hue` - a clause tests only period, region, kind"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": [{}]}]}"), "SourceTagError: source-sections.json section `works-a`: a clause is an object of period, region, kind"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": [{\"kind\": [\"nope\"]}]}]}"), "SourceTagError: source-sections.json section `works-a`: `kind: nope` - no kind value `nope` in source-tags.json"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": [{\"kind\": {\"book\": 1}}]}]}"), "SourceTagError: source-sections.json: exactly one section is the canon section"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": [{\"kind\": 5}]}]}"), "TypeError: 'int' object is not iterable"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": 5}]}"), "TypeError: 'int' object is not iterable"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-a\", \"title\": \"A\", \"takes\": \"ab\"}]}"), "SourceTagError: source-sections.json section `works-a`: a clause is an object of period, region, kind"),
    ("source-sections.json", Some("{\"sections\": [{\"id\": \"works-c\", \"title\": \"C\", \"canon\": true}]}"), "ok"),
];

#[test]
fn every_broken_file_is_refused_as_the_python_refused_it() {
    for (rel, text, want) in CASES {
        let dir = record();
        match text {
            Some(t) => put(&dir, rel, t),
            None => std::fs::remove_file(dir.join(rel)).unwrap(),
        }
        let got = load_vocabulary(&dir)
            .and_then(|v| load_sections(&dir, &v))
            .map_or_else(
                |e| {
                    let m = format!("{}: {}", e.kind, e.message);
                    m.find("not JSON (")
                        .map_or(m.clone(), |at| m[..at + 10].to_owned())
                },
                |_| "ok".to_owned(),
            );
        assert_eq!(got, *want, "{rel} {text:?}");
    }
}

#[test]
fn a_work_is_tagged_sectioned_and_labeled() {
    let dir = record();
    let vocab = load_vocabulary(&dir).unwrap();
    let sections = load_sections(&dir, &vocab).unwrap();
    let tags = parse(
        "<p>x</p>\n<!-- tags: period=modern,premodern; region=japan; kind=book -->",
        "w",
        &vocab,
    )
    .unwrap()
    .unwrap();
    assert_eq!(
        tags.marker(),
        "<!-- tags: period=modern,premodern; region=japan; kind=book -->"
    );
    assert_eq!(
        (tags.primary("region"), tags.values("kind").len()),
        ("japan", 1)
    );
    assert!(takes(&sections[0], &tags) && !takes(&sections[1], &tags));
    assert_eq!(home(&sections, Some(&tags)).unwrap().id, "works-japan");
    assert_eq!(home(&sections, None).unwrap().id, "works-canon");
    assert_eq!(
        labels_html(Some(&tags), &vocab),
        "<p class=\"srctags\"><span class=\"srctag srctag-period\" data-def=\"now &amp; &quot;then&quot;\" title=\"now &amp; &quot;then&quot;\">Modern</span> <span class=\"srctag srctag-period\" data-def=\"old\" title=\"old\">Premodern</span> <span class=\"srctag srctag-region\" data-def=\"jp\" title=\"jp\">Japan</span> <span class=\"srctag srctag-kind\" data-def=\"bound\" title=\"bound\">Book</span></p>"
    );
    assert_eq!(
        labels_html(None, &vocab),
        "<p class=\"srctags\"><span class=\"srctag srctag-canon\" data-def=\"the GM&#x27;s\" title=\"the GM&#x27;s\">Canon</span></p>"
    );
    assert_eq!(section_heading(&sections[0], 3, "x"), "<h3 class=\"works-section\" id=\"x\">Japan &amp; more</h3>\n<p class=\"works-section-desc\"><em>Japanese works</em></p>");
    assert_eq!(
        section_heading(&sections[1], 3, "y"),
        "<h3 class=\"works-section\" id=\"y\">China</h3>"
    );
    assert_eq!(
        kind_heading(&sections[0], &vocab.labels("kind")[1], 4, "u-"),
        "<h4 class=\"works-kind\" id=\"u-works-japan-web\" title=\"online\">Web &lt;page&gt;</h4>"
    );
    assert_eq!(vocab.known("period").len(), 2);
    assert!(vocab.labels("nope").is_empty());
    assert_eq!(strip_marker("<p>x</p>\n<!-- tags: a -->  \n"), "<p>x</p>\n");
    let block = contract_block(&vocab);
    assert!(block.starts_with(CONTRACT_OPEN) && block.ends_with(CONTRACT_CLOSE));
    assert!(block.contains(
        "\n- `kind=web` - **Web <page>**: online\n- (no marker) - **Canon**: the GM's\n"
    ));
    assert_eq!(
        synced_contract(
            &format!("a\n{CONTRACT_OPEN}\nold\n{CONTRACT_CLOSE}\nb"),
            &vocab
        )
        .unwrap(),
        format!("a\n{block}\nb")
    );
    assert_eq!(
        synced_contract(&format!("{CONTRACT_CLOSE}{CONTRACT_OPEN}"), &vocab)
            .unwrap_err()
            .message,
        "the contract has no derived source-tags block - its two markers are missing"
    );
    for (text, want) in [
        ("<!-- tags: period=x -->", "w: `period=x` - not a period value; the values are modern, premodern (source-tags.json)"),
        ("<!-- tags: a -->\n<!-- tags: b -->", "w: two tags markers"),
        ("<!-- tags: period=; region=japan; kind=book -->", "w: no period in its tags"),
        ("<!-- tags: kind=book; kind=web -->", "w: `kind=web` - the marker is `period=a; region=x,y; kind=k`, each facet once"),
        ("<!-- tags: period=modern,modern; region=japan; kind=book -->", "w: a period value is stated twice"),
    ] {
        assert_eq!(parse(text, "w", &vocab).unwrap_err().message, want);
    }
    assert!(parse("none", "w", &vocab).unwrap().is_none());
}

#[test]
fn the_catalog_reads_every_entry_and_keeps_every_refusal() {
    let dir = record();
    let entries: Vec<(String, String)> = [
        (
            "src-a",
            "<p>a</p>\n<!-- tags: period=modern,premodern; region=japan; kind=book -->",
        ),
        ("l7r-notes", "<p>The GM's l7r.md</p>"),
        (
            "grok",
            "<p>g</p>\n<!-- tags: period=modern; region=china; kind=web -->",
        ),
        (
            "k1",
            "<p>x</p>\n<!-- tags: period=nope; region=japan; kind=book -->",
        ),
        ("k2", "<p>no tags</p>"),
        (
            "k3",
            "<p>c</p><!-- tags: period=modern; region=japan; kind=book -->",
        ),
        (
            "k4",
            "<!-- tags: period=modern; region=china; kind=book -->",
        ),
    ]
    .iter()
    .map(|(k, t)| ((*k).to_owned(), (*t).to_owned()))
    .collect();
    let canon: BTreeSet<String> = ["l7r-notes".to_owned(), "k3".to_owned()]
        .into_iter()
        .collect();
    let c = Catalog::new(&dir, &entries, &canon, "w").unwrap();
    assert_eq!(
        c.errors,
        [
            "w/ k1: `period=nope` - not a period value; the values are modern, premodern (source-tags.json)",
            "w/ k2: no tags - every keyed work states `<!-- tags: period=...; region=...; kind=... -->` on its last line (source-tags.json)",
            "w/ k3: a canon entry (the GM's own notes) carries no tags - remove its marker",
            "w/ k4: no section of source-sections.json takes the primary tags period=modern, region=china, kind=book",
        ]
    );
    assert!(c.labels("src-a").contains("srctag-kind"));
    assert!(c.labels("l7r-notes").contains("srctag-canon"));
    assert_eq!(c.labels("nope"), "");
    let keys: Vec<String> = ["src-a", "l7r-notes", "grok", "nope"]
        .iter()
        .map(|s| (*s).to_owned())
        .collect();
    let kinds: Vec<(Option<String>, Vec<String>)> = c
        .by_kind(&keys)
        .into_iter()
        .map(|(l, r)| (l.map(|l| l.id), r))
        .collect();
    assert_eq!(
        kinds,
        [
            (None, vec!["l7r-notes".to_owned(), "nope".to_owned()]),
            (Some("book".to_owned()), vec!["src-a".to_owned()]),
            (Some("web".to_owned()), vec!["grok".to_owned()])
        ]
    );
    assert_eq!(c.anchors().len(), 9);
    let grouped: Vec<(String, Vec<String>)> = c
        .grouped(&keys)
        .into_iter()
        .map(|(s, r)| (s.id, r))
        .collect();
    assert_eq!(
        grouped[0],
        ("works-japan".to_owned(), vec!["src-a".to_owned()])
    );
    assert_eq!(grouped.len(), 3);
    let tagged_again: Vec<(String, String)> = vec![
        ("src-a".into(), entries[0].1.clone()),
        ("src-a".into(), entries[2].1.clone()),
    ];
    let twice = Catalog::new(&dir, &tagged_again, &canon, "w").unwrap();
    assert_eq!(
        (twice.tags.len(), twice.section[0].1.as_str()),
        (1, "works-china")
    );
    std::fs::remove_file(dir.join("source-tags.json")).unwrap();
    assert!(Catalog::new(&dir, &entries, &canon, "w").is_err());
}
