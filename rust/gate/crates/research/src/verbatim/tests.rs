//! `quote_verbatim`'s reading of a note (feature 449 T145; each expected value `quote_verbatim.py`'s on the same input, 2026-11-16).

use serde_json::json;

use super::{
    assertions, classify, decode, footnotes, head, is_wanted, passages, render, squeeze,
    strip_markup, top_level_quotes, visible_text, wanted, Passage,
};

fn p(quote: &str, original: &str, language: &str) -> Passage {
    Passage {
        quote: quote.into(),
        original: original.into(),
        language: language.into(),
        more: None,
    }
}

#[test]
fn text_is_squeezed_as_the_python_squeezed_it() {
    assert_eq!(squeeze("  a \t\x1c b\n"), "a b");
    assert_eq!(squeeze("\u{fa4c} \u{2f76}"), "\u{793e}\u{7c73}");
    assert_eq!(squeeze("\u{3042} \u{3044} a b"), "\u{3042}\u{3044} a b");
    assert_eq!(
        visible_text("<p>A</p><script>x</script><b>b</b> &amp; c"),
        "A b & c"
    );
    assert_eq!(head("abc", 2), "ab");
    assert_eq!(head("ab", 5), "ab");
}

/// 449 T197: a PDF line broken between a kana and a digit (okada-bitchu-2004's 「割合は\n18.23％」) kept its space, and a correct
/// quotation failed; the gap closes between a CJK character and a digit either way, and stays between two digits or Latin words.
#[test]
fn a_line_break_between_a_cjk_character_and_a_digit_is_squeezed_out() {
    assert_eq!(squeeze("割合は 18.23％"), "割合は18.23％");
    assert_eq!(squeeze("18.23 ％で"), "18.23％で");
    assert_eq!(squeeze("1 2 a 3"), "1 2 a 3");
}

/// 449 T257: a page's `m<sup>2</sup>` reads as `m2` in its visible text, where a quotation writes the superscript digit
/// `m²` (shakkanho-jawiki's 「≒ 3.305785 m²」); a superscript digit folds to its digit on both sides, as NFKC folds it.
#[test]
fn a_superscript_digit_reads_as_the_digit_a_sup_tag_leaves() {
    assert_eq!(squeeze("3.305785 m²"), "3.305785 m2");
    assert_eq!(squeeze("10³ x¹ y⁴"), "103 x1 y4");
}

#[test]
fn a_page_decodes_by_its_charset_then_the_suspects() {
    assert_eq!(
        decode("caf\u{e9}".as_bytes(), "").as_deref(),
        Some("caf\u{e9}")
    );
    assert_eq!(
        decode(b"caf\xe9", "iso-8859-1").as_deref(),
        Some("caf\u{e9}")
    );
    assert_eq!(
        decode(b"<META charset='Shift_JIS'>\x93\xfa", "").as_deref(),
        Some("<META charset='Shift_JIS'>\u{65e5}")
    );
    assert_eq!(
        decode(b"\x93\xfa\x96\x7b", "nonsense").as_deref(),
        Some("\u{65e5}\u{672c}")
    );
    assert_eq!(
        decode(b"\xa4\xa2", " UTF-8 ").as_deref(),
        Some("\u{ff64}\u{ff62}")
    );
    assert_eq!(decode(b"\x81", ""), None);
}

#[test]
fn the_outermost_quotes_are_found() {
    let chars: Vec<char> =
        "a \u{300c}x\u{300c}y\u{300d}z\u{300d} \"q\" \u{300c}open \u{201c}c\u{201d}"
            .chars()
            .collect();
    assert_eq!(top_level_quotes(&chars), vec![(2, 9), (10, 13), (20, 23)]);
}

#[test]
fn a_notes_passages_and_their_originals() {
    assert_eq!(
        passages("\u{300c}one\u{300d} (a gloss \u{300c}two\u{300d})"),
        vec![p("one", "", "")]
    );
    assert_eq!(
        passages("\u{300c}the hedge\u{300d} (translated; original: \u{300c}\u{57a3}\u{300d})"),
        vec![p("the hedge", "\u{57a3}", "")]
    );
    assert_eq!(
        passages("\u{300c}a\u{300d} (translated from the Old Chinese (Han) by Legge; original: \u{300c}x\u{300d} \u{300c}y\u{300d})")[0],
        Passage { more: Some(vec!["y".into()]), ..p("a", "x", "the Old Chinese (Han)") }
    );
    assert_eq!(
        passages("\u{300c}Q1\u{300d} and \u{300c}Q2\u{300d} (title translated; original: \u{300c}O1\u{300d} and original: \u{300c}O2\u{300d})"),
        vec![p("Q1", "O1", ""), p("Q2", "O2", "")]
    );
    // a run whose parenthetical holds too few originals, or a joiner that is no joiner, is read one quote at a time
    assert_eq!(
        passages(
            "\u{300c}Q1\u{300d}; \u{300c}Q2\u{300d} (translated; original: \u{300c}O1\u{300d})"
        )
        .len(),
        2
    );
    assert_eq!(
        passages("\u{300c}Q1\u{300d} and \u{300c}Q2\u{300d} (translated; original: \u{300c}O1\u{300d} x \u{300c}O2\u{300d})").len(),
        2
    );
    assert_eq!(
        passages("\u{300c}Q1\u{300d} and \u{300c}Q2\u{300d}"),
        vec![p("Q1", "", ""), p("Q2", "", "")]
    );
    assert_eq!(
        passages("\u{300c}Q1\u{300d} and \u{300c}Q2\u{300d} (x \u{300c}O1\u{300d} \u{300c}O2\u{300d} \u{300c}O3\u{300d})"),
        vec![p("Q1", "", ""), p("Q2", "", "")]
    );
    assert_eq!(
        passages("\u{300c}Q1\u{300d} and \u{300c}Q2\u{300d} (translated from Dutch by Ann; original: \u{300c}O1\u{300d} and \u{300c}O2\u{300d})"),
        vec![p("Q1", "O1", "Dutch"), p("Q2", "O2", "Dutch")]
    );
    assert!(p("a", "", "").to_json().get("more").is_none());
    assert_eq!(
        Passage {
            more: Some(vec!["m".into()]),
            ..p("a", "b", "")
        }
        .to_json()["more"],
        json!(["m"])
    );
}

