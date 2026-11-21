//! A settlement map's recorded features as the map check reads them (feature 449 T175, `mapmatch.py`'s `MapFeature`, `_pairs`,
//! `_features` and `load_map`): each manifest list in map px, as a point, a circle, a rect or a line, in the shapes research.md R2 names -
//! read from the JSON as Python's `json.load` made it, so a `float()` of a string or a bool, a missing key and a value of the wrong type
//! fail or pass as they did.
//!
//! Research:
//!     the map's features - NONE: a recorded manifest read into shapes, deciding nothing about a building

use std::path::Path;

use l7r_gate_research::Error;
use l7r_shared::pyjson::truthy;
use serde_json::{Map, Value};

use crate::audit::checks::min_of;
use crate::py::{hypot, max, min};

/// The mark `pyjson::loads` keeps a number `serde_json` cannot hold under (an integer past 64 bits, a NaN, an infinity).
const KEPT: char = '\u{10FE00}';

/// Python's `float()` of what `json.load` made of a value.
///
/// # Errors
/// `float()`'s `ValueError` for a string it cannot read, its `TypeError` for `None`, a list or a dict.
pub fn json_float(v: &Value) -> Result<f64, Error> {
    match v {
        Value::Bool(b) => Ok(f64::from(u8::from(*b))),
        Value::Number(n) => Ok(n.as_f64().unwrap_or(0.0)),
        Value::String(s) => match s.strip_prefix(KEPT) {
            Some(number) => Ok(number.parse().unwrap_or(f64::NAN)),
            None => crate::py::float(s),
        },
        other => Err(Error::new(
            "TypeError",
            format!(
                "float() argument must be a string or a real number, not '{}'",
                crate::py::type_name(other)
            ),
        )),
    }
}

/// `rec[key]`, the Python's `KeyError` where it is missing.
///
/// # Errors
/// The key is not there.
pub fn item<'v>(rec: &'v Map<String, Value>, key: &str) -> Result<&'v Value, Error> {
    rec.get(key).ok_or_else(|| Error::new("KeyError", key))
}

/// `float(rec.get(key, 0.0))`.
fn float_or_zero(rec: &Map<String, Value>, key: &str) -> Result<f64, Error> {
    rec.get(key).map_or(Ok(0.0), json_float)
}

/// One recorded map feature in map px: a point (`r` 0), a circle, a rect (`w`, `h`) or a line (`pts`).
#[derive(Debug, Clone, PartialEq)]
pub struct MapFeature {
    pub cls: String,
    pub x: f64,
    pub y: f64,
    pub w: f64,
    pub h: f64,
    pub r: f64,
    pub pts: Vec<(f64, f64)>,
}

impl MapFeature {
    #[must_use]
    pub fn point(cls: &str, x: f64, y: f64) -> Self {
        Self {
            cls: cls.to_owned(),
            x,
            y,
            w: 0.0,
            h: 0.0,
            r: 0.0,
            pts: Vec::new(),
        }
    }

    /// How far (px, py) is from the feature's edge - zero inside a rect or a circle, on a line.
    #[must_use]
    pub fn distance(&self, px: f64, py: f64) -> f64 {
        if !self.pts.is_empty() {
            if self.pts.len() > 1 {
                return min_of(
                    self.pts
                        .windows(2)
                        .map(|w| seg_distance(px, py, w[0], w[1])),
                    f64::INFINITY,
                );
            }
            return hypot(px - self.pts[0].0, py - self.pts[0].1);
        }
        if self.w != 0.0 || self.h != 0.0 {
            let dx = max(
                max(self.x - self.w / 2.0 - px, 0.0),
                px - self.x - self.w / 2.0,
            );
            let dy = max(
                max(self.y - self.h / 2.0 - py, 0.0),
                py - self.y - self.h / 2.0,
            );
            return hypot(dx, dy);
        }
        max(0.0, hypot(px - self.x, py - self.y) - self.r)
    }

