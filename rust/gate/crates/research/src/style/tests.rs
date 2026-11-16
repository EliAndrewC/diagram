//! The style guide's mechanical half (feature 449 T145; each expected value `style_prepass.py`'s on the same markup, 2026-11-16).

use std::collections::{BTreeMap, HashSet};

use super::{
    absence_sentences, foreign_in_own_text, glosses, gm_mentions, lead_line_years, lead_lines,
    long_paragraphs, old_absence, own_text, report, unconverted,
};

const HTML: &str = r#"<!-- GM 2026 note: 9 m -->
<p>A wall 3.5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根 (kakine, "hedge") and 石垣 alone; 「quoted 5 m」 and <q>said 6 m</q> &quot;7 m&quot; "8 m".<sup data-note="abs">x</sup> A guess here.<sup data-note="abs"></sup> Next.</p>
<ul><li><strong>In 1650 the town?</strong><br>Body text here about 1650 and more.</li>
<li><strong>A plain statement in 1700</strong><br>Its body.<ul><li>inner</li></ul></li></ul>
<p>word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word</p><li>short</li>
<span class="orig">原文 5 m</span> 屋敷 (yashiki, &quot;estate&quot;) 門 (mon, “gate”)"#;
const NOTES: &str = r#"<li data-note="abs">no publicly readable source (searched 2026: x)</li>
<li data-note="ok">no publicly readable source, still</li>
<li data-note="k">「原文」 and 庭 garden</li>"#;
const WANT: &str = r#"{"own_text": " A wall 3.5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根 (kakine, «hedge») and 石垣 alone; and . x A guess here. Next. In 1650 the town? Body text here about 1650 and more. A plain statement in 1700 Its body. inner word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word short 屋敷 (yashiki, «estate») 門 (mon, «gate»)", "foreign": ["石垣 - ...'s word stood. 垣根 (kakine, «hedge») and 石垣 alone; and . x A gu..."], "glosses": [["垣根", "kakine", "hedge"], ["屋敷", "yashiki", "estate"], ["門", "mon", "gate"]], "unconverted": ["3.5 m - ...A wall 3.5 m high (~11 ft), a moat 2-4 km...", "2-4 km - ...A wall 3.5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5...", "10 ha - ...5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1...", "1,200 to 1,500 meters - ...ide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根...", "5 m - ...word word word word word word word word short 原文 5 m 屋敷 (yashiki, ) 門 (mon, “gate”..."], "gm": ["...f rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根 (kakine, \"hedge\") and 石垣 alone; 「quoted 5 m」..."], "long": ["151 words - word word word word word word word word word word word word word word..."], "absence": ["[abs, abs] The GM's word stood. 垣根 (kakine, \"hedge\") and 石垣 alone; 「quoted 5 m」 and said 6 m &quot;7 m&quot; \"8 m\".x A guess here."], "years": ["1650 (a glossary tooltip) - In 1650 the town?", "1700 (NOT in the glossary) - A plain statement in 1700"], "leads": ["Q  In 1650 the town?  |  Body text here about 1650 and more.", "S  A plain statement in 1700  |  Its body."], "old": ["abs"], "report": "== 0001-a.html\nMETRIC WITHOUT A CONVERSION (5) - each is a FAIL of STYLE.md 6:\n  3.5 m - ...A wall 3.5 m high (~11 ft), a moat 2-4 km...\n  2-4 km - ...A wall 3.5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5...\n  10 ha - ...5 m high (~11 ft), a moat 2-4 km wide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1...\n  1,200 to 1,500 meters - ...ide, a field of 10 ha and 5 mm (~0.2 in) of rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根...\n  5 m - ...word word word word word word word word short 原文 5 m 屋敷 (yashiki, ) 門 (mon, “gate”...\nGM IN THE VISIBLE TEXT (1) - each is a FAIL of STYLE.md 1 (the ruling goes in a comment):\n  ...f rain; 1,200 to 1,500 meters away. The GM's word stood. 垣根 (kakine, \"hedge\") and 石垣 alone; 「quoted 5 m」...\nPARAGRAPH OVER 150 WORDS (1) - each is a FAIL of STYLE.md 3 (split it, or make it a list):\n  151 words - word word word word word word word word word word word word word word...\nABSENCE NOTE IN THE OLD FORM (1) - each is a FAIL of STYLE.md 7 (search into a comment, findings visible):\n  abs\nKANJI WITHOUT ITS GLOSS (2) - each is a FAIL of STYLE.md 5: follow it with (romaji, \"English meaning\"), or drop it:\n  石垣 - ...'s word stood. 垣根 (kakine, «hedge») and 石垣 alone; and . x A gu...\n  庭 - ...no publicly readable source, still and 庭 garden...\nSENTENCES RESTING ON AN ABSENCE NOTE (1) - rule on each: a silence or our own GUESS, never what an unread page says:\n  [abs, abs] The GM's word stood. 垣根 (kakine, \"hedge\") and 石垣 alone; 「quoted 5 m」 and said 6 m &quot;7 m&quot; \"8 m\".x A guess here.\nYEARS IN LEAD LINES (2) - rule on each: is its significance given in the line, or by its tooltip?\n  1650 (a glossary tooltip) - In 1650 the town?\n  1700 (NOT in the glossary) - A plain statement in 1700\nLEAD LINES (2) - rule on each: statement or question (STYLE.md 3), and readable from what precedes it:\n  Q  In 1650 the town?  |  Body text here about 1650 and more.\n  S  A plain statement in 1700  |  Its body.\n== 0002-b.html\nMETRIC WITHOUT A CONVERSION (0) - each is a FAIL of STYLE.md 6:\n  none\nGM IN THE VISIBLE TEXT (0) - each is a FAIL of STYLE.md 1 (the ruling goes in a comment):\n  none\nPARAGRAPH OVER 150 WORDS (0) - each is a FAIL of STYLE.md 3 (split it, or make it a list):\n  none\nABSENCE NOTE IN THE OLD FORM (0) - each is a FAIL of STYLE.md 7 (search into a comment, findings visible):\n  none\nKANJI WITHOUT ITS GLOSS (0) - each is a FAIL of STYLE.md 5: follow it with (romaji, \"English meaning\"), or drop it:\n  none\nSENTENCES RESTING ON AN ABSENCE NOTE (0) - rule on each: a silence or our own GUESS, never what an unread page says:\n  none\nYEARS IN LEAD LINES (0) - rule on each: is its significance given in the line, or by its tooltip?\n  none\nLEAD LINES (0) - rule on each: statement or question (STYLE.md 3), and readable from what precedes it:\n  none\n"}"#;

