//! What a historical amount of money was worth, shown on hover (`record/money.py`, feature 413, diagram#14; ported by feature 449 T148,
//! `ask:449-phase4-slices`). An amount the author marks - `<span class="money" data-amount="20" data-coin="mon">20 mon</span>`, its era
//! named by `data-era` on the span or on the nearest element around it carrying one - is converted at build time into the text its hover
//! box shows: goods dollars as a range from the central reading to the high one (feature 421), wage dollars and Rokugani coin, each the
//! per-unit figure of gm-assistant's table times the amount.
//!
//! THE TABLE IS GM-ASSISTANT'S (`research/assets/money-conversions.json`, refreshed by `make money-conversions`); nothing here computes a
//! price. THE ERA IS THE AUTHOR'S CHOICE, NEVER THE BUILD'S (the asker, #14: *"no automatic fallback in the build"*).
//!
//! The figures are written as the Python wrote them: `round()` half to even on the float's exact value (to an integer, or to tens and
//! hundreds for a sum past $10,000), `:,` thousands separators, `:.2f` and `:.1f` correctly rounded, and a digit read as Python's `float()`
//! and `int()` read any decimal digit of Unicode.
//!
//! Research: money conversion on the record's site - NONE: presentation of gm-assistant's conversion table

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::pyre::py;
use crate::{digit_value, Error, Result};
use l7r_guard::shared::html_text::{escape, unescape};
use l7r_guard::shared::py_text::{repr, strip};
use l7r_guard::shared::pyjson::{py_str, truthy};

pub const CONVERSIONS: &str = "money-conversions.json";
pub const AWAITING: &str = "money-eras-awaiting.json";
/// Rokugani coin, in sen (1 koku = 10 bu = 100 zeni = 1,000 sen; the canon is `l7r.md` "Money").
pub const COINS: [(&str, i64); 4] = [("koku", 1000), ("bu", 100), ("zeni", 10), ("sen", 1)];

static TAG: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<(/?)([a-zA-Z][\w-]*)((?:"[^"]*"|'[^']*'|[^'">])*)>"#));
static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w-]+)\s*=\s*"([^"]*)""#));
static ANY_TAG: LazyLock<Regex> = LazyLock::new(|| py(r"<[^>]+>"));
const VOID: [&str; 9] = [
    "br", "hr", "img", "meta", "link", "input", "wbr", "col", "source",
];
/// Elements the record leaves unclosed: one ends where the next of its kind opens.
const AUTO: [&str; 7] = ["p", "li", "td", "th", "tr", "dd", "dt"];
static AMOUNT: LazyLock<Regex> =
    LazyLock::new(|| py(r"^\s*(\d[\d,]*(?:\.\d+)?)\s*(?:-\s*(\d[\d,]*(?:\.\d+)?))?\s*$"));
static YEARS: LazyLock<Regex> = LazyLock::new(|| py(r"(\d{3,4})(?:\s*-\s*(\d{1,4}))?"));

/// The vendored conversion table's eras, and the era ids awaiting their row.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Table {
    pub eras: Map<String, Value>,
    pub awaiting: Map<String, Value>,
}

fn read_json(path: &Path) -> Result<Map<String, Value>> {
    let Some(text) = crate::read(path) else {
        if path.exists() {
            return Err(Error::new(
                "OSError",
                format!("cannot read '{}'", path.display()),
            ));
        }
        return Ok(Map::new());
    };
    match crate::json(&text).map_err(|e| Error::new("JSONDecodeError", e))? {
        Value::Object(m) => Ok(m),
        _ => Ok(Map::new()),
    }
}

