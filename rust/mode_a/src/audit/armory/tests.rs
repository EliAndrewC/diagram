//! The armory site's tests (feature 449 T303): small yards drawing each site, and the pool's five magistracies.
//!
//! Research:
//!     the armory site's test yards - NONE: test sheets, deciding nothing about a building

use std::path::{Path, PathBuf};

use super::{
    armory_site, drawn_site, gate_range_drawn, rolled, sites, stem, GATE_RANGE, GATE_RANGE_FORM,
    HALL, STORE, STORE_FORM,
};
use crate::parse::parse_svg;

fn tree() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// A two-court yard: the divider at y 150, the main gate's posts on the south wall about (200, 280), the office hall in the outer court;
/// `gate` the gatehouse (the passage runs through it for a range), `armory` the armory's rect.
fn yard(gate: &str, armory: &str) -> String {
    format!(
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="inner court"/>
<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="150" x2="380" y2="150"/></g>
<rect x="100" y="160" width="200" height="50" fill="#DDB87A" data-kind="office hall"/>
{gate}
<g data-kind="main gate"><rect x="180" y="274" width="6" height="12"/><rect x="214" y="274" width="6" height="12"/></g>
{armory}
</svg>"##
    )
}

const RANGE: &str =
    r##"<rect x="150" y="268" width="100" height="24" fill="#8C6F3E" data-kind="gatehouse"/>"##;
const ONE_BAY: &str =
    r##"<rect x="260" y="250" width="60" height="24" fill="#8C6F3E" data-kind="gatehouse"/>"##;
/// Ubame's form: the range's two rooms either side of an open passage, the armory the west one, its east end at the west post.
const SPLIT_RANGE: &str =
    r##"<rect x="220" y="268" width="80" height="24" fill="#8C6F3E" data-kind="gatehouse"/>"##;
const SPLIT_ARMORY: &str =
    r##"<rect x="150" y="268" width="36" height="24" fill="#8C6F3E" data-kind="armory"/>"##;
const IN_HALL: &str =
    r##"<rect x="100" y="180" width="42" height="30" fill="#DDB87A" data-kind="armory"/>"##;
const IN_RANGE: &str =
    r##"<rect x="152" y="270" width="26" height="20" fill="#8C6F3E" data-kind="armory"/>"##;
const STORE_OUTER: &str =
    r##"<rect x="40" y="220" width="54" height="36" fill="#DDB87A" data-kind="armory"/>"##;
const STORE_INNER: &str =
    r##"<rect x="40" y="60" width="54" height="36" fill="#DDB87A" data-kind="armory"/>"##;

/// The sites a sheet offers, in the roll's order (the round arbiter's ask:armory-store-ubame, route (a)): the gate range only where the
/// main gate is drawn as one; on that order every pool sheet keeps the site 449 T276 rolled it under the two-way roll - Ubame the gate
/// range, Hayakawa the hall, the three one-bay sheets the hall (measured 2026-11-22 against Python's `random`).
#[test]
fn the_sites_and_the_pool_sheets_rolls() {
    assert_eq!(sites(true), [GATE_RANGE, HALL, STORE]);
    assert_eq!(sites(false), [HALL, STORE]);
    let rolls = [
        ("ubame-magistracy", true, GATE_RANGE),
        ("hayakawa-magistracy", true, HALL),
        ("ochiba-magistracy", false, HALL),
        ("ochiba-roundtrip-test", false, HALL),
        ("county-magistracy-example", false, HALL),
    ];
    for (sheet, range, want) in rolls {
        assert_eq!(rolled(sheet, range), want, "{sheet}");
    }
    // the store is rolled: a one-bay gate's `b` and a gate range's `a` (Python's `random`, 2026-11-22)
    assert_eq!(rolled("b", false), STORE);
    assert_eq!(rolled("a", true), STORE);
    assert_eq!(stem("pool/x/ubame-magistracy.svg"), "ubame-magistracy");
}

/// Every pool magistracy draws its armory where its seed rolls it, its gate read as its notes record it, and passes the check.
#[test]
fn every_pool_magistracy_draws_its_armory_where_its_seed_rolls_it() {
    let tree = tree();
    let sheets = [
        ("ubame-magistracy", true, GATE_RANGE),
        ("hayakawa-magistracy", true, HALL),
        ("ochiba-magistracy", false, HALL),
        ("ochiba-roundtrip-test", false, HALL),
        ("county-magistracy-example", false, HALL),
    ];
    for (sheet, range, site) in sheets {
        let svg = tree.join(format!("pool/magistracies/{sheet}/{sheet}.svg"));
        let text = std::fs::read_to_string(&svg).unwrap();
        let plan = parse_svg(&text).unwrap();
        let form = crate::audit::report::read_form(&svg.to_string_lossy()).unwrap();
        assert_eq!(gate_range_drawn(&plan), range, "{sheet}");
        assert_eq!(drawn_site(&plan).map(|(s, _)| s), Some(site), "{sheet}");
        let found = armory_site(&plan, sheet, form.as_deref());
        assert!(found.is_empty(), "{sheet}: {found:?}");
    }
}

