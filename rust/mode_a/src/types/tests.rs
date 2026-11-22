//! The building types' reader: the real declaration read, and each refusal in the words `types.py` gave (feature 449 T168; the lockstep
//! with `types.py` deleted with it, T212).
//!
//! Research:
//!     the building types' tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    by_tier, classification, hand_drawn_tiers, load_types, parse_types, tiers, Band, Kinds,
    RequiredItem, DECLARATION, NOTHING_GUESSED, PER_STATEMENT,
};

fn real() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// The real declaration reads, every type's tier unique, and its items name the kinds the sheets are tagged with (the lockstep with
/// `types.py` this replaced went with the Python, feature 449 T212).
#[test]
fn the_real_declaration_reads() {
    let types = load_types(&real()).unwrap();
    let tiers: std::collections::BTreeSet<&str> = types.iter().map(|t| t.tier.as_str()).collect();
    assert!(!types.is_empty() && tiers.len() == types.len());
    assert!(types
        .iter()
        .any(|t| t.required.iter().any(|i| i.kind.is_some())));
}

fn a_type() -> Value {
    json!({"tier": "t", "title": "T", "program": "p", "hand_drawn": true, "checks": ["c"],
           "required": [{"id": "a", "label": "hall", "band_ft": {"w": [1, 2], "h": [3, 4.5]}, "class": "guess", "why": "w"}]})
}

fn refused(data: &Value) -> String {
    let e = parse_types(data).unwrap_err();
    format!("{}: {}", e.kind, e.message)
}

fn with(f: impl FnOnce(&mut serde_json::Map<String, Value>)) -> Value {
    let mut t = a_type();
    f(t.as_object_mut().unwrap());
    json!([t])
}

fn with_item(f: impl FnOnce(&mut serde_json::Map<String, Value>)) -> Value {
    with(|t| f(t["required"][0].as_object_mut().unwrap()))
}

#[test]
fn a_type_is_read_with_its_defaults() {
    let t = &parse_types(&json!([a_type()])).unwrap()[0];
    assert_eq!(
        (t.tier.as_str(), t.hand_drawn, t.notes.as_str()),
        ("t", true, "")
    );
    assert!(t.generated_exceptions.is_empty() && t.map_keys.is_empty());
    let i = &t.required[0];
    assert_eq!(i.label.as_deref(), Some("hall"));
    assert_eq!(
        i.band,
        Band {
            w: Some((1.0, 2.0)),
            h: Some((3.0, 4.5)),
            area: None
        }
    );
    assert_eq!(
        (i.optional, i.site.as_deref(), i.kind.as_deref()),
        (false, None, None)
    );
    // what `str()` and `bool()` make of the other JSON values
    let t = &parse_types(&with(|t| {
        t.insert("notes".into(), Value::Null);
        t.insert("checks".into(), json!("ab"));
        t.insert("map_keys".into(), json!({"k": 1}));
        t.insert(
            "generated_exceptions".into(),
            json!([1, 2.5, true, null, [1]]),
        );
        t.insert("hand_drawn".into(), json!(0));
    }))
    .unwrap()[0];
    assert_eq!(t.notes, "None");
    assert_eq!(t.checks, ["a", "b"]);
    assert_eq!(t.map_keys, ["k"]);
    assert_eq!(t.generated_exceptions, ["1", "2.5", "True", "None", "[1]"]);
    assert!(!t.hand_drawn);
}

#[test]
fn an_item_reads_its_forms_site_and_kind() {
    let data = with(|t| {
        t["required"] = json!([
            {"id": "k", "kind": "office hall", "band_ft": {}, "site": "a_b", "optional": 1,
             "forms": {"x": null, "y": {"area": [1, 2]}}},
            {"id": "f", "kind": "k", "band_ft": {}, "forms": []}
        ]);
    });
    let t = &parse_types(&data).unwrap()[0];
    let i = &t.required[0];
    assert_eq!(
        (i.kind.as_deref(), i.site.as_deref(), i.optional),
        (Some("office hall"), Some("a_b"), true)
    );
    assert_eq!(i.label, None);
    assert!(i.band.presence_only());
    assert_eq!(i.forms[0], ("x".to_owned(), None));
    assert_eq!(i.band_for(Some("x")), None);
    assert_eq!(i.band_for(Some("y")).unwrap().area, Some((1.0, 2.0)));
    assert_eq!(i.band_for(Some("z")), Some(i.band));
    assert_eq!(i.band_for(None), Some(i.band));
    assert!(t.required[1].forms.is_empty());
}

