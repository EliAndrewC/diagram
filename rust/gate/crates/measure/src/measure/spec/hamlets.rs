//! Feature 261's four measures of the pool hamlets (feature 449 T139, from `specs/261-northwest-wind-by-default/measure/board_well.py`,
//! `brook_turn.py`, `fixtures_and_board.py` and `row_spread.py`, `ask:449-phase3-remainder` Q4).
//!
//! Each reads `pool/hamlets/<m>/<m>.json` from the working directory, or the old skill directory's where the working directory has no
//! `pool/hamlets` (the Python's fallback, kept: its `--rev` form names that path too). A JSON number stays the int or float Python read,
//! because `round(x, 1)` of an int prints `5` and of a float `5.0`; the arithmetic is Python's, `math.hypot` and float `%` included.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_guard::shared::py_text::{py_float_of, repr};
use l7r_guard::shared::pyjson::py_float;
use serde_json::Value;

use super::super::events::{py_str, read_text, truthy, Raised};
use super::super::turn_time::py_round;
use super::Ran;

const OLD_POOL: &str = ".claude/skills/diagram/pool/hamlets";
const MAPS: [&str; 5] = ["inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada"];

/// A number as Python holds what `json.loads` made of it: an int (a bool among them) or a float.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Num {
    Int(i128),
    Float(f64),
}

impl Num {
    #[expect(
        clippy::cast_precision_loss,
        reason = "an int as Python's float() converts it"
    )]
    fn f(self) -> f64 {
        match self {
            Self::Int(i) => i as f64,
            Self::Float(x) => x,
        }
    }

    fn sub(self, o: Self) -> Self {
        match (self, o) {
            (Self::Int(a), Self::Int(b)) => Self::Int(a - b),
            _ => Self::Float(self.f() - o.f()),
        }
    }

    /// `a * b`, exact for ints as Python's are; past what an i128 holds the floats' product, a divergence no map reaches.
    fn mul(self, o: Self) -> Self {
        match (self, o) {
            (Self::Int(a), Self::Int(b)) => a
                .checked_mul(b)
                .map_or(Self::Float(self.f() * o.f()), Self::Int),
            _ => Self::Float(self.f() * o.f()),
        }
    }

    fn negative(self) -> bool {
        match self {
            Self::Int(i) => i < 0,
            Self::Float(x) => x < 0.0,
        }
    }

    /// `round(x, 1)`: an int unchanged, a float to one place.
    fn round1(self) -> String {
        match self {
            Self::Int(i) => i.to_string(),
            Self::Float(x) => py_float(py_round(x, 1)),
        }
    }

    /// `round(x)`: half to even, an int.
    #[expect(
        clippy::cast_possible_truncation,
        reason = "Python's round() of a coordinate, an int"
    )]
    fn round0(self) -> i128 {
        match self {
            Self::Int(i) => i,
            Self::Float(x) => x.round_ties_even() as i128,
        }
    }
}

fn num(v: &Value) -> Result<Num, Raised> {
    match v {
        Value::Bool(b) => Ok(Num::Int(i128::from(*b))),
        Value::Number(n) => Ok(n
            .as_i64()
            .map(i128::from)
            .or_else(|| n.as_u64().map(i128::from))
            .map_or_else(|| Num::Float(n.as_f64().unwrap_or(0.0)), Num::Int)),
        _ => Err("TypeError: unsupported operand type(s) for -".to_owned()),
    }
}

/// `v[key]`: a dict's value, the Python's `KeyError` or `TypeError` otherwise.
fn at<'a>(v: &'a Value, key: &str) -> Result<&'a Value, Raised> {
    match v {
        Value::Object(m) => m.get(key).ok_or_else(|| format!("KeyError: {}", repr(key))),
        _ => Err("TypeError: indices must be integers".to_owned()),
    }
}

/// `v.get(key)`; anything but a dict the Python's `AttributeError`.
fn get<'a>(v: &'a Value, key: &str) -> Result<Option<&'a Value>, Raised> {
    match v {
        Value::Object(m) => Ok(m.get(key)),
        _ => Err("AttributeError: no .get on a value that is no dict".to_owned()),
    }
}

/// `for x in v`: a list's items; an empty dict or string none. A dict's keys or a string's characters are text every use of them here
/// refuses, so a non-empty one is the failure the Python reached a line later.
fn items(v: &Value) -> Result<&[Value], Raised> {
    match v {
        Value::Array(a) => Ok(a),
        Value::Object(m) if m.is_empty() => Ok(&[]),
        Value::String(s) if s.is_empty() => Ok(&[]),
        _ => Err("TypeError: not a list of records".to_owned()),
    }
}

