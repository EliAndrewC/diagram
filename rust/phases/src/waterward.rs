//! The waterward fringe (feature 444 T29): a polder's reed strips outside its dike, on the flanks that face the water it was
//! reclaimed from - laid once the seat names the flank the village stands on, before the houses and the track, so both treat it as
//! the wet ground it is. Nothing on a valley hamlet.
//!
//! Research:
//!     the waterward fringe - NONE: the stage's machinery; each rule's claim is at the unit that keeps it

use std::collections::HashMap;

use crate::field::fan::Pt;

/// How far the strip runs past the dike's ends, across the other axis (feet): before its start and past its end.
///
/// Research:
///     its reed strip's run - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 30 ft before the dike's start, 20 ft past its end
pub const RUN_PAST: (f64, f64) = (30.0, 20.0);

/// How far off the canvas a strip may reach (feet).
///
/// Research:
///     the strip off the frame - CONVENTION: wild ground continuing, carried 20 ft past the canvas edge
pub const OFF_CANVAS: f64 = 20.0;

/// The compass letter a map vector points to (the map's y grows down, so +y is S).
fn compass(v: Pt) -> char {
    if v.0.abs() >= v.1.abs() {
        if v.0 > 0.0 {
            'E'
        } else {
            'W'
        }
    } else if v.1 > 0.0 {
        'S'
    } else {
        'N'
    }
}

/// Which flanks of the dike face the water it was reclaimed from: the foot (the outfall side, already wet) and the cross flanks the
/// village does not stand on - not the head, where the header reservoir stands as the wild water.
///
/// Research:
///     waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: every flank but the landward one holds water back; a reed fringe along the low foot where the outfall drains and along the cross flank off the shore, the wild pond that feeds the polder at its head - its water drawn there as the pond, so no reed strip is laid off the head
#[must_use]
pub fn flanks(fall: Pt, seat_out: Option<Pt>) -> Vec<char> {
    let (dx, dy) = fall;
    let cluster = seat_out.map(compass);
    [compass((-dy, dx)), compass((dy, -dx)), compass((dx, dy))]
        .into_iter()
        .filter(|q| Some(*q) != cluster)
        .collect()
}

/// The side of the box `(x0, y0, x1, y1)` a point stands nearest: `W`, `E`, `N` or `S`, the first of them on a tie.
fn nearest(p: Pt, (x0, y0, x1, y1): (f64, f64, f64, f64)) -> char {
    let near = [
        ('W', p.0 - x0),
        ('E', x1 - p.0),
        ('N', p.1 - y0),
        ('S', y1 - p.1),
    ];
    near.iter()
        .fold(near[0], |a, &b| if b.1 < a.1 { b } else { a })
        .0
}

