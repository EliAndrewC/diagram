//! A drawn sheet read by kind (449 T377): what a kind's marks are, and which kinds two drawings differ in.

use super::*;

const DEFS: &str = r##"<defs><pattern id="hatch"><line x1="0" stroke="#000"/></pattern><pattern id="wrap" href="#hatch"/></defs>"##;

/// A sheet: its `<defs>`, a hall tagged on its own mark, a well whose group names its kind and a caption under it, and a frame.
fn sheet(defs: &str, hall: &str, well: &str) -> String {
    format!(
        "<?xml version=\"1.0\"?>\n<svg viewBox=\"0 0 9 9\">\n{defs}\n<!-- the sheet's marks -->\n\
         <rect x=\"{hall}\" data-kind=\"hall\" data-id=\"d0\"/>\n\
         <g data-kind=\"well\"><circle r=\"{well}\" data-id=\"d1\"/><text x=\"1\">well</text></g>\n\
         <rect fill=\"url(#wrap)\" data-part-of=\"gate\"/>\n<text data-kind=\"-\">title</text>\n</svg>\n"
    )
}

fn kinds(was: &str, now: &str) -> Option<Vec<String>> {
    differing(&read(was), &read(now)).map(|s| s.into_iter().collect())
}

#[test]
fn each_token_belongs_to_its_own_kind_or_the_one_it_is_written_inside() {
    let m = read(&sheet(DEFS, "1", "2"));
    assert_eq!(m.kinds["hall"], [r#"<rect x="1" data-kind="hall"/>"#]);
    assert_eq!(
        m.kinds["well"],
        [
            r#"<g data-kind="well">"#,
            r#"<circle r="2"/>"#,
            r#"<text x="1">"#,
            "well",
            "</text>",
            "</g>"
        ]
    );
    assert_eq!(
        m.kinds["gate"],
        [r#"<rect fill="url(#wrap)" data-part-of="gate"/>"#]
    );
    assert_eq!(m.defs["hatch"].len(), 3);
    assert_eq!(m.defs["wrap"], [r##"<pattern id="wrap" href="#hatch"/>"##]);
    // the document's own tags; the comment and the whitespace draw nothing
    assert_eq!(
        m.loose,
        [
            r#"<?xml version="1.0"?>"#,
            r#"<svg viewBox="0 0 9 9">"#,
            "<defs>",
            "</defs>",
            "</svg>"
        ]
    );
}

/// A mark renumbered (`data-id`, document order) is the same mark; one moved, resized or recolored is not.
#[test]
fn only_the_kinds_whose_marks_differ_are_named() {
    let base = sheet(DEFS, "1", "2");
    assert_eq!(
        kinds(&base, &base.replace("\"d1\"", "\"d7\"")),
        Some(vec![])
    );
    assert_eq!(
        kinds(&base, &sheet(DEFS, "5", "2")),
        Some(vec!["hall".to_owned()])
    );
    // a caption moved is the kind's mark too
    assert_eq!(
        kinds(&base, &base.replace("<text x=\"1\">", "<text x=\"3\">")),
        Some(vec!["well".to_owned()])
    );
    // a kind new or gone differs
    let gone = base.replace(r#"<rect x="1" data-kind="hall" data-id="d0"/>"#, "");
    assert_eq!(kinds(&base, &gone), Some(vec!["hall".to_owned()]));
}

/// A `<defs>` entry changed redraws the kinds that use it, through an entry that uses it too.
#[test]
fn a_changed_definition_owes_the_kinds_that_use_it() {
    let base = sheet(DEFS, "1", "2");
    let recolored = sheet(&DEFS.replace("#000", "#111"), "1", "2");
    assert_eq!(kinds(&base, &recolored), Some(vec!["gate".to_owned()]));
    // an entry no kind uses, added
    let added = DEFS.replace("</defs>", r#"<pattern id="new"/></defs>"#);
    assert_eq!(kinds(&base, &sheet(&added, "1", "2")), Some(vec![]));
}

/// What no kind owns - the document's own tags, an entry with no id - cannot say what it redraws.
#[test]
fn a_difference_no_kind_owns_cannot_be_told() {
    let base = sheet(DEFS, "1", "2");
    assert_eq!(kinds(&base, &base.replace("0 0 9 9", "0 0 9 8")), None);
    let style = DEFS.replace("</defs>", "<style>.a{}</style></defs>");
    assert_eq!(kinds(&base, &sheet(&style, "1", "2")), None);
}

/// A discharge binds a kind's marks and the definitions they use: a mark or a used entry changed moves it, another kind's change
/// does not.
#[test]
fn a_kinds_digest_moves_with_its_marks_and_what_they_use() {
    let base = read(&sheet(DEFS, "1", "2"));
    let gate = digest(&base, "gate").unwrap();
    assert_eq!(gate.len(), 16);
    assert_eq!(digest(&read(&sheet(DEFS, "5", "2")), "gate").unwrap(), gate);
    assert_ne!(
        digest(
            &read(&sheet(&DEFS.replace("#000", "#111"), "1", "2")),
            "gate"
        )
        .unwrap(),
        gate
    );
    assert_ne!(digest(&base, "hall").unwrap(), gate);
    assert_eq!(digest(&base, "kiln"), None);
}

/// An unclosed tag, an unclosed comment and a stray closing tag are read to the end, never past it.
#[test]
fn a_broken_sheet_is_read_to_its_end() {
    let m = read("</g>text<!-- open");
    assert_eq!(m.loose, ["</g>", "text"]);
    assert_eq!(read("<rect data-kind=\"a").loose, ["<rect data-kind=\"a"]);
}
