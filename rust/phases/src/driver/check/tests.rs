//! The finished map's checks' unit tests (449 T435: moved out of `check.rs`, past the 1,000-line bar).
//!
//! Research:
//!     the checks' tests - NONE: fixtures and assertions, deciding nothing about the place

use super::{check, depth_inside, mean, polder_checks};
use crate::driver::{roll, spec::parse};
use crate::field::dry::DryPlot;

#[test]
fn a_dry_plot_on_the_belts_ground_at_the_bands_windward_end_is_named() {
    // Inashiro's back faces the northwest wind 45 degrees off square (449 T294), so its belt wraps the band's windward end: a
    // plot there, past the band's half-length, stands on the belt's ground and is named, as one behind the band's middle is
    let mut r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    let f = r.seated.as_ref().unwrap().frames[0].clone();
    let w = crate::driver::wind(&r.plan.windward);
    let side = (w.0 * f.along.0 + w.1 * f.along.1).signum();
    let at = (
        f.center.0 + f.along.0 * f.band.0 * side + w.0 * 80.0,
        f.center.1 + f.along.1 * f.band.0 * side + w.1 * 80.0,
    );
    let past = (at.0 - f.center.0) * f.along.0 + (at.1 - f.center.1) * f.along.1;
    assert!(past.abs() > f.band.0 + 50.0, "{past}");
    r.dry = vec![DryPlot {
        poly: vec![
            (at.0 - 4.0, at.1 - 4.0),
            (at.0 + 4.0, at.1 - 4.0),
            (at.0 + 4.0, at.1 + 4.0),
            (at.0 - 4.0, at.1 + 4.0),
        ],
        crop: "soy",
        theta: 0.0,
        tract: 0,
    }];
    let found = check(&r).join("\n");
    assert!(found.contains("dry_on_settlement: dry plot 0"), "{found}");
}

