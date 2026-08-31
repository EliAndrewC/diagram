"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

import math
import os

from l7r.diagram.settlement import moat_swept_tap
from l7r.diagram.waterfields import AZE, BEAN_GREEN, aze_w, build_comb, hem_on_paddy

# THE ORDER IS A CONTRACT, AND THIS IMPORT IS WHAT HOLDS IT. `s` comes from the part IMMEDIATELY
# ABOVE this one, not from `frame`, so Python cannot execute this part until that one has
# finished drawing. The first cut of this split had every part import from `frame`, which
# constrained only that `frame` ran first - and `ruff`'s isort then sorted the list in
# `__init__.py` ALPHABETICALLY, so `fields` (which calls `s.finish()`) ran fourth of seven and
# the wharf, the yashiki band and the trade works drew into a map already written to disk.
# Caught by settlement-review, 2026-08-31; invisible to the gate, which rolls no wip map.
from .civic import s
from .frame import MOAT, PLOT_ACROSS, RIVER, ROW_STEP

# the wharf works and the aqueduct now anchor the frame's east; a modest uniform margin still
# shows each road running off the edge, and the south side carries the Imperial road caption,
# which finish() seats AFTER the crop and so cannot widen it itself. The EAST margin is wide on
# purpose: the aqueduct's intake works on the river (~x3140) are the part of the system a reader
# traces first (spec 020, User Story 3), and the default crop cut them - plus the east road's
# river bridge - clean off the sheet.


_TORING = []  # (envelope, fall, drain) per field - ringed AFTER every field is drawn


def _below_drain(x, y, drain, fx, fy, berth=26.0):
    """Is (x, y) downslope of the drain COLLECTOR? Measured to the nearest point on the drain
    polyline and projected along the fall, which is what the check does - a global cut along the
    fall axis is not the same thing, and let a farmstead sit in the toe where the drain bends."""
    _best = (float("inf"), drain[0])
    for _k in range(len(drain) - 1):
        _ax, _ay = drain[_k]
        _bx, _by = drain[_k + 1]
        _dx, _dy = _bx - _ax, _by - _ay
        _ll = _dx * _dx + _dy * _dy or 1.0
        _t = max(0.0, min(1.0, ((x - _ax) * _dx + (y - _ay) * _dy) / _ll))
        _px, _py = _ax + _t * _dx, _ay + _t * _dy
        _d = math.hypot(x - _px, y - _py)
        if _d < _best[0]:
            _best = (_d, (_px, _py))
    _nx, _ny = _best[1]
    return (x - _nx) * fx + (y - _ny) * fy > -berth


def _on_cropland(x, y, pad=13.0):
    """Is (x, y) on drawn cropland - any field's paddy plots or its dry hem? Farmsteads stand
    BESIDE the fields they work, never on them, and the map records both."""
    for _f in s.M.get("fields") or []:
        for _pp in _f.get("plot_polys") or ():
            _xs = [q[0] for q in _pp]
            _ys = [q[1] for q in _pp]
            if min(_xs) - pad <= x <= max(_xs) + pad and min(_ys) - pad <= y <= max(_ys) + pad:
                return True
    for _d in s.M.get("dry_plots") or []:
        _pp = _d.get("poly") or _d.get("outline") or ()
        if _pp:
            _xs = [q[0] for q in _pp]
            _ys = [q[1] for q in _pp]
            if min(_xs) - pad <= x <= max(_xs) + pad and min(_ys) - pad <= y <= max(_ys) + pad:
                return True
    return False


