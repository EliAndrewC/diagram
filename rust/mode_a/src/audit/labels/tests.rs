//! The program's labels on a declaration of LABELED items (feature 254 D7), which no declared tier carries since feature 262: an item
//! found by its pattern over a caption's words, by its kind, or by an element declared with its id; its band held on the footprint its
//! captions are tagged with (the checks' lockstep read the same declaration until feature 449 T212 deleted it with the Python).
//!
//! Research:
//!     the program labels' tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::Path;

use super::{check_bands, check_program, kinds_of, matches};
use crate::parse::parse_svg;
use crate::types::{parse_types, Kinds};

/// Two tiers: one of labeled items (and one kind item), one whose only item is of a kind no registry knows.
const TYPES: &str = r#"[
 {"tier": "labeled", "title": "L", "program": "P", "hand_drawn": true, "checks": [], "required": [
  {"id": "kitchen", "label": "kitch\\w+", "band_ft": {"w": [5, 10], "h": [5, 10]}, "class": "guess", "why": "a test's"},
  {"id": "hall", "label": "great\\s+hall", "band_ft": {"area": [10, 20]}, "class": "accurate", "why": "a test's",
   "forms": {"small": null}},
  {"id": "pond", "label": "pond", "band_ft": {}, "class": "convention", "why": "a test's", "site": "water"},
  {"id": "well", "label": "well", "band_ft": {}, "class": "convention", "why": "a test's", "site": "water_point"},
  {"id": "gate", "label": "gate", "band_ft": {}, "class": "guess", "why": "a test's", "optional": true},
  {"id": "precinct", "label": "nothing drawn says this", "band_ft": {}, "class": "guess", "why": "a test's"},
  {"id": "porch", "label": "porch", "band_ft": {"w": [1, 2]}, "class": "guess", "why": "a test's"},
  {"id": "shed", "label": "shed", "band_ft": {"w": [1, 2], "h": [1, 2]}, "class": "guess", "why": "a test's"},
  {"id": "byre", "label": "byre", "band_ft": {}, "class": "guess", "why": "a test's"},
  {"id": "hearth", "kind": "hearth", "band_ft": {}}]},
 {"tier": "unknown", "title": "U", "program": "P", "hand_drawn": true, "checks": [], "required": [
  {"id": "store", "kind": "no such kind", "band_ft": {"w": [1, 2], "h": [1, 2]}}]}]"#;

/// The kitchen 20 x 15 ft and the hall 30 x 20 ft, each captioned inside its tagged group; a porch inside its band's one side; a shed
/// captioned on open ground, a byre on ground tagged `ground`; a pond's caption; a store of the unknown kind.
const SHEET: &str = r##"<svg><rect id="precinct" x="0" y="0" width="300" height="200" fill="url(#court-earth)"/><g data-kind="kitchen"><rect x="10" y="10" width="60" height="45" fill="#C9A57A"/><text x="20" y="30">Kitchen  yard</text></g><g data-kind="hall"><rect x="100" y="10" width="90" height="60" fill="#DDB87A"/><text x="110" y="30">GREAT   Hall</text></g><g data-kind="porch"><rect x="100" y="100" width="9" height="9" fill="#DDB87A"/><text x="100" y="100">porch</text></g><text x="200" y="150">shed</text><g data-kind="ground"><text x="10" y="180">byre</text></g><rect id="gate" x="1" y="1" width="2" height="2" fill="#000"/><g data-kind="no such kind"><rect x="200" y="100" width="30" height="30" fill="#C9A57A"/></g><text x="10" y="150">Pond</text></svg>"##;

fn tree() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn a_labeled_item_is_found_by_its_caption_its_id_or_its_kind() {
    let plan = parse_svg(SHEET).unwrap();
    let types = parse_types(&serde_json::from_str(TYPES).unwrap()).unwrap();
    let labeled = &types[0];
    let missing = |form, site| check_program(&plan, labeled, form, site);
    let well = "no `well` on the sheet (a label matching /well/, or an element marked id=\"well\")";
    let hearth = "no `hearth` on the sheet (an element tagged data-kind=\"hearth\", or an element marked id=\"hearth\")";
    // the precinct found by its id, the gate optional, every captioned item by its words however spaced or cased
    assert_eq!(missing(None, None), [well, hearth]);
    assert_eq!(missing(Some("small"), None), [well, hearth]);
    // a site item asked for only where the declared map shows its class
    let water = [("water".to_owned(), true)];
    assert_eq!(missing(None, Some(&[])), [hearth]);
    assert_eq!(missing(None, Some(&water)), [hearth]);
    assert_eq!(
        check_program(&plan, &types[1], None, None),
        Vec::<String>::new()
    );
    let found: Vec<(&str, Vec<String>, usize)> = labeled
        .required
        .iter()
        .map(|i| {
            let n = i
                .label
                .as_ref()
                .map_or(0, |_| matches(i, &plan.labels).len());
            (i.id.as_str(), kinds_of(i, &plan), n)
        })
        .collect();
    let want = [
        ("kitchen", vec!["kitchen".to_owned()], 1),
        ("hall", vec!["hall".to_owned()], 1),
        ("pond", Vec::new(), 1),
        ("well", Vec::new(), 0),
        ("gate", Vec::new(), 0),
        ("precinct", Vec::new(), 0),
        ("porch", vec!["porch".to_owned()], 1),
        ("shed", Vec::new(), 1),
        ("byre", vec!["ground".to_owned()], 1),
        ("hearth", vec!["hearth".to_owned()], 0),
    ];
    assert_eq!(found, want);
}

#[test]
fn a_labeled_item_s_band_is_held_on_its_tagged_footprint() {
    let tree = tree();
    let plan = parse_svg(SHEET).unwrap();
    let types = parse_types(&serde_json::from_str(TYPES).unwrap()).unwrap();
    let mut kinds = Kinds::new(&tree);
    let full = check_bands(&plan, &types[0], None, &mut kinds).unwrap();
    assert_eq!(full.len(), 2, "{full:?}");
    assert!(full[0].starts_with("`kitchen` (kitchen) is 20 x 15 ft (300 sq ft) at svg(10,10) - the band is w 5-10 by h 5-10 ft (guess: "));
    assert!(full[1].starts_with("`hall` (hall) is 30 x 20 ft (600 sq ft) at svg(100,10) - the band is area 10-20 sq ft (accurate: "));
    // the small form declares no hall
    let small = check_bands(&plan, &types[0], Some("small"), &mut kinds).unwrap();
    assert_eq!(small, full[..1]);
    // an item of a kind no registry knows is refused where its band fails
    assert!(check_bands(&plan, &types[1], None, &mut kinds).is_err());
}
