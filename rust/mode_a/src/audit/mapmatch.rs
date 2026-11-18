//! A sheet on a map matches the map (feature 449 T175, `pack_audit/mapmatch.py` whole; feature 257, spec FR-004; the GM, 2026-09-20: "we
//! shouldn't put any trees or graveyard on the shrine diagram if those are not in correspnding places on the village map").
//!
//! The sheet declares the map ([`super::onmap`]); its RECORDED manifest is read, the sheet's frame and every feature of a corresponding
//! class mapped into map px through the subject's position and the two scales, and disagreement reported in three directions - a sheet
//! feature with no map counterpart within the grain, a map feature in the frame with no sheet counterpart, the subject's footprint per
//! side - and (feature 294 B24) the subject's gate. THE SUBJECT IS A GLYPH ON THE MAP (GM 2026-07-27): what stands inside its footprint
//! is the sheet's own and is not compared.
//!
//! Research:
//!     the map match - NONE: a sheet laid on its declared map within the grains whose claims stand on them, deciding nothing more

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::pyjson::{py_str, truthy};
use serde_json::{Map, Value};

use super::checks::{first_min, main_gate_passage, main_gate_passage_ft, min_of};
use super::onmap::OnMap;
use super::Sheet;
use crate::grids::FTPX;
use crate::parse::{ParsedPlan, Rect};
use crate::py::{fixed, float, hypot};

pub mod features;

pub use features::{features, json_float, load_map, MapFeature, POLYLINE_KEYS};
use features::{get, item};

/// A POSITION is the same feature within this (m:map-grain, research.md R1: the village map's rings step 12-16 px).
///
/// Research:
///     map position grain - NONE: a position matches the same feature within 15 px, an audit matching tolerance.
pub const MAP_GRAIN_PX: f64 = 15.0;
/// A SIDE matches within the map's own resolution: the map records a footprint to the px and a sheet draws it exactly.
///
/// Research:
///     map size grain - NONE: a side matches within 1 px, the map's own resolution.
pub const SIZE_GRAIN_PX: f64 = 1.0;

