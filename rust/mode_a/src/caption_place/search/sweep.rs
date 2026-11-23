//! The third step, past the usual gap (feature 449 T202; T209's leader rule): the sweep outward from the feature's drawn box, a chunk at
//! a time per ranked direction, the nearest free seat winning - one tied back by a leader across another feature's building refused
//! while a seat whose leader crosses none is within reach.
//!
//! Research: the sweep's module - NONE: the third step split from `search.rs` at the file-size bar, deciding nothing itself; its rules are claimed where they are decided

use super::super::captions::Caption;
use super::super::geom::{bbox, grow, length_inside, ring, turn, Pt, EPS};
use super::super::index::{band, near, Own, Stance, Weight};
use super::super::leader::{leader, Slide};
use super::interval;
use super::{mid, seat_center};
use super::{Frame, Placer, CHUNK_PX, LEADER_PAST_GAPS, RANKS, SWEEP_REACH_GAPS, SWEEP_START_GAPS};
use crate::work_counts::count;

/// How far a leader may run inside another building, in usual gaps, before it crosses it.
///
/// Research: a corner clipped - GUESS: twice the usual gap; no page sizes it - a leader clipping a building's corner still reads as passing beside it, one run through it reads as tying the name to it (the coordinator's ruling 2026-11-19: a pool sheet's latrine leader clipping the gatehouse's corner read fine, and refused it was led along the stables' wall instead)
pub const CLIP_ALLOWED_GAPS: f64 = 2.0;

/// How near a building's or wall's drawn edge a leader runs along it, at least: a stroke's width, never under this.
///
/// Research: along an edge - CONVENTION: a leader within a stroke's width of a building's or wall's drawn edge (at least 1 px, a hairline's band either side as the index files one) for more than a usual gap cannot be told from the edge, and is refused as one crossing it (the coordinator's ruling 2026-11-19: a pool sheet's latrine leader run down the stables' wall line read as part of the stables)
pub const ALONG_MIN_PX: f64 = 1.0;

/// One sweep asked: the block, each direction's start center (offset 0) and the offsets it may take, where to start and how far to go.
struct Sweep {
    wh: (f64, f64),
    starts: [Pt; 8],
    spans: [(f64, f64); 8],
    from: f64,
    reach: f64,
    /// The offset past which the seat is tied back by a leader, whose run is asked of each candidate past it.
    lead: f64,
}

/// Is an index entry another feature's ink a leader in `lb` could meet: a building or fixture's ink near the leader, not its own feature,
/// nor ink its caption stands to as `Stance::Skip` (`Own::stance`), nor a caption (a leader past another name's
/// letters was tried and sent a pool sheet's "Fox Clan lands" across the border it names, onto the far side's road), ground, a way or a
/// named area.
///
/// Research: the ink a leader is kept off - CONVENTION: a building's or fixture's ink alone (an index entry of `Weight::Block`), never the caption's own feature, ink the caption stands to as `Stance::Skip` (the cases `Own::stance` lists), another caption's letters, ground, a way or a named area (every weight but `Block`) - the rule `Placer::leader_crosses` states, which the slide (`Placer::led`) shares
fn other_ink(
    lb: super::super::geom::Bx,
    e: &super::super::index::Entry,
    ix: &super::super::index::Index,
    own: &Own<'_>,
) -> bool {
    // its own feature, outline and all, is where the leader ends
    near(lb, e)
        && !e.shape.is_some_and(|p| own.parts.contains(&p))
        && own.stance(ix, e) != Stance::Skip
        && e.weight == Weight::Block
}