/// The table and the awaiting list beside the record; a missing file reads as empty.
///
/// # Errors
/// A file that is not JSON, or a table whose `eras` is not an object (the Python's `.get` on it failing).
pub fn load(record_dir: &Path) -> Result<Table> {
    let assets = record_dir.join("assets");
    let eras = match read_json(&assets.join(CONVERSIONS))?.remove("eras") {
        None => Map::new(),
        Some(Value::Object(m)) => m,
        Some(other) => {
            return Err(Error::new(
                "AttributeError",
                format!(
                    "'{}' object has no attribute 'get'",
                    l7r_guard::shared::blocked::type_name(&other)
                ),
            ))
        }
    };
    Ok(Table {
        eras,
        awaiting: read_json(&assets.join(AWAITING))?,
    })
}

/// Decimal digits of any script as ASCII, as Python's `int()` and `float()` read them.
fn ascii_digits(text: &str) -> String {
    text.chars()
        .map(|c| match digit_value(c) {
            Some(d) if !c.is_ascii_digit() => char::from_digit(d, 10).unwrap_or(c),
            _ => c,
        })
        .collect()
}

fn int_of(text: &str) -> i64 {
    ascii_digits(text).parse().unwrap_or(0)
}

/// The span a text names, `1745-1754`, `1745-54` or `1766`, as (first, last); none when it names no year.
#[must_use]
pub fn years(text: &str) -> Option<(i64, i64)> {
    let m = YEARS
        .captures_iter(text)
        .map_while(std::result::Result::ok)
        .last()?;
    let first = int_of(&m[1]);
    let Some(tail) = m.get(2).map(|t| t.as_str()).filter(|t| !t.is_empty()) else {
        return Some((first, first));
    };
    let whole = first.to_string();
    let (n, w) = (tail.chars().count(), whole.chars().count());
    let last = if n < w {
        int_of(&format!("{}{tail}", &whole[..w - n]))
    } else {
        int_of(tail)
    };
    Some((first, last))
}

/// `1745-1754` as `1745-54`, as the asker wrote it; anything else as written.
#[must_use]
pub fn short_years(text: &str) -> String {
    match years(text) {
        Some((a, b)) if a != b && first_two(a) == first_two(b) => {
            format!("{a}-{}", b.to_string().get(2..).unwrap_or(""))
        }
        _ => text.to_owned(),
    }
}

fn first_two(n: i64) -> String {
    n.to_string().chars().take(2).collect()
}

/// An integer's digits with Python's `:,` separators.
fn commas(digits: &str) -> String {
    let (sign, body) = digits.strip_prefix('-').map_or(("", digits), |b| ("-", b));
    let (int, frac) = body
        .split_once('.')
        .map_or((body, None), |(i, f)| (i, Some(f)));
    let mut out = String::new();
    for (i, c) in int.chars().enumerate() {
        if i > 0 && (int.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    match frac {
        Some(f) => format!("{sign}{out}.{f}"),
        None => format!("{sign}{out}"),
    }
}

/// Exact Rokugani coin: 3215 -> `3 koku 2 bu 1 zeni 5 sen`.
#[must_use]
pub fn fmt(sen: i64) -> String {
    let mut left = sen;
    let mut parts = Vec::new();
    for (coin, per) in COINS {
        let count = left.div_euclid(per);
        left = left.rem_euclid(per);
        if count != 0 {
            parts.push(format!("{} {coin}", commas(&count.to_string())));
        }
    }
    if parts.is_empty() {
        "0 sen".to_owned()
    } else {
        parts.join(" ")
    }
}

/// `round(x)` to an integer, half to even.
fn round_int(x: f64) -> i64 {
    // a sum in sen or dollars is far inside an i64
    #[allow(
        clippy::cast_possible_truncation,
        reason = "a figure of the money table times an amount the record writes"
    )]
    let n = x.round_ties_even() as i64;
    n
}

/// The two largest coins an amount needs, rounded, `about` when rounded.
#[must_use]
pub fn everyday(sen: i64) -> String {
    if sen < 100 {
        return fmt(sen);
    }
    let at = COINS.iter().position(|(_, per)| sen >= *per).unwrap_or(0);
    let small = COINS[(at + 1).min(COINS.len() - 1)].1;
    #[allow(
        clippy::cast_precision_loss,
        reason = "Python's true division of two integers is a float's"
    )]
    let rounded = round_int(sen as f64 / small as f64) * small;
    let text = fmt(rounded);
    if rounded == sen {
        text
    } else {
        format!("about {text}")
    }
}

