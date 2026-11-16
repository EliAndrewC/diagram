//! The kept pages' entries (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record).

use serde_json::json;

use super::*;
use crate::testkit::{reserve, W};

const TAGS: &str = "period=modern; region=japan; kind=book";

fn draft(w: &W, lines: &[String]) -> std::path::PathBuf {
    let d = w.root().join("out/312-draft-0001");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("ids.json"), json!({"p1": "https://k.org/1", "p2": "https://k.org/2", "p3": "https://k.org/3", "p4": "https://k.org/4"}).to_string())
        .unwrap();
    std::fs::write(d.join("entries.jsonl"), lines.join("\n") + "\n").unwrap();
    d
}

fn entry(id: &str, key: &str, cite: &str) -> String {
    json!({"id": id, "key": key, "citation": cite, "what": "What it is: a page", "why": "it applies", "tags": TAGS}).to_string()
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "every refusal a draft line meets, one table of lines on one world"
)]
fn install_writes_each_kept_pages_entry_once() {
    let w = W::new("entries-install");
    w.lines(
        KEPT,
        &[
            json!({"url": "k.org/1", "raw": "https://k.org/1"}),
            json!({"url": "k.org/2", "raw": "https://k.org/2"}),
            json!({"url": "k.org/4", "raw": "https://k.org/4"}),
        ],
    );
    w.uncited("0090-old.html", "<p>https://k.org/4</p>");
    let d = draft(
        &w,
        &[
            entry("p1", "src-a", "A (https://k.org/1)"),
            entry("p1", "src-a", "A (https://k.org/1)"),
            entry("p2", "held", "B (https://k.org/2)"),
            entry("p3", "k3", "C (https://k.org/3)"),
            entry("p4", "k4", "D (https://k.org/4)"),
            entry("p1", "Bad Key", "A (https://k.org/1)"),
            entry("p1", "k", "no url"),
            json!({"id": "p1", "key": "k", "citation": "https://k.org/1", "what": "What it is:", "why": "w", "tags": TAGS}).to_string(),
            entry("p9", "k", "c"),
            json!({"id": "p1", "key": "k"}).to_string(),
            json!({"id": "p1", "key": "k", "citation": "c", "what": "w", "why": "w", "tags": "period=never; region=japan; kind=book"}).to_string(),
            json!({"id": "p1", "key": "k", "citation": "c", "what": "w", "why": "w", "tags": "nothing"}).to_string(),
            json!({"id": "p1", "key": "k", "citation": "c", "what": "w", "why": "w", "tags": "period=modern;\nregion=japan"}).to_string(),
            json!({"id": ["l"]}).to_string(),
            json!({"id": {}}).to_string(),
            json!({"id": 5}).to_string(),
            json!([1]).to_string(),
            json!("s").to_string(),
            json!(3).to_string(),
            "not json".to_owned(),
            String::new(),
        ],
    );
    std::fs::write(
        d.join("entries.jsonl"),
        std::fs::read_to_string(d.join("entries.jsonl"))
            .unwrap()
            .replace("\"tags\":\"nothing\"", "\"tags\":\"x --> <!-- tags: y\""),
    )
    .unwrap();
    let mut err = String::new();
    let got = install(w.root(), &d, &reserve, &mut err).unwrap();
    assert_eq!(
        got,
        Installed {
            written: 2,
            refused: 16,
            already: 2,
            dropped: 1
        }
    );
    assert_eq!(
        got.json(),
        json!({"written": 2, "refused": 16, "already": 2, "dropped": 1})
    );
    let lines: Vec<&str> = err.lines().collect();
    assert_eq!(lines[0], "uncited: 312-draft-0001: refused p1 - a bad key, an empty field, or a citation without its URL");
    assert!(lines[3].starts_with("uncited: 312-draft-0001: refused - 'p9': {\"id\":\"p9\""),);
    assert!(lines[4].starts_with("uncited: 312-draft-0001: refused - 'citation': "),);
    assert!(lines[5].contains("`period=never` - not a period value"),);
    assert!(lines[6].contains("two tags markers"), "{}", lines[6]);
    assert!(lines[7].starts_with(
        "uncited: 312-draft-0001: refused - 'NoneType' object has no attribute 'marker': "
    ));
    assert!(lines[8].starts_with("uncited: 312-draft-0001: refused - cannot use 'list' as a dict key (unhashable type: 'list'): "));
    assert!(lines[9].starts_with("uncited: 312-draft-0001: refused - cannot use 'dict' as a dict key (unhashable type: 'dict'): "));
    assert!(lines[10].starts_with("uncited: 312-draft-0001: refused - 5: "));
    assert!(lines[11].starts_with(
        "uncited: 312-draft-0001: refused - list indices must be integers or slices, not str: "
    ));
    assert!(lines[12].starts_with(
        "uncited: 312-draft-0001: refused - string indices must be integers, not 'str': "
    ));
    assert!(lines[13]
        .starts_with("uncited: 312-draft-0001: refused - 'int' object is not subscriptable: "));
    // the key taken by the registry got `-2`, the one held elsewhere `-2` past its refusal
    let names: Vec<String> = crate::entries(&w.root().join(UNCITED))
        .iter()
        .map(|p| crate::name_of(p))
        .collect();
    assert!(
        names.iter().any(|n| n.ends_with("-src-a-2.html"))
            && names.iter().any(|n| n.ends_with("-held-2.html")),
    );
    let written = std::fs::read_to_string(
        w.root()
            .join(UNCITED)
            .join(names.iter().find(|n| n.ends_with("-src-a-2.html")).unwrap()),
    )
    .unwrap();
    assert!(written.starts_with("<h3 id=\"src-a-2\"><code>src-a-2</code></h3>\n<p><!-- WRITTEN "),);
    assert!(written.ends_with("<p><em>What it is:</em> a page</p>\n<p><em>Why it applies, and its limits:</em> it applies</p>\n<!-- tags: period=modern; region=japan; kind=book -->\n"));
    // a reservation refused for another reason stops the install
    let d = draft(&w, &[entry("p3", "boom", "C (https://k.org/3)")]);
    w.lines(KEPT, &[json!({"url": "k.org/3", "raw": "https://k.org/3"})]);
    assert_eq!(
        install(w.root(), &d, &reserve, &mut String::new())
            .unwrap_err()
            .kind,
        "OSError"
    );
    // no entries file: nothing
    std::fs::remove_file(d.join("entries.jsonl")).unwrap();
    assert_eq!(
        install(w.root(), &d, &reserve, &mut String::new()).unwrap(),
        Installed::default()
    );
    std::fs::write(d.join("ids.json"), "[]").unwrap();
    assert_eq!(
        install(w.root(), &d, &reserve, &mut String::new()).unwrap(),
        Installed::default()
    );
    std::fs::write(d.join("ids.json"), "{").unwrap();
    assert!(install(w.root(), &d, &reserve, &mut String::new()).is_err());
}

