//! The place card's own edges (feature 449 T150); part A's page lockstep held the card, its sentences and its counts to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`) on every
//! pool hamlet and every tier of the legacy pool.
//!
//! Research: the place card's tests - NONE: fixtures and assertions, deciding nothing about a building

use serde_json::json;

use super::{dwellings_shown, format_what, grouped, population_int, size_sentence, Kind};

fn kind(excludes: bool) -> Kind {
    Kind {
        noun: "town".into(),
        what: String::new(),
        houses_noun: "dwellings".into(),
        excludes_farms: excludes,
        population_note: String::new(),
        default_population: json!(null),
    }
}

#[test]
fn a_tier_s_text_formats_as_str_format_does() {
    assert_eq!(
        format_what("{{a}} {HAMLETS_PER_DOMAIN:,} {VILLAGES_PER_DOMAIN} {HAMLET_SHARE}").unwrap(),
        "{a} 1,296 216 40%"
    );
    assert_eq!(format_what("{NOPE}").unwrap_err().kind, "KeyError");
    assert_eq!(
        format_what("{HAMLET_SHARE:,}").unwrap_err().kind,
        "ValueError"
    );
    assert_eq!(
        format_what("{VILLAGES_PER_DOMAIN:x}").unwrap_err().kind,
        "ValueError"
    );
    assert_eq!(format_what("a } b").unwrap_err().kind, "ValueError");
    assert_eq!(grouped(-1_234_567), "-1,234,567");
}

#[test]
fn a_population_is_read_as_int_reads_it() {
    assert_eq!(population_int(&json!(7)).unwrap(), 7);
    assert_eq!(population_int(&json!(7.9)).unwrap(), 7);
    assert_eq!(population_int(&json!(" 1_200 ")).unwrap(), 1200);
    assert_eq!(population_int(&json!("x")).unwrap_err().kind, "ValueError");
    assert_eq!(population_int(&json!([1])).unwrap_err().kind, "TypeError");
    let m = json!({"households": 3}).as_object().unwrap().clone();
    assert_eq!(
        size_sentence(&kind(false), &m, 0).unwrap(),
        "population ~15"
    );
}

#[test]
fn a_count_takes_the_length_python_measures() {
    assert_eq!(
        dwellings_shown(&json!({"houses": {"a": 1, "b": 2}}), &kind(false)).unwrap(),
        2
    );
    assert_eq!(
        dwellings_shown(&json!({"houses": 1.5}), &kind(false))
            .unwrap_err()
            .kind,
        "TypeError"
    );
}

/// FIXED (feature 449 T183, T150's finding): a households value given as text was multiplied as Python multiplies a string - `"12"`
/// five times over, a population of 1,212,121,212 - and never equaled the drawn count. It is read as the number it names, as `int()`
/// reads it, and refused in `int()`'s words when it names none.
#[test]
fn a_households_text_is_read_as_its_number() {
    let meta = |v: serde_json::Value| json!({ "households": v }).as_object().unwrap().clone();
    let k = kind(false);
    assert_eq!(
        size_sentence(&k, &meta(json!("12")), 66).unwrap(),
        "66 dwellings, about 12 households, population ~60"
    );
    assert_eq!(
        size_sentence(&k, &meta(json!(" 66 ")), 66).unwrap(),
        "66 dwellings, population ~330"
    );
    assert_eq!(
        size_sentence(&k, &meta(json!(66)), 66).unwrap(),
        "66 dwellings, population ~330"
    );
    assert_eq!(
        size_sentence(&k, &meta(json!("0")), 3).unwrap(),
        "3 dwellings"
    );
    // an empty text is no households, as the Python's truth test read it
    assert_eq!(
        size_sentence(&k, &meta(json!("")), 3).unwrap(),
        "3 dwellings"
    );
    let e = size_sentence(&k, &meta(json!("about 12")), 3).unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        (
            "ValueError",
            "invalid literal for int() with base 10: 'about 12'"
        )
    );
}
