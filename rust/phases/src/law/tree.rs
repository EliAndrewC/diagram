//! The access tree drawn as lanes, and the one question asked of each household's way before it is admitted (feature 444 T30):
//! would the tree, the way added as a lane, keep the lane law - the new lane's own ground and its meetings with the lanes near it
//! (`settle/lawful.py` `Lawful.fault`), in the whole tree and in the chain the web draws for it alone; no needle of grass among the
//! tree's lanes or with its ends joined; no farmhouse discharging more than two free ends; its way out crossing each brook at most
//! once; no way beside another past a pitch (`ways/tree.py` `admits`, `laid_run`, `rejoined`, `lane_record`, `hosts`, `chain_of`,
//! `lanes_chain`, `way_out_once`, `records_of`; `tree_base.py` `TreeBase`).
//!
//! Research:
//!     tree keeps the lane law - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way, laid once the last house stands, admitted with no hook, fold, hairpin or dangling end among the tree's lanes
//!     no sliver between the tree's lanes - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined (`as_joined`), two paths side by side are drawn as one (no needle, `needle_loops`), no stub run on past a crossing (no doubled tail)
//!     way out crosses each brook once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
//!     track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub judged at 6 ft, the track out as drawn
//!     square at the water, as laid - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a way crosses the brook or a ditch square, squared where it is laid
//!     a corridor judged as the web will lay it - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way, laid once the last house stands
//!     the record's rounding - NONE: every point at 0.1 ft, as the web draws it
//!     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.2 (floor on sin, a divide-by-zero guard); 1.5 (a point on the tree, the record's rounding room); 60 (the lanes a run is asked to meet, past every joint rule's reach)
#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use super::faces::needles;
use super::ground::LawGround;
use super::meet::{
    along_tail, connector_hairpin_ends, dangling_lane_ends, folded_joint_pairs, foot, needle_ends,
    Destinations, Lane, ALONG,
};
use super::rules::crossing_points;
use super::walk::{as_joined, fronting_counts, tree_shadows, walked_shadows, Steading, JOIN};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::squaring::{square_run, LEG_PAD_FT};
use crate::ways::track::{poly_box, seg_intersect, segments_cross};

/// A household's way's tread, the track out's as judged, how far off its host a way's end is set on its foot, and the pad past
/// the square leg a run is given a vertex at either side of a crossing (ft).
///
/// Research:
///     a drawn corridor's tread - research/questions/0081-village-lanes.drawing.html: a footpath, 3 ft
///     track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub judged at 6 ft
///     a way's end set on its host - GUESS: no source could speak to it, a value of ours; within 20 ft it is carried onto its host's foot
///     the rejoin pad - NONE: past the squaring's elbow pass, so the vertex stands clear of the water - 4 ft
pub const TREE: (f64, f64, f64, f64) = (3.0, 6.0, 20.0, 4.0);

/// How near a point must stand to a run to be on it (ft): the record's rounding room.
pub const ON_TREE_FT: f64 = 1.5;

/// The lanes a run is asked to meet: those whose box comes within this of its box (ft).
pub const MEET_REACH_FT: f64 = 60.0;

fn rounded(run: &[Pt]) -> Vec<Pt> {
    let r = |v: f64| (v * 10.0).round() / 10.0;
    dedup(&run.iter().map(|q| (r(q.0), r(q.1))).collect::<Vec<_>>())
}

fn dedup(run: &[Pt]) -> Vec<Pt> {
    let mut out: Vec<Pt> = Vec::new();
    for &p in run {
        if out.last().is_none_or(|&l| dist(p, l) > 1e-6) {
            out.push(p);
        }
    }
    out
}

fn on(q: Pt, run: &[Pt]) -> bool {
    run.windows(2)
        .any(|w| seg_dist(q, w[0], w[1]) <= ON_TREE_FT)
}