/// The dike's outer face along one flank, as a polyline spanning `lo` to `hi` along the flank's axis: the outline `ring`'s corners
/// that stand nearest the flank (of the box `bbox` round the ring) in order along the axis - the face itself, point for point -
/// carried at each end one corner on round the dike's corner, then to the box's own corner and on along its side, so the strip
/// meets the next flank's at the corner's diagonal without turning onto its next face; each depth rounded outward to a tenth of a
/// foot.
///
/// Research:
///     strip at the dike's outer face - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); the reeds stop at the outermost face, meeting it point for point and never on the band (research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the maps curve the dike's outer face with the water's edge)
///     the flank's own face - GUESS: no page says where one flank's fringe gives way to the next at a corner; a corner of the outline is the flank whose side of the box it stands nearest, the strip carried one corner past it and out to the box's corner, so two strips meeting at a corner leave no bare ground between them and neither turns onto the other's face
#[must_use]
pub fn face(
    ring: &[Pt],
    bbox: (f64, f64, f64, f64),
    flank: char,
    lo: f64,
    hi: f64,
    tests: &mut u64,
) -> Vec<Pt> {
    let horiz = matches!(flank, 'W' | 'E');
    let (along, depth) = (
        |p: Pt| if horiz { p.1 } else { p.0 },
        |p: Pt| if horiz { p.0 } else { p.1 },
    );
    let outward_min = matches!(flank, 'W' | 'N');
    let side = match flank {
        'W' => bbox.0,
        'E' => bbox.2,
        'N' => bbox.1,
        _ => bbox.3,
    };
    let (start, end) = if horiz {
        (bbox.1, bbox.3)
    } else {
        (bbox.0, bbox.2)
    };
    let n = ring.len();
    // each corner filed to its side, and the corners walked again for the flank's own; those put in order along the axis, a
    // comparison each
    *tests += 2 * n as u64;
    let filed: Vec<bool> = ring.iter().map(|&p| nearest(p, bbox) == flank).collect();
    let mut own: Vec<usize> = (0..n).filter(|&i| filed[i]).collect();
    own.sort_by(|&a, &b| {
        *tests += 1;
        along(ring[a]).total_cmp(&along(ring[b]))
    });
    let out = |v: f64| {
        if outward_min {
            (v * 10.0).floor() / 10.0
        } else {
            (v * 10.0).ceil() / 10.0
        }
    };
    let put = |t: f64, d: f64| if horiz { (out(d), t) } else { (t, out(d)) };
    // the corner on round the dike from an end of the face, strictly `before` or past it along the axis: a neighbor not the flank's own
    let past = |i: usize, before: bool| {
        [(i + n - 1) % n, (i + 1) % n].into_iter().find(|&j| {
            !filed[j]
                && if before {
                    along(ring[j]) < along(ring[i])
                } else {
                    along(ring[j]) > along(ring[i])
                }
        })
    };
    // the two ends' neighbors asked, and the flank's own written out once
    *tests += 4 + own.len() as u64;
    let mut line = vec![put(lo, side), put(start, side)];
    if let (Some(&first), Some(&last)) = (own.first(), own.last()) {
        line.extend(past(first, true).map(|j| put(along(ring[j]), depth(ring[j]))));
        line.extend(own.iter().map(|&i| put(along(ring[i]), depth(ring[i]))));
        line.extend(past(last, false).map(|j| put(along(ring[j]), depth(ring[j]))));
    }
    line.push(put(end, side));
    line.push(put(hi, side));
    line
}

/// The face's depth at `t` along its axis, read off the polyline `face` of (along, depth) pairs in order along the axis, held at its
/// ends past them: the first point at or past `t` found by halving, a test a step.
fn face_at(face: &[(f64, f64)], t: f64, tests: &mut u64) -> f64 {
    *tests += steps(face.len());
    let i = face.partition_point(|p| p.0 < t);
    match (i, face.get(i)) {
        (_, None) => face.last().map_or(0.0, |p| p.1),
        (0, Some(b)) => b.1,
        (_, Some(&b)) => {
            let a = face[i - 1];
            a.1 + (b.1 - a.1) * ((t - a.0) / (b.0 - a.0))
        }
    }
}

/// The steps a halving search over `n` items takes: one more than the bits of `n`.
fn steps(n: usize) -> u64 {
    u64::from(usize::BITS - n.leading_zeros()) + 1
}

/// The ring `ring` cut to the half-plane where `n . p >= k` (Sutherland and Hodgman's walk), a test a corner: the corners on that
/// side kept in order, a corner added where an edge crosses the line.
fn clip(ring: &[Pt], n: Pt, k: f64, tests: &mut u64) -> Vec<Pt> {
    *tests += ring.len() as u64;
    let side = |p: Pt| n.0 * p.0 + n.1 * p.1 - k;
    let mut out = Vec::new();
    for (i, &p) in ring.iter().enumerate() {
        let q = ring[(i + 1) % ring.len()];
        let (sp, sq) = (side(p), side(q));
        if sp >= 0.0 {
            out.push(p);
        }
        if (sp >= 0.0) != (sq >= 0.0) {
            let s = sp / (sp - sq);
            out.push((p.0 + (q.0 - p.0) * s, p.1 + (q.1 - p.1) * s));
        }
    }
    out
}

/// The four corners of a channel's bed along one straight reach `a` to `b`, `w` feet wide and carried half its width past each
/// end, in order round it; `None` for a reach of no length.
///
/// Research:
///     the channel's bed - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: the bed its drawn width across and run square half a width past each end of every reach, so a bend's outer corner is covered and the reeds come to the water's edge and stay out of the water (about 3 ft past a channel's drawn end inside the strip)
fn bed(a: Pt, b: Pt, w: f64) -> Option<[Pt; 4]> {
    let len = crate::field::geom::dist(a, b);
    if len < 1e-9 {
        return None;
    }
    // the bed half its width either side of the reach and half its width past each end, so a bend's outer corner is covered
    let (ux, uy) = ((b.0 - a.0) / len * w / 2.0, (b.1 - a.1) / len * w / 2.0);
    let (a, b) = ((a.0 - ux, a.1 - uy), (b.0 + ux, b.1 + uy));
    let (nx, ny) = (-uy, ux);
    Some([
        (a.0 + nx, a.1 + ny),
        (b.0 + nx, b.1 + ny),
        (b.0 - nx, b.1 - ny),
        (a.0 - nx, a.1 - ny),
    ])
}

