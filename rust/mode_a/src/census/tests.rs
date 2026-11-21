//! The notes census's port (feature 449 T170): the block, its refusals on a manifest of the wrong shape, the command, and the typed
//! counts - each expected value the deleted Python's on the same input (observed 2026-11-17, `notes_census.py` at HEAD run on each).
//!
//! Research:
//!     the notes census's tests - NONE: fixtures and assertions, deciding nothing about the place

use std::os::unix::fs::PermissionsExt as _;

use serde_json::{json, Value};

use super::{
    census, current_prose, fixed1, main, replace, sheet_counts, sheet_prose, stale_counts,
    stale_sheet_counts, stem, BEGIN, END,
};
use crate::py::uncaught;

fn refusal<T: std::fmt::Debug>(r: Result<T, l7r_gate_research::Error>) -> String {
    uncaught(&r.unwrap_err()).trim_end().to_owned()
}

fn manifest() -> Value {
    json!({
        "houses": [{"x": 0, "y": 0}, {"x": "100", "y": 0.5}, {"x": true, "y": 300}],
        "village_groves": [{"role": "windbreak", "clumps": [1, 2], "clumps_offpage": [1]}, {"role": "windbreak", "clumps": "abc"},
                           {"clumps": {"a": 1}}],
        "meta": {"family_form": "stem"}, "retirement_houses": [1],
        "farm_fixtures": [{"form": "privy"}, {"kind": "woodpile"}, {}, {"form": 0, "kind": 3}, {"form": 2.5}], "farm_sheds": [1, 2],
        "kosatsuba": [{"x": 10, "y": -0.04}, "skip", {"x": "1e3", "y": 2.25}], "byres": [1], "wells": [], "bridges": [1, 2]
    })
}

#[test]
fn the_block_is_the_python_s() {
    assert_eq!(
        census(&manifest()).unwrap(),
        "- windbreak: **5** clumps drawn, **1** off the page\n- copse: **1** clumps drawn\n- farmhouses: **3**\n- family form: **stem**, \
         retirement houses **1**\n- farmstead fixtures: 2.5 **1**, 3 **1**, None **1**, privy **1**, woodpile **1**\n- storehouses: **2** \
         of **3** farmhouses\n- notice board at **(10.0, -0.0)**, **2** of 3 farmhouses within 250 ft\n- notice board at **(1000.0, 2.2)**, \
         **0** of 3 farmhouses within 250 ft"
    );
    let odd = json!({"meta": {"family_form": null}, "farm_fixtures": [{"form": [1, "a"]}, {"kind": {"a": null}}, {"form": true}]});
    assert_eq!(
        census(&odd).unwrap(),
        "- windbreak: **0** clumps drawn, **0** off the page\n- copse: **0** clumps drawn\n- farmhouses: **0**\n- family form: **None**, \
         retirement houses **0**\n- farmstead fixtures: True **1**, [1, 'a'] **1**, {'a': None} **1**\n- storehouses: **0** of **0** farmhouses"
    );
    // the numbers Python's JSON reads past serde's: NaN, an infinity, an integer past 64 bits
    let kept = l7r_shared::pyjson::loads(
        r#"{"kosatsuba":[{"x":NaN,"y":Infinity}], "farm_fixtures":[{"form":NaN},{"form":123456789012345678901234567890}]}"#,
    )
    .unwrap();
    assert_eq!(
        census(&kept).unwrap(),
        "- windbreak: **0** clumps drawn, **0** off the page\n- copse: **0** clumps drawn\n- farmhouses: **0**\n- family form: **one_roof**, \
         retirement houses **0**\n- farmstead fixtures: 123456789012345678901234567890 **1**, nan **1**\n- storehouses: **0** of **0** \
         farmhouses\n- notice board at **(nan, inf)**, **0** of 0 farmhouses within 250 ft"
    );
    assert!(census(&json!({"meta": {"x": 1}}))
        .unwrap()
        .contains("family form: **one_roof**"));
    let huge = l7r_shared::pyjson::loads(
        r#"{"houses":[{"x":123456789012345678901234567890,"y":-Infinity}]}"#,
    )
    .unwrap();
    assert!(census(&huge).unwrap().contains("farmhouses: **1**"));
    assert_eq!(
        (
            fixed1(f64::NAN),
            fixed1(f64::NEG_INFINITY),
            fixed1(0.25),
            fixed1(0.35)
        ),
        ("nan".into(), "-inf".into(), "0.2".into(), "0.3".into())
    );
}

