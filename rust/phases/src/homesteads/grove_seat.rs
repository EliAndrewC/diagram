//! A scattered hamlet's grove farms seated (feature 444 T30, from `homesteads/stages.py` `_seat_households_as`'s scattered branch,
//! `seats.py` `front_row`, `rank_rounds.py`, `capacity.py` `seat_the_rest` and `rolling/place.py` `_place_bundle_dispersed`): a front
//! row offset from the field's facing chains, each seat turned and pushed off the other ground, then ranks behind it in a brick and a
//! rescue cloud, then every free point of the ground - each offer the spiral placer's: the nearest seat that fits, slid against the
//! field and then against its neighbor. A grove farm is judged by the fit test's grove half (`grove_fits`): its parts and every band
//! on free ground, its yard's and beds' sun kept from the bands, no fixture in a band but its persimmon in its own.
//!
//! Research:
//!     a scattered hamlet's seating - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a front row along the paddy's chords, ranks behind in a brick pattern, a rescue cloud, then the exhaustive pass; the whole line hugged to the field edge in single file where the line holds every farm
//!     front-row standoff from the field set by the house and its yard - research/questions/0029-farmhouses-minka.drawing.html: never nearer the paddy than 6 ft, the yard before the south wall turning with the house as one
//!     a footpath's room off the outline - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a pushed seat cleared by `WEB_FABRIC_GAP` (7 ft) * 2 + 6 ft off the outline
//!     a lane's room between ranks - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `MIN_WEB_GAP`, 18 ft, kept between ranks
//!     a yard's sun between ranks - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the step adds `SUN_CORRIDOR_FT` by its north-south share
//!     the ranks' rounds and the rescue - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, 2026-10-25); round k at the row's depth plus k steps, center-out, four rank rounds then three rescue rounds, the band widened 22% and 16% a round
//!     the exhaustive seat order - research/questions/0029-farmhouses-minka.drawing.html: every legal grid point on the canvas, nearest the seat first, a tie broken by nearness to the field
//!     grove farm packed against the bund and its neighbor - GUESS: no source could speak to it, an algorithm's order of ours; the nearest fitting seat on a spiral, slid 2 ft at a time toward the field and then the nearest homestead
//!     yard drying strip kept from bands - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the yard seated with its grove's bands clear of a 22 ft strip south of it, a seating preference
//!     bed's morning-sun reach - research/questions/0038-sunlight-and-shade-on-the-farm.html: the band 22 ft, a departure the code keeps until feature 417 T33

#![expect(
    clippy::manual_midpoint,
    clippy::many_single_char_names,
    reason = "two edges summed at a map's few thousand feet, where no overflow is possible; the plane geometry's own names"
)]

use super::bundle::{grove_bundle, Bundle, Grove, Lot, Sun};
use super::fit::{sun_ok, too_near};
use super::fit_rules::{admitted, persimmon_conflict, unreachable, wall_on_the_bund, Chord};
use super::fixtures::Kind;
use super::layout::Rect;
use super::place::{Seating, Site};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::pyrand::PyRandom;
use crate::ways::track::in_poly;

/// The seating's figures (feet): a bundle's pitch, the front row's standoff slack, a house's wall gap off the paddy and its slack,
/// a footpath's room off the outline, the lane's room between ranks, the yard's sun corridor, a seat's near-a-house reach, the spiral's
/// step and reach, and the slide's step and steps.
///
/// Research:
///     the bundle's pitch - research/questions/0029-farmhouses-minka.drawing.html: 100 ft between homesteads, `BUNDLE_PITCH`
///     front-row standoff - research/questions/0029-farmhouses-minka.drawing.html: the wall 6 ft off the paddy, 1 ft of rounding and 3 of slack
///     a footpath's room - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft each side and 6 ft, 20
///     a lane's room between ranks - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 18 ft
///     a yard's sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 39 ft
///     its search steps and tolerances - NONE: a seat within half a pitch of a house is the same guess again (50); the spiral's rings 7 ft apart out to 91, 14 on a row's exact seat, 12 bearings; the slide 2 ft a step, 48 steps, stopped within 1.5 ft
pub const SEAT: (f64, f64, f64, f64, f64, f64, f64) = (100.0, 3.0, 7.0, 20.0, 18.0, 39.0, 50.0);