static VIEWBOX: LazyLock<Regex> =
    LazyLock::new(|| py(r#"viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*""#));

/// THE CORRESPONDENCE CLASSES (contracts/on-map.md): a sheet class, the manifest keys it corresponds to - every key a map records a way
/// under among the lane's (feature 294 B24).
pub const CLASSES: [(&str, &[&str]); 7] = [
    ("tree", &["tree_crowns", "village_groves", "forest_patches"]),
    ("burial_ground", &["cemeteries"]),
    // a well or a purification basin: the map's shrine well IS the shrine's ablution water
    ("water_point", &["wells"]),
    ("arch", &["torii"]),
    ("water", &["streams", "channels", "pond", "crescent_ponds"]),
    ("lane", &["lanes", "lane", "roads", "road", "ring_road"]),
    (
        "building",
        &[
            "houses",
            "byres",
            "farm_sheds",
            "retirement_houses",
            "storehouses",
            "buildings",
        ],
    ),
];
/// The kinds a sheet draws a way under that a map can record (no map records a footpath, measured 2026-10-01).
pub const SHEET_WAY_KINDS: [&str; 1] = ["road"];
/// How the sheet marks each class, by element id (trees are known by their drawing).
pub const SHEET_IDS: [(&str, &str); 7] = [
    ("burial_ground", "burial_ground"),
    ("well", "water_point"),
    ("basin", "water_point"),
    ("arch", "arch"),
    ("water", "water"),
    ("lane", "lane"),
    ("building", "building"),
];

/// A manifest key a sheet might mistake for a class id, less the ids that ARE the class marks.
fn is_stray_key(ident: &str) -> bool {
    CLASSES.iter().any(|(_, keys)| keys.contains(&ident))
        && !SHEET_IDS.iter().any(|(k, _)| *k == ident)
}

/// The skill root a manifest path is read from (`SKILL_ROOT`): an absolute path as it is.
#[must_use]
pub fn manifest_path(on_map: &OnMap, root: &Path) -> PathBuf {
    let p = Path::new(&on_map.manifest);
    if p.is_absolute() {
        p.to_path_buf()
    } else {
        root.join(p)
    }
}

/// Sheet px to map px: sheet px / FTPX = ft; ft / the map's ftpx = map px; origin at the subject's center.
#[derive(Debug, Clone, PartialEq)]
pub struct Transform {
    pub ftpx: f64,
    pub sheet_ox: f64,
    pub sheet_oy: f64,
    pub map_ox: f64,
    pub map_oy: f64,
}

impl Transform {
    #[must_use]
    pub fn to_map(&self, sx: f64, sy: f64) -> (f64, f64) {
        let k = 1.0 / (FTPX * self.ftpx);
        (
            self.map_ox + (sx - self.sheet_ox) * k,
            self.map_oy + (sy - self.sheet_oy) * k,
        )
    }

    /// The sheet's viewBox in map px, None without one.
    ///
    /// Research:
    ///     the sheet's frame on the map - NONE: the viewBox's four numbers carried into map px, deciding nothing about the place
    ///
    /// # Errors
    /// A viewBox number `float()` refuses.
    pub fn frame(&self, text: &str) -> Result<Option<(f64, f64, f64, f64)>, Error> {
        let Some(found) = VIEWBOX.captures(text).ok().flatten() else {
            return Ok(None);
        };
        let (left, top) = (float(&found[1])?, float(&found[2])?);
        let (width, height) = (float(&found[3])?, float(&found[4])?);
        let (x0, y0) = self.to_map(left, top);
        let (x1, y1) = self.to_map(left + width, top + height);
        Ok(Some((x0, y0, x1, y1)))
    }
}

fn center(r: &Rect) -> (f64, f64) {
    (r.x + r.w / 2.0, r.y + r.h / 2.0)
}

/// Every sheet feature of a corresponding class: trees by their drawing, the rest by their declared id.
#[must_use]
pub fn sheet_features(plan: &ParsedPlan) -> Vec<(&'static str, &Rect)> {
    let mut out: Vec<(&str, &Rect)> = plan.trees.iter().map(|t| ("tree", t)).collect();
    for (ident, cls) in SHEET_IDS {
        out.extend(plan.by_id(ident).into_iter().map(|r| (cls, r)));
    }
    out
}

/// The features of every class a manifest records, all of them (`inventory` before its frame).
fn all_features(m: &Value) -> Result<Vec<(&'static str, Vec<MapFeature>)>, Error> {
    let mut out = Vec::new();
    for (cls, keys) in CLASSES {
        let mut found = Vec::new();
        for key in keys {
            found.extend(features(key, cls, get(m, key)?)?);
        }
        out.push((cls, found));
    }
    Ok(out)
}

/// The map's features of every class that lie inside the frame (map px).
///
/// # Errors
/// The manifest cannot be read, or a feature not.
pub fn inventory(
    on_map: &OnMap,
    frame: (f64, f64, f64, f64),
    root: &Path,
) -> Result<Vec<(&'static str, Vec<MapFeature>)>, Error> {
    let m = load_map(&manifest_path(on_map, root))?;
    Ok(all_features(&m)?
        .into_iter()
        .map(|(cls, fs)| (cls, fs.into_iter().filter(|f| f.in_frame(frame)).collect()))
        .collect())
}

/// The subject's footprint on the sheet: the UNION of every rect marked with its id (feature 294 B24 - a walled compound marks each court
/// `precinct`).
#[must_use]
pub fn subject_box(plan: &ParsedPlan, sheet_id: &str) -> Option<Rect> {
    let rects = plan.by_id(sheet_id);
    let first = rects.first()?;
    let x0 = min_of(rects.iter().map(|r| r.x), 0.0);
    let y0 = min_of(rects.iter().map(|r| r.y), 0.0);
    let x1 = super::checks::max_of(rects.iter().map(|r| r.x2()), 0.0);
    let y1 = super::checks::max_of(rects.iter().map(|r| r.y2()), 0.0);
    let mut out = Rect::new(x0, y0, x1 - x0, y1 - y0, &first.fill, first.pos);
    sheet_id.clone_into(&mut out.ident);
    Some(out)
}

fn inside(px: f64, py: f64, r: &Rect) -> bool {
    r.x <= px && px <= r.x2() && r.y <= py && py <= r.y2()
}

/// Every way the sheet draws (a path or line tagged road), as its points in sheet px, each once.
///
/// # Errors
/// The sheet's marks refused.
pub fn sheet_ways(svg: &Sheet) -> Result<Vec<Vec<(f64, f64)>>, Error> {
    let mut out: Vec<Vec<(f64, f64)>> = Vec::new();
    for mk in svg.marks()? {
        if matches!(mk.tag.as_str(), "path" | "line")
            && mk
                .kind
                .as_deref()
                .is_some_and(|k| SHEET_WAY_KINDS.contains(&k))
            && mk.pts.len() >= 2
            && !out.contains(&mk.pts)
        {
            out.push(mk.pts.clone());
        }
    }
    Ok(out)
}

/// The polyline's points with more set between them, none farther apart than `step`.
///
/// # Errors
/// A step's count that is no integer (an infinite or undefined length): Python's `math.ceil` refusal.
pub fn densify(pts: &[(f64, f64)], step: f64) -> Result<Vec<(f64, f64)>, Error> {
    let mut out = vec![pts[0]];
    for w in pts.windows(2) {
        let ((ax, ay), (bx, by)) = (w[0], w[1]);
        let n = crate::py::int(crate::py::round_int(
            (hypot(bx - ax, by - ay) / step).ceil(),
        )?)?
        .max(1);
        #[expect(
            clippy::cast_precision_loss,
            reason = "a step count, far inside f64's integers"
        )]
        let nf = n as f64;
        for i in 1..=n {
            #[expect(
                clippy::cast_precision_loss,
                reason = "a step index, far inside f64's integers"
            )]
            let fi = i as f64;
            out.push((ax + (bx - ax) * fi / nf, ay + (by - ay) * fi / nf));
        }
    }
    Ok(out)
}

