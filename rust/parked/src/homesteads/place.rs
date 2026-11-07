//! Seating a nucleated cluster (feature 444 T30): the first house on the free ground nearest the seat's center, each next house
//! offered from a standing one at the distance their footprints part, ring by ring, jittered by the standing house's position,
//! wider rings while households are left; each offer laid on its four garden sides and judged - the house's box, the union of the
//! sides, each side's own box with at most one computed move off a single neighbor, the parts' rules - and the first side by its rank
//! kept. Every household is seated or the seating stops short; no house is taken back. The GM, 2026-10-02 (feature 308): "once you've
//! placed the first house, you should notionally be able to compute the minimum distance needed to seat a second house, then place
//! it in a direction, then repeat, with a little randomized jitter to the distance and direction so that it's not jhusgt [just] an
//! unrealistic grid" - and "keep in mind the sunlight / shade requirements when computing minimum distance".
//!
//! Research:
//!     the grown irregular cluster - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the cluster grown from its first house
//!     nearest the seat first, the field a tie-break - CANON: the GM's ruling of 2026-10-03, all else being equal; the ring a GUESS
//!     no house refused for its distance from the fields - research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html
//!     the exhaustive seat order - research/questions/0029-farmhouses-minka.drawing.html: every legal grid point on the canvas, nearest the seat first
#![expect(
    clippy::manual_midpoint,
    reason = "two half-sizes summed at a map's few hundred feet, where no overflow is possible"
)]

use super::Counts;
use std::collections::{BinaryHeap, HashSet};

use super::bearing::{house_rot, turned_box, Margin};
use super::bundle::{bundle, Bundle, Lot, Sun};
use super::fit::{
    across_a_stream, on_free_ground, opens, sun_ok, too_near, Placed, Standing, SUN_FT,
};
use super::fixtures::{Forms, Kind};
use super::ground::{Ground, Reach};
use super::layout::{hjit, Rect, Side, SIDES};
use super::lots::Lots;
use super::passage::{passage_of, yard_side, Passage, Tight, TIGHT};
use crate::field::fan::Pt;
use crate::field::geom::seg_dist;

/// The growth's levels: the directions offered round each standing house, and the rings out (in footprints) at each.
///
/// Research:
///     growth levels - GUESS: no source could speak to it, a value of ours; 8, 12 and 16 directions on rings of 1 to 2 footprints, then 16 on one ring widening by half a footprint
pub const LEVELS: [(u32, &[f64]); 3] = [(8, &[1.0]), (12, &[1.0, 1.5]), (16, &[1.25, 1.75, 2.0])];

/// The direction jitter at eight directions (degrees, scaled with the step) and the distance jitter (a share).
///
/// Research:
///     direction jitter - GUESS: scaled with the step, so neighboring directions never cross; 12 degrees at eight
///     distance jitter - GUESS: no source could speak to it, a value of ours; up to 12% further
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 300 (direction salt); 400 (distance salt); 12 (side-hand salt)
pub const JITTER: (f64, f64) = (12.0, 0.12);

/// The ring the growth's queue orders its offers by (feet).
///
/// Research:
///     the queue's ring - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 20 ft
pub const TIE_RING_FT: f64 = 20.0;

/// A reserved wood seat's clump, by which a standing homestead's footprint reaches past the seat (feet).
///
/// Research:
///     the household's wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: its reserved copse seats inside its footprint, beside its house, so no lane comes between them - in every account found the way runs outside the grove or through a gap in it to the house - 12 (`growth.py` `WOOD_CLUMP_PX`)
pub const WOOD_CLUMP_FT: f64 = 12.0;

/// The narrowest gap a way takes between two homesteads, and the parting the growth adds (feet).
///
/// Research:
///     the gap a way threads - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 18 ft between two homesteads, so a way can always be laid between them
///     the parting - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the 2 ft the cluster's growth leaves between neighbors
pub const GAP_FT: (f64, f64) = (18.0, 2.0);

/// The moves a settled seat makes while its household's envelope outgrows the one it was offered for.
///
/// Research:
///     its search steps and tolerances - NONE: a search's breadth, deciding nothing about the place - 4 moves
pub const SETTLE_TRIES: usize = 4;

/// The first house's seat grid (feet: a third of the bundle's 100 ft pitch), the sheet's inset, and the offers in a row that may
/// seat none before the first house's search ends.
///
/// Research:
///     about as near - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); one grid pitch
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (seat grid inset 6 px from the sheet edge)
///     its search steps and tolerances - NONE: a search's breadth - 400 offers
pub const FIRST: (f64, f64, usize) = (100.0 / 3.0, 6.0, 400);

/// A homestead's reach from its house's center: west, east, north and south (feet).
pub type Footprint = (f64, f64, f64, f64);

/// The reach of a box from a center.
#[must_use]
pub fn box_reach(c: Pt, b: Rect) -> Footprint {
    (
        c.0 - (b.0 - b.2 / 2.0),
        (b.0 + b.2 / 2.0) - c.0,
        c.1 - (b.1 - b.3 / 2.0),
        (b.1 + b.3 / 2.0) - c.1,
    )
}

