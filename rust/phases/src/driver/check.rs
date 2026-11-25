//! The finished map's checks (feature 444 T42; the GM 2026-11-07: "focus entirely on our Rust code ... until our Rust is solid"):
//! what a stage drew read back against the rules its research keeps, so the cohort finds a stage that draws a thing wrong, not
//! only one that refuses. Each check names what it found; none moves anything.
//!
//! Research:
//!     the map's checks - NONE: read-only, each rule's claim at the Rust that keeps it while laying

use super::Rolled;
use crate::field::fan::Pt;
use crate::field::geom::{inside, seg_dist};

/// How far inside a ring a point must stand to count as on it, and how close to a line's water past its half-width (ft): a
/// drawing's slack, so two features sharing an edge read as neighbors.
///
/// Research:
///     the drawing's slack - CONVENTION: a foot, under a bund's 1.5 ft stroke, so a shared edge is not an overlap
const SLACK_FT: f64 = 1.0;

fn depth_inside(p: Pt, ring: &[Pt]) -> f64 {
    if ring.len() < 3 || !inside(p, ring) {
        return 0.0;
    }
    (0..ring.len())
        .map(|i| seg_dist(p, ring[i], ring[(i + 1) % ring.len()]))
        .fold(f64::MAX, f64::min)
}

fn mean(ring: &[Pt]) -> Pt {
    #[expect(
        clippy::cast_precision_loss,
        reason = "a ring of a few hundred corners"
    )]
    let n = ring.len().max(1) as f64;
    (
        ring.iter().map(|p| p.0).sum::<f64>() / n,
        ring.iter().map(|p| p.1).sum::<f64>() / n,
    )
}

/// The rolled hamlet's violations, each a line naming the rule, what broke it and where; none on a sound map.
///
/// Research:
///     no dry plot on the paddy - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry fields stand beyond the paddy, along the canal's high side
///     no dry plot on the water - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry plots kept to the dry side of the canal, behind a bare bank - tested against the field's channels, the brook and the drain's run (the pond's rim is `reed_checks`' reeds')
///     no dry plot on another - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: plots laid end to end, each its own ground
///     the tameike off the paddy - research/questions/0060-field-drains-akusuiro.drawing.html: the pond at the field's foot, below it
///     the settlement off the field - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the houses on the field's margin, beside the paddy
///     on the canvas - CONVENTION: the map is drawn on its canvas; only the brook and the drain's run leave it
#[must_use]
pub fn check(r: &Rolled) -> Vec<String> {
    let mut out = Vec::new();
    let (w, h) = (r.plan.w, r.plan.h);
    let off = |p: &Pt| p.0 < 0.0 || p.1 < 0.0 || p.0 > w || p.1 > h;
    let rings: Vec<&[Pt]> = r.fields.iter().map(|f| f.fan.ring.as_slice()).collect();
    let water: Vec<(Pt, Pt, f64)> = r
        .fields
        .iter()
        .flat_map(|f| {
            f.channels.iter().flat_map(|c| {
                c.pts
                    .windows(2)
                    .map(move |s| (s[0], s[1], c.w.max(c.w_tail)))
            })
        })
        .chain(
            r.brooks
                .iter()
                .flat_map(|b| b.windows(2).map(|s| (s[0], s[1], super::BROOK_W))),
        )
        .chain(
            r.sunk
                .iter()
                .flat_map(|s| s.run.windows(2).map(|w| (w[0], w[1], super::RUN_W))),
        )
        .collect();
    for (i, d) in r.dry.iter().enumerate() {
        if let Some(p) = d
            .poly
            .iter()
            .find(|p| rings.iter().any(|ring| depth_inside(**p, ring) > SLACK_FT))
        {
            out.push(format!(
                "dry_on_paddy: dry plot {i} has a corner inside the field at ({:.0}, {:.0})",
                p.0, p.1
            ));
        }
        if let Some(p) = d.poly.iter().find(|p| {
            water
                .iter()
                .any(|&(a, b, ww)| seg_dist(**p, a, b) < ww / 2.0 - SLACK_FT)
        }) {
            out.push(format!(
                "dry_on_water: dry plot {i} has a corner on the water at ({:.0}, {:.0})",
                p.0, p.1
            ));
        }
        let m = mean(&d.poly);
        if let Some(j) = r
            .dry
            .iter()
            .enumerate()
            .position(|(j, e)| j != i && depth_inside(m, &e.poly) > SLACK_FT)
        {
            out.push(format!(
                "dry_on_dry: dry plot {i}'s middle stands inside dry plot {j}"
            ));
        }
        if d.poly.iter().any(off) {
            out.push(format!("off_canvas: dry plot {i}"));
        }
    }
    for (c, rx, ry) in r.sunk.iter().filter_map(|s| s.pond) {
        let rim: Vec<Pt> = (0..16)
            .map(|k| f64::from(k) * std::f64::consts::PI / 8.0)
            .map(|a| (c.0 + rx * a.cos(), c.1 + ry * a.sin()))
            .collect();
        let reaches = rim
            .iter()
            .chain(std::iter::once(&c))
            .any(|p| rings.iter().any(|ring| depth_inside(*p, ring) > SLACK_FT));
        out.extend(reaches.then(|| {
            format!(
                "pond_on_paddy: the tameike at ({:.0}, {:.0}) reaches inside the field",
                c.0, c.1
            )
        }));
        out.extend(
            rim.iter()
                .any(off)
                .then(|| "off_canvas: the tameike".to_owned()),
        );
    }
    out.extend(reed_checks(r));
    for f in r.seated.iter().filter_map(|s| s.frames.first()) {
        let on = rings
            .iter()
            .any(|ring| depth_inside(f.center, ring) > SLACK_FT);
        out.extend(on.then(|| {
            format!(
                "seat_on_field: the settlement's middle ({:.0}, {:.0}) stands inside the field",
                f.center.0, f.center.1
            )
        }));
    }
    out.extend(polder_checks(r));
    if rings.iter().any(|ring| ring.iter().any(off)) {
        out.push("off_canvas: the field".to_owned());
    }
    out
}