    /// Any part of the feature lies inside the frame (x0, y0, x1, y1).
    #[must_use]
    pub fn in_frame(&self, frame: (f64, f64, f64, f64)) -> bool {
        let (x0, y0, x1, y1) = frame;
        if !self.pts.is_empty() {
            return self
                .pts
                .iter()
                .any(|&(x, y)| x0 <= x && x <= x1 && y0 <= y && y <= y1)
                || self.pts.windows(2).any(|w| seg_crosses(w[0], w[1], frame));
        }
        if self.w != 0.0 || self.h != 0.0 {
            return self.x + self.w / 2.0 >= x0
                && self.x - self.w / 2.0 <= x1
                && self.y + self.h / 2.0 >= y0
                && self.y - self.h / 2.0 <= y1;
        }
        let cx = min(max(self.x, x0), x1);
        let cy = min(max(self.y, y0), y1);
        hypot(cx - self.x, cy - self.y) <= self.r
    }
}

/// From a point to a segment (`mapmatch._seg_distance`: the foot `a + t * d` taken first).
#[must_use]
pub fn seg_distance(px: f64, py: f64, a: (f64, f64), b: (f64, f64)) -> f64 {
    let ((ax, ay), (bx, by)) = (a, b);
    let (dx, dy) = (bx - ax, by - ay);
    if dx == 0.0 && dy == 0.0 {
        return hypot(px - ax, py - ay);
    }
    let t = max(
        0.0,
        min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)),
    );
    hypot(px - (ax + t * dx), py - (ay + t * dy))
}

/// A segment with both ends outside the frame still crosses it when the point of it closest to the frame's center lies inside.
fn seg_crosses(a: (f64, f64), b: (f64, f64), frame: (f64, f64, f64, f64)) -> bool {
    let (x0, y0, x1, y1) = frame;
    let (cx, cy) = (crate::py::half_sum(x0, x1), crate::py::half_sum(y0, y1));
    let ((ax, ay), (bx, by)) = (a, b);
    let (dx, dy) = (bx - ax, by - ay);
    if dx == 0.0 && dy == 0.0 {
        return false;
    }
    let t = max(
        0.0,
        min(1.0, ((cx - ax) * dx + (cy - ay) * dy) / (dx * dx + dy * dy)),
    );
    let (qx, qy) = (ax + t * dx, ay + t * dy);
    x0 <= qx && qx <= x1 && y0 <= qy && qy <= y1
}

/// `_pairs(seq)`: every item of `seq` that is a list of at least two, as a point; iterating a string's characters or a dict's keys finds
/// none.
///
/// # Errors
/// `seq` is no iterable (a number, a bool, None), or a coordinate `float()` refuses.
pub fn pairs(seq: &Value) -> Result<Vec<(f64, f64)>, Error> {
    let mut out = Vec::new();
    for p in crate::py::iterate(seq)? {
        if let Value::Array(items) = &p {
            if items.len() >= 2 {
                out.push((json_float(&items[0])?, json_float(&items[1])?));
            }
        }
    }
    Ok(out)
}

/// The keys whose value is one polyline, a flat list of points, rather than a list of records.
pub const POLYLINE_KEYS: [&str; 3] = ["lane", "road", "ring_road"];

