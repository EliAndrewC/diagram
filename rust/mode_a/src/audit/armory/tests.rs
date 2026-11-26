//! The armory site's tests (feature 449 T303): small yards drawing each site, and the pool's five magistracies - each read as the pool
//! sweep reads it ([`crate::sweep::sheet`]): a hand sheet as tracked, a declared generated exception composed in process from its
//! tracked `<map>.compound.json`, never read from its svg on disk, which git ignores and a tree that never drew it lacks (feature 451
//! T159: a fresh worktree's run failed `NotFound` on the two generated sheets, observed 2026-11-22 and 2026-11-26).
//!
//! Research:
//!     the armory site's test yards - NONE: test sheets, deciding nothing about a building

use std::path::{Path, PathBuf};

use super::{
    armory_site, drawn_end, drawn_site, end_bays, gate_range_drawn, rolled, rolled_end, sites,
    stem, EAST, GATE_RANGE, GATE_RANGE_FORM, HALL, STORE, STORE_FORM, WEST,
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
/// The hall's east end bay (449 T367).
const IN_HALL_EAST: &str =
    r##"<rect x="258" y="180" width="42" height="30" fill="#DDB87A" data-kind="armory"/>"##;
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
        ("ubame-magistracy", true, GATE_RANGE, false),
        ("hayakawa-magistracy", true, HALL, false),
        ("ochiba-magistracy", false, HALL, false),
        ("ochiba-roundtrip-test", false, HALL, true),
        ("county-magistracy-example", false, HALL, true),
    ];
    let ends = [
        ("ubame-magistracy", None),
        ("hayakawa-magistracy", Some(EAST)),
        ("ochiba-magistracy", Some(WEST)),
        ("ochiba-roundtrip-test", Some(EAST)),
        ("county-magistracy-example", Some(WEST)),
    ];
    let walked = l7r_gate_pool::walk(&tree);
    for ((sheet, range, site, generated), (_, end)) in sheets.into_iter().zip(ends) {
        // as the sweep reads it: a hand sheet's tracked svg, a generated exception composed from its spec (451 T159)
        let read = crate::sweep::sheet(&tree, walked.folder(sheet).unwrap()).unwrap();
        // the two generated sheets are composed here, so no sheet a tree happened to draw stands in for the generator's
        assert_eq!(read.generated, generated, "{sheet}");
        let plan = parse_svg(&read.text).unwrap();
        let form = crate::audit::report::read_form(&read.svg.to_string_lossy()).unwrap();
        assert_eq!(gate_range_drawn(&plan), range, "{sheet}");
        assert_eq!(drawn_site(&plan).map(|(s, _)| s), Some(site), "{sheet}");
        assert_eq!(drawn_end(&plan), end, "{sheet}");
        let found = armory_site(&plan, sheet, form.as_deref());
        assert!(found.is_empty(), "{sheet}: {found:?}");
    }
}

/// The pool test goes red on a generated sheet whose armory is placed off its roll: the county example's spec with the armory moved
/// to the hall's east end, composed as the pool's is, reads east where its seed rolls west, and the check refuses it (451 T159).
#[test]
fn a_generated_sheet_with_its_armory_off_its_roll_is_refused() {
    let tree = tree();
    let name = "county-magistracy-example";
    let spec = format!("pool/magistracies/{name}/{name}.compound.json");
    let real = std::fs::read_to_string(tree.join(&spec)).unwrap();
    // the armory room as the spec places it, in the hall's west end bay, and the same room moved into the hall's east half, where it
    // overlaps the official study: the generator composes overlapping rooms today, and a refusal of them would fail this at `compose`
    let room = r#"{"kind": "armory", "caption": "armory", "x": 0, "y": 0, "w": 14, "h": 20}"#;
    let moved = real.replace(room, &room.replace(r#""x": 0,"#, r#""x": 92.5,"#));
    assert_ne!(moved, real);
    let scratch = l7r_shared::tempdir::TempDir::new("mode-a-armory-off-roll");
    let at = scratch.path().join(format!("{name}.compound.json"));
    std::fs::write(&at, moved).unwrap();
    let text = crate::sweep::compose(&tree, &at).unwrap();
    let plan = parse_svg(&text).unwrap();
    assert_eq!(drawn_site(&plan).map(|(s, _)| s), Some(HALL));
    assert_eq!(drawn_end(&plan), Some(EAST));
    let found = armory_site(&plan, name, None);
    assert_eq!(found.len(), 1, "{found:?}");
    assert!(found[0].contains("rolls \"west\""), "{found:?}");
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
    // `e` rolls the gate range among three; `h` the hall among three, its west end bay; `b` a store among two
    assert!(armory_site(&range_room, "e", Some(GATE_RANGE_FORM)).is_empty());
    assert!(armory_site(&plan(RANGE, IN_HALL), "h", None).is_empty());
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

/// The hall's end bay is a second roll (449 T367; 0123: the armory's side varied across county offices - Pingyao's west end bay,
/// Jiexiu's both, Neixiang's on the left, Wuyang's to the right of its hall, Zhenping's east and west stores), keyed
/// `<sheet>:armory end bay` among west and east in that order, read only where the site is the hall: the pool's four hall-bay sheets
/// roll county and Ochiba west, Hayakawa and the round trip east (measured 2026-11-23 against Python's `random`).
#[test]
fn the_end_bay_is_rolled_from_the_seed() {
    assert_eq!(end_bays(), [WEST, EAST]);
    for (sheet, want) in [
        ("county-magistracy-example", WEST),
        ("ochiba-magistracy", WEST),
        ("hayakawa-magistracy", EAST),
        ("ochiba-roundtrip-test", EAST),
        ("e", WEST),
        ("a", EAST),
    ] {
        assert_eq!(rolled_end(sheet), want, "{sheet}");
    }
}

/// An armory in the hall's other end bay is refused, the refusal naming the roll and the fix; one in its rolled end bay passes, and
/// an armory elsewhere has no end bay.
#[test]
fn an_armory_in_the_other_end_bay_is_refused() {
    let plan = |g, a| parse_svg(&yard(g, a)).unwrap();
    // `a` rolls the hall among two and its east end bay; `e` the hall among two and its west end bay
    assert_eq!(drawn_end(&plan(ONE_BAY, IN_HALL)), Some(WEST));
    assert_eq!(drawn_end(&plan(ONE_BAY, IN_HALL_EAST)), Some(EAST));
    assert_eq!(drawn_end(&plan(ONE_BAY, STORE_OUTER)), None);
    assert_eq!(drawn_end(&plan(ONE_BAY, "")), None);
    assert!(armory_site(&plan(ONE_BAY, IN_HALL_EAST), "a", None).is_empty());
    assert!(armory_site(&plan(ONE_BAY, IN_HALL), "e", None).is_empty());
    let west = armory_site(&plan(ONE_BAY, IN_HALL), "a", None);
    assert_eq!(west.len(), 1, "{west:?}");
    assert!(west[0].contains("west end bay"), "{west:?}");
    assert!(west[0].contains("rolls \"east\""), "{west:?}");
    assert!(west[0].contains("`a:armory end bay`"), "{west:?}");
    assert!(west[0].contains("from its east end"), "{west:?}");
    let east = armory_site(&plan(ONE_BAY, IN_HALL_EAST), "e", None);
    assert_eq!(east.len(), 1, "{east:?}");
    assert!(east[0].contains("rolls \"west\""), "{east:?}");
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