/// The three sites read off a sheet, and the check passing each where the seed rolls it.
#[test]
fn each_site_passes_where_its_seed_rolls_it() {
    let plan = |g, a| parse_svg(&yard(g, a)).unwrap();
    let range_room = plan(RANGE, IN_RANGE);
    assert!(gate_range_drawn(&range_room));
    assert!(!gate_range_drawn(&plan(ONE_BAY, IN_HALL)));
    assert_eq!(drawn_site(&range_room).map(|(s, _)| s), Some(GATE_RANGE));
    let split = plan(SPLIT_RANGE, SPLIT_ARMORY);
    assert!(gate_range_drawn(&split));
    assert_eq!(drawn_site(&split).map(|(s, _)| s), Some(GATE_RANGE));
    assert!(armory_site(&split, "e", Some(GATE_RANGE_FORM)).is_empty());
    // the split range without its armory has one room, so no range; a gatehouse beside a one-bay gate is no gate range, so an armory
    // in it reads as a store of its own and the gate range's form is refused (impl-drift 2026-11-22)
    assert!(!gate_range_drawn(&plan(SPLIT_RANGE, IN_HALL)));
    let in_gatehouse =
        r##"<rect x="262" y="252" width="20" height="20" fill="#8C6F3E" data-kind="armory"/>"##;
    let beside = plan(ONE_BAY, in_gatehouse);
    assert_eq!(drawn_site(&beside).map(|(s, _)| s), Some(STORE));
    let off = armory_site(&beside, "b", Some(GATE_RANGE_FORM));
    assert_eq!(off.len(), 1, "{off:?}");
    assert!(off[0].contains("notes declare Some"), "{off:?}");
    // a sheet with no main gate drawn has no gate range
    let ungated = yard(RANGE, IN_RANGE).replace(r#"data-kind="main gate""#, r#"data-kind="-""#);
    assert!(!gate_range_drawn(&parse_svg(&ungated).unwrap()));
    // `e` rolls the gate range among three; `c` the hall among three; `b` a store among two
    assert!(armory_site(&range_room, "e", Some(GATE_RANGE_FORM)).is_empty());
    assert!(armory_site(&plan(RANGE, IN_HALL), "c", None).is_empty());
    assert!(armory_site(&plan(ONE_BAY, STORE_OUTER), "b", Some(STORE_FORM)).is_empty());
    assert!(armory_site(&plan(ONE_BAY, ""), "b", None).is_empty());
}

/// The check refuses an armory off its roll and a form that does not name its site; a store of its own stands where the sheet draws it.
#[test]
fn an_armory_off_its_roll_or_its_form_is_refused() {
    let plan = |g, a| parse_svg(&yard(g, a)).unwrap();
    let off = armory_site(&plan(ONE_BAY, IN_HALL), "b", None);
    assert_eq!(off.len(), 1, "{off:?}");
    assert!(off[0].contains("rolls \"a store of its own\""), "{off:?}");
    let unformed = armory_site(&plan(RANGE, IN_RANGE), "e", None);
    assert_eq!(unformed.len(), 1, "{unformed:?}");
    assert!(unformed[0].contains("notes declare None"), "{unformed:?}");
    // a store of its own stands where the sheet draws it: in the inner court too, or on a sheet with no divider or no main gate
    assert!(armory_site(&plan(ONE_BAY, STORE_INNER), "b", Some(STORE_FORM)).is_empty());
}

/// A gate in a north-south wall: the range's two rooms stand north and south of its passage, across the passage's line.
#[test]
fn a_range_in_a_north_south_wall_flanks_its_passage() {
    let svg = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="inner court"/>
<rect x="368" y="90" width="24" height="32" fill="#8C6F3E" data-kind="armory"/>
<rect x="368" y="154" width="24" height="40" fill="#8C6F3E" data-kind="gatehouse"/>
<g data-kind="main gate"><rect x="374" y="120" width="12" height="6"/><rect x="374" y="150" width="12" height="6"/></g>
</svg>"##;
    let plan = parse_svg(svg).unwrap();
    assert!(gate_range_drawn(&plan));
    assert_eq!(drawn_site(&plan).map(|(s, _)| s), Some(GATE_RANGE));
    let lone = svg.replace(r#"data-kind="armory""#, r#"data-kind="-""#);
    assert!(!gate_range_drawn(&parse_svg(&lone).unwrap()));
}