#[test]
fn cite_moves_an_entry_to_the_works_cited_with_its_placeholder() {
    let w = W::new("entries-cite");
    w.uncited("0100-u.html", "<p>x</p>\n<!-- tags: a -->\n");
    w.uncited("0110-v.html", "<p>no marker</p>\n");
    let dest = cite(w.root(), "u").unwrap();
    assert_eq!(crate::name_of(&dest), "0100-u.html");
    assert_eq!(
        std::fs::read_to_string(&dest).unwrap(),
        format!("<p>x</p>\n{USED_FOR_PLACEHOLDER}<!-- tags: a -->\n")
    );
    assert!(!w.root().join(UNCITED).join("0100-u.html").exists());
    assert_eq!(
        std::fs::read_to_string(cite(w.root(), "v").unwrap()).unwrap(),
        format!("<p>no marker</p>\n{USED_FOR_PLACEHOLDER}")
    );
    assert_eq!(
        cite(w.root(), "u").unwrap_err().message,
        "no uncited entry for 'u' in research/sources/040-uncited-works"
    );
    std::fs::rename(
        w.root().join("research/sources/010-works-cited"),
        w.root().join("moved"),
    )
    .unwrap();
    w.uncited("0120-w.html", "x");
    assert_eq!(cite(w.root(), "w").unwrap_err().kind, "FileNotFoundError");
}

