//! The set (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record).

use serde_json::json;

use super::*;
use crate::testkit::W;

#[test]
fn one_work_under_one_key() {
    for (n, want) in [
        ("zh.wikipedia.org/zh-hant/城", "zh.wikipedia.org/wiki/城"),
        ("zh.wikisource.org/zh-mo/x", "zh.wikisource.org/wiki/x"),
        ("zh.wikipedia.org/wiki/y", "zh.wikipedia.org/wiki/y"),
        (
            "raw.githubusercontent.com/o/r/main/f.txt",
            "github.com/o/r/blob/main/f.txt",
        ),
        ("kotobank.jp/word/町屋-123", "kotobank.jp/word/123"),
        ("kotobank.jp/word/町屋-123\n", "kotobank.jp/word/123\n"),
        ("api.openalex.org/works/doi:10.1/x", "doi.org/10.1/x"),
        ("mdpi-res.com/d/1.pdf", "res.mdpi.com/d/1.pdf"),
        ("online.bunka.go.jp/x", "bunka.nii.ac.jp/x"),
        ("e.org/a", "e.org/a"),
    ] {
        assert_eq!(work(n), want, "{n}");
    }
    assert!(
        canon("GitHub.com/EliAndrewC/gm-assistant")
            && canon("raw.githubusercontent.com/eliandrewc/x")
            && !canon("github.com/other")
    );
}

#[test]
fn the_set_is_every_page_read_with_no_verdict_entry_or_row() {
    let w = W::new("set");
    w.ledger(&[
        json!({"url": "a.org/1", "raw": "https://a.org/1"}),
        json!({"url": "a.org/2", "raw": "https://a.org/2", "outcome": "cited:src-a"}),
        json!({"url": "a.org/3", "raw": "https://a.org/3", "outcome": "cited:gone-key"}),
        json!({"url": "a.org/4", "raw": "https://a.org/4"}),
        json!({"url": "a.org/5", "raw": "https://a.org/5"}),
        json!({"url": "zh.wikipedia.org/zh-hans/x", "raw": "https://zh.wikipedia.org/zh-hans/x"}),
        json!({"url": "zh.wikipedia.org/wiki/x", "raw": "https://zh.wikipedia.org/wiki/x"}),
        json!({"url": "grokipedia.com/p", "raw": "https://grokipedia.com/p"}),
        json!({"url": "github.com/eliandrewc/notes", "raw": "https://github.com/EliAndrewC/notes"}),
        json!({"url": "u.org/written", "raw": "https://u.org/written"}),
    ]);
    w.lines(KEPT, &[json!({"url": "a.org/4", "raw": "https://a.org/4"})]);
    w.lines(
        NOT_KEPT,
        &[json!({"url": "a.org/5", "raw": "https://a.org/5"})],
    );
    w.uncited("0100-u.html", "<p>(https://u.org/written)</p>");
    let bare = "https://e.org/prehold";
    l7r_gate_archive::manifest::write_row(
        w.root(),
        bare,
        &json!({"url": bare, "keys": [], "notes": []}),
    )
    .unwrap();
    assert_eq!(
        uncited_set(w.root()).unwrap(),
        [
            "https://a.org/1",
            "https://a.org/3",
            "https://e.org/prehold",
            "https://zh.wikipedia.org/wiki/x"
        ]
    );
    assert_eq!(prehold(w.root()).unwrap(), [bare]);
    assert_eq!(cited_marks(w.root()).unwrap().len(), 1);
    assert!(registry_norms(w.root()).unwrap().contains("u.org/written"));
    assert_eq!(judged(w.root()).unwrap().len(), 2);
}

#[test]
fn a_record_that_will_not_read_is_refused() {
    let w = W::new("set-bad");
    w.ledger(&[json!({"url": "a.org/1", "outcome": "cited:src-a"})]);
    assert_eq!(cited_marks(w.root()).unwrap().len(), 1);
    w.ledger(&[json!([1])]);
    assert_eq!(cited_marks(w.root()).unwrap_err().kind, "AttributeError");
    w.ledger(&[json!({"outcome": "cited:src-a"})]);
    assert_eq!(cited_marks(w.root()).unwrap_err().kind, "KeyError");
    w.lines(KEPT, &[json!({"raw": "x"})]);
    assert_eq!(judged(w.root()).unwrap_err().kind, "KeyError");
    assert!(uncited_set(w.root()).is_err());
    w.lines(KEPT, &[]);
    w.lines(NOT_KEPT, &[json!({"raw": "x"})]);
    assert_eq!(judged(w.root()).unwrap_err().kind, "KeyError");
    std::fs::write(
        w.root()
            .join("research/sources/010-works-cited/0040-bad.html"),
        [0xff],
    )
    .unwrap();
    assert_eq!(
        registry_norms(w.root()).unwrap_err().kind,
        "UnicodeDecodeError"
    );
    w.put("research/archive/a1/a1b2c3d4e5f6.json", "[1]");
    assert_eq!(prehold(w.root()).unwrap_err().kind, "AttributeError");
    w.put("research/archive/a1/a1b2c3d4e5f6.json", "{}");
    assert_eq!(prehold(w.root()).unwrap_err().kind, "KeyError");
    w.put("research/archive/a1/a1b2c3d4e5f6.json", "{");
    assert_eq!(prehold(w.root()).unwrap_err().kind, "JSONDecodeError");
}
