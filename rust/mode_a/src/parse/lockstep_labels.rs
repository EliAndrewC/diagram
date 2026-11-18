//! THE LABELS' COMPARISON (feature 449 T151, step 3a's part A; the GM 2026-11-17: "the resulting maps do NOT need to be bitwise
//! identical"): the four caption-placing pool sheets' captions as the Python's `hand_sheet.placed` seats them and as the port does, in the
//! crate's one end-to-end test (`parse/lockstep.rs`) - each caption's placement on both sides, the distance between them, and how each
//! side's seat stands against the rules the placer seats by ([`standing`]): on the sheet, within the hug, no overlap the placer never
//! draws, a leader exactly where the standard draws one. The test RECORDS the differences and asserts the Rust breaks no rule the Python's
//! seat kept.
//!
//! Each difference is traced to its geometry call: the Python's two shapely calls are logged with their inputs - each multi-part subject's
//! union area (`_covers`) and each leader's tip before and after `leader_to_ink` - and the port's answer on the same inputs measured
//! beside them, so a caption that moved is laid either to one of those calls or to the port (where the test goes red).
//!
//! Research:
//!     the labels' comparison - NONE: the Python and the port compared, deciding nothing about a building

use std::collections::BTreeMap;
use std::path::Path;

use l7r_guard::shared::pyjson::py_float;
use serde_json::{json, Value};

use crate::labels::geom::{dist, Pt};
use crate::labels::hand_sheet::read::View;
use crate::labels::hand_sheet::seat::{captions_of, standing, union_area, SeatedCaption, Standing};
use crate::labels::hand_sheet::{leader_to_ink, placed, read_sheet, seat, Shape, STEPPED};
use crate::labels::placer::{InkPart, Kind, Placement, Subject};

/// The pool sheets whose captions the hand sheet's placer seats (the generators that call `placed`, observed 2026-11-18, method: each
/// pool generator's imports read).
pub const SHEETS: [&str; 4] = [
    "pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg",
    "pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.svg",
    "pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg",
    "pool/magistracies/ubame-magistracy/ubame-magistracy.svg",
];

/// The Python half: `caption_reading(text)`, defined for the parse lockstep's script (its `conv` writes a float as `f:<repr>`), which the
/// script's `one` calls for each of [`SHEETS`] as a task of its own. It wraps the module's `place`, `leader_to_ink`, `_covers` and `seat`
/// for the one run, so the reading is the generator's own `placed(text)`, with each seat's subject and each shapely call's inputs kept.
pub const PYTHON: &str = r#"
def caption_reading(text):
    from l7r.diagram.labels import hand_sheet as H
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    subj, keep, got, covers, raw = {}, [], [], {}, {}
    orig = (H.place, H.leader_to_ink, H._covers, H.seat)
    def place(*a, **k):
        p = orig[0](*a, **k)
        keep.append(p)
        subj[id(p)] = a[2]
        return p
    def ink(p, parts):
        q = orig[1](p, parts)
        keep.append(q)
        subj[id(q)], raw[id(q)] = subj.get(id(p)), p.leader
        return q
    def cover(own, box):
        closed = [s.poly for s in own if not s.line and len(s.poly) >= 3]
        verdict = orig[2](own, box)
        if closed:
            covers[repr(closed)] = {"polys": conv(closed), "area": conv(unary_union([Polygon(c) for c in closed]).area),
                                    "box": conv(H._area(box)), "verdict": verdict}
        return verdict
    def seat(src):
        r = orig[3](src)
        got.append(r)
        return r
    H.place, H.leader_to_ink, H._covers, H.seat = place, ink, cover, seat
    try:
        out = H.placed(text)
    finally:
        H.place, H.leader_to_ink, H._covers, H.seat = orig
    rows = []
    for caps, p, per in got[0]:
        s = subj.get(id(p))
        rows.append({"head": caps[0].at, "x": conv(p.x), "y": conv(p.y), "angle": conv(p.angle), "lines": list(p.lines),
                     "block": conv(p.block), "ring": p.ring, "rank": p.rank, "position": p.position, "cost": conv(p.cost),
                     "leader": conv(p.leader), "raw_leader": conv(raw.get(id(p))), "per": per,
                     "subject": {"kind": s.kind, "poly": conv(s.poly), "angle": conv(s.angle),
                                 "ink": [{"pts": conv(i.pts), "line": i.line, "half": conv(i.half)} for i in s.ink]}})
    return {"rows": rows, "placed": out, "covers": sorted(covers.values(), key=lambda c: repr(c["polys"]))}
