//! The item tags (feature 451 T187).

use super::{faults, items, Item};

fn tag(id: &str, label: &str, guess: &str) -> String {
    format!(
        r#"<span class="item" data-item="{id}" data-label="{label}" data-guess="{guess}"></span>"#
    )
}

const PAGE: &str = r#"<h2 id="x">How our maps draw it</h2>
<ul>
<li><strong>A shrine in every compound.</strong><br>Accurate for every office.TAG1</li>
<li><strong>The tree beside it.</strong><br>That they give it a tree is a GUESS.TAG2</li>
</ul>
<p>One shrine, a deliberate deviation.TAG3</p>"#;

fn page() -> String {
    PAGE.replace("TAG1", &tag("shrine", "ATTESTED", ""))
        .replace(
            "TAG2",
            &tag(
                "tree",
                "GUESS",
                "The tree beside the shrine: no account gives it as the custom",
            ),
        )
        .replace("TAG3", &tag("one", "DEVIATION", ""))
}

#[test]
fn a_page_s_tags_read_with_their_blocks() {
    let got = items(&page());
    assert_eq!(got.len(), 3);
    assert_eq!(
        got[1],
        Item {
            id: "tree".into(),
            label: "GUESS".into(),
            guess: "The tree beside the shrine: no account gives it as the custom".into(),
            block: "The tree beside it. That they give it a tree is a GUESS.".into(),
        }
    );
    assert_eq!(got[2].block, "One shrine, a deliberate deviation.");
    let f = faults("p.html", &page());
    assert_eq!(f, Vec::<String>::new());
}

#[test]
fn an_entity_in_a_bullet_is_decoded_and_a_tag_outside_a_block_reads_the_page() {
    let html = format!("lead {} a GUESS", tag("x", "GUESS", "it&#x27;s ours"));
    let got = items(&html);
    assert_eq!(got[0].guess, "it's ours");
    assert_eq!(got[0].block, "lead a GUESS");
}

#[test]
fn a_tag_whose_block_says_another_label_is_refused() {
    let relabeled = page().replace(
        r#"data-item="tree" data-label="GUESS""#,
        r#"data-item="tree" data-label="ATTESTED""#,
    );
    let f = faults("p.html", &relabeled);
    assert_eq!(f.len(), 1, "{f:?}");
    let said = &f[0];
    assert!(said.contains("item `tree` - its tag says ATTESTED"),);
    let conv = format!("<li>A rule of ours.{}</li>", tag("c", "CONVENTION", ""));
    assert!(faults("p.html", &conv)[0].contains("says CONVENTION"));
    let conv_ok = format!(
        "<li>A convention of the drawing.{}</li>",
        tag("c", "CONVENTION", "")
    );
    assert!(faults("p.html", &conv_ok).is_empty());
    let dev = format!(
        "<li>Ours, a GUESS and a deviation.{}</li>",
        tag("d", "DEVIATION", "")
    );
    assert!(faults("p.html", &dev)[0].contains("says DEVIATION"));
}

#[test]
fn a_bad_id_a_twice_tagged_id_an_unknown_label_and_a_guess_with_no_bullet_are_refused() {
    let html = format!(
        "<li>a GUESS{}</li><li>a GUESS{}</li><li>a GUESS{}</li><li>x{}</li><li>a GUESS{}</li>",
        tag("Bad Id", "GUESS", "b"),
        tag("dup", "GUESS", "b"),
        tag("dup", "GUESS", "b"),
        tag("odd", "MAYBE", ""),
        tag("bare", "GUESS", " "),
    );
    let f = faults("p.html", &html);
    assert_eq!(f.len(), 4, "{f:?}");
    assert!(f[0].contains("lowercase slug"));
    assert!(f[1].contains("tagged twice"));
    assert!(f[2].contains("`MAYBE` is not one of"));
    assert!(f[3].contains("carries its Guesses bullet"));
}