/// The side (N, S, E, W) of `b` nearest the point.
#[must_use]
pub fn side_of(px: f64, py: f64, b: &Rect) -> &'static str {
    let sides = [
        ("N", (py - b.y).abs()),
        ("S", (py - b.y2()).abs()),
        ("W", (px - b.x).abs()),
        ("E", (px - b.x2()).abs()),
    ];
    first_min(sides, |s| s.1).map_or("N", |s| s.0)
}

/// The side a record's `gate_dir` names (`_SIDES`), its `str().lower()`.
fn side_named(dir: &str) -> Option<&'static str> {
    match dir {
        "north" | "n" => Some("N"),
        "south" | "s" => Some("S"),
        "east" | "e" => Some("E"),
        "west" | "w" => Some("W"),
        _ => None,
    }
}

/// The records of a manifest list as Python iterated `m.get(key) or []`.
fn records(m: &Value, key: &str) -> Result<Vec<Value>, Error> {
    let empty = Value::Array(Vec::new());
    crate::py::iterate(get(m, key)?.filter(|v| truthy(v)).unwrap_or(&empty))
}

/// The subject's raw record in the manifest (the one whose center lies within the grain of the declaration).
///
/// # Errors
/// The manifest is not a dict, its list not iterable, or a center `float()` refuses.
pub fn subject_record(
    m: &Value,
    on_map: &OnMap,
    grain: f64,
) -> Result<Option<Map<String, Value>>, Error> {
    for rec in records(m, &on_map.key)? {
        if let Value::Object(rec) = rec {
            if rec.contains_key("x") && rec.contains_key("y") {
                let x = json_float(item(&rec, "x")?)?;
                let y = json_float(item(&rec, "y")?)?;
                if hypot(x - on_map.x, y - on_map.y) <= grain {
                    return Ok(Some(rec));
                }
            }
        }
    }
    Ok(None)
}