"#;

fn f(v: &Value) -> f64 {
    v.as_str()
        .and_then(|s| s.strip_prefix("f:"))
        .and_then(|s| crate::py::float(s).ok())
        .unwrap_or(f64::NAN)
}

fn pt(v: &Value) -> Pt {
    (f(&v[0]), f(&v[1]))
}

fn pts(v: &Value) -> Vec<Pt> {
    v.as_array().into_iter().flatten().map(pt).collect()
}

fn leader(v: &Value) -> Option<(Pt, Pt)> {
    (!v.is_null()).then(|| (pt(&v[0]), pt(&v[1])))
}

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect()
}

/// A Python seat read back as the port's: its placement, its lines and its subject, its texts found by its head's place in the document.
fn python_row(r: &Value, caps: &[Vec<usize>], at_of: &BTreeMap<usize, usize>) -> SeatedCaption {
    let head = r["head"]
        .as_u64()
        .and_then(|a| usize::try_from(a).ok())
        .and_then(|a| at_of.get(&a))
        .copied()
        .unwrap_or(usize::MAX);
    let idx = caps
        .iter()
        .find(|c| c[0] == head)
        .cloned()
        .unwrap_or_default();
    let position = crate::labels::standard::POSITIONS
        .iter()
        .map(|p| p.0)
        .chain(["inside"])
        .find(|p| r["position"] == *p)
        .unwrap_or("?");
    let p = Placement {
        x: f(&r["x"]),
        y: f(&r["y"]),
        angle: f(&r["angle"]),
        lines: strings(&r["lines"]),
        block: pts(&r["block"]),
        ring: r["ring"]
            .as_u64()
            .and_then(|n| usize::try_from(n).ok())
            .unwrap_or(0),
        rank: r["rank"]
            .as_u64()
            .and_then(|n| usize::try_from(n).ok())
            .unwrap_or(0),
        position,
        cost: f(&r["cost"]),
        leader: leader(&r["leader"]),
    };
    let s = &r["subject"];
    let kind = match s["kind"].as_str() {
        Some("area") => Kind::Area,
        Some("line") => Kind::Line,
        _ => Kind::Point,
    };
    let per = r["per"]
        .as_array()
        .into_iter()
        .flatten()
        .map(strings)
        .collect();
    (
        idx,
        p,
        per,
        Subject {
            ink: s["ink"]
                .as_array()
                .into_iter()
                .flatten()
                .map(|i| InkPart {
                    pts: pts(&i["pts"]),
                    line: i["line"].as_bool().unwrap_or(false),
                    half: f(&i["half"]),
                })
                .collect(),
            ..Subject::new(kind, pts(&s["poly"]), f(&s["angle"]))
        },
    )
}

fn same(a: &Placement, b: &Placement) -> bool {
    let bits = |v: f64| v.to_bits();
    let lead = |l: Option<(Pt, Pt)>| l.map(|(p, q)| [p.0, p.1, q.0, q.1].map(bits));
    bits(a.x) == bits(b.x)
        && bits(a.y) == bits(b.y)
        && bits(a.angle) == bits(b.angle)
        && a.lines == b.lines
        && a.block
            .iter()
            .map(|p| (bits(p.0), bits(p.1)))
            .eq(b.block.iter().map(|p| (bits(p.0), bits(p.1))))
        && (a.ring, a.rank, a.position) == (b.ring, b.rank, b.position)
        && bits(a.cost) == bits(b.cost)
        && lead(a.leader) == lead(b.leader)
}

fn seat_json(p: &Placement) -> Value {
    json!({"x": py_float(p.x), "y": py_float(p.y), "lines": p.lines, "ring": p.ring, "rank": p.rank, "position": p.position,
           "cost": py_float(p.cost), "leader": p.leader.map(|(a, b)| [py_float(a.0), py_float(a.1), py_float(b.0), py_float(b.1)])})
}

fn breaks(s: &Standing) -> Vec<&'static str> {
    let mut out = Vec::new();
    if s.off_sheet {
        out.push("off the sheet");
    }
    if s.hug_gap > crate::labels::standard::HUG_PX {
        out.push("past the hug");
    }
    if s.overlap {
        out.push("an overlap");
    }
    if !s.leader_as_ruled {
        out.push("a leader not as ruled");
    }
    out
}

/// The port's half of one sheet: its shapes and view, its captions, its seats and how each stands, and the placed text - computed while
/// the Python's half runs.
pub struct Ours {
    shapes: Vec<Shape>,
    view: View,
    caps: Vec<Vec<usize>>,
    rows: Vec<SeatedCaption>,
    standing: Vec<Standing>,
    placed: String,
}