def _ring_upslope(env, down_deg, drain=None, gaps=(30, 50, 70, 92)):
    """Seat farmsteads along the UPSLOPE perimeter of a field, at several standoffs. s.ring() walks
    the whole envelope and projects each seat OUTWARD, so on the low edge it throws households into
    the wet toe below the drainage line - and clipping the polygon does not help, because the cut
    edge still projects outward. So the perimeter is walked here and the low side simply skipped."""
    _fx, _fy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
    # the DRAIN is the real line, not the centroid: the check measures whether a dwelling sits
    # BELOW the drainage collector, and a seat can be upslope of the field's middle while still
    # sitting below its drain where that drain cuts across a corner.
    _dcut = max((q[0] * _fx + q[1] * _fy for q in drain), default=None) if drain else None
    if _dcut is not None:
        _dcut -= 30.0  # a clear berth above the drainage line, not a hairline
    _cx = sum(q[0] for q in env) / len(env)
    _cy = sum(q[1] for q in env) / len(env)
    _n = 0
    for _g in gaps:
        _k = 0
        while _k < len(env):
            _ax, _ay = env[_k]
            _bx, _by = env[(_k + 1) % len(env)]
            _seg = math.hypot(_bx - _ax, _by - _ay) or 1.0
            _steps = max(1, int(_seg // 17))
            for _t in range(_steps):
                _px = _ax + (_bx - _ax) * (_t + 0.5) / _steps
                _py = _ay + (_by - _ay) * (_t + 0.5) / _steps
                _ox, _oy = _px - _cx, _py - _cy
                _ol = math.hypot(_ox, _oy) or 1.0
                if (_ox / _ol) * _fx + (_oy / _ol) * _fy > 0.34:  # only the genuinely LOW side is skipped - a flank that merely tilts downhill still carries farms
                    continue
                _sx = _px + _ox / _ol * _g
                _sy = _py + _oy / _ol * _g
                if drain and _below_drain(_sx, _sy, drain, _fx, _fy):
                    continue  # below the drainage line - the wettest ground in the valley
                if _on_cropland(_sx, _sy):
                    continue
                if s.try_place(_sx, _sy, "plain"):
                    _n += 1
            _k += 1
    return _n


# ---- THE PADDY (GM 2026-08-11: no farmland on the capital, and there should be). Comb doctrine,
# tied to the declared flow: tapped off the river WITH the current, the fall running with it so the
# drain returns downstream of its own intake. Helper as the provincial-city gens carry it.
def _pt_seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    ll = vx * vx + vy * vy or 1.0
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / ll))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def _in_poly(x, y, poly):
    n = len(poly)
    j = n - 1
    c = False
    for i in range(n):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
            c = not c
        j = i
    return c


