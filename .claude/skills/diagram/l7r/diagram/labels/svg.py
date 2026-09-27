"""A placed caption written as SVG (feature 266) - one writer for the compound composer and `make seat-label`.

The settlement engine draws through its own `label()`, which carries its halo, its record and its interactive class;
the Mode A paths write plain SVG, and they write it here so a caption and its leader come out the same way in both.
The geometry is `label()`'s: the block is centered 0.275 em above the first line's baseline, lines stand 1.15 em apart
about that center, and the whole block turns about its center by the placement's angle.
"""

from __future__ import annotations

from .placer import Placement
from .standard import CENTER_ABOVE_BASELINE_EM, PITCH_EM


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _kind(kind: str) -> str:
    return f' data-kind="{kind}"' if kind else ""


def caption_svg(p: Placement, size: float, style: str, fill: str, kind: str = "") -> str:
    """The `<text>` for a placement. `style` is the element's own font attributes (` font-style="italic"`)."""
    cx, cy = p.x, p.y - CENTER_ABOVE_BASELINE_EM * size
    turn = f' transform="rotate({p.angle:.1f} {cx:.1f} {cy:.1f})"' if round(p.angle, 1) else ""
    n = len(p.lines)
    pitch = PITCH_EM * size
    y0 = p.y - (n - 1) * pitch / 2
    one = _esc(p.lines[0])
    body = one if n == 1 else "".join(f'<tspan x="{p.x:.1f}" dy="{0 if i == 0 else pitch:.1f}">{_esc(ln)}</tspan>' for i, ln in enumerate(p.lines))
    return f'<text x="{p.x:.1f}" y="{y0:.1f}" text-anchor="middle" font-size="{size:g}"{style} fill="{fill}"{turn}{_kind(kind)}>{body}</text>'


def leader_svg(p: Placement, size: float, stroke: str, kind: str = "", mark: bool = False) -> str:
    """The leader line for a placement that has one, else the empty string. `mark` tags it `data-leader="1"`, which is
    how `make seat-label` finds its own leaders on a hand-drawn sheet."""
    if p.leader is None:
        return ""
    (x1, y1), (x2, y2) = p.leader
    tag = ' data-leader="1"' if mark else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{max(0.6, 0.08 * size):.2f}" stroke-linecap="round"{_kind(kind)}{tag}/>'
