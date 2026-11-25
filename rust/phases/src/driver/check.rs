//! The finished map's checks (feature 444 T42; the GM 2026-11-07: "focus entirely on our Rust code ... until our Rust is solid"):
//! what a stage drew read back against the rules its research keeps, so the cohort finds a stage that draws a thing wrong, not
//! only one that refuses. Each check names what it found; none moves anything.
//!
//! Research:
//!     the map's checks - NONE: read-only, each rule's claim at the Rust that keeps it while laying

use super::Rolled;
use crate::field::dry::seg_seg_dist;
use crate::field::fan::Pt;
use crate::field::geom::{inside, seg_dist};
use crate::field::index::{bbox, Index};

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

/// The plot `poly` drawn in by `by` feet on every side, or the plot itself where it is under two of `by` across (a side of the
/// drawn-in ring turning back on its own), so a small plot is asked exactly.
///
/// Research:
///     the plot drawn in - NONE: geometry, each side's line moved in and its neighbors' lines met
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn drawn_in(poly: &[Pt], by: f64) -> Vec<Pt> {
    let n = poly.len();
    let sense = crate::field::geom::signed_area(poly).signum();
    // each side's line moved in: a point on it and its direction
    let lines: Vec<(Pt, Pt)> = (0..n)
        .map(|i| {
            let (a, b) = (poly[i], poly[(i + 1) % n]);
            let len = (b.0 - a.0).hypot(b.1 - a.1).max(f64::MIN_POSITIVE);
            let u = ((b.0 - a.0) / len, (b.1 - a.1) / len);
            // the inward normal on the ring's own turning
            let inward = (-u.1 * sense, u.0 * sense);
            ((a.0 + inward.0 * by, a.1 + inward.1 * by), u)
        })
        .collect();
    let corner = |i: usize| {
        let ((p, u), (q, v)) = (lines[(i + n - 1) % n], lines[i]);
        let cross = u.0 * v.1 - u.1 * v.0;
        if cross.abs() < 1e-9 {
            return q;
        }
        let t = ((q.0 - p.0) * v.1 - (q.1 - p.1) * v.0) / cross;
        (p.0 + u.0 * t, p.1 + u.1 * t)
    };
    let inner: Vec<Pt> = (0..n).map(corner).collect();
    let kept = (0..n).all(|i| {
        let (a, b) = (inner[i], inner[(i + 1) % n]);
        (b.0 - a.0) * lines[i].1 .0 + (b.1 - a.1) * lines[i].1 .1 > 0.0
    });
    if kept {
        inner
    } else {
        poly.to_vec()
    }
}

