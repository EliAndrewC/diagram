"""Feature 282's review-finding measurements, read from the DRAWN artifacts (the SVG ink, the rendered page, the notes)."""
import re, json, math, sys
def segdist(p,a,b):
    (px,py),(ax,ay),(bx,by)=p,a,b
    dx,dy=bx-ax,by-ay; t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
res={}
for h in ['inashiro','kashikawa','mizuguchi','sawada']:
    svg=open(f'pool/hamlets/{h}/{h}.svg').read()
    shares=[]; margins=[]; gaps=[]; turned=0; yard_turned=[]; racklines=0; rackboxes=0; yards=0
    for m in re.finditer(r'<g transform="translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)"><polygon points="([^"]+)" fill="#D2BE94"(.*?)</g>', svg):
        yards+=1
        poly=[tuple(map(float,p.split(','))) for p in m.group(4).split()]; body=m.group(5)
        mats=[]
        for r in re.finditer(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"(?: transform="rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)")? fill="#E4CC86"',body):
            x,y,w,hh=map(float,r.group(1,2,3,4)); a=float(r.group(5) or 0); cx,cy=x+w/2,y+hh/2; t=math.radians(a)
            mats.append((x,y,w,hh,a,[(cx+dx*math.cos(t)-dy*math.sin(t),cy+dx*math.sin(t)+dy*math.cos(t)) for dx,dy in ((-w/2,-hh/2),(w/2,-hh/2),(w/2,hh/2),(-w/2,hh/2))]))
        area=0.5*abs(sum(poly[i][0]*poly[(i+1)%4][1]-poly[(i+1)%4][0]*poly[i][1] for i in range(4)))
        shares.append(len(mats)/(area/18))
        if mats: yard_turned.append(sum(1 for m_ in mats if m_[4] != 0) / len(mats))
        for k,(x,y,w,hh,a,cs) in enumerate(mats):
            turned += a != 0
            for c in cs:
                margins.append(min(segdist(c,poly[i],poly[(i+1)%4]) for i in range(4)))
            for x2,y2,w2,h2,a2,cs2 in mats[k+1:]:  # the smallest drawn gap between two mats: corner of one to edge of the other
                gaps.append(min(min(segdist(c,cs2[i],cs2[(i+1)%4]) for i in range(4) for c in cs), min(segdist(c,cs[i],cs[(i+1)%4]) for i in range(4) for c in cs2)))
        racklines+=len(re.findall(r'stroke="#D9B64A"',body)); rackboxes+=len(re.findall(r'<rect(?![^>]*#E4CC86)',body))
    html=open(f'pool/hamlets/{h}/{h}.html').read()
    res[h]=dict(yards=yards, share_min=round(min(shares),2), share_max=round(max(shares),2), min_margin_ft=round(min(margins),2), min_gap_ft=round(min(gaps),2), mats=sum(1 for _ in margins)//4, turned=turned, least_turned_yard=round(min(yard_turned),2),
      rack_lines=racklines, rack_boxes=rackboxes, modal_third=html.count('between a third and two thirds of the straw mats'), modal_askew=html.count('laid a little askew'), modal_smallest=html.count('the smallest yards a little fewer'), modal_barley=html.count('barley country'),
      modal_about_half=html.count('about half of the straw mats'), modal_rack_conditional=html.count('where a map draws racks by the houses'))
res['notes_282']={h: sum(1 for l in open(f'pool/hamlets/{h}/{h}.notes.md') if 'feature 282' in l) for h in ['inashiro','kashikawa','mizuguchi','sawada']}
print(json.dumps(res))