#[test]
fn a_manifest_of_the_wrong_shape_is_refused_in_the_python_s_words() {
    let cases = [
        (
            json!([]),
            "AttributeError: 'list' object has no attribute 'get'",
        ),
        (
            json!({"village_groves": ["x"]}),
            "AttributeError: 'str' object has no attribute 'get'",
        ),
        (json!({"village_groves": [{}]}), "KeyError: 'clumps'"),
        (
            json!({"village_groves": [{"clumps": 5}]}),
            "TypeError: object of type 'int' has no len()",
        ),
        (
            json!({"houses": [[1]]}),
            "TypeError: list indices must be integers or slices, not str",
        ),
        (
            json!({"houses": ["ab"]}),
            "TypeError: string indices must be integers, not 'str'",
        ),
        (
            json!({"houses": [5]}),
            "TypeError: 'int' object is not subscriptable",
        ),
        (
            json!({"houses": [{"x": [1], "y": 1}]}),
            "TypeError: float() argument must be a string or a real number, not 'list'",
        ),
        (
            json!({"houses": [{"x": "abc", "y": 1}]}),
            "ValueError: could not convert string to float: 'abc'",
        ),
        (json!({"houses": [{"y": 1}]}), "KeyError: 'x'"),
        (
            json!({"village_groves": 5}),
            "TypeError: 'int' object is not iterable",
        ),
        (
            json!({"retirement_houses": 5}),
            "TypeError: object of type 'int' has no len()",
        ),
        (
            json!({"meta": "x"}),
            "AttributeError: 'str' object has no attribute 'get'",
        ),
        (
            json!({"farm_fixtures": [1]}),
            "AttributeError: 'int' object has no attribute 'get'",
        ),
        (json!({"kosatsuba": [{"y": 1}]}), "KeyError: 'x'"),
    ];
    for (m, want) in cases {
        assert_eq!(refusal(census(&m)), want, "{m}");
    }
}

/// T171: an entrance board's line counts the households' ways out that pass it (feature 261 FR-015), not the farmhouses within 250 ft;
/// a board of any other seat keeps the 250-ft count.
#[test]
fn an_entrance_board_is_judged_by_the_ways_out_that_pass_it() {
    let lanes = json!([
        {"pts": [[-200, 0], [100, 0]], "connector": true},
        {"pts": [[100, 0], [100, 80]]},
        {"pts": [[100, 0], [250, 0]]}
    ]);
    let m = json!({
        "houses": [{"x": 110, "y": 85}, {"x": 255, "y": 10}, {"x": 900, "y": 900}],
        "lanes": lanes, "meta": {"kosatsuba_seat": "entrance"},
        "kosatsuba": [{"x": 100, "y": 70}, {"x": 100, "y": 5}]
    });
    let body = census(&m).unwrap();
    assert_eq!(
        body.lines().rev().take(2).collect::<Vec<_>>(),
        [
            "- notice board at the entrance, **(100.0, 5.0)**: **2** of 2 households' ways out pass it",
            "- notice board at the entrance, **(100.0, 70.0)**: **1** of 2 households' ways out pass it"
        ]
    );
    let center = json!({"houses": [{"x": 110, "y": 85}], "lanes": lanes, "meta": {"kosatsuba_seat": "center"},
                        "kosatsuba": [{"x": 100, "y": 70}]});
    assert!(census(&center)
        .unwrap()
        .ends_with("- notice board at **(100.0, 70.0)**, **1** of 1 farmhouses within 250 ft"));
    let bad =
        json!({"houses": [], "lanes": [{"pts": [[1]]}], "meta": {"kosatsuba_seat": "entrance"}});
    assert!(census(&bad).is_err());
}

#[test]
fn the_block_is_replaced_between_its_markers_only() {
    let m = json!({});
    let body = census(&m).unwrap();
    let text = format!("before\n{BEGIN}\nold\n{END}\nafter");
    assert_eq!(
        replace(&text, &m).unwrap(),
        format!("before\n{BEGIN}\n{body}\n{END}\nafter")
    );
    for unchanged in [
        "no block".to_owned(),
        format!("{END} then {BEGIN}"),
        format!("{BEGIN} only"),
    ] {
        assert_eq!(replace(&unchanged, &json!([])).unwrap(), unchanged);
    }
    assert_eq!(
        refusal(replace(&text, &json!([]))),
        "AttributeError: 'list' object has no attribute 'get'"
    );
}

