//! The seated captions written into the sheet's text (feature 449 T202): each declared line element rewritten in place at its seat -
//! `x`, `y` and a middle anchor, its own attributes kept but the declaration's marks (`data-cont`, `data-names`), a turn where the caption
//! turns - and a leader written after the caption's last line, marked `data-leader="1"` as the sheet reader knows it and carrying the
//! caption's own `data-kind` where the caption carries one (a leader is ink, and the census refuses ink with no kind). Everything else of
//! the sheet is left as it was. Coordinates are written in the element's parent frame, as the caption writer before T202 wrote them
//! (`labels/svg.rs`, deleted with the old placer: lines 1.15 em apart, the block turned about its center).
//!
//! Research: the placed text - NONE: seats written as text, deciding nothing about where a caption stands

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;

use super::captions::{Caption, BASELINE_EM, PITCH_EM};
use super::geom::Pt;
use super::search::Seat;
use super::Shape;
use crate::labels::hand_sheet::read::{angle, apply, inverse, Affine};
use crate::py::fixed;

static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([^\s=/<>"']+)\s*=\s*("[^"]*"|'[^']*')"#));

/// The attributes a placed caption no longer carries: its seat is written anew, and it is no longer a declaration.
const DROPPED: [&str; 8] = [
    "x",
    "y",
    "dx",
    "dy",
    "text-anchor",
    "transform",
    "data-cont",
    "data-names",
];

fn esc(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
}

/// The start tag's name as written (with its prefix, if any) and its kept attributes as written, in order.
fn tag_parts(start: &str) -> (String, Vec<String>, Option<String>, Option<String>) {
    let name: String = start[1..]
        .chars()
        .take_while(|c| !c.is_whitespace() && *c != '>' && *c != '/')
        .collect();
    let mut kept = Vec::new();
    let (mut fill, mut kind) = (None, None);
    for c in ATTR.captures_iter(start).map_while(Result::ok) {
        let key = &c[1];
        if key == "fill" {
            fill = Some(c[2][1..c[2].len() - 1].to_owned());
        }
        if key == "data-kind" {
            kind = Some(c[0].to_owned());
        }
        if !DROPPED.contains(&key) {
            kept.push(c[0].to_owned());
        }
    }
    (name, kept, fill, kind)
}

/// Where a tagged group closes - the byte of its closing tag - and whether each of `children` (start tags' bytes) is a child of the
/// group itself rather than of an element within it; `None` for a group written `<g .../>`.
#[must_use]
pub fn group_end(
    src: &str,
    open: (usize, usize),
    children: &[usize],
) -> Option<(usize, Vec<bool>)> {
    if src[open.0..open.1].ends_with("/>") {
        return None;
    }
    let mut direct = vec![false; children.len()];
    let (mut depth, mut at) = (1_usize, open.1);
    while let Some(i) = src[at..].find('<').map(|k| at + k) {
        let rest = &src[i..];
        let skip = |end: &str| rest.find(end).map_or(src.len(), |k| i + k + end.len());
        if rest.starts_with("<!--") {
            at = skip("-->");
        } else if rest.starts_with("<![CDATA[") {
            at = skip("]]>");
        } else if rest.starts_with("<!") || rest.starts_with("<?") {
            at = skip(">");
        } else if rest.starts_with("</") {
            depth -= 1;
            if depth == 0 {
                return Some((i, direct));
            }
            at = skip(">");
        } else {
            if let Some(k) = children.iter().position(|&c| c == i) {
                direct[k] = depth == 1;
            }
            // the tag's end, a `>` inside a quoted value passed over
            let mut quote = None;
            let mut end = src.len();
            for (k, ch) in rest.char_indices().skip(1) {
                match (quote, ch) {
                    (None, '"' | '\'') => quote = Some(ch),
                    (Some(q), c) if c == q => quote = None,
                    (None, '>') => {
                        end = i + k + 1;
                        break;
                    }
                    _ => {}
                }
            }
            if !src[..end].ends_with("/>") {
                depth += 1;
            }
            at = end;
        }
    }
    None
}

/// A byte offset for each code point offset of the text.
#[must_use]
pub fn byte_at(src: &str) -> Vec<usize> {
    src.char_indices()
        .map(|(b, _)| b)
        .chain(std::iter::once(src.len()))
        .collect()
}

/// A caption's head element as the leader is written after it: its tag's name, ink and kind, its frame's inverse, its letter size, and
/// where its start tag begins.
struct Head {
    name: String,
    fill: Option<String>,
    kind: Option<String>,
    inv: Affine,
    size: f64,
    at: usize,
}

/// One line element written at its seat: `x` and the first baseline `y` in its frame, `turn` its angle there, its lines `pitch` apart.
fn element(
    name: &str,
    kept: &[String],
    (c, y, turn): (Pt, f64, f64),
    (lines, pitch): (&[String], f64),
) -> String {
    let body = if lines.len() == 1 {
        esc(&lines[0])
    } else {
        let span = name.strip_suffix("text").unwrap_or_default().to_owned() + "tspan";
        lines
            .iter()
            .enumerate()
            .fold(String::new(), |mut out, (k, l)| {
                let dy = if k == 0 { 0.0 } else { pitch };
                let _ = write!(
                    out,
                    "<{span} x=\"{}\" dy=\"{}\">{}</{span}>",
                    fixed(c.0, 1),
                    fixed(dy, 1),
                    esc(l)
                );
                out
            })
    };
    let rotate = if fixed(turn, 1) == "0.0" || fixed(turn, 1) == "-0.0" {
        String::new()
    } else {
        format!(
            " transform=\"rotate({} {} {})\"",
            fixed(turn, 1),
            fixed(c.0, 1),
            fixed(c.1, 1)
        )
    };
    let attrs = kept.iter().fold(String::new(), |mut out, a| {
        let _ = write!(out, " {a}");
        out
    });
    format!(
        "<{name} x=\"{}\" y=\"{}\" text-anchor=\"middle\"{attrs}{rotate}>{body}</{name}>",
        fixed(c.0, 1),
        fixed(y, 1)
    )
}

/// A caption's leader, on its own line at the head's indent, in the head's frame.
///
/// Research: the leader's stroke - CONVENTION: a leader is drawn in its caption's ink, 0.08 of its letter size wide and at least 0.6 px, round-capped, the leader the caption writer before T202 drew (`labels/svg.rs`'s `leader_svg`, deleted with the old placer); a drawn size on the sheet, not in the world
fn leader_line(src: &str, head: &Head, (a, b): (Pt, Pt)) -> String {
    let line = head
        .name
        .strip_suffix("text")
        .unwrap_or_default()
        .to_owned()
        + "line";
    let (p, q) = (apply(head.inv, a), apply(head.inv, b));
    let indent: String = src[..head.at]
        .chars()
        .rev()
        .take_while(|c| *c == ' ' || *c == '\t')
        .collect();
    let stroke = head.fill.clone().unwrap_or_else(|| "#3A2E1C".to_owned());
    format!(
        "\n{indent}<{line} x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"{stroke}\" stroke-width=\"{}\" stroke-linecap=\"round\"{} data-leader=\"1\"/>",
        fixed(p.0, 1),
        fixed(p.1, 1),
        fixed(q.0, 1),
        fixed(q.1, 1),
        fixed((0.08 * head.size).max(0.6), 2),
        head.kind.as_ref().map(|k| format!(" {k}")).unwrap_or_default()
    )
}

/// The sheet's text with every caption written at its seat: in place, or - a caption declared inside its tagged group - at the group's
/// end, so it paints after its own feature.
///
/// Research:
///     written last in its group - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: captions are placed last, once the map is finished - and drawn last in their own group, after the feature they name (a caption declared before its building's shapes was painted over by them: observed 2026-11-19, a pool sheet's RESIDENCE); kept in its group, so it keeps its kind
///     the block written - CONVENTION: a caption's elements are stacked as one block centered on its seat, each line 1.15 em below the last (`PITCH_EM`) and its baseline 0.85 em below its line's top (`BASELINE_EM`), so the block drawn is the block the placer seated
#[must_use]
pub fn write(src: &str, shapes: &[Shape], seated: &[(Caption, Seat)]) -> String {
    let spans = crate::hand_sheet::start_tags(src);
    let bytes = byte_at(src);
    let mut edits: Vec<(usize, usize, String)> = Vec::new();
    for (cap, seat) in seated {
        let mut lines_of: Vec<Vec<String>> = cap.elems.iter().map(|e| e.lines.clone()).collect();
        if let Some(cut) = &seat.cut {
            lines_of[0].clone_from(cut);
        }
        #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
        let height = |i: usize| lines_of[i].len() as f64 * PITCH_EM * cap.elems[i].size;
        let total: f64 = (0..cap.elems.len()).map(height).sum();
        let mut top = -total / 2.0;
        let mut last_end = 0;
        let mut head = None;
        let mut moved = String::new();
        for (i, e) in cap.elems.iter().enumerate() {
            let s = &shapes[e.shape];
            // every element of the sheet has its start tag, numbered as the reader numbers it
            let (c0, c1) = spans[s.at];
            let (b0, b1) = (bytes[c0], bytes[c1]);
            let start = &src[b0..b1];
            let (name, kept, fill, kind) = tag_parts(start);
            let end = if start.ends_with("/>") {
                b1
            } else {
                let close = format!("</{name}>");
                src[b1..]
                    .find(&close)
                    .map_or(b1, |at| b1 + at + close.len())
            };
            let inv = inverse(s.frame);
            let c = apply(inv, seat.center);
            let turn = seat.angle - angle(s.frame);
            let pitch = PITCH_EM * e.size;
            let y = c.1 + top + BASELINE_EM * e.size;
            top += height(i);
            let text = element(&name, &kept, (c, y, turn), (&lines_of[i], pitch));
            if cap.move_to.is_some() {
                // written at its group's end: taken from here with the line it stood on
                let indent: String = src[..b0]
                    .chars()
                    .rev()
                    .take_while(|c| *c == ' ' || *c == '\t')
                    .collect();
                let from =
                    b0 - indent.len() - usize::from(src[..b0 - indent.len()].ends_with('\n'));
                edits.push((from, end, String::new()));
                moved.push('\n');
                moved.push_str(&indent);
                moved.push_str(&text);
            } else {
                edits.push((b0, end, text));
            }
            last_end = end;
            if i == 0 {
                head = Some(Head {
                    name,
                    fill,
                    kind,
                    inv,
                    size: e.size,
                    at: b0,
                });
            }
        }
        let leader = match (seat.leader, head) {
            (Some(ends), Some(head)) => leader_line(src, &head, ends),
            _ => String::new(),
        };
        match cap.move_to {
            Some(at) => edits.push((at, at, moved + &leader)),
            None => edits.push((last_end, last_end, leader)),
        }
    }
    edits.sort_by_key(|e| (e.0, e.1));
    let mut out = String::with_capacity(src.len() + 64 * edits.len());
    let mut at = 0;
    for (b0, b1, text) in edits {
        out.push_str(&src[at..b0]);
        out.push_str(&text);
        at = b1;
    }
    out.push_str(&src[at..]);
    out
}
