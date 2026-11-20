//! The driver's rolls end to end: a comb and the polders through their stages, the record, the ink census (feature 444 T42, 449 T230).
//!
//! Research:
//!     the driver's tests - NONE: fixtures and assertions; each rule's claim is at the unit it tests

use super::{manifest, roll, spec::parse};

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
    const KINDS: [&str; 23] = [
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