/// The tameike's reeds off the dry plots; the paddy is painted over them, the deleted `pond_reeds`' cut on the sheet (`roll`).
///
/// Research:
///     no dry plot in the reeds - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry plots laid clear of the water and the pond's ground
///     no dry plot on the settlement's ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields, so no plot stands where they do (`dry_on_settlement`)
fn reed_checks(r: &Rolled) -> Vec<String> {
    let ground: Vec<Vec<Pt>> = r
        .seated
        .iter()
        .filter_map(|s| s.frames.first())
        .map(|f| super::settlement_ground(f, super::wind(&r.plan.windward)))
        .collect();
    let on_ground = r.dry.iter().enumerate().filter_map(|(i, d)| {
        d.poly
            .iter()
            .any(|p| ground.iter().any(|g| depth_inside(*p, g) > SLACK_FT))
            .then(|| {
                format!("dry_on_settlement: dry plot {i} has a corner on the settlement's ground")
            })
    });
    r.sunk
        .iter()
        .filter(|s| s.reeds.len() >= 3)
        .filter_map(|s| {
            r.dry
                .iter()
                .position(|d| d.poly.iter().any(|p| depth_inside(*p, &s.reeds) > SLACK_FT))
        })
        .map(|i| format!("reeds_on_dry: dry plot {i} has a corner inside the tameike's reeds"))
        .chain(on_ground)
        .collect()
}

/// The segments of a polder's ring canal, the four ditches round the inside foot of its dike.
///
/// Research:
///     the ring canal - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a ring canal round the inside foot of the dike, on the field side - the head canal, the two flank canals and the drain at the tail, the four ditches the polder lays at the dike's foot
const RING_CANAL: [&str; 4] = ["feeder", "w_toe", "e_toe", "drain"];

/// How far apart a ring canal's course is sampled against the settlement's ground (ft).
///
/// Research:
///     the canal's samples - NONE: a check's grain, under the ring canal's narrowest 1.5 ft lateral's reach into a ground it crosses
const CANAL_STEP_FT: f64 = 2.0;

/// The settlement's ground against the polder: whether it reaches over the dike's outer face (a corner of it inside the face, or
/// a point of the face inside it, past the slack), and whether any of the ring canal's course lies on it.
///
/// Research:
///     over the dike and the canal - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village on the dry ground just off the dike, and from outside in the wild water, the dike, the ring canal - so the ground is tested against the dike's outer face and the canal's course
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn ground_on_polder(ground: &[Pt], s: &crate::field::staged::PolderStage) -> (bool, bool) {
    let outer = &s.dike.outer;
    let dike = ground.iter().any(|p| depth_inside(*p, outer) > SLACK_FT)
        || outer.iter().any(|p| depth_inside(*p, ground) > SLACK_FT);
    let canal = s
        .polder
        .ditches
        .iter()
        .filter(|d| RING_CANAL.contains(&d.seg))
        .flat_map(|d| d.pts.windows(2))
        .any(|seg| {
            let (a, b) = (seg[0], seg[1]);
            let len = ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt();
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a canal reach's samples, a few thousand at most"
            )]
            let n = (len / CANAL_STEP_FT).ceil().max(1.0) as u32;
            (0..=n).any(|k| {
                let t = f64::from(k) / f64::from(n);
                let p = (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t);
                depth_inside(p, ground) > SLACK_FT
            })
        });
    (dike, canal)
}