#[test]
fn a_planted_break_is_named() {
    // a roll to plant the breaks on; whether a seed rolls clean is the fresh seeds' question (`hamlet --seeds`), never a fixed
    // seed's (the GM 2026-11-07: "We should probably avoid fixed seeds because of overfitting")
    let mut r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    let fan = r.fields[0].fan.ring.clone();
    let m = mean(&fan);
    let square = |c: (f64, f64), s: f64| {
        vec![
            (c.0 - s, c.1 - s),
            (c.0 + s, c.1 - s),
            (c.0 + s, c.1 + s),
            (c.0 - s, c.1 + s),
        ]
    };
    let on_water = r.fields[0].channels[0].pts[1];
    r.dry = vec![
        DryPlot {
            poly: square(m, 20.0),
            crop: "barley",
            theta: 0.0,
            tract: 0,
        },
        DryPlot {
            poly: square(m, 10.0),
            crop: "barley",
            theta: 0.0,
            tract: 0,
        },
        DryPlot {
            poly: square(on_water, 0.5),
            crop: "soy",
            theta: 0.0,
            tract: 1,
        },
        DryPlot {
            poly: square((-50.0, -50.0), 5.0),
            crop: "millet",
            theta: 0.0,
            tract: 2,
        },
    ];
    let reed = r.sunk.as_ref().map(|s| mean(&s.reeds)).unwrap();
    let home = mean(&crate::driver::settlement_ground(
        &r.seated.as_ref().unwrap().frames[0],
        crate::driver::wind(&r.plan.windward),
    ));
    r.dry.push(DryPlot {
        poly: square(home, 5.0),
        crop: "soy",
        theta: 0.0,
        tract: 4,
    });
    r.dry.push(DryPlot {
        poly: square(reed, 5.0),
        crop: "soy",
        theta: 0.0,
        tract: 3,
    });
    if let Some(s) = r.sunk.as_mut() {
        s.pond = Some((m, 30.0, 20.0));
    }
    if let Some(s) = r.seated.as_mut() {
        s.frames[0].center = m;
    }
    let found = check(&r).join("\n");
    for rule in [
        "dry_on_paddy",
        "dry_on_water",
        "dry_on_dry",
        "off_canvas: dry plot",
        "pond_on_paddy",
        "seat_on_field",
        "reeds_on_dry",
        "dry_on_settlement",
    ] {
        assert!(found.contains(rule), "{rule} not named in:\n{found}");
    }
    r.fields[0].fan.ring.push((-10.0, -10.0));
    r.sunk.as_mut().unwrap().pond = Some(((-5.0, -5.0), 30.0, 20.0));
    let found = check(&r).join("\n");
    assert!(found.contains("off_canvas: the field") && found.contains("off_canvas: the tameike"));
    assert!(depth_inside((0.0, 0.0), &[(0.0, 0.0), (1.0, 0.0)]) == 0.0);
    let mut p = roll(&parse(r#"{"name": "K", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}"#).unwrap()).unwrap();
    let block = p.polder.as_ref().unwrap().polder.outline.clone();
    let mid = mean(&block);
    p.seated.as_mut().unwrap().frames[0].center = mid;
    p.waterward.as_mut().unwrap().strips.push(vec![
        (mid.0 - 5.0, mid.1 - 5.0),
        (mid.0 + 5.0, mid.1 - 5.0),
        (mid.0, mid.1 + 5.0),
    ]);
    let found = check(&p).join("\n");
    assert!(
        found.contains("seat_on_field: the settlement's band lies over the polder")
            && found.contains("reeds_on_field")
    );
    p.polder.as_mut().unwrap().polder.outline.push((-9.0, -9.0));
    assert!(check(&p).join("\n").contains("off_canvas: the polder"));
}

/// A WATERCOURSE THROUGH A PLOT, OR ENDING IN IT, OR A POND ROUND IT (449 T433): 0006's drawing drops a dry plot that comes within
/// about a foot of any water the map draws or would have the end of one inside it, so the check asks the plot's whole area. Red
/// before T433: the check asked only a plot's corners against the channels, the brook and the run, and named none of the first
/// three plots - a brook through one's middle, a run ending in another, one standing in the pond - nor the fifth, half a foot inside
/// the clearance from a brook; the fourth, half a foot past it, is clear on both.
#[test]
fn a_watercourse_through_a_plot_or_ending_in_it_is_named() {
    let mut r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    let square = |c: (f64, f64), s: f64| {
        vec![
            (c.0 - s, c.1 - s),
            (c.0 + s, c.1 - s),
            (c.0 + s, c.1 + s),
            (c.0 - s, c.1 + s),
        ]
    };
    let plot = |c: (f64, f64), s: f64| DryPlot {
        poly: square(c, s),
        crop: "soy",
        theta: 0.0,
        tract: 0,
    };
    // the map's own water taken off, the water each plot is asked against planted on open ground
    r.fields[0].channels.clear();
    let past = crate::driver::BROOK_W / 2.0 + crate::hem::CLEAR_FT + 0.5;
    r.brooks = vec![
        vec![(990.0, 1020.0), (1080.0, 1020.0)],
        vec![(3980.0, 1040.0 + past), (4060.0, 1040.0 + past)],
        vec![(4980.0, 1039.0 + past), (5060.0, 1039.0 + past)],
    ];
    let s = r.sunk.as_mut().unwrap();
    s.run = vec![(1950.0, 1020.0), (2010.0, 1020.0)];
    s.pond = Some(((3000.0, 1000.0), 60.0, 40.0));
    s.reeds.clear();
    r.dry = vec![
        plot((1020.0, 1020.0), 20.0),
        plot((2000.0, 1020.0), 20.0),
        plot((3000.0, 1000.0), 5.0),
        plot((4020.0, 1020.0), 20.0),
        plot((5020.0, 1020.0), 20.0),
    ];
    let found = check(&r);
    let on: Vec<&String> = found
        .iter()
        .filter(|l| l.starts_with("dry_on_water"))
        .collect();
    assert_eq!(on.len(), 4, "{found:?}");
    for (i, how, what) in [
        (0, "ft from the edge of", "the brook"),
        (1, "reaching inside it", "the drain's run"),
        (2, "stands in", "the pond"),
        (4, "comes 0.5 ft from the edge of", "the brook"),
    ] {
        let tag = format!("dry plot {i} ");
        let named = on
            .iter()
            .any(|l| l.contains(&tag) && l.contains(how) && l.contains(what));
        assert!(named, "plot {i} {how} {what} not named in {on:?}");
    }
    // a plot just past the clearance from the pond's rim stands clear of it
    r.dry = vec![plot(
        (
            3000.0,
            1040.0 + super::super::POND_RIM_W / 2.0 + crate::hem::CLEAR_FT + 20.5,
        ),
        20.0,
    )];
    let found = check(&r).join("\n");
    assert!(!found.contains("dry_on_water"), "{found}");
}

/// A PADDY, A SETTLEMENT'S GROUND OR A REED BED ACROSS A PLOT'S MIDDLE (449 T434): 0006 keeps a dry plot off the rice, off the
/// houses' ground and clear of the pond's ground, and states no gap for any of them, so each check asks the plot's whole area
/// past the drawing's slack. Red before T434: the three checks asked only a plot's corners, and named none of the plots a
/// paddy, the settlement's ground or a reed bed crosses without holding a corner of (the first three), nor a reed clump
/// inside a plot, nor a plot lapping the reeds by a foot and a half; a plot lapping them by half a foot, within the slack, is
/// named by neither.
#[test]
fn a_field_ground_or_reeds_across_a_plots_middle_is_named() {
    use crate::field::fan::Pt;
    use crate::field::geom::inside;
    let mut r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    let rect = |x0: f64, y0: f64, x1: f64, y1: f64| vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)];
    let plot = |poly: Vec<Pt>| DryPlot {
        poly,
        crop: "soy",
        theta: 0.0,
        tract: 0,
    };
    let named = |r: &crate::driver::Rolled, rule: &str| -> Vec<String> {
        check(r)
            .into_iter()
            .filter(|l| l.starts_with(rule))
            .collect()
    };
    let no_corner_in = |poly: &[Pt], ring: &[Pt]| poly.iter().all(|c| !inside(*c, ring));
    // the paddy: a tongue of the field 20 ft wide through a plot's middle, past both its sides
    r.fields[0].fan.ring = rect(950.0, 1010.0, 1100.0, 1030.0);
    let p = rect(1000.0, 984.0, 1092.0, 1056.0);
    assert!(no_corner_in(&p, &r.fields[0].fan.ring));
    r.dry = vec![plot(p)];
    assert_eq!(named(&r, "dry_on_paddy").len(), 1, "{:?}", check(&r));
    // the settlement's ground as the seat chose it: a strip 20 ft deep running through its middle, past both its sides
    let ground = crate::driver::settlement_ground(
        &r.seated.as_ref().unwrap().frames[0],
        crate::driver::wind(&r.plan.windward),
    );
    let (lo, hi) = crate::field::index::bbox(&ground);
    let m = mean(&ground);
    let p = rect(lo.0 - 50.0, m.1 - 10.0, hi.0 + 50.0, m.1 + 10.0);
    assert!(no_corner_in(&p, &ground) && no_corner_in(&ground, &p));
    r.dry = vec![plot(p)];
    assert_eq!(named(&r, "dry_on_settlement").len(), 1, "{:?}", check(&r));
    // the reeds: a bed 20 ft wide through a plot's middle; a clump inside one; a plot lapping the bed 1.5 ft, then 0.5 ft
    let laps = |by: f64| rect(4000.0, 1030.0 - by, 4092.0, 1102.0 - by);
    for (bed, p, want) in [
        (3950.0, rect(4000.0, 984.0, 4092.0, 1056.0), 1),
        (4010.0, laps(1.5), 1),
        (4010.0, laps(0.5), 0),
    ] {
        r.sunk.as_mut().unwrap().reeds = rect(bed, 1010.0, 8090.0 - bed, 1030.0);
        assert!(no_corner_in(&p, &r.sunk.as_ref().unwrap().reeds));
        r.dry = vec![plot(p)];
        assert_eq!(named(&r, "reeds_on_dry").len(), want, "{:?}", check(&r));
    }
    r.sunk.as_mut().unwrap().reeds = rect(4040.0, 1015.0, 4050.0, 1025.0);
    r.dry = vec![plot(rect(4000.0, 984.0, 4092.0, 1056.0))];
    assert_eq!(named(&r, "reeds_on_dry").len(), 1, "{:?}", check(&r));
    // a plot under two slacks across is asked exactly: one standing across the bed is named
    r.sunk.as_mut().unwrap().reeds = rect(3950.0, 1010.0, 4100.0, 1030.0);
    r.dry = vec![plot(rect(4000.0, 1005.0, 4001.5, 1035.0))];
    assert_eq!(named(&r, "reeds_on_dry").len(), 1, "{:?}", check(&r));
    // a plot drawn in either way round, a corner on a straight side kept on it; a ring of two points meets nothing
    let square = vec![
        (0.0, 0.0),
        (5.0, 0.0),
        (10.0, 0.0),
        (10.0, 10.0),
        (0.0, 10.0),
    ];
    let reversed: Vec<Pt> = square.iter().rev().copied().collect();
    for ring in [square, reversed] {
        let inner = super::drawn_in(&ring, 1.0);
        let kept = (inner.contains(&(5.0, 1.0)), inner.contains(&(9.0, 9.0)));
        assert_eq!(kept, (true, true), "{inner:?}");
    }
    assert!(super::lies_over(&rect(0.0, 0.0, 9.0, 9.0), &[(1.0, 1.0), (5.0, 5.0)]).is_none());
}