def furrows(poly, color, theta):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    fcx, fcy = sum(xs) / len(xs), sum(ys) / len(ys)
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    dx, dy = math.cos(theta), math.sin(theta)
    nx, ny = -dy, dx
    cid = s._cid("dry")
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in poly)
    g = [f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>', f'<g clip-path="url(#{cid})">']
    t = -diag / 2
    while t <= diag / 2:
        mx, my = fcx + nx * t, fcy + ny * t
        g.append(f'<line x1="{mx - dx * diag / 2:.1f}" y1="{my - dy * diag / 2:.1f}" x2="{mx + dx * diag / 2:.1f}" y2="{my + dy * diag / 2:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>')
        t += 5
    g.append('</g>')
    s.add(''.join(g))


def plot_centroid(net, key, inset=0.15):
    cens = [(sum(v[0] for v in p["poly"]) / len(p["poly"]), sum(v[1] for v in p["poly"]) / len(p["poly"])) for p in net["plots"] if not p.get("filler")]
    cx, cy = key(cens)
    mx = sum(c[0] for c in cens) / len(cens)
    my = sum(c[1] for c in cens) / len(cens)
    return (round(cx + inset * (mx - cx), 1), round(cy + inset * (my - cy), 1))


def topo_channel(pts, frm, to, draw_w=0.0, col='#7C9EB0'):
    ax, ay = pts[0]
    bx, by = pts[-1]
    chord = math.hypot(bx - ax, by - ay) or 1.0
    dev = max(abs((py - ay) * (bx - ax) - (px - ax) * (by - ay)) / chord for px, py in pts[1:-1]) if len(pts) > 2 else 0.0
    if dev < 6:
        k = max(range(len(pts) - 1), key=lambda i: math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
        mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
        pts = list(pts[: k + 1]) + [(mx - 12 * (by - ay) / chord, my + 12 * (bx - ax) / chord)] + list(pts[k + 1 :])
    poly = [[round(px, 1), round(py, 1)] for px, py in pts]
    s.M["channels"].append({"poly": poly, "frm": frm, "to": to, "w": draw_w or 2.5, "drawn": bool(draw_w)})
    s.corridors.append(([(px, py) for px, py in poly], 33))
    if draw_w:
        s.field_channel([(px, py) for px, py in poly], col, draw_w, draw_w)


def comb_field(name, sluice, down_deg, seed, field_fall, canal_a, canal_b, offtakes_a, offtakes_b=(), dry_band=(47, 88), avoid=(), dry_keepout=()):
    net = build_comb(
        3200,
        3050,
        sluice,
        seed,
        down_deg=down_deg,
        field_fall=field_fall,
        canal_a_len=canal_a,
        canal_b_len=canal_b,
        offtakes_a=offtakes_a,
        offtakes_b=offtakes_b,
        plot_across=PLOT_ACROSS,
        row_step=ROW_STEP,
        dry_band=dry_band,
        dry_keepout=dry_keepout,
        grain=2 / 3,
    )
    env = [(round(x, 1), round(y, 1)) for x, y in net["envelope"]]
    s.field_polys.append([(p[0], p[1]) for p in env])
    s.comb_base_fill(net, name, color="#CDB78C", full_envelope=True)
    _prior = [fld["outline"] for fld in s.M["fields"] if fld.get("kind") == "paddy"]
    for dp in net["dry_plots"]:
        if any(_pt_seg(x, y, ln[i][0], ln[i][1], ln[i + 1][0], ln[i + 1][1]) < 16 for ln in avoid for (x, y) in dp["poly"] for i in range(len(ln) - 1)):
            continue
        if any(hem_on_paddy(dp["poly"], _pol) for _pol in _prior):
            continue
        s.dry_polys.append(dp["poly"])
        pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in dp["poly"])
        s.add(f'<polygon points="{pts}" fill="{dp["fill"]}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>')
        furrows(dp["poly"], dp["furrow"], dp["theta"])
        s.M["dry_plots"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in dp["poly"]], "crop": dp["crop"], "theta": round(dp["theta"], 3)})
    for p in net["plots"]:
        pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in p["poly"])
        s.add(f'<polygon points="{pts}" fill="{p["fill"]}" stroke="{AZE}" stroke-width="{aze_w(s.ftpx):.2f}" stroke-linejoin="round"/>')
    s.bund_junctions(net["plots"], name)
    beads = ''.join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{BEAN_GREEN}"/>' for x, y in net["bund_beans"])
    s.add(f'<g opacity="0.85">{beads}</g>')
    for c in sorted(net["channels"], key=lambda c: -c["w"]):
        s.field_channel(c["pts"], '#7C9EB0' if c["role"] == "drain" else '#6C9CBE', c["w"], c.get("w_tail", c["w"]), late=True)
    exs = [p[0] for p in env]
    eys = [p[1] for p in env]
    pvx = [v[0] for p in net["plots"] for v in p["poly"]]
    pvy = [v[1] for p in net["plots"] for v in p["poly"]]
    s.M["fields"].append(
        {
            "name": name,
            "kind": "paddy",
            "down_deg": down_deg,
            "outline": [[x, y] for x, y in env],
            "bbox": [min(exs), min(eys), max(exs), max(eys)],
            "vis_bbox": [min(pvx), min(pvy), max(pvx), max(pvy)],
            "plot_polys": [[[round(v[0], 1), round(v[1], 1)] for v in p["poly"]] for p in net["plots"]],
        }
    )
    for c in net["channels"]:
        s.M["field_ditches"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in c["pts"]], "role": c["role"], "field": name, "w": round(c["w"], 1), "w_tail": round(c.get("w_tail", c["w"]), 1)})
    return net, env, (round(sum(exs) / len(exs), 1), round(sum(eys) / len(eys), 1))