/// How far past its sides a bed is taken out (feet), so a ring's edge lying along one of them - a strip's end set at the bed's
/// nearest point - is crossed cleanly rather than touched.
const PAST_BED: f64 = 1e-10;

/// Where a ring's edge crosses a bed's side: the edge (`i`) and how far along it (`s`, 0 to 1), the bed's side (`j`) and how far
/// along it (`r`, feet), the point, and whether the ring goes in there.
#[derive(Clone, Copy)]
struct Crossing {
    i: usize,
    s: f64,
    j: usize,
    r: f64,
    at: Pt,
    enter: bool,
}

/// A side of a bed: its start, its direction and its inward normal (feet).
type Side = (Pt, Pt, Pt);

/// How far inside a bed's side `side` the point `x` stands (feet), the bed taken out `PAST_BED` past it.
fn depth((a, _, m): Side, x: Pt) -> f64 {
    m.0 * (x.0 - a.0) + m.1 * (x.1 - a.1) + PAST_BED
}

/// Whether the point `x` stands within the bed whose sides are `sides`, `PAST_BED` past them.
fn within(sides: &[Side; 4], x: Pt) -> bool {
    sides.iter().all(|&j| depth(j, x) >= 0.0)
}

/// Where each edge of the ring `p` goes into and comes out of the bed whose sides are `sides` (Cyrus and Beck's clip of each edge
/// to the bed), in order round the ring: four tests an edge.
fn crossings(p: &[Pt], sides: &[Side; 4], tests: &mut u64) -> Vec<Crossing> {
    let n = p.len();
    let along = |(a, e, _): Side, x: Pt| e.0 * (x.0 - a.0) + e.1 * (x.1 - a.1);
    *tests += 4 * n as u64;
    let mut xs = Vec::new();
    for i in 0..n {
        let (a, b) = (p[i], p[(i + 1) % n]);
        let (mut s0, mut s1, mut j0, mut j1) = (0.0_f64, 1.0_f64, 0, 0);
        for (j, &side) in sides.iter().enumerate() {
            let (fa, fb) = (depth(side, a), depth(side, b));
            if fa < 0.0 && fb >= 0.0 && fa / (fa - fb) > s0 {
                (s0, j0) = (fa / (fa - fb), j);
            } else if fa >= 0.0 && fb < 0.0 && fa / (fa - fb) < s1 {
                (s1, j1) = (fa / (fa - fb), j);
            } else if fa < 0.0 && fb < 0.0 {
                s0 = f64::INFINITY;
            }
        }
        let pt = |s: f64| (a.0 + (b.0 - a.0) * s, a.1 + (b.1 - a.1) * s);
        let (ain, bin) = (within(sides, a), within(sides, b));
        if !ain && (bin || s0 < s1) {
            let at = pt(s0);
            xs.push(Crossing {
                i,
                s: s0,
                j: j0,
                r: along(sides[j0], at),
                at,
                enter: true,
            });
        }
        if !bin && (ain || s0 < s1) {
            let at = pt(s1);
            xs.push(Crossing {
                i,
                s: s1,
                j: j1,
                r: along(sides[j1], at),
                at,
                enter: false,
            });
        }
    }
    xs
}