#[test]
fn requeue_merge_and_the_entry_holding_a_url() {
    let w = W::new("entries-requeue");
    w.lines(
        KEPT,
        &[
            json!({"url": "k.org/1", "raw": "https://k.org/1"}),
            json!({"url": "k.org/2", "raw": "https://k.org/2"}),
        ],
    );
    w.uncited("0100-k1.html", "<p>https://k.org/1</p>");
    w.uncited("x-not-numbered.html", "<p>https://k.org/1</p>");
    w.uncited("0200-.html", "<p>https://k.org/9</p>");
    assert_eq!(
        entry_holding(w.root(), "https://k.org/1")
            .unwrap()
            .as_deref(),
        Some("k1")
    );
    assert_eq!(
        entry_holding(w.root(), "https://k.org/9")
            .unwrap()
            .as_deref(),
        Some("")
    );
    assert_eq!(entry_holding(w.root(), "https://none.org").unwrap(), None);
    assert_eq!(
        requeue(w.root(), "https://k.org/1").unwrap().as_deref(),
        Some("k1")
    );
    assert!(!w.root().join(UNCITED).join("0100-k1.html").exists());
    assert_eq!(requeue(w.root(), "https://k.org/2").unwrap(), None);
    // an entry whose key is empty retires nothing, and is no entry to requeue
    assert_eq!(
        requeue(w.root(), "https://k.org/9").unwrap_err().kind,
        "ValueError"
    );
    assert_eq!(
        requeue(w.root(), "https://none.org").unwrap_err().message,
        "https://none.org has no verdict and no entry to requeue"
    );
    // merge: an uncited entry into a cited or uncited one, its kept pages moved as duplicates
    w.lines(KEPT, &[json!({"url": "k.org/3", "raw": "https://k.org/3"})]);
    w.uncited("0300-k3.html", "<p>https://k.org/3</p>");
    w.uncited("0310-nothing.html", "<p>none kept</p>");
    let gone = merge(w.root(), "k3", "src-a").unwrap();
    assert_eq!(crate::name_of(&gone), "0300-k3.html");
    assert!(w.read(crate::NOT_KEPT).contains("the same work as src-a"));
    assert_eq!(
        merge(w.root(), "k3", "src-a").unwrap_err().message,
        "no uncited entry for 'k3' under research/sources"
    );
    assert_eq!(
        merge(w.root(), "nothing", "no-such").unwrap_err().message,
        "no entry for 'no-such' under research/sources"
    );
    assert_eq!(
        merge(w.root(), "nothing", "src-a").unwrap_err().message,
        "'nothing': no kept page's URL appears in 0310-nothing.html"
    );
    w.lines(KEPT, &[json!({"url": "k"})]);
    assert_eq!(
        merge(w.root(), "nothing", "src-a").unwrap_err().kind,
        "KeyError"
    );
    std::fs::write(w.root().join(UNCITED).join("0400-bad.html"), [0xff]).unwrap();
    assert!(entry_holding(w.root(), "x").is_err());
}