/// The grove farm's sun strips (feet): the yard's drying strip south of it, and a bed's morning-sun reach east.
///
/// Research:
///     yard drying strip width - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the strip 22 ft, a width 0038 does not give
///     bed's morning-sun reach - research/questions/0038-sunlight-and-shade-on-the-farm.html: 22 ft, a departure the code keeps until feature 417 T33
pub const STRIPS: (f64, f64) = (22.0, 22.0);

/// The seat band's axes: its seat center, the field-margin bearing along it and the bearing out from the field, the anchor its
/// front row's stretch is measured from, and its half-length and half-depth.
#[derive(Clone, Copy, Debug)]
pub struct Axes {
    /// The seat's center.
    pub c: Pt,
    /// Along the field margin.
    pub along: Pt,
    /// Out from the field.
    pub out: Pt,
    /// The front row's stretch is measured from here.
    pub anchor: Pt,
    /// The band's half-length.
    pub lat: f64,
}

/// The other ground's outline as rings with holes, and the water courses with their clearance (`boundary.py` `SiteCorridors`).
#[derive(Default)]
pub struct Corridors {
    /// The outline's exterior rings.
    pub rings: Vec<Vec<Pt>>,
    /// Its holes.
    pub holes: Vec<Vec<Pt>>,
    /// The water courses, each segment with its clearance.
    pub water: Vec<(Pt, Pt, f64)>,
}

impl Corridors {
    /// Does any of `pts` stand within a course's clearance, or inside the outline (an exterior ring and none of its holes), or a ring's
    /// vertex inside the points' box (`SiteCorridors.hit_points`)?
    #[must_use]
    pub fn hit_points(&self, pts: &[Pt], tests: &mut Counts) -> bool {
        let (x0, y0, x1, y1) = pts
            .iter()
            .fold((f64::MAX, f64::MAX, f64::MIN, f64::MIN), |m, p| {
                (m.0.min(p.0), m.1.min(p.1), m.2.max(p.0), m.3.max(p.1))
            });
        tests.add("pt_test@hit_points", (pts.len() * self.water.len()) as u64);
        pts.iter()
            .any(|&p| self.water.iter().any(|&(a, b, c)| seg_dist(p, a, b) < c))
            || self.rings.iter().any(|r| {
                pts.iter()
                    .any(|&p| in_poly(p, r) && !self.holes.iter().any(|h| in_poly(p, h)))
                    || r.iter()
                        .any(|v| v.0 >= x0 && v.0 <= x1 && v.1 >= y0 && v.1 <= y1)
            })
    }
}

/// What a scattered hamlet's seating reads besides the placer's site: the grove its farms carry, the paddies the slide hugs, the other
/// ground and the water, the seat band, the facing chains its front row is offset from, the largest house the roll can take, the
/// cluster's shape, whether the lanes are alleys, the map's seed, the households wanted, the band's reach, and whether the farms
/// stand in single file round the fields.
#[derive(Clone, Copy)]
pub struct GroveSite<'a> {
    /// The placer's site.
    pub site: &'a Site<'a>,
    /// The grove its farms carry.
    pub grove: Grove,
    /// The paddy outlines.
    pub paddies: &'a [Vec<Pt>],
    /// The other ground and the water.
    pub corridors: &'a Corridors,
    /// The seat band.
    pub axes: Axes,
    /// The chains the front row is offset from.
    pub chains: &'a [Vec<Chord>],
    /// The largest house the roll can take.
    pub house_max: (f64, f64),
    /// The cluster's shape.
    pub shape: &'a str,
    /// Whether the lanes are alleys (the ranks jittered off the line).
    pub alleys: bool,
    /// The map's seed.
    pub seed: i64,
    /// The households wanted.
    pub want: usize,
    /// The seating band's half-length and half-depth the ranks are stepped in (`plan.band_extent`).
    pub band: (f64, f64),
    /// How far from the seat center a homestead may stand.
    pub bound: f64,
    /// Whether the farms stand in single file round the fields.
    pub single_file: bool,
    /// A row village's planned streets while its farms are seated, and the half-width of the tread reserved on them (none off a row
    /// village).
    pub streets: (&'a [(Pt, Pt)], f64),
}