/// (e) Where the subject's record carries its gate (`gate`, `gate_dir`, `gate_w` - a town's manor records all three), the sheet's main
/// gate passage stands at it within the grain, on the side it names, and as wide within the map's resolution.
///
/// # Errors
/// A gate figure `float()` refuses.
pub fn gate_agrees(
    plan: &ParsedPlan,
    rec: &Map<String, Value>,
    tf: &Transform,
    b: &Rect,
    grain: f64,
) -> Result<Vec<String>, Error> {
    if !["gate", "gate_dir", "gate_w"]
        .iter()
        .any(|k| rec.contains_key(*k))
    {
        return Ok(Vec::new());
    }
    let passage = main_gate_passage(plan);
    let Some(&(px, py)) = passage.first() else {
        return Ok(vec!["the map records the subject's gate, and the sheet draws no `main gate` (tag its posts data-kind=\"main gate\")".to_owned()]);
    };
    let mut out = Vec::new();
    if let Some(Value::Array(gate)) = rec.get("gate") {
        if gate.len() >= 2 {
            let (mx, my) = tf.to_map(px, py);
            let (gx, gy) = (json_float(&gate[0])?, json_float(&gate[1])?);
            let off = hypot(mx - gx, my - gy);
            if off > grain {
                out.push(format!(
                    "the main gate at svg({},{}) = map ({},{}) is {} map px from the map's gate at ({},{})",
                    fixed(px, 0),
                    fixed(py, 0),
                    fixed(mx, 0),
                    fixed(my, 0),
                    fixed(off, 0),
                    fixed(gx, 0),
                    fixed(gy, 0)
                ));
            }
        }
    }
    let dir = rec
        .get("gate_dir")
        .map_or_else(String::new, py_str)
        .to_lowercase();
    let have = side_of(px, py, b);
    if let Some(want) = side_named(&dir) {
        if want != have {
            out.push(format!(
                "the main gate is on the sheet's {have} side; the map faces it {}",
                rec.get("gate_dir").map_or_else(String::new, py_str)
            ));
        }
    }
    let ft = main_gate_passage_ft(plan);
    if let (Some(w), Some(ft)) = (rec.get("gate_w"), ft) {
        let want = json_float(w)? * tf.ftpx;
        if (ft - want).abs() > SIZE_GRAIN_PX * tf.ftpx {
            out.push(format!(
                "the main gate's passage is {} ft on the sheet; the map records it {} ft",
                fixed(ft, 1),
                fixed(want, 1)
            ));
        }
    }
    Ok(out)
}

/// The map's scale, `float(m.get("meta", {}).get("ftpx", 0) or 0)`.
fn scale(m: &Value) -> Result<f64, Error> {
    let empty = Value::Object(Map::new());
    let meta = get(m, "meta")?.unwrap_or(&empty);
    match get(meta, "ftpx")? {
        Some(v) if truthy(v) => json_float(v),
        _ => Ok(0.0),
    }
}

/// The subject's features within the grain of the declaration.
fn subject_features(m: &Value, on_map: &OnMap, grain: f64) -> Result<Vec<MapFeature>, Error> {
    Ok(features(&on_map.key, "subject", get(m, &on_map.key)?)?
        .into_iter()
        .filter(|f| hypot(f.x - on_map.x, f.y - on_map.y) <= grain)
        .collect())
}