/// The union of two reaches.
#[must_use]
pub fn union(a: Footprint, b: Footprint) -> Footprint {
    (a.0.max(b.0), a.1.max(b.1), a.2.max(b.2), a.3.max(b.3))
}

/// Where a homestead of reach `new` stands from one of reach `standing` at `center`, along `angle`, the two parting by `gap` on
/// the axis that parts them first.
#[must_use]
pub fn seat_toward(center: Pt, standing: Footprint, new: Footprint, angle: f64, gap: f64) -> Pt {
    let (dx, dy) = (angle.cos(), angle.sin());
    let need_x = if dx > 0.0 {
        standing.1 + new.0
    } else {
        standing.0 + new.1
    };
    let need_y = if dy > 0.0 {
        standing.3 + new.2
    } else {
        standing.2 + new.3
    };
    let tx = if dx.abs() > 1e-9 {
        (need_x + gap) / dx.abs()
    } else {
        f64::INFINITY
    };
    let ty = if dy.abs() > 1e-9 {
        (need_y + gap) / dy.abs()
    } else {
        f64::INFINITY
    };
    let t = tx.min(ty);
    (center.0 + dx * t, center.1 + dy * t)
}

/// Does a box keep `gap` from the standing homestead's reach about `center`, on one axis at least?
#[must_use]
pub fn keeps_its_distance(b: Rect, center: Pt, standing: Footprint, gap: f64) -> bool {
    let apart_x = ((b.0 - b.2 / 2.0) - (center.0 + standing.1))
        .max((center.0 - standing.0) - (b.0 + b.2 / 2.0));
    let apart_y = ((b.1 - b.3 / 2.0) - (center.1 + standing.3))
        .max((center.1 - standing.2) - (b.1 + b.3 / 2.0));
    apart_x.max(apart_y) >= gap - 1e-9
}

/// The distance a moved seat must still keep: from the standing homestead it was offered from by the parting, and from every other
/// by the threading gap - the one a tight seat stands against by the tight parting alone; and the tight seat's context.
pub struct Keep {
    /// The center and reach of the homestead it was offered from.
    pub from: (Pt, Footprint),
    /// The parting kept from it.
    pub gap: f64,
    /// Every standing homestead's center and reach.
    pub standing: Vec<(Pt, Footprint)>,
    /// The gap kept from every other.
    pub others: f64,
    /// The tight seat it is, where it is one.
    pub tight: Option<Tight>,
}

impl Keep {
    /// Does the box `b` keep its distance?
    #[must_use]
    pub fn holds(&self, b: Rect) -> bool {
        keeps_its_distance(b, self.from.0, self.from.1, self.gap)
            && self.standing.iter().enumerate().all(|(k, &(c, r))| {
                let g = if self.tight.is_some_and(|t| t.nb == k) {
                    TIGHT.0
                } else {
                    self.others
                };
                keeps_its_distance(b, c, r, g)
            })
    }
}

/// What the seating reads: the free ground and its reach, the field's outline the queue's tie-break measures, the streams, the
/// canvas, the margin the houses turn with and the common bearing, the lots and the forms, the sun rule's reach.
pub struct Site<'a> {
    /// The free ground's raster over the seating's window.
    pub ground: &'a Ground,
    /// Whether a point past the window is taken.
    pub beyond: &'a dyn Fn(Pt) -> bool,
    /// The reach of the way out.
    pub reach: &'a Reach,
    /// The field's outline.
    pub field: &'a [Pt],
    /// The streams' segments.
    pub streams: &'a [(Pt, Pt)],
    /// The canvas (feet).
    pub canvas: Pt,
    /// The field margin's bend, and the common bearing (degrees).
    pub bearing: (&'a Margin, f64),
    /// The households' lots.
    pub lots: &'a Lots,
    /// The byre form a keeper's stall takes, where the byres are the households' own.
    pub byre: Option<super::layout::Byre>,
    /// The hamlet's fixture forms.
    pub forms: &'a Forms,
    /// The persimmon's reach off the plots' sun.
    pub shade: f64,
    /// What the rules read past the raster.
    pub rules: &'a super::fit_rules::Rules,
}

/// A household seated: its lot's ordinal, the seat it was offered and its homestead.
#[derive(Debug)]
pub struct Seated {
    /// The lot it took.
    pub lot: usize,
    /// The seat its rolls are keyed on.
    pub seat: Pt,
    /// Its homestead.
    pub bundle: Bundle,
    /// Its share of the homestead wood: the seats it reserved.
    pub wood: Vec<Pt>,
    /// Its passage across a neighbor's yard, where it is reached by one.
    pub passage: Option<Passage>,
}

/// A seat placed: where its house stands, its homestead, its wood's seats, its copse keep-outs and its passage.
type Placement = (Pt, Bundle, Vec<Pt>, super::wood::Keepouts, Option<Passage>);