# the head is tapped off the river's west bank below the wharf and the fall runs WITH the current
# (the river's flow_deg is 117.7), so the drain collector returns to the river DOWNSTREAM of its own
# intake - never above it. The comb spreads inland across the open ground south of the rampart.
# the TAP is on the river's own bank, upstream of everything the field drains back into, and the
# head-race runs from it to the sluice gate; the drain leaves the low corner for the river's lower
# reach. Both ends are DECLARED (topo_channel), which is what grounds the net for the water checks.
# DERIVED from the river's own lower reach, not eyeballed: a point 12% down the reach below the
# wharf, with the sluice set inland on the river's west side along that reach's normal.
_QT = 0.30
_QRA, _QRB = RIVER[3], RIVER[4]
_QTAP = (_QRA[0] + (_QRB[0] - _QRA[0]) * _QT, _QRA[1] + (_QRB[1] - _QRA[1]) * _QT)
_qrl = math.hypot(_QRB[0] - _QRA[0], _QRB[1] - _QRA[1])
_qnx, _qny = -(_QRB[1] - _QRA[1]) / _qrl, (_QRB[0] - _QRA[0]) / _qrl  # inland (west) normal
_PSL = (_QTAP[0] + _qnx * 55, _QTAP[1] + _qny * 55)
_PMID = ((_QTAP[0] + _PSL[0]) / 2 + _qny * 16, (_QTAP[1] + _PSL[1]) / 2 - _qnx * 16)  # a gentle bend: a cut follows the ground, it is not ruled
s.field_channel([_QTAP, _PMID, _PSL], "#9CB4C8", 7, 7)
s.sluice_gate(_PSL[0], _PSL[1], rot=math.degrees(math.atan2(_PSL[1] - _QTAP[1], _PSL[0] - _QTAP[0])) + 90)
s.sluice_gate(_QTAP[0], _QTAP[1], rot=math.degrees(math.atan2(_PSL[1] - _QTAP[1], _PSL[0] - _QTAP[0])) + 90)  # the head gate where the cut leaves the river
_PADDY, _PENV, _PCEN = comb_field("daika-s", _PSL, 150, 61, 150, (185, 225), (105, 130), (0.35, 0.7), dry_band=(20, 40), avoid=(MOAT, RIVER))
_PPD = plot_centroid(_PADDY, lambda cs: max(cs, key=lambda pc: pc[1]))
topo_channel([_QTAP, _PSL, _PPD], {"kind": "river"}, {"kind": "field", "name": "daika-s"})
_PDR = next(c["pts"] for c in _PADDY["channels"] if c["role"] == "drain")
topo_channel([tuple(_PDR[-2]), tuple(_PDR[-1])], {"kind": "drain", "name": "daika-s"}, {"kind": "offmap"})
# the households that work it, ringed on the field's own envelope
# the households that work it, ringed on the field's own envelope (n seats, gap px apart)
_PXS = [q[0] for q in _PENV]
_PYS = [q[1] for q in _PENV]
_PW = max(_PXS) - min(_PXS)
_PH = max(_PYS) - min(_PYS)
# the households that work it. Placed one at a time against the placer rather than ringed: the
# perimeter ring seats nothing here, because the field's envelope is hemmed by the river on one
# flank, the towpath on another and the funerary ground on a third, and every candidate the ring
# offers falls on one of them.
_PB = s.bound  # the CITY bound refuses every seat out on the paddy
_PXS = [q[0] for q in _PENV]
_PYS = [q[1] for q in _PENV]
s.bound = [[min(_PXS) - 240, min(_PYS) - 240], [max(_PXS) + 240, min(_PYS) - 240], [max(_PXS) + 240, max(_PYS) + 240], [min(_PXS) - 240, max(_PYS) + 240]]
_PH0 = len(s.M["houses"])
_TORING.append((_PENV, 118, [tuple(q) for q in next(c["pts"] for c in _PADDY["channels"] if c["role"] == "drain")]))
_PFH = len(s.M["houses"]) - _PH0
s.bound = _PB
print(f"paddy farmhouses: {_PFH}")


