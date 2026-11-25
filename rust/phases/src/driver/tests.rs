//! The driver's rolls end to end: a comb and the polders through their stages, the record, the ink census (feature 444 T42, 449 T230).
//!
//! Research:
//!     the driver's tests - NONE: fixtures and assertions; each rule's claim is at the unit it tests

use super::{manifest, roll, spec::parse};
use crate::field::geom::dist;

#[test]
fn a_comb_hamlet_rolls_and_draws_its_field() {
    let r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    assert_eq!(
        r.stages,
        vec!["water_frame", "field", "sink", "seat", "hem"]
    );
    assert!(!r.dry.is_empty() && r.grain.is_some_and(|g| g.0 > 0.0));
    assert_eq!(
        ["barley", "millet", "buckwheat", "soy"]
            .map(|c| super::crop_ink(c).0)
            .iter()
            .collect::<std::collections::HashSet<_>>()
            .len(),
        4
    );
    assert!(r.sunk.as_ref().is_some_and(|s| s.pond.is_some()));
    assert!(!r.fields.is_empty() && !r.fields[0].basins.is_empty());
    assert!(r.svg.starts_with("<svg") && r.svg.matches("<path").count() > r.fields[0].basins.len());
    let m = manifest(&r);
    assert!(m.contains("\"grain_acres\": {\"field\": {\"drawn\": "));
    assert!(
        m.contains("\"name\": \"Inashiro\"")
            && m.contains("\"stages\": [\"water_frame\", \"field\", \"sink\", \"seat\", \"hem\"]")
            && m.contains("\"plot_size\"")
    );
}

