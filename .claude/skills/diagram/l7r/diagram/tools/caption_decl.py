"""The one-time migration of feature 286: a hand sheet's captions from hand-SEATED to DECLARED.

Before feature 286 a hand sheet's caption stood where a person (or `make seat-label WRITE=1`) had set it, and what it
named was read from where it stood: the part of its group it lay in or nearest, the nearest drawn shape of its kind, and
the texts that stood one under another were one caption. Feature 286 places every caption in the render pipeline
(`labels.hand_sheet.placed`), and a caption declares only its text and what it names (plan D1):

- a caption names the non-text shapes of the tagged group it stands in when that group has one caption; otherwise it
  carries `data-names="<id> ..."`, naming the drawn things it names by their `data-id`;
- a text marked `data-cont="1"` is the next line of the caption before it;
- it has no `x`, `y`, `text-anchor` or `transform`, and no leader is drawn for it.

This module reads a sheet the OLD way - the position readings are kept here and nowhere else, for this one use - and
writes the declarations that reading implies, so no caption changes what it names. A caption the old reading found no
subject for is left as it stands and reported: its declaration is the author's to write.

    python3 -m l7r.diagram.tools.caption_decl <sheet.svg> [--write]
"""

from __future__ import annotations

import math
import re

from l7r.diagram.labels.geom import inside
from l7r.diagram.labels.hand_sheet import Shape, _area, _box_gap, _self_tagged, bbox, read_sheet, start_tags
from l7r.diagram.labels.standard import PITCH_EM


def stacked_captions(shapes: list[Shape]) -> list[list[int]]:
    """The sheet's captions as the old reading found them, each the list of its `<text>` indices: the texts of one
    tagged group that STACK - each the next line under the last - are one caption (feature 267)."""
    groups: dict[int, list[list[int]]] = {}
    order: list[int] = []
    for i, s in enumerate(shapes):
        if s.tag == "text" and s.text and s.kind and s.kind != "-":
            key = s.group or -i - 1
            if key not in groups:
                groups[key] = []
                order.append(key)
            runs = groups[key]
            if runs and stacks_under(shapes[runs[-1][-1]], s):
                runs[-1].append(i)
            else:
                runs.append([i])
    return [run for k in order for run in groups[k]]


def stacks_under(above: Shape, below: Shape) -> bool:
    """Is `below` the next line of `above`'s caption: under it by at most two line pitches, and sharing at least half the
    narrower block's width with it."""
    ay, by = above.center[1], below.center[1]
    pitch = PITCH_EM * max(above.size, below.size)
    ax0, _ay0, ax1, _ay1 = bbox(above.poly)
    bx0, _by0, bx1, _by1 = bbox(below.poly)
    shared = min(ax1, bx1) - max(ax0, bx0)
    return 0 < by - ay <= 2 * pitch and shared >= 0.5 * min(ax1 - ax0, bx1 - bx0)


def cluster_of(seed: Shape, same: list[Shape], reach: float) -> list[Shape]:
    """`seed` and every shape of `same` joined to it through shapes within `reach` of each other."""
    out = [seed]
    grew = True
    while grew:
        grew = False
        for s in same:
            if s not in out and any(_box_gap(s.poly, o.poly) <= reach for o in out):
                out.append(s)
                grew = True
    return out