#[test]
fn retire_cited_leaves_the_works_cited_with_its_state() {
    let w = W::new("entries-retire");
    w.put(
        "research/source-access.json",
        r#"{"states": [{"id": "gone"}, {"id": "down"}], "recorded": {}}"#,
    );
    w.put(
        "research/sources/010-works-cited/0500-dead.html",
        "<p>(https://dead.org/x).</p>",
    );
    w.put(
        "research/sources/010-works-cited/0510-nourl.html",
        "<p>none</p>",
    );
    let gone = retire_cited(w.root(), "dead", "gone", "read: it is gone").unwrap();
    assert_eq!(crate::name_of(&gone), "0500-dead.html");
    assert!(!gone.exists());
    let line = w.read(crate::NOT_KEPT);
    assert!(
        line.contains("\"raw\": \"https://dead.org/x\"")
            && line.contains("\"note\": \"dead: read: it is gone\"")
            && line.contains("\"access\": \"gone\"")
    );
    assert!(w.read("research/source-access.json").contains("\"dead\""));
    assert_eq!(
        retire_cited(w.root(), "dead", "gone", "n")
            .unwrap_err()
            .message,
        "no works-cited entry for 'dead'"
    );
    assert_eq!(
        retire_cited(w.root(), "src-a", "gone", "n").unwrap_err().message,
        "src-a is still cited in 0001-paddies.notes.html - remove or re-source those footnotes first (FR-019)"
    );
    assert_eq!(
        retire_cited(w.root(), "nourl", "gone", "n")
            .unwrap_err()
            .kind,
        "IndexError"
    );
    assert_eq!(
        retire_cited(w.root(), "grok", "lost", "n")
            .unwrap_err()
            .kind,
        "ValueError"
    );
    assert_eq!(
        retire_cited(w.root(), "grok", "gone", "read: it is gone")
            .unwrap_err()
            .kind,
        "Blocked"
    );
    w.put("research/source-access.json", "not json");
    w.put(
        "research/sources/010-works-cited/0520-dead2.html",
        "<p>https://dead2.org/x</p>",
    );
    let e = retire_cited(w.root(), "dead2", "gone", "read: it is gone").unwrap_err();
    assert!(
        e.message.starts_with("access-tags: REFUSED - "),
        "{}",
        e.message
    );
}

#[test]
fn the_report_says_where_the_set_stands() {
    let w = W::new("entries-report");
    w.lines(
        KEPT,
        &[
            json!({"url": "k.org/1", "raw": "https://k.org/1"}),
            json!({"url": "k.org/2", "raw": "https://k.org/2"}),
        ],
    );
    w.lines(
        crate::NOT_KEPT,
        &[
            json!({"url": "n.org/1", "reasons": ["off-topic", "duplicate"]}),
            json!({"url": "n.org/2", "reasons": ["duplicate"]}),
        ],
    );
    w.uncited("0100-k1.html", "<p>(https://k.org/1).</p>");
    w.uncited("0110-stray.html", "<p>https://stray.org/x</p>");
    w.ledger(&[
        json!({"url": "s.org/1", "raw": "https://s.org/1"}),
        json!({"url": "s.org/2", "raw": "https://s.org/2"}),
    ]);
    w.page("https://s.org/1", "saved", "fetch");
    assert_eq!(
        report(w.root()).unwrap(),
        "uncited: 2 page(s) not yet judged (1 with saved text); 2 kept, 2 not kept (duplicate 2, off-topic 1); 2 written up, 1 kept with no \
         entry, 1 entr(ies) whose URL is no kept page's (a citation a check corrected)"
    );
    std::fs::remove_dir_all(w.root().join(UNCITED)).unwrap();
    assert!(report(w.root())
        .unwrap()
        .contains("0 written up, 2 kept with no entry, 0 entr(ies)"));
    w.lines(crate::NOT_KEPT, &[json!({"url": "n.org/1"})]);
    assert_eq!(report(w.root()).unwrap_err().kind, "KeyError");
    assert_eq!(shown(&json!({"a": 1})), "{\"a\": 1}");
}

#[test]
fn written_reads_the_uncited_entries() {
    let w = W::new("entries-written");
    assert!(written(w.root()).unwrap().is_empty());
    w.uncited("0100-a.html", "<p>https://www.a.org/x/</p>");
    assert!(written(w.root()).unwrap().contains("a.org/x"));
    std::fs::write(w.root().join(UNCITED).join("0200-bad.html"), [0xff]).unwrap();
    assert!(written(w.root()).is_err());
    assert!(entry_html("k", "c", "w", "y", "m").contains("<!-- WRITTEN "));
}
