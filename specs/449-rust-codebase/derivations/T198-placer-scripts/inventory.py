"""Inventory of the Mode A pool sheets for the T198 derivation: captions, drawn shapes, extents.
Reads only the SVG (the placer's input, or for the two generated sheets its output text positions are ignored)."""
import sys, re, math, json
import xml.etree.ElementTree as ET
NS = '{http://www.w3.org/2000/svg}'
GROUND = {'inner court','outer court','hearing court','garden','vegetable garden','practice ground','cart yard','rear yard',
          'precinct clearing','border court','shrine grove','garden pines','-'}
CROSS = {'road','approach','footpath','river','revetment'}  # crossable at a cost (0242: a lane or ditch may be crossed)
NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')

def tag(e): return e.tag.replace(NS, '')

def shape_box(e, tx, ty):
    t = tag(e); g = lambda k, d=0.0: float(e.get(k, d))
    sw = float(e.get('stroke-width', 0) or 0)
    if t == 'rect':
        x, y, w, h = g('x'), g('y'), g('width'), g('height'); b = (x, y, x+w, y+h)
    elif t == 'circle':
        cx, cy, r = g('cx'), g('cy'), g('r'); b = (cx-r, cy-r, cx+r, cy+r)
    elif t == 'ellipse':
        cx, cy, rx, ry = g('cx'), g('cy'), g('rx'), g('ry'); b = (cx-rx, cy-ry, cx+rx, cy+ry)
    elif t == 'line':
        b = (min(g('x1'), g('x2')), min(g('y1'), g('y2')), max(g('x1'), g('x2')), max(g('y1'), g('y2')))
    elif t in ('polygon', 'polyline', 'path'):
        s = e.get('points') or e.get('d') or ''
        n = [float(v) for v in NUM.findall(s)]
        xs, ys = n[0::2], n[1::2]
        if not xs or not ys: return None, 0
        b = (min(xs), min(ys), max(xs), max(ys))
        return (b[0]-sw/2+tx, b[1]-sw/2+ty, b[2]+sw/2+tx, b[3]+sw/2+ty), max(len(xs)-1, 1)
    else:
        return None, 0
    return (b[0]-sw/2+tx, b[1]-sw/2+ty, b[2]+sw/2+tx, b[3]+sw/2+ty), 1

def text_lines(e):
    ts = [x for x in e if tag(x) == 'tspan']
    if ts: return [(t.text or '') for t in ts]
    return [e.text or '']

def width(line, fs, bold, ls):
    k = 0.58 if bold else 0.52   # mean advance of a Georgia glyph, in ems (a GUESS of this script)
    return len(line) * (fs * k + ls)