#[test]
fn a_resting_field_drains_off_the_map() {
    let r = roll(&parse(r#"{"name": "Sawada", "seed": 24, "households": 19, "down_deg": 225, "water_sink": "offmap", "intake": "open", "pins": {"paddy_rest": "unsettled"}}"#).unwrap()).unwrap();
    assert!(r.fields[0]
        .states
        .contains(&crate::field::states::State::Rest));
    assert!(r
        .sunk
        .as_ref()
        .is_some_and(|s| s.pond.is_none() && !s.run.is_empty()));
    // its fall runs into the wind: the seat backs the hill, recorded off the wind
    assert!(r.refusals.is_empty() && r.seated.as_ref().is_some_and(|s| s.frames[0].offwind));
    // its paddy lies to windward, so its belt's ground lies between the houses and the paddy, not uphill behind them (0072: the
    // wind decides the side; 449 T277): the band stands the belt's depth off the margin, the kept ground no deeper than before
    let f = &r.seated.as_ref().unwrap().frames[0];
    let off = (f.center.0 - f.anchor.0) * f.out.0 + (f.center.1 - f.anchor.1) * f.out.1;
    let owed = crate::seat::margins::STANDOFF + crate::seat::margins::BELT_BAND.1 + f.band.1;
    assert!((off - owed).abs() < 1e-6, "{f:?}");
    let ground = super::settlement_ground(f, super::wind(&r.plan.windward));
    let deep = ground
        .iter()
        .map(|p| (p.0 - f.anchor.0) * f.out.0 + (p.1 - f.anchor.1) * f.out.1)
        .fold(0.0, f64::max);
    assert!((deep - (off + f.band.1)).abs() < 1e-6, "{deep} {off}");
    let mut kept_why = Vec::new();
    assert!(super::kept::<u8>(
        Err(super::Refused("the seat refused: x".into())),
        &mut kept_why
    )
    .is_none());
    let mut refused = r;
    refused.refusals = kept_why;
    assert!(manifest(&refused).contains("\"refusals\": [\"the seat refused: x\"]"));
}

#[test]
fn a_dike_pond_polder_rolls_through_its_seat_and_its_waterside_reeds() {
    let r = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    assert!(
        r.stages.contains(&"waterward") && r.polder.as_ref().is_some_and(|s| s.converted.is_some())
    );
    assert!(r.svg.contains(DIKE_EARTH_FOR_TEST));
    // the fringe reads the dike's outer face and the two sluices' channels, a point each (449 T236: the two faces' copy gone)
    #[cfg(feature = "counters")]
    {
        let s = r.polder.as_ref().unwrap();
        let ward = r.by_stage.iter().find(|s| s.0 == "waterward").unwrap();
        assert_eq!(
            ward.1.get("read@dike"),
            Some(&((s.dike.outer.len() + s.polder.feeder.len() + s.outfall.len()) as u64))
        );
        assert_eq!(ward.1.get("read@stage_waterward"), None);
    }
    assert!(manifest(&r).contains("\"grain_acres\": {\"field\": null, \"hem\": null}"));
    let rice = roll(&parse(r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 0, "field_archetype": "polder_grid", "pins": {"paddy_rest": "unsettled"}}"#).unwrap()).unwrap();
    assert!(rice.polder.as_ref().is_some_and(|s| s.converted.is_none()));
    let tea = roll(&parse(r#"{"name": "T", "seed": 21, "households": 16, "down_deg": 0, "field_archetype": "mulberry_dike_fishpond", "dike_crop": "tea"}"#).unwrap()).unwrap();
    assert!(tea
        .polder
        .as_ref()
        .is_some_and(|s| s.converted.as_ref().is_some_and(|c| !c.1.hedges.is_empty())));
    assert_eq!(
        ["willow", "fruit", "tea", "mulberry"]
            .map(super::polder::crown_fill)
            .iter()
            .collect::<std::collections::HashSet<_>>()
            .len(),
        4
    );
}

const DIKE_EARTH_FOR_TEST: &str = super::polder::DIKE_EARTH;

#[test]
fn every_state_has_its_fill_and_a_field_refusal_names_its_rule() {
    use crate::field::states::State;
    let fills: Vec<&str> = [
        State::Green,
        State::Wet,
        State::Flooded,
        State::Gold,
        State::Rest,
    ]
    .into_iter()
    .map(super::fill)
    .collect();
    assert_eq!(
        fills.iter().collect::<std::collections::HashSet<_>>().len(),
        5
    );
    assert!(super::seat_refused(crate::seat::SeatRefused("x".into()))
        .0
        .starts_with("the seat refused"));
    assert_eq!(
        ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "?"]
            .map(super::wind)
            .iter()
            .filter(|w| (w.0.hypot(w.1) - 1.0).abs() < 1e-9)
            .count(),
        9
    );
    assert!(super::sink_refused(crate::sink::SinkRefused("x".into()))
        .0
        .starts_with("the sink refused"));
    let e = super::field_refused(crate::field::rules::FieldRefused {
        rule: "a_rule",
        detail: "why".into(),
    });
    assert!(e.0.starts_with("the field refused: "));
}

#[test]
fn a_cohort_seed_rolls_with_its_households_by_the_seed() {
    let s = super::cohort_spec(4, None);
    assert_eq!((s.name.as_str(), s.households), ("Audit-04", 16));
    assert!(roll(&s).is_ok());
    let p = roll(&super::cohort_spec(4, Some("polder_grid"))).unwrap();
    assert!(p.polder.is_some());
}

#[test]
fn each_stage_run_reports_its_counted_work_and_not_its_placements() {
    let c: std::collections::HashMap<String, u64> = [
        ("placed", 5),
        ("moved@settle_runs", 2),
        ("dropped", 1),
        ("write@frames", 3),
        ("read", 4),
    ]
    .into_iter()
    .map(|(k, n)| (k.to_owned(), n))
    .collect();
    assert_eq!(super::ops(&c), 7);
    for r in [
        roll(&super::cohort_spec(4, None)).unwrap(),
        roll(&super::cohort_spec(4, Some("polder_grid"))).unwrap(),
    ] {
        assert_eq!(r.by_stage.iter().map(|s| s.0).collect::<Vec<_>>(), r.stages);
    }
}

#[test]
fn a_name_is_escaped_in_the_record() {
    // the record's counts, written as the counting build fills them (a default build's map is empty)
    let mut r = roll(&super::cohort_spec(4, None)).unwrap();
    r.counts.insert("write@x".to_owned(), 3);
    assert!(super::manifest(&r).contains("\"write@x\": 3"));
    assert_eq!(super::Refused("why".into()).to_string(), "why");
    assert_eq!(super::record::js("a\"b\\c\nd"), "\"a\\\"b\\\\c\\nd\"");
}

/// THE INK CENSUS (449 T230): every mark a roll draws is named by a kind of the registry - none unnamed - and the record holds
/// the census as the deleted Python's manifest did, `ink_classes`, which the review owed lookup reads as the hamlet's legend.
#[test]
fn every_mark_drawn_is_a_registry_kind_in_the_census() {
    // the registry's kinds the driver's stages draw (`rust/gate/crates/registry/src/kinds.rs`), and `-` for the placeholder
    const KINDS: [&str; 24] = [
        "-",
        "paddy",
        "wet paddy",
        "bund beans",
        "barley",
        "millet",
        "buckwheat",
        "soy",
        "stream",
        "irrigation ditch",
        "drainage ditch",
        "pond canal",
        "weir",
        "pond",
        "field pond",
        "field grave",
        "marsh",
        "fish pond",
        "fry pond",
        "mulberry dike",
        "fruit dike",
        "tea dike",
        "perimeter dike",
        "sluice gate",
    ];
    let specs = [
        r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#,
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        r#"{"name": "T", "seed": 21, "households": 16, "down_deg": 0, "field_archetype": "mulberry_dike_fishpond", "dike_crop": "tea"}"#,
        r#"{"name": "F", "seed": 21, "households": 16, "down_deg": 0, "field_archetype": "mulberry_dike_fishpond", "dike_crop": "fruit"}"#,
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 0, "field_archetype": "polder_grid", "pins": {"paddy_rest": "unsettled"}}"#,
    ];
    let rolls = specs
        .iter()
        .map(|s| parse(s).unwrap())
        .chain((1..=24).map(|seed| super::cohort_spec(seed, None)))
        .map(|spec| roll(&spec).unwrap());
    let mut seen = std::collections::BTreeSet::new();
    for r in rolls {
        let unnamed = r.ink.get(super::svg::UNNAMED);
        assert_eq!(unnamed, None, "{}", r.plan.name);
        assert!(super::manifest(&r).contains("\"ink_classes\": {"));
        seen.extend(r.ink.into_keys());
    }
    let unknown: Vec<&String> = seen
        .iter()
        .filter(|k| !KINDS.contains(&k.as_str()))
        .collect();
    assert!(unknown.is_empty(), "{unknown:?}");
    let never: Vec<&str> = [
        "paddy",
        "stream",
        "marsh",
        "perimeter dike",
        "mulberry dike",
        "tea dike",
        "fish pond",
        "-",
    ]
    .into_iter()
    .filter(|k| !seen.contains(*k))
    .collect();
    assert!(never.is_empty(), "{never:?}");
}

/// A BARE WINTER THE DRY GROUND CANNOT FEED IS ROLLED AGAIN AS BARLEY (449 T418): seed 31 of 16 households falling at 200
/// degrees rolled its winter crop bare, and its dry fields climbed to 43 plots, 6.45 of the 13.60 acres its grain needs, before
/// every column ended - 0011 draws a bare winter paddy only where the fan's dry ground can grow the whole need.
#[test]
fn a_bare_winter_the_dry_ground_cannot_feed_is_rolled_again_as_barley() {
    let short = r#"{"name": "S", "seed": 31, "households": 16, "down_deg": 200}"#;
    let r = roll(&parse(short).unwrap()).unwrap();
    let need = 16.0 * 0.85;
    let (drawn, _) = r.grain.unwrap();
    let (_, owed, _) = r.field_grain.unwrap();
    // the barley on the drained paddy, counted acre for acre, and the dry fields on the toe's one band
    assert_eq!(r.knobs["fan_middle"], "wild");
    assert_eq!(r.knobs["winter_crop"], "barley", "{drawn} of {need} acres");
    assert!(owed < need, "the dry need less the drained paddy: {owed}");
    let line = &r.fields[0].hem.as_ref().unwrap().line;
    let toe = dist(line[0], line[line.len() - 1]);
    assert!(toe < 0.4 * r.fields[0].fan.length, "only up the toe: {toe}");
    assert!(!r.dry.is_empty() && r.dry.len() < 43);
    assert!(super::check::check(&r).is_empty());
    // a PINNED bare winter the ground cannot feed is refused by name, on a wild middle and on a cleared one: no map of it is drawn
    for middle in ["wild", "cleared"] {
        let pinned = format!(
            r#"{{"name": "S", "seed": 31, "households": 16, "down_deg": 200, "pins": {{"winter_crop": "none", "fan_middle": "{middle}"}}}}"#
        );
        let e = roll(&parse(&pinned).unwrap()).unwrap_err().0;
        let named = e.starts_with("the winter crop refused: winter_crop is pinned none");
        assert!(named && e.contains("of the 13.60 acres"), "{middle}: {e}");
        assert!(e.contains("pin barley"), "{middle}: {e}");
    }
    // ...and a bare winter whose dry ground holds the need is left bare (Inashiro)
    let fed = r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#;
    let f = roll(&parse(fed).unwrap()).unwrap();
    assert_eq!(f.knobs["winter_crop"], "none");
    assert!(f.grain.unwrap().0 >= 15.0 * 0.85);
}

/// A DIKE-POND'S WATER IS ITS POND CANALS (449 T420): the feeder, the ring's supply reaches and the creeks, each creek one stroke
/// at the block's 6 to 8 ft (0018's drawing page), are `pond canal` in the census; a rice polder's stay irrigation ditches.
#[test]
fn a_dike_ponds_channels_are_pond_canals_drawn_at_the_creeks_width() {
    let kuwabata = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    let s = kuwabata.polder.as_ref().unwrap();
    let between = |d: &&crate::field::polder::Ditch| d.seg == "column" || d.seg == "row";
    let creeks: Vec<_> = s.polder.ditches.iter().filter(between).collect();
    let w = creeks[0].w;
    let one = creeks.iter().all(|d| (d.w_tail - w).abs() < 1e-12);
    assert!((6.0..=8.0).contains(&w) && one);
    // the feeder, the ring's four supply reaches (two trunks, the far flank, the inlet's join) and each creek
    assert_eq!(kuwabata.ink.get("pond canal"), Some(&(creeks.len() + 5)));
    assert_eq!(kuwabata.ink.get("irrigation ditch"), None);
    let stroke = format!(r#"stroke-width="{}""#, (w * 10.0).round() / 10.0);
    assert!(kuwabata.svg.matches(stroke.as_str()).count() >= creeks.len());
    let rice = roll(&parse(r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#).unwrap()).unwrap();
    assert!(rice.ink.contains_key("irrigation ditch") && !rice.ink.contains_key("pond canal"));
}

#[test]
fn a_fall_square_across_the_wind_seats_at_the_heads_windward_corner_astride_its_intake() {
    // 449 T426: `make seeds`' fresh comb seed 941239097 and seed 508 at 20 households falling at 135 degrees were refused by the seat
    // ("1 walled in"), and 508 was still written as a map with no settlement, a bare winter and no dry fields
    let fresh = roll(&super::cohort_spec(941_239_097, None)).unwrap();
    let declared = roll(
        &parse(r#"{"name": "S508", "seed": 508, "households": 20, "down_deg": 135}"#).unwrap(),
    )
    .unwrap();
    for r in [&fresh, &declared] {
        assert_eq!(
            r.stages,
            vec!["water_frame", "field", "sink", "seat", "hem"]
        );
        // its back to the wind still, and no rule of the finished map broken
        assert!(r.seated.as_ref().is_some_and(|s| !s.frames[0].offwind));
        assert_eq!(super::check::check(r), Vec::<String>::new());
    }
    // a roll that kept a stage's refusal is refused whole: no map is handed back to be written
    let mut kept = declared;
    kept.refusals.push("the seat refused: x".into());
    assert_eq!(
        super::whole(kept).unwrap_err().0,
        "the seat refused: x - no map is drawn of a hamlet a stage refused"
    );
}

#[test]
fn a_rice_polder_s_pocket_pond_is_never_off_its_low_row() {
    // 449 T429: seed 183 at ten households lays every last-row plot a merged pair, and the pond fell to a top-row plot
    // (0008: "Our maps sink each pond wholly inside one low plot")
    for rest in ["", r#", "pins": {"paddy_rest": "unsettled"}"#] {
        let spec = format!(
            r#"{{"name": "P", "seed": 183, "households": 10, "down_deg": 90, "field_archetype": "polder_grid"{rest}}}"#
        );
        let r = roll(&parse(&spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let reached = s
            .polder
            .plots
            .iter()
            .filter(|p| p.low)
            .all(|p| p.ring.len() != 4);
        assert!(reached, "the case no longer reached");
        let drawn = s.pocket.is_some();
        assert!(!drawn, "{rest}: a pond with no low four-sided plot left");
    }
}

/// A DIKE-POND BLOCK'S PONDS HOLD THEIR BANKS (449 T430): on the rolled mosaics whose drift left a parcel too small for its
/// bank or folded a bent pair's water over it, every pond keeps its bank's width all round (a foot and a half of slack for a
/// corner's rounding), none falls to the least pond for the bend alone, and no bush or hedge stands in a pond's water.
#[test]
fn a_dike_pond_block_s_ponds_hold_their_banks_and_no_bush_stands_in_one() {
    use crate::field::geom::{inside, seg_dist, signed_area};
    for seed in [14, 47, 51, 54, 75, 79] {
        let spec = format!(
            r#"{{"name": "P", "seed": {seed}, "households": 15, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}}"#
        );
        let r = roll(&parse(&spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let (parcels, crops, inset) = s.converted.as_ref().unwrap();
        for q in parcels {
            let Some((_, w)) = &q.water else { continue };
            let n = q.ring.len();
            let line = |p: (f64, f64)| {
                (0..n)
                    .map(|k| seg_dist(p, q.ring[k], q.ring[(k + 1) % n]))
                    .fold(f64::INFINITY, f64::min)
            };
            let near = w.iter().map(|&p| line(p)).fold(f64::INFINITY, f64::min);
            let (bank, at) = (*inset, near);
            assert!(at >= bank - 1.5, "seed {seed}: {at:.1} of {bank:.1}");
            let share = signed_area(w).abs() / signed_area(&q.ring).abs();
            assert!(share > 0.02, "seed {seed}: a speck pond, {share:.3} of it");
            let wet = crops
                .crowns
                .iter()
                .filter(|c| inside((c.0, c.1), w))
                .count()
                + crops
                    .hedges
                    .iter()
                    .flatten()
                    .filter(|&&p| inside(p, w))
                    .count();
            assert_eq!(wet, 0, "seed {seed}: crowns or hedge points in a pond");
        }
    }
}
