//! A placed caption written as SVG (feature 449 T151, `labels/svg.py` whole; feature 266): one writer for the compound composer and the
//! hand-drawn sheets. The geometry is `label()`'s: the block is centered 0.275 em above the first line's baseline, lines stand 1.15 em
//! apart about that center, and the whole block turns about its center by the placement's angle. Every figure is printed as the
//! Python's f-string printed it ([`crate::py::fixed`], [`crate::py::fmt_g`]), so a caption written from the same placement is the same
//! text.
//!
//! Research: the caption's SVG - NONE: a placement written as text, deciding nothing about where it stands

use std::fmt::Write as _;

use super::placer::Placement;
use super::standard::{CENTER_ABOVE_BASELINE_EM, PITCH_EM};
use crate::py::{fixed, fmt_g, max, round_to};

fn esc(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
}

fn kind_attr(kind: &str) -> String {
    if kind.is_empty() {
        String::new()
    } else {
        format!(" data-kind=\"{kind}\"")
    }
}

/// The `<text>` for a placement. `style` is the element's own font attributes (` font-style="italic"`); `names`, the `data-id`s of the
/// drawn shapes the caption names, written as its `data-names` - a hand sheet's declaration (feature 340).
#[must_use]
pub fn caption_svg(
    p: &Placement,
    size: f64,
    style: &str,
    fill: &str,
    kind: &str,
    names: &str,
) -> String {
    let (cx, cy) = (p.x, p.y - CENTER_ABOVE_BASELINE_EM * size);
    let turn = if round_to(p.angle, 1) == 0.0 {
        String::new()
    } else {
        format!(
            " transform=\"rotate({} {} {})\"",
            fixed(p.angle, 1),
            fixed(cx, 1),
            fixed(cy, 1)
        )
    };
    #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
    let n = p.lines.len() as f64;
    let pitch = PITCH_EM * size;
    let y0 = p.y - (n - 1.0) * pitch / 2.0;
    let body = if p.lines.len() == 1 {
        esc(&p.lines[0])
    } else {
        p.lines
            .iter()
            .enumerate()
            .fold(String::new(), |mut out, (i, ln)| {
                let dy = if i == 0 { 0.0 } else { pitch };
                let _ = write!(
                    out,
                    "<tspan x=\"{}\" dy=\"{}\">{}</tspan>",
                    fixed(p.x, 1),
                    fixed(dy, 1),
                    esc(ln)
                );
                out
            })
    };
    let names = if names.is_empty() {
        String::new()
    } else {
        format!(" data-names=\"{names}\"")
    };
    format!(
        "<text x=\"{}\" y=\"{}\" text-anchor=\"middle\" font-size=\"{}\"{style} fill=\"{fill}\"{turn}{}{names}>{body}</text>",
        fixed(p.x, 1),
        fixed(y0, 1),
        fmt_g(size),
        kind_attr(kind)
    )
}

/// The leader line for a placement that has one, else the empty string. `mark` tags it `data-leader="1"`, which is how a placed
/// hand-drawn sheet's leaders are told from its drawn lines.
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.6 (thinnest leader stroke); 0.08 (leader stroke as a share of font size)
#[must_use]
pub fn leader_svg(p: &Placement, size: f64, stroke: &str, kind: &str, mark: bool) -> String {
    let Some(((x1, y1), (x2, y2))) = p.leader else {
        return String::new();
    };
    let tag = if mark { " data-leader=\"1\"" } else { "" };
    format!(
        "<line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"{stroke}\" stroke-width=\"{}\" stroke-linecap=\"round\"{}{tag}/>",
        fixed(x1, 1),
        fixed(y1, 1),
        fixed(x2, 1),
        fixed(y2, 1),
        fixed(max(0.6, 0.08 * size), 2),
        kind_attr(kind)
    )
}

#[cfg(test)]
mod tests;