/// The ring `p` with the convex four-sided bed `q` taken out, as the rings left (Weiler and Atherton's walk): the ring's own edges
/// outside the bed, and between each place it goes into the bed and the place it comes out the bed's own sides that lie in the
/// ring, so the ring is cut along the bed itself. A bed wholly inside the ring is first parted across its middle; a ring wholly
/// inside the bed is gone; a ring the bed misses is kept whole.
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn difference(p: &[Pt], q: &[Pt; 4], tests: &mut u64) -> Vec<Vec<Pt>> {
    use crate::field::geom::signed_area;
    let n = p.len();
    // the bed walked against the ring's sense, so its sides between going in and coming out bound what is left
    let mut q = *q;
    // the ring's sense read, a test a corner
    *tests += n as u64;
    if signed_area(&q) * signed_area(p) > 0.0 {
        q.reverse();
    }
    let sense = signed_area(&q).signum();
    let sides: [Side; 4] = [0, 1, 2, 3].map(|j| {
        let e = crate::field::geom::unit(q[j], q[(j + 1) % 4]);
        (q[j], e, (-sense * e.1, sense * e.0))
    });
    let xs = crossings(p, &sides, tests);
    let m = xs.len();
    if m == 0 {
        // each corner asked of the bed's four sides, then the bed's middle of the ring, a test a corner each
        *tests += 4 * n as u64;
        if p.iter().all(|&x| within(&sides, x)) {
            return Vec::new();
        }
        let mid = (f64::midpoint(q[0].0, q[2].0), f64::midpoint(q[0].1, q[2].1));
        *tests += n as u64;
        if !crate::field::geom::inside(mid, p) {
            return vec![p.to_vec()];
        }
        // a bed wholly inside: the ring parted across the bed's middle, each half then cut
        let (_, e, _) = sides[0];
        let k = e.0 * mid.0 + e.1 * mid.1;
        return [clip(p, e, k, tests), clip(p, (-e.0, -e.1), -k, tests)]
            .iter()
            .flat_map(|h| difference(h, &q, tests))
            .collect();
    }
    // the crossings in order round the bed, each one's place in it
    let mut order: Vec<usize> = (0..m).collect();
    order.sort_by(|&a, &b| {
        *tests += 1;
        xs[a].j.cmp(&xs[b].j).then(xs[a].r.total_cmp(&xs[b].r))
    });
    let mut place = vec![0; m];
    for (k, &x) in order.iter().enumerate() {
        place[x] = k;
    }
    let mut seen = vec![false; m];
    let mut out = Vec::new();
    for start in 0..m {
        if xs[start].enter || seen[start] {
            continue;
        }
        let mut ring = Vec::new();
        let mut k = start;
        loop {
            seen[k] = true;
            // out along the ring to where it next goes in
            let (x, y) = (xs[k], xs[(k + 1) % m]);
            ring.push(x.at);
            let mut run = (y.i + n - x.i) % n;
            if run == 0 && k + 1 == m && y.s <= x.s {
                run = n;
            }
            *tests += run as u64 + 1;
            ring.extend((1..=run).map(|t| p[(x.i + t) % n]));
            ring.push(y.at);
            // round the bed's sides to where the ring next comes out
            let z = order[(place[(k + 1) % m] + 1) % m];
            let mut round = (xs[z].j + 4 - y.j) % 4;
            if round == 0 && place[z] <= place[(k + 1) % m] {
                round = 4;
            }
            ring.extend((1..=round).map(|t| q[(y.j + t) % 4]));
            k = z;
            if k == start || seen[k] {
                break;
            }
        }
        out.push(ring);
    }
    out
}

