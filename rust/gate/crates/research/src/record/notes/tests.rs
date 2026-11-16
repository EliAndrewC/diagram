//! Notes by key, numbered at assembly (feature 449 T144; expected values `notes.py`'s).

use super::{allocate, is_key, merge, notes_of, number_references, render_note, Notes, Placed};

fn notes(pairs: &[(&str, &str)]) -> Notes {
    pairs
        .iter()
        .map(|(k, b)| ((*k).to_owned(), (*b).to_owned()))
        .collect()
}

const REF_B: &str = "<sup class=\"fn\" data-note=\"b\"></sup>";
const REF_A: &str = "<sup class=\"fn\" data-note=\"a\"></sup>";

#[test]
fn references_are_numbered_in_page_order() {
    let page = format!("x{REF_B}y{REF_A}z{REF_B}");
    let (bare, placed) = allocate(&page, &notes(&[("a", "A"), ("b", "B")]), "w").unwrap();
    assert_eq!(bare, "xyz");
    assert_eq!(
        placed[0],
        Placed {
            key: "b".into(),
            number: 1,
            body: "B".into(),
            references: 2
        }
    );
    assert_eq!(placed[1].number, 2);
    assert_eq!(
        number_references(&page, &placed, "c.html"),
        "x<sup class=\"fn\"><a id=\"fnref-1\" href=\"c.html#fn-1\">1</a></sup>y<sup class=\"fn\"><a id=\"fnref-2\" href=\"c.html#fn-2\">2</a></sup>z<sup class=\"fn\"><a id=\"fnref-1-2\" href=\"c.html#fn-1\">1</a></sup>"
    );
    assert_eq!(
        render_note(&placed[0], "p.html"),
        "<li id=\"fn-1\">B <a class=\"fnback\" href=\"p.html#fnref-1\">back</a></li>"
    );
    assert!(is_key("a-1\n") && !is_key("A"));
}

#[test]
fn what_the_notes_refuse() {
    let msg = |r: Result<(String, Vec<Placed>), crate::Error>| r.unwrap_err().message;
    assert_eq!(
        msg(allocate(
            "<sup class=\"fn\" data-note=\"B\"></sup>",
            &notes(&[]),
            "w"
        )),
        "w: `B` is not a note key - lower case, digits and hyphens"
    );
    assert_eq!(
        msg(allocate(REF_A, &notes(&[]), "w")),
        "w: a reference names `a`, which no note on this page defines"
    );
    assert_eq!(
        msg(allocate(REF_A, &notes(&[("a", "A"), ("z", "Z"), ("c", "C")]), "w")),
        "w: c, z - defined as a note, referenced nowhere. A note nothing cites is either a reference that was deleted or a note that was never wired up; the assembly will not quietly drop it"
    );
    assert_eq!(
        notes_of("<li data-note=\"k\">a\nb</li>", "w").unwrap(),
        notes(&[("k", "a\nb")])
    );
    assert_eq!(
        notes_of("<li data-note=\"K\">a</li>", "w")
            .unwrap_err()
            .message,
        "w: `K` is not a note key - lower case, digits and hyphens"
    );
    assert_eq!(
        notes_of("<li data-note=\"k\">a</li><li data-note=\"k\">b</li>", "w")
            .unwrap_err()
            .message,
        "w: `k` is defined twice in one file"
    );
    let one = notes(&[("k", "a")]);
    assert_eq!(merge(&[("p".into(), one.clone())]).unwrap(), one);
    assert_eq!(
        merge(&[("p".into(), one.clone()), ("q".into(), one)]).unwrap_err().message,
        "`k` is defined in p and again in q - a note key is unique within its page, because the reference names it and nothing else"
    );
}