#[test]
fn a_path_loses_its_extension_as_splitext_drops_it() {
    for (path, want) in [
        ("a/b.json", "a/b"),
        ("a/.json", "a/.json"),
        ("a.b/c", "a.b/c"),
        ("a/..b", "a/..b"),
        ("file", "file"),
        ("a.tar.gz", "a.tar"),
        ("..x.y", "..x"),
    ] {
        assert_eq!(stem(path), want, "{path}");
    }
}

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn the_command_rewrites_each_block_and_says_so() {
    let dir = l7r_shared::tempdir::TempDir::new("mode-a-census");
    let at = |name: &str| dir.path().join(name).to_string_lossy().into_owned();
    let block = format!("{BEGIN}\n{}\n{END}", census(&json!({})).unwrap());
    for (name, notes) in [
        (
            "stale",
            Some(format!("intro\r\n{BEGIN}\r\nold\r\n{END}\r\n")),
        ),
        ("none", None),
        ("plain", Some("no block\n".to_owned())),
        ("current", Some(format!("x\n{block}\n"))),
    ] {
        std::fs::write(at(&format!("{name}.json")), "{}").unwrap();
        if let Some(text) = notes {
            std::fs::write(at(&format!("{name}.notes.md")), text).unwrap();
        }
    }
    let r = main(&args(&[
        &at("stale.json"),
        &at("none.json"),
        &at("plain.json"),
        &at("current.json"),
    ]));
    assert_eq!(
        (r.code, r.stdout.as_str(), r.stderr.as_str()),
        (
            0,
            "  stale.notes.md: census refreshed\n  none.notes.md: no notes file\n  plain.notes.md: no census block\n  current.notes.md: \
             already current\nnotes-census: 1 file(s) rewritten\n",
            ""
        )
    );
    // read with universal newlines and written with Python's line ends
    assert_eq!(
        std::fs::read_to_string(at("stale.notes.md")).unwrap(),
        format!("intro\n{block}\n")
    );
    // a failure ends the run where it stands, the files before it rewritten
    std::fs::write(at("stale.notes.md"), format!("{BEGIN}{END}")).unwrap();
    let r = main(&args(&[
        &at("stale.json"),
        &at("missing.json"),
        &at("plain.json"),
    ]));
    assert_eq!(
        (r.code, r.stdout.as_str(), r.stderr),
        (
            1,
            "  stale.notes.md: census refreshed\n",
            format!(
                "FileNotFoundError: [Errno 2] No such file or directory: '{}'\n",
                at("missing.json")
            )
        )
    );
    std::fs::write(at("bad.json"), "{").unwrap();
    assert!(main(&args(&[&at("bad.json")]))
        .stderr
        .starts_with("json.decoder.JSONDecodeError: "));
    std::fs::write(at("stale.notes.md"), format!("{BEGIN}{END}")).unwrap();
    std::fs::set_permissions(at("stale.notes.md"), std::fs::Permissions::from_mode(0o444)).unwrap();
    let r = main(&args(&[&at("stale.json")]));
    assert_eq!(
        r.stderr,
        format!(
            "PermissionError: [Errno 13] Permission denied: '{}'\n",
            at("stale.notes.md")
        )
    );
    std::fs::write(at("list.json"), "[]").unwrap();
    std::fs::write(at("list.notes.md"), format!("{BEGIN}{END}")).unwrap();
    assert_eq!(
        main(&args(&[&at("list.json")])).stderr,
        "AttributeError: 'list' object has no attribute 'get'\n"
    );
    std::fs::write(at("binary.json"), "{}").unwrap();
    std::fs::write(at("binary.notes.md"), [0xff_u8]).unwrap();
    assert!(main(&args(&[&at("binary.json")]))
        .stderr
        .starts_with("UnicodeDecodeError: "));
    let r = main(&[]);
    assert_eq!(
        (r.code, r.stderr.starts_with("usage: notes_census.py")),
        (2, true)
    );
}

const NOTES: &str = "# Notes\nthree farmhouses here. Two Households. \n## 2026-08-11 history\n15 farmhouses old.\n## Current\n- 4 byres\n\
                     - 2026-09-01 the GM saw 9 wells\nseven persimmons and 0 privies, 2 wood sheds, twenty footbridges, 1 retirement houses, 5 \
                     homesteads\n";