fn meet(a: Rect, b: Rect) -> bool {
    (a.0 - b.0).abs() < (a.2 + b.2) / 2.0 && (a.1 - b.1).abs() < (a.3 + b.3) / 2.0
}

fn round1(v: f64) -> f64 {
    (v * 10.0).round_ties_even() / 10.0
}

impl Seating {
    /// A grove farm's homestead for the lot at `at`, its rolls keyed on `seat`, its rake the seat's.
    fn lay_grove(&mut self, gs: &GroveSite, lot: &Lot, seat: Pt, at: Pt) -> Bundle {
        let site = gs.site;
        let turn = super::bearing::house_rot(
            at,
            site.bearing.1,
            site.bearing.0.follow(at, &mut self.tests),
        );
        let sun = Sun {
            shade: site.shade,
            turns: &[turn],
        };
        grove_bundle(
            lot,
            seat,
            at,
            turn,
            site.forms,
            &sun,
            &gs.grove,
            &mut self.tests,
        )
    }

    /// Is the box within 2 ft of a standing homestead's box or a box placed before the houses?
    fn lapped(&mut self, site: &Site, b: Rect) -> bool {
        let m = 2.0;
        let (lo, hi) = (
            (b.0 - b.2 / 2.0 - m, b.1 - b.3 / 2.0 - m),
            (b.0 + b.2 / 2.0 + m, b.1 + b.3 / 2.0 + m),
        );
        !self.standing.meeting(lo, hi, &mut self.tests).is_empty()
            || site.rules.placed.iter().any(|&p| {
                (b.0 - p.0).abs() < (b.2 + p.2) / 2.0 + m
                    && (b.1 - p.1).abs() < (b.3 + p.3) / 2.0 + m
            })
    }

    fn refused(&mut self, site: &Site, r: Rect) -> bool {
        site.ground.rect_refused(
            (r.0 - r.2 / 2.0, r.1 - r.3 / 2.0),
            (r.0 + r.2 / 2.0, r.1 + r.3 / 2.0),
            site.beyond,
            &mut self.tests,
        )
    }

    /// Would the placer refuse a grove farm whose house stands at `q` before laying it out (`place._seat_refused`): its house on taken
    /// ground, within 2 ft of a placed box, too near a neighbor's eaves, or deeper than a way's reach?
    fn grove_seat_refused(&mut self, gs: &GroveSite, lot: &Lot, q: Pt) -> bool {
        let site = gs.site;
        let house = (q.0, q.1, lot.house.0, lot.house.1);
        if self.refused(site, house) || self.lapped(site, house) {
            return true;
        }
        let turn =
            super::bearing::house_rot(q, site.bearing.1, site.bearing.0.follow(q, &mut self.tests));
        too_near(house, turn, &self.standing, &mut self.tests)
            || unreachable(q, site.rules, &mut self.tests)
    }

    /// Does a band of `b` stand in a standing yard's drying strip, or a standing band in `b`'s; a band in a standing bed's morning sun,
    /// or a standing band in one of `b`'s beds' (`fit._yard_sun_conflict`, `_garden_sun_conflict`)?
    fn grove_sun_conflict(&mut self, b: &Bundle) -> bool {
        let (strip, east) = STRIPS;
        let mine: Vec<Rect> = b.groves.iter().map(|g| g.0).collect();
        let (yard, beds) = (b.boxes[1], &b.boxes[2..2 + b.gardens.len()]);
        let r = strip.max(east);
        let near = self.standing.meeting(
            (b.bbox.0 - b.bbox.2 / 2.0 - r, b.bbox.1 - b.bbox.3 / 2.0 - r),
            (b.bbox.0 + b.bbox.2 / 2.0 + r, b.bbox.1 + b.bbox.3 / 2.0 + r),
            &mut self.tests,
        );
        near.into_iter().any(|k| {
            let p = &self.standing.all[k];
            mine.iter()
                .any(|&g| yard_shaded(g, p.yard) || p.beds.iter().any(|&d| bed_shaded(g, d)))
                || p.groves
                    .iter()
                    .any(|&g| yard_shaded(g, yard) || beds.iter().any(|&d| bed_shaded(g, d)))
        })
    }