/// How a box stands against the ground and the standing homesteads.
#[derive(Clone, Copy, PartialEq)]
enum Block {
    /// Clear.
    Clear,
    /// Refused outright: off the canvas, on taken ground, or over two homesteads.
    Refused,
    /// Over exactly one standing homestead's box.
    One(Rect),
}

/// The seating's state: what stands, and what each search counted.
#[derive(Default)]
pub struct Seating {
    /// The homesteads standing, filed for the rules.
    pub standing: Standing,
    /// The households seated, in order.
    pub seated: Vec<Seated>,
    /// The offers, the positions, the rectangles and the part layouts tried.
    pub search: (u64, u64, u64, u64),
    /// The operations counted.
    pub tests: Counts,
    /// The households' wood reservations.
    pub wood: super::wood::Shares,
    /// The wood seats reserved so far.
    pub seats: Vec<Pt>,
    /// How many passages lie between each seated household and a way of its own.
    pub depth: Vec<Option<u32>>,
    /// The passages' walks, kept clear of every later homestead.
    pub walks: super::access::AccessTree,
    /// The passages the settlement's share has left.
    pub passage_left: usize,
    /// A row village's holdings reserved so far, which no later part stands on.
    pub holdings: Vec<Vec<Pt>>,
    /// The streams filed once a seating, for the layouts' stream test (`parts_refused`).
    pub streams: Option<crate::field::index::Index>,
}

impl Seating {
    fn lot(&self, site: &Site) -> Option<Lot> {
        let (house, kura, beast, fixtures) = site.lots.lot(self.seated.len())?;
        Some(Lot {
            house,
            kura,
            byre: if beast { site.byre } else { None },
            fixtures,
        })
    }

    fn turn(site: &Site, p: Pt, tests: &mut Counts) -> f64 {
        house_rot(p, site.bearing.1, site.bearing.0.follow(p, tests))
    }

    fn lay(&mut self, site: &Site, lot: &Lot, rolls_at: Pt, garden: Side, at: Pt) -> Bundle {
        let turn = Self::turn(site, at, &mut self.tests);
        let sun = Sun {
            shade: site.shade,
            turns: &[turn],
        };
        bundle(
            lot,
            rolls_at,
            garden,
            at,
            turn,
            site.forms,
            &sun,
            &mut self.tests,
        )
    }

    /// What a walk keeps off besides the two households' parts, at the tight seat against `nb`: every other homestead's box and the
    /// boxes placed before the houses, the taken ground and the reserved wood.
    fn walls<'s>(&'s self, site: &'s Site, nb: usize) -> super::passage::Walls<'s> {
        let boxes = (0..self.standing.all.len())
            .filter(|&k| k != nb)
            .map(|k| self.standing.all[k].bbox)
            .chain(site.rules.placed.iter().copied())
            .collect();
        super::passage::Walls {
            boxes,
            ground: site.ground,
            beyond: site.beyond,
            wood: &self.wood,
            lane_gap: site.rules.lane_gap,
        }
    }

    /// The passage the layout `b` at the tight seat `t` is reached by, or None (`passage.passage_of`).
    fn passage_for(
        &self,
        site: &Site,
        b: &Bundle,
        t: &Tight,
        tests: &mut Counts,
    ) -> Option<Passage> {
        let walls = self.walls(site, t.nb);
        passage_of(
            b,
            &self.seated[t.nb].bundle,
            self.depth[t.nb],
            t,
            &walls,
            tests,
        )
    }

    /// Is the household at the tight seat `t` on land the custom covers - some laid side with a walk to the neighbor's yard and none
    /// with a way of its own (`passage.landlocked`)?
    fn landlocked(
        &mut self,
        site: &Site,
        sides: &[Bundle],
        t: &Tight,
        reach: &super::ground::Reach,
    ) -> bool {
        let lays: Vec<&Bundle> = sides.iter().filter(|b| b.unlaid.is_none()).collect();
        let mut local = Counts::default();
        let got = !lays.iter().any(|b| opens(b, reach, &mut local))
            && lays
                .iter()
                .any(|b| self.passage_for(site, b, t, &mut local).is_some());
        for (k, v) in local.0 {
            self.tests.add(&k, v);
        }
        got
    }