impl Placer<'_> {
    /// Would a leader from `a` to `b` cross another feature: run through a building or fixture's ink past a clipped corner's allowance
    /// ([`CLIP_ALLOWED_GAPS`]), or along its drawn edge ([`ALONG_MIN_PX`]) - not another caption, open ground, a way, a named area drawn
    /// by no ink of its own, nor the caption's own feature (`exact_test`, one an entry's segment, for each of the two tests).
    ///
    /// Research: a leader kept off other features - CONVENTION: 0330 fixes where a leader ends and says nothing of what it crosses; a leader run across another building reads as tying the name to that one (observed 2026-11-19 on a pool sheet: with T209's fix the bounty board's name was swept beside the notice board, its leader across the notice board's roof), so a swept seat whose leader would cross one is refused while a seat whose leader crosses none is within reach; ground, ways and named areas are crossed as a caption may lie on them, and another caption's letters too (refusing a leader across them sent a pool sheet's "Fox Clan lands" across the border it names)
    fn leader_crosses(&mut self, (a, b): (Pt, Pt), gap: f64, own: &Own<'_>) -> bool {
        // the leader's box out by the widest band an edge is read within, so an edge the leader runs beside is met
        let lb = grow(bbox(&[a, b]), (2.0 * self.ix.widest_edge).max(ALONG_MIN_PX));
        for id in self.ix.query(lb, "leader_cross") {
            let e = &self.ix.entries[id as usize];
            if !other_ink(lb, e, &self.ix, own) {
                continue;
            }
            let poly: &[Pt] = &e.poly;
            // through it, past a clipped corner's allowance
            count("exact_test@leader_cross", poly.len() as u64);
            if length_inside(a, b, poly) > CLIP_ALLOWED_GAPS * gap {
                return true;
            }
            // along its drawn edge, within a stroke's width of it, for more than a gap
            let near_edge = (2.0 * e.edge).max(ALONG_MIN_PX);
            count("exact_test@leader_along", poly.len() as u64);
            if ring(poly).any(|(c, d)| length_inside(a, b, &band(c, d, near_edge)) > gap) {
                return true;
            }
        }
        false
    }

    /// The leader drawn for a seated caption's tie: where it ends at a shared span's middle and another feature's ink stands on that line,
    /// slid along the span, a pixel at a time, to the line meeting the least other ink - the middle of that run of lines nearest the
    /// span's middle (the lower offset on a tie) - unless that line crosses a feature (`leader_crosses`) the middle's does not; else the
    /// tie as drawn. The sweep asks its seats with the middle's line, so the slide moves no caption, only its leader.
    ///
    /// Research: a leader slid along its shared span - CONVENTION: 0330 leaves open which of a span's equally near points a leader ends at; the span's middle is taken (`leader::block_pair`) unless another feature's ink stands on that line, when the lines within the span a pixel apart are weighed by the ink each runs through or along and the middle of the run of least-ink lines nearest the span's middle is drawn, kept at the middle instead where that line crosses a feature (`Placer::leader_crosses`) the middle's does not (449 T384: at its middle the Ubame sheet's wood-kami altar's leader ran 1 px from a fire-water tub's center, where from the span's end it had passed the tub); the seat itself is chosen on the middle's line, the algorithmically easier route (a slide asked of every swept seat moved the Ochiba sheet's latrine name to a 164 px leader 1.75 px under the retainers' quarters' wall, observed 2026-11-23)
    pub(super) fn led(
        &mut self,
        (a, b, slide): (Pt, Pt, Slide),
        gap: f64,
        own: &Own<'_>,
    ) -> (Pt, Pt) {
        let Some((u, half)) = slide else {
            return (a, b);
        };
        let at = |k: i32| {
            let o = (f64::from(k) * u.0, f64::from(k) * u.1);
            ((a.0 + o.0, a.1 + o.1), (b.0 + o.0, b.1 + o.1))
        };
        if self.ink_met(at(0), own) <= EPS {
            return (a, b);
        }
        #[expect(
            clippy::cast_possible_truncation,
            reason = "half a span on the sheet, a few hundred pixels at most"
        )]
        let n = half.floor() as i32;
        let met: Vec<f64> = (-n..=n).map(|k| self.ink_met(at(k), own)).collect();
        let least = met.iter().copied().fold(f64::INFINITY, f64::min);
        let best = |k: i32| met[usize::try_from(k + n).unwrap_or_default()] <= least + EPS;
        // the best line nearest the middle, the lower offset on a tie (`least` is one of `met`, so one is found), and the run of
        // best lines it stands in
        let k0 = (0..=n)
            .flat_map(|d| [-d, d])
            .find(|&k| best(k))
            .unwrap_or_default();
        let (mut lo, mut hi) = (k0, k0);
        while lo > -n && best(lo - 1) {
            lo -= 1;
        }
        while hi < n && best(hi + 1) {
            hi += 1;
        }
        let k = f64::from(lo + hi) / 2.0;
        let o = (k * u.0, k * u.1);
        let slid = ((a.0 + o.0, a.1 + o.1), (b.0 + o.0, b.1 + o.1));
        if self.leader_crosses(slid, gap, own) && !self.leader_crosses((a, b), gap, own) {
            return (a, b);
        }
        slid
    }

    /// How much of another building's or fixture's ink a leader meets: its length through each, and along within a stroke's width of
    /// each drawn edge - the two tests `leader_crosses` makes, summed.
    ///
    /// Research: the slide's measure - CONVENTION: the ink a line meets, through and along, summed over the features `other_ink` names;
    /// `Placer::led` draws the line along the span that meets the least
    fn ink_met(&mut self, (a, b): (Pt, Pt), own: &Own<'_>) -> f64 {
        let lb = grow(bbox(&[a, b]), (2.0 * self.ix.widest_edge).max(ALONG_MIN_PX));
        let mut met = 0.0;
        for id in self.ix.query(lb, "leader_slide") {
            let e = &self.ix.entries[id as usize];
            if !other_ink(lb, e, &self.ix, own) {
                continue;
            }
            let poly: &[Pt] = &e.poly;
            let near_edge = (2.0 * e.edge).max(ALONG_MIN_PX);
            count("exact_test@leader_slide", 2 * poly.len() as u64);
            met += length_inside(a, b, poly);
            met += ring(poly)
                .map(|(c, d)| length_inside(a, b, &band(c, d, near_edge)))
                .sum::<f64>();
        }
        met
    }

    /// The offsets along `r` from `c0` at which the block stays wholly on the sheet.
    fn view_span(&self, fr: &Frame, c0: Pt, (w, h): (f64, f64), r: (i8, i8)) -> (f64, f64) {
        let u = turn((f64::from(r.0), f64::from(r.1)), fr.angle);
        let v = self.ix.view;
        let (mut lo, mut hi) = (f64::NEG_INFINITY, f64::INFINITY);
        for corner in [
            (-w / 2.0, -h / 2.0),
            (w / 2.0, -h / 2.0),
            (w / 2.0, h / 2.0),
            (-w / 2.0, h / 2.0),
        ] {
            let p = turn((c0.0 + corner.0, c0.1 + corner.1), fr.angle);
            for (x, ux, a, b) in [(p.0, u.0, v.0, v.2), (p.1, u.1, v.1, v.3)] {
                if ux.abs() < 1e-12 {
                    if x < a - EPS || x > b + EPS {
                        return (1.0, 0.0);
                    }
                } else {
                    let (d1, d2) = ((a - x) / ux, (b - x) / ux);
                    lo = lo.max(d1.min(d2));
                    hi = hi.min(d1.max(d2));
                }
            }
        }
        (lo, hi)
    }

    /// The obstacles' intervals along one direction over one chunk `[d0, d1]` (`sweep_interval`, one an obstacle's box).
    ///
    /// Research: a wall ahead - CONVENTION: no swept place lies past a wall standing between the feature and it, unless the wall runs through the feature's middle (a gate in the wall, which has a side each way); 0242 and 0330 say nothing of walls, and a caption beyond one names the wrong court
    fn intervals(
        &mut self,
        fr: &Frame,
        own: &Own<'_>,
        (c0, wh, r): (Pt, (f64, f64), (i8, i8)),
        (d0, d1, from): (f64, f64, f64),
    ) -> (Vec<(f64, f64)>, f64) {
        let (a, b) = (
            (c0.0 + d0 * f64::from(r.0), c0.1 + d0 * f64::from(r.1)),
            (c0.0 + d1 * f64::from(r.0), c0.1 + d1 * f64::from(r.1)),
        );
        let local = (
            a.0.min(b.0) - wh.0 / 2.0,
            a.1.min(b.1) - wh.1 / 2.0,
            a.0.max(b.0) + wh.0 / 2.0,
            a.1.max(b.1) + wh.1 / 2.0,
        );
        let strip = fr.sheet(local);
        let mut fresh = Vec::new();
        let mut wall = f64::INFINITY;
        for id in self.ix.query(strip, "sweep") {
            let e = &self.ix.entries[id as usize];
            if !near(strip, e) || own.stance(&self.ix, e) == Stance::Skip {
                continue;
            }
            let o = Self::met_box(fr, &e.poly, e.convex, local);
            count("sweep_interval@sweep", 1);
            let iv = interval(c0, wh, r, o);
            // a wall reaching past where the sweep starts lies between the feature and every place past it - unless it runs through the
            // feature itself (a gate in the wall), which has a side each way
            let through = own.fbox_sheet.is_some_and(|fb| {
                let m = mid(fb);
                e.bx.0 <= m.0 && m.0 <= e.bx.2 && e.bx.1 <= m.1 && m.1 <= e.bx.3
            });
            if let Some((lo, _)) = iv.filter(|w| e.wall && !through && w.1 > from) {
                wall = wall.min(lo.max(from));
            }
            fresh.extend(iv);
        }
        (fresh, wall)
    }

    /// A sweep: per direction, the intervals its obstacles cover, a chunk at a time, stopped at the first chunk where any direction is
    /// free; the nearest free offset wins, rank breaking ties, a seat whose leader would cross another feature only where no other is
    /// within reach. `(center in the frame, offset, rank, whether its leader crosses another feature)`.
    ///
    /// Research:
    ///     the caption's seat - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: when every place at the usual gap is taken, the same ranked places are tried a step further out, and the nearer free place always wins - ties going to the higher rank; never a place off the edge of the picture (the view's span), nor one past a wall (`intervals`' claim)
    ///     a leader kept off other features - CONVENTION: past twice the gap, where a leader is drawn, a direction whose nearest free seat's leader would cross another building (`leader_crosses`) is given up rather than swept on - the algorithmically easier route, the record silent: a seat further out the same way is led back past the same building - and the first such seat is kept, returned only where no seat within reach is led clear, for `search` to weigh against covering least
    fn sweep(&mut self, s: &Sweep, fr: &Frame, own: &Own<'_>) -> Option<(Pt, f64, usize, bool)> {
        let mut kept: Vec<Vec<(f64, f64)>> = vec![Vec::new(); RANKS.len()];
        // per direction, the nearest offset at which a wall ahead begins: no place past it
        let mut walls = [f64::INFINITY; 8];
        // the nearest seat whose leader would cross another feature, taken only where no seat within reach crosses none
        let mut crossing: Option<(Pt, f64, usize, bool)> = None;
        let mut d0 = s.from;
        while d0 <= s.reach && walls.iter().any(|w| *w >= d0) {
            let d1 = d0 + CHUNK_PX;
            let mut free: Vec<(f64, usize)> = Vec::new();
            for (rank, &r) in RANKS.iter().enumerate() {
                let (lo_ok, hi_ok) = s.spans[rank];
                if lo_ok > hi_ok || hi_ok < d0 || lo_ok > d1 || walls[rank] < d0 {
                    continue;
                }
                let (fresh, wall) =
                    self.intervals(fr, own, (s.starts[rank], s.wh, r), (d0, d1, s.from));
                walls[rank] = walls[rank].min(wall);
                let list = &mut kept[rank];
                list.retain(|iv| iv.1 > d0);
                let n = fresh.len();
                if n > 0 {
                    #[expect(
                        clippy::cast_possible_truncation,
                        clippy::cast_sign_loss,
                        clippy::cast_precision_loss,
                        reason = "a small sort's comparisons"
                    )]
                    let sorting =
                        (n as f64 * (n as f64 + 1.0).log2().ceil().max(1.0)) as u64 + n as u64;
                    count("sweep_compare@sweep", sorting);
                    list.extend(fresh);
                    list.sort_by(|x, y| x.0.total_cmp(&y.0));
                }
                let mut d = d0.max(lo_ok);
                for &(lo, hi) in list.iter() {
                    count("sweep_compare@sweep", 1);
                    if hi <= d {
                        continue;
                    }
                    if lo < d {
                        d = hi;
                    } else {
                        break;
                    }
                }
                count("seat@sweep", 1);
                if d <= d1 && d <= hi_ok && d <= walls[rank] {
                    free.push((d, rank));
                }
            }
            // the nearest free seat, rank breaking ties; one tied back across another feature gives up its direction - a seat further
            // out the same way is led back past the same feature - and the next nearest is asked
            while let Some((d, rank)) = nearest_first(&mut free) {
                let (c0, r) = (s.starts[rank], RANKS[rank]);
                let c = (c0.0 + d * f64::from(r.0), c0.1 + d * f64::from(r.1));
                if d > s.lead {
                    let tie = leader(
                        turn(c, fr.angle),
                        (s.wh.0, s.wh.1, fr.angle),
                        self.shapes,
                        own.parts,
                    );
                    if tie.is_some_and(|t| self.leader_crosses(t, s.lead / LEADER_PAST_GAPS, own)) {
                        walls[rank] = f64::NEG_INFINITY;
                        crossing = crossing.or(Some((c, d, rank, true)));
                        continue;
                    }
                }
                return Some((c, d, rank, false));
            }
            d0 = d1;
        }
        crossing
    }

    /// The third step, past the usual gap: the sweep outward from the feature's drawn box.
    pub(super) fn beyond(
        &mut self,
        cap: &Caption,
        fr: &Frame,
        own: &Own<'_>,
    ) -> Option<(Pt, f64, usize, bool)> {
        let wh = (cap.w, cap.h);
        let mut starts = [(0.0, 0.0); 8];
        let mut spans = [(0.0, 0.0); 8];
        for (k, &r) in RANKS.iter().enumerate() {
            starts[k] = seat_center(fr.fb, wh, r, 0.0);
            spans[k] = self.view_span(fr, starts[k], wh, r);
        }
        let sweep = Sweep {
            wh,
            starts,
            spans,
            from: SWEEP_START_GAPS * cap.gap,
            reach: SWEEP_REACH_GAPS * cap.gap,
            lead: LEADER_PAST_GAPS * cap.gap,
        };
        self.sweep(&sweep, fr, own)
    }
}

