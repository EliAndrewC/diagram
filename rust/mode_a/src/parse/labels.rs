//! The sheet's text labels with an ESTIMATED box (feature 449 T170, `parse.py`'s `_parse_labels`, `_bold_char_w` and `_unescape`): the
//! box from the font size by the string's length, a wrapped caption one line per `<tspan>`, a quarter-turned label stood on its end.
//!
//! Research:
//!     the labels' boxes - NONE: a caption's box estimated from its text, deciding nothing about a building

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::strip;

use super::{cp, Label, CAPS_RATIO, CHAR_W_BOLD, CHAR_W_BOLD_MIXED, CHAR_W_FRAC};
use crate::py::{float, min, sum};
use crate::sheet::Offsets;
use crate::tagged::attrs;

static TEXT: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<text\s([^>]*)>(.*?)</text>"));
static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w-]+)="([^"]*)""#));
static INNER_TAG: LazyLock<Regex> = LazyLock::new(|| py(r"<[^>]*>"));
static TSPAN: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"(?s)<tspan\b(?=[^>]*?\bx="([\-\d.]*)"|)(?=[^>]*?\bdy="([\-\d.]*)"|)[^>]*>(.*?)</tspan>"#)
});
static TSPAN_ALL: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<tspan\b[^>]*>.*?</tspan>"));
static ROTATE: LazyLock<Regex> =
    LazyLock::new(|| py(r"rotate\(\s*([\-\d.]+)[\s,]+([\-\d.]+)[\s,]+([\-\d.]+)\s*\)"));
static LETTER: LazyLock<Regex> = LazyLock::new(|| py(r"\A\p{L}\z"));

/// A text's characters as drawn: the three entities the sheets write.
fn unescape(s: &str) -> String {
    s.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
}

/// Per-character advance for BOLD text: caps labels run wider than mixed-case ones (a letter is Python's `isalpha`, a Unicode letter).
fn bold_char_w(text: &str) -> f64 {
    let letters: Vec<char> = text
        .chars()
        .filter(|c| LETTER.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false))
        .collect();
    let caps = if letters.is_empty() {
        0.0
    } else {
        count(letters.iter().filter(|c| c.is_uppercase()).count()) / count(letters.len())
    };
    if caps >= CAPS_RATIO {
        CHAR_W_BOLD
    } else {
        CHAR_W_BOLD_MIXED
    }
}

/// A count as Python's `int` meets a float: exactly, a label being far shorter than 2^53 characters.
fn count(n: usize) -> f64 {
    f64::from(u32::try_from(n).unwrap_or(u32::MAX))
}

/// Text labels with an estimated box (font size by string length) and their draw-order offset.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.78 (font ascent figure)
///
/// # Errors
/// A position, size, spacing, line drop or rotation the Python's `float()` refuses.
pub fn parse_labels(text: &str) -> Result<Vec<Label>, Error> {
    let offsets = Offsets::new(text);
    let mut out = Vec::new();
    for found in TEXT.captures_iter(text).flatten() {
        let attr = attrs(&ATTR, &found[1]);
        let body = &found[2];
        let content = unescape(&INNER_TAG.replace_all(body, ""));
        let content = strip(&content);
        let (Some(xs), Some(ys)) = (attr.get("x"), attr.get("y")) else {
            continue;
        };
        if content.is_empty() {
            continue;
        }
        let (at_x, at_y) = (float(xs)?, float(ys)?);
        let fs = float(attr.get("font-size").map_or("13", String::as_str))?;
        let ls = float(attr.get("letter-spacing").map_or("0", String::as_str))?;
        // a wrapped caption is one line per <tspan dy>: its block is its widest line by its lines' height (feature 267); only tspans that
        // each set their own x are lines, an inline tspan continuing the line it is in
        let spans: Vec<(String, String, String)> = TSPAN
            .captures_iter(body)
            .flatten()
            .map(|c| {
                let g = |i| c.get(i).map_or(String::new(), |m| m.as_str().to_owned());
                (g(1), g(2), g(3))
            })
            .collect();
        let wrapped = spans.len() > 1
            && spans.iter().all(|(x, _, _)| !x.is_empty())
            && strip(&TSPAN_ALL.replace_all(body, "")).is_empty();
        let lines: Vec<String> = if wrapped {
            spans
                .iter()
                .map(|(_, _, t)| strip(&unescape(t)).to_owned())
                .collect()
        } else {
            vec![content.to_owned()]
        };
        let drop = if wrapped {
            sum(spans[1..]
                .iter()
                .map(|(_, dy, _)| if dy.is_empty() { Ok(0.0) } else { float(dy) })
                .collect::<Result<Vec<f64>, Error>>()?)
        } else {
            0.0
        };
        let frac = if attr.get("font-weight").map(String::as_str) == Some("bold") {
            bold_char_w(content)
        } else {
            CHAR_W_FRAC
        };
        let mut widest: Option<f64> = None;
        for line in &lines {
            let n = line.chars().count();
            let v = count(n) * fs * frac + ls * count(n.saturating_sub(1));
            widest = Some(widest.map_or(v, |best| if v > best { v } else { best }));
        }
        let mut width = widest.unwrap_or_default();
        let mut height = fs + drop;
        let anchor = attr.get("text-anchor").map_or("start", String::as_str);
        let mut left = match anchor {
            "middle" => at_x - width / 2.0,
            "end" => at_x - width,
            _ => at_x,
        };
        let mut top = at_y - fs * 0.78;
        if let Some(rot) = ROTATE
            .captures(attr.get("transform").map_or("", String::as_str))
            .ok()
            .flatten()
        {
            if (float(&rot[1])?.abs() - 90.0).abs() < 1.0 {
                // a quarter-turned label (a river's name along its band) stands on its end about its pivot
                let (px, py_) = (float(&rot[2])?, float(&rot[3])?);
                let sign = if float(&rot[1])? > 0.0 { 1.0 } else { -1.0 };
                let turn = |cx: f64, cy: f64| (px - sign * (cy - py_), py_ + sign * (cx - px));
                let (ax, ay) = turn(left, top);
                let (bx, by) = turn(left + width, top + height);
                (left, top, width, height) =
                    (min(ax, bx), min(ay, by), (bx - ax).abs(), (by - ay).abs());
            }
        }
        out.push(Label {
            x: left,
            y: top,
            w: width,
            h: height,
            text: lines.join(" "),
            pos: cp(&offsets, found.get(0).map_or(0, |g| g.start())),
        });
    }
    Ok(out)
}