/// THE SETTLEMENT'S GROUND OFF THE DIKE AND THE RING CANAL, ITS WAY OUT PAST THE REEDS (449 T240): Kuwabata as rolled passes the
/// polder's checks; a reed strip planted round its settlement is named as walling it in; and T239's unfixed roll - the seat handed the plots' edge as its ring, so its ground ran in over the dike and the head canal - is
/// named on both. Red before T240: the polder's checks tested only the seat's middle against the plots' edge, and named
/// nothing on T239's unfixed roll.
#[test]
fn a_settlement_over_the_dike_and_the_ring_canal_is_named() {
    let mut r = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    let rolled = polder_checks(&r);
    assert_eq!(rolled, Vec::<String>::new());
    let unfixed = {
        let s = r.polder.as_ref().unwrap();
        let ground = crate::driver::Ground {
            ring: &s.polder.outline,
            foot: None,
            lines: s
                .polder
                .ditches
                .iter()
                .map(|d| d.pts.as_slice())
                .chain([s.polder.feeder.as_slice(), s.outfall.as_slice()])
                .collect(),
            brook: &[],
            reeds: vec![s.polder.fringe.clone()],
            pond: None,
            back: None,
        };
        crate::driver::stage_seat(&r.plan, &ground).unwrap()
    };
    // a reed strip planted round the settlement walls its way out
    let c = r.seated.as_ref().unwrap().frames[0].center;
    let ring = vec![
        (c.0 - 500.0, c.1 - 500.0),
        (c.0 + 500.0, c.1 - 500.0),
        (c.0 + 500.0, c.1 + 500.0),
        (c.0 - 500.0, c.1 + 500.0),
    ];
    r.waterward.as_mut().unwrap().strips.push(ring);
    // (the planted strip, a 1,000 ft square, also lies over the polder's block: named apart, 449 T435)
    let walled: Vec<String> = polder_checks(&r)
        .into_iter()
        .filter(|l| l.starts_with("seat_"))
        .collect();
    let want_walled = vec![
        "seat_walled_by_reeds: no dry way out of the settlement past the waterside reeds"
            .to_owned(),
    ];
    assert_eq!(walled, want_walled);
    r.waterward.as_mut().unwrap().strips.pop();
    r.seated = Some(unfixed);
    let found = polder_checks(&r);
    let want = vec![
        "seat_on_dike: the settlement's ground reaches over the dike's outer face".to_owned(),
        "seat_on_canal: the settlement's ground lies over the ring canal".to_owned(),
    ];
    assert_eq!(found, want);
}