    /// Does a fixture of `b` but its persimmon, as recorded, stand in one of its own farm's bands (`fit._fixtures_in_bands`)? Python
    /// asks a neighbor's bands too - and the persimmon of them alone - from the homesteads whose boxes meet this one's; but it asks
    /// after the side fit has refused every box within 2 ft of a standing one, and a farm's bands lie inside its box, so no
    /// neighbor's band can meet a fixture here: that half never refuses, and is not ported.
    fn fixtures_in_bands(b: &Bundle) -> bool {
        let first = 2 + b.gardens.len();
        let turn = round1(b.turn);
        let own: Vec<Rect> = b
            .groves
            .iter()
            .map(|g| (round1(g.0 .0), round1(g.0 .1), g.0 .2, g.0 .3))
            .collect();
        b.fixtures
            .iter()
            .zip(&b.boxes[first..])
            .any(|(&(k, f), _)| {
                let r = super::bearing::turned_box(
                    (round1(f.0), round1(f.1), round1(f.2), round1(f.3)),
                    turn,
                );
                k != Kind::Persimmon && own.iter().any(|&g| meet(r, g))
            })
    }

    /// The fit test's grove half (`fit._bundle_fits` on a grove farm): every part and band on free ground, the house's wall off the
    /// paddy, its eaves off its neighbors' and within a way's reach, the sun both ways, the bands' sun preferences, the box on the canvas
    /// and clear of every placed box, a neighbor's persimmon out of its sun (its own dropped), no fixture in a band, the registry.
    fn grove_fits(&mut self, gs: &GroveSite, b: &mut Bundle) -> bool {
        let site = gs.site;
        let rules = site.rules;
        let mut solid = vec![b.boxes[0], b.boxes[1]];
        solid.extend(b.well.map(|w| super::bearing::turned_box(w, b.turn)));
        solid.extend(b.groves.iter().map(|g| g.0));
        solid.extend(&b.boxes[2..2 + b.gardens.len()]);
        let (inset, bb) = (6.0, b.bbox);
        let off_canvas = bb.0 - bb.2 / 2.0 < inset
            || bb.1 - bb.3 / 2.0 < inset
            || bb.0 + bb.2 / 2.0 > site.canvas.0 - inset
            || bb.1 + bb.3 / 2.0 > site.canvas.1 - inset;
        // ...a layout whose lot found no seat for a part is not the household's; the rest refuse in the order Python asks them
        if b.unlaid.is_some()
            || off_canvas
            || solid.iter().any(|&r| self.refused(site, r))
            || self.lapped(site, bb)
            || {
                let t = &mut self.tests;
                wall_on_the_bund(b, rules, t)
                    || too_near(b.house, b.turn, &self.standing, t)
                    || unreachable((b.house.0, b.house.1), rules, t)
                    || persimmon_conflict(b, &self.standing, rules, t)
                    || !sun_ok(b, &self.standing, t)
            }
        {
            return false;
        }
        !self.grove_sun_conflict(b)
            && !Self::fixtures_in_bands(b)
            && admitted(b, rules, &mut self.tests)
            && !on_the_streets(b, gs.streets, &mut self.tests)
            && !self.on_a_holding(&solid)
    }