/// The port's half of one sheet.
///
/// # Panics
/// A pool sheet the port cannot read or seat, which the end-to-end test means to fail on.
#[must_use]
pub fn ours(text: &str) -> Ours {
    let (shapes, view) = read_sheet(text).expect("a pool sheet reads");
    let rows = seat(&shapes, view).expect("a pool sheet seats");
    let caps = captions_of(&shapes).expect("a pool sheet's captions");
    let standing = standing(&shapes, view, &rows).expect("its seats stand");
    let placed = placed(text).expect("a pool sheet places");
    Ours {
        shapes,
        view,
        caps,
        rows,
        standing,
        placed,
    }
}

/// What one sheet's comparison found, for the test's assertions (its full record is [`compare`]'s JSON).
#[derive(Debug, Default)]
pub struct Found {
    pub captions: (usize, usize),
    pub identical: usize,
    pub largest_move: f64,
    /// each rule broken - the caption's row, its words, the rules - by the port's seats, and by the Python's (a sheet repeats a caption's
    /// words, two privies both "latrine", so a seat is matched to the Python's by its row)
    pub rust_breaks: Vec<Broken>,
    pub python_breaks: Vec<Broken>,
    /// the placed sheet's text the same as the Python's, byte for byte
    pub placed_identical: bool,
    pub covers: (usize, usize),
    pub area_difference: f64,
    pub area_margin: f64,
    /// the farthest a leader's tip stands from the Python's, both carried onto the ink from the same leader
    pub tip_difference: f64,
}

