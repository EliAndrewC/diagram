//! The item tags (feature 451 T187).

use super::{faults, items, strip, Item};

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
    // a block holding a guess and a deviation tags each (451 T192: 27 such blocks on 22 drawing pages, measured 2026-11-23 by
    // `.git/t192/tag.py`'s label words); the deviation's own word is what its tag needs
    let dev = format!(
        "<li>Ours, a GUESS and a deviation.{}{}</li>",
        tag("d", "DEVIATION", ""),
        tag("g", "GUESS", "That it is ours: no page says")
    );
    assert!(faults("p.html", &dev).is_empty());
    let no_word = format!("<li>Ours, a GUESS.{}</li>", tag("d", "DEVIATION", ""));
    assert!(faults("p.html", &no_word)[0].contains("says DEVIATION"));
}

#[test]
fn a_bad_id_a_twice_tagged_id_and_an_unknown_label_are_refused() {
    let html = format!(
        "<li>a GUESS{}</li><li>a GUESS{}</li><li>a GUESS{}</li><li>x{}</li>",
        tag("Bad Id", "GUESS", "b"),
        tag("dup", "GUESS", "b"),
        tag("dup", "GUESS", "b"),
        tag("odd", "MAYBE", ""),
    );
    let f = faults("p.html", &html);
    assert_eq!(f.len(), 3, "{f:?}");
    assert!(f[0].contains("lowercase slug"));
    assert!(f[1].contains("tagged twice"));
    assert!(f[2].contains("`MAYBE` is not one of"));
}

/// A GUESS tag's bullet is owed only where a pop-up references the item (451 T192, the GM's cheap route 2026-11-24): an unreferenced
/// tag names its item and label alone, and the registry refuses a reference to a tag with no `data-guess`.
#[test]
fn a_guess_tag_with_no_bullet_is_no_fault_on_its_page() {
    let html = format!(
        "<li>a GUESS{}</li><li>a GUESS{}</li>",
        tag("bare", "GUESS", " "),
        r#"<span class="item" data-item="none" data-label="GUESS"></span>"#
    );
    assert_eq!(faults("p.html", &html), Vec::<String>::new());
}

/// Tagging moves nothing a pop-up's fingerprint reads (feature 451 T192): `strip` takes every well-formed tag out and leaves a malformed
/// one, which then stays visible.
#[test]
fn strip_takes_out_each_well_formed_tag_and_leaves_a_malformed_one() {
    let bare = "<li><strong>A gate.</strong> Guarded, a GUESS.</li>";
    let tagged = bare.replace(
        "</li>",
        &format!(
            "{}</li>",
            tag("gate", "GUESS", "That it is guarded: no page says")
        ),
    );
    assert_ne!(tagged, bare);
    assert_eq!(strip(&tagged), bare);
    let malformed = r#"<li>x<span class="item" data-item="g">y</span></li>"#;
    assert_eq!(strip(malformed), malformed);
}

#[test]
fn an_unresearched_tag_is_a_fifth_label_its_block_saying_so() {
    // feature 451 T236 (the GM 2026-11-25): UNRESEARCHED, not yet searched, beside a GUESS, searched and silent
    let html = format!(
        "<li>The fence's height is UNRESEARCHED: no search has run.{}</li>",
        tag("fence", "UNRESEARCHED", "")
    );
    assert_eq!(faults("p.html", &html), Vec::<String>::new());
    assert_eq!(items(&html)[0].label, "UNRESEARCHED");
    // a block that does not say it is refused, as a GUESS's is
    let silent = html.replace("UNRESEARCHED: no", "four feet: no");
    let f = faults("p.html", &silent);
    assert_eq!(f.len(), 1, "{f:?}");
    assert!(f[0].contains("its tag says UNRESEARCHED"), "{f:?}");
    // an ATTESTED block that calls itself unresearched says another label
    let attested = html.replace(r#"data-label="UNRESEARCHED""#, r#"data-label="ATTESTED""#);
    assert_eq!(faults("p.html", &attested).len(), 1);
}