    /// Slide the farm at `c` toward `target` 2 ft a step as far as it still fits; where it stops.
    fn slide(
        &mut self,
        gs: &GroveSite,
        lot: &Lot,
        seat: Pt,
        mut c: Pt,
        target: &dyn Fn(&Self, Pt) -> Option<Pt>,
    ) -> Pt {
        for _ in 0..48 {
            self.tests.add("candidate@slide", 1);
            // ...stopped with no target, or within a foot and a half of it
            let Some(tg) = target(self, c).filter(|&tg| dist(c, tg) >= 1.5) else {
                break;
            };
            let d = dist(c, tg);
            let n = (c.0 + (tg.0 - c.0) / d * 2.0, c.1 + (tg.1 - c.1) / d * 2.0);
            // ...stopped at the first step refused, before its homestead is laid or by its fit
            if self.grove_seat_refused(gs, lot, n) || {
                let mut b = self.lay_grove(gs, lot, seat, n);
                !self.grove_fits(gs, &mut b)
            } {
                break;
            }
            c = n;
        }
        c
    }

    /// The grove farm of `lot` offered the seat (x, y) (`place._place_bundle_dispersed`): the nearest offset on a spiral that fits, then
    /// slid against the field and then its nearest neighbor - unless the seat is exact (a row's) - and laid there; None where none fits.
    pub fn place_grove(
        &mut self,
        gs: &GroveSite,
        lot: &Lot,
        x: f64,
        y: f64,
        exact: bool,
    ) -> Option<Bundle> {
        let mut offsets = vec![(0.0, 0.0)];
        let last = if exact { 14 } else { 91 };
        for r in (7..=last).step_by(7) {
            for k in 0..12 {
                let a = f64::from(k) * std::f64::consts::PI / 6.0;
                offsets.push((
                    (f64::from(r) * a.cos()).round_ties_even(),
                    (f64::from(r) * a.sin()).round_ties_even(),
                ));
            }
        }
        let seat = (x, y);
        for (nx, ny) in offsets {
            self.tests.add("candidate@place_grove", 1);
            let q = (x + nx, y + ny);
            if self.grove_seat_refused(gs, lot, q) {
                continue;
            }
            let mut b = self.lay_grove(gs, lot, seat, q);
            if !self.grove_fits(gs, &mut b) {
                continue;
            }
            let mut c = q;
            if !exact {
                c = self.slide(gs, lot, seat, c, &|_, p| nearest_on(p, gs.paddies));
                c = self.slide(gs, lot, seat, c, &|st, p| st.nearest_placed(gs.site, p));
            }
            let mut b = self.lay_grove(gs, lot, seat, c);
            self.grove_fits(gs, &mut b);
            return Some(b);
        }
        None
    }

    /// The center of the nearest placed box - a standing homestead's or one placed before the houses.
    fn nearest_placed(&self, site: &Site, p: Pt) -> Option<Pt> {
        self.standing
            .all
            .iter()
            .map(|s| (s.bbox.0, s.bbox.1))
            .chain(site.rules.placed.iter().map(|b| (b.0, b.1)))
            .min_by(|a, b| dist(p, *a).total_cmp(&dist(p, *b)))
    }

    /// Does a solid part stand on a row village's holding already reserved (`s.block_polys`)?
    fn on_a_holding(&mut self, solid: &[Rect]) -> bool {
        self.tests.add(
            "seg_test@on_a_holding",
            (solid.len() * self.holdings.len()) as u64,
        );
        let holdings = &self.holdings;
        let tests = &mut self.tests;
        holdings.iter().any(|q| {
            solid
                .iter()
                .any(|&r| super::rows::polys_meet(&super::track_out::box_poly(r), q, tests))
        })
    }

    /// Offer the seat (x, y) to the next household as a grove farm; true where it is seated.
    pub fn offer_grove(&mut self, gs: &GroveSite, x: f64, y: f64) -> bool {
        self.offer_grove_as(gs, x, y, false)
    }

    /// Would the `k`-th lot's grove farm be admitted at (x, y) - every rule `offer_grove_as` asks, asked, and nothing stood (a
    /// row's room counted before any farm is seated, feature 444 T31: S4, every rule asked of a candidate before it is placed)?
    pub fn admits_grove_as(&mut self, gs: &GroveSite, k: usize, x: f64, y: f64) -> bool {
        let lot = gs
            .site
            .lots
            .lot(k)
            .map(|(house, _kura, _beast, fixtures)| Lot {
                house,
                kura: false,
                byre: None,
                fixtures,
            });
        lot.and_then(|lot| self.place_grove(gs, &lot, x, y, true))
            .is_some()
    }