/// One flank's strip cut at the channels that cross it, each straight reach's bed (`bed`) taken out of it along the bed's own
/// sides (`difference`), so the reeds run to each bank of a slanting reach as of a square one, round a reach's end where it stops
/// inside the strip, and never over the water. A bed that reaches either end of the strip's span also ends the strip's run past the
/// dike's end (`RUN_PAST`) square across at the bed's nearest point past the dike's extent. Each piece left lies between the
/// strip's `outer` edge, the face and the beds - a piece between a slanting bed and the dike may touch neither the outer edge nor
/// the strip's ends; a piece wholly past the dike's own extent along the axis (`ext`) - the run past a corner that the channel cuts
/// off - is dropped.
///
/// Research:
///     the strip stops at the channel's bank - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: its section "How our maps draw the marsh's edge" - where a stream or a ditch crosses the marsh the reeds are drawn right to the water's edge, and kept out of the water itself - each reach's bed taken out along its own sides at its drawn width, slanting or square; the strip ends at the bank of the channel that crosses the dike at a sluice (research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: water crosses the dike only at gated sluices; research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: where a channel crosses the dike the band is cut), so no reed is drawn across the channel the sluice shuts
///     the run past the cut dropped - GUESS: a piece left wholly past the dike's own extent is the strip's run past the dike's end (`RUN_PAST`, itself a GUESS) beyond the channel, dropped so the strip stops at the cut, and a bed reaching the end of the strip's span ends that run square across at the bed's nearest point past the dike's extent; a channel crossing mid-flank leaves reeds on both its banks, as research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html lines each bank, but past a corner the far bank keeps only what another flank's strip lays there
#[expect(
    clippy::too_many_arguments,
    reason = "the flank's face, edge, span and extent, the channels and the counter"
)]
fn pieces(
    face: &[Pt],
    flank: char,
    outer: f64,
    (lo, hi): (f64, f64),
    ext: (f64, f64),
    channels: &[(&[Pt], f64)],
    tests: &mut u64,
    out: &mut Vec<Vec<Pt>>,
) {
    let horiz = matches!(flank, 'W' | 'E');
    let o = if matches!(flank, 'W' | 'N') {
        -1.0
    } else {
        1.0
    };
    let turn = |(x, y): Pt| if horiz { (y, x) } else { (x, y) };
    // the face turned to (along, depth), a point each
    *tests += face.len() as u64;
    let f: Vec<(f64, f64)> = face.iter().map(|&p| turn(p)).collect();
    let side = f.first().map_or(outer, |p| p.1);
    let boxed = |r: &[Pt], tests: &mut u64| {
        // a ring boxed, a test a corner
        *tests += r.len() as u64;
        r.iter().fold(
            (f64::MAX, f64::MAX, f64::MIN, f64::MIN),
            |(x0, y0, x1, y1), p| (x0.min(p.0), y0.min(p.1), x1.max(p.0), y1.max(p.1)),
        )
    };
    let beds: Vec<[Pt; 4]> = channels
        .iter()
        .flat_map(|&(course, w)| course.windows(2).filter_map(move |r| bed(r[0], r[1], w)))
        .collect();
    // a bed reaching an end of the span ends the run past the dike there: the bed cut to the run past the dike's end (along the
    // axis from the dike's end to the span's, in depth from the face's side to the outer edge), four sides each
    let (mut from, mut to) = (lo, hi);
    for b in &beds {
        let t: Vec<(f64, f64)> = b.iter().map(|&p| turn(p)).collect();
        let deep = |r: Vec<(f64, f64)>, tests: &mut u64| {
            let r = clip(&r, (0.0, o), o * side, tests);
            clip(&r, (0.0, -o), -o * outer, tests)
        };
        let past = deep(
            clip(&clip(&t, (1.0, 0.0), ext.1, tests), (-1.0, 0.0), -hi, tests),
            tests,
        );
        if past.iter().any(|p| p.0 >= hi - 1e-9) {
            to = to.min(past.iter().fold(hi, |a, p| a.min(p.0)));
        }
        let before = deep(
            clip(&clip(&t, (-1.0, 0.0), -ext.0, tests), (1.0, 0.0), lo, tests),
            tests,
        );
        if before.iter().any(|p| p.0 <= lo + 1e-9) {
            from = from.max(before.iter().fold(lo, |a, p| a.max(p.0)));
        }
    }
    // the strip from its outer edge to the face, its ends read off the face
    *tests += f.len() as u64;
    let mut whole = vec![turn((from, outer)), turn((from, face_at(&f, from, tests)))];
    whole.extend(
        f.iter()
            .filter(|p| p.0 > from && p.0 < to)
            .map(|&p| turn(p)),
    );
    whole.push(turn((to, face_at(&f, to, tests))));
    whole.push(turn((to, outer)));
    let mut parts = vec![(boxed(&whole, tests), whole)];
    for b in &beds {
        // a bed whose box misses a piece's box takes nothing from it, asked once a piece
        let bb = b.iter().fold(
            (f64::MAX, f64::MAX, f64::MIN, f64::MIN),
            |(x0, y0, x1, y1), p| (x0.min(p.0), y0.min(p.1), x1.max(p.0), y1.max(p.1)),
        );
        let mut next = Vec::new();
        for (r, ring) in parts {
            *tests += 1;
            if bb.2 < r.0 || bb.0 > r.2 || bb.3 < r.1 || bb.1 > r.3 {
                next.push((r, ring));
                continue;
            }
            for left in difference(&ring, b, tests) {
                next.push((boxed(&left, tests), left));
            }
        }
        parts = next;
    }
    // each piece's span along the axis, a test a corner; the pieces put in order along it, a comparison each
    let mut spans: Vec<(f64, f64, Vec<Pt>)> = parts
        .into_iter()
        .map(|(_, ring)| {
            *tests += ring.len() as u64;
            let (a, b) = ring.iter().fold((f64::MAX, f64::MIN), |(a, b), &q| {
                let t = turn(q).0;
                (a.min(t), b.max(t))
            });
            (a, b, ring)
        })
        .collect();
    spans.sort_by(|x, y| {
        *tests += 1;
        x.0.total_cmp(&y.0)
    });
    out.extend(
        spans
            .into_iter()
            .filter(|&(a, b, _)| b > ext.0 && a < ext.1)
            .map(|(_, _, ring)| ring),
    );
}

