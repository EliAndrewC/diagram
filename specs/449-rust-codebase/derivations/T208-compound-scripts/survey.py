import sys, re, xml.etree.ElementTree as ET
NS='{http://www.w3.org/2000/svg}'
def tag(e): return e.tag.replace(NS,'')
def bbox(e):
    t=tag(e); a=e.attrib
    try:
        if t=='rect': x,y,w,h=[float(a.get(k,0)) for k in ('x','y','width','height')]; return (x,y,x+w,y+h)
        if t=='circle': cx,cy,r=[float(a[k]) for k in ('cx','cy','r')]; return (cx-r,cy-r,cx+r,cy+r)
        if t=='ellipse': cx,cy,rx,ry=[float(a[k]) for k in ('cx','cy','rx','ry')]; return (cx-rx,cy-ry,cx+rx,cy+ry)
        if t=='line': x1,y1,x2,y2=[float(a[k]) for k in ('x1','y1','x2','y2')]; return (min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2))
        if t in('polygon','polyline'):
            p=[float(v) for v in re.split(r'[ ,]+',a['points'].strip())]; xs=p[0::2]; ys=p[1::2]; return (min(xs),min(ys),max(xs),max(ys))
        if t=='path':
            p=[float(v) for v in re.findall(r'-?\d+\.?\d*',a['d'])]; xs=p[0::2]; ys=p[1::2]; return (min(xs),min(ys),max(xs),max(ys))
    except Exception: return None
    return None
def walk(e, kind, depth, out):
    k=e.attrib.get('data-kind',kind)
    t=tag(e)
    if t in ('defs','pattern'): return
    if t=='text':
        out.append((k,'text',None,''.join(e.itertext()).strip()[:30], e.attrib.get('data-cont'))); return
    if t=='g':
        for c in e: walk(c,k,depth+1,out)
        return
    out.append((k,t,bbox(e),e.attrib.get('data-id',''),e.attrib.get('fill','')))
root=ET.parse(sys.argv[1]).getroot()
out=[]
for c in root: walk(c,'?',0,out)
for o in out: print(o)