#[test]
fn a_typed_count_is_held_to_the_manifest_and_history_is_exempt() {
    assert_eq!(
        current_prose(NOTES),
        "# Notes\nthree farmhouses here. Two Households. \n## Current\n\n- 4 byres"
    );
    assert_eq!(
        current_prose(&format!("a\n{BEGIN}\n7 wells\n{END}\nb")),
        "a\n\nb"
    );
    assert_eq!(
        stale_counts(NOTES, &manifest()).unwrap(),
        [
            "'Two Households' - the map ships 3 households",
            "'4 byres' - the map ships 1 byres"
        ]
    );
    let all = "1 farmhouses\n\n0 households\n\n9 homesteads\n\n2 retirement houses\n\n1 wells\n\n3 footbridges\n\n1 persimmons\n\n2 privies\n\n2 wood sheds";
    let m = json!({"houses": [1], "farm_fixtures": [{"kind": "privy"}, {"kind": "woodpile"}, {"kind": "woodpile"}], "persimmons": [1, 2]});
    assert_eq!(
        stale_counts(all, &m).unwrap(),
        [
            "'0 households' - the map ships 1 households",
            "'9 homesteads' - the map ships 1 homesteads",
            "'2 retirement houses' - the map ships 0 retirement houses",
            "'1 wells' - the map ships 0 wells",
            "'3 footbridges' - the map ships 0 footbridges",
            "'1 persimmons' - the map ships 2 persimmons",
            "'2 privies' - the map ships 1 privies"
        ]
    );
    // a digit of another script is its value, as `int()` reads it; a count of any length compared as written
    assert!(
        stale_counts("\u{663} farmhouses", &json!({"houses": [1, 2, 3]}))
            .unwrap()
            .is_empty()
    );
    assert!(
        stale_counts("0003 farmhouses", &json!({"houses": [1, 2, 3]}))
            .unwrap()
            .is_empty()
    );
    assert_eq!(
        stale_counts("00 byres", &json!({})).unwrap(),
        Vec::<String>::new()
    );
    assert_eq!(
        stale_counts("99999999999999999999999 byres", &json!({})).unwrap(),
        ["'99999999999999999999999 byres' - the map ships 0 byres"]
    );
    // the case-blind match takes the long s; `lower()` gives no word back, the Python's KeyError
    assert_eq!(
        refusal(stale_counts("\u{17f}ix wells", &json!({}))),
        "KeyError: '\u{17f}ix'"
    );
    assert_eq!(
        refusal(stale_counts("6 wellſ", &json!({}))),
        "KeyError: 'wellſ'"
    );
    assert_eq!(
        refusal(stale_counts("3 farmhouses", &json!([]))),
        "AttributeError: 'list' object has no attribute 'get'"
    );
    assert_eq!(
        refusal(stale_counts("3 privies", &json!({"farm_fixtures": [1]}))),
        "AttributeError: 'int' object has no attribute 'get'"
    );
}

/// A sheet drawing two tubs, a privy (its hatch beside it, of another fill) and a well, under a precinct.
const SHEET: &str = r##"<svg><rect id="precinct" x="0" y="0" width="99" height="99" fill="#fff"/>
<g fill="#8FB0C6"><circle cx="5" cy="5" r="2"/><circle cx="9" cy="5" r="2"/></g>
<g data-kind="latrine"><rect x="1" y="1" width="4" height="4" fill="#7E726A"/><rect x="6" y="1" width="2" height="2" fill="#000"/></g>
<rect x="20" y="1" width="4" height="4" fill="#9C8C70" data-kind="well"/><rect x="30" y="1" width="4" height="4" fill="#9C8C70"/></svg>"##;

#[test]
fn a_sheet_s_counts_are_its_tags_and_the_notes_are_held_to_them() {
    assert_eq!(
        sheet_counts(SHEET).unwrap(),
        [("tubs", 2), ("privies", 1), ("wells", 1)]
    );
    let notes = "Two tubs and 3 fire-water tubs. The house's two privies. 1 latrines, eleven wells.\n\n- 2026-07 four wells\n\n~5 tubs, 1-2 wells";
    assert_eq!(sheet_prose(notes), "Two tubs and 3 fire-water tubs. The house's two privies. 1 latrines, eleven wells.\n\n~5 tubs, 1-2 wells");
    assert_eq!(
        stale_sheet_counts(notes, SHEET).unwrap(),
        [
            "'3 fire-water tubs' - the sheet draws 2 tubs",
            "'eleven wells' - the sheet draws 1 wells"
        ]
    );
    // the part-of window is forty characters, no more
    let far = format!("the {} 7 tubs", "x".repeat(40));
    assert_eq!(
        stale_sheet_counts(&far, SHEET).unwrap(),
        ["'7 tubs' - the sheet draws 2 tubs"]
    );
    assert!(stale_sheet_counts("\u{6c34}\u{6c34} the 7 tubs", SHEET)
        .unwrap()
        .is_empty());
    assert_eq!(
        refusal(stale_sheet_counts("6 tub\u{17f}", SHEET)),
        "KeyError: 'tub\u{17f}'"
    );
    assert_eq!(
        refusal(stale_sheet_counts("", "<svg/>"))
            .split(" - ")
            .next()
            .unwrap(),
        "ValueError: no rect marked id=\"precinct\" in the SVG"
    );
    let bad = SHEET.replace("<svg>", "<svg><g transform=\"translate(.)\"><rect/></g>");
    assert_eq!(
        refusal(sheet_counts(&bad)),
        "ValueError: could not convert string to float: '.'"
    );
}