/// `v[-1]`.
fn last(v: &Value) -> Result<&Value, Raised> {
    match v {
        Value::Array(a) => a
            .last()
            .ok_or_else(|| "IndexError: list index out of range".to_owned()),
        _ => Err("TypeError: not a list".to_owned()),
    }
}

/// A point's `[0]` and `[1]`.
fn xy(v: &Value) -> Result<(Num, Num), Raised> {
    match v {
        Value::Array(a) if a.len() >= 2 => Ok((num(&a[0])?, num(&a[1])?)),
        _ => Err("IndexError: a point needs two coordinates".to_owned()),
    }
}

fn pool(cwd: &Path) -> PathBuf {
    if cwd.join("pool/hamlets").is_dir() {
        cwd.join("pool/hamlets")
    } else {
        cwd.join(OLD_POOL)
    }
}

fn load(cwd: &Path, m: &str) -> Result<Value, Raised> {
    let path = pool(cwd).join(m).join(format!("{m}.json"));
    serde_json::from_str(&read_text(&path)?).map_err(|e| format!("JSONDecodeError: {e}"))
}

/// `math.hypot(x, y)` as `CPython` computes it (`vector_norm`: lossless scaling and squaring, compensated sums and a differential
/// correction), not the C library's `hypot`, which differed from it in the last place on 1,760 of 300,000 pairs of map coordinates
/// (observed 2026-11-13, method: `ctypes` libm `hypot` against `math.hypot` in Python 3.14.4, `scratchpad/t139/`).
fn hypot(x: f64, y: f64) -> f64 {
    let (x, y) = (x.abs(), y.abs());
    let max = x.max(y);
    if max.is_infinite() || max == 0.0 {
        return max;
    }
    let e = frexp_exponent(max);
    if e < -1023 {
        // a largest coordinate so small that `ldexp(1.0, -max_e)` would overflow: the Python's rescale by `DBL_MIN`
        return f64::MIN_POSITIVE * hypot(x / f64::MIN_POSITIVE, y / f64::MIN_POSITIVE);
    }
    let scale = pow2(-e);
    let (mut csum, mut frac1, mut frac2) = (1.0f64, 0.0f64, 0.0f64);
    for v in [x, y] {
        let v = v * scale;
        let (hi, lo) = (v * v, v.mul_add(v, -(v * v)));
        let sum = csum + hi;
        frac2 += (csum - sum) + hi;
        csum = sum;
        frac1 += lo;
    }
    let mut h = (csum - 1.0 + (frac1 + frac2)).sqrt();
    let (hi, lo) = (-h * h, (-h).mul_add(h, h * h));
    let sum = csum + hi;
    frac2 += (csum - sum) + hi;
    csum = sum;
    frac1 += lo;
    h += (csum - 1.0 + (frac1 + frac2)) / (2.0 * h);
    h / scale
}

/// `frexp(x)[1]` of a positive finite float: `x = m * 2**e` with `0.5 <= m < 1`, a subnormal scaled up by `2**54` first.
fn frexp_exponent(x: f64) -> i32 {
    let biased = i32::try_from((x.to_bits() >> 52) & 0x7ff).unwrap_or(0);
    if biased == 0 {
        frexp_exponent(x * 18_014_398_509_481_984.0) - 54
    } else {
        biased - 1022
    }
}

/// `ldexp(1.0, k)` for `-1074 <= k <= 1023`, built from its bits so no product rounds or underflows on the way.
fn pow2(k: i32) -> f64 {
    if k >= -1022 {
        f64::from_bits(u64::try_from(k + 1023).unwrap_or(0) << 52)
    } else {
        f64::from_bits(1u64 << u32::try_from(k + 1074).unwrap_or(0))
    }
}

/// `math.degrees(x)`: `x * (180.0 / pi)`, the constant computed as `CPython` computes it.
fn degrees(x: f64) -> f64 {
    x * (180.0 / std::f64::consts::PI)
}

/// Python's float `x % m` for a positive `m`: the sign of the divisor.
fn py_mod(x: f64, m: f64) -> f64 {
    let r = x % m;
    if r == 0.0 {
        0.0
    } else if r < 0.0 {
        r + m
    } else {
        r
    }
}

