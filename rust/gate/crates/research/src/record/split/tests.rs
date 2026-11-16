//! The splitter against the Python's own answers (feature 449 T144; each expected value is `split.py`'s on the same text, 2026-11-16).

use super::{comments, heading_id, headings, split};
use crate::record::assemble;

const CLOSE: &str = "\n</main>\n</body>\n</html>\n";

#[test]
fn a_page_splits_and_assembles_back() {
    let page = format!(
        "<html><main>\n<!-- <h2 id=\"hid\">x</h2> --><h2 id=\"a\">A</h2><p>t</p><h3 id=\"e1\">e</h3>b<h3 id=\"e2\">f</h3>\n<h2 id=\"b\">B</h2>\n<section class=\"citations\">c</section>{CLOSE}"
    );
    let got = split(&page, Some(3), 2).unwrap();
    assert_eq!(got.front, "<html><main>\n<!-- <h2 id=\"hid\">x</h2> -->");
    assert_eq!(got.sections.len(), 2);
    assert_eq!(got.sections[0].entries.len(), 2);
    assert_eq!(got.sections[0].text, "<h2 id=\"a\">A</h2><p>t</p>");
    assert!(got.sections[1].entries.is_empty());
    assert_eq!(
        got.tail,
        format!("\n<section class=\"citations\">c</section>{CLOSE}")
    );
    assert_eq!(assemble(&got), page);
    let plain = split(&page, None, 2).unwrap();
    assert!(plain.sections[0].entries.is_empty());
    let none = split(&format!("front{CLOSE}"), None, 2).unwrap();
    assert!(none.sections.is_empty());
    assert_eq!(none.front, "front");
    // two newlines end it too, as `$` before a final newline reads; a `</section>` not opened as the pointer is no pointer
    assert_eq!(
        split(&format!("x</section>{CLOSE}\n"), None, 2)
            .unwrap()
            .front,
        "x</section>"
    );
    assert_eq!(
        split("x\n</main>\n</body>\n</html>", None, 2)
            .unwrap()
            .front,
        "x"
    );
}

#[test]
fn what_the_splitter_refuses() {
    assert_eq!(
        split("no tail", None, 2).unwrap_err().message,
        "this page does not end with `</main></body></html>` and its optional citations pointer - the splitter has not been shown its shape"
    );
    let e = split(&format!("\u{65e5}<h2 class=\"x\">A</h2>{CLOSE}"), None, 2).unwrap_err();
    assert_eq!(
        e.message,
        "a heading with no id at offset 1: '<h2 class=\"x\">' - the record's anchors are heading ids, and a fragment is named for one"
    );
    let e = split(&format!("<h2 id=\"a\">A</h2><h3>e</h3>{CLOSE}"), Some(3), 2).unwrap_err();
    assert!(e
        .message
        .starts_with("a heading with no id at offset 17: '<h3>'"));
    assert_eq!(
        heading_id("<h2 open", 0).unwrap_err().message,
        "substring not found"
    );
}

#[test]
fn a_heading_in_a_comment_or_a_longer_tag_opens_nothing() {
    let html = "<!-- <h2 id=\"x\"> --> <h2 id=\"y\"> <h2x> <h2>";
    assert_eq!(comments(html), vec![(0, 20)]);
    assert_eq!(headings(html, 2), vec![21, 39]);
}