    /// Does a rule of the parts refuse the layout `b` - a neighbor's persimmon in its sun (its own dropped), the sun both ways, the
    /// taken ground, the stream, the paddy's chords, the water, the registry, a neighbor's eaves or the ground no way reaches?
    fn parts_refused(&mut self, site: &Site, b: &mut Bundle) -> bool {
        let rules = site.rules;
        // the streams near the layout's box, from the index filed once a seating: a stream crossing the line from the house to a
        // part, or running through a part, lies in the box round them all (every stream asked of every layout was the stage's
        // costliest test after the reach - 12 million at 40, the work-budget run of 2026-11-05)
        let idx = self.streams.get_or_insert_with(|| {
            let mut i = crate::field::index::Index::default();
            for &(a, c) in site.streams {
                i.file_w(a, c, 0.0);
            }
            i
        });
        let bb = b.bbox;
        let (before, seen) = (idx.touched, idx.examined);
        let near: Vec<(Pt, Pt)> = idx
            .near(
                (bb.0 - bb.2 / 2.0, bb.1 - bb.3 / 2.0),
                (bb.0 + bb.2 / 2.0, bb.1 + bb.3 / 2.0),
            )
            .into_iter()
            .map(|k| idx.segs[k])
            .collect();
        self.tests.add("index_query@streams", idx.touched - before);
        self.tests
            .add("index_examined@streams", idx.examined - seen);
        let t = &mut self.tests;
        super::fit_rules::persimmon_conflict(b, &self.standing, rules, t)
            || !sun_ok(b, &self.standing, t)
            || !on_free_ground(b, site.ground, site.beyond, t)
            || across_a_stream(b, &near, t)
            || super::fit_rules::wall_on_the_bund(b, rules, t)
            || super::fit_rules::beds_on_water(b, rules, t)
            || !super::fit_rules::admitted(b, rules, t)
            || too_near(b.house, b.turn, &self.standing, t)
            || super::fit_rules::unreachable((b.house.0, b.house.1), rules, t)
    }

    /// A layout moved at the tight seat `t`, asked for its passage: none once a layout here had a way of its own (`own_way`), none
    /// with no walk to the neighbor's yard, none - and `own_way` set - where its yard opens onto lane ground (`fit._parts_fit`).
    fn tight_passage(
        &mut self,
        site: &Site,
        b: &Bundle,
        t: &Tight,
        reach: &super::ground::Reach,
        own_way: &mut bool,
    ) -> Option<Passage> {
        let mut local = Counts::default();
        let got = (!*own_way)
            .then(|| self.passage_for(site, b, t, &mut local))
            .flatten();
        for (k, v) in local.0 {
            self.tests.add(&k, v);
        }
        let got = got?;
        *own_way = opens(b, reach, &mut self.tests);
        (!*own_way).then_some(got)
    }

    /// The wood seats the layout `b` would reserve among its keep-outs `own` (`wood.rs` `Shares::share`), or None.
    fn wood_share(
        &mut self,
        site: &Site,
        b: &Bundle,
        own: &super::wood::Keepouts,
    ) -> Option<Vec<Pt>> {
        let wsite = super::wood::WoodSite {
            ground: site.ground,
            streams: site.streams,
            canvas: site.canvas,
        };
        self.wood
            .share((b.house.0, b.house.1), b.turn, own, &wsite, &mut self.tests)
    }

    /// May a passage cross to the seated household `k` - reached within the chain?
    fn crossable(&self, k: usize) -> bool {
        self.depth[k].is_some_and(|d| d < super::passage::PASSAGE.1)
    }

    /// The envelope the household of `lot` lays at `q`, its rake the seat's.
    fn envelope_at(&mut self, site: &Site, lot: &Lot, q: Pt) -> Rect {
        let turn = Self::turn(site, q, &mut self.tests);
        super::bundle::envelope(
            lot,
            q,
            q,
            turn,
            site.forms,
            &Sun {
                shade: site.shade,
                turns: &[turn],
            },
            &mut self.tests,
        )
    }

    /// How a box stands: clear, refused by the canvas, the ground or two homesteads, or over exactly one standing homestead's box.
    fn blocked(&mut self, site: &Site, b: Rect) -> Block {
        let (lo, hi) = (
            (b.0 - b.2 / 2.0, b.1 - b.3 / 2.0),
            (b.0 + b.2 / 2.0, b.1 + b.3 / 2.0),
        );
        let inset = FIRST.1;
        if lo.0 < inset
            || lo.1 < inset
            || hi.0 > site.canvas.0 - inset
            || hi.1 > site.canvas.1 - inset
        {
            return Block::Refused;
        }
        if site
            .ground
            .rect_refused(lo, hi, site.beyond, &mut self.tests)
        {
            return Block::Refused;
        }
        if self.walks.covers_box(b, &mut self.tests) {
            return Block::Refused;
        }
        let margin = GAP_FT.1;
        let near = self.standing.meeting(
            (lo.0 - margin, lo.1 - margin),
            (hi.0 + margin, hi.1 + margin),
            &mut self.tests,
        );
        // ...and the boxes placed before any house (a shared byre's pocket), met as a standing homestead's box is
        let (x0, y0, x1, y1) = (lo.0 - margin, lo.1 - margin, hi.0 + margin, hi.1 + margin);
        let early: Vec<Rect> = site
            .rules
            .placed
            .iter()
            .filter(|p| {
                p.0 + p.2 / 2.0 > x0
                    && p.0 - p.2 / 2.0 < x1
                    && p.1 + p.3 / 2.0 > y0
                    && p.1 - p.3 / 2.0 < y1
            })
            .copied()
            .collect();
        self.tests
            .add("index_query@blocked", site.rules.placed.len() as u64);
        match (near.len(), early.as_slice()) {
            (0, []) => Block::Clear,
            (1, []) => Block::One(self.standing.all[near[0]].bbox),
            (0, [p]) => Block::One(*p),
            _ => Block::Refused,
        }
    }