/// A Rokugani sum: under 10 sen to a tenth of a sen, else [`everyday`].
#[must_use]
pub fn rokugani(sen: f64) -> String {
    if sen < 10.0 {
        format!("{sen:.1} sen")
    } else {
        everyday(round_int(sen))
    }
}

/// `round(x, digits)` for a negative `digits`: the float's exact decimal value rounded half to even at that place.
fn round_to(x: f64, digits: i32) -> f64 {
    let exact = format!("{:.0}", x.trunc());
    let frac = x - x.trunc();
    let place = usize::try_from(-digits).unwrap_or(0);
    let (sign, body) = exact
        .strip_prefix('-')
        .map_or(("", exact.as_str()), |b| ("-", b));
    if body.len() <= place {
        // every digit is below the place: the value rounds to zero, or to one unit of the place when past its half
        let unit = 10f64.powi(-digits);
        return if x.abs() * 2.0 > unit {
            unit.copysign(x)
        } else {
            0.0
        };
    }
    let (keep, cut) = body.split_at(body.len() - place);
    let mut kept: i64 = keep.parse().unwrap_or(0);
    let half = format!("5{}", "0".repeat(place.saturating_sub(1)));
    let past = cut > half.as_str() || (cut == half.as_str() && frac != 0.0);
    if past || (cut == half.as_str() && frac == 0.0 && kept % 2 == 1) {
        kept += 1;
    }
    format!("{sign}{kept}{}", "0".repeat(place))
        .parse()
        .unwrap_or(x)
}

/// Dollars: to the cent under $100, the dollar under $10,000, three figures above; `scale` (a range's larger end) sets the precision, so
/// both ends of a range read alike.
#[must_use]
pub fn dollars(x: f64, scale: Option<f64>) -> String {
    let big = scale.unwrap_or(x);
    if big < 100.0 {
        return format!("${}", commas(&format!("{x:.2}")));
    }
    if big < 10000.0 {
        return format!("${}", commas(&round_int(x).to_string()));
    }
    #[allow(
        clippy::cast_possible_truncation,
        reason = "Python's int() of a sum of dollars"
    )]
    let width = (big.trunc() as i64).to_string().len();
    let digits = 3 - i32::try_from(width).unwrap_or(3);
    let rounded = round_to(x, digits);
    format!("${}", commas(&format!("{rounded:.0}")))
}

fn dollar_range(ends: &[f64]) -> String {
    let big = ends.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    ends.iter()
        .map(|e| dollars(*e, Some(big)))
        .collect::<Vec<_>>()
        .join("-")
}

fn number(unit: &Map<String, Value>, k: &str) -> Result<f64> {
    unit.get(k)
        .ok_or_else(|| Error::new("KeyError", format!("'{k}'")))?
        .as_f64()
        .ok_or_else(|| {
            Error::new(
                "TypeError",
                format!("can't multiply sequence by non-int of type 'float' ('{k}')"),
            )
        })
}

fn field(era: &Map<String, Value>, k: &str) -> Result<String> {
    era.get(k)
        .map(py_str)
        .ok_or_else(|| Error::new("KeyError", format!("'{k}'")))
}