# ---- THE REST OF THE RING (GM 2026-08-11: "the city should be SURROUNDED by farmland. Cities grow
# up around fertile land, so keep adding rice paddies and farmhouses until there are no more places
# to put them"). Each field is tapped off the nearest water DOWNSTREAM of the city's own draw: the
# moat's flow runs NE->SW (inlet 2480,950 -> outlet 2067,2264), so a west or southwest field takes
# its head from the moat's lower arc, and the east field taps the river above the wharf.
def _upslope(env, down_deg):
    """The field envelope with its DOWNSLOPE third trimmed off. Farmsteads ring the ground ABOVE
    the drainage line - below it is the wettest land in the valley (marsh, low reclaimed paddy, the
    tameike) and nobody builds there (dwellings_above_field_drain). Ringing the whole envelope puts
    a fifth of the households in the bog."""
    _fx, _fy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
    _pr = [q[0] * _fx + q[1] * _fy for q in env]
    _cut = min(_pr) + (max(_pr) - min(_pr)) * 0.66
    _keep = [q for q, pr in zip(env, _pr, strict=True) if pr <= _cut]
    return _keep if len(_keep) >= 3 else env


def _nearest_on(poly, hint):
    """The nearest point ON a water polyline to `hint` - so a tap is DERIVED from the watercourse
    rather than eyeballed beside it (every hand-picked tap in the first cut stood on dry ground)."""
    best = (float("inf"), poly[0])
    for k in range(len(poly) - 1):
        ax, ay = poly[k]
        bx, by = poly[k + 1]
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy or 1.0
        t = max(0.0, min(1.0, ((hint[0] - ax) * dx + (hint[1] - ay) * dy) / ll))
        px_, py_ = ax + t * dx, ay + t * dy
        d = math.hypot(hint[0] - px_, hint[1] - py_)
        if d < best[0]:
            best = (d, (px_, py_))
    return best[1]