    /// The seat at (x, y) for the next household: its four sides laid, the union tested, each side's own box with at most one
    /// computed move off a single neighbor, the parts' rules asked, the first side by its rank kept. `keep` is the growth's distance a
    /// moved box must still keep.
    #[expect(
        clippy::cast_possible_truncation,
        reason = "a seat's position in eighths of a foot, a few hundred thousand"
    )]
    fn place(
        &mut self,
        site: &Site,
        lot: &Lot,
        x: f64,
        y: f64,
        keep: Option<&Keep>,
    ) -> Option<Placement> {
        self.search.1 += 1;
        let (hw, hh) = lot.house;
        let turn = Self::turn(site, (x, y), &mut self.tests);
        let house = turned_box((x, y, hw, hh), turn);
        if self.blocked(site, house) == Block::Refused {
            return None;
        }
        let sides: Vec<Bundle> = SIDES
            .iter()
            .map(|&side| self.lay(site, lot, (x, y), side, (x, y)))
            .collect();
        // THE REACH LABELED ONCE (the derivation's invariant: no house is painted into it while the houses are seated, 0246): flooded
        // again after every household with its reserved wood seats painted on - as the Python's seat region was - it was most of the
        // stage's counted work, the exponent near 2, and a 48-seed cohort and the Rust gate seated and failed the same seeds either way
        let reach = site.reach;
        // a tight seat is judged by its land, not one layout: taken only where some layout here has a walk to the neighbor's yard and
        // none a way of its own (`passage.landlocked`)
        let tight = keep.and_then(|k| k.tight);
        if !tight.is_none_or(|t| self.landlocked(site, &sides, &t, reach)) {
            return None;
        }
        let mut own_way = false;
        let env = super::bundle::bbox_of(&sides.iter().map(|b| b.bbox).collect::<Vec<_>>());
        self.search.2 += 1;
        let union_clear = self.blocked(site, env) == Block::Clear;
        let mut best: Option<((usize, u32), Placement)> = None;
        let mut reaches: std::collections::HashMap<(i64, i64), bool> =
            std::collections::HashMap::new();
        for (rank, (side, mut b)) in SIDES.iter().zip(sides).enumerate() {
            let (mut cx, mut cy) = (x, y);
            if b.unlaid.is_some() {
                continue;
            }
            let mut hit = Block::Clear;
            if !union_clear {
                self.search.2 += 1;
                hit = self.blocked(site, b.bbox);
            }
            if let Block::One(p) = hit {
                let env = b.bbox;
                let ox = (env.2 + p.2) / 2.0 + GAP_FT.1 - (env.0 - p.0).abs();
                let oy = (env.3 + p.3) / 2.0 + GAP_FT.1 - (env.1 - p.1).abs();
                if ox <= oy {
                    cx += if env.0 >= p.0 { ox } else { -ox };
                } else {
                    cy += if env.1 >= p.1 { oy } else { -oy };
                }
                b = self.lay(site, lot, (x, y), *side, (cx, cy));
                self.search.1 += 1;
                self.search.2 += 1;
                hit = self.blocked(site, b.bbox);
                if hit == Block::Clear && keep.is_some_and(|k| !k.holds(b.bbox)) {
                    hit = Block::Refused;
                }
            }
            if hit != Block::Clear || b.unlaid.is_some() {
                continue;
            }
            // the yard's reach, asked once a position: the seat's unmoved sides share one answer, a moved side is another seat - but a
            // side moved at a tight seat is asked for its passage instead: no way of its own, a walk to the neighbor's yard
            let asked = tight
                .filter(|_| (cx, cy) != (x, y))
                .map(|t| self.tight_passage(site, &b, &t, reach, &mut own_way));
            let tests = &mut self.tests;
            let refused = asked.as_ref().map_or_else(
                || {
                    !*reaches
                        .entry(((cx * 8.0).round() as i64, (cy * 8.0).round() as i64))
                        .or_insert_with(|| opens(&b, reach, tests))
                },
                Option::is_none,
            );
            if refused {
                continue;
            }
            let passage = asked.flatten();
            self.search.3 += 1;
            if self.parts_refused(site, &mut b) {
                continue;
            }
            // the wood, last: no part over another household's seat, and its own floor within its reach
            let own = Self::keepouts_of(&b);
            if self.wood.covers_a_seat(&own, &mut self.tests) {
                continue;
            }
            let Some(seats) = self.wood_share(site, &b, &own) else {
                continue;
            };
            let hand = u32::from(rank % 2 == 1) ^ u32::from(hjit(cx, cy, 12.0) < 0.5);
            // (a bed in a standing house's sun is refused by `sun_ok`, so no kept layout's garden is shaded: the sides are ordered by their
            // rank and their hand alone)
            let score = (rank / 2, hand);
            if best.as_ref().is_none_or(|(s, ..)| score < *s) {
                best = Some((score, ((cx, cy), b, seats, own, passage)));
            }
        }
        best.map(|(_, p)| p)
    }

    /// A homestead's copse keep-outs, from its parts as drawn: its house, kura, byre and retirement house, its yard and beds, and
    /// its well pocket (`wood_share.py` `bundle_parts`, `copse_keepouts`: of the fixtures only the retirement house is a solid).
    pub(super) fn keepouts_of(b: &Bundle) -> super::wood::Keepouts {
        let mut solids = vec![b.house];
        solids.extend(b.kura);
        solids.extend(b.byre.map(|(r, _)| r));
        solids.extend(
            b.fixtures
                .iter()
                .filter(|(k, _)| *k == Kind::Retirement)
                .map(|(_, r)| *r),
        );
        let mut plots = vec![b.yard];
        plots.extend(&b.gardens);
        let mut own = super::wood::keepouts(&solids, &plots);
        own.0
            .extend(b.well.map(|w| (w.0, w.1, super::wood::WELL_KEEPOUT_FT)));
        own
    }

    fn stand(
        &mut self,
        seat: Pt,
        b: Bundle,
        wood: Vec<Pt>,
        own: super::wood::Keepouts,
        passage: Option<Passage>,
    ) {
        self.wood.commit(&wood, own, &mut self.tests);
        // ...its passage's walk kept clear of every later homestead, counted against the share; a household reached by none has a way
        // of its own (its yard opened onto lane ground)
        if let Some(p) = &passage {
            for w in p.walk.windows(2) {
                self.walks.bar(w[0], w[1]);
            }
            self.passage_left = self.passage_left.saturating_sub(1);
        }
        self.depth
            .push(Some(passage.as_ref().map_or(0, |p| p.depth)));
        if !wood.is_empty() {
            self.seats.extend(&wood);
        }
        let placed = Placed {
            house: (b.house, b.turn),
            house_box: b.boxes[0],
            yard: b.boxes[1],
            beds: b.boxes[2..2 + b.gardens.len()].to_vec(),
            bbox: b.bbox,
            persimmon: super::fit_rules::persimmon_of(&b),
            groves: Vec::new(),
        };
        self.standing.add(placed, &mut self.tests);
        let lot = self.seated.len();
        self.seated.push(Seated {
            lot,
            seat,
            bundle: b,
            wood,
            passage,
        });
    }

    /// Offer the seat (x, y) to the next household; true where it is seated.
    pub fn offer(&mut self, site: &Site, x: f64, y: f64, keep: Option<&Keep>) -> bool {
        self.search.0 += 1;
        let Some(lot) = self.lot(site) else {
            return false;
        };
        let Some((_at, b, wood, own, passage)) = self.place(site, &lot, x, y, keep) else {
            return false;
        };
        self.stand((x, y), b, wood, own, passage);
        true
    }

    /// The footprint of a seated homestead: its box, and its yard's and beds' south sun.
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names: a reach's w, e, n and s"
    )]
    pub fn footprint(&self, k: usize) -> (Pt, Footprint) {
        let s = &self.seated[k].bundle;
        let c = (s.house.0, s.house.1);
        let (mut w, mut e, mut n, mut so) = box_reach(c, s.bbox);
        // ...its reserved wood seats inside it, each by its clump, so no lane comes between a household and its grove
        for &(x, y) in &self.seated[k].wood {
            w = w.max(c.0 - x + WOOD_CLUMP_FT);
            e = e.max(x - c.0 + WOOD_CLUMP_FT);
            n = n.max(c.1 - y + WOOD_CLUMP_FT);
            so = so.max(y - c.1 + WOOD_CLUMP_FT);
        }
        let sun = SUN_FT.0 + SUN_FT.1;
        for r in std::iter::once(s.boxes[1]).chain(s.boxes[2..2 + s.gardens.len()].iter().copied())
        {
            so = so.max(r.1 + r.3 / 2.0 - c.1 + sun);
        }
        (c, (w, e, n, so))
    }
}