    /// Offer the seat (x, y) to the next household as a grove farm, `exact` for a row's (nudged, never slid); true where it is seated.
    pub fn offer_grove_as(&mut self, gs: &GroveSite, x: f64, y: f64, exact: bool) -> bool {
        self.search.0 += 1;
        // ...none once the lots are spent
        let lot = gs
            .site
            .lots
            .lot(self.seated.len())
            .map(|(house, _kura, _beast, fixtures)| Lot {
                house,
                kura: false,
                byre: None,
                fixtures,
            });
        let Some(b) = lot.and_then(|lot| self.place_grove(gs, &lot, x, y, exact)) else {
            return false;
        };
        self.stand_grove((x, y), b);
        true
    }
}

/// Does a part of `b` the reserved tread keeps clear - its house, yard, beds, held fixtures and well (the corridor rule's
/// built and worked ground; its bands are not) - stand within the tread's half-width of a planned street (`reserved.conflicts`)?
fn on_the_streets(b: &Bundle, (streets, half): (&[(Pt, Pt)], f64), tests: &mut Counts) -> bool {
    if streets.is_empty() {
        return false;
    }
    let turned = |r: Rect| super::fit::corners(r, b.turn).to_vec();
    let mut parts = vec![turned(b.house), turned(b.yard)];
    // (a grove farm's lot lays neither a kura nor a byre: `offer_grove_as`)
    parts.extend(b.gardens.iter().map(|&g| turned(g)));
    parts.extend(
        b.well
            .map(|w| super::fit::corners(super::bearing::turned_box(w, b.turn), 0.0).to_vec()),
    );
    let first = 2 + b.gardens.len();
    parts.extend(
        b.fixtures
            .iter()
            .zip(&b.boxes[first..])
            .filter(|(&(k, _), _)| super::fit_rules::held_key(k).is_some())
            .map(|(_, &bx)| super::fit::corners(bx, 0.0).to_vec()),
    );
    tests.add(
        "seg_test@on_the_streets",
        (parts.len() * streets.len()) as u64,
    );
    parts.iter().any(|q| {
        streets.iter().any(|&(a, c)| {
            crate::ways::track::in_poly(a, q)
                || (0..q.len())
                    .any(|m| crate::seat::exit::seg_seg(q[m], q[(m + 1) % q.len()], a, c) < half)
        })
    })
}

/// Does the band `g` stand in the yard `y`'s drying strip, the `STRIPS` depth south of it across its width (`fit._yard_sun_conflict`)?
#[must_use]
pub fn yard_shaded(g: Rect, y: Rect) -> bool {
    let strip = STRIPS.0;
    (g.0 - y.0).abs() < (g.2 + y.2) / 2.0
        && (g.1 - (y.1 + y.3 / 2.0 + strip / 2.0)).abs() < (g.3 + strip) / 2.0
}

/// Does the band `g` stand hard against the bed `d`'s east across its height, within the bed's morning reach (`fit._garden_sun_conflict`)?
#[must_use]
pub fn bed_shaded(g: Rect, d: Rect) -> bool {
    let (gx1, west) = (d.0 + d.2 / 2.0, g.0 - g.2 / 2.0);
    let across = g.1 - g.3 / 2.0 < d.1 + d.3 / 2.0 && d.1 - d.3 / 2.0 < g.1 + g.3 / 2.0;
    gx1 - 2.0 <= west && west < gx1 + STRIPS.1 && across
}

/// The nearest point on any of the outlines to `p` (`place._nearest_field_point`).
#[must_use]
pub fn nearest_on(p: Pt, rings: &[Vec<Pt>]) -> Option<Pt> {
    rings
        .iter()
        .flat_map(|r| (0..r.len()).map(move |i| (r[i], r[(i + 1) % r.len()])))
        .map(|(a, b)| {
            let (dx, dy) = (b.0 - a.0, b.1 - a.1);
            let l2 = dx * dx + dy * dy;
            let t = if l2 == 0.0 {
                0.0
            } else {
                (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / l2).clamp(0.0, 1.0)
            };
            (a.0 + t * dx, a.1 + t * dy)
        })
        .min_by(|a, b| dist(p, *a).total_cmp(&dist(p, *b)))
}