def _ring_field(name, water, hint, out_dir, down_deg, seed, fall, canal_a, canal_b, offtakes, src_kind, hem=(47, 88)):
    """One more paddy on the ring, with the whole water chain the checks require: a tap ON the
    water, a bent head-race to a sluice set inland, gates at both ends, the comb beyond, the source
    and the drain both DECLARED, and the farmsteads that work it."""
    tap = _nearest_on(water, hint)
    _tl = math.hypot(out_dir[0], out_dir[1]) or 1.0
    if src_kind == "drain-to-moat":
        # its HEAD comes off the sheet - the high ground beyond the frame - so the race starts at
        # the map edge in the direction the field lies, not on the moat it discharges into
        _ex = 0.0 if out_dir[0] < 0 else float(s.W)
        _ey = 0.0 if out_dir[1] < 0 else float(s.H)
        tap = (_ex, _ey) if abs(out_dir[0]) > abs(out_dir[1]) else (hint[0] + out_dir[0] / _tl * 400, _ey)
    _ux, _uy = out_dir[0] / _tl, out_dir[1] / _tl
    _sl = (tap[0] + _ux * 78, tap[1] + _uy * 78)
    if src_kind == "moat":
        _mf = s.M["moat_flow"]
        tap = moat_swept_tap(water, _mf["inlet"], _mf["outlet"], _sl, tap, want_deg=42.0, max_back=240.0)  # a short walk: sweeping 300 px upstream turns a 78 px head-race into a long diagonal
    _md = ((tap[0] + _sl[0]) / 2 - _uy * 7, (tap[1] + _sl[1]) / 2 + _ux * 7)
    s.field_channel([tap, _md, _sl], "#9CB4C8", 7, 7)
    if src_kind != "drain-to-moat":
        # a field FED from the water is gated where it draws; one that merely DISCHARGES has its
        # only gate at the outfall, because there is no watercourse at its head to gate
        s.sluice_gate(_sl[0], _sl[1], rot=math.degrees(math.atan2(_uy, _ux)) + 90)
    _net, _env, _cen = comb_field(
        name, _sl, down_deg, seed, fall, canal_a, canal_b, offtakes, avoid=(MOAT, RIVER), dry_band=(47, 88)
    )  # the pool cities' 3 ft/px hem: the dry-crop margin is what QUILTS the uncommanded fan head, so a thin one leaves bare parchment
    _pd = plot_centroid(_net, lambda cs: max(cs, key=lambda pc: pc[1]))  # the chain must END IN the field, or nothing anchors it there
    topo_channel([tap, _sl, _pd], {"kind": "offmap"} if src_kind == "drain-to-moat" else {"kind": src_kind}, {"kind": "field", "name": name})
    if src_kind == "drain-to-moat":
        # the head comes off the sheet (the high ground beyond the frame), and the DRAIN is what
        # meets the moat - so the junction is a discharge, gated, and swept with the moat's current
        _dr0 = next(c["pts"] for c in _net["channels"] if c["role"] == "drain")
        _out = _nearest_on(water, tuple(_dr0[-1]))
        s.field_channel([tuple(_dr0[-1]), _out], "#9CB4C8", 6, 6)
        s.sluice_gate(_out[0], _out[1], rot=math.degrees(math.atan2(_out[1] - _dr0[-1][1], _out[0] - _dr0[-1][0])) + 90)
        topo_channel([tuple(_dr0[-1]), _out], {"kind": "drain", "name": name}, {"kind": "moat"})
        _od = (_out[0] - _dr0[-1][0], _out[1] - _dr0[-1][1])
        _ol2 = math.hypot(*_od) or 1.0
        topo_channel([_out, (_out[0] + _od[0] / _ol2 * 600, _out[1] + _od[1] / _ol2 * 600)], {"kind": "moat"}, {"kind": "offmap"}, draw_w=0.0)
    _dr = next(c["pts"] for c in _net["channels"] if c["role"] == "drain")
    _de = tuple(_dr[-1])
    _dd2 = (_de[0] - _dr[-2][0], _de[1] - _dr[-2][1])
    _dl = math.hypot(*_dd2) or 1.0
    _off = (_de[0] + _dd2[0] / _dl * 900, _de[1] + _dd2[1] / _dl * 900)  # carry it clear OFF the sheet - a drain that stops on-canvas is a drain that goes nowhere
    if src_kind != "drain-to-moat":
        topo_channel([_de, _off], {"kind": "drain", "name": name}, {"kind": "offmap"}, draw_w=4.0)
    # the households that work it, on the flanks that stay in view once the sheet is cropped
    _xs = [q[0] for q in _env]
    _ys = [q[1] for q in _env]
    _pb = s.bound
    s.bound = [[min(_xs) - 200, min(_ys) - 200], [max(_xs) + 200, min(_ys) - 200], [max(_xs) + 200, max(_ys) + 200], [min(_xs) - 200, max(_ys) + 200]]
    # RINGED the way the provincial cities ring theirs - three passes at increasing standoff, which
    # is what puts 15-35 households on a field instead of the eight a hand-picked list manages.
    # (The rings seated NOTHING until the bound above was opened: s.bound was still the city's.)
    _TORING.append((_env, down_deg, [tuple(q) for q in _dr]))
    _n = 0
    s.bound = _pb
    print(f"{name}: {_n} farmsteads")
    return _net, _env


