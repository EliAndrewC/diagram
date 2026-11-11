//! The claim grammar: each backing, each refusal, the section reader's flat, indented and carried forms.

use super::{claims_of, expandtabs, parse_claim, partition, section_lines};

#[test]
fn each_backing_parses_and_each_wrong_one_is_refused() {
    let c = parse_claim("  dry   share - research/questions/0033-row-villages.html, research/questions/0034-x.drawing.html: rolled ").unwrap();
    assert_eq!(
        (
            c.label.as_str(),
            c.backing.as_str(),
            c.pointers.len(),
            c.account.as_str()
        ),
        ("dry share", "POINTER", 2, "rolled")
    );
    assert_eq!(
        c.normalized(),
        "dry share - row-villages, x.drawing: rolled"
    );
    let g = parse_claim("g - GUESS research/questions/0001-a.drawing.html: ours").unwrap();
    assert_eq!((g.backing.as_str(), g.pointers.len()), ("GUESS", 1));
    assert_eq!(parse_claim("n - NONE").unwrap().backing, "NONE");
    let d = parse_claim("d - DEVIATION research/questions/0001-a.html").unwrap();
    assert_eq!(d.backing, "DEVIATION");
    for (bad, why) in [
        ("no dash", "has no `<label> - <backing>`"),
        (" - NONE", "has no `<label> - <backing>`"),
        ("x - ", "has no `<label> - <backing>`"),
        (
            "g - GUESS research/questions/0001-a.html",
            "names the drawing page",
        ),
        (
            "n - NONE research/questions/0001-a.html",
            "`NONE` takes no pointer",
        ),
        ("d - DEVIATION", "is not question files or a class"),
        ("p - somewhere", "is not question files or a class"),
    ] {
        assert!(parse_claim(bad).unwrap_err().contains(why), "{bad}");
    }
    assert_eq!(partition("a: b", ": "), ("a", true, "b"));
    assert_eq!(partition("a", ": "), ("a", false, ""));
}

#[test]
fn a_section_is_read_flat_indented_or_carried() {
    assert_eq!(section_lines(None), None);
    assert_eq!(section_lines(Some("")), None);
    assert_eq!(section_lines(Some("no section here")), None);
    let indented = "Doc.\n\nResearch:\n    a - NONE\n    b - GUESS\n        continued deeper\n    c line with no dash\nafter";
    assert_eq!(
        section_lines(Some(indented)).unwrap(),
        vec!["a - NONE", "b - GUESS continued deeper c line with no dash"]
    );
    let flat = "Research:\na - NONE\ncontinued\nb - GUESS\n\nprose";
    assert_eq!(
        section_lines(Some(flat)).unwrap(),
        vec!["a - NONE continued", "b - GUESS"]
    );
    let flat_first = "Research:\nno dash first\nthen - NONE";
    assert_eq!(
        section_lines(Some(flat_first)).unwrap(),
        vec!["no dash first", "then - NONE"]
    );
    let flat_carried =
        "Research: one claim - research/questions/0001-a.html: runs\non to here\nnext - NONE";
    assert_eq!(
        section_lines(Some(flat_carried)).unwrap(),
        vec![
            "one claim - research/questions/0001-a.html: runs on to here",
            "next - NONE"
        ]
    );
    let carried = "x\nResearch: one claim - NONE\non to here\nnext - NONE";
    assert_eq!(
        section_lines(Some(carried)).unwrap(),
        vec!["one claim - NONE on to here"]
    );
    let shallower = "x\nResearch:\n        deep - NONE\n    shallow - NONE\n            deeper - x";
    assert_eq!(
        section_lines(Some(shallower)).unwrap(),
        vec!["deep - NONE", "shallow - NONE deeper - x"]
    );
    assert_eq!(
        expandtabs("a\tb\n\tc\r\td"),
        "a       b\n        c\r        d"
    );
}

#[test]
fn claims_and_their_errors_come_from_one_docstring() {
    let (claims, errors) = claims_of(Some("Research:\n    a - NONE\n    bad one"));
    assert_eq!(
        (claims.len(), errors),
        (
            0,
            vec!["`a - NONE bad one`: `NONE` takes no pointer".to_owned()]
        )
    );
    assert_eq!(
        claims_of(Some("Research:\n    a - NONE\n    b - GUESS"))
            .0
            .len(),
        2
    );
    let (claims, errors) = claims_of(Some("x\nResearch:\n    nodash - here - NONE x\n"));
    assert_eq!((claims.len(), errors), (0, vec!["`nodash - here - NONE x`: the backing `here - NONE x` is not question files or a class".to_owned()]));
    let (claims, errors) = claims_of(Some("x\nResearch:\n\ny"));
    assert_eq!(
        (claims.len(), errors),
        (0, vec!["an empty `Research:` section".to_owned()])
    );
    assert_eq!(claims_of(None), (Vec::new(), Vec::new()));
}