/// A rectangle from its low corner to its high one.
fn rect(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<crate::field::fan::Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

/// A dry plot of soy on `poly`.
fn soy(poly: Vec<crate::field::fan::Pt>) -> DryPlot {
    DryPlot {
        poly,
        crop: "soy",
        theta: 0.0,
        tract: 0,
    }
}

/// Whether the rolled hamlet's checks name `rule`.
fn named(rolled: &crate::driver::Rolled, rule: &str) -> bool {
    check(rolled).iter().any(|l| l.starts_with(rule))
}

/// A PLOT ACROSS ANOTHER, AND A PLOT PAST A PLOT'S SIZE (449 T435): 0006 lays the plots end to end, each its own ground, and
/// draws a plot roughly 92 ft across, giving no gap between plots, so `dry_on_dry` asks a plot's whole area past the drawing's
/// slack and `dry_size` holds the plot's two edges along the canal between the hem's pinch and its stretch. Red before T435:
/// `dry_on_dry` asked a plot's middle and nothing held a plot's size, so each case marked `true` went unnamed; a case marked
/// `false` is named by neither.
#[test]
fn a_plot_across_another_or_past_a_plots_size_is_named() {
    let mut seen: Vec<(String, bool, bool)> = Vec::new();
    let mut hamlet = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    // two plots: one across another with no corner or middle in it, a corner lapped 1.5 ft, abutting, lapped 0.5 ft
    let first = rect(1000.0, 1020.0, 1092.0, 1040.0);
    for (case, other, want) in [
        ("across", rect(1070.0, 980.0, 1080.0, 1060.0), true),
        ("a corner in", rect(1080.0, 1035.0, 1090.0, 1115.0), true),
        ("lapped 1.5 ft", rect(1090.5, 1020.0, 1182.5, 1040.0), true),
        ("abutting", rect(1092.0, 1020.0, 1184.0, 1040.0), false),
        ("lapped 0.5 ft", rect(1091.5, 1020.0, 1183.5, 1040.0), false),
    ] {
        hamlet.dry = vec![soy(first.clone()), soy(other)];
        seen.push((
            format!("dry_on_dry {case}"),
            named(&hamlet, "dry_on_dry"),
            want,
        ));
    }
    // a plot's size: a plot, one at the stretch's bound, a wedge whose short edge forbids cutting it, a pinched edge, five corners
    for (case, poly, want) in [
        ("a plot", rect(0.0, 0.0, 91.4, 71.5), false),
        ("at the bound", rect(0.0, 0.0, 137.1, 71.5), false),
        (
            "a wedge",
            vec![(0.0, 0.0), (55.0, 0.0), (150.0, 71.5), (-100.0, 71.5)],
            true,
        ),
        ("pinched", rect(0.0, 0.0, 40.0, 71.5), true),
        (
            "five corners",
            vec![
                (0.0, 0.0),
                (91.4, 0.0),
                (91.4, 71.5),
                (40.0, 80.0),
                (0.0, 71.5),
            ],
            true,
        ),
    ] {
        hamlet.dry = vec![soy(poly)];
        seen.push((format!("dry_size {case}"), named(&hamlet, "dry_size"), want));
    }
    let (got, wanted): (Vec<_>, Vec<_>) = seen.iter().map(|s| ((&s.0, s.1), (&s.0, s.2))).unzip();
    assert_eq!(got, wanted);
}

/// A POND ACROSS A TONGUE OF PADDY, THE HOUSES' BAND PAST ITS DIP, A REED STRIP LAPPING THE POLDER (449 T435): the pond at the
/// field's foot (0060), the houses beside their paddy (0031), the reeds outside the dike (0019), none giving a gap, so each check
/// asks the whole area past the drawing's slack - the band's near edge drawn back by the seat's own tenth first. Red before T435:
/// the checks asked sixteen points of the pond's rim and its middle, the band's middle and a strip's middle, so each case marked
/// `true` went unnamed; a case marked `false` is named by neither.
#[test]
fn a_pond_band_or_reed_strip_lapping_the_field_is_named() {
    let mut seen: Vec<(String, bool, bool)> = Vec::new();
    let mut hamlet = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
    hamlet.dry.clear();
    // the pond: a tongue of paddy across it between the old rim's points, and one lapping its rim by under the slack
    let pond = (3000.0, 1000.0);
    hamlet.sunk.as_mut().unwrap().pond = Some((pond, 60.0, 40.0));
    for (case, tongue, want) in [
        (
            "across",
            rect(0.0, pond.1 + 17.0, 9000.0, pond.1 + 27.0),
            true,
        ),
        (
            "lapped 0.4 ft",
            rect(0.0, pond.1 + 39.6, 9000.0, pond.1 + 60.0),
            false,
        ),
    ] {
        hamlet.fields[0].fan.ring = tongue;
        seen.push((
            format!("pond_on_paddy {case}"),
            named(&hamlet, "pond_on_paddy"),
            want,
        ));
    }
    // the settlement's band: the field reaching into its near edge past the seat's tenth of its depth, and within it
    hamlet.sunk.as_mut().unwrap().pond = None;
    let frame = hamlet.seated.as_ref().unwrap().frames[0].clone();
    let (lat, half) = frame.band;
    let on_band = |along: f64, out: f64| {
        (
            frame.center.0 + frame.along.0 * along + frame.out.0 * out,
            frame.center.1 + frame.along.1 * along + frame.out.1 * out,
        )
    };
    for (case, reach, want) in [
        ("past the dip", 0.3 * half, true),
        ("within the dip", 0.2 * half - 0.5, false),
    ] {
        hamlet.fields[0].fan.ring = vec![
            on_band(-lat - 50.0, -half - 100.0),
            on_band(lat + 50.0, -half - 100.0),
            on_band(lat + 50.0, -half + reach),
            on_band(-lat - 50.0, -half + reach),
        ];
        seen.push((
            format!("seat_on_field {case}"),
            named(&hamlet, "seat_on_field"),
            want,
        ));
    }
    // a polder's reed strip lapping its block 10 ft with its middle outside, and one lapping it 0.5 ft
    let mut polder = roll(&parse(r#"{"name": "K", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}"#).unwrap()).unwrap();
    let block = polder.polder.as_ref().unwrap().polder.outline.clone();
    let (middle, edge) = (mean(&block), mean(&block[..2]));
    let away = (edge.0 - middle.0).hypot(edge.1 - middle.1);
    let normal = ((edge.0 - middle.0) / away, (edge.1 - middle.1) / away);
    let side = (block[1].0 - block[0].0, block[1].1 - block[0].1);
    let length = side.0.hypot(side.1);
    let tangent = (side.0 / length, side.1 / length);
    let strip = |inside: f64| {
        let at = |along: f64, out: f64| {
            (
                edge.0 + tangent.0 * along + normal.0 * out,
                edge.1 + tangent.1 * along + normal.1 * out,
            )
        };
        vec![
            at(-50.0, -inside),
            at(50.0, -inside),
            at(50.0, 40.0),
            at(-50.0, 40.0),
        ]
    };
    for (case, inside, want) in [("lapped 10 ft", 10.0, true), ("lapped 0.5 ft", 0.5, false)] {
        polder.waterward.as_mut().unwrap().strips = vec![strip(inside)];
        seen.push((
            format!("reeds_on_field {case}"),
            named(&polder, "reeds_on_field"),
            want,
        ));
    }
    let (got, wanted): (Vec<_>, Vec<_>) = seen.iter().map(|s| ((&s.0, s.1), (&s.0, s.2))).unzip();
    assert_eq!(got, wanted);
}
