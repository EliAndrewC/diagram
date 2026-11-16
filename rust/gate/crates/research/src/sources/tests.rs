//! What a modal's references rest on (feature 449 T144; each expected value `sources.py`'s on the same record, 2026-11-16).

use super::{
    entry_fragments, heading_text, link_target, linkify, not_read, page_text, question_text,
    research_questions, Question, Reader,
};
use crate::fixture::{put, record};
use crate::record::store;

/// The record's questions directory, built from parts so no fixture names a pointer that does not resolve.
const Q: &str = "research/questions";

#[test]
fn a_heading_reads_as_its_reader_sees_it() {
    assert_eq!(
        heading_text(" *A* `b` <span class=\"xref\">x</span> "),
        "A b"
    );
    assert_eq!(
        page_text("<p>A &amp; <span class=\"xref\">x</span>\n b</p>"),
        "A & b"
    );
    assert_eq!(question_text("Q **x** (feature 1, 2026-08-29) "), "Q x");
    assert_eq!(question_text("Q (no date)"), "Q (no date)");
    let entry = format!("{Q}/0001-paddies.html, {Q}/0001-paddies.drawing.html; {Q}/0001-paddies.html `{Q}/0002-coins.html`");
    assert_eq!(
        entry_fragments(&entry),
        [
            "0001-paddies.html",
            "0001-paddies.drawing.html",
            "0002-coins.html"
        ]
    );
}

#[test]
fn where_a_citation_links() {
    for (cite, unread, target) in [
        ("SUMMARY-ONLY x", true, "../SOURCES.html#k"),
        ("URL: none", true, "../SOURCES.html#k"),
        ("unfetched https://a.org", true, "../SOURCES.html#k"),
        ("READ https://a.org/x). unfetched", false, "https://a.org/x"),
        ("see l7r.md https://a.org", false, "../SOURCES.html#k"),
        ("https://a.org/b_(c)).", false, "https://a.org/b_(c)"),
        ("nothing", false, "../SOURCES.html#k"),
    ] {
        assert_eq!(not_read(cite), unread, "{cite}");
        assert_eq!(link_target("k", cite, "../"), target, "{cite}");
    }
    assert_eq!(
        linkify("see https://a.org/x). and <a href=\"https://b.org\">https://b.org</a> <!-- https://c.org --> https://d.org/(e)) <script>https://s.org</script>"),
        "see <a href=\"https://a.org/x\" target=\"_blank\" rel=\"noopener\">https://a.org/x</a>). and <a href=\"https://b.org\">https://b.org</a> <!-- https://c.org --> <a href=\"https://d.org/(e)\" target=\"_blank\" rel=\"noopener\">https://d.org/(e)</a>) <script>https://s.org</script>"
    );
}

#[test]
fn the_record_read_for_its_readers() {
    let dir = record();
    let entry = format!("Entry: {Q}/0001-paddies.html and {Q}/0002-coins.html, {Q}/0001-paddies.html {Q}/0009-none.html");
    assert_eq!(
        research_questions(&entry, &dir),
        [
            Question {
                text: "Paddies wet".into(),
                url: "../../../research/site/q/paddies.html".into()
            },
            Question {
                text: "Coins".into(),
                url: "../../../research/site/q/coins.html".into()
            },
        ]
    );
    let reader = Reader::new(&dir);
    let r = store::load(&dir).unwrap();
    assert_eq!(
        reader.record_text("questions/0002-coins.html").unwrap(),
        store::page_html(&r, r.by_file("0002-coins.html").unwrap(), &dir, None).unwrap()
    );
    assert!(reader
        .record_text("questions/0001-paddies.html")
        .unwrap()
        .contains("class=\"xref\""));
    assert_eq!(
        reader.record_text("SOURCES.html").unwrap(),
        store::registry_html(&dir).unwrap()
    );
    assert!(reader
        .record_text("contents.json")
        .unwrap()
        .starts_with("{\n \"opening\""));
    assert_eq!(reader.record_text("none.html").unwrap(), "");
    assert_eq!(
        reader
            .record_text("questions/0001-paddies.notes.html")
            .unwrap_err()
            .message,
        "'0001-paddies.notes.html'"
    );
    let entries = reader.registry_entries().unwrap();
    assert_eq!(entries[0].0, "work-src-a");
    assert_eq!(entries[0].1.cite, "Src A, https://e.org/a READ");
    assert_eq!(
        entries[0].1.line,
        "Src A, https://e.org/a READ   READ 2026-10-01 at https://e.org/a2  "
    );
    assert_eq!(
        (
            entries[0].1.what.as_str(),
            entries[0].1.why.as_str(),
            entries[0].1.used.as_str()
        ),
        ("a book", "", "paddies")
    );
    assert_eq!(entries.len(), 3);
    assert_eq!(
        reader.canon_keys().unwrap().into_iter().collect::<Vec<_>>(),
        ["l7r-notes"]
    );
    // an entry no terminator follows is no entry of the registry's reader; a key seen twice keeps its first place and its last value
    put(&dir, "sources/_tail.html", "\n</body>\n</html>\n");
    put(
        &dir,
        "sources/010-works-cited/0040-src-a.html",
        "<h3 id=\"work-src-a\">again</h3>\n<p>Again</p>\n",
    );
    let again = Reader::new(&dir).registry_entries().unwrap();
    assert_eq!((again.len(), again[0].1.cite.as_str()), (3, "Again"));
    let broken = record();
    put(&broken, "contents.json", "nope");
    assert_eq!(
        Reader::new(&broken)
            .record_text("questions/0002-coins.html")
            .unwrap_err()
            .kind,
        "RecordError"
    );
    let unpaired = record();
    put(
        &unpaired,
        "confusables.json",
        "[{\"a\": \"x.html#y\", \"b\": \"x.html#y\"}]",
    );
    assert_eq!(
        Reader::new(&unpaired)
            .record_text("questions/0002-coins.html")
            .unwrap_err()
            .kind,
        "RecordError"
    );
    std::fs::remove_dir_all(unpaired.join("sources")).unwrap();
    assert_eq!(
        Reader::new(&unpaired).record_text("SOURCES.html").unwrap(),
        ""
    );
    std::fs::create_dir(unpaired.join("sources")).unwrap();
    assert!(Reader::new(&unpaired).registry_entries().is_err());
    assert!(Reader::new(&unpaired).canon_keys().is_err());
}