_RING = []
for _nm, _wat, _hint, _od, _dd, _sd, _ff, _ca, _cb, _oa, _sk, _hm in (
    ("daika-w", MOAT, (264, 1180), (-1.0, 0.12), 180, 71, 174, (188, 239), (123, 159), (0.22, 0.45, 0.68, 0.88), "moat", (47, 88)),
    ("daika-s2", RIVER, (1950, 2960), (-0.97, 0.24), 175, 73, 114, (130, 167), (81, 104), (0.22, 0.45, 0.68, 0.88), "river", (47, 88)),  # a second bay of the southern paddy, downstream of the first
    ("daika-e", RIVER, (2700, 1480), (0.6, 0.8), 52, 77, 174, (188, 239), (123, 159), (0.22, 0.45, 0.68, 0.88), "river", (47, 88)),
    ("daika-w2", MOAT, (264, 800), (-1.0, -0.1), 170, 87, 188, (217, 275), (130, 171), (0.22, 0.45, 0.68, 0.88), "moat", (47, 88)),
    # THE SOUTHWEST PLAIN - the ground the first pass left bare. Fed from the river's lowest reach,
    # which runs southwest past the city, so these bays lie downstream of everything the city draws
    # and their drains carry on off the sheet in the same direction.
    ("daika-sw", RIVER, (2010, 2985), (-0.9, -0.44), 236, 101, 100, (120, 152), (74, 95), (0.22, 0.45, 0.68, 0.88), "river", (47, 88)),
    (
        "daika-nw",
        MOAT,
        (760, 130),
        (-0.25, -0.97),
        330,
        107,
        46,
        (56, 74),
        (36, 48),
        (0.22, 0.45, 0.68, 0.88),
        "drain-to-moat",
        (10, 20),
    ),  # the north shelf is ~120 px deep between rampart and sheet edge: a pool-sized hem alone would not fit
    ("daika-e2", RIVER, (3010, 1980), (0.85, 0.53), 75, 93, 188, (217, 275), (130, 171), (0.22, 0.45, 0.68, 0.88), "river", (47, 88)),
):
    try:
        _RING.append(_ring_field(_nm, _wat, _hint, _od, _dd, _sd, _ff, _ca, _cb, _oa, _sk, _hm))
    except (ValueError, IndexError) as _e:
        # a site the comb cannot build on - too little room between the moat, the roads and the
        # sheet edge for a fan of this size. Report it, and UNRECORD the half-built field: it is
        # recorded before its water is declared, so leaving it would put a paddy on the map with
        # no source, no drain and no farmhouses, invisible to every rule that reads the water.
        s.M["fields"] = [_f for _f in s.M["fields"] if _f.get("name") != _nm]
        s.M["field_ditches"] = [_d for _d in s.M.get("field_ditches") or [] if _d.get("field") != _nm]
        print(f"{_nm}: NO FIELD ({_e}) - withdrawn")

# THE FARMSTEADS, once every field is on the map: each ringed on its upslope side, clear of its
# own cropland and of every other field's (the check reads them all, and so must the placer).
_FH = 0
for _renv, _rdd, _rdr in _TORING:
    _rb = s.bound
    _rxs = [q[0] for q in _renv]
    _rys = [q[1] for q in _renv]
    s.bound = [[min(_rxs) - 260, min(_rys) - 260], [max(_rxs) + 260, min(_rys) - 260], [max(_rxs) + 260, max(_rys) + 260], [min(_rxs) - 260, max(_rys) + 260]]
    _FH += _ring_upslope(_renv, _rdd, drain=_rdr)
    s.bound = _rb
print(f"farmsteads on the ring: {_FH}")

# ...and DECK AGAIN: the ring's head-races are laid long after the first bridges() pass, so any
# road they cross is still fording them until this runs (roads_bridge_water).
s.bridges()

s.crop_city(
    margin=36
)  # ~110 real ft of edge (GM 2026-08-10: 400 ft of empty margin was too much)  # the south=240/east=700 overrides padded dead margin onto both flanks (GM 2026-08-10); the aggressive default frames the real content
s.title("Shiro Daika")
# THE OUTPUT IS NAMED FOR THE MAP, NOT FOR THIS FILE. Verbatim in the monolith this read
# `os.path.splitext(os.path.abspath(__file__))[0].replace(".gen", "")`, where `__file__` was
# `wip/shiro-daika.gen.py` and the stem came out `wip/shiro-daika`. Moved here it became
# `wip/shiro_daika/fields`, so the map wrote itself into its own source package under the name
# of a module - and, because a single `*` in .gitignore does not cross `/`, straight into a
# commit. This is the shape a "verbatim move" cannot preserve: code that reads its own location
# at run time. State the stem instead of deriving it (settlement-review, 2026-08-31).
s.finish(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shiro-daika"), png_width=4600)