#[test]
fn a_note_is_classified() {
    assert_eq!(classify("No publicly readable source here", &[]), "absence");
    assert_eq!(classify("no source is owed: x", &[]), "grounds");
    assert_eq!(classify("x", &[]), "unlinked");
    assert_eq!(classify("x", &["u".into()]), "citation");
    assert_eq!(strip_markup("<b>a</b><!-- c --> &amp; b"), "a & b");
}

#[test]
fn the_footnotes_and_the_sentences_they_close() {
    let cites = "<li id=\"fn-1\"><a href=\"https://e.org/a?b=1&amp;c=2\"><code>k-1</code></a> - \u{300c}quoted\u{300d} <a class=\"fnback\" href=\"#r\">back</a></li>\n<li id=\"fn-2\">no publicly readable source (x)</li>";
    let notes = footnotes(cites);
    assert_eq!(notes[0]["links"], json!(["https://e.org/a?b=1&c=2"]));
    assert_eq!(notes[0]["key"], "k-1");
    assert_eq!(notes[0]["passages"][0]["quote"], "quoted");
    assert_eq!(notes[1]["class"], "absence");
    assert_eq!(notes[1]["key"], "");
    let page = "<p>First. Then the claim.<sup class=\"fn\"><a href=\"#fn-1\">1</a></sup> Again<sup class=\"fn\"><a href=\"#fn-1\">1</a></sup></p><!-- <sup class=\"fn\"><a href=\"#fn-9\">9</a></sup> --><li>Two<sup class=\"fn\"><a href=\"#fn-2\">2</a></sup></li>";
    let said = assertions(page);
    assert_eq!(said["fn-1"], "Then the claim.");
    assert_eq!(said["fn-2"], "Two");
    assert!(!said.contains_key("fn-9"));
}

#[test]
fn the_notes_a_run_is_asked_for() {
    let ids = wanted(" 2-4, fn-7,k-a-2 ,9-").unwrap();
    assert!(
        ids.contains("fn-3")
            && ids.contains("fn-7")
            && ids.contains("fn-9")
            && ids.contains("key:k-a")
            && ids.contains("key:k-a-2")
    );
    assert!(ids.contains("key:9-") || ids.contains("fn-9"));
    assert_eq!(wanted(" , "), None);
    assert!(wanted("\u{0663}").unwrap().contains("fn-3"));
    let note = json!({"id": "fn-3", "key": "k"});
    let note = note.as_object().unwrap();
    assert!(is_wanted(note, None));
    assert!(is_wanted(note, Some(&ids)));
    assert!(!is_wanted(
        json!({"id": "fn-1", "key": "z"}).as_object().unwrap(),
        Some(&ids)
    ));
}

#[test]
fn a_report_is_rendered() {
    let entries = vec![
        json!({"id": "fn-1", "key": "a", "class": "citation", "passages": [
            {"quote": "q", "original": "", "matched": "quote", "quotation": "VERBATIM"},
            {"quote": "q", "original": "o", "matched": "original", "quotation": "DIFFERS", "page_text": "p", "differences": ["d1", "d2"], "only_reference_markers": true},
            {"quote": "r", "original": "", "matched": "quote", "quotation": "DIFFERS", "page_text": "p", "differences": [], "only_reference_markers": false},
            {"quote": "w", "original": "", "matched": "quote", "quotation": "NOT-CHECKED", "why": "a PDF"},
            {"quote": "n", "original": "", "matched": "quote", "quotation": "NOT-ON-PAGE"}]}),
        json!({"id": "fn-2", "key": "b", "class": "citation", "passages": []}),
        json!({"id": "fn-3", "key": "", "class": "absence", "passages": []}),
    ];
    let entries: Vec<_> = entries
        .into_iter()
        .map(|e| e.as_object().unwrap().clone())
        .collect();
    let refused = vec![
        ("z.org".to_owned(), "no".to_owned()),
        ("a.org".to_owned(), "x".to_owned()),
    ];
    let text = render("questions/x.html", &entries, &refused);
    assert_eq!(
        text,
        "quote-verbatim: questions/x.html - 3 footnotes\n  fn-1 a - DIFFERS (original): o\n      page has: p\n      d1; d2   [only the page's reference markers differ]\n  fn-1 a - DIFFERS (quote): r\n      page has: p\n      \n  fn-1 a - NOT-CHECKED (quote): w\n      a PDF\n  fn-1 a - NOT-ON-PAGE (quote): n\n  fn-2 b - NO-QUOTE: a citation that quotes nothing\n  DIFFERS 2, NO-QUOTE 1, NOT-CHECKED 1, NOT-ON-PAGE 1, VERBATIM 1, absence 1\n  refused: a.org - x\n  refused: z.org - no"
    );
}