def inventory(path):
    root = ET.parse(path).getroot()
    vb = [float(v) for v in root.get('viewBox').split()]
    shapes = []   # (box, kind, ids, segs, inherited stroke, group-key)
    captions = []
    def walk(e, kind, ids, tx, ty, grp, stroke, inside_defs):
        t = tag(e)
        if t in ('defs', 'pattern'): return
        m = re.match(r'translate\(([-\d.]+)[ ,]+([-\d.]+)\)', e.get('transform', ''))
        if m: tx, ty = tx+float(m.group(1)), ty+float(m.group(2))
        k = e.get('data-kind', kind)
        my_ids = ids + [v for v in (e.get('data-id'), e.get('id')) if v]
        stroke = e.get('stroke', stroke)
        if t in ('g', 'svg', 'a'):
            g2 = grp if e.get('data-kind') is None and e.get('data-id') is None else id(e)
            prev = None
            for c in e:
                walk(c, k, my_ids, tx, ty, g2, stroke, False)
            return
        if t == 'text':
            captions.append(dict(el=e, kind=k, grp=grp, tx=tx, ty=ty))
            return
        b, segs = shape_box(e, tx, ty)
        if b: shapes.append(dict(box=b, kind=k, ids=my_ids, segs=segs, grp=grp, tag=t,
                                 fill=e.get('fill', ''), area=(b[2]-b[0])*(b[3]-b[1])))
    walk(root, '-', [], 0, 0, 0, None, False)
    # captions: declared or placed texts that name something (skip sheet furniture: title, scale)
    caps = []
    for c in captions:
        e = c['el']
        if e.get('data-cont') == '1':
            if caps: caps[-1]['lines'] += text_lines(e); caps[-1]['fs_lines'] += [float(e.get('font-size', 10))]*len(text_lines(e))
            continue
        if c['kind'] == '-' and not e.get('data-names'): continue
        if e.get('x') is not None and not e.get('data-names'): continue   # placed furniture
        fs = float(e.get('font-size', 10)); bold = e.get('font-weight') == 'bold'
        ls = float(e.get('letter-spacing', 0) or 0)
        lines = text_lines(e)
        caps.append(dict(words=' '.join(lines), lines=lines, fs=fs, bold=bold, ls=ls, fs_lines=[fs]*len(lines),
                         names=(e.get('data-names') or '').split(), grp=c['grp'], kind=c['kind']))
    for c in caps:
        c['w1'] = width(' '.join(c['lines']), c['fs'], c['bold'], c['ls'])      # as one line
        c['wN'] = max(width(l, f, c['bold'], c['ls']) for l, f in zip(c['lines'], c['fs_lines']))
        c['hN'] = sum(c['fs_lines']) * 1.15
        c['h1'] = c['fs'] * 1.15
        c['nwords'] = len(' '.join(c['lines']).split())
        # the feature named: data-names ids, else the shapes of the group it stands in
        if c['names']:
            fs_ = [s for s in shapes if set(s['ids']) & set(c['names'])]
        else:
            fs_ = [s for s in shapes if s['grp'] == c['grp'] and c['grp'] != 0]
        c['parts'] = len(fs_)
        if fs_:
            c['fbox'] = (min(s['box'][0] for s in fs_), min(s['box'][1] for s in fs_),
                         max(s['box'][2] for s in fs_), max(s['box'][3] for s in fs_))
        else:
            c['fbox'] = None
        c['fshapes'] = fs_
    return vb, shapes, caps

if __name__ == '__main__':
    out = {}
    for p in sys.argv[1:]:
        vb, shapes, caps = inventory(p)
        name = p.split('/')[-1][:-4]
        blocking = [s for s in shapes if s['kind'] not in GROUND and s['kind'] not in CROSS]
        cross = [s for s in shapes if s['kind'] in CROSS]
        segs = sum(s['segs'] for s in shapes)
        unresolved = sum(1 for c in caps if c['fbox'] is None)
        fits = 0
        for c in caps:
            if c['fbox']:
                fw, fh = c['fbox'][2]-c['fbox'][0], c['fbox'][3]-c['fbox'][1]
                if (c['w1'] <= fw and c['h1'] <= fh) or (c['wN'] <= fw and c['hN'] <= fh): fits += 1
        out[name] = dict(extent_px=(vb[2], vb[3]), area_px2=vb[2]*vb[3], shapes=len(shapes), blocking=len(blocking),
                         crossable=len(cross), ground=len(shapes)-len(blocking)-len(cross), segments=segs,
                         captions=len(caps), multi_line_declared=sum(1 for c in caps if len(c['lines']) > 1),
                         unresolved=unresolved, fits_inside_bbox=fits,
                         mean_fs=round(sum(c['fs'] for c in caps)/max(len(caps),1), 2),
                         mean_w1=round(sum(c['w1'] for c in caps)/max(len(caps),1), 1),
                         mean_h=round(sum(c['hN'] for c in caps)/max(len(caps),1), 1),
                         mean_parts=round(sum(c['parts'] for c in caps)/max(len(caps),1), 2),
                         max_parts=max((c['parts'] for c in caps), default=0),
                         mean_words=round(sum(c['nwords'] for c in caps)/max(len(caps),1), 2))
    for k, v in out.items(): print(k, json.dumps(v))