/// The manifest list `key` as features of class `cls`.
///
/// # Errors
/// A coordinate `float()` refuses, a record missing the key its shape needs, a value that is not iterable where one is.
pub fn features(key: &str, cls: &str, recs: Option<&Value>) -> Result<Vec<MapFeature>, Error> {
    let mut out = Vec::new();
    let Some(Value::Array(recs)) = recs else {
        return Ok(out);
    };
    let empty = Value::Array(Vec::new());
    if key == "tree_crowns" {
        // a flat list of x, y, r triplets
        let mut i = 0;
        while i + 2 < recs.len() {
            let mut f = MapFeature::point(cls, json_float(&recs[i])?, json_float(&recs[i + 1])?);
            f.r = json_float(&recs[i + 2])?;
            out.push(f);
            i += 3;
        }
    } else if key == "village_groves" {
        for g in recs {
            if let Value::Object(g) = g {
                // `r` is read once a clump (none: never read)
                for (cx, cy) in pairs(g.get("clumps").unwrap_or(&empty))? {
                    let mut f = MapFeature::point(cls, cx, cy);
                    f.r = float_or_zero(g, "r")?;
                    out.push(f);
                }
            }
        }
    } else if key == "torii" {
        out.extend(
            pairs(&Value::Array(recs.clone()))?
                .into_iter()
                .map(|(x, y)| MapFeature::point(cls, x, y)),
        );
    } else if POLYLINE_KEYS.contains(&key) {
        let pts = pairs(&Value::Array(recs.clone()))?;
        if let Some(&(x, y)) = pts.first() {
            let mut f = MapFeature::point(cls, x, y);
            f.pts = pts;
            out.push(f);
        }
    } else if key == "pond"
        && !recs.is_empty()
        && !matches!(recs[0], Value::Array(_) | Value::Object(_))
    {
        // one rect: x, y, w, h
        if recs.len() >= 4 {
            // `x, y, w, h = (float(v) for v in recs[:4])`: the first refusal, in order
            let (left, top) = (json_float(&recs[0])?, json_float(&recs[1])?);
            let (width, height) = (json_float(&recs[2])?, json_float(&recs[3])?);
            let mut feature = MapFeature::point(cls, left + width / 2.0, top + height / 2.0);
            (feature.w, feature.h) = (width, height);
            out.push(feature);
        }
    } else {
        for rec in recs {
            let Value::Object(rec) = rec else {
                continue;
            };
            let shape = [rec.get("poly"), rec.get("pts")]
                .into_iter()
                .flatten()
                .find(|v| truthy(v))
                .unwrap_or(&empty);
            let pts = pairs(shape)?;
            if let Some(&(x, y)) = pts.first() {
                let mut f = MapFeature::point(cls, x, y);
                f.pts = pts;
                out.push(f);
            } else if rec.contains_key("cx") {
                let mut f = MapFeature::point(
                    cls,
                    json_float(item(rec, "cx")?)?,
                    json_float(item(rec, "cy")?)?,
                );
                f.r = float_or_zero(rec, "r")?;
                out.push(f);
            } else if rec.contains_key("x") && rec.contains_key("y") {
                let mut f = MapFeature::point(
                    cls,
                    json_float(item(rec, "x")?)?,
                    json_float(item(rec, "y")?)?,
                );
                f.w = float_or_zero(rec, "w")?;
                f.h = float_or_zero(rec, "h")?;
                f.r = float_or_zero(rec, "r")?;
                out.push(f);
            }
        }
    }
    Ok(out)
}

/// The map's recorded manifest (`json.load` of the file; the Python's memo of 8 is not carried - a reading is a pure function of the file,
/// which nothing writes during a run).
///
/// Research:
///     the map's manifest - NONE: the recorded manifest read as `json.load` reads it, each time asked (the Python's memo of 8 not carried), deciding nothing about the place
///
/// # Errors
/// The file cannot be read, or is not JSON.
pub fn load_map(path: &Path) -> Result<Value, Error> {
    let text = l7r_gate_core::record::read_text(path)
        .map_err(|e| crate::py::os_error(&e, &path.to_string_lossy()))?;
    l7r_shared::pyjson::loads(&text)
        .map_err(|e| Error::new("json.decoder.JSONDecodeError", e.to_string()))
}

/// `m.get(key)` of a manifest: a dict's value, the Python's `AttributeError` for anything else `json.load` can make.
///
/// # Errors
/// The manifest is not a dict.
pub fn get<'v>(m: &'v Value, key: &str) -> Result<Option<&'v Value>, Error> {
    match m {
        Value::Object(map) => Ok(map.get(key)),
        other => Err(Error::new(
            "AttributeError",
            format!(
                "'{}' object has no attribute 'get'",
                crate::py::type_name(other)
            ),
        )),
    }
}