#[test]
fn every_list_is_the_pythons() {
    let want: serde_json::Value = serde_json::from_str(WANT).unwrap();
    let list = |v: &Vec<String>| serde_json::json!(v);
    assert_eq!(serde_json::json!(own_text(HTML)), want["own_text"]);
    assert_eq!(list(&foreign_in_own_text(HTML)), want["foreign"]);
    let g: Vec<serde_json::Value> = glosses(HTML)
        .into_iter()
        .map(|(a, b, c)| serde_json::json!([a, b, c]))
        .collect();
    assert_eq!(serde_json::json!(g), want["glosses"]);
    assert_eq!(list(&unconverted(HTML)), want["unconverted"]);
    assert_eq!(list(&gm_mentions(HTML)), want["gm"]);
    assert_eq!(list(&long_paragraphs(HTML)), want["long"]);
    assert_eq!(list(&absence_sentences(HTML, NOTES)), want["absence"]);
    let known: HashSet<String> = ["1650".to_owned()].into();
    assert_eq!(list(&lead_line_years(HTML, &known)), want["years"]);
    assert_eq!(list(&lead_lines(HTML)), want["leads"]);
    assert_eq!(list(&old_absence(NOTES)), want["old"]);
    let notes: BTreeMap<String, String> = [("0001-a.html".to_owned(), NOTES.to_owned())].into();
    let fragments = vec![
        ("0001-a.html".to_owned(), HTML.to_owned()),
        ("0002-b.html".to_owned(), "<p>plain</p>".to_owned()),
    ];
    assert_eq!(
        serde_json::json!(report(&fragments, &known, &notes)),
        want["report"]
    );
}