/// The hover box's text for one amount (one figure, or the two ends of a range) at one era's row.
///
/// # Errors
/// A unit or era missing a figure the box reads (the Python's `KeyError`).
pub fn hover_box(
    amount: &[f64],
    label: &str,
    unit: &Map<String, Value>,
    era: &Map<String, Value>,
    borrowed: bool,
) -> Result<String> {
    let (first, last) = (amount[0], amount[amount.len() - 1]);
    let goods = dollar_range(&[
        first * number(unit, "goods_dollars")?,
        last * number(unit, "goods_dollars_high")?,
    ]);
    let wage = number(unit, "wage_dollars")?;
    let wages = dollar_range(&amount.iter().map(|a| a * wage).collect::<Vec<_>>());
    let per = number(unit, "rokugan_sen")?;
    let sen: Vec<String> = amount.iter().map(|a| rokugani(a * per)).collect();
    let mut lines = vec![format!(
        "{label}: about {goods} in goods, {wages} in wages, {} in Rokugan",
        sen.join(" to ")
    )];
    let place = field(era, "place")?;
    let span = field(era, "years")?;
    if borrowed {
        lines.push(format!("at {place} {} prices", short_years(&span)));
    }
    let left: Vec<String> = match era.get("goods_left_out") {
        Some(v) if truthy(v) => match v {
            Value::Array(items) => items.iter().map(|g| py_str(g).to_lowercase()).collect(),
            // a string is iterated by its characters, as Python's `for g in ...` iterates one
            other => py_str(other)
                .chars()
                .map(|c| c.to_lowercase().collect())
                .collect(),
        },
        _ => Vec::new(),
    };
    let coverage = era.get("basket_coverage").map_or_else(String::new, py_str);
    let leaves = if left.is_empty() {
        String::new()
    } else {
        format!("; leaves out {}", left.join(", "))
    };
    lines.push(format!("{place} {span}: {coverage}{leaves}"));
    if let Some(c) = era.get("confidence").filter(|c| truthy(c)) {
        lines.push(py_str(c));
    }
    Ok(lines.join("\n"))
}

fn attrs(raw: &str) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = Vec::new();
    for c in ATTR.captures_iter(raw).map_while(std::result::Result::ok) {
        let v = unescape(&c[2]);
        match out.iter_mut().find(|(k, _)| k == &c[1]) {
            Some(slot) => slot.1 = v,
            None => out.push((c[1].to_owned(), v)),
        }
    }
    out
}

fn get<'a>(a: &'a [(String, String)], k: &str) -> Option<&'a str> {
    a.iter().find(|(n, _)| n == k).map(|(_, v)| v.as_str())
}

fn inherited<'a>(
    stack: &[&'a [(String, String)]],
    own: &'a [(String, String)],
    name: &str,
) -> Option<&'a str> {
    get(own, name).or_else(|| stack.iter().rev().find_map(|a| get(a, name)))
}