/// Python's `max()` of `(offset, px, py)` triples: a tuple compared item by item, the first greatest kept.
fn worst(offs: &[(f64, f64, f64)]) -> Option<(f64, f64, f64)> {
    let mut best: Option<(f64, f64, f64)> = None;
    for &o in offs {
        if best.is_none_or(|b| {
            o.0.partial_cmp(&b.0)
                .unwrap_or(std::cmp::Ordering::Equal)
                .then(o.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
                .then(o.2.partial_cmp(&b.2).unwrap_or(std::cmp::Ordering::Equal))
                .is_gt()
        }) {
            best = Some(o);
        }
    }
    best
}

/// Spec FR-004's three directions and FR-005's refusals, and (feature 294 B24) the subject's gate; an empty list on a sheet with no
/// declaration (the report says "on no map" for it - [`skipped`]). `root` is the skill root a relative manifest is read from.
///
/// # Errors
/// The manifest's JSON, a record's figure or the sheet's marks refused, as the Python raised them.
#[expect(
    clippy::too_many_lines,
    reason = "the Python's one function, its five steps in its order"
)]
pub fn matches_map(
    plan: &ParsedPlan,
    svg: &Sheet,
    on_map: Option<&OnMap>,
    grain: f64,
    root: &Path,
) -> Result<Vec<String>, Error> {
    let Some(on_map) = on_map else {
        return Ok(Vec::new());
    };
    let path = manifest_path(on_map, root);
    if !path.is_file() {
        return Ok(vec![format!(
            "the declared manifest {} cannot be read (no file at {})",
            on_map.manifest,
            path.to_string_lossy()
        )]);
    }
    let m = load_map(&path)?;
    let ftpx = scale(&m)?;
    if ftpx <= 0.0 {
        return Ok(vec![format!(
            "the manifest {} records no scale (meta.ftpx)",
            on_map.manifest
        )]);
    }
    let subject_map = subject_features(&m, on_map, grain)?;
    let Some(home) = subject_map.first() else {
        return Ok(vec![format!(
            "no `{}` feature within {} map px of ({}, {}) in {}",
            on_map.key,
            fixed(grain, 0),
            fixed(on_map.x, 0),
            fixed(on_map.y, 0),
            on_map.manifest
        )]);
    };
    let Some(b) = subject_box(plan, &on_map.sheet_id) else {
        return Ok(vec![format!(
            "no element marked id=\"{}\" on the sheet - the declaration names it as the subject",
            on_map.sheet_id
        )]);
    };
    let mut out = Vec::new();
    let known: Vec<&str> = SHEET_IDS.iter().map(|(k, _)| *k).collect();
    for ident in plan.ids.iter().filter(|i| is_stray_key(i)) {
        out.push(format!(
            "the sheet marks id=\"{ident}\", a manifest key, not a class the check knows - the classes are {}",
            known.join(", ")
        ));
    }
    let (sx, sy) = center(&b);
    let tf = Transform {
        ftpx,
        sheet_ox: sx,
        sheet_oy: sy,
        map_ox: home.x,
        map_oy: home.y,
    };
    let Some(frame) = tf.frame(svg.text)? else {
        out.push("the sheet has no viewBox, so its frame cannot be laid on the map".to_owned());
        return Ok(out);
    };
    // a map feature standing inside the subject's own map footprint is the glyph's, as a sheet feature inside it is
    let inv: Vec<(&str, Vec<MapFeature>)> = inventory(on_map, frame, root)?
        .into_iter()
        .map(|(cls, fs)| {
            (
                cls,
                fs.into_iter()
                    .filter(|f| !f.pts.is_empty() || home.distance(f.x, f.y) > 0.0)
                    .collect(),
            )
        })
        .collect();
    let all_of = all_features(&m)?;
    let of = |cls: &str| -> &[MapFeature] {
        all_of
            .iter()
            .find(|(c, _)| *c == cls)
            .map_or(&[], |(_, fs)| fs.as_slice())
    };
    let sheet: Vec<(&str, &Rect)> = sheet_features(plan)
        .into_iter()
        .filter(|(_, r)| {
            let (cx, cy) = center(r);
            !inside(cx, cy, &b)
        })
        .collect();
    let step = grain * FTPX * ftpx; // a way is sampled at the map's grain, in sheet px
    let mut ways = Vec::new();
    for pts in sheet_ways(svg)? {
        ways.push(
            densify(&pts, step)?
                .into_iter()
                .filter(|&(px, py)| !inside(px, py, &b))
                .collect::<Vec<_>>(),
        );
    }
    // (b) every sheet feature has its map counterpart within the grain
    for (cls, r) in &sheet {
        let (cx, cy) = center(r);
        let (mx, my) = tf.to_map(cx, cy);
        let near = min_of(of(cls).iter().map(|f| f.distance(mx, my)), f64::INFINITY);
        if near > grain {
            let name = cls.replace('_', " ");
            out.push(format!(
                "{name} at svg({},{}) has no {name} on the map within {} map px (map ({},{}))",
                fixed(cx, 0),
                fixed(cy, 0),
                fixed(grain, 0),
                fixed(mx, 0),
                fixed(my, 0)
            ));
        }
    }
    for samples in &ways {
        let offs: Vec<(f64, f64, f64)> = samples
            .iter()
            .map(|&(px, py)| {
                let (mx, my) = tf.to_map(px, py);
                (
                    min_of(of("lane").iter().map(|f| f.distance(mx, my)), f64::INFINITY),
                    px,
                    py,
                )
            })
            .collect();
        if let Some((off, px, py)) = worst(&offs) {
            if off > grain {
                out.push(format!(
                    "the road at svg({},{}) runs {} map px from every way on the map (the grain is {})",
                    fixed(px, 0),
                    fixed(py, 0),
                    fixed(off, 0),
                    fixed(grain, 0)
                ));
            }
        }
    }
    // (c) every map feature inside the frame has its sheet counterpart within the grain
    for (cls, feats) in &inv {
        let mut mine: Vec<(f64, f64)> = sheet
            .iter()
            .filter(|(c, _)| c == cls)
            .map(|(_, r)| {
                let (cx, cy) = center(r);
                tf.to_map(cx, cy)
            })
            .collect();
        if *cls == "lane" {
            mine.extend(ways.iter().flatten().map(|&(px, py)| tf.to_map(px, py)));
        }
        for f in feats {
            if !mine.iter().any(|&(mx, my)| f.distance(mx, my) <= grain) {
                let px = tf.sheet_ox + (f.x - tf.map_ox) * FTPX * ftpx;
                let py = tf.sheet_oy + (f.y - tf.map_oy) * FTPX * ftpx;
                out.push(format!(
                    "the map's {} at map ({},{}) = svg({},{}) is inside the frame and not on the sheet",
                    cls.replace('_', " "),
                    fixed(f.x, 0),
                    fixed(f.y, 0),
                    fixed(px, 0),
                    fixed(py, 0)
                ));
            }
        }
    }
    // (d) the subject's footprint, per side
    let (sw, sh) = (b.w / FTPX, b.h / FTPX);
    let (mw, mh) = (home.w * ftpx, home.h * ftpx);
    if (sw - mw).abs() > SIZE_GRAIN_PX * ftpx || (sh - mh).abs() > SIZE_GRAIN_PX * ftpx {
        out.push(format!(
            "the subject is {} x {} ft on the sheet; the map draws it {} x {} ft",
            fixed(sw, 0),
            fixed(sh, 0),
            fixed(mw, 0),
            fixed(mh, 0)
        ));
    }
    // (e) the subject's gate, where the map records one
    if let Some(rec) = subject_record(&m, on_map, grain)? {
        out.extend(gate_agrees(plan, &rec, &tf, &b, grain)?);
    }
    Ok(out)
}