/// `l7r-gate measure spec 261 board-well <map>...`: the recorded `meta.kosatsuba_well_ft` beside the drawn board's distance to its
/// nearest well.
pub(super) fn board_well(maps: &[String], cwd: &Path, out: &mut String) -> Ran {
    for m in maps {
        let map = load(cwd, m)?;
        let k = last(at(&map, "kosatsuba")?)?;
        let (kx, ky) = (num(at(k, "x")?)?, num(at(k, "y")?)?);
        let mut nearest: Option<f64> = None;
        for w in items(at(&map, "wells")?)? {
            let d = hypot(kx.sub(num(at(w, "x")?)?).f(), ky.sub(num(at(w, "y")?)?).f());
            nearest = Some(nearest.map_or(d, |n| if d < n { d } else { n }));
        }
        let nearest =
            nearest.ok_or_else(|| "ValueError: min() iterable argument is empty".to_owned())?;
        let meta = at(&map, "meta")?;
        let ftpx = get(meta, "ftpx")?.filter(|v| truthy(v));
        let scale = ftpx.map_or(Ok(1.0), py_float_of)?;
        let recorded = get(meta, "kosatsuba_well_ft")?.map_or_else(|| "None".to_owned(), py_str);
        let drawn = Num::Float(nearest * scale).round1();
        let _ = writeln!(out, "{m} recorded {recorded} drawn {drawn}");
    }
    Ok(0)
}

/// `l7r-gate measure spec 261 brook-turn <map>...`: the sharpest turn, in degrees, at any vertex of each map's recorded brook.
pub(super) fn brook_turn(maps: &[String], cwd: &Path, out: &mut String) -> Ran {
    for m in maps {
        let map = load(cwd, m)?;
        let mut turns = Vec::new();
        for s in items(get(&map, "streams")?.unwrap_or(&Value::Array(Vec::new())))? {
            let Value::Array(p) = at(s, "poly")? else {
                return Err("TypeError: a brook's poly is no list".to_owned());
            };
            let mut sharpest: Option<f64> = None;
            for w in p.windows(3) {
                let (a, b, c) = (xy(&w[0])?, xy(&w[1])?, xy(&w[2])?);
                let out_of = c.1.sub(b.1).f().atan2(c.0.sub(b.0).f());
                let into = b.1.sub(a.1).f().atan2(b.0.sub(a.0).f());
                let turn = (py_mod(degrees(out_of - into) + 180.0, 360.0) - 180.0).abs();
                sharpest = Some(sharpest.map_or(turn, |t| if turn > t { turn } else { t }));
            }
            let sharpest = sharpest
                .ok_or_else(|| "ValueError: max() iterable argument is empty".to_owned())?;
            turns.push(Num::Float(sharpest).round1());
        }
        let _ = writeln!(out, "{m} [{}]", turns.join(", "));
    }
    Ok(0)
}

/// `cross(p, q, a, b)`: whether segment p-q (a fixture to its house) properly crosses lane segment a-b.
fn cross(start: (Num, Num), end: (Num, Num), lane_a: (Num, Num), lane_b: (Num, Num)) -> bool {
    let o = |from: (Num, Num), to: (Num, Num), at: (Num, Num)| {
        to.0.sub(from.0)
            .mul(at.1.sub(from.1))
            .sub(to.1.sub(from.1).mul(at.0.sub(from.0)))
    };
    o(start, end, lane_a).mul(o(start, end, lane_b)).negative()
        && o(lane_a, lane_b, start)
            .mul(o(lane_a, lane_b, end))
            .negative()
}

/// Whether a fixture's line to its house crosses any lane, the lanes read as the Python's generator read them: each lane's points only
/// while no earlier segment crossed.
fn across(map: &Value, of: &Value, r: &Value) -> Result<bool, Raised> {
    for lane in items(at(map, "lanes")?)? {
        let pts: &[Value] = match at(lane, "pts")? {
            Value::Array(a) => a,
            Value::String(s) if s.chars().count() <= 1 => &[],
            Value::Object(o) if o.len() <= 1 => &[],
            _ => return Err("TypeError: a lane's pts is no list of points".to_owned()),
        };
        for seg in pts.windows(2) {
            let (p, q) = (xy(of)?, (num(at(r, "x")?)?, num(at(r, "y")?)?));
            if cross(p, q, xy(&seg[0])?, xy(&seg[1])?) {
                return Ok(true);
            }
        }
    }
    Ok(false)
}