/// The nearest of the free seats taken out of the list, the higher rank winning a tie: the list keeps its rank order, so a tie after a
/// seat is taken out still goes to the higher rank.
fn nearest_first(free: &mut Vec<(f64, usize)>) -> Option<(f64, usize)> {
    let k = (0..free.len()).reduce(|i, j| if free[j].0 < free[i].0 - EPS { j } else { i })?;
    Some(free.remove(k))
}

#[cfg(test)]
mod tests {
    use super::super::super::index::{Index, Met, Own};
    use super::super::Placer;
    use super::nearest_first;
    use crate::labels::hand_sheet::read_sheet;

    /// A leader crosses a building it runs through, and not one whose box it meets but whose ink it passes, nor one whose corner it
    /// clips by no more than twice the usual gap; and a leader running along a building's drawn edge for more than a gap is refused as
    /// one crossing it (4 px gaps: a 7.07 px clip passes, a 20 px run through and a 40 px run along the edge do not).
    #[test]
    fn a_leader_crosses_only_the_ink_it_runs_through() {
        let src = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect x="100" y="100" width="40" height="40" fill="#C9A57A" stroke="#5A3F1E" stroke-width="1" data-kind="storehouse"/></svg>"##;
        let (shapes, view) = read_sheet(src).unwrap();
        let ix = Index::build(&shapes, view, vec![0; shapes.len()], usize::MAX);
        let mut placer = Placer {
            shapes: &shapes,
            ix,
        };
        let met = Met::default();
        let own = bare(&met);
        assert!(placer.leader_crosses(((130.0, 80.0), (130.0, 120.0)), 4.0, &own));
        // past the corner (140, 100): at x = 140 the line stands at y = 90
        assert!(!placer.leader_crosses(((130.0, 80.0), (160.0, 110.0)), 4.0, &own));
        // clipping the corner: inside from (135, 100) to (140, 105), 7.07 px, under twice the gap
        assert!(!placer.leader_crosses(((130.0, 95.0), (150.0, 115.0)), 4.0, &own));
        // along the right edge, 0.5 px off its line and 40 px long, it reads as the edge
        assert!(placer.leader_crosses(((140.5, 100.0), (140.5, 140.0)), 4.0, &own));
        // and 6 px off it, a clear line beside it
        assert!(!placer.leader_crosses(((146.0, 100.0), (146.0, 140.0)), 4.0, &own));
    }