/// Which correspondence classes the declared map shows inside the sheet's frame - what the program check asks a SITE item against; None
/// when the sheet declares no map or the declaration cannot be laid on it (then [`matches_map`] names why).
///
/// # Errors
/// The manifest's JSON or a record's figure refused, as the Python raised them.
pub fn site_classes(
    plan: &ParsedPlan,
    svg: &Sheet,
    on_map: Option<&OnMap>,
    root: &Path,
) -> Result<Option<Vec<(String, bool)>>, Error> {
    let Some(on_map) = on_map else {
        return Ok(None);
    };
    let path = manifest_path(on_map, root);
    if !path.is_file() {
        return Ok(None);
    }
    let m = load_map(&path)?;
    let ftpx = scale(&m)?;
    let subject_map = subject_features(&m, on_map, MAP_GRAIN_PX)?;
    let subject = subject_box(plan, &on_map.sheet_id);
    let (Some(home), Some(subject)) = (subject_map.first(), subject) else {
        return Ok(None);
    };
    if ftpx <= 0.0 {
        return Ok(None);
    }
    let (sx, sy) = center(&subject);
    let tf = Transform {
        ftpx,
        sheet_ox: sx,
        sheet_oy: sy,
        map_ox: home.x,
        map_oy: home.y,
    };
    let Some(frame) = tf.frame(svg.text)? else {
        return Ok(None);
    };
    Ok(Some(
        inventory(on_map, frame, root)?
            .into_iter()
            .map(|(cls, fs)| (cls.to_owned(), !fs.is_empty()))
            .collect(),
    ))
}

/// The trees a settlement manifest lives in, from the skill root.
pub const MAP_TREES: [&str; 2] = ["pool", "legacy-hand-authored-pool"];