/// `l7r-gate measure spec 261 fixtures-and-board`: per pool hamlet, homestead plots, fixtures and persimmons across a lane from their
/// house, unseated fixtures, the board's seat. The Python ran its five maps whatever it was given, so arguments are taken and ignored.
pub(super) fn fixtures_and_board(cwd: &Path, out: &mut String) -> Ran {
    let empty = Value::Array(Vec::new());
    for m in MAPS {
        let map = load(cwd, m)?;
        let mut homestead = 0;
        for d in items(get(&map, "dry_plots")?.unwrap_or(&empty))? {
            homestead += usize::from(get(d, "homestead")?.is_some_and(truthy));
        }
        let (mut total, mut crossing) = (0, 0);
        for key in ["farm_fixtures", "persimmons"] {
            for r in items(get(&map, key)?.unwrap_or(&empty))? {
                let Some(of) = get(r, "of")?.filter(|v| truthy(v)) else {
                    continue;
                };
                total += 1;
                crossing += usize::from(across(&map, of, r)?);
            }
        }
        let k = last(at(&map, "kosatsuba")?)?;
        let meta = at(&map, "meta")?;
        let shown = |v: Option<&Value>| v.map_or_else(|| "None".to_owned(), py_str);
        let unseated = shown(get(meta, "farm_fixtures_unseated")?);
        let (x, y) = (num(at(k, "x")?)?.round0(), num(at(k, "y")?)?.round0());
        let rot = shown(get(k, "rot")?);
        let caption = shown(get(meta, "kosatsuba_caption_level")?);
        let roll = shown(get(meta, "roll_attempt")?);
        let _ = writeln!(out, "{m} homestead plots {homestead} fixtures {total} across lane {crossing} unseated {unseated} board {x} {y} {rot} caption {caption} roll {roll}");
    }
    Ok(0)
}

/// Runs of sorted values whose neighbors lie within 40 ft, each of three or more as `(count, spread)`.
fn groups(values: &[Value]) -> Result<String, Raised> {
    let mut vals = values.iter().map(num).collect::<Result<Vec<_>, _>>()?;
    vals.sort_by(|a, b| {
        a.f()
            .partial_cmp(&b.f())
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    let Some(first) = vals.first() else {
        return Err("IndexError: list index out of range".to_owned());
    };
    let (mut runs, mut cur) = (Vec::new(), vec![*first]);
    for v in &vals[1..] {
        if v.sub(cur[cur.len() - 1]).f() <= 40.0 {
            cur.push(*v);
        } else {
            runs.push(std::mem::replace(&mut cur, vec![*v]));
        }
    }
    runs.push(cur);
    let shown: Vec<String> = runs
        .iter()
        .filter(|g| g.len() >= 3)
        .map(|g| format!("({}, {})", g.len(), g[g.len() - 1].sub(g[0]).round1()))
        .collect();
    Ok(format!("[{}]", shown.join(", ")))
}

/// `l7r-gate measure spec 261 row-spread [--rev <sha>] <map>...`: the farmhouses grouped into rows by y and columns by x, each group of
/// three or more with its spread in feet (the settlement review's measure of a lattice: ranks of 5 ft or less).
pub(super) fn row_spread(args: &[String], cwd: &Path, out: &mut String) -> Ran {
    let (rev, maps) = match args.first().map(String::as_str) {
        Some("--rev") => (
            Some(
                args.get(1)
                    .ok_or_else(|| "IndexError: list index out of range".to_owned())?
                    .as_str(),
            ),
            args.get(2..).unwrap_or(&[]),
        ),
        _ => (None, args),
    };
    let top = std::process::Command::new("git")
        .arg("-C")
        .arg(cwd)
        .args(["rev-parse", "--show-toplevel"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .ok_or_else(|| "CalledProcessError: git rev-parse --show-toplevel failed".to_owned())?;
    let root = String::from_utf8_lossy(&top.stdout).trim().to_owned();
    for m in maps {
        let map: Value = match rev.filter(|r| !r.is_empty()) {
            Some(r) => {
                let shown = std::process::Command::new("git")
                    .args(["-C", &root, "show", &format!("{r}:{OLD_POOL}/{m}/{m}.json")])
                    .output()
                    .ok()
                    .filter(|o| o.status.success())
                    .ok_or_else(|| format!("CalledProcessError: git show {r}"))?;
                serde_json::from_slice(&shown.stdout)
                    .map_err(|e| format!("JSONDecodeError: {e}"))?
            }
            None => load(cwd, m)?,
        };
        let houses = items(at(&map, "houses")?)?;
        let ys = houses
            .iter()
            .map(|h| at(h, "y").cloned())
            .collect::<Result<Vec<_>, _>>()?;
        let rows = groups(&ys)?;
        let xs = houses
            .iter()
            .map(|h| at(h, "x").cloned())
            .collect::<Result<Vec<_>, _>>()?;
        let columns = groups(&xs)?;
        let _ = writeln!(out, "{m} rows {rows} columns {columns}");
    }
    Ok(0)
}

#[cfg(test)]
mod tests;
