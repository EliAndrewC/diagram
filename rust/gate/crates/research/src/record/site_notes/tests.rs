//! The site's footnotes (feature 449 T144; each expected value `site_notes.py`'s on the same record, 2026-11-16).

use super::{foot, keyed_to, small_page, Numbering};
use crate::fixture::record;
use crate::record::{questions, store};

const NUMBERED: &str = "<h2 id=\"paddies\">Paddies <em>wet</em> (researched 2026-08-27, feature 133)</h2>\n<!-- tags: subject=farming; setting=countryside; level=detail -->\n<p>Paddies are wet. They hold water.<sup class=\"fn\"><a id=\"fnref-1\" href=\"#fn-1\">1</a></sup> See https://e.org/b).</p>\n<p>Again.<sup class=\"fn\"><a id=\"fnref-1-2\" href=\"#fn-1\">1</a></sup><sup class=\"fn\"><a id=\"fnref-2\" href=\"#fn-2\">2</a></sup></p>\n";

#[test]
fn a_small_page_counts_from_one_and_the_single_page_once() {
    let dir = record();
    let r = questions::load(&dir).unwrap();
    let paddies = r.by_file("0001-paddies.html").unwrap();
    let notes = store::page_notes("0001-paddies.html", &dir).unwrap();
    let (text, placed) = small_page(&paddies.text, &notes, "w").unwrap();
    assert_eq!(text, NUMBERED);
    assert_eq!((placed.len(), placed[0].references), (2, 2));
    assert!(foot(&placed, "<ul>w</ul>").starts_with("\n<section class=\"footnotes\"><h2 id=\"page-notes\">Notes</h2>\n<ol>\n<li id=\"fn-1\"><a href=\"#work-src-a\"><code>src-a</code></a>"));
    assert!(foot(&placed, "<ul>w</ul>").ends_with("<a class=\"fnback\" href=\"#fnref-2\">back</a></li>\n</ol></section>\n<section class=\"works\"><h2 id=\"page-works\">Works cited here</h2>\n<ul>w</ul>\n</section>\n"));
    assert_eq!(foot(&[], "x"), "");
    let unknown = "<sup class=\"fn\" data-note=\"zz\"></sup>";
    assert_eq!(
        small_page(unknown, &notes, "w").unwrap_err().message,
        "w: a reference names `zz`, which no note on this page defines"
    );
    let mut count = Numbering::new();
    assert_eq!(
        count.number(&paddies.text, "a.html", &notes, "w").unwrap(),
        NUMBERED
    );
    assert!(count
        .number(&paddies.text, "a.html", &notes, "w")
        .unwrap()
        .contains("<a id=\"fnref-1-3\" href=\"#fn-1\">1</a></sup> See"));
    assert_eq!(
        count
            .number(
                "<sup class=\"fn\" data-note=\"zz\"></sup><sup class=\"fn\" data-note=\"k\"></sup>",
                "b.html",
                &notes,
                "w"
            )
            .unwrap_err()
            .message,
        "w: a reference names `zz`, which no note on b.html defines"
    );
    assert_eq!(count.placed.len(), 2);
    assert_eq!(
        keyed_to("<a href=\"https://e.org\"><code>k-1</code></a>", "#"),
        "<a href=\"#k-1\"><code>k-1</code></a>"
    );
}