/// The manifests (paths from `root`) that record a subject of the sheet's tier at the sheet's PLACE - the name convention
/// `<place>-<type>` (`ubame-magistracy` -> `ubame`), matched to a map folder `<tree>/<tier>/<place>/<place>.json` whose tier key
/// (`map_keys`, `types.json`) is a non-empty list. The name convention is a GUESS (the scout's, feature 294).
///
/// # Errors
/// The declaration or a manifest cannot be read.
pub fn maps_recording(stem: &str, tier: &str, root: &Path) -> Result<Vec<String>, Error> {
    let place = stem.split('-').next().unwrap_or_default();
    let keys = crate::types::by_tier(tier, root)?
        .map(|t| t.map_keys)
        .unwrap_or_default();
    let mut out = Vec::new();
    for tree in MAP_TREES {
        let base = root.join(tree);
        if !base.is_dir() {
            continue;
        }
        let mut tiers: Vec<String> = std::fs::read_dir(&base)
            .map_err(|e| crate::py::os_error(&e, &base.to_string_lossy()))?
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .collect();
        tiers.sort();
        for map_tier in tiers {
            let rel = format!("{tree}/{map_tier}/{place}/{place}.json");
            let path = root.join(&rel);
            if !path.is_file() {
                continue;
            }
            let mut recorded = false;
            for k in &keys {
                let m = load_map(&path)?;
                if matches!(get(&m, k)?, Some(Value::Array(items)) if !items.is_empty()) {
                    recorded = true;
                    break;
                }
            }
            if recorded {
                out.push(rel);
            }
        }
    }
    Ok(out)
}

/// Why the check did not run: the report's line for a sheet on no map.
#[must_use]
pub fn skipped(on_map: Option<&OnMap>) -> Option<&'static str> {
    on_map
        .is_none()
        .then_some("on no map (no `**On map**:` line in the notes)")
}

#[cfg(test)]
mod tests {
    use super::{features, json_float, load_map, side_named, side_of};
    use crate::parse::Rect;
    use serde_json::json;

    #[test]
    fn a_side_is_named_and_found_as_the_python_s() {
        let named = ["north", "n", "south", "s", "east", "e", "west", "w", "up"].map(side_named);
        assert_eq!(
            named,
            [
                Some("N"),
                Some("N"),
                Some("S"),
                Some("S"),
                Some("E"),
                Some("E"),
                Some("W"),
                Some("W"),
                None
            ]
        );
        let b = Rect::new(0.0, 0.0, 10.0, 10.0, "", -1);
        assert_eq!(
            [
                side_of(5.0, 9.0, &b),
                side_of(1.0, 5.0, &b),
                side_of(9.0, 5.0, &b)
            ],
            ["S", "W", "E"]
        );
    }

    #[test]
    fn a_manifest_is_read_as_json_load_reads_it() {
        let dir = l7r_guard::shared::tempdir::TempDir::new("mode-a-mapmatch");
        // a folder is no file, and a file that is not JSON is the decoder's refusal (its words the library's)
        assert_eq!(load_map(dir.path()).unwrap_err().kind, "IsADirectoryError");
        std::fs::write(dir.path().join("bad.json"), "{").unwrap();
        assert_eq!(
            load_map(&dir.path().join("bad.json")).unwrap_err().kind,
            "json.decoder.JSONDecodeError"
        );
        let kinds: Vec<&str> = [json!(true), json!("x"), json!([1])]
            .iter()
            .map(|v| json_float(v).map_or_else(|e| e.kind, |_| "ok"))
            .collect();
        assert_eq!(kinds, ["ok", "ValueError", "TypeError"]);
        // a manifest list that is not a list has no features
        assert!(features("wells", "water_point", Some(&json!({"x": 1})))
            .unwrap()
            .is_empty());
    }

    #[test]
    fn a_tree_with_no_legacy_pool_and_an_unreadable_pool_are_read_as_the_python_s() {
        use std::os::unix::fs::PermissionsExt as _;
        let dir = l7r_guard::shared::tempdir::TempDir::new("mode-a-maps");
        let root = dir.path();
        let decl = "l7r/diagram/buildings/types.json";
        let real = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        std::fs::create_dir_all(root.join("l7r/diagram/buildings")).unwrap();
        std::fs::copy(real.join(decl), root.join(decl)).unwrap();
        std::fs::create_dir_all(root.join("pool/towns")).unwrap();
        assert!(super::maps_recording("ubame-x", "magistracies", root)
            .unwrap()
            .is_empty());
        std::fs::set_permissions(root.join("pool"), std::fs::Permissions::from_mode(0o000))
            .unwrap();
        let refused = super::maps_recording("ubame-x", "magistracies", root);
        std::fs::set_permissions(root.join("pool"), std::fs::Permissions::from_mode(0o755))
            .unwrap();
        assert_eq!(refused.unwrap_err().kind, "PermissionError");
    }
}