/// The box text for an amount converted (`Ok(Some)`), the refusal of a bad mark (`Err`'s message), or nothing for an amount whose era is
/// awaiting its row, which keeps the glossary tooltip alone (FR-005).
fn checked(
    own: &[(String, String)],
    stack: &[&[(String, String)]],
    text: &str,
    place: &str,
    table: &Table,
) -> Result<std::result::Result<Option<String>, String>> {
    let said = format!("{place}: the amount {}", repr(text));
    let Some(era_id) = inherited(stack, own, "data-era").filter(|e| !e.is_empty()) else {
        return Ok(Err(format!("{said} names no era - put data-era=\"<era id>\" on it or on an element around it (feature 413)")));
    };
    let raw = get(own, "data-amount").unwrap_or("");
    let Some(m) = AMOUNT.captures(raw).ok().flatten() else {
        return Ok(Err(format!(
            "{said} has data-amount={} - a number, or two joined by a hyphen (\"15-20\")",
            repr(raw)
        )));
    };
    let amount: Vec<f64> = (1..=2)
        .filter_map(|i| m.get(i))
        .map(|g| {
            ascii_digits(&g.as_str().replace(',', ""))
                .parse()
                .unwrap_or(0.0)
        })
        .collect();
    let coin = get(own, "data-coin").unwrap_or("");
    let paid = inherited(stack, own, "data-paid");
    let Some(era) = table.eras.get(era_id) else {
        if table.awaiting.contains_key(era_id) {
            return Ok(Ok(None));
        }
        let mut known: Vec<&String> = table.eras.keys().chain(table.awaiting.keys()).collect();
        known.sort();
        let known = if known.is_empty() {
            "none".to_owned()
        } else {
            known
                .iter()
                .map(|k| k.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        };
        return Ok(Err(format!("{said} names era {}, which the conversion table does not have and research/assets/{AWAITING} does not list (known: {known})", repr(era_id))));
    };
    let era = era
        .as_object()
        .ok_or_else(|| Error::new("AttributeError", "an era of the money table is an object"))?;
    let empty = Map::new();
    let units = era
        .get("units")
        .and_then(Value::as_object)
        .unwrap_or(&empty);
    let Some(unit) = units.get(coin) else {
        let has: Vec<&str> = units.keys().map(String::as_str).collect();
        return Ok(Err(format!(
            "{said} names coin {}, which era {} has no unit for (it has: {})",
            repr(coin),
            repr(era_id),
            has.join(", ")
        )));
    };
    if let Some(p) = paid.filter(|p| years(p).is_none()) {
        return Ok(Err(format!("{said} has data-paid={} with no year - write \"<place> <year>\" or \"<place> <year>-<year>\"", repr(p))));
    }
    let unit = unit
        .as_object()
        .ok_or_else(|| Error::new("TypeError", "a unit of the money table is an object"))?;
    hover_box(&amount, text, unit, era, paid.is_some()).map(|b| Ok(Some(b)))
}

/// `markup` with each converted amount's box text written into its span as `data-def`, and the refusals, each naming `place` and the
/// amount. Markup with no `class="money"` is returned as it is.
///
/// # Errors
/// An era's row missing a figure the box reads (the Python's uncaught `KeyError`).
pub fn annotate(markup: &str, place: &str, table: &Table) -> Result<(String, Vec<String>)> {
    if !markup.contains("class=\"money\"") {
        return Ok((markup.to_owned(), Vec::new()));
    }
    let mut out = String::with_capacity(markup.len() + 256);
    let mut errors = Vec::new();
    let mut stack: Vec<(String, Vec<(String, String)>)> = Vec::new();
    let mut last = 0;
    for m in TAG.captures_iter(markup).map_while(std::result::Result::ok) {
        let (closing, raw) = (!m[1].is_empty(), &m[3]);
        let name = m[2].to_lowercase();
        if closing {
            if stack.iter().any(|(n, _)| *n == name) {
                while let Some((n, _)) = stack.pop() {
                    if n == name {
                        break;
                    }
                }
            }
            continue;
        }
        if VOID.contains(&name.as_str())
            || raw
                .trim_end_matches(l7r_guard::shared::py_text::is_space)
                .ends_with('/')
        {
            continue;
        }
        if AUTO.contains(&name.as_str()) && stack.last().is_some_and(|(n, _)| *n == name) {
            stack.pop();
        }
        let own = attrs(raw);
        let end_of_tag = m.get(0).map_or(0, |g| g.end());
        if name == "span" && get(&own, "class") == Some("money") {
            let end = markup[end_of_tag..]
                .find("</span>")
                .map_or(markup.len(), |at| end_of_tag + at);
            let text = unescape(strip(&ANY_TAG.replace_all(&markup[end_of_tag..end], "")));
            let above: Vec<&[(String, String)]> = stack.iter().map(|(_, a)| a.as_slice()).collect();
            match checked(&own, &above, &text, place, table)? {
                Err(refusal) => errors.push(refusal),
                Ok(Some(tip)) => {
                    out.push_str(&markup[last..end_of_tag - 1]);
                    let _ = write!(out, " data-def=\"{}\">", escape(&tip, true));
                    last = end_of_tag;
                }
                Ok(None) => {}
            }
        }
        stack.push((name, own));
    }
    out.push_str(&markup[last..]);
    Ok((out, errors))
}

#[cfg(test)]
mod tests;
