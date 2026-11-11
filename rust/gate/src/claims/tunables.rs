//! The numbers that are OURS (`scripts/record/tunables.py`, ported by feature 449 T82; feature 417 T28, D31): every claim whose value no
//! source states, and with `--inline` every number inside the map code its unit's claims never state - the Rust stages read here, a
//! `.py` file's numbers by Python's syntax tree through the runner (`ask:449-T82-claims`).

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::json;

use super::index::Cur;
use super::scope::Reader;
use super::units::{items, rel, rglob};
use crate::record::repo::{read_text, Fail};
use crate::record::units::re;

/// The labels whose value is ours, searched and silent first.
const OURS: [&str; 3] = ["GUESS", "UNRESEARCHED", "CONVENTION"];
static FIGURE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])"));
/// The code that draws a map, and the audit that grades a Mode A sheet (D31 (d)).
const MAP_CODE: [&str; 5] = [
    "l7r/diagram/tools/pack_audit/",
    "l7r/diagram/labels/",
    "l7r/diagram/compound",
    "l7r/diagram/well_gear.py",
    "rust/phases/src/",
];
/// Numbers too plain to be a decision.
const TRIVIAL: [f64; 12] = [
    0.0, 1.0, 2.0, 3.0, 4.0, 10.0, 100.0, 90.0, 180.0, 360.0, 255.0, 0.5,
];
static RUST_NUMBER: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?<![\w.])(\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?)(?:_?(?:f32|f64|u8|u16|u32|u64|usize|i8|i16|i32|i64|isize))?(?![\w.])",
    )
});
static CFG_TEST: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#\[cfg\(test\)\]"));
static LINE_COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"//.*"));
static STRING: LazyLock<Regex> = LazyLock::new(|| re(r#""(?:[^"\\]|\\.)*""#));

/// `f"{v:g}"`: six significant digits, trailing zeros dropped, an exponent outside 1e-4..1e6.
pub(crate) fn fmt_g(v: f64) -> String {
    if v == 0.0 {
        return if v.is_sign_negative() {
            "-0".to_owned()
        } else {
            "0".to_owned()
        };
    }
    if v.is_infinite() {
        return if v > 0.0 {
            "inf".to_owned()
        } else {
            "-inf".to_owned()
        };
    }
    let sci = format!("{v:.5e}");
    let (mantissa, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    let trim = |s: &str| {
        if s.contains('.') {
            s.trim_end_matches('0').trim_end_matches('.').to_owned()
        } else {
            s.to_owned()
        }
    };
    if (-4..6).contains(&exp) {
        let decimals = usize::try_from(5 - exp).unwrap_or(0);
        trim(&format!("{v:.decimals$}"))
    } else {
        format!(
            "{}e{}{:02}",
            trim(mantissa),
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        )
    }
}

fn stated(value: f64, text: &str) -> bool {
    re(&format!(
        r"(?<![\d.]){}(?![\d])",
        fancy_regex::escape(&fmt_g(value))
    ))
    .is_match(text)
    .unwrap_or(false)
}

fn trivial(v: f64) -> bool {
    TRIVIAL.contains(&v) || v.abs() < 1e-3
}

/// (label, key, account) for every claim labeled one of [`OURS`] under `path`, sorted by label then key; with `figures_only`, only those naming a figure.
pub(crate) fn tunables(cur: &Cur, path: &str, figures_only: bool) -> Vec<(String, String, String)> {
    let mut out: Vec<(String, String, String)> = cur
        .iter()
        .filter(|r| OURS.contains(&r.claim.backing.as_str()) && r.key.starts_with(path))
        .filter(|r| !figures_only || FIGURE.is_match(&r.claim.account).unwrap_or(false))
        .map(|r| {
            (
                r.claim.backing.clone(),
                r.key.clone(),
                r.claim.account.clone(),
            )
        })
        .collect();
    out.sort_by(|a, b| {
        let rank = |l: &str| OURS.iter().position(|o| *o == l).unwrap_or(0);
        (rank(&a.0), &a.1).cmp(&(rank(&b.0), &b.1))
    });
    out
}

/// (function, line, value) for every non-trivial number in a Rust function's body its claims never state.
pub(crate) fn unstated_rust(
    source: &str,
    unit_text: &HashMap<String, String>,
) -> Vec<(String, usize, f64)> {
    let source = match CFG_TEST.find(source).ok().flatten() {
        Some(m) => &source[..m.start()],
        None => source,
    };
    let mut out = Vec::new();
    for (qual, kind, first, _, _, body) in items(source, 0, "", false) {
        if kind != "function" && kind != "method" {
            continue;
        }
        let name = qual
            .rsplit_once('.')
            .map_or(qual.as_str(), |p| p.1)
            .to_owned();
        let text = unit_text.get(&name).map_or("", String::as_str);
        for (i, line) in super::units::splitlines(&body).iter().enumerate() {
            let code = LINE_COMMENT.replace_all(line, "");
            let code = STRING.replace_all(&code, "").into_owned();
            for m in RUST_NUMBER.captures_iter(&code).flatten() {
                let whole = m.get(0).unwrap_or_else(|| unreachable!());
                let v: f64 = m[1].replace('_', "").parse().unwrap_or(0.0);
                let index = code[whole.end()..].starts_with(']')
                    && code[..whole.start()].trim_end().ends_with('[');
                if trivial(v) || stated(v, text) || index {
                    continue;
                }
                out.push((name.clone(), first + i, v));
            }
        }
    }
    out
}

/// One audit line: (file, line, function, value).
pub(crate) type Found = (String, usize, String, f64);

/// Every number `unstated` finds in the map code under `root` (and `path`): the `.py` files by the runner, the Rust here.
pub(crate) fn inline(
    reader: &mut Reader,
    root: &Path,
    cur: &Cur,
    path: &str,
) -> Result<Vec<Found>, Fail> {
    let mut text: HashMap<String, HashMap<String, String>> = HashMap::new();
    for row in cur.iter() {
        let unit = row.key.split_once('#').map_or(row.key.as_str(), |p| p.0);
        let (f, name) = unit.split_once("::").unwrap_or((unit, ""));
        let bare = name.rsplit_once('.').map_or(name, |p| p.1);
        let bag = text
            .entry(f.to_owned())
            .or_default()
            .entry(bare.to_owned())
            .or_default();
        let _ = write!(bag, " {} {}", row.claim.label, row.claim.account);
    }
    let empty = HashMap::new();
    let mut out = Vec::new();
    for p in rglob(&root.join("l7r"), ".py") {
        let r = rel(&p, root);
        if !MAP_CODE.iter().any(|m| r.starts_with(m)) || !r.starts_with(path) {
            continue;
        }
        let source = read_text(&p)?;
        let got = reader.ask(
            "tunables_unstated",
            &json!([source, text.get(&r).unwrap_or(&empty)]),
        );
        let got = got?;
        for t in got.as_array().into_iter().flatten() {
            let line = t[1]
                .as_u64()
                .and_then(|n| usize::try_from(n).ok())
                .unwrap_or(0);
            out.push((
                r.clone(),
                line,
                t[0].as_str().unwrap_or_default().to_owned(),
                t[2].as_f64().unwrap_or(0.0),
            ));
        }
    }
    for p in rglob(&root.join("rust"), ".rs") {
        let r = rel(&p, root);
        if p.components().any(|c| c.as_os_str() == "target")
            || !MAP_CODE.iter().any(|m| r.starts_with(m))
            || !r.starts_with(path)
        {
            continue;
        }
        for (f, line, v) in unstated_rust(&read_text(&p)?, text.get(&r).unwrap_or(&empty)) {
            out.push((r.clone(), line, f, v));
        }
    }
    Ok(out)
}

/// The inline audit, or its count by file.
pub(crate) fn render_inline(found: &[Found], count: bool) -> String {
    let mut per: Vec<(String, usize)> = Vec::new();
    for (f, ..) in found {
        match per.iter_mut().find(|(g, _)| g == f) {
            Some(e) => e.1 += 1,
            None => per.push((f.clone(), 1)),
        }
    }
    let mut lines = vec![format!("tunables --inline: {} number(s) in {} file(s) no claim states - ours by default, a knob (docs/approach-checklist.md A3)", found.len(), per.len())];
    if count {
        per.sort_by(|a, b| b.1.cmp(&a.1));
        lines.extend(per.iter().map(|(f, n)| format!("  {n:>5}  {f}")));
    } else {
        lines.extend(
            found
                .iter()
                .map(|(f, line, func, v)| format!("  {f}:{line} {func} {}", fmt_g(*v))),
        );
    }
    lines.join("\n")
}

/// The list, or its counts, with the line that says what it is for.
pub(crate) fn render(found: &[(String, String, String)], count: bool) -> String {
    let tally = |l: &str| found.iter().filter(|f| f.0 == l).count();
    let head = if found.is_empty() {
        "tunables: none".to_owned()
    } else {
        let parts: Vec<String> = OURS
            .iter()
            .filter(|l| tally(l) > 0)
            .map(|l| format!("{l} {}", tally(l)))
            .collect();
        format!("tunables: {}", parts.join(", "))
    };
    let mut lines = vec![format!("{head} - values no source states: a goal and a knob, never a target to defend (docs/approach-checklist.md A3)")];
    if !count {
        lines.extend(
            found
                .iter()
                .map(|(label, key, account)| format!("  {label:<12} {key} - {account}")),
        );
    }
    lines.join("\n")
}

#[cfg(test)]
mod tests;