#[test]
fn a_band_holds_a_footprint_either_way() {
    let b = Band {
        w: Some((10.0, 20.0)),
        h: Some((5.0, 8.0)),
        area: Some((60.0, 120.0)),
    };
    assert!(b.holds(12.0, 6.0) && b.holds(6.0, 12.0));
    assert!(!b.holds(12.0, 12.0) && !b.holds(30.0, 3.0));
    let area = Band {
        area: Some((10.0, 20.0)),
        ..Band::default()
    };
    assert!(area.holds(3.0, 5.0) && !area.holds(1.0, 1.0));
    assert!(!b.presence_only() && Band::default().presence_only());
}

#[test]
fn a_malformed_declaration_is_refused_in_the_python_s_words() {
    assert_eq!(
        refused(&json!([])),
        "ValueError: types.json is a non-empty list of type objects"
    );
    assert_eq!(
        refused(&json!({})),
        "ValueError: types.json is a non-empty list of type objects"
    );
    let carries = "ValueError: a type object carries ['checks', 'hand_drawn', 'program', 'required', 'tier', 'title'] (and generated_exceptions, notes, map_keys), not";
    assert_eq!(refused(&json!([3])), format!("{carries} 3"));
    assert_eq!(
        refused(&with(|t| {
            t.remove("title");
        })),
        format!("{carries} ['checks', 'hand_drawn', 'program', 'required', 'tier']")
    );
    assert!(refused(&with(|t| {
        t.insert("odd".into(), json!(1));
    }))
    .ends_with("'odd', 'program', 'required', 'tier', 'title']"));
    assert_eq!(
        refused(&with(|t| {
            t.insert("tier".into(), json!("Bad"));
        })),
        "ValueError: tier 'Bad' is not lower-case kebab"
    );
    assert_eq!(
        refused(&with(|t| {
            t.insert("tier".into(), json!(""));
        })),
        "ValueError: tier '' is not lower-case kebab"
    );
    assert_eq!(
        refused(&with(|t| {
            t.insert("tier".into(), json!("a_b"));
        })),
        "ValueError: tier 'a_b' is not lower-case kebab"
    );
    // Python's `$` matches before a final newline
    assert_eq!(
        parse_types(&with(|t| {
            t.insert("tier".into(), json!("a-1\n"));
        }))
        .unwrap()[0]
            .tier,
        "a-1\n"
    );
    assert_eq!(
        refused(&with(|t| {
            t.insert("required".into(), json!(5));
        })),
        "TypeError: 'int' object is not iterable"
    );
    assert_eq!(
        refused(&with(|t| {
            t.insert("checks".into(), json!(null));
        })),
        "TypeError: 'NoneType' object is not iterable"
    );
    assert_eq!(
        refused(&with(|t| {
            t["required"] = json!([a_type()["required"][0], a_type()["required"][0]]);
        })),
        "ValueError: t: required item ids repeat"
    );
    assert_eq!(
        refused(&json!([a_type(), a_type()])),
        "ValueError: a tier is declared twice"
    );
}