/// A caption's seat that breaks a rule: its row in the sheet's captions, its words, and the rules.
pub type Broken = (usize, String, Vec<&'static str>);

/// How far a leader's tip may stand from GEOS's: a round cap drawn as chords stands inside the true circle by `r (1 - cos(pi / 64))`,
/// 0.12% of the half-width - under 0.01 px for every stroke the sheets draw up to 8 px half-width (`leader_to_ink`).
pub const TIP_BOUND: f64 = 0.01;

impl Found {
    /// Do the port's seats keep every rule the Python's kept? Every caption seated on both sides; off the sheet, past the hug and a
    /// leader not as ruled never drawn; an overlap only where the Python's seat of the same caption overlapped too (a caption with no
    /// free seat goes down where it covers the least, 0242); every union's verdict the same, its area's difference under the nearest
    /// margin to the threshold.
    #[must_use]
    pub fn holds(&self) -> bool {
        let theirs: BTreeMap<usize, &Vec<&str>> = self
            .python_breaks
            .iter()
            .map(|(row, _, b)| (*row, b))
            .collect();
        let kept = self.rust_breaks.iter().all(|(row, _, b)| {
            b.as_slice() == ["an overlap"]
                && theirs.get(row).is_some_and(|t| t.contains(&"an overlap"))
        });
        let unions = self.covers.0 == self.covers.1
            && self.area_difference < self.area_margin
            && self.tip_difference < TIP_BOUND;
        self.captions.0 > 0 && self.captions.0 == self.captions.1 && kept && unions
    }

    /// The record's line in the test's report: the captions identical, and each that moved with its distance.
    #[must_use]
    pub fn summary(&self, record: &Value) -> String {
        let moved: Vec<String> = record["moved"]
            .as_array()
            .into_iter()
            .flatten()
            .map(|m| format!("{} {}", m["caption"], m["distance"]))
            .collect();
        let overlaps: Vec<&String> = self.rust_breaks.iter().map(|b| &b.1).collect();
        format!(
            "{} of {} identical, placed text identical {}, moved {moved:?}, overlaps {overlaps:?}",
            self.identical, self.captions.0, self.placed_identical
        )
    }
}

/// One sheet compared: the Python's reading of it against the port's seats. Its record: each caption identical or moved (with both seats
/// and the distance between them), the rules each side's seats break, whether the placed text is the same, and each shapely call's port
/// measured on its own inputs - every union area's difference against its nearest margin to the [`STEPPED`] threshold, every leader tip's
/// distance from the Python's.
///
/// # Panics
/// A Python seat the port's own measures cannot stand, which the end-to-end test means to fail on.
#[must_use]
pub fn compare(path: &Path, ours: &Ours, python: &Value) -> (Value, Found) {
    let Ours {
        shapes,
        view,
        caps,
        rows: rust,
        standing: ours_standing,
        placed,
    } = ours;
    let (shapes, view) = (shapes.as_slice(), *view);
    let at_of: BTreeMap<usize, usize> = shapes.iter().enumerate().map(|(i, s)| (s.at, i)).collect();
    let theirs: Vec<SeatedCaption> = python["rows"]
        .as_array()
        .into_iter()
        .flatten()
        .map(|r| python_row(r, caps, &at_of))
        .collect();
    let theirs_standing = standing(shapes, view, &theirs).expect("its seats stand");
    let mut found = Found {
        captions: (rust.len(), theirs.len()),
        area_margin: f64::INFINITY,
        ..Found::default()
    };
    let (mut moved, mut every) = (Vec::new(), Vec::new());
    for (r, p) in rust.iter().zip(&theirs) {
        let d = dist((r.1.x, r.1.y), (p.1.x, p.1.y));
        let row = json!({"caption": shapes[r.0[0]].text, "identical": same(&r.1, &p.1), "distance": py_float(d), "python": seat_json(&p.1),
                         "rust": seat_json(&r.1), "same_subject": p.3 == r.3});
        found.identical += usize::from(same(&r.1, &p.1));
        found.largest_move = found.largest_move.max(d);
        if !same(&r.1, &p.1) {
            moved.push(row.clone());
        }
        every.push(row);
    }
    // each shapely call's port on the Python's own inputs
    for c in python["covers"].as_array().into_iter().flatten() {
        let polys: Vec<Vec<Pt>> = c["polys"]
            .as_array()
            .into_iter()
            .flatten()
            .map(pts)
            .collect();
        let refs: Vec<&[Pt]> = polys.iter().map(Vec::as_slice).collect();
        let area = union_area(&refs);
        let threshold = STEPPED * f(&c["box"]);
        found.covers.0 += 1;
        found.covers.1 +=
            usize::from((area >= threshold) == c["verdict"].as_bool().unwrap_or(false));
        found.area_difference = found.area_difference.max((area - f(&c["area"])).abs());
        found.area_margin = found.area_margin.min((f(&c["area"]) - threshold).abs());
    }
    let mut tips = (0_usize, 0.0_f64);
    for (r, row) in theirs
        .iter()
        .zip(python["rows"].as_array().into_iter().flatten())
    {
        let Some(raw) = leader(&row["raw_leader"]) else {
            continue;
        };
        let parts: Vec<_> = shapes_of(shapes, &r.0);
        let ink = leader_to_ink(
            Placement {
                leader: Some(raw),
                ..r.1.clone()
            },
            &parts,
        );
        if let (Some(a), Some(b)) = (ink.leader, r.1.leader) {
            tips.0 += 1;
            tips.1 = tips.1.max(dist(a.1, b.1));
        }
    }
    let side = |st: &[Standing], rows: &[SeatedCaption]| -> Vec<Broken> {
        st.iter()
            .zip(rows)
            .enumerate()
            .filter(|(_, (s, _))| !breaks(s).is_empty())
            .map(|(i, (s, r))| (i, shapes[r.0[0]].text.clone(), breaks(s)))
            .collect()
    };
    found.placed_identical = python["placed"].as_str() == Some(placed.as_str());
    (found.rust_breaks, found.python_breaks) =
        (side(ours_standing, rust), side(&theirs_standing, &theirs));
    let record = json!({
        "sheet": path.to_string_lossy(), "captions": rust.len(), "python_captions": theirs.len(), "identical": found.identical,
        "moved": moved, "largest_move": py_float(found.largest_move),
        "placed_identical": found.placed_identical, "every": every,
        "python_breaks": found.python_breaks, "rust_breaks": found.rust_breaks,
        "covers": {"calls": found.covers.0, "verdicts_agree": found.covers.1, "largest_area_difference": py_float(found.area_difference),
                   "least_margin": py_float(found.area_margin)},
        "leader_tips": {"measured": tips.0, "largest_tip_difference": py_float(tips.1)},
    });
    found.tip_difference = tips.1;
    (record, found)
}

/// The shapes a caption names, as the port declared them (the same declaration both sides read).
fn shapes_of<'s>(shapes: &'s [Shape], idx: &[usize]) -> Vec<&'s Shape> {
    let head = idx[0];
    let mut per_group: BTreeMap<usize, usize> = BTreeMap::new();
    for c in captions_of(shapes).unwrap_or_default() {
        *per_group.entry(shapes[c[0]].group).or_default() += 1;
    }
    let alone = per_group.get(&shapes[head].group) == Some(&1);
    crate::labels::hand_sheet::seat::declared_parts(&shapes[head], shapes, alone)
        .unwrap_or_default()
        .into_iter()
        .map(|i| &shapes[i])
        .collect()
}