/// Where the ring `ring` lies over the dry plot `poly` past the drawing's slack, or `None`: a corner of the plot more than the
/// slack inside the ring, or the plot drawn in by the slack meeting it - a corner of the drawn-in plot inside the ring, or a side
/// of the ring ending inside the drawn-in plot or crossing its sides. So the plot's whole area is asked, not its corners alone,
/// and a ring sharing an edge with it within the slack is not named.
///
/// Research:
///     the plot's whole area asked - CONVENTION: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html states no gap between a dry plot and the rice, the houses' ground or the pond's, so exact overlap past the drawing's slack (`SLACK_FT`), a shared edge not an overlap (449 T434)
fn lies_over(poly: &[Pt], ring: &[Pt]) -> Option<Pt> {
    if ring.len() < 3 || poly.len() < 3 {
        return None;
    }
    if let Some(p) = poly.iter().find(|p| depth_inside(**p, ring) > SLACK_FT) {
        return Some(*p);
    }
    let inner = drawn_in(poly, SLACK_FT);
    if let Some(p) = inner.iter().find(|p| inside(**p, ring)) {
        return Some(*p);
    }
    let m = inner.len();
    (0..ring.len())
        .map(|i| (ring[i], ring[(i + 1) % ring.len()]))
        .find(|&(a, b)| {
            inside(a, &inner)
                || (0..m).any(|k| seg_seg_dist(a, b, inner[k], inner[(k + 1) % m]) == 0.0)
        })
        .map(|(a, b)| if inside(a, &inner) { a } else { mean(&[a, b]) })
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

/// Whether two boxes (low corner, high corner) meet or come within the drawing's slack: two plots whose boxes stand farther apart
/// cannot lie over each other, so `lies_over` is not asked of them.
///
/// Research:
///     the boxes - NONE: a check's lookup
fn boxes_meet(a: (Pt, Pt), b: (Pt, Pt)) -> bool {
    a.0 .0 <= b.1 .0 + SLACK_FT
        && b.0 .0 <= a.1 .0 + SLACK_FT
        && a.0 .1 <= b.1 .1 + SLACK_FT
        && b.0 .1 <= a.1 .1 + SLACK_FT
}

/// Where the field `ring` lies over the settlement's band (the houses' ground the seat chose, `frame`'s), or `None`: the band
/// asked whole by `lies_over`, its near edge, on the field's side, drawn back by the seat's own `FIELD_IN_BAND_MAX` of its depth
/// first - the dip a straight band along a bending field edge is let make into the paddy (449 T435).
///
/// Research:
///     the band's whole area asked - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the cluster beside its paddy, on the higher, drier ground - so no part of the houses' band lies over the field past the dip the seat allows a straight band along a bending margin (`seat::margins::FIELD_IN_BAND_MAX`, a tenth of its depth, a GUESS), the drawing's slack beyond it; the page gives no gap between the houses and the paddy (449 T435)
fn on_band(frame: &crate::seat::Frame, ring: &[Pt]) -> Option<Pt> {
    let (l, o, (lat, half), c) = (frame.along, frame.out, frame.band, frame.center);
    let near = half - crate::seat::margins::FIELD_IN_BAND_MAX * 2.0 * half;
    let at = |s: f64, t: f64| (c.0 + l.0 * s + o.0 * t, c.1 + l.1 * s + o.1 * t);
    let band = [
        at(-lat, -near),
        at(lat, -near),
        at(lat, half),
        at(-lat, half),
    ];
    lies_over(&band, ring)
}

/// Why the dry plot `poly` is not a plot's size, or `None`: its inner edge (`poly[0]`-`poly[1]`, on the canal's side) or its outer
/// edge (`poly[3]`-`poly[2]`) running past `STRETCH_SHARE` of a plot's length or under `PINCH_SHARE` of it - the hem's two bounds
/// on a strip, the stretch it cuts past and the pinch it ends a climb under (449 T435).
///
/// Research:
///     a plot's size held - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html draws each plot roughly 92 ft across (`PLOT_FT`), never dwarfing the rice basins, and a strip's edge never under half a plot's length; the page is silent on how far past a plot's length a strip may run, so the bound is the hem's own `STRETCH_SHARE` (1.5 plots), a GUESS, and the pinch's `PINCH_SHARE` (half a plot), the page's GUESS - each edge's straight length, within a hundredth of a foot
///     a plot's four corners - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each plot "a rectangle square to the canal where it stands (at a bend they taper)" - so a dry plot of any corner count but four is named a size break (449 T435)
fn sized(poly: &[Pt]) -> Option<String> {
    use crate::field::dry::{PINCH_SHARE, PLOT_FT, STRETCH_SHARE};
    if poly.len() != 4 {
        return Some(format!("{} corners are not a strip's four", poly.len()));
    }
    let run = |p: Pt, q: Pt| (q.0 - p.0).hypot(q.1 - p.1);
    let (lo, hi) = (
        PINCH_SHARE * PLOT_FT.0 - SIZE_EPS_FT,
        STRETCH_SHARE * PLOT_FT.0 + SIZE_EPS_FT,
    );
    [
        ("inner", run(poly[0], poly[1])),
        ("outer", run(poly[3], poly[2])),
    ]
    .into_iter()
    .find(|(_, ft)| !(lo..=hi).contains(ft))
    .map(|(edge, ft)| {
        format!(
            "{edge} edge runs {ft:.1} ft, {:.2} plots' length, outside the {PINCH_SHARE} to {STRETCH_SHARE} a plot is drawn at",
            ft / PLOT_FT.0
        )
    })
}

/// How far an edge's length may stand past a size bound and still be held to it (ft): the float arithmetic of a strip's corners.
///
/// Research:
///     the size's grain - NONE: a check's tolerance, a hundredth of a foot
const SIZE_EPS_FT: f64 = 0.01;

/// The ellipse at `c` with radii `rx`, `ry` as a ring of `n` points, the first on the long radius's east end.
///
/// Research:
///     the ellipse's ring - NONE: geometry
fn ellipse(c: Pt, rx: f64, ry: f64, n: u32) -> Vec<Pt> {
    (0..n)
        .map(|k| f64::from(k) * std::f64::consts::TAU / f64::from(n))
        .map(|a| (c.0 + rx * a.cos(), c.1 + ry * a.sin()))
        .collect()
}

/// How many points the tameike's water is asked at against the field, round its ellipse.
///
/// Research:
///     the pond's points - NONE: a check's grain, a 64-sided ring within about a thousandth of its radius of the ellipse (under the drawing's slack for any pond whose long radius is under 800 ft), its every fourth point the old 16-point rim's
const POND_AREA_POINTS: u32 = 64;

/// How many points the tameike's rim is filed at, round its ellipse.
///
/// Research:
///     the rim's points - NONE: a check's grain, a 32-sided rim within about a hundredth of its radius of the ellipse
const RIM_POINTS: u32 = 32;

/// The water the map draws, filed once in the water index at each line's drawn width, with what each segment is, and the ponds:
/// asked of each dry plot (449 T433).
///
/// Research:
///     the drawn water - NONE: the check's lookup; what it keeps a plot off is `Drawn::of`'s and `Drawn::meets`'
struct Drawn {
    ix: Index,
    what: Vec<&'static str>,
    ponds: Vec<(Pt, f64, f64)>,
}

impl Drawn {
    /// The field's channels as drawn, the drawn brook, the drain's run and the tameike's rim.
    ///
    /// Research:
    ///     the water a plot is kept off - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: any water the map draws - a canal, its own canal where it bends, a ditch, the brook or a pond - each line at its drawn width (a ditch at the wider of its two ends), the pond's rim at its stroke; a polder's water is not filed, since a polder lays no dry plot (`driver::polder`)
    fn of(r: &Rolled) -> Self {
        let mut d = Self {
            ix: Index::default(),
            what: Vec::new(),
            ponds: Vec::new(),
        };
        let mut file = |line: &[Pt], w: f64, what: &'static str| {
            for s in line.windows(2) {
                d.ix.file_w(s[0], s[1], w);
                d.what.push(what);
            }
        };
        for c in r.fields.iter().flat_map(|f| &f.channels) {
            let what = match c.role {
                "main" => "a canal",
                "drain" => "the field's drain",
                _ => "a ditch",
            };
            file(&c.pts, c.w.max(c.w_tail), what);
        }
        for b in &r.brooks {
            file(b, super::BROOK_W, "the brook");
        }
        if let Some(s) = &r.sunk {
            file(&s.run, super::RUN_W, "the drain's run");
        }
        for (c, rx, ry) in r.sunk.iter().filter_map(|s| s.pond) {
            let rim: Vec<Pt> = (0..=RIM_POINTS)
                .map(|k| f64::from(k) * std::f64::consts::TAU / f64::from(RIM_POINTS))
                .map(|a| (c.0 + rx * a.cos(), c.1 + ry * a.sin()))
                .collect();
            file(&rim, super::POND_RIM_W, "the pond");
            d.ponds.push((c, rx, ry));
        }
        d
    }

    /// Why the plot `poly` stands on the water, or `None`: a line reaching inside it, a line within the hem's clearance past its
    /// half-width of a side (crossing it, at zero), or a corner in a pond.
    ///
    /// Research:
    ///     the plot's whole area asked - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would come within about a foot of any water the map draws, or would have the end of one inside it, is left out - so its whole area is asked, the hem's `CLEAR_FT` past each line's half-width, not its corners alone
    fn meets(&mut self, poly: &[Pt]) -> Option<String> {
        let clear = crate::hem::CLEAR_FT;
        let reach = clear + self.ix.widest / 2.0;
        let lo = poly
            .iter()
            .fold((f64::MAX, f64::MAX), |m, p| (m.0.min(p.0), m.1.min(p.1)));
        let hi = poly
            .iter()
            .fold((f64::MIN, f64::MIN), |m, p| (m.0.max(p.0), m.1.max(p.1)));
        for i in self
            .ix
            .near((lo.0 - reach, lo.1 - reach), (hi.0 + reach, hi.1 + reach))
        {
            let ((a, b), half) = (self.ix.segs[i], self.ix.widths[i] / 2.0);
            if let Some(p) = [a, b].into_iter().find(|p| inside(*p, poly)) {
                return Some(format!(
                    "has {} reaching inside it at ({:.0}, {:.0})",
                    self.what[i], p.0, p.1
                ));
            }
            let gap = (0..poly.len())
                .map(|k| seg_seg_dist(a, b, poly[k], poly[(k + 1) % poly.len()]))
                .fold(f64::MAX, f64::min);
            if gap < clear + half {
                return Some(format!(
                    "comes {:.1} ft from the edge of {} near ({:.0}, {:.0}), inside the {clear} ft kept clear",
                    gap - half,
                    self.what[i],
                    a.0,
                    a.1
                ));
            }
        }
        let ellipse = |p: &Pt, &(c, rx, ry): &(Pt, f64, f64)| {
            ((p.0 - c.0) / rx).powi(2) + ((p.1 - c.1) / ry).powi(2) < 1.0
        };
        poly.iter()
            .find(|p| self.ponds.iter().any(|e| ellipse(p, e)))
            .map(|p| format!("stands in the pond at ({:.0}, {:.0})", p.0, p.1))
    }
}