/// How far `q` stands from the nearest chord of the field's facing chains (unsigned), 0 where there are none - the growth's tie-break
/// within a ring (`growth.py` `field_distance`, `chain_distance`).
#[must_use]
pub fn chain_distance(q: Pt, chains: &[Vec<super::fit_rules::Chord>]) -> f64 {
    let d = chains
        .iter()
        .flatten()
        .map(|&(a, b, _)| seg_dist(q, a, b))
        .fold(f64::INFINITY, f64::min);
    if d.is_finite() {
        d
    } else {
        0.0
    }
}

/// How far `q` stands from the field's outline - the first house's tie-break within a ring.
#[must_use]
pub fn field_distance(q: Pt, field: &[Pt]) -> f64 {
    let n = field.len();
    (0..n)
        .map(|i| seg_dist(q, field[i], field[(i + 1) % n]))
        .fold(f64::MAX, f64::min)
}

/// A queued seat's offer: the standing homestead's center and reach it was offered from, its bearing, its scale, and the neighbor
/// it is a tight seat against.
type Offer = (Pt, Footprint, f64, f64, Option<usize>);

/// An offer's place in the growth's queue: its ring, its field distance and its distance (each non-negative, so its bits order as
/// it does - Python's float key exactly), and its order queued - the least first (`Reverse`), and the offer itself by its ordinal.
type QueueKey = std::cmp::Reverse<(i64, u64, u64, usize)>;