#[cfg(test)]
mod tests {
    use serde_json::{json, Value};

    use super::{compare, ours};
    use crate::labels::geom::Pt;

    fn f(x: f64) -> Value {
        Value::from(format!("f:{}", l7r_guard::shared::pyjson::py_float(x)))
    }

    fn pts(v: &[Pt]) -> Value {
        Value::from(
            v.iter()
                .map(|p| json!([f(p.0), f(p.1)]))
                .collect::<Vec<_>>(),
        )
    }

    /// A Python reading made of the port's own seats, the first caption carried far off the sheet with a leader it should not have: the
    /// comparison names it moved and every rule it breaks, and the rest identical.
    #[test]
    fn a_seat_that_moved_is_measured_and_its_breaks_named() {
        let held: Value =
            serde_json::from_str(include_str!("../labels/hand_sheet/held.json")).unwrap();
        let text = held[0]["svg"].as_str().unwrap();
        let mine = ours(text);
        let mut rows: Vec<Value> = mine
            .rows
            .iter()
            .map(|(idx, p, per, sub)| {
                let kind = match sub.kind {
                    crate::labels::placer::Kind::Area => "area",
                    _ => "point",
                };
                json!({"head": mine.shapes[idx[0]].at, "x": f(p.x), "y": f(p.y), "angle": f(p.angle), "lines": p.lines,
                       "block": pts(&p.block), "ring": p.ring, "rank": p.rank, "position": p.position, "cost": f(p.cost),
                       "leader": p.leader.map(|(a, b)| pts(&[a, b])), "raw_leader": p.leader.map(|(a, b)| pts(&[a, b])), "per": per,
                       "subject": {"kind": kind, "poly": pts(&sub.poly), "angle": f(sub.angle)}})
            })
            .collect();
        // the first caption seated beside its subject, carried far off
        let k = mine
            .rows
            .iter()
            .position(|r| r.3.kind == crate::labels::placer::Kind::Point)
            .unwrap();
        let far: Vec<Pt> = mine.rows[k]
            .1
            .block
            .iter()
            .map(|p| (p.0 + 900.0, p.1))
            .collect();
        rows[k]["x"] = f(mine.rows[k].1.x + 900.0);
        rows[k]["block"] = pts(&far);
        rows[k]["ring"] = json!(0);
        rows[k]["leader"] = pts(&[(0.0, 0.0), (1.0, 1.0)]);
        let python = json!({"rows": rows, "placed": "", "covers": [{"polys": [pts(&[(0.0, 0.0), (2.0, 0.0), (2.0, 2.0)])], "area": f(2.0),
                            "box": f(4.0), "verdict": false}]});
        let (record, found) = compare(std::path::Path::new("sheet.svg"), &mine, &python);
        assert_eq!(
            (found.captions.0, found.identical + 1),
            (found.captions.1, found.captions.0)
        );
        assert_eq!(record["moved"][0]["distance"], "900.0");
        let first = &mine.shapes[mine.rows[k].0[0]].text;
        let broken = found
            .python_breaks
            .iter()
            .find(|b| &b.1 == first)
            .map(|b| b.2.clone());
        assert_eq!(
            broken,
            Some(vec![
                "off the sheet",
                "past the hug",
                "an overlap",
                "a leader not as ruled"
            ])
        );
        assert_eq!(
            (found.covers, record["placed_identical"].as_bool()),
            ((1, 1), Some(false))
        );
        assert!(found.summary(&record).starts_with(&format!(
            "{} of {} identical, placed text identical false, moved [\"\\\"",
            found.identical, found.captions.0
        )));
        // the port broke nothing the Python kept, but the made-up leader stands far from the tip its ink gives
        assert!(found.tip_difference > super::TIP_BOUND && !found.holds());
    }

    /// A sheet repeats a caption's words: an overlap the port draws on one "latrine" is not excused by the Python's on the other.
    #[test]
    fn an_overlap_is_matched_to_the_python_s_by_its_row_not_its_words() {
        let at = |row: usize| vec![(row, "latrine".to_owned(), vec!["an overlap"])];
        let found = |ours: usize, theirs: usize| super::Found {
            captions: (2, 2),
            rust_breaks: at(ours),
            python_breaks: at(theirs),
            area_margin: 1.0,
            ..super::Found::default()
        };
        assert!(found(1, 1).holds() && !found(0, 1).holds());
    }
}