/// The front row's seats and their chords' outward normals, offset from the chains by the house's reach toward its chord and the
/// wall's gap, sampled every `pitch` along them within `reach` of the anchor along the band, at most 64, center-out
/// (`seats._front_row_from_chains`).
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "at most 64 of a few hundred samples"
)]
pub fn front_row(
    chains: &[Vec<Chord>],
    axes: &Axes,
    envelope: (f64, f64, f64, f64),
    pitch: f64,
    reach: f64,
) -> Vec<(Pt, Pt)> {
    let (left, top, right, bottom) = envelope;
    let mut out = Vec::new();
    for chain in chains {
        let mut carry = 0.0;
        for &(a, b, n) in chain {
            let seg = dist(a, b);
            if seg <= 1e-9 {
                continue;
            }
            let (dx, dy) = (-n.0, -n.1);
            let along = dx.abs() * if dx > 0.0 { right } else { -left }
                + dy.abs() * if dy > 0.0 { bottom } else { -top };
            let off = 6.0 + 1.0 + SEAT.1 + along;
            let mut t = carry;
            while t <= seg {
                let p = (a.0 + (b.0 - a.0) * t / seg, a.1 + (b.1 - a.1) * t / seg);
                if ((p.0 - axes.anchor.0) * axes.along.0 + (p.1 - axes.anchor.1) * axes.along.1)
                    .abs()
                    <= reach
                {
                    out.push(((p.0 + n.0 * off, p.1 + n.1 * off), n));
                }
                t += pitch;
            }
            carry = t - seg;
        }
    }
    if out.len() > 64 {
        let step = out.len() as f64 / 64.0;
        out = (0..64)
            .map(|i| out[(f64::from(i) * step) as usize])
            .collect();
    }
    out.sort_by(|p, q| dist(p.0, axes.c).total_cmp(&dist(q.0, axes.c)));
    out
}

/// How far a core box (left, top, right, bottom about the house center) reaches along `toward` once turned by `rot`.
#[must_use]
pub fn turned_reach(core: (f64, f64, f64, f64), rot: f64, toward: Pt) -> f64 {
    let (l, t, r, b) = core;
    let (s, c) = rot.to_radians().sin_cos();
    [(l, t), (r, t), (r, b), (l, b)]
        .iter()
        .map(|&(x, y)| (x * c - y * s) * toward.0 + (x * s + y * c) * toward.1)
        .fold(f64::NEG_INFINITY, f64::max)
}

/// How far a box must move along `n` so that no water course lies within its clearance of the box (`seat_geometry.water_push`).
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a course's samples every 8 ft"
)]
pub fn water_push(
    water: &[(Pt, Pt, f64)],
    center: Pt,
    n: Pt,
    half_lat: f64,
    near: f64,
    far: f64,
) -> f64 {
    let (lx, ly) = (-n.1, n.0);
    let mut push: f64 = 0.0;
    for &(a, b, clr) in water {
        if seg_dist(center, a, b) > half_lat + (far - near) + clr {
            continue;
        }
        let k = ((dist(a, b) / 8.0) as usize).max(1);
        for j in 0..=k {
            let (x, y) = (
                a.0 + (b.0 - a.0) * j as f64 / k as f64,
                a.1 + (b.1 - a.1) * j as f64 / k as f64,
            );
            if ((x - center.0) * lx + (y - center.1) * ly).abs() <= half_lat + clr {
                let d = x * n.0 + y * n.1;
                if near - clr <= d && d <= far + clr {
                    push = push.max(d + clr - near);
                }
            }
        }
    }
    push
}