/// What the fringe laid: the flanks facing the water, each one's strip cut where a sluice's channel crosses it, and the counters.
#[derive(Debug, Default)]
pub struct Fringe {
    /// The flanks facing the water.
    pub flanks: Vec<char>,
    /// The strips, flank by flank in the order the flanks are asked, a flank's strip in as many pieces as the channels leave it.
    pub strips: Vec<Vec<Pt>>,
    /// The counters (D5).
    pub counts: HashMap<String, u64>,
}

/// The fringe of a polder whose dike's outer face is `dike`, the channels that cross it at its sluices `channels` (each its course
/// and drawn width), the strip `depth` deep, on a `canvas`; nothing where no dike stands.
///
/// Research:
///     reed fringe on the waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a marsh strip off each water-facing flank
///     stopped at each sluice's channel - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: the reeds drawn to the water's edge and kept out of the water itself (`pieces`)
#[must_use]
pub fn fringe(
    dike: &[Pt],
    channels: &[(&[Pt], f64)],
    depth: f64,
    canvas: Pt,
    fall: Pt,
    seat_out: Option<Pt>,
) -> Fringe {
    let mut counts = HashMap::new();
    let pts = dike;
    if pts.is_empty() {
        return Fringe {
            counts,
            ..Fringe::default()
        };
    }
    let (mut x0, mut y0, mut x1, mut y1) = (f64::MAX, f64::MAX, f64::MIN, f64::MIN);
    for p in pts {
        x0 = x0.min(p.0);
        y0 = y0.min(p.1);
        x1 = x1.max(p.0);
        y1 = y1.max(p.1);
    }
    let (ylo, yhi, xlo, xhi) = (
        y0 - RUN_PAST.0,
        y1 + RUN_PAST.1,
        x0 - RUN_PAST.0,
        x1 + RUN_PAST.1,
    );
    let mut tests = 0;
    let fl = flanks(fall, seat_out);
    // the ring boxed (one test a point), each flank asked of the seat's side
    crate::counts::tally(&mut counts, "test@fringe", pts.len() as u64);
    crate::counts::tally(&mut counts, "test@flanks", 3);
    let mut strips = Vec::new();
    for &q in &fl {
        let (outer, lo, hi, ext) = match q {
            'W' => ((x0 - depth).max(-OFF_CANVAS), ylo, yhi, (y0, y1)),
            'E' => ((x1 + depth).min(canvas.0 + OFF_CANVAS), ylo, yhi, (y0, y1)),
            'N' => ((y0 - depth).max(-OFF_CANVAS), xlo, xhi, (x0, x1)),
            _ => ((y1 + depth).min(canvas.1 + OFF_CANVAS), xlo, xhi, (x0, x1)),
        };
        let f = face(pts, (x0, y0, x1, y1), q, lo, hi, &mut tests);
        pieces(
            &f,
            q,
            outer,
            (lo, hi),
            ext,
            channels,
            &mut tests,
            &mut strips,
        );
    }
    crate::counts::tally(
        &mut counts,
        "read@dike",
        pts.len() as u64 + channels.iter().map(|c| c.0.len() as u64).sum::<u64>(),
    );
    crate::counts::tally(&mut counts, "test@face", tests);
    crate::counts::tally(
        &mut counts,
        "write@strip",
        strips.iter().map(Vec::len).sum::<usize>() as u64,
    );
    Fringe {
        flanks: fl,
        strips,
        counts,
    }
}

#[cfg(test)]
mod tests;