/// Whether the settlement at `center` has no dry way out of the map once the waterside reeds are laid: the seat asked its way out
/// before the strips, so it is asked again with them - each strip and the wild pond's fringe grown by the lane's width, the dike's
/// outer face, and the polder's channels as the lines a track may not cross.
///
/// Research:
///     a dry way out past the reeds - research/questions/0081-village-lanes.drawing.html: every way keeps off every marsh's reeds and a track crosses no water - the strips and the fringe grown by the lane's width as walls, the channels as lines
///     the polder a wall - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0081-village-lanes.drawing.html: the polder enclosed by its dike all the way round, and a lane stops at the flooded paddy and never crosses row crops, so no way out runs over the dike or through the fields - the dike's outer face a wall, as the seat's own walk takes its ring
fn walled_by_reeds(r: &Rolled, s: &crate::field::staged::PolderStage, center: Pt) -> bool {
    let mut counts = std::collections::HashMap::new();
    let mut walls: Vec<crate::seat::Wall> = r
        .waterward
        .iter()
        .flat_map(|w| w.strips.iter())
        .chain(std::iter::once(&s.polder.fringe))
        .filter(|w| w.len() >= 3)
        .map(|w| (super::toe::grow(w, super::LANE_FT, &mut counts), 0.0))
        .collect();
    walls.push((s.dike.outer.clone(), 0.0));
    let lines: Vec<(Pt, Pt)> = s
        .polder
        .ditches
        .iter()
        .map(|d| d.pts.as_slice())
        .chain([s.polder.feeder.as_slice(), s.outfall.as_slice()])
        .flat_map(|p| p.windows(2).map(|w| (w[0], w[1])))
        .collect();
    !crate::seat::exit::Exit::new(&walls, &lines, (r.plan.w, r.plan.h), &mut counts)
        .has_exit(center, &mut counts)
}

/// A polder's own checks: its seat off its block, a dry way out of it past the waterside reeds, the settlement's ground off the dike
/// and the ring canal, its waterside reeds off its ground, the block on the canvas.
///
/// Research:
///     the polder's checks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the reeds outside the dike on the flanks that face the water, the settlement on the block's dry shore
///     the way out past the waterside reeds - research/questions/0081-village-lanes.drawing.html: every way keeps off every marsh's reeds - the seat's way out asked again once the strips it came before are laid (`seat_walled_by_reeds`)
///     the settlement's ground off the dike and the ring canal - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village drawn on the dry ground just off the dike, and from outside in the wild water, the dike, the ring canal, the field ditches and the paddies - so no part of the settlement's ground lies over the dike's outer face or the ring canal at its inside foot (`seat_on_dike`, `seat_on_canal`)
fn polder_checks(r: &Rolled) -> Vec<String> {
    let mut out = Vec::new();
    let (w, h) = (r.plan.w, r.plan.h);
    let off = |p: &Pt| p.0 < 0.0 || p.1 < 0.0 || p.0 > w || p.1 > h;
    let Some(s) = &r.polder else {
        return out;
    };
    let block = &s.polder.outline;
    for f in r.seated.iter().filter_map(|x| x.frames.first()) {
        let on = depth_inside(f.center, block) > SLACK_FT;
        out.extend(on.then(|| {
            format!(
                "seat_on_field: the settlement's middle ({:.0}, {:.0}) stands inside the polder",
                f.center.0, f.center.1
            )
        }));
        out.extend(walled_by_reeds(r, s, f.center).then(|| {
            "seat_walled_by_reeds: no dry way out of the settlement past the waterside reeds"
                .to_owned()
        }));
        let (dike, canal) = ground_on_polder(
            &super::settlement_ground(f, super::wind(&r.plan.windward)),
            s,
        );
        out.extend(dike.then(|| {
            "seat_on_dike: the settlement's ground reaches over the dike's outer face".to_owned()
        }));
        out.extend(
            canal.then(|| {
                "seat_on_canal: the settlement's ground lies over the ring canal".to_owned()
            }),
        );
    }
    for (i, strip) in r.waterward.iter().flat_map(|w| w.strips.iter()).enumerate() {
        let on = depth_inside(mean(strip), block) > SLACK_FT;
        out.extend(on.then(|| {
            format!("reeds_on_field: waterside strip {i}'s middle stands inside the polder")
        }));
    }
    out.extend(
        block
            .iter()
            .any(off)
            .then(|| "off_canvas: the polder".to_owned()),
    );
    out
}

#[cfg(test)]
mod tests {
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
        assert!(
            found.contains("off_canvas: the field") && found.contains("off_canvas: the tameike")
        );
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
        assert!(found.contains("inside the polder") && found.contains("reeds_on_field"));
        p.polder.as_mut().unwrap().polder.outline.push((-9.0, -9.0));
        assert!(check(&p).join("\n").contains("off_canvas: the polder"));
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
        let walled = polder_checks(&r);
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
}