#[test]
fn a_malformed_item_is_refused_in_the_python_s_words() {
    let carries = "ValueError: t: a required item carries id, label, band_ft, class, why - or id, kind, band_ft, whose class and why are its kind's (feature 262) - (and optional, forms, site), not";
    assert_eq!(
        refused(&with(|t| {
            t["required"] = json!(["x"]);
        })),
        format!("{carries} 'x'")
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("kind".into(), json!("k"));
        })),
        format!("{carries} ['band_ft', 'class', 'id', 'kind', 'label', 'why']")
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("odd".into(), json!(1));
        })),
        format!("{carries} ['band_ft', 'class', 'id', 'label', 'odd', 'why']")
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("site".into(), json!(""));
        })),
        "ValueError: t/a: site names a correspondence class (a non-empty string), not ''"
    );
    assert_eq!(
        refused(&with(|t| {
            t["required"] = json!([{"id": 7, "kind": 3, "band_ft": {}}]);
        })),
        "ValueError: t/7: kind names a Mode A kind (a non-empty string), not 3"
    );
    assert_eq!(refused(&with_item(|i| { i.insert("class".into(), json!("odd")); })), "ValueError: t/a: class must be one of ('accurate', 'deviation', 'convention', 'guess'), not 'odd'");
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("forms".into(), json!([1]));
        })),
        "AttributeError: 'list' object has no attribute 'items'"
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("forms".into(), json!({"f": {"q": 1}}));
        })),
        "ValueError: t/a/forms/f: band_ft carries only w, h and area, not {'q': 1}"
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("band_ft".into(), json!([1]));
        })),
        "ValueError: t/a: band_ft carries only w, h and area, not [1]"
    );
    let range = "ValueError: t/a: a band range is [min, max] with min <= max, not";
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("band_ft".into(), json!({"w": [2, 1]}));
        })),
        format!("{range} [2, 1]")
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("band_ft".into(), json!({"h": [1, "2"]}));
        })),
        format!("{range} [1, '2']")
    );
    assert_eq!(
        refused(&with_item(|i| {
            i.insert("band_ft".into(), json!({"area": 5}));
        })),
        format!("{range} 5")
    );
    // a bool is an int to Python's isinstance
    assert_eq!(
        parse_types(&with_item(|i| {
            i.insert("band_ft".into(), json!({"w": [false, true]}));
        }))
        .unwrap()[0]
            .required[0]
            .band
            .w,
        Some((0.0, 1.0))
    );
    let e = parse_types(&with_item(|i| {
        i.insert("label".into(), json!("("));
    }))
    .unwrap_err();
    assert_eq!(e.kind, "re.PatternError");
}

#[test]
fn the_declaration_is_read_from_the_tree() {
    let dir = l7r_gate_core::checks::scratch("mode-a-types");
    let root = dir.path();
    let e = load_types(root).unwrap_err();
    assert_eq!(e.kind, "FileNotFoundError");
    std::fs::create_dir_all(root.join("l7r/diagram/buildings")).unwrap();
    std::fs::write(root.join(DECLARATION), "[").unwrap();
    assert_eq!(
        load_types(root).unwrap_err().kind,
        "json.decoder.JSONDecodeError"
    );
    let mut b = a_type();
    b["tier"] = json!("b");
    b["hand_drawn"] = json!(false);
    std::fs::write(root.join(DECLARATION), json!([a_type(), b]).to_string()).unwrap();
    assert_eq!(
        tiers(root).unwrap().into_iter().collect::<Vec<_>>(),
        ["b", "t"]
    );
    assert_eq!(
        hand_drawn_tiers(root)
            .unwrap()
            .into_iter()
            .collect::<Vec<_>>(),
        ["t"]
    );
    assert_eq!(by_tier("b", root).unwrap().unwrap().tier, "b");
    assert_eq!(by_tier("z", root).unwrap(), None);
    assert!(
        tiers(&root.join("none")).is_err()
            && hand_drawn_tiers(&root.join("none")).is_err()
            && by_tier("b", &root.join("none")).is_err()
    );
}

/// A scratch tree holding every kind's modal file, minimal (the registry's testkit), and the page text its package reads.
pub(crate) fn kinds_tree(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = l7r_gate_core::checks::scratch(tag);
    l7r_gate_registry::testkit::modals(dir.path(), "research/questions/x.html");
    let assets = dir.path().join("l7r/diagram/interactive/assets");
    std::fs::write(assets.join("page-text.json"), "{}").unwrap();
    let well = dir.path().join(l7r_gate_registry::about::modal_rel(
        &l7r_gate_registry::kinds::SHEET_REGISTRY,
        "well",
    ));
    let text = std::fs::read_to_string(&well).unwrap();
    std::fs::write(&well, format!("{text}Guesses:\n- its depth\n- its curb\n")).unwrap();
    dir
}