/// The seat moved once along `n` by the other ground's reach past the homestead's near edge, and whether the water moved it - unmoved
/// where the homestead's box is clear (`stages._ground_push`).
#[must_use]
pub fn ground_push(
    seat: Pt,
    n: Pt,
    bx: Rect,
    corridors: &Corridors,
    tests: &mut Counts,
) -> (Pt, bool) {
    let pts: Vec<Pt> = [-1.0, 0.0, 1.0]
        .iter()
        .flat_map(|&dx| [-1.0, 0.0, 1.0].map(|dy| (bx.0 + dx * bx.2 / 2.0, bx.1 + dy * bx.3 / 2.0)))
        .collect();
    if !corridors.hit_points(&pts, tests) {
        return (seat, false);
    }
    let (lx, ly) = (-n.1, n.0);
    let half_lat = lx.abs() * bx.2 / 2.0 + ly.abs() * bx.3 / 2.0;
    let near = bx.0 * n.0 + bx.1 * n.1 - (n.0.abs() * bx.2 / 2.0 + n.1.abs() * bx.3 / 2.0);
    let far = near + (n.0.abs() * bx.2 + n.1.abs() * bx.3);
    let mut push: f64 = 0.0;
    for &(x, y) in corridors.rings.iter().flatten() {
        if ((x - bx.0) * lx + (y - bx.1) * ly).abs() <= half_lat {
            let d = x * n.0 + y * n.1;
            if near <= d && d <= far {
                push = push.max(d - near);
            }
        }
    }
    let wet = water_push(&corridors.water, (bx.0, bx.1), n, half_lat, near, far);
    let by_water = wet > push;
    push = push.max(wet);
    if push <= 0.0 {
        return (seat, false);
    }
    push += SEAT.3;
    ((seat.0 + n.0 * push, seat.1 + n.1 * push), by_water)
}

/// `n` seeds of a cluster of `shape` about the origin, `ex` and `ey` its half-extents, drawn from `rng` (`houses.cluster_seeds`).
#[must_use]
pub fn cluster_seeds(shape: &str, ex: f64, ey: f64, n: usize, rng: &mut PyRandom) -> Vec<Pt> {
    let uniform = |a: f64, b: f64, rng: &mut PyRandom| a + (b - a) * rng.random();
    (0..n)
        .map(|_| {
            let a = uniform(0.0, std::f64::consts::TAU, rng);
            let r = rng.random().sqrt();
            match shape {
                "round" => (a.cos() * r * ex, a.sin() * r * ey),
                "elongated" => (a.cos() * r * ex * 0.55, a.sin() * r * ey * 1.4),
                "crescent" => {
                    let t = uniform(-1.0, 1.0, rng);
                    let depth = rng.random().sqrt();
                    (
                        t * ex * 0.5 + a.cos() * ex * 0.22 * depth,
                        (t * t - 0.5) * ey * 0.5 + a.sin() * ey * 0.95 * depth,
                    )
                }
                _ => {
                    let side = if rng.random() < 0.5 { -1.0 } else { 1.0 };
                    (
                        side * ex * 0.62 + a.cos() * r * ex * 0.42,
                        a.sin() * r * ey * 0.82,
                    )
                }
            }
        })
        .collect()
}

/// The drawn aspect band of a cluster's shape (`consts.CLUSTER_DRAWN_ASPECT`).
///
/// Research:
///     the drawn aspect - GUESS: searched, the record silent (feature 417 T38, 2026-10-25); round 1.0-2.0, crescent and split 1.9-4.2, elongated 2.8-12.0
#[must_use]
pub fn drawn_aspect(shape: &str) -> (f64, f64) {
    match shape {
        "round" => (1.0, 2.0),
        "elongated" => (2.8, 12.0),
        _ => (1.9, 4.2),
    }
}

/// How far the front row wraps along the field, as a multiple of the band's half-length (`consts.CLUSTER_ROW_SPAN`).
///
/// Research:
///     the front row's wrap - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); round 1.2, crescent and split 1.6, elongated 2.6
#[must_use]
pub fn row_span(shape: &str) -> f64 {
    match shape {
        "round" => 1.2,
        "elongated" => 2.6,
        _ => 1.6,
    }
}