    /// A caption that owns no drawn part, its leader asked of every other feature's ink.
    fn bare(met: &Met) -> Own<'_> {
        Own {
            parts: &[],
            fbox_sheet: None,
            ground: false,
            at: 0,
            clear_own_lines: false,
            under: None,
            region: false,
            met,
            subtree: None,
            stack: 0.0,
            on_outline: false,
        }
    }

    /// A slide is not kept where its line crosses a feature the middle's line does not (449 T384): the middle meets two small
    /// sheds, 7 px through each (under twice the 4 px gap) and across their ends, while every other line within its 3 px of span
    /// runs along a drawn edge for more than the gap (a 7 x 6 px store's face 3 px each side, the sheds' own sides 1.5 px off) - less
    /// ink, but a crossing; so the middle's line is drawn.
    #[test]
    fn a_slide_onto_a_crossing_keeps_the_middle() {
        let rect = |x: f64, y: f64, w: f64, h: f64| {
            format!(
                r##"<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9A57A" stroke="#5A3F1E" stroke-width="1" data-kind="storehouse"/>"##
            )
        };
        let body = [
            rect(98.5, 10.0, 3.0, 7.0),
            rect(98.5, 30.0, 3.0, 7.0),
            rect(90.0, 60.0, 7.0, 6.0),
            rect(103.0, 60.0, 7.0, 6.0),
        ]
        .concat();
        let src = format!(
            r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">{body}</svg>"#
        );
        let (shapes, view) = read_sheet(&src).unwrap();
        let ix = Index::build(&shapes, view, vec![0; shapes.len()], usize::MAX);
        let mut placer = Placer {
            shapes: &shapes,
            ix,
        };
        let met = Met::default();
        let own = bare(&met);
        let mid = ((100.0, 0.0), (100.0, 100.0));
        let side = ((97.0, 0.0), (97.0, 100.0));
        let (crossed, side_crossed) = (
            placer.leader_crosses(mid, 4.0, &own),
            placer.leader_crosses(side, 4.0, &own),
        );
        assert!(!crossed && side_crossed, "{crossed} {side_crossed}");
        let got = placer.led((mid.0, mid.1, Some(((1.0, 0.0), 3.0))), 4.0, &own);
        assert_eq!(got, mid);
    }

    /// The nearest free seat first, a tie to the higher rank even after a nearer seat is taken out of the list.
    #[test]
    fn the_nearest_seat_first_rank_breaking_ties() {
        let mut free = vec![(5.0, 0), (7.0, 1), (6.0, 2), (7.0, 7)];
        assert_eq!(nearest_first(&mut free), Some((5.0, 0)));
        assert_eq!(nearest_first(&mut free), Some((6.0, 2)));
        assert_eq!(nearest_first(&mut free), Some((7.0, 1)));
        assert_eq!(nearest_first(&mut free), Some((7.0, 7)));
        assert_eq!(nearest_first(&mut free), None);
    }
}