#[test]
fn a_kind_item_is_classified_by_its_kind_s_guesses() {
    let dir = kinds_tree("mode-a-kinds");
    let mut kinds = Kinds::new(dir.path());
    let item = |kind: &str| RequiredItem {
        id: "i".into(),
        label: None,
        band: Band::default(),
        cls: String::new(),
        why: String::new(),
        optional: false,
        forms: Vec::new(),
        site: None,
        kind: Some(kind.into()),
    };
    assert_eq!(
        classification(&item("well"), &mut kinds).unwrap(),
        (PER_STATEMENT.to_owned(), "its depth its curb".to_owned())
    );
    assert_eq!(
        classification(&item("main gate"), &mut kinds).unwrap().1,
        NOTHING_GUESSED
    );
    assert_eq!(
        classification(&item("t168-none"), &mut kinds)
            .unwrap_err()
            .message,
        "program item 'i' names the kind 't168-none', which the Mode A registry does not know"
    );
    let own = RequiredItem {
        kind: None,
        cls: "guess".into(),
        why: "w".into(),
        ..item("x")
    };
    assert_eq!(
        classification(&own, &mut kinds).unwrap(),
        ("guess".to_owned(), "w".to_owned())
    );
    // a registry that does not load refuses every kind item, and is asked again by the next
    let mut broken = Kinds::new(Path::new("/nonexistent/t168"));
    assert!(classification(&item("well"), &mut broken).is_err());
    assert!(classification(&item("well"), &mut broken).is_err());
}

/// The armory's band is held to its two forms (449 T290; size-audit 2026-11-22 S3, S4): a hall end bay up to 18 x 41 ft and 740 sq ft by
/// default, a gate-range room up to 13 x 25 ft and 320 sq ft under the sheet's `**Form**: armory in the gate range`, so the old band's
/// 24 x 40 ft (about 6.7x Kaibara's eight-mat room) is refused under both, and every drawn armory still holds.
#[test]
fn the_armory_band_holds_its_two_forms() {
    let mag = by_tier("magistracies", &real()).unwrap().unwrap();
    let armory = mag.required.iter().find(|i| i.id == "armory").unwrap();
    let hall = armory.band_for(None).unwrap();
    let range = armory.band_for(Some("armory in the gate range")).unwrap();
    let wide = (hall.holds(24.0, 40.0), range.holds(24.0, 40.0));
    assert_eq!(wide, (false, false));
    let drawn = (
        hall.holds(14.0, 20.0),
        hall.holds(14.0, 16.7),
        range.holds(13.3, 12.0),
    );
    assert_eq!(drawn, (true, true, true));
    let hall_room_in_a_range = range.holds(14.0, 20.0);
    assert!(!hall_room_in_a_range);
}

/// A store of its own reads its own band (449 T303), about Nirayama's weapons store of 5.4 x 3.7 m (~17.7 x 12.1 ft, ~215 sq ft; 0123):
/// 11-18 x 11-24 ft and 120-430 sq ft under `**Form**: armory as a store of its own`, so Nirayama's holds and a hall bay run the hall's
/// whole depth (14 x 41 ft, which the default band takes) does not.
#[test]
fn a_store_of_its_own_reads_a_band_about_nirayamas() {
    let mag = by_tier("magistracies", &real()).unwrap().unwrap();
    let armory = mag.required.iter().find(|i| i.id == "armory").unwrap();
    let store = armory
        .band_for(Some("armory as a store of its own"))
        .unwrap();
    assert!(store.holds(17.7, 12.1), "Nirayama's store");
    assert!(!store.holds(14.0, 41.0), "a hall bay at full depth");
    assert!(armory.band_for(None).unwrap().holds(14.0, 41.0));
    assert!(!store.holds(18.0, 24.0), "past twice Nirayama's floor");
}