/// `run` with a vertex set either side of each crossing of the water it would be squared at, far enough out to stand clear of it,
/// so the squaring moves the run only about its crossing.
#[must_use]
pub fn rejoined(run: &[Pt], waters: &[(Vec<Pt>, f64)]) -> Vec<Pt> {
    let mut out: Vec<Pt> = run.first().copied().into_iter().collect();
    for w in run.windows(2) {
        let (a, b) = (w[0], w[1]);
        let d = dist(a, b);
        let mut cuts: Vec<f64> = Vec::new();
        for (course, half) in waters {
            for c in course.windows(2) {
                let (c, e) = (c[0], c[1]);
                let Some(x) = (d > 0.0 && dist(c, e) > 0.0 && segments_cross(a, b, c, e))
                    .then(|| seg_intersect(a, b, c, e))
                    .flatten()
                else {
                    continue;
                };
                let sin = (((b.0 - a.0) * (e.1 - c.1) - (b.1 - a.1) * (e.0 - c.0))
                    / (d * dist(c, e)))
                .abs();
                let reach =
                    (half.max(crate::ways::route::BENDS.2 / 2.0 + 1.0) + LEG_PAD_FT + TREE.3)
                        / sin.max(0.2);
                let t = dist(a, x);
                cuts.extend([t - reach, t + reach]);
            }
        }
        cuts.retain(|&c| 0.0 < c && c < d);
        cuts.sort_by(f64::total_cmp);
        out.extend(
            cuts.iter()
                .map(|&t| (a.0 + (b.0 - a.0) * t / d, a.1 + (b.1 - a.1) * t / d)),
        );
        out.push(b);
    }
    dedup(&out)
}

/// A way's end set on its host: where it stands off the host, carried onto the host's foot - its last point moved there within
/// reach, else a leg added to it.
#[must_use]
pub fn carried_onto(mut pts: Vec<Pt>, host: &[Pt]) -> Vec<Pt> {
    let n = pts.len();
    if host.len() < 2 || on(pts[n - 1], host) {
        return pts;
    }
    let q = pts[n - 1];
    let f = host
        .windows(2)
        .map(|w| foot(q, (w[0], w[1])))
        .min_by(|a, b| dist(q, *a).total_cmp(&dist(q, *b)))
        .unwrap_or(q);
    if dist(q, f) <= TREE.2 && n >= 2 && dist(pts[n - 2], f) > 1e-6 {
        pts[n - 1] = f;
    } else {
        pts.push(f);
    }
    rounded(&pts)
}

/// Each run laid, by its points' bits.
type Laid = std::collections::HashMap<Vec<(u64, u64)>, Vec<Pt>>;

/// A household's way in the tree: its run as reserved, its household, its host (-1 the track out) and its lane as drawn.
#[derive(Clone)]
struct Record {
    pts: Vec<Pt>,
    host: i64,
    lane: Lane,
}

/// The access tree: the track out as its root, every household's way admitted, and the ground and destinations the law reads.
pub struct Tree<'a> {
    /// The ground the law reads, the houses and yards seated so far among it.
    pub ground: LawGround,
    /// What a lane's end may reach.
    pub destinations: Destinations,
    /// The farmhouses and their steadings, for the doorstep count.
    pub steadings: Vec<Steading>,
    /// The waters a run is squared against.
    pub waters: &'a [(Vec<Pt>, f64)],
    /// The brooks a way out crosses once.
    pub brooks: &'a [Vec<Pt>],
    root: Vec<Pt>,
    recs: Vec<Record>,
    // each run laid once while the water stands: the judge, the admission and the reservation all lay the same run
    laid_memo: std::cell::RefCell<Laid>,
}

impl<'a> Tree<'a> {
    /// The tree of the track out `root`, on the ground given.
    #[must_use]
    pub fn new(
        root: Vec<Pt>,
        ground: LawGround,
        destinations: Destinations,
        waters: &'a [(Vec<Pt>, f64)],
        brooks: &'a [Vec<Pt>],
    ) -> Self {
        Self {
            ground,
            destinations,
            steadings: Vec::new(),
            waters,
            brooks,
            root,
            recs: Vec::new(),
            laid_memo: std::cell::RefCell::default(),
        }
    }

    /// The run as the web lays it: rejoined either side of its crossings and squared at them.
    #[must_use]
    pub fn laid(&self, run: &[Pt], tests: &mut Counts) -> Vec<Pt> {
        let key: Vec<(u64, u64)> = run.iter().map(|p| (p.0.to_bits(), p.1.to_bits())).collect();
        if let Some(hit) = self.laid_memo.borrow().get(&key) {
            return hit.clone();
        }
        let laid = square_run(&rejoined(run, self.waters), self.waters, tests);
        self.laid_memo.borrow_mut().insert(key, laid.clone());
        laid
    }

    fn stub(&self) -> Lane {
        Lane {
            pts: self.root.clone(),
            w: TREE.1,
            connector: true,
            ..Lane::default()
        }
    }