/// The rolled hamlet's violations, each a line naming the rule, what broke it and where; none on a sound map.
///
/// Research:
///     no dry plot on the paddy - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry fields stand beyond the paddy, along the canal's high side, and a plot that would lap onto the rice is dropped - so the plot's whole area is asked of the field past the drawing's slack (`lies_over`), not its corners (449 T434)
///     no dry plot on the water - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot that would come within about a foot of any water the map draws - a canal, a ditch, the brook or a pond - or would have the end of one inside it, is left out; the plot's whole area asked of the drawn water (`Drawn::meets`), not its corners (449 T433)
///     no dry plot on another - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: plots laid end to end, each its own ground, neighbors abutting - so a plot's whole area is asked of every other past the drawing's slack (`lies_over`), a shared edge not a lap, not its middle alone (449 T435)
///     no dry plot past a plot's size - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each plot roughly 92 ft across, never dwarfing the rice basins - each plot's two edges along the canal between the hem's pinch and stretch (`sized`, 449 T435)
///     the tameike off the paddy - research/questions/0060-field-drains-akusuiro.drawing.html: the pond at the field's foot, below it - its whole water asked of the field past the drawing's slack (`lies_over` on a 64-point ring), not sixteen points of its rim (449 T435)
///     the settlement off the field - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the houses on the field's margin, beside the paddy - the houses' whole band asked (`on_band`), not its middle (449 T435)
///     on the canvas - CONVENTION: the map is drawn on its canvas; only the brook and the drain's run leave it
#[must_use]
pub fn check(r: &Rolled) -> Vec<String> {
    let mut out = Vec::new();
    let (w, h) = (r.plan.w, r.plan.h);
    let off = |p: &Pt| p.0 < 0.0 || p.1 < 0.0 || p.0 > w || p.1 > h;
    let rings: Vec<&[Pt]> = r.fields.iter().map(|f| f.fan.ring.as_slice()).collect();
    let mut water = Drawn::of(r);
    let boxes: Vec<(Pt, Pt)> = r.dry.iter().map(|d| bbox(&d.poly)).collect();
    for (i, d) in r.dry.iter().enumerate() {
        if let Some(p) = rings.iter().find_map(|ring| lies_over(&d.poly, ring)) {
            out.push(format!(
                "dry_on_paddy: dry plot {i} lies over the field near ({:.0}, {:.0})",
                p.0, p.1
            ));
        }
        out.extend(
            water
                .meets(&d.poly)
                .map(|why| format!("dry_on_water: dry plot {i} {why}")),
        );
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
        } else if let Some((j, p)) = r
            .dry
            .iter()
            .enumerate()
            .skip(i + 1)
            .filter(|(j, _)| boxes_meet(boxes[i], boxes[*j]))
            .find_map(|(j, e)| lies_over(&d.poly, &e.poly).map(|p| (j, p)))
        {
            out.push(format!(
                "dry_on_dry: dry plot {i} lies over dry plot {j} near ({:.0}, {:.0})",
                p.0, p.1
            ));
        }
        out.extend(sized(&d.poly).map(|why| format!("dry_size: dry plot {i}'s {why}")));
        if d.poly.iter().any(off) {
            out.push(format!("off_canvas: dry plot {i}"));
        }
    }
    for (c, rx, ry) in r.sunk.iter().filter_map(|s| s.pond) {
        let rim: Vec<Pt> = (0..16)
            .map(|k| f64::from(k) * std::f64::consts::PI / 8.0)
            .map(|a| (c.0 + rx * a.cos(), c.1 + ry * a.sin()))
            .collect();
        let water = ellipse(c, rx, ry, POND_AREA_POINTS);
        let reaches = rings
            .iter()
            .any(|ring| depth_inside(c, ring) > SLACK_FT || lies_over(&water, ring).is_some());
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
        out.extend(rings.iter().find_map(|ring| on_band(f, ring)).map(|p| {
            format!(
                "seat_on_field: the settlement's band lies over the field near ({:.0}, {:.0})",
                p.0, p.1
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
///     no dry plot in the reeds - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry fields drawn on the higher, drier ground along the paddy's high edge, where the paddy water stops - so none on the reed bed round the tameike at the field's foot; the plot's whole area asked of the reeds' ring past the drawing's slack (`lies_over`), not its corners (449 T434)
///     no dry plot on the settlement's ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields, so no plot stands where they do (`dry_on_settlement`); the plot's whole area asked of the ground past the drawing's slack (`lies_over`), not its corners (449 T434)
fn reed_checks(r: &Rolled) -> Vec<String> {
    let ground: Vec<Vec<Pt>> = r
        .seated
        .iter()
        .filter_map(|s| s.frames.first())
        .map(|f| super::settlement_ground(f, super::wind(&r.plan.windward)))
        .collect();
    let on_ground = r.dry.iter().enumerate().filter_map(|(i, d)| {
        ground
            .iter()
            .find_map(|g| lies_over(&d.poly, g))
            .map(|p| {
                format!(
                    "dry_on_settlement: dry plot {i} lies over the settlement's ground near ({:.0}, {:.0})",
                    p.0, p.1
                )
            })
    });
    r.sunk
        .iter()
        .filter_map(|s| {
            r.dry
                .iter()
                .enumerate()
                .find_map(|(i, d)| lies_over(&d.poly, &s.reeds).map(|p| (i, p)))
        })
        .map(|(i, p)| {
            format!(
                "reeds_on_dry: dry plot {i} lies over the tameike's reeds near ({:.0}, {:.0})",
                p.0, p.1
            )
        })
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
///     the polder's checks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the reeds outside the dike on the flanks that face the water, the settlement on the block's dry shore - each strip's and the houses' band's whole area asked of the block past the drawing's slack (`lies_over`, `on_band`), not their middles (449 T435)
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
        out.extend(on_band(f, block).map(|p| {
            format!(
                "seat_on_field: the settlement's band lies over the polder near ({:.0}, {:.0})",
                p.0, p.1
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
        if depth_inside(mean(strip), block) > SLACK_FT {
            out.push(format!(
                "reeds_on_field: waterside strip {i}'s middle stands inside the polder"
            ));
        } else if let Some(p) = lies_over(block, strip) {
            out.push(format!(
                "reeds_on_field: waterside strip {i} lies over the polder near ({:.0}, {:.0})",
                p.0, p.1
            ));
        }
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
mod tests;