/// Seat `want` households of a nucleated cluster about `center`: the first on the free ground nearest it, the rest grown from the
/// standing ones. Returns the seating; fewer seated than wanted where the ground is full.
#[must_use]
#[expect(
    clippy::too_many_lines,
    reason = "the growth's one loop, as the seating runs it"
)]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    clippy::cast_sign_loss,
    reason = "ring indices and grid counts of a few hundred"
)]
pub fn grow(site: &Site, center: Pt, want: usize) -> Seating {
    let mut st = Seating {
        passage_left: site.rules.passage_left,
        walks: super::access::AccessTree::new(super::access::ACCESS_HALF_FT),
        ..Seating::default()
    };
    // what the seating reserved before any house - a shared byre's pocket - filed against the wood, so no seat is reserved under it
    if !site.rules.bars.is_empty() {
        st.wood
            .commit(&[], (site.rules.bars.clone(), Vec::new()), &mut st.tests);
    }
    // the first house: the free ground's grid, nearest the seat first, the field breaking ties within a pitch
    let (pitch, inset, dry) = FIRST;
    let (ni, nj) = (
        ((site.canvas.0 - 2.0 * inset) / pitch) as usize + 1,
        ((site.canvas.1 - 2.0 * inset) / pitch) as usize + 1,
    );
    let mut grid: Vec<(i64, f64, f64, Pt)> = Vec::new();
    for i in 0..ni {
        for j in 0..nj {
            let q = (inset + i as f64 * pitch, inset + j as f64 * pitch);
            st.tests.add("candidate@grow", 1);
            if site.ground.taken_at(q).unwrap_or_else(|| (site.beyond)(q)) {
                continue;
            }
            let d = (q.0 - center.0).hypot(q.1 - center.1);
            grid.push((
                (d / pitch).round_ties_even() as i64,
                field_distance(q, site.field),
                d,
                q,
            ));
        }
    }
    grid.sort_by(|a, b| {
        a.0.cmp(&b.0)
            .then(a.1.total_cmp(&b.1))
            .then(a.2.total_cmp(&b.2))
    });
    st.tests.add("candidate@grow", grid.len() as u64 * 12);
    for (since, &(_, _, _, q)) in grid.iter().enumerate() {
        if !st.seated.is_empty() || since >= dry || want == 0 {
            break;
        }
        if !opens_at(site, q, &mut st.tests) {
            continue;
        }
        st.offer(site, q.0, q.1, None);
    }
    // the rest grown from the standing houses, ring by ring
    let gap = GAP_FT.0 + GAP_FT.1;
    let mut heap: BinaryHeap<QueueKey> = BinaryHeap::new();
    let mut offers: Vec<(Pt, Offer)> = Vec::new();
    let mut seen: HashSet<(i64, i64)> = HashSet::new();
    let mut tight_q: HashSet<usize> = HashSet::new();
    let (mut level, mut done) = (0usize, 0usize);
    // the next household's reach rolled at the first house - the guess every queued seat is parted by, and the settle's start
    let guess = match (st.seated.first(), st.lot(site)) {
        (Some(h0), Some(lot)) => {
            let at = (h0.bundle.house.0, h0.bundle.house.1);
            box_reach(at, st.envelope_at(site, &lot, at))
        }
        _ => (0.0, 0.0, 0.0, 0.0),
    };
    let mut start = guess;
    while st.seated.len() < want && !st.seated.is_empty() {
        let (ndir, rings): (u32, Vec<f64>) = match LEVELS.get(level) {
            Some((n, r)) => (*n, r.to_vec()),
            None => (16, vec![2.0 + 0.5 * (level as f64 - 2.0)]),
        };
        let mut queued = 0;
        for k in done..st.seated.len() {
            let (c, reach) = st.footprint(k);
            for d in 0..ndir {
                let jit = JITTER.0 * 8.0 / f64::from(ndir);
                let ang = (360.0 / f64::from(ndir) * f64::from(d)
                    + (hjit(c.0, c.1, 300.0 + f64::from(d)) - 0.5) * 2.0 * jit)
                    .to_radians();
                let far = 1.0 + hjit(c.0, c.1, 400.0 + f64::from(d)) * JITTER.1;
                let base = seat_toward(c, reach, guess, ang, gap);
                for &ring in &rings {
                    let q = (
                        c.0 + (base.0 - c.0) * far * ring,
                        c.1 + (base.1 - c.1) * far * ring,
                    );
                    let key = (
                        (q.0 / 10.0).round_ties_even() as i64,
                        (q.1 / 10.0).round_ties_even() as i64,
                    );
                    st.tests.add("candidate@grow", 8);
                    if q.0 >= 0.0
                        && q.1 >= 0.0
                        && q.0 <= site.canvas.0
                        && q.1 <= site.canvas.1
                        && seen.insert(key)
                    {
                        queued += 1;
                        let dist = (q.0 - center.0).hypot(q.1 - center.1);
                        heap.push(std::cmp::Reverse((
                            (dist / TIE_RING_FT) as i64,
                            chain_distance(q, &site.rules.site_chains).to_bits(),
                            dist.to_bits(),
                            offers.len(),
                        )));
                        offers.push((q, (c, reach, ang, far * ring, None)));
                    }
                }
            }
            // ...and, while the share has room, its tight seats: at the tight parting in the same directions, unjittered in distance,
            // on its yard's side, queued once a house and only round one a passage may cross to (`growth.py`, feature 317)
            if st.passage_left > 0 && st.crossable(k) && tight_q.insert(k) {
                let yard = st.seated[k].bundle.boxes[1];
                for d in 0..ndir {
                    let jit = JITTER.0 * 8.0 / f64::from(ndir);
                    let ang = (360.0 / f64::from(ndir) * f64::from(d)
                        + (hjit(c.0, c.1, 300.0 + f64::from(d)) - 0.5) * 2.0 * jit)
                        .to_radians();
                    if !yard_side(c, (yard.0, yard.1), ang) {
                        continue;
                    }
                    let q = seat_toward(c, reach, guess, ang, TIGHT.0);
                    st.tests.add("candidate@grow", 4);
                    if q.0 >= 0.0 && q.1 >= 0.0 && q.0 <= site.canvas.0 && q.1 <= site.canvas.1 {
                        queued += 1;
                        let dist = (q.0 - center.0).hypot(q.1 - center.1);
                        heap.push(std::cmp::Reverse((
                            (dist / TIE_RING_FT) as i64,
                            chain_distance(q, &site.rules.site_chains).to_bits(),
                            dist.to_bits(),
                            offers.len(),
                        )));
                        offers.push((q, (c, reach, ang, 1.0, Some(k))));
                    }
                }
            }
        }
        done = st.seated.len();
        let Some(top) = heap.pop() else {
            if level >= LEVELS.len() && queued == 0 {
                break;
            }
            level += 1;
            done = 0;
            continue;
        };
        let (c, reach, ang, scale, nb) = offers[top.0 .3].1;
        // a tight seat once the share is spent is no seat: it is not settled (no settle moves the start)
        let spent = nb.is_some() && st.passage_left == 0;
        let parting = if nb.is_some() { TIGHT.0 } else { gap };
        let Some(lot) = st.lot(site) else { break };
        // the settled seat: from the start, moved out while the household's envelope there outgrows the one it was offered for; none
        // as soon as a seat it would roll at is one the placer refuses its house outright (`seat_refused`)
        let mut new = start;
        let mut got = None;
        for _ in 0..if spent { 0 } else { SETTLE_TRIES } {
            let base = seat_toward(c, reach, new, ang, parting);
            let q = (c.0 + (base.0 - c.0) * scale, c.1 + (base.1 - c.1) * scale);
            let turn = Seating::turn(site, q, &mut st.tests);
            let house = turned_box((q.0, q.1, lot.house.0, lot.house.1), turn);
            if st.blocked(site, house) == Block::Refused {
                break;
            }
            let r = box_reach(q, st.envelope_at(site, &lot, q));
            if r.0 <= new.0 + 1e-9
                && r.1 <= new.1 + 1e-9
                && r.2 <= new.2 + 1e-9
                && r.3 <= new.3 + 1e-9
            {
                got = Some((q, new));
                start = union(guess, r);
                break;
            }
            new = union(r, new);
        }
        let Some((q, own)) = got else { continue };
        if st
            .seated
            .iter()
            .any(|s| (s.bundle.house.0 - q.0).hypot(s.bundle.house.1 - q.1) < 50.0)
        {
            continue;
        }
        let standing: Vec<(Pt, Footprint)> =
            (0..st.seated.len()).map(|k| st.footprint(k)).collect();
        let keep = Keep {
            from: (c, reach),
            gap: parting,
            standing,
            others: gap,
            tight: nb.map(|k| Tight {
                nb: k,
                land: super::passage::land_box(c, reach),
                own,
            }),
        };
        st.offer(site, q.0, q.1, Some(&keep));
    }
    st
}

/// Does a seat's smallest yard, in front of the house at `q`, touch the reach - the first house's ground a way can come to?
fn opens_at(site: &Site, q: Pt, tests: &mut Counts) -> bool {
    let hh = 28.0 * 0.90;
    let y = (q.0, q.1 + hh / 2.0 + 3.0 + 10.0, 30.0, 20.0);
    site.reach
        .touches((y.0 - y.2, y.1 - y.3), (y.0 + y.2, y.1 + y.3), tests)
}