def read_parts(caption: Shape, shapes: list[Shape]) -> list[Shape]:
    """What the old reading took a caption to name, from where it stood (feature 267): its group's shapes; in a group
    of several captions, the rect it lies in, else the cluster nearest it; with nothing in its group, the rect of its
    kind it lies in, else the cluster of its kind nearest it. Empty when nothing is drawn for it."""
    own = [s for s in shapes if s.group == caption.group and s.group and s.tag != "text" and not s.leader]
    holding = [s for s in own if s.tag == "rect" and inside(caption.center[0], caption.center[1], s.poly)]
    if len(own) > 1 and len([s for s in shapes if s.tag == "text" and s.group == caption.group]) > 1:
        near = min(own, key=lambda s: math.dist(_mid(s.poly), caption.center))
        own = [min(holding, key=lambda s: _area(s.poly))] if holding else cluster_of(near, own, 2 * caption.size)
    if not own:
        same = [s for s in shapes if s.kind == caption.kind and s.tag != "text" and not s.leader]
        if not same:
            return []
        held = [s for s in same if s.tag == "rect" and inside(caption.center[0], caption.center[1], s.poly)]
        own = [min(held, key=lambda s: _area(s.poly))] if held else cluster_of(min(same, key=lambda s: math.dist(_mid(s.poly), caption.center)), same, 2 * caption.size)
    return own


def _mid(poly: list[tuple[float, float]]) -> tuple[float, float]:
    x0, y0, x1, y1 = bbox(poly)
    return (x0 + x1) / 2, (y0 + y1) / 2


_PLACE_ATTRS = re.compile(r'\s(?:x|y|dx|dy|text-anchor|transform)="[^"]*"')


def declare(src: str) -> tuple[str, list[str]]:
    """The sheet with every caption declared (see the module), and the captions left as they stood because nothing was
    found for them to name."""
    shapes, _view = read_sheet(src)
    caps = stacked_captions(shapes)
    per_group: dict[int, int] = {}
    for idx in caps:
        per_group[shapes[idx[0]].group] = per_group.get(shapes[idx[0]].group, 0) + 1
    taken = set(re.findall(r'\sdata-id="([^"]*)"', src))
    new_ids: dict[int, str] = {}  # element index -> the id written onto it
    text_edits: dict[int, str] = {}  # element index -> the attributes to add
    left: list[str] = []
    for idx in caps:
        head = shapes[idx[0]]
        own = read_parts(head, shapes)
        if not own:
            left.append(" / ".join(shapes[i].text for i in idx))
            continue
        group_own = [s for s in shapes if s.group == head.group and s.group and s.tag != "text" and not s.leader]
        names = ""
        if per_group[head.group] > 1 or _self_tagged(head) or {s.at for s in own} != {s.at for s in group_own}:
            ids = []
            for s in own:
                if s.element is not None and s.element.get("data-id"):
                    ids.append(s.element.get("data-id", ""))
                    continue
                if s.at not in new_ids:
                    stem = re.sub(r"[^a-z0-9]+", "-", s.kind.lower()).strip("-") or "part"
                    n = 1
                    while f"{stem}-{n}" in taken:
                        n += 1
                    taken.add(f"{stem}-{n}")
                    new_ids[s.at] = f"{stem}-{n}"
                ids.append(new_ids[s.at])
            names = f' data-names="{" ".join(dict.fromkeys(ids))}"'
        text_edits[head.at] = names
        for i in idx[1:]:
            text_edits[shapes[i].at] = ' data-cont="1"'
    tags = start_tags(src)
    out: list[str] = []
    last = 0
    leader = re.compile(r'<line\b[^>]*\sdata-leader="1"[^>]*/>')
    for k, (a, b) in enumerate(tags):
        if k not in new_ids and k not in text_edits:
            continue
        out.append(src[last:a])
        tag = src[a:b]
        if k in new_ids:
            tag = re.sub(r"^(<\w+)", rf'\1 data-id="{new_ids[k]}"', tag)
        else:
            tag = _PLACE_ATTRS.sub("", tag)[:-1] + text_edits[k] + ">"
            end = src.index("</text>", b)
            body = re.sub(r"<tspan\b[^>]*>", lambda m: _PLACE_ATTRS.sub("", m.group(0)), src[b:end])
            out.append(tag + body)
            last = end
            continue
        out.append(tag)
        last = b
    out.append(src[last:])
    return re.sub(r"\n[ \t]*" + leader.pattern, "", "".join(out)), left