    /// The host of a run ending at `q`: -1 on the track out, else the earliest way it stands on, else None.
    fn host_of(&self, q: Pt) -> Option<i64> {
        if on(q, &self.root) {
            return Some(-1);
        }
        self.recs
            .iter()
            .position(|r| on(q, &r.pts))
            .map(|k| i64::try_from(k).unwrap_or(-1))
    }

    fn drawn_of(&self, h: i64) -> &[Pt] {
        usize::try_from(h).map_or(&self.root, |k| &self.recs[k].lane.pts)
    }

    /// The lane a run of household `of`, hosted on `h`, is drawn as: laid, rounded, its end set on its host's foot within reach.
    fn lane_for(&self, run: &[Pt], of: Pt, h: i64, tests: &mut Counts) -> Lane {
        let pts = carried_onto(rounded(&self.laid(run, tests)), self.drawn_of(h));
        Lane {
            pts,
            w: TREE.0,
            of: Some(of),
            ..Lane::default()
        }
    }

    /// The first rule the run breaks as a new lane beside `lanes`, by name, or None: its ground half, then its meetings with the
    /// lanes near it - a needle, a fold, the track's hairpin, a dangling end, a doubled tail.
    pub fn fault(
        &self,
        lanes: &[Lane],
        run: &[Pt],
        width: f64,
        owner: Option<Pt>,
        tests: &mut Counts,
    ) -> Option<&'static str> {
        if let Some(why) = self.ground.ground_fault(run, width, owner, tests) {
            return Some(why);
        }
        let rb = poly_box(run);
        let pad = MEET_REACH_FT;
        let mut tl: Vec<Lane> = lanes
            .iter()
            .filter(|l| {
                let b = poly_box(&l.pts);
                l.pts.len() >= 2
                    && !(b.2 < rb.0 - pad
                        || b.0 > rb.2 + pad
                        || b.3 < rb.1 - pad
                        || b.1 > rb.3 + pad)
            })
            .cloned()
            .collect();
        let k = tl.len();
        tl.push(Lane {
            pts: run.to_vec(),
            w: width,
            of: owner,
            ..Lane::default()
        });
        let g = &self.ground;
        let mut blocked = |a: Pt, b: Pt, w: f64| g.blocked(a, b, w, tests);
        if needle_ends(&tl, &mut blocked)
            .iter()
            .any(|n| n.0 == k || n.2 == k)
        {
            return Some("needle_joins");
        }
        if folded_joint_pairs(&tl, &mut blocked)
            .iter()
            .any(|j| j.0 == k || j.2 == k)
        {
            return Some("folded_joints");
        }
        if connector_hairpin_ends(&tl, &mut blocked)
            .iter()
            .any(|h| h.1 == k)
        {
            return Some("connector_hairpins");
        }
        if dangling_lane_ends(&tl, &self.destinations, Some(k))
            .iter()
            .any(|d| d.0 == k)
        {
            return Some("dangling_lane_ends");
        }
        let rev: Vec<Pt> = run.iter().rev().copied().collect();
        let doubled = tl[..k].iter().any(|o| {
            let orev: Vec<Pt> = o.pts.iter().rev().copied().collect();
            [
                (run, &o.pts[..]),
                (&rev[..], &o.pts[..]),
                (&o.pts[..], run),
                (&orev[..], run),
            ]
            .iter()
            .any(|&(p, q)| along_tail(p, q, ALONG.2).is_some())
        });
        doubled.then_some("doubled_tails")
    }

    /// Would the tree, the way `run` of household `of` added, keep the lane law among its lanes?
    pub fn admits(&mut self, run: &[Pt], of: Pt, tests: &mut Counts) -> bool {
        self.refusal(run, of, None, tests).is_none()
    }

    /// The first rule the tree refuses the way `run` of household `of` by, named, or None where it admits it - its threshing yard
    /// `yard` (as the least that will be drawn of it) standing among the steadings a lane's end reaches while it is asked, as
    /// `tree.admits` judges a corridor against its household's records-to-be (`records_of`).
    pub fn refusal(
        &mut self,
        run: &[Pt],
        of: Pt,
        yard: Option<&[Pt]>,
        tests: &mut Counts,
    ) -> Option<&'static str> {
        let owner = self
            .steadings
            .iter()
            .position(|s| dist(s.house.at, of) <= 0.5);
        if let Some(y) = yard {
            self.destinations.steadings.push(y.to_vec());
            if let Some(k) = owner {
                self.steadings[k].parts.push(y.to_vec());
            }
        }
        let why = self.judged(run, of, tests);
        if yard.is_some() {
            self.destinations.steadings.pop();
            if let Some(k) = owner {
                self.steadings[k].parts.pop();
            }
        }
        why
    }

    fn judged(&self, run: &[Pt], of: Pt, tests: &mut Counts) -> Option<&'static str> {
        let run = dedup(run);
        let Some(h) = run
            .last()
            .and_then(|&q| self.host_of(q))
            .filter(|_| run.len() >= 2)
        else {
            return Some("no host");
        };
        let new = self.lane_for(&run, of, h, tests);
        let stub = self.stub();
        let mut chain: Vec<usize> = Vec::new();
        let mut c = h;
        // a host is always reserved before the way it hosts, so the chain runs back to the track out
        while let Ok(k) = usize::try_from(c) {
            chain.push(k);
            c = self.recs[k].host;
        }
        let whole: Vec<Lane> = self
            .recs
            .iter()
            .map(|r| r.lane.clone())
            .chain([new.clone()])
            .collect();
        let mut alone: Vec<Lane> = chain
            .iter()
            .rev()
            .map(|&k| self.recs[k].lane.clone())
            .collect();
        alone.push(new.clone());
        for (lanes, all) in [(&whole, true), (&alone, false)] {
            tests.add("candidate@admits", 1);
            let mut others: Vec<Lane> = lanes[..lanes.len() - 1].to_vec();
            others.push(stub.clone());
            if let Some(why) = self.fault(&others, &new.pts, new.w, Some(of), tests) {
                return Some(why);
            }
            if let Some(why) = all
                .then(|| self.whole_fault(lanes, &stub, &chain, &new, tests))
                .flatten()
            {
                return Some(why);
            }
        }
        None
    }

    /// The whole tree's own rules with the new lane: no needle with the track or with the ends joined, at most two free ends a
    /// farmhouse, the way out across each brook once, no way beside another past a pitch.
    fn whole_fault(
        &self,
        lanes: &[Lane],
        stub: &Lane,
        chain: &[usize],
        new: &Lane,
        tests: &mut Counts,
    ) -> Option<&'static str> {
        let mut trial = lanes.to_vec();
        trial.push(stub.clone());
        let ways: Vec<Vec<Pt>> = trial.iter().map(|l| l.pts.clone()).collect();
        // ...and with every end that stops short carried on, as the web will join it
        let joined: Vec<Vec<Pt>> = as_joined(&self.ground, &trial, lanes.len(), tests)
            .into_iter()
            .map(|l| l.pts)
            .collect();
        if needles(&ways, tests) + needles(&joined, tests) > 0 {
            return Some("needle_loops");
        }
        if fronting_counts(&trial, &self.steadings)
            .iter()
            .any(|&n| n > JOIN.2)
        {
            return Some("doorstep_ends");
        }
        let mut path = new.pts.clone();
        for &k in chain {
            let host = &self.recs[k].lane.pts;
            let q = path[path.len() - 1];
            let m = (0..host.len() - 1)
                .min_by(|&a, &b| {
                    seg_dist(q, host[a], host[a + 1]).total_cmp(&seg_dist(q, host[b], host[b + 1]))
                })
                .unwrap_or(0);
            path.push(foot(q, (host[m], host[m + 1])));
            path.extend(&host[m + 1..]);
        }
        let path = dedup(&path);
        if self
            .brooks
            .iter()
            .any(|b| crossing_points(&path, b, tests).len() > 1)
        {
            return Some("way_out_over_and_back");
        }
        (tree_shadows(
            &lanes.iter().map(|l| l.pts.clone()).collect::<Vec<_>>(),
            tests,
        ) || walked_shadows(lanes, tests))
        .then_some("shadows")
    }

    /// Reserve the admitted way `run` of household `of` in the tree.
    pub fn append(&mut self, run: &[Pt], of: Pt, tests: &mut Counts) {
        let run = dedup(run);
        let h = run.last().and_then(|&q| self.host_of(q)).unwrap_or(-1);
        let lane = self.lane_for(&run, of, h, tests);
        self.recs.push(Record {
            pts: run,
            host: h,
            lane,
        });
    }

    /// The ways drawn, in the order admitted.
    #[must_use]
    pub fn lanes(&self) -> Vec<Lane> {
        self.recs.iter().map(|r| r.lane.clone()).collect()
    }
}
